from datetime import date
from decimal import Decimal
from io import BytesIO
import json
import random
import string
from django.contrib import messages
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
import qrcode
from certificate.forms import ApplyCertificateForm, SearchForm
from certificate.models import ApprovedCertificate, ApprovedCertificate, Requested
from course.models import Course, ExamResult
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from users.models import User


app = "certificate/admin/"

class AllExamResultsView(View):
    template_name = app + 'all_exam_results.html'

    def get(self, request, *args, **kwargs):
        exam_results = ExamResult.objects.all()
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            exam_results = search_form.search(exam_results)

        context = {
            'exam_results': exam_results,
            'search_form': search_form,
        }
        return render(request, self.template_name, context)
    

        
class ApplyCertificateView(View):
    form_class = ApplyCertificateForm
    template_name = app + 'apply_cerificate.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            student = form.cleaned_data['student']
            batch = form.cleaned_data.get('batch') or course.batch

            if student:  # If a specific student is selected
                users = User.objects.filter(id=student.id)
            else:  # If no student is selected, apply for all students in the course
                users = User.objects.filter(course_of_interest=course)

            if not users.exists():
                messages.warning(request, "No students found for the selected course.")
                return render(request, self.template_name, {'form': form})
            batch = student.batch
            print(f"DEBUG:Batch: {batch}")

            for user in users:
                exam_result = ExamResult.objects.filter(student=user, course=course).first()

                if exam_result:
                    exam_data = {
                        'subjects': exam_result.subjects_data,
                        'percentage': self.convert_decimal(exam_result.percentage),
                        'grade': exam_result.grade,
                        'result': exam_result.result,
                    }
                else:
                    exam_data = None

                Requested.objects.create(
                    user=user,
                    course=course,
                    batch=batch, 
                    exam_data=exam_data,
                    status='Pending'
                )

            messages.success(request, "Certificates applied successfully.")
            return redirect('certificate:requested_certificates')

        return render(request, self.template_name, {'form': form})

    def convert_decimal(self, value):
        if isinstance(value, Decimal):
            return float(value)
        return value

def get_students_by_course(request, course_id):
    if request.method == "GET":
        students = User.objects.filter(course_of_interest_id=course_id)
        student_list = [
            {'id': student.id, 'name': student.full_name or student.roll_number or student.email}
            for student in students
        ]

        if student_list:
            return JsonResponse({'students': student_list})
        else:
            return JsonResponse({'students': []})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

class RequestedCertificatesListView(View):
    template_name = app + 'requested_certificates.html'

    def get(self, request):
        applications = Requested.objects.all()
        context = {'applications': applications}
        return render(request, self.template_name, context)

    def post(self, request, application_id=None):
        if not application_id:
            return HttpResponseNotFound("Application ID not provided.")
        
        try:
            application = get_object_or_404(Requested, id=application_id)
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'approve':
                application.status = 'Approved'
                application.is_approved = True
                application.save()
                ApprovedCertificate.objects.update_or_create(
                    user=application.user,
                    course=application.course,
                    batch=application.batch,
                    defaults={'applied_date': application.applied_date, 'status': 'Approved'},
                )
            elif action == 'reject':
                application.status = 'Rejected'
                application.is_approved = False
                application.save()
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)

            return JsonResponse({'status': application.status})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ApprovedCertificatesListView(View):
    template_name = app +  'approved_certificates.html'

    def get(self, request):
        full_name_query = request.GET.get('full_name', '').strip()
        course_query = request.GET.get('course', '').strip()
        batch_query = request.GET.get('batch', '').strip()

        applications = ApprovedCertificate.objects.all()

        if full_name_query:
            applications = applications.filter(user__full_name__icontains=full_name_query)

        if course_query:
            applications = applications.filter(course__icontains=course_query)

        if batch_query:
            applications = applications.filter(batch__icontains=batch_query)

        context = {
            'applications': applications,
        }
        return render(request, self.template_name, context)
    
class DeleteAppliedCertificateView(View):
    def post(self, request, pk):
        applied_certificate = get_object_or_404(Requested, pk=pk)
        applied_certificate.delete()
        return JsonResponse({'success': True, 'message': 'Application deleted successfully.'})
    
    
def toggle_certificate_status(request, pk):
    print(f"Received request for application ID: {pk}")
    if request.method == 'POST':
        application = get_object_or_404(ApprovedCertificate, pk=pk)
        status = request.POST.get('status')

        if status == 'approve':
            application.status = 'Approved'
        elif status == 'reject':
            application.status = 'Rejected'
        elif status == 'reset':
            application.status = 'Pending'
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)

        application.save()
        return JsonResponse({'status': application.status})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


