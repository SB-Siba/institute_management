from base64 import b64encode
from collections import defaultdict
import io
import os
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
import qrcode
from helpers import utils
from users import models,forms
from users.forms import BatchForm, StudentForm, StudentPaymentForm
from users.models import Course, OnlineClass, Payment, Batch, User
# from course.models import Course
import csv
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from datetime import date, datetime, timedelta
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import UpdateView
from django.utils import timezone
from users.models import Attendance
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

app = "users/admin/"

# admin dashboard and manage users list

@method_decorator(utils.super_admin_only, name='dispatch')
class AdminDashboard(View):
    template = app + "index.html"

    def get(self, request):
        query = request.GET.get('search', '')  # Allow search query for filtering students
        if query:
            students = User.objects.filter(Q(full_name__icontains=query), is_superuser=False, is_staff=False)
        else:
            students = User.objects.filter(is_superuser=False, is_staff=False)

        # Fetch the latest payment details for each student
        student_data = []
        for student in students:
            # Get the latest payment for each student
            latest_payment = Payment.objects.filter(student=student).order_by('-date').first()

            student_data.append({
                'user': student,
                'latest_payment_date': latest_payment.date if latest_payment else None,
                'total_fees': student.total_fees or 0,  # Default to 0 if total_fees is None
                'fees_received': student.fees_received or 0,  # Default to 0 if fees_received is None
                'balance': student.balance or 0,  # Default to 0 if balance is None
            })

        # Calculate the overall totals
        total_fees = sum(data['total_fees'] for data in student_data if data['total_fees'] is not None)
        total_paid_fees = sum(data['fees_received'] for data in student_data if data['fees_received'] is not None)
        total_balance_fees = sum(data['balance'] for data in student_data if data['balance'] is not None)

        # Context to pass to the template
        context = {
            "students": student_data,
            "total_fees": total_fees,
            "total_paid_fees": total_paid_fees,
            "total_balance_fees": total_balance_fees,
            "search_query": query,
        }

        # Render the template with dynamic context
        return render(request, self.template, context)


class StudentListView(View):
    template_name = app + 'student_list.html'
   
    def get(self, request):
        search_query = request.GET.get('q', '').strip()
        students = User.objects.filter(is_admitted=True).order_by('full_name')

        # Apply search filter if query is provided
        if search_query:
            students = students.filter(full_name__icontains=search_query)

        # Paginate the student list
        paginator = Paginator(students, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
        }
        return render(request, self.template_name, context)
    
