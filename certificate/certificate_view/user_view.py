from decimal import Decimal
from pyexpat.errors import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from certificate.forms import ApplyCertificateForm
from certificate.models import Requested
from course.models import Course, ExamResult
from users.models import User

 
app = "certificate/user/"


class ApplyCertificateView(View):
    form_class = ApplyCertificateForm
    template_name = app + 'apply_for_certificate.html'

    def get(self, request):
        form = self.form_class(user=request.user)  # Pass the logged-in user to the form
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, user=request.user)  # Pass the logged-in user
        if form.is_valid():
            course = form.cleaned_data['course']
            student = request.user  # The logged-in user

            # Validate if the student is enrolled in the selected course
            if not course.students.filter(id=student.id).exists():
                messages.warning(request, "You are not enrolled in the selected course.")
                return render(request, self.template_name, {'form': form})

            # Save the certificate request
            requested = form.save(commit=False)
            requested.user = student
            requested.status = 'Pending'
            requested.save()

            messages.success(request, "Certificate applied successfully.")
            return redirect('certificate:requested_certificates')

        return render(request, self.template_name, {'form': form})

def get_students_by_course(request, course_id):
    if request.method == "GET":
        course = get_object_or_404(Course, id=course_id)
        students = course.students.all()

        student_list = [
            {'id': student.id, 'name': student.get_full_name() or student.email}
            for student in students
        ]

        return JsonResponse({'students': student_list})

    return JsonResponse({'error': 'Invalid request method'}, status=400)