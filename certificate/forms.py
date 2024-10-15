from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')

    def search(self, queryset):
        query = self.cleaned_data['q']
        if query:
            return queryset.filter(
                Q(student__name__icontains=query) |
                Q(course__name__icontains=query) |
                Q(exam_mode__icontains=query)
            )
        return queryset