class ExportStudentsView(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        # Write the headers for the CSV file
        writer.writerow([
            'S/N', 'Photo', 'Batch', 'Student Name','Email', 'Course Interested', 'Mobile', 'Admission Date','Action'
        ])

        students = models.User.objects.all()
        for idx, student in enumerate(students, start=1):
            writer.writerow([
                idx, student.student_image, student.batch, student.full_name,student.email,
                student.course_of_interest,
                student.contact,
                student.admission_date
            ])

        return response

class StudentDetailView(View):
    model = models.User
    template = app + "user_profile.html"
    def get(self, request, user_id):
        user_obj = get_object_or_404(self.model, id=user_id)

        context = {
            "user_obj": user_obj,
        }
        return render(request, self.template, context)

def get_course_fee(request):
    course_id = request.GET.get('course_id')
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
            return JsonResponse({
                'total_fees': course.total_fees,
                'balance': course.balance,
                'discount_rate': course.discount_rate,
                'discount_amount': course.discount_amount,
                'fees_received': course.fees_received,
                'remarks': course.remarks,
            })
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)
    return JsonResponse({'error': 'No course_id provided'}, status=400)


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class AddNewStudentView(View):
    template = app + 'add_new_student.html'  # Update with your actual template path
    confirmation_template = os.path.join('users/email/admission_confirmation.html')

    def get(self, request):
        user_form = StudentForm()
        courses = Course.objects.all()  # Get all available courses
        return render(request, self.template, {
            'user_form': user_form,
            'courses': courses,
        })

    def post(self, request):
        course_id = request.POST.get('course_of_interest')
        user_form = StudentForm(request.POST, request.FILES)  # Initialize form with POST data
        admit_existing_user = request.POST.get('admit_existing_user', False) == 'true'

        # Initialize the form with POST data

        if user_form.is_valid():
            full_name = user_form.cleaned_data.get('full_name')

            try:
                # Check if the user is already registered (but not admitted)
                student = User.objects.get(full_name=full_name)

            except User.DoesNotExist:
            # Create a new user if not found
                student = user_form.save(commit=False)

        # Dynamically update all fields from the form
            for field, value in user_form.cleaned_data.items():
                if hasattr(student, field):
                    setattr(student, field, value)

        # Update additional fields
            student.is_admitted = True
            student.course_of_interest = Course.objects.get(id=course_id) if course_id else None

            # Save the student instance
            student.save()
            # Prepare the email context
            course = student.course_of_interest
            context = {
               'full_name': student.full_name,
                'course': {
                    'course_name': course.course_name if course else "Not Selected",
                    'award': course.award if course else "N/A",
                    'course_fees': course.course_fees if course else 0,
                    'course_mrp': course.course_mrp if course else 0,
                    'minimum_fees': course.minimum_fees if course else 0,
                    'course_duration': course.course_duration if course else "N/A",
                    'exam_fees': course.exam_fees if course else 0,
                    'eligibility': course.eligibility if course else "N/A",
                    'status': course.status if course else "N/A",
                    'course_syllabus': course.course_syllabus if course else "N/A",
                    'course_subject': course.course_subject if course else [],
                },
            }

            # Send confirmation email
            email_subject = "Admission Confirmation - REACT Institute"
            email_body = render_to_string(self.confirmation_template, context)

            email = EmailMessage(
                subject=email_subject,
                body=email_body,
                to=[student.email],  # Ensure the `email` field exists and is valid
            )
            email.content_subtype = "html"
            email.send()

            messages.success(request, f'{student.full_name} has been admitted to the course successfully!')

            return redirect('users:student_list')

            
            # If the form is not valid, re-render the page with form errors
        courses = Course.objects.all()
        return render(request, self.template, {
            'user_form': user_form,
            'courses': courses,
        })
    
class StudentsDetailView(View):
    template_name = app + 'students_details.html'

    def get(self, request, pk):
        # Fetch the student details
        student = get_object_or_404(User, pk=pk)
        public_ip = "127.0.0.1:8000"

        # Prepare data to encode in the QR code
        student_data = {
            "id": student.pk,
            "name": student.full_name,  # Use full_name instead of combining first_name and last_name
            "email": student.email,
            "phone": student.contact if hasattr(student, 'contact') else "N/A",
        }
        
        student_detail_url = f"http://{public_ip}/student-details/{student.pk}/"

        # Generate the QR code with the URL
        qr = qrcode.make(student_detail_url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        
        # Convert QR code to base64 to render in HTML
        qr_data = b64encode(buffer.getvalue()).decode()
        qr_image = f"data:image/png;base64,{qr_data}"
        
        # Pass data to the template
        context = {
            'student': student,
            'qr_image': qr_image,
            'student_detail_url': student_detail_url,  # For displaying or debugging
        }
        return render(request, self.template_name, context)
    
class StudentUpdateView(View):
    model = User
    form_class = StudentForm
    template_name = app + 'student_update.html'
    success_url = reverse_lazy('users:student_list')

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def get_context_data(self, form=None):
        if form is None:
            form = self.form_class(instance=self.get_object())
        return {'form': form}

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=user)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Student updated successfully!')
                return redirect(self.success_url)

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, 'Please correct the errors below.')
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)

        
class StudentDeleteView(View):
    def post(self, request, student_id):
        student = get_object_or_404(models.User, id=student_id, is_admitted=True)
        student.delete()
        return JsonResponse({'success': True})

# AJAX view to fetch course fees dynamically
class GetCourseFeesView(View):
    def get(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id)
        data = {
            'course_fees': course.course_fees,
            'minimum_fees': course.minimum_fees,
            'exam_fees': course.exam_fees,
        }
        return JsonResponse(data)
    
class CourseDetailsView(View):                                                                          
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            data = {
                'total_fees': course.total_fees,  
                'balance': course.balance,
                'discount_rate': course.discount_rate,
                'discount_amount': course.discount_amount,
                'fees_received': course.fees_received,
                'remarks': course.remarks,
            }
            return JsonResponse(data)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'No course found with the specified ID'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class StudentPaymentListView(View):
    model = Payment
    template_name = app + 'students_fees.html'
    def get(self, request):
        payments = Payment.objects.select_related('user').all().order_by('-date')
        
        # Calculate the total fees, paid, and balance 
        total_fees = sum(payment.course_fees or 0 for payment in payments)
        total_paid_fees = sum(payment.amount or 0 for payment in payments)
        total_balance_fees = total_fees - total_paid_fees   
        return render(request, self.template_name, {
            'payments': payments,
            'total_fees': total_fees,
            'total_paid_fees': total_paid_fees,
            'total_balance_fees': total_balance_fees,
        })

class StudentDeleteView(View):
    def post(self, request, pk):
        student = models.User.objects.get(pk=pk)
        student.delete()
        return JsonResponse({'message': 'Student deleted successfully'})

class ExportPaymentsView(View):
    model = Payment

    def get(self, request):
        payments = self.model.objects.all()

        if not payments.exists():
            messages.warning(request, "No records are there.")
            return redirect('users:student_payment_list')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_payments.csv"'

        writer = csv.writer(response)
        writer.writerow(['Sl No', 'Student Name', 'Course Name', 'Total Course Fees', 'Fees Paid', 'Fees Balance'])

        for i, payment in enumerate(payments, 1):
            writer.writerow([
                i,
                payment.student.full_name,
                payment.student.course_of_interest.course_name,
                payment.student.total_fees,
                payment.amount,
                payment.student.balance
            ])

        return response

class AddNewPaymentView(View):
    form_class = StudentPaymentForm
    template = app + 'add_new_payment.html'

    def get(self, request,student_id=None):
        student = get_object_or_404(User, id=student_id)
        course = student.course_of_interest if student.course_of_interest else None
        balance = self.calculate_balance(student.id, course.id) if course else 0
        payment = Payment.objects.filter(student=student, course=course).order_by('-id').first()
        if payment:
            form = self.form_class(initial={
                'student': student.id,
                'course': course.id if course else '',
                'amount': payment.amount,
                'payment_mode': payment.payment_mode,
                'description': payment.description,
                'balance': balance,
            })
        else:
            form = self.form_class(initial={
                'student': student.id,
                'course': course.id if course else '',
                'balance': balance
            })

        context = {
            'form': form,
            'student': student,
            'course': course,
            'balance': balance
        }
        return render(request, self.template, context)

    def post(self, request, student_id=None):
        form = self.form_class(request.POST)
        student = get_object_or_404(User, id=student_id)
        course = student.course_of_interest if student.course_of_interest else None
        balance = self.calculate_balance(student.id, course.id) if course else 0

        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = student
            payment.course = course
            payment.balance = balance  
            payment.payment_mode = form.cleaned_data.get('payment_mode')
            payment.description = form.cleaned_data.get('description')
            payment.save()
            student.fees_received += payment.amount
            student.balance = self.calculate_balance(student.id, course.id)
            student.save()
            return redirect('users:student_fees_list')
        else:
            print("Form errors:", form.errors)

        return render(request, self.template, {
            'form': form,
            'student': student,
            'course': course,
            'balance': balance
        })

    def calculate_balance(self, student_id, course_id):

        student = User.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        total_fees = student.total_fees or 0
        fees_received = student.fees_received or 0
        balance = total_fees - fees_received
        return balance

