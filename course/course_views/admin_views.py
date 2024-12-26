import json
import bleach
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from course.forms import AwardCategoryForm, CourseForm, ExamResultForm, ExamapplyForm
# from course.models import AwardCategory, Course, Exam, ExamResult
from users.models import AwardCategory, Course, Exam, ExamResult, User

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
            return JsonResponse({'status': 'success'}, status=200) 
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
    allowed_tags = [  
        'b', 'i', 'u', 'strong', 'em', 'p', 'br', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'ul',   
        'ol', 'li', 'blockquote'  
    ]  
    allowed_attrs = {}

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
                course.eligibility = bleach.clean(request.POST.get('eligibility', ''),tags=self.allowed_tags, attributes=self.allowed_attrs, strip=False)  
                course.course_syllabus = bleach.clean(request.POST.get('course_syllabus', ''), tags=self.allowed_tags, attributes=self.allowed_attrs, strip=False)  
                if not course.status:
                    course.status = 'active'
                course.course_subject = [{'id': i + 1, 'name': subject} for i, subject in enumerate(subjects)]
                course.save()
                messages.success(request, 'Course added successfully!')
                return redirect('course:course_list')  
            return render(request, self.template_name, {'form': form, 'subjects': subjects})

        return render(request, self.template_name, {'form': form, 'subjects': []})

class CourseDetail(View):
    template_name = app + 'course_detail.html'

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        return render(request, self.template_name, {'course': course})

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
        exam_results = ExamResult.objects.all().order_by('-created_on')        
        grade = request.GET.get('grade')
        if grade:
            exam_results = exam_results.filter(grade=grade)        
        grades = [choice[0] for choice in ExamResult._meta.get_field('grade').choices]        
        context = {
            'exam_results': exam_results,
            'grades': grades,
        }
        return render(request, self.template_name, context)
    
class AddStudentResultsView(View):
    template_name = app + 'add_exam_result.html'  
    def get(self, request, *args, **kwargs):
        form = ExamResultForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        course_id = request.POST.get('course')
        form = ExamResultForm(request.POST, course_id=course_id)

        if form.is_valid():
            course = form.cleaned_data['course']
            student = form.cleaned_data['student']
            subjects = course.course_subject or []
            
            total_marks = 0
            total_obtained_marks = 0
            obtained_theory_total = 0
            obtained_practical_total = 0

            subjects_data = []
            for subject in subjects:
                subject_id = subject['id']
                subject_name = subject['name']

                total_theory_marks = int(request.POST.get(f'total_theory_marks_{subject_id}', 0))
                theory_obtained_marks = int(request.POST.get(f'theory_marks_{subject_id}', 0))
                total_practical_marks = int(request.POST.get(f'total_practical_marks_{subject_id}', 0))
                practical_obtained_marks = int(request.POST.get(f'practical_marks_{subject_id}', 0))

                total_subject_marks = total_theory_marks + total_practical_marks
                obtained_subject_marks = theory_obtained_marks + practical_obtained_marks

                total_marks += total_subject_marks
                total_obtained_marks += obtained_subject_marks
                obtained_theory_total += theory_obtained_marks
                obtained_practical_total += practical_obtained_marks

                subjects_data.append({
                    'subject': subject_name,
                    'total_theory_marks': total_theory_marks,
                    'theory_marks': theory_obtained_marks,
                    'total_practical_marks': total_practical_marks,
                    'practical_marks': practical_obtained_marks,
                    'total_marks': total_subject_marks,
                    'obtained_marks': obtained_subject_marks,
                })

            percentage = (total_obtained_marks / total_marks) * 100 if total_marks > 0 else 0
            if percentage >= 85:
                grade = 'A+'
            elif percentage >= 70:
                grade = 'A'
            elif percentage >= 55:
                grade = 'B'
            elif percentage >= 40:
                grade = 'C'
            else:
                grade = 'D'

            exam_result = ExamResult.objects.create(
                student=student,
                course=course,
                total_mark=total_marks,
                obtained_mark=total_obtained_marks,
                obtained_theory_marks=obtained_theory_total,
                obtained_practical_marks=obtained_practical_total,
                percentage=percentage,
                grade=grade,
                result='passed' if grade != 'D' else 'failed',
                subjects_data=subjects_data
            )

            exam_result.student_name = student.full_name
            exam_result.save()

            return redirect('course:exam_results_list')

        return render(request, self.template_name, {'form': form})

