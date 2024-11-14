import json
from msilib.schema import ListView
from winreg import DeleteKey
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from course.forms import AwardCategoryForm, CourseForm, ExamResultForm, ExamapplyForm
from course.models import AwardCategory, Course, Exam, ExamResult
from users.models import User

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
                if not course.status:
                    course.status = 'active'
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



class ExamApply(View):
    template_name = app +'exam_apply.html'  # Adjust 
    success_url = reverse_lazy('course:exam_list')  
    exam_data = []

    def get(self, request):
        form = ExamapplyForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ExamapplyForm(request.POST)
        if form.is_valid():
            new_exam = form.save(commit=False) 
            subject_names = form.cleaned_data.get('subjects', [])
            new_exam.course_subject = [{"name": name} for name in subject_names]
            new_exam.save() 
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})

class GetCourseSubjectsView(View):
    def get(self, request, course_id):
        try:
            # Fetch the course based on the given ID
            course = Course.objects.get(id=course_id)
            
            # Ensure `course_subject` contains a list of dictionaries
            subjects = course.course_subject if course.course_subject else []
            return JsonResponse({'subjects': subjects})
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)
    
class ExamListView(View):
    template_name = app +'exam_list.html'

   
    def get(self, request):  
        exams = Exam.objects.all()
        search_query = request.GET.get('q', '').strip() 
        if search_query:
            exams = exams.filter(exam_name__icontains=search_query) 
        return render(request, self.template_name, {'exams': exams})

    def post(self, request):
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
    template_name = app + 'exam_edit.html'  
    success_url = reverse_lazy('course:exam_list')  
    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs['pk'])
        
        if not request.user.is_staff:
            messages.error(request, "You are not authorized to edit this exam.")
            return redirect(self.success_url)
        form = ExamapplyForm(instance=exam)
        initial_subjects = [subject['name'] for subject in exam.course.course_subject]  
        form.fields['subjects'].initial = initial_subjects
        return render(request, self.template_name, {'form': form, 'exam': exam})

    def post(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs['pk'])
        if not request.user.is_staff:
            messages.error(request, "You are not authorized to edit this exam.")
            return redirect(self.success_url)
        form = ExamapplyForm(request.POST, instance=exam)
        
        if form.is_valid():
            updated_exam = form.save(commit=False)
            subject_names = form.cleaned_data.get('subjects', [])            
            updated_exam.course_subject = [{"name": name} for name in subject_names]            
            updated_exam.save()
            messages.success(request, "Exam updated successfully.")
            return redirect(self.success_url)  
        return render(request, self.template_name, {'form': form, 'exam': exam})

class ExamResultListView(View):
    template_name = app + 'exam_result_list.html'
    
    def get(self, request, *args, **kwargs):
        # Fetch all results, order by creation date
        exam_results = ExamResult.objects.all().order_by('-created_on')
        
        # Apply filtering by grade if a grade is selected
        grade = request.GET.get('grade')
        if grade:
            exam_results = exam_results.filter(grade=grade)
        
        # Fetch list of unique grades for the dropdown
        grades = [choice[0] for choice in ExamResult._meta.get_field('grade').choices]
        
        # Prepare context data for the template
        context = {
            'exam_results': exam_results,
            'grades': grades,
        }
        return render(request, self.template_name, context)
    
class AddStudentResultsView(View):
    template_name = app + 'add_exam_result.html'  # Adjust the template path as needed

    def get(self, request, *args, **kwargs):
        form = ExamResultForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        course_id = request.POST.get('course')
        student_id = request.POST.get('student')

        if not course_id or not student_id:
            return JsonResponse({'error': 'Course and Student are required'}, status=400)

        course = get_object_or_404(Course, id=course_id)
        student = get_object_or_404(User, id=student_id)
        subjects = course.course_subject if course.course_subject else []
        print(subjects)
        print(student)
        print(course)
        form = ExamResultForm(request.POST, subjects=subjects)
        if form.is_valid():
            for idx, subject in enumerate(subjects):
                ExamResult.objects.create(
                    student=student,
                    course=course,
                    subject=subject,
                    theory_marks=form.cleaned_data[f'obtained_theory_marks_{idx}'],
                    practical_marks=form.cleaned_data[f'obtained_practical_marks_{idx}']
                )
            return redirect('/success/')
        return render(request, self.template_name, {'form': form})

# AJAX endpoint to fetch students for a given course
def get_students_by_course(request, course_id):
    if request.method == "GET":
        students = User.objects.filter(course_of_interest_id=course_id, is_admitted=True)
        #print(students)
        student_list = [
            {'id': student.id, 'name': student.full_name or student.roll_number or student.email}
            for student in students
        ]

        if student_list:
            return JsonResponse({'students': student_list})
        else:
            return JsonResponse({'students': []})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# AJAX endpoint to fetch subjects for a given course
def get_subjects_by_course(request, course_id):
    if request.method == "GET":
        try:
            course = Course.objects.get(id=course_id)
            print(course.course_subject)  # Print the entire course_subject field to check its structure

            # Assuming the structure is [{"name": {"id": 1, "name": "Subject1"}}, ...]
            subjects = []
            if course.course_subject:
                for subject in course.course_subject:
                    # Make sure to handle the case where the 'name' or 'name.name' might be missing or malformed
                    if isinstance(subject, dict) and 'name' in subject and isinstance(subject['name'], dict):
                        subjects.append(subject['name'].get('name', 'Unknown Subject'))  # Default to 'Unknown Subject' if missing
                    else:
                        subjects.append('Invalid Subject Format')  # Fallback for incorrect format

            return JsonResponse({'subjects': subjects})

        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


class GetSubjectsView(View):
    def get(self, request, course_id):
        # Fetch the course object using the course_id
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return JsonResponse({'error': 'Course not found'}, status=404)
        
        # Get the list of subjects stored in the course's 'course_subject' JSON field
        subjects = course.course_subject  # List of subjects (strings)
        
        # Prepare subject data in the desired format
        subject_data = [{'id': idx + 1, 'name': subject} for idx, subject in enumerate(subjects)]
        
        # Return the subject data as a JSON response
        return JsonResponse({'subjects': subject_data})