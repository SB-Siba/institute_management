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
        queryset=Course.objects.none(),  # Set to none initially
        label="Course",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'course-select'})
    )

    class Meta:
        model = Requested
        fields = ['course']  # 'student' is not included since it's automatically set

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the logged-in user
        super().__init__(*args, **kwargs)

        if user:
            # Filter courses to show only those the user is enrolled in
            self.fields['course'].queryset = Course.objects.filter(students=user)


class RequestedCertificateForm(forms.ModelForm):
    class Meta:
        model = Requested
        fields = ['status']

        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