class DesignedCertificateView(View):
    template_name = app + 'designed_certificate.html'

    def generate_certificate_no(self):
        while True:
            certificate_no = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not ApprovedCertificate.objects.filter(certificate_no=certificate_no).exists():
                return certificate_no
            
    def generate_certificate_pdf(self, certificate, qr_code_url,exam_result):
        # Render the HTML content for the certificate
        context = {
            'application': certificate,
            'percentage': exam_result.percentage,
            'grade': exam_result.grade,
            'course_name': exam_result.course.course_name,
            'course_duration': exam_result.course.course_duration,
            'course_period': '23 Nov 2023 TO 22 Nov 2024',
            'date_of_issue': date.today().strftime('%d-%m-%Y'),
            'qr_code_url': qr_code_url,
        }

        html_content = render_to_string(self.template_name, context)

        # Convert HTML to PDF using xhtml2pdf
        pdf_output = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_output)

        if pisa_status.err:
            print("Error while generating PDF")
            return None
        return pdf_output.getvalue()

    def get(self, request, application_id, *args, **kwargs):
        application = get_object_or_404(ApprovedCertificate, id=application_id)
        if not application.certificate_no:
            application.certificate_no = self.generate_certificate_no()
            application.save()
        
        exam_result = ExamResult.objects.filter(student=application.user).first()
        if not exam_result:
            return render(request, 'error_page.html', {'message': 'Exam result not found.'})
        
        qr_file_name = f"qrcodes/qr_{application.certificate_no}.png"
        if default_storage.exists(qr_file_name):
            qr_code_url = default_storage.url(qr_file_name)
        else:
        # Generate the QR code for the certificate
            local_domain = "http://127.0.0.1:8000"
            certificate_pdf_url = f"{local_domain}/media/certificates/{application.certificate_no}.pdf"
            print(f"Generated certificate URL: {certificate_pdf_url}")
            qr_code = qrcode.make(certificate_pdf_url)

            # Save the QR code as an image file
            qr_image = BytesIO()
            qr_code.save(qr_image)
            qr_image.seek(0)
            qr_file_name = f"qr_{application.certificate_no}.png"
            file_path = default_storage.save(f"qrcodes/{qr_file_name}", ContentFile(qr_image.read()))
            qr_code_url = default_storage.url(file_path)

        pdf_file_name = f"certificates/{application.certificate_no}.pdf"
        if default_storage.exists(pdf_file_name):
            pdf_url = default_storage.url(pdf_file_name)
        else:
            pdf_content = self.generate_certificate_pdf(application, qr_code_url,exam_result)
        # Save the PDF in the media folder
            if pdf_content:
                pdf_path = default_storage.save(f"certificates/{application.certificate_no}.pdf", ContentFile(pdf_content))
                pdf_url = default_storage.url(pdf_path)
            else:
                return render(request, 'error_page.html', {'message': 'PDF generation failed.'})
            
        context = {
            'application': application,
            'percentage': exam_result.percentage,
            'grade': exam_result.grade,
            'course_name': exam_result.course.course_name,
            'course_duration': exam_result.course.course_duration,
            'percentage': exam_result.percentage,
            'grade': exam_result.grade,
            'course_period': '23 Nov 2023 TO 22 Nov 2024',
            'qr_code_url': qr_code_url,
            'pdf_url': pdf_url, 
            'institute_details': {
                'name': "RATIONAL EDUCATION AND COMPUTER TRAINING",
                'email': "step2reactindia@gmail.com",
                'contact': "9778577090",
                'address': "SUBASH JENA COLONY, BANPUR ROAD, BALUGAON, STREET NO 37C, KHORDHA, ODISHA",
            },
        }
        return render(request, self.template_name, context)
    
def verify_certificate(request, certificate_no):
    # Try to fetch the certificate with the provided certificate_no
    certificate = get_object_or_404(ApprovedCertificate, certificate_no=certificate_no)
    
    
    return render(request, 'certificate_verification.html')

class MarksSheetView(View):
    template_name = app + 'marksheet.html'

    def get(self, request, application_id, *args, **kwargs):
        application = get_object_or_404(ApprovedCertificate, id=application_id)
        exam_result = ExamResult.objects.filter(student=application.user).first()
        
        if not exam_result:
            return render(request, 'error_page.html', {'message': 'Exam result not found.'})

        # Generate random marksheet number in the format RCT-XXXX-MKT
        random_number = random.randint(1000, 9999)  # Generate a random 4-digit number
        marksheet_no = f"RCT-{random_number}-MKT"

        # Calculate total theory, practical, and overall marks
        total_theory_marks = sum(
            subject.get("total_theory_marks", 0) for subject in exam_result.subjects_data
        )
        total_practical_marks = sum(
            subject.get("total_practical_marks", 0) for subject in exam_result.subjects_data
        )
        total_mark = total_theory_marks + total_practical_marks

        # Prepare context data for the template
        context = {
            'student_name': exam_result.student.full_name,
            'father_name': exam_result.student.father_husband_name,
            'mother_name': exam_result.student.mother_name,
            'course_name': exam_result.student.course_of_interest.course_name if exam_result.student.course_of_interest else 'N/A',
            'institute_name': "RATIONAL EDUCATION AND COMPUTER TRAINING",
            'course_duration': exam_result.student.course_of_interest.course_duration if exam_result.student.course_of_interest else 'N/A',
            'marksheet_no': marksheet_no,
            'dob': exam_result.student.date_of_birth,
            'course_period': "2024",
            'subjects': exam_result.subjects_data,
            'obtained_theory_marks': exam_result.obtained_theory_marks,
            'obtained_practical_marks': exam_result.obtained_practical_marks,
            'obtained_mark': exam_result.obtained_mark,
            'total_theory_marks': total_theory_marks,
            'total_practical_marks': total_practical_marks,
            'percentage': exam_result.percentage,
            'grade': exam_result.grade,
            'subject_data': exam_result.subjects_data,
            'total_mark': total_mark,
        }

        return render(request, self.template_name, context)
