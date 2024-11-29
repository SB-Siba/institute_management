from django import forms
from django.db.models import Q 
from certificate.models import Requested
from course.models import Course
from users.models import Batch, User

class SearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')

    def search(self, queryset):
        query = self.cleaned_data.get('q')
        if query:
            return queryset.filter(
                Q(student__name__icontains=query) |  # Assuming student is a ForeignKey with name field
                Q(course__name__icontains=query) |   # Assuming course has a name field
                Q(exam_mode__icontains=query)        # Assuming exam_mode is a field in your model
            )
        return queryset

class ApplyCertificateForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Course",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'course-select'})
    )

    student = forms.ModelChoiceField(
        queryset=User.objects.filter(is_admitted=True),
        label="Student",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'student-select'})
    )
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), required=False)  # Optional if derived from the course


    class Meta:
        model = Requested
        fields = ['student', 'course']

    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)

        # Populate the student field based on the course_id if provided
        if course_id:
            self.fields['student'].queryset = User.objects.filter(course_of_interest_id=course_id)
        # Custom label for students in the dropdown
        self.fields['student'].label_from_instance = lambda obj: (
            f"{obj.full_name} ({obj.email})" if obj.full_name else obj.roll_number
        )


class RequestedCertificateForm(forms.ModelForm):
    class Meta:
        model = Requested
        fields = ['status']

        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
