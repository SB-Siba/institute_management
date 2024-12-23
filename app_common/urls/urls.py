from django.urls import path
from app_common import views
from app_common.app_common_views import app_common_views, admin_views

app_name = 'app_common'

urlpatterns = [
    # Static pages
    path('about_us/', app_common_views.AboutUs.as_view(), name="about_us"),
    path('our_courses/', app_common_views.Ourcourses.as_view(), name="our_courses"),
    path('course/<str:course_code>/', app_common_views.OurCourseDetailView.as_view(), name='our_course_details'),
    path('our-achievers/', app_common_views.OurAchieversView.as_view(), name='our_achievers'),
    path('contact_us/', app_common_views.ContactSupport.as_view(), name="contact_support"),
    path('terms_conditions/', app_common_views.TermsConditions.as_view(), name="terms_conditions"),
    path('privacy_policy/', app_common_views.PrivacyPolicy.as_view(), name="privacy_policy"),
    path('retrun_policy/', app_common_views.ReturnPolicy.as_view(), name="retrun_policy"),
    path('our_services/', app_common_views.OurServices.as_view(), name="our_services"),
    path('locate_us/', app_common_views.LocateUs.as_view(), name="locate_us"),

    # Admin messages
    path('admin/messages/', admin_views.AdminMessageListView.as_view(), name='admin_message_list'),
    path('admin/messages/<int:message_id>/', admin_views.AdminMessageDetailView.as_view(), name='admin_message_detail'),
    path('admin/messages/<int:message_id>/delete/', admin_views.AdminMessageDeleteView.as_view(), name='admin_message_delete'),
    path('admin/messages/bulk-delete/', admin_views.AdminMessageBulkDeleteView.as_view(), name='admin_message_bulk_delete'),
]