class TakeAttendanceView(View):
    template = app + "take_attendance.html"  

    def get(self, request):
        today_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
        selected_batch = request.GET.get('batch', None)
        batches = Batch.objects.all()

        # Fetch admitted students for the selected batch
        admitted_students = User.objects.filter(batch__id=selected_batch) if selected_batch else User.objects.none()

        students = admitted_students

        # Fetch attendance records for the selected date and batch
        attendance_records = Attendance.objects.filter(date=today_date, student__batch__id=selected_batch) if selected_batch else []
        attendance_status_map = {record.student.id: record.status for record in attendance_records}

        context = {
            'today_date': today_date,
            'batches': batches,
            'students': students,
            'attendance_status_map': attendance_status_map,
            'selected_batch': selected_batch
        }
        return render(request, self.template, context)

    def post(self, request):
        selected_batch = request.POST.get('batch')
        attendance_date = request.POST.get('date', date.today())

        # Fetch admitted students for the selected batch
        admitted_students = User.objects.filter(batch__id=selected_batch) if selected_batch else User.objects.none()

        students = admitted_students

        # Update or create attendance records for each student
        for student in students:
            attendance_status = request.POST.get(f'attendance_{student.id}')
            Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                defaults={'status': attendance_status}
            )
        messages.success(request, 'Attendance submitted successfully.')
        return redirect('users:take_attendance')
    
