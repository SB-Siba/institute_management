from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from app_common import forms
from app_common.models import ContactMessage
# from course.models import Course
from users.models import Attendance, Course, User
from users.forms import LoginForm
from app_common.models import ContactMessage
from app_common.forms import ContactMessageForm
from django.conf import settings
from django.db.models import Prefetch
from django.utils import timezone
from django.db.models import Count
from datetime import datetime
from django.db import models
from django.db.models import Count, Q



app = "app_common/"


# static pages 


class HomeView(View):
    unauthenticated_template = app + "landing_page.html"
    authenticated_template = "users/user/index.html"

    def get(self, request):
        if not request.user.is_authenticated:
            popular_courses = Course.objects.filter(status='Active')[:4]  # Retrieve top 4 popular courses
            current_month = datetime.now().month
            current_year = datetime.now().year
            students_with_attendance = Attendance.objects.filter(
                date__month=current_month,
                date__year=current_year
            ).values('student').annotate(present_days=Count('status', filter=models.Q(status="Present")))
            if students_with_attendance:
                max_attendance = max(students_with_attendance, key=lambda x: x['present_days'])['present_days']
                achievers = User.objects.filter(
                    id__in=[attendance['student'] for attendance in students_with_attendance if attendance['present_days'] == max_attendance]
                ).select_related('course_of_interest')
            else:
                achievers = []  

            context = {
                'MEDIA_URL': settings.MEDIA_URL,
                'popular_courses': popular_courses,
                'achievers': achievers, 
            }

            return render(request, self.unauthenticated_template, context)

        context = {
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, self.authenticated_template, context)

class AboutUs(View):
    template = app + "about_us.html"

    def get(self, request):
       
        return render(request, self.template)

class Ourcourses(View):
    template = 'app_common/our_courses.html'

    def get(self, request):
        courses = Course.objects.filter(status='Active')

        return render(request, self.template, {'courses': courses})

class OurCourseDetailView(View):
    template_name = 'app_common/our_course_details.html'

    def get(self, request, course_code):
        course = get_object_or_404(Course, course_code=course_code)
        
        # Check if 'subjects' attribute exists on the course, otherwise set an empty list
        subjects = getattr(course, 'subjects', [])
        context = {
            'course': course,
            'subjects': subjects if subjects else []  # Use empty list if subjects are missing
        }
        return render(request, self.template_name, context)


class ContactSupport(View):
    contact_template = app + 'contact_us.html'
    support_template = app + 'support.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            initial_data = {
                'full_name': request.user.full_name if request.user.full_name else '',
                'email': request.user.email if request.user.email else '',
                'contact': request.user.contact if request.user.contact else '',
            }
            template = self.support_template
        else:
            initial_data = {
                'full_name': '',
                'email': '',
                'contact': '',
            }
            template = self.contact_template

        form = forms.ContactMessageForm(initial=initial_data)
        return render(request, template, {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms.ContactMessageForm(request.POST)
        if form.is_valid():
            # Create a new ContactMessage instance
            contact_message = ContactMessage(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                contact=form.cleaned_data['contact'],
                message=form.cleaned_data['message']
            )
            
            # Associate the message with the authenticated user if available
            if request.user.is_authenticated:
                contact_message.user = request.user
            
            contact_message.save()

            if request.user.is_authenticated:
                messages.success(request, 'Your support request has been sent successfully.')
                return redirect('app_common:contact_support')
            else:
                messages.success(request, 'Your message has been sent successfully.')
                return redirect('app_common:contact_support')

        template = self.support_template if request.user.is_authenticated else self.contact_template
        return render(request, template, {'form': form})

class TermsConditions(View):
    template = app + "terms_conditions.html"

    def get(self, request):
       
        return render(request, self.template)

class PrivacyPolicy(View):
    template = app + "privacy_policy.html"

    def get(self, request):
       
        return render(request, self.template)

class ReturnPolicy(View):
    template = app + "return_policy.html"

    def get(self, request):
       
        return render(request, self.template)

class OurServices(View):
    template = app + "our_services.html"

    def get(self, request):
       
        return render(request, self.template)
class LocateUs(View):
    template = app + "locate_us.html"

    def get(self, request):
       
        return render(request, self.template)

class OurAchieversView(View):
    template = app + "our_achievers.html"
    
    def get(self, request):
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Get attendance data
        students_with_attendance = Attendance.objects.filter(
            date__month=current_month,
            date__year=current_year
        ).values('student').annotate(present_days=Count('status', filter=models.Q(status="Present")))

        if students_with_attendance:
            # Find max present_days if attendance data exists
            max_attendance = max(students_with_attendance, key=lambda x: x['present_days'])['present_days']
            
            # Get achievers based on max present_days
            achievers = User.objects.filter(
                id__in=[attendance['student'] for attendance in students_with_attendance if attendance['present_days'] == max_attendance]
            ).select_related('course_of_interest')
        else:
            # No attendance data, set achievers to an empty queryset
            achievers = User.objects.none()

        current_month_name = datetime.now().strftime("%B")
        
        return render(request, self.template, {'achievers': achievers, 'current_month': current_month_name})