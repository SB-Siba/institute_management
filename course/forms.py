
from datetime import timedelta
from doctest import Example
from django import forms
# from course.models import AwardCategory, Course, Exam, ExamResult
from django.forms.widgets import ClearableFileInput
from django_summernote.widgets import SummernoteWidget

from users.models import AwardCategory, Batch, Course, Exam, ExamResult, User

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs.update({'multiple': 'multiple'})
        self.attrs = attrs


class AwardCategoryForm(forms.ModelForm):
    class Meta:
        model = AwardCategory
        fields = ['category_name', 'status']
        labels = {
            'category_name': 'Award Category Name',
            'status': 'Status',
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'course_code', 'award', 'course_name', 'course_fees',
            'course_mrp', 'minimum_fees', 'course_duration', 'exam_fees', 'course_video_link_1', 
            'course_video_link_2', 'course_syllabus', 'eligibility', 'course_image',
            'display_course_fees_on_website', 'status'
        ]
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_mrp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 12  months'}),
            'exam_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_syllabus': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter course syllabus here...'
            }),
            'eligibility': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter eligibility criteria here...'
            }),
            'course_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'display_course_fees_on_website': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'status': forms.Select(choices=Course.STATUS_CHOICES, attrs={'class': 'form-control'}),
        }

    def clean_subjects(self):
        subjects_data = self.cleaned_data['subjects']
        if subjects_data:
            return [{'id': i+1, 'name': subject.strip()} for i, subject in enumerate(subjects_data.split(',')) if subject.strip()]
        return []

    def clean_pdf_files(self):
        pdf_files = self.files.getlist('pdf_files')  
        for pdf_file in pdf_files:
            if not pdf_file.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
        return pdf_files

class ExamapplyForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), 
        label="Course"
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), 
        label="Batch"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        label="Exam Date"
    )
    duration = forms.DurationField(
        widget=forms.TextInput(attrs={'placeholder': 'HH:MM:SS'}),
    )
    subjects = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Subjects",
    )
    status = forms.ChoiceField(
        choices=Exam.STATUS_CHOICES,
        label="Exam Status",
        initial='pending',  # You can set a default value
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    total_questions = forms.IntegerField(
        required=False,
        label="Total Questions",
        widget=forms.NumberInput(attrs={'placeholder': 'Total Questions'})
    )
    passing_marks = forms.IntegerField(
        required=False,
        label="Passing Marks",
        widget=forms.NumberInput(attrs={'placeholder': 'Passing Marks'})
    )
  
    class Meta:
        model = Exam
        fields = ['exam_name', 'date', 'duration', 'total_marks', 'total_questions', 'passing_marks', 'course', 'batch', 'status','subjects']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subjects'].choices = []

        # Populate subjects with names only based on the selected course
        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                course = Course.objects.get(id=course_id)
                self.fields['subjects'].choices = [(sub['name'], sub['name']) for sub in course.course_subject]
            except (ValueError, Course.DoesNotExist):
                pass

    def clean_subjects(self):
        # Return only the selected subject names
        subjects = self.cleaned_data.get('subjects', [])
        return subjects

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if isinstance(duration, int):
            duration = timedelta(minutes=duration)
        elif isinstance(duration, str):
            try:
                hours, minutes, seconds = map(int, duration.split(':'))
                duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except ValueError:
                raise forms.ValidationError("Duration must be in HH:MM:SS format or an integer representing minutes.")
        return duration
    
class ExamResultForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Course",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'course-select'})
    )
    student = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Student",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'student-select'})
    )

    class Meta:
        model = ExamResult
        fields = ['course', 'student']

    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)

        # Populate the student field based on the course_id if available
        if course_id:
            self.fields['student'].queryset = User.objects.filter(course_of_interest_id=course_id, is_admitted=True)
        self.fields['student'].label_from_instance = lambda obj: f"{obj.full_name} ({obj.email})" if obj.full_name else obj.roll_number