class AttendanceReportView(View):
    template = app + "attendance_report.html"

    def get(self, request):
        selected_batch = request.GET.get('batch', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        batches = Batch.objects.all()

        students = None
        attendance_data = []
        date_range = []

        if selected_batch and start_date and end_date:
            # Parse the date range
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            date_range = [start_date_obj + timedelta(days=i) for i in range((end_date_obj - start_date_obj).days + 1)]

            # Fetch admitted students for the selected batch
            admitted_students = User.objects.filter(batch__id=selected_batch).values('id', 'full_name', 'course_of_interest_id')
            students = User.objects.filter(id__in=[student['id'] for student in admitted_students]).select_related('course_of_interest')

            # Fetch attendance records for the selected date range
            attendance_records = Attendance.objects.filter(
                student__in=students,
                date__range=[start_date_obj, end_date_obj]
            ).select_related('student')

            # Map attendance data to the students
            attendance_map = defaultdict(lambda: {date: 'Not Attended' for date in date_range})
            for record in attendance_records:
                attendance_map[record.student.id][record.date] = record.status

            # Prepare the attendance data for each student
            for student in students:
                attendance_row = []
                for date in date_range:
                    attendance_row.append({
                        'date': date,
                        'status': attendance_map[student.id].get(date, 'Not Attended')
                    })
                attendance_data.append({
                    'student': student,
                    'attendance_row': attendance_row,
                    'course_name': student.course_of_interest.course_name if student.course_of_interest else ''
                })

        context = {
            'batches': batches,
            'students': students,
            'attendance_data': attendance_data,
            'date_range': date_range,
            'selected_batch': selected_batch,
            'start_date': start_date,
            'end_date': end_date
        }
        return render(request, self.template, context)

class StudentAttendanceReportView(View):
    template_name = app +'student_attendance_report.html' 

    def get(self, request):
        students = User.objects.exclude(full_name__isnull=True).exclude(full_name__exact="")        
        selected_student = request.GET.get('student', None)
        selected_course = None
        attendance_data = []
        date_range = []

        if selected_student:
            selected_student_obj = User.objects.get(id=selected_student)
            selected_course = selected_student_obj.course_of_interest

            start_date = request.GET.get('start_date', None)
            end_date = request.GET.get('end_date', None)
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                date_range = [start_date_obj + timedelta(days=i) for i in range((end_date_obj - start_date_obj).days + 1)]

                attendance_records = Attendance.objects.filter(
                    student=selected_student_obj,
                    date__range=[start_date_obj, end_date_obj]
                )

                for date in date_range:
                    status = 'Not Attended'  
                    for record in attendance_records:
                        if record.date == date:
                            status = record.status
                            break
                    attendance_data.append({'date': date, 'status': status})

        context = {
            'students': students,
            'selected_student': selected_student_obj if selected_student else None,
            'selected_course': selected_course,
            'attendance_data': attendance_data,
            'date_range': date_range,
        }
        return render(request, self.template_name, context)

class BatchDetailsView(View):
    template = app + "batch_details.html"
    
    def get(self, request,batch_id):
        try:
            batch = Batch.objects.get(id=batch_id)
            remaining_seats = batch.total_seats - batch.number_of_students
            return JsonResponse({'remaining_seats': remaining_seats})
        except Batch.DoesNotExist:
            return JsonResponse({'error': 'Batch not found'}, status=404)
    

class FilterClass(View):
    template_name = app + 'online_class_list.html'

    def get(self, request):
        # Get search query and pagination size from GET parameters
        search_query = request.GET.get('search_query', '')
        pagination_size = request.GET.get('pagination', 10)  # Default to 10 entries per page if not provided

        if search_query:
            online_classes = OnlineClass.objects.filter(course__course_name__icontains=search_query).order_by('id')
        else:
            online_classes = OnlineClass.objects.all().order_by('id')

        paginator = Paginator(online_classes, pagination_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            "online_classes": page_obj,  # Use page_obj to show paginated results
            'page_obj': page_obj,
            'search_query': search_query,
        }

        return render(request, self.template_name, context)
    

class BatchListView(View):
    template_name = app + 'batch_list.html'

    def get(self, request):
        batches = Batch.objects.all().order_by('id')
        for batch in batches:
            # Only count new admissions
            new_admissions_count = User.objects.filter(batch=batch).count()
            batch.number_of_students = new_admissions_count
            batch.save()

        search_query = request.GET.get('search_query', '').strip()
        if search_query:
            batches = batches.filter(name__icontains=search_query)

        pagination_count = request.GET.get('pagination', '10')
        if not pagination_count.isdigit():
            pagination_count = '10'
        paginator = Paginator(batches, int(pagination_count))

        page_number = request.GET.get('page', '1')
        page_obj = paginator.get_page(page_number)

        context = {
            "online_classes": page_obj.object_list,
            'page_obj': page_obj,
            'search_query': search_query,
            'pagination_count': int(pagination_count),
        }
        return render(request, self.template_name, context)

    
class AddNewBatchView(View):
    template_name = app + 'add_new_batch.html'

    def get(self, request):
        form = BatchForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:list_batches')
        return render(request, self.template_name, {'form': form})


class BatchUpdateView(UpdateView):
    model = Batch
    form_class = BatchForm
    template_name = app + 'edit_batch.html' 
    success_url = reverse_lazy('users:list_batches')

    def get_object(self, queryset=None):
        return get_object_or_404(Batch, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch = self.get_object()
        
        # Only count new admissions
        new_admissions_count = User.objects.filter(batch=batch).count()
        
        context['number_of_students'] = new_admissions_count
        return context

    def form_valid(self, form):
        batch = form.save(commit=False)
        
        # Only count new admissions
        new_admissions_count = User.objects.filter(batch=batch).count()
        
        batch.number_of_students = new_admissions_count
        batch.save()
        return redirect(self.success_url)
    
class BatchDeleteView(View):

    def delete(self, request, pk):
        try:
            batch = Batch.objects.get(pk=pk)
            batch.delete()
            return JsonResponse({'success': True}, status=200)
        except Batch.DoesNotExist:
            return JsonResponse({'error': 'Batch not found.'}, status=404)

class StudentFeesListView(View):
    model = models.User
    template = app + "student_fees.html"

    def get(self, request):
        query = request.GET.get('search', '')
        if query:
            students = self.model.objects.filter(Q(full_name__icontains=query))
        else:
            students = self.model.objects.filter(is_superuser=False, is_staff=False)

        # Fetch the latest payment date for each student
        student_data = []
        for student in students:
            # Get the latest payment for each student
            latest_payment = Payment.objects.filter(student=student).order_by('-date').first()
            
            student_data.append({
                'user': student,
                'latest_payment_date': latest_payment.date if latest_payment else None,
                'total_fees': student.total_fees,
                'fees_received': student.fees_received,
                'balance': student.balance,
            })

        total_fees = sum(data['total_fees'] for data in student_data)
        total_paid_fees = sum(data['fees_received'] or 0 for data in student_data)
        total_balance_fees = sum(data['balance'] for data in student_data)

        context = {
            "students": student_data,
            "total_fees": total_fees,
            "total_paid_fees": total_paid_fees,
            "total_balance_fees": total_balance_fees,
            "search_query": query,
        }
        return render(request, self.template, context)
    
class DeleteStudentView(View):
    def get(self, request, student_id):
        student = get_object_or_404(models.User, id=student_id)
        student.delete()
        return redirect('users:student_fees_list')
    
class StudentpaymentEdit(View):
    template_name = app + 'edit_payment.html'

    def get(self, request, pk):
        student = get_object_or_404(models.User, pk=pk)
        form = forms.StudentForm(instance=student)
        return render(request, self.template_name, {'form': form, 'student': student})

    def post(self, request, pk):
        student = get_object_or_404(models.User, pk=pk)
        form = forms.StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('users:student_fees_list')  
        return render(request, self.template_name, {'form': form, 'student': student})

def course_selection_view(request):
    selected_course = None
    if request.method == 'POST':
        course_id = request.POST.get('course')
        selected_course = Course.objects.get(id=course_id)

    courses = Course.objects.all()
    return render(request, 'course_selection.html', {
        'courses': courses,
        'selected_course': selected_course
    })

def get_course_details(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        data = {
            'total_fees': course.total_fees,
            'balance': course.balance,
            'discount_rate': course.discount_rate,
            'discount_amount': course.discount_amount,
            'fees_received': course.fees_received,
            'remarks': course.remarks,
        }
        return JsonResponse(data)
    except Course.DoesNotExist:
        return JsonResponse({'error': 'Course not found.'}, status=404)

class AllUserListView(View):
    template_name = app + 'all_users.html'

    def get(self, request):
        # Get users who are only registered (not admitted)
        registered_users = User.objects.filter(is_superuser=False, is_staff=False, is_admitted=False).order_by('id')
        
        # Get users who are admitted (students)
        admitted_students = User.objects.filter(is_superuser=False, is_staff=False, is_admitted=True).order_by('id')
        
        # Pass users to the template with additional context
        context = {
            'registered_users': registered_users,
            'admitted_students': admitted_students,
            'title': 'All Users',
        }
        return render(request, self.template_name, context)
    
class UserEditView(View):
    model = User
    template_name = 'user_edit.html'
    fields = ['username', 'email', 'profile__contact']  # Adjust fields as needed
    success_url = reverse_lazy('all_user_list')

class DeleteUserView(View):
    def delete(self, request, user_id):
        # Ensure the request is an AJAX request
        if not request.is_ajax():
            return HttpResponseBadRequest("Invalid request")

        try:
            # Fetch the user and delete
            user = get_object_or_404(User, id=user_id)
            user_id = user.id  # Save user ID for the response
            user.delete()
            return JsonResponse({'success': True, 'message': 'User deleted successfully.', 'user_id': user_id})
        except Exception as e:
            # Handle unexpected exceptions and return an error message
            return JsonResponse({'success': False, 'message': str(e)}, status=500)