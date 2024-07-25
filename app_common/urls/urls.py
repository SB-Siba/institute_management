from django.urls import path
from app_common import views
from app_common.app_common_views import app_common_views


app_name = 'app_common'



urlpatterns = [
    # static pages
    path('about',app_common_views.AboutPage.as_view(),name="about"),    
]