from django.shortcuts import render
from django.views import View
from certificate.forms import SearchForm
from certificate.models import ExamResult

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
        # You can pass any context data here if needed
        context = {
            # For example, you can pass dynamic data to the template
            'certificate_holder': 'JITENDRA PRADHAN',
            'score': '73.20%',
            'course': 'POST GRADUATE DIPLOMA IN COMPUTER APPLICATION',
            # Add other data as needed
        }
        return render(request, self.template_name, context)
