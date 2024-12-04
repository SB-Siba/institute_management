from django.http import HttpResponseNotAllowed, JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from course.models import Course, ExamResult


app = "course/user/"

class UserCourseListView(View):
    template_name = app + 'course_list.html'

    def get(self, request):
        search_query = request.GET.get('q', '')
        courses = Course.objects.filter(
            course_name__icontains=search_query,
            status='Active'
        ).order_by('id')

        paginator = Paginator(courses, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query
        }
        return render(request, self.template_name, context)

class ExamResultsView(View):
    template_name = app + 'exam_results.html'  

    def get(self, request, *args, **kwargs):
        # Retrieve exam results for the logged-in user
        exam_results = ExamResult.objects.filter(student=request.user).order_by('-created_on')

        for result in exam_results:
            # Calculate percentage and result dynamically (can also be handled in save method)
            result.percentage = (result.obtained_mark / result.total_mark) * 100
            result.result = 'Passed' if result.percentage >= 50 else 'Failed'

        # Extract grade choices for the filter dropdown
        grades = [choice[0] for choice in ExamResult._meta.get_field('grade').choices]

        # Pass the data to the context
        context = {
            'exam_results': exam_results,
            'grades': grades,
        }

        return render(request, self.template_name, context)

class CourseDetailView(View):
    model = Course
    template_name = app + "course_detail.html"
    context_object_name = "course"
    
    def get(self, request, pk, *args, **kwargs):
        # Fetch the course object
        course = get_object_or_404(Course, pk=pk)
        context = {
            'course': course
        }
        # Render the course detail template
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        # Example logic for handling POST data (e.g., form submission)
        course = get_object_or_404(Course, pk=pk)
        action = request.POST.get('action', None)  # Example action parameter
        if action == 'enroll':  # Example: enroll in a course
            # Perform some logic here, e.g., add the user to the course
            return JsonResponse({'message': 'Successfully enrolled in the course!'}, status=200)
        return JsonResponse({'error': 'Invalid action'}, status=400)