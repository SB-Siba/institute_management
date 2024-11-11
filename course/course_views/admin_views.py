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
    
class EditAwardCategoryView(View):
        model = AwardCategory
        form_class = AwardCategoryForm
        success_url = reverse_lazy('course:award_categories')  # Ensure correct URL name

        def get(self, request, category_id):
            category = get_object_or_404(AwardCategory, id=category_id)
            form = AwardCategoryForm(instance=category)
            return render(request, 'award_category.html', {'form': form})

        def post(self, request, category_id):
            category = get_object_or_404(AwardCategory, id=category_id)
            form = AwardCategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success', 'category_name': form.instance.category_name})
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
class AwardCategoryDeleteView(View):
    model = AwardCategory
    form_class = AwardCategoryForm
    
    def post(self, request, category_id):
        try:
            category = AwardCategory.objects.get(id=category_id)
            category.delete()
            return redirect('course:award_categories')  # Redirect to the award category list view
        except AwardCategory.DoesNotExist:
            return JsonResponse({'error': 'Award category not found.'}, status=404)

    
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

    def get(self, request):
        form = CourseForm()
        return render(request, self.template_name, {'form': form, 'subjects': []})

    def post(self, request):
        form = CourseForm(request.POST, request.FILES)
        subjects = request.POST.getlist('course_subjects', [])

        if 'add_subject' in request.POST:
            subject_name = request.POST.get('course_subject', '').strip()
            if subject_name:
                subjects.append(subject_name)

            return render(request, self.template_name, {'form': form, 'subjects': subjects})

        elif 'delete_subject' in request.POST:
            subject_index = int(request.POST.get('delete_subject'))
            if 0 <= subject_index < len(subjects):
                subjects.pop(subject_index)

            return render(request, self.template_name, {'form': form, 'subjects': subjects})

        elif 'add_course' in request.POST:
            if form.is_valid():
                course = form.save(commit=False)
                course.course_subject = [{'id': i + 1, 'name': subject} for i, subject in enumerate(subjects)]
                course.save()
                messages.success(request, 'Course added successfully!')
                return redirect('course:course_list')  
            return render(request, self.template_name, {'form': form, 'subjects': subjects})

        return render(request, self.template_name, {'form': form, 'subjects': []})

    
class CourseEditView(View):
    template_name = app + 'edit_course.html'

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        form = CourseForm(instance=course)

        # Load existing subjects from the course's JSONField
        subjects = course.course_subject if course.course_subject else []

        return render(request, self.template_name, {
            'form': form,
            'subjects': subjects,
            'course': course
        })

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        form = CourseForm(request.POST, request.FILES, instance=course)
        subjects = course.course_subject if course.course_subject else []

        if 'add_subject' in request.POST:
            subject_name = request.POST.get('course_subject', '').strip()

            if subject_name:
                # Append new subject to the list, ensuring each has a unique ID
                subjects.append({'id': len(subjects) + 1, 'name': subject_name})

            return render(request, self.template_name, {
                'form': form,
                'subjects': subjects,
                'course': course
            })

        elif 'delete_subject' in request.POST:
            subject_index = int(request.POST.get('delete_subject'))

            if 0 <= subject_index < len(subjects):
                subjects.pop(subject_index)  # Remove the selected subject

            return render(request, self.template_name, {
                'form': form,
                'subjects': subjects,
                'course': course
            })

        elif 'edit_course' in request.POST:
            if form.is_valid():
                course = form.save(commit=False)

                # Save updated subjects as JSON in the course_subject field
                course.course_subject = [{'id': subject['id'], 'name': subject['name']} for subject in subjects]
                course.save()

                # Redirect to course list after successful edit
                messages.success(request, 'Course updated successfully!')
                return redirect('course:course_list')
            else:
                return render(request, self.template_name, {
                    'form': form,
                    'subjects': subjects,
                    'course': course
                })

        return render(request, self.template_name, {
            'form': form,
            'subjects': subjects,
            'course': course
        })

    
class CourseDeleteView(View):
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('pk')
        course = get_object_or_404(Course, id=course_id)
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('course:course_list')