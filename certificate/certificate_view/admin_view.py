from multiprocessing import Value
from django.contrib import messages
from django.forms import CharField
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from certificate.forms import ApplyCertificateForm, SearchForm
from certificate.models import AppliedCertificate
from course.models import Course, ExamResult
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.db.models import Q
from django.core.exceptions import FieldError
from django.db.models.functions import Concat


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
            batch = form.cleaned_data['batch']
            course = form.cleaned_data['course']

            # Get the user model dynamically
            User = get_user_model()

            # Filter users by selected batch and course
            users_in_batch_course = User.objects.filter(batch=batch, course_of_interest=course)

            if users_in_batch_course.exists():
                # If users are found, apply certificates
                for user in users_in_batch_course:
                    AppliedCertificate.objects.create(user=user, batch=batch, course=course)

                # Success message for applied certificates
                messages.success(request, 'Certificate applications submitted for all students in the selected batch and course!')
            else:
                # Show an alert message if no users found
                messages.warning(request, 'No students found for the selected batch and course.')

            # Reset the form after processing
            form = self.form_class()

        return render(request, self.template_name, {'form': form})
    

class AppliedCertificateListView(View):
    template_name = app + 'applied_certificates.html'  # Corrected template path

    def get(self, request):
        # Get search parameters from the GET request
        full_name_query = request.GET.get('full_name', '')
        course_query = request.GET.get('course', '')
        batch_query = request.GET.get('batch', '')

        # Fetch all applications initially
        applications = AppliedCertificate.objects.all()

        try:
            # Apply filters based on the query parameters
            if full_name_query:
                applications = applications.annotate(
                    full_name=Concat('user__first_name', 'user__last_name', output_field=CharField())
                        ).filter(full_name__icontains=full_name_query)
        except FieldError as e:
            print(f"FieldError: {e}")

        if course_query:
            applications = applications.filter(course__course_name__icontains=course_query)

        if batch_query:
            applications = applications.filter(batch__name__icontains=batch_query)

        # Fetch exam results for the logged-in user
        exam_results = ExamResult.objects.filter(student=request.user)

        # Pass the filtered data to the template
        context = {
            'applications': applications,
            'exam_results': exam_results,
        }

        return render(request, self.template_name, context)


    
class DeleteAppliedCertificateView(View):
    def post(self, request, pk):
        applied_certificate = get_object_or_404(AppliedCertificate, pk=pk)
        applied_certificate.delete()
        return redirect('certificate:applied_certificates')  
    