def get_students_by_course(request, course_id):
    if request.method == "GET":
        students = User.objects.filter(course_of_interest_id=course_id, is_admitted=True)
        student_list = [
            {'id': student.id, 'name': student.full_name or student.roll_number or student.email}
            for student in students
        ]

        if student_list:
            return JsonResponse({'students': student_list})
        else:
            return JsonResponse({'students': []})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_subjects_by_course(request, course_id):
    if request.method == "GET":
            course = Course.objects.get(id=course_id)
            subjects = json.loads(course.course_subject or '[]')
    return JsonResponse({'subjects': subjects})


class GetSubjectsView(View):
    def get(self, request, course_id):
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return JsonResponse({'error': 'Course not found'}, status=404)
        subjects = course.course_subject         
        subject_data = [{'id': idx + 1, 'name': subject} for idx, subject in enumerate(subjects)]        
        return JsonResponse({'subjects': subject_data})
    
class ExamResultDeleteView(View):
    def post(self, request, *args, **kwargs):
        exam_result = get_object_or_404(ExamResult, pk=self.kwargs['pk'])
        
        exam_result.delete()
        
        return JsonResponse({'success': True})
    
class UpdateStudentResultsView(View):
    template_name = app + 'update_exam_result.html'  # Adjust the template path as needed

    def get(self, request, pk):
        # Fetch the student's exam result
        exam_result = get_object_or_404(ExamResult, student_id=pk)

        # Load the subject data from the JSON field
        subjects_data = exam_result.subjects_data or []

        return render(request, self.template_name, {
            'exam_result': exam_result,
            'subjects_data': subjects_data,
        })

    def post(self, request, pk):
        exam_result = get_object_or_404(ExamResult, student_id=pk)
        subjects_data = exam_result.subjects_data or []

        # Initialize totals
        total_obtained_marks = 0
        obtained_theory_total = 0
        obtained_practical_total = 0

        updated_subjects_data = []

        for subject in subjects_data:
            subject_name = subject['subject']
            total_theory_marks = subject['total_theory_marks']
            total_practical_marks = subject['total_practical_marks']

            # Fetch updated marks from the form
            try:
                theory_obtained_marks = int(request.POST.get(f'theory_marks_{subject_name}', 0))
                practical_obtained_marks = int(request.POST.get(f'practical_marks_{subject_name}', 0))

                # Calculate obtained marks
                obtained_subject_marks = theory_obtained_marks + practical_obtained_marks

                # Update totals
                total_obtained_marks += obtained_subject_marks
                obtained_theory_total += theory_obtained_marks
                obtained_practical_total += practical_obtained_marks

                # Update the subject data
                updated_subjects_data.append({
                    'subject': subject_name,
                    'total_theory_marks': total_theory_marks,
                    'theory_marks': theory_obtained_marks,
                    'total_practical_marks': total_practical_marks,
                    'practical_marks': practical_obtained_marks,
                    'total_marks': total_theory_marks + total_practical_marks,
                    'obtained_marks': obtained_subject_marks,
                })
            except ValueError:
                messages.error(request, f"Invalid marks entered for {subject_name}")
                return redirect('course:update_exam_result', student_id=pk)

        # Recalculate percentage
        total_marks = sum(sub['total_marks'] for sub in updated_subjects_data)
        percentage = (total_obtained_marks / total_marks) * 100 if total_marks > 0 else 0

        # Determine grade based on percentage
        if percentage >= 85:
            grade = 'A+'
        elif percentage >= 70:
            grade = 'A'
        elif percentage >= 55:
            grade = 'B'
        elif percentage >= 40:
            grade = 'C'
        else:
            grade = 'D'

        # Update the ExamResult instance
        exam_result.subjects_data = updated_subjects_data
        exam_result.obtained_mark = total_obtained_marks
        exam_result.obtained_theory_marks = obtained_theory_total
        exam_result.obtained_practical_marks = obtained_practical_total
        exam_result.percentage = percentage
        exam_result.grade = grade
        exam_result.result = 'passed' if grade != 'D' else 'failed'
        exam_result.save()

        messages.success(request, "Marks updated successfully!")
        return redirect('course:exam_results_list')
