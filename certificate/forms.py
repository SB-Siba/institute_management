from django import forms
from django.db.models import Q 
from certificate.models import AppliedCertificate
from course.models import Course
from users.models import Batch

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
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), label='Select Batch')
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label='Select Course')

    class Meta:
        model = AppliedCertificate
        fields = ['batch', 'course']  # Only show these fields in the form

    def __init__(self, *args, **kwargs):
        super(ApplyCertificateForm, self).__init__(*args, **kwargs)