from decimal import Decimal
from pyexpat.errors import messages
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