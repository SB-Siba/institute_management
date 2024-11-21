import logging
from multiprocessing import Value
from django.contrib import messages
from django.forms import CharField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from certificate.forms import ApplyCertificateForm, SearchForm
from certificate.models import ApprovedCertificate, ApprovedCertificate, Requested
from course.models import Course, ExamResult
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.db.models import Q
from django.core.exceptions import FieldError
from django.db.models.functions import Concat
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
    
class DesignedCertificateView(View):
    template_name = app + 'designed_certificate.html'

    def get(self, request, *args, **kwargs):
        context = {
            # For example, you can pass dynamic data to the template
            'certificate_holder': 'JITENDRA PRADHAN',
            'score': '73.20%',
            'course': 'POST GRADUATE DIPLOMA IN COMPUTER APPLICATION',
            # Add other data as needed
        }
        return render(request, self.template_name, context)\
        
class ApplyCertificateView(View):
    form_class = ApplyCertificateForm
    template_name = 'certificate/apply_certificate.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            batch = form.cleaned_data['batch']
            course = form.cleaned_data['course']

            users = User.objects.filter(batch=batch, course_of_interest=course)
            if not users.exists():
                messages.warning(request, "No students found for the selected batch and course.")
                return render(request, self.template_name, {'form': form})

            for user in users:
                exam_result = ExamResult.objects.filter(student=user, course=course).first()
                exam_data = None
                if exam_result:
                    exam_data = {
                        'subjects': exam_result.subjects_data,
                        'percentage': exam_result.percentage,
                        'grade': exam_result.grade,
                        'result': exam_result.result,
                    }
                Requested.objects.create(
                    user=user, course=course, batch=batch, exam_data=exam_data
                )

            messages.success(request, "Certificates applied successfully.")
            return redirect('certificate:requested_certificates')
        return render(request, self.template_name, {'form': form})


class RequestedCertificatesListView(View):
    template_name = app + 'requested_certificates.html'

    def get(self, request):
        applications = Requested.objects.all()
        context = {'applications': applications}
        return render(request, self.template_name, context)

    def post(self, request, application_id):
        application = get_object_or_404(Requested, id=application_id)
        action = request.POST.get('action')

        if action == 'approve':
            application.status = 'Approved'
            application.is_approved = True
            application.save()
            ApprovedCertificate.objects.create(
                user=application.user, 
                course=application.course, 
                batch=application.batch
            )
        elif action == 'reject':
            application.status = 'Rejected'
            application.save()
        return JsonResponse({'status': application.status})


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
    

@method_decorator(csrf_exempt, name='dispatch')
class DeleteCertificateApplicationView(View):
    def delete(self, request, pk):
        # Fetch the application and delete it
        application = get_object_or_404(ApprovedCertificate, pk=pk)
        application.delete()
        return JsonResponse({'success': True, 'message': 'Application deleted successfully.'})

class RequestedCertificatesListView(View):
    template_name = app + 'requested_certificates.html'

    def get(self, request):
        # Fetch search parameters and filter requested certificates
        full_name_query = request.GET.get('full_name', '').strip()
        course_query = request.GET.get('course', '').strip()
        batch_query = request.GET.get('batch', '').strip()

        applications = Requested.objects.filter(status = 'Approved')

        if full_name_query:
            applications = applications.filter(user__full_name__icontains=full_name_query)

        if course_query:
            applications = applications.filter(course__icontains=course_query)

        if batch_query:
            applications = applications.filter(batch__icontains=batch_query)

        

        context = {'applications': applications}
        return render(request, self.template_name, context)

    def post(self, request):
        # Handle certificate approval
        certificate_id = request.POST.get('certificate_id')
        if certificate_id:
            try:
                requested_certificate = Requested.objects.get(id=certificate_id)
                ApprovedCertificate.objects.create(
                    user=requested_certificate.user,
                    batch=requested_certificate.batch,
                    course=requested_certificate.course,
                )
                requested_certificate.is_approved = True
                requested_certificate.save()
                messages.success(request, 'Certificate approved successfully!')
            except Requested.DoesNotExist:
                messages.error(request, 'Requested certificate not found.')

        return redirect('requested-certificates')
    
class DeleteAppliedCertificateView(View):
    def post(self, request, pk):
        applied_certificate = get_object_or_404(ApprovedCertificate, pk=pk)
        applied_certificate.delete()
        return redirect('certificate:applied_certificates')  
    
    
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


class UpdateCertificateView(View):
    model = ApprovedCertificate
    template_name = app + 'update_certificate.html'
    fields = ['user', 'batch', 'course']  # Editable fields for updating certificates

    def get(self, request, pk):
        """Handles GET requests to display the form."""
        application = get_object_or_404(ApprovedCertificate, pk=pk)

        # Populate context with dynamic fields
        context = {
            'application': application,
            'student_name_on_marksheet': application.user.full_name,
            'father_name': application.user.father_name,  # Assuming this field exists
            'surname_name': application.user.surname,
            'mother_name': application.user.mother_name,
            'date_of_birth': application.user.date_of_birth,
            'subjects': application.course.course_subject,  # Assuming subjects stored in JSONField
            'exam_title': "POST GRADUATE DIPLOMA IN COMPUTER APPLICATION",
            'certificate_no': f"PGDCA-{application.pk:05d}",
            'certificate_date': application.applied_date.strftime('%d %b %Y'),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """Handles POST requests to update the certificate."""
        application = get_object_or_404(ApprovedCertificate, pk=pk)

        # Update fields from form submission
        application.user.full_name = request.POST.get('student_name_on_marksheet')
        application.user.father_name = request.POST.get('father_name')
        application.user.surname = request.POST.get('surname_name')
        application.user.mother_name = request.POST.get('mother_name')
        application.user.date_of_birth = request.POST.get('date_of_birth')

        # Assuming `subjects` and other data are submitted in JSON format
        application.course.course_subject = request.POST.get('subjects')

        # Save changes
        application.save()
        messages.success(request, "Certificate updated successfully!")
        return redirect('certificate:approved-certificates')
