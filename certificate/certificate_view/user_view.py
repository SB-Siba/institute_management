from decimal import Decimal
from pyexpat.errors import messages
import random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from certificate.forms import ApplyCertificateForm
from certificate.models import ApprovedCertificate, Requested
from course.models import Course, ExamResult
from users.models import User
from django.contrib import messages

 
app = "certificate/user/"


class ApplyCertificateView(View):
    form_class = ApplyCertificateForm
    template_name = app + 'apply_for_certificate.html'

    def get(self, request, *args, **kwargs):
        # Handle GET request and render the template
        user = request.user
        course_of_interest = user.course_of_interest  # Assuming the user has a course_of_interest

        # Check if the user has already applied for the certificate for the course
        already_applied = Requested.objects.filter(user=user, course=course_of_interest).exists()

        context = {
            'course': course_of_interest,
            'already_applied': already_applied,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Handle the "Apply for Certificate" action
        user = request.user
        course_of_interest = user.course_of_interest

        if not course_of_interest:
            messages.error(request, "You are not enrolled in any course.")
            return redirect('my_courses')  # Redirect to a relevant page

        # Check if the user has already applied
        if Requested.objects.filter(user=user, course=course_of_interest).exists():
            messages.warning(request, "You have already applied for a certificate for this course.")
            return redirect('certificate:apply_certificate')

        # Create an entry in the Requested model with minimal data
        Requested.objects.create(
            user=user,
            course=course_of_interest,
            batch=user.batch,  # Assuming the user has a batch attribute
            status='Pending',  # Set initial status as 'Pending'
        )

        # Add success message
        messages.success(request, "Your certificate application has been submitted.")
        
        # Redirect to the same page or another relevant page
        return redirect('certificate:apply_certificate')



class ApprovedCer(View):
    template_name = app +  'approve_certificate.html'

    def get(self, request):
        user = request.user

        # Initial queryset filtered by the logged-in user
        applications = ApprovedCertificate.objects.filter(user=user)

        # Apply additional filters based on query parameters
        full_name_query = request.GET.get('full_name', '').strip()
        course_query = request.GET.get('course', '').strip()
        batch_query = request.GET.get('batch', '').strip()

        if full_name_query:
            applications = applications.filter(user__full_name__icontains=full_name_query)

        if course_query:
            applications = applications.filter(course__course_name__icontains=course_query)

        if batch_query:
            applications = applications.filter(batch__batch_name__icontains=batch_query)

        context = {
            'applications': applications,
        }
        return render(request, self.template_name, context)
    
    
class MarksSheet(View):
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