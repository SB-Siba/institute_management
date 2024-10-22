import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from course.models import Course
from course.forms import CourseForm


from course.forms import AwardCategoryForm, CourseForm
from course.models import AwardCategory, Course

app = "course/admin/"

class AwardCategoryListView(View):
    template_name = app + 'award_categories.html'
    
    def get(self, request):
        search_query = request.GET.get('q', '')
        award_categories = AwardCategory.objects.filter(category_name__icontains=search_query).order_by('id')
        
        # Pagination
        paginator = Paginator(award_categories, 10)  # Show 10 categories per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query
        }
        return render(request, self.template_name, context)

class AwardCategoryCreateView(View):
    form_class = AwardCategoryForm
    template_name = app + 'add_award_category.html'
    success_url = reverse_lazy('course:award_categories')

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})
    
class AwardCategoryUpdateView(View):
    model = AwardCategory
    form_class = AwardCategoryForm
    template_name = 'edit_award_category_form.html'
    context_object_name = 'category'

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({'status': 'success', 'category_name': self.object.name})

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'errors': form.errors})
    
class AwardCategoryDeleteView(View):
    model = AwardCategory

    def post(self, request, *args, **kwargs):
        category = get_object_or_404(self.model, pk=kwargs.get('pk'))
        category.delete()
        return JsonResponse({'status': 'success'})
    
class CourseListView(View):
    template_name = app + 'course_list.html'

    def get(self, request):
        search_query = request.GET.get('q', '')
        # Updated the field name to course_name
        courses = Course.objects.filter(course_name__icontains=search_query).order_by('id')
        
        # Pagination
        paginator = Paginator(courses, 10)  # Show 10 courses per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query
        }
        return render(request, self.template_name, context)

class CourseCreateView(View):
    template_name = app + 'add_course.html'

    def get(self, request, pk=None):
        if pk:  # Editing an existing course
            course = get_object_or_404(Course, pk=pk)
            form = CourseForm(instance=course)
            subjects = [subject.strip() for subject in course.course_subject.split(',')] if course.course_subject else []
        else:  # Adding a new course
            course = None
            form = CourseForm()
            subjects = []

        return render(request, self.template_name, {'form': form, 'course': course, 'subjects': subjects})

    def post(self, request, pk=None):
        # Initialize course variable to avoid UnboundLocalError
        course = None

        if pk:  # Editing an existing course
            course = get_object_or_404(Course, pk=pk)
            form = CourseForm(request.POST, request.FILES, instance=course)
        else:  # Adding a new course
            form = CourseForm(request.POST, request.FILES)

        if form.is_valid():
            course = form.save(commit=False)

            # Get subjects from the hidden input
            subjects_json = request.POST.get('subjects')
            if subjects_json:
                existing_subjects = json.loads(subjects_json)  # Load JSON string to list
                course.course_subject = ', '.join(existing_subjects)  # Join subjects into a single string

            course.save()

            messages.success(request, "Course added successfully!")  # Flash message
            return redirect(reverse_lazy('course:course_list'))
        else:
            print(form.errors)
        # If form is invalid, retrieve existing subjects if editing
        existing_subjects = course.course_subject.split(',') if course and course.course_subject else []

        return render(request, self.template_name, {'form': form, 'course': course, 'subjects': existing_subjects})

class CourseEditView(View):
    template_name = app + 'edit_course.html'  # Adjust to your actual template path

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        form = CourseForm(instance=course)

        # Split existing subjects and clean up whitespace
        subjects = [subject.strip() for subject in course.course_subject.split(',')] if course.course_subject else []

        return render(request, self.template_name, {
            'form': form,
            'course': course,
            'subjects': subjects  # Pass existing subjects to the template
        })

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        form = CourseForm(request.POST, request.FILES, instance=course)

        if form.is_valid():
            # Save the updated course instance
            course = form.save(commit=False)

            # Get existing subjects and new subjects from the form
            existing_subjects = [subject.strip() for subject in course.course_subject.split(',')] if course.course_subject else []
            new_subjects = request.POST.getlist('course_subject')

            # Combine existing and new subjects, remove duplicates and empty entries
            all_subjects = list(set(existing_subjects + [subject.strip() for subject in new_subjects if subject.strip()]))

            # Join them into a single string and save
            course.course_subject = ', '.join(all_subjects)
            course.save()  # Save the updated course instance

            return redirect(reverse_lazy('course:course_list'))  # Redirect after saving

        # If form is not valid, render the form again with existing subjects
        subjects = [subject.strip() for subject in course.course_subject.split(',')] if course.course_subject else []
        
        return render(request, self.template_name, {
            'form': form,
            'course': course,
            'subjects': subjects  # Make sure this variable is defined here
        })

    
class CourseDeleteView(View):
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('pk')
        course = get_object_or_404(Course, id=course_id)
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('course:course_list')