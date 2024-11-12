import json
from msilib.schema import ListView
from winreg import DeleteKey
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from course.forms import AwardCategoryForm, CourseForm, ExamapplyForm
from course.models import AwardCategory, Course, Exam, ExamResult

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

        if 'add_subject' in request.POST:
            subject_name = request.POST.get('course_subject', '').strip()
            subjects = request.POST.getlist('subjects', [])

            if subject_name:
                # Add the new subject to the subjects list
                subjects.append(subject_name)
            
            return render(request, self.template_name, {'form': form, 'subjects': subjects})

        elif 'delete_subject' in request.POST:
            subject_index = int(request.POST.get('delete_subject'))
            subjects = request.POST.getlist('subjects', [])

            if 0 <= subject_index < len(subjects):
                subjects.pop(subject_index)

            return render(request, self.template_name, {'form': form, 'subjects': subjects})

        elif 'add_course' in request.POST:
            subjects = request.POST.getlist('subjects', [])
            if form.is_valid():
                course = form.save(commit=False)

                # Save subjects as JSON in the course_subject field
                course.course_subject = [{'id': i + 1, 'name': subject} for i, subject in enumerate(subjects)]
                course.save()

                # Redirect to course list after successful save
                messages.success(request, 'Course added successfully!')
                return redirect('course:course_list')  # Adjust the URL name as per your config
            else:
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



class ExamApply(View):
    template_name = app +'exam_apply.html'  # Adjust `app` to your actual template directory name
    success_url = reverse_lazy('course:exam_list')  # Redirect URL on successful form submission
    exam_data = []

    def get(self, request):
        form = ExamapplyForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ExamapplyForm(request.POST)
        if form.is_valid():
            # Save a new Exam instance with all fields from the form
            new_exam = form.save(commit=False)  # We use commit=False so we can add extra logic before saving
            new_exam.save()  # Save the exam instance to the database
            return redirect(self.success_url)

        # If the form is not valid, render the form with errors
        return render(request, self.template_name, {'form': form})


class ExamListView(View):
    template_name = app +'exam_list.html'

   
    def get(self, request):
        search_query = request.GET.get('q', '').strip()  # Default to empty string if no query
        exams = Exam.objects.all() 
        if search_query:
            exams = exams.filter(exam_name__icontains=search_query)  # Fetch all exams from the database
        return render(request, self.template_name, {'exams': exams,'search_query': search_query})

    def post(self, request):
        # Implement search/filter functionality as before
        search_query = request.POST.get('search_query', '').strip()
        filter_course = request.POST.get('filter_course')
        filter_date = request.POST.get('filter_date')

        exams = Exam.objects.all()
        if search_query:
            exams = exams.filter(name__icontains=search_query)
        if filter_course:
            exams = exams.filter(course__course_name=filter_course)
        if filter_date:
            exams = exams.filter(date=filter_date)

        return render(request, self.template_name, {'exams': exams, 'search_query': search_query})

class DeleteExamView(View):
  
    def post(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs['pk'])
        exam.delete()
        return redirect('course:exam_list')

class EditExamView(View):
    template_name = app + 'exam_edit.html'  # Template for the edit exam form
    success_url = reverse_lazy('course:exam_list')  # Redirect to the exam list after editing

    def get(self, request, *args, **kwargs):
        # Get the exam object to be edited using the primary key (pk) from the URL
        exam = get_object_or_404(Exam, pk=kwargs['pk'])
        
        # Make sure only staff members or admins can edit the exam
        if not request.user.is_staff:
            messages.error(request, "You are not authorized to edit this exam.")
            return redirect(self.success_url)
        
        # Prepopulate the form with the existing exam data
        form = ExamapplyForm(instance=exam)
        
        return render(request, self.template_name, {'form': form, 'exam': exam})

    def post(self, request, *args, **kwargs):
        # Get the exam object to be edited
        exam = get_object_or_404(Exam, pk=kwargs['pk'])
        
        # Make sure only staff members or admins can edit the exam
        if not request.user.is_staff:
            messages.error(request, "You are not authorized to edit this exam.")
            return redirect(self.success_url)
        
        # Bind the form with the POST data and the current exam instance
        form = ExamapplyForm(request.POST, instance=exam)
        
        # Validate the form
        if form.is_valid():
            # Save the updated exam object
            form.save()
            messages.success(request, "Exam updated successfully.")
            return redirect(self.success_url)  # Redirect to the success_url after saving the form

        # If the form is invalid, render the form with errors
        return render(request, self.template_name, {'form': form, 'exam': exam})

