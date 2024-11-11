from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator
from course.models import Course


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
