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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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

class RequestedCertificateListView(View):
    template_name = app + 'requested_certificates.html'

    def get(self, request):
        # Fetch search parameters from the GET request
        full_name_query = request.GET.get('full_name', '').strip()
        course_query = request.GET.get('course', '').strip()
        batch_query = request.GET.get('batch', '').strip()

        # Start with all applications
        applications = AppliedCertificate.objects.all()

        try:
            # Apply filter for full name if a query is provided
            if full_name_query:
                applications = applications.annotate(
                    full_name=Concat(
                        'user__first_name', Value(' '), 'user__last_name', output_field=CharField()
                    )
                ).filter(full_name__icontains=full_name_query)
        except FieldError as e:
            print(f"FieldError: {e}")

        # Apply additional filters based on other query parameters
        if course_query:
            applications = applications.filter(course__course_name__icontains=course_query)

        if batch_query:
            applications = applications.filter(batch__name__icontains=batch_query)

        # Fetch exam results for the logged-in user (assuming this is required)
        exam_results = ExamResult.objects.filter(student=request.user)

        # Pagination (if needed)
        paginator = Paginator(applications, 10)  # Display 10 applications per page
        page = request.GET.get('page', 1)

        try:
            applications = paginator.page(page)
        except PageNotAnInteger:
            applications = paginator.page(1)
        except EmptyPage:
            applications = paginator.page(paginator.num_pages)

        # Pass the filtered and paginated data to the template
        context = {
            'applications': applications,
            'exam_results': exam_results,
            'full_name_query': full_name_query,
            'course_query': course_query,
            'batch_query': batch_query,
        }

        return render(request, self.template_name, context)
    
class DeleteAppliedCertificateView(View):
    def post(self, request, pk):
        applied_certificate = get_object_or_404(AppliedCertificate, pk=pk)
        applied_certificate.delete()
        return redirect('certificate:applied_certificates')  
    