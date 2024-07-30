from django.urls import path
from app_common import views
from app_common.app_common_views import app_common_views


app_name = 'app_common'



urlpatterns = [
    # static pages
    path('about_us/',app_common_views.AboutUs.as_view(),name="about_us"),    
    path('contact_us/',app_common_views.ContactUs.as_view(),name="contact_us"),
    path('terms_conditions/',app_common_views.TermsConditions.as_view(),name="terms_conditions"),
    path('privacy_policy/',app_common_views.PrivacyPolicy.as_view(),name="privacy_policy"),
    path('retrun_policy/',app_common_views.ReturnPolicy.as_view(),name="retrun_policy"),
    path('our_services/',app_common_views.OurServices.as_view(),name="our_services"),


]