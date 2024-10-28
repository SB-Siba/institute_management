
from django import forms
from course.models import AwardCategory, Course
from ckeditor.widgets import CKEditorWidget
from django.forms.widgets import ClearableFileInput

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
