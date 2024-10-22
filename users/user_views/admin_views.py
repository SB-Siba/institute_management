from collections import defaultdict
from decimal import Decimal
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from helpers import utils
from django.forms import formset_factory, modelformset_factory
from users import models,forms
from users.forms import BatchForm, OnlineClassForm, StudentForm, InstallmentForm, StudentPaymentForm
from django.forms import formset_factory 
from users.models import Installment, OnlineClass, Payment, Batch, ReferralSettings, User
from course.models import Course
import csv
from django.http import HttpResponse
from django.contrib import messages
from datetime import date, datetime, timedelta
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import UpdateView

from users.models import Attendance
app = "users/admin/"

# admin dashboard and manage users list

@method_decorator(utils.super_admin_only, name='dispatch')
class AdminDashboard(View):
    template = app + "index.html"  # Update the template path if necessary

    def get(self, request):
        return render(request, self.template)

class StudentListView(View):
    template_name = app + 'student_list.html'  # Adjust the path as needed
    
    def get(self, request):
        search_query = request.GET.get('q', '')
        students = models.User.objects.filter(full_name__icontains=search_query).order_by('id')
        
        # Pagination
        paginator = Paginator(students, 10)  # Show 10 students per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query
        }
        return render(request, self.template_name, context)

class ExportStudentsView(View):
    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        # Write the headers for the CSV file
        writer.writerow([
            'S/N', 'Status', 'Batch', 'Student Name', 'Course Interested',
            'Username', 'Password', 'Mobile', 'Referral Code',
            'Referral Name', 'Admission Date'
        ])

        # Write student data to CSV
        students = models.User.objects.all()
        for idx, student in enumerate(students, start=1):
            writer.writerow([
                idx, student.status, student.batch, student.full_name,
                student.course_of_interest, student.username, student.password,
                student.contact, student.referral_code, student.referral_name,
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

class AddNewStudentView(View):
    model = models.User
    template = app + 'add_new_student.html'  # Update this path as needed

    def get(self, request):
        user_form = StudentForm()
        InstallmentFormSet = formset_factory(InstallmentForm, extra=1)
        installment_formset = InstallmentFormSet()
        batch = Batch.objects.all()
        courses = Course.objects.all()
        return render(request, self.template, {
            'user_form': user_form,
            'installment_formset': installment_formset,
            'courses': courses,
        })

    def post(self, request):
        user_form = StudentForm(request.POST, request.FILES)  # Ensure request.FILES is passed
        InstallmentFormSet = formset_factory(InstallmentForm, extra=1)
        installment_formset = InstallmentFormSet(request.POST)

        if user_form.is_valid() and installment_formset.is_valid():
            try:
                # Save the student form, including the file upload
                student = user_form.save(commit=False)

                # Check if student_image file is uploaded
                if 'student_image' in request.FILES:
                    student.student_image = request.FILES['student_image']

                student.save()

                # Save the installment forms
                for form in installment_formset:
                    if form.cleaned_data and form.cleaned_data.get('installment_name'):
                        installment = form.save(commit=False)
                        installment.student = student  # Link the installment to the student
                        installment.save()
                messages.success(request, 'Student added successfully!')
                return redirect('users:student_list')

            except ValueError as e:
                messages.error(request, f"There was an error: {e}")
        else:
            # Handle form validation errors
            print("User form errors:", user_form.errors)
            print("Installment formset errors:", installment_formset.errors)

        return render(request, self.template, {
            'user_form': user_form,
            'installment_formset': installment_formset
        })
    
class StudentUpdateView(View):
    model = User
    form_class = StudentForm
    template_name = app + 'student_update.html'
    success_url = reverse_lazy('student_list')

    def get_object(self):
        # Fetch the User object you want to update
        return get_object_or_404(User, pk=self.kwargs['pk'])

    def get_installment_formset(self, instance=None, data=None):
        # Create the Installment formset
        InstallmentFormSet = modelformset_factory(
            Installment, 
            fields=('installment_name', 'amount', 'date'), 
            extra=1
        )
        if data:
            return InstallmentFormSet(data, queryset=instance.installments.all())
        else:
            return InstallmentFormSet(queryset=instance.installments.all())

    def get_context_data(self, form=None, installment_formset=None):
        # Prepare context data for the template
        if form is None:
            form = self.form_class(instance=self.get_object())
        if installment_formset is None:
            installment_formset = self.get_installment_formset(instance=self.get_object())

        return {
            'form': form,
            'installment_formset': installment_formset,
        }

    def get(self, request, *args, **kwargs):
        # Handle GET requests
        user = self.get_object()
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Handle POST requests (submitting the form)
        user = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=user)
        installment_formset = self.get_installment_formset(instance=user, data=request.POST)

        if form.is_valid() and installment_formset.is_valid():
            # Save the student form
            form.save()

            # Save the installment formset
            installments = installment_formset.save(commit=False)
            for installment in installments:
                installment.student = user  # Associate the installment with the student (user)
                installment.save()
            
            # Save any deleted installments
            installment_formset.save()

            # Redirect to the student list after successful update
            return redirect(self.success_url)
        else:
            # If form or formset is invalid, render the template with errors
            context = self.get_context_data(form, installment_formset)
            return render(request, self.template_name, context)
        
class StudentDeleteView(View):
    def delete(self, request, pk):
        try:
            student = models.User.objects.get(pk=pk)
            student.delete()
            return JsonResponse({'success': True}, status=200)
        except models.User.DoesNotExist:
            return JsonResponse({'error': 'Student not found.'}, status=404)

class CourseDetailsView(View):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            data = {
                'total_fees': course.total_fees,  # Replace with actual fields from your Course model
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
    template_name = app + 'students_payment_list.html'

    def get(self, request):
        payment_obj = self.model.objects.select_related('student').order_by('date')        
        return render(request, self.template_name, {'payments': payment_obj})

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

    def get(self, request):
        form = self.form_class()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:student_payment_list')
        return render(request, self.template, {'form': form})

class TakeAttendanceView(View):
    template =  app + "take_attendance.html"  # Adjust the template path according to your structure

    def get(self, request):
        today_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
        selected_batch = request.GET.get('batch', None)

        # Fetch batches and students based on the selected batch
        batches = Batch.objects.all()
        students = User.objects.filter(batch__id=selected_batch) if selected_batch else None
        attendance_records = Attendance.objects.filter(date=today_date, student__batch__id=selected_batch) if selected_batch else []

        # Create a dictionary to store attendance status by student ID
        attendance_status_map = {record.student.id: record.status for record in attendance_records}

        context = {
            'today_date': today_date,
            'batches': batches,
            'students': students,
            'attendance_status_map': attendance_status_map,  # Pass the attendance status map
            'selected_batch': selected_batch
        }
        return render(request, self.template, context)

    def post(self, request):
        selected_batch = request.POST.get('batch')
        attendance_date = request.POST.get('date', date.today())

        students = User.objects.filter(batch__id=selected_batch)

        # Update or create attendance records for each student
        for student in students:
            attendance_status = request.POST.get(f'attendance_{student.id}')
            Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                defaults={'status': attendance_status}
            )

        return redirect('users:take_attendance')
    
class AttendanceReportView(View):
    template = app + "attendance_report.html"

    def get(self, request):
        selected_batch = request.GET.get('batch', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        # Fetch all batches
        batches = Batch.objects.all()

        students = None
        attendance_data = []
        date_range = []

        if selected_batch and start_date and end_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            date_range = [start_date_obj + timedelta(days=i) for i in range((end_date_obj - start_date_obj).days + 1)]

            # Fetch students enrolled in the selected batch
            students = User.objects.filter(batch__id=selected_batch).select_related('course_of_interest')

            # Fetch attendance records for students in the selected batch
            attendance_records = Attendance.objects.filter(
                student__batch__id=selected_batch,
                date__range=[start_date_obj, end_date_obj]
            ).select_related('student')

            # Create a map for attendance data, defaulting to 'Not Attended'
            attendance_map = defaultdict(lambda: {date: 'Not Attended' for date in date_range})

            # Populate attendance_map with attendance records
            for record in attendance_records:
                attendance_map[record.student.id][record.date] = record.status

            # Prepare attendance data for each student
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
    template_name = app +'student_attendance_report.html'  # Adjust your template path

    def get(self, request):
        students = User.objects.all()  # Fetch all students
        selected_student = request.GET.get('student', None)
        selected_course = None
        attendance_data = []
        date_range = []

        if selected_student:
            selected_student_obj = User.objects.get(id=selected_student)
            selected_course = selected_student_obj.course_of_interest

            # Set up the date range for attendance
            start_date = request.GET.get('start_date', None)
            end_date = request.GET.get('end_date', None)
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                date_range = [start_date_obj + timedelta(days=i) for i in range((end_date_obj - start_date_obj).days + 1)]

                # Fetch attendance records for the selected student and date range
                attendance_records = Attendance.objects.filter(
                    student=selected_student_obj,
                    date__range=[start_date_obj, end_date_obj]
                )

                # Build the attendance_data list with date and status
                for date in date_range:
                    status = 'Not Attended'  # Default status
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
    
    def get(self, request):
        # Retrieve all batches from the database
        batches = Batch.objects.all()
        context = {'batches': batches}
        return render(request, self.template, context)

class ReferralAmountView(View):
    template = app + "referral_amount.html"

    def get(self, request):
        referral_settings = ReferralSettings.objects.first()
        context = {'referral_amount': referral_settings.amount if referral_settings else 300.00}
        return render(request, self.template, context)

    def post(self, request):
        new_amount = request.POST.get('amount', 300.00)
        referral_settings, created = ReferralSettings.objects.get_or_create(id=1)
        referral_settings.amount = new_amount
        referral_settings.save()

        return redirect('users:referral_amount')
class OnlineClassListView(View):
    template_name = app + 'online_class_list.html'

    def get(self, request):

        online_classes = OnlineClass.objects.all().order_by('id')
 
        paginator = Paginator(online_classes, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            "online_classes":online_classes,
            'page_obj': page_obj,
        }

        return render(request, self.template_name, context)
    

class FilterClass(View):
    template_name = app + 'online_class_list.html'

    def get(self, request):
        # Get search query and pagination size from GET parameters
        search_query = request.GET.get('search_query', '')
        pagination_size = request.GET.get('pagination', 10)  # Default to 10 entries per page if not provided

        # Filter the online classes based on the search query (or show all if no query is provided)
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
    
class AddOnlineClassView(View):
    form_class = OnlineClassForm
    template_name = app + 'add_online_class.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:online_class_notifications")
        return render(request, self.template_name, {'form': form})

class BatchListView(View):
    template_name = app + 'batch_list.html'

    def get(self, request):
        batches = Batch.objects.all().order_by('id')
        paginator = Paginator(batches, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            "online_classes": page_obj.object_list,
            'page_obj': page_obj,
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
        students = self.model.objects.all()

        context = {
            "students": students,
        }
        return render(request, self.template, context)

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

