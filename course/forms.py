
from datetime import timedelta
from doctest import Example
from django import forms
from course.models import AwardCategory, Course, Exam
from ckeditor.widgets import CKEditorWidget
from django.forms.widgets import ClearableFileInput

from users.models import Batch

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True  # Allow multiple files to be selected

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs.update({'multiple': 'multiple'})  # Add the 'multiple' attribute to the widget
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
    #subjects = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'subject-input-area'}), required=False)
    class Meta:
        model = Course
        fields = [
            'course_code', 'award', 'course_name', 'course_fees',
            'course_mrp', 'minimum_fees', 'course_duration', 'exam_fees', 'course_video_link_1', 
            'course_video_link_2', 'course_syllabus', 'eligibility', 'course_image', 'course_video_links',
            'display_course_fees_on_website', 'status'
        ]
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_mrp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 30 hours'}),
            'exam_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_syllabus': forms.Textarea(attrs={'class': 'form-control'}),
            'eligibility': forms.Textarea(attrs={'class': 'form-control'}),
            'course_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'course_video_links': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'display_course_fees_on_website': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'status': forms.RadioSelect(choices=[('Active', 'Active'), ('Inactive', 'Inactive')]),
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
    status = forms.ChoiceField(
        choices=Exam.STATUS_CHOICES,
        label="Exam Status",
        initial='pending',  # You can set a default value
        widget=forms.Select(attrs={'class': 'form-control'})
    )

  
    class Meta:
        model = Exam
        fields = ['exam_name', 'date', 'duration', 'total_marks', 'course', 'batch', 'status']

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if isinstance(duration, int):  # If entered as an integer (minutes)
            duration = timedelta(minutes=duration)  # Convert minutes to timedelta
        elif isinstance(duration, str):  # If entered as a string
            try:
                hours, minutes, seconds = map(int, duration.split(':'))
                duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except ValueError:
                raise forms.ValidationError("Duration must be in HH:MM:SS format or an integer representing minutes.")
        return duration
