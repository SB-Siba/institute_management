from django.urls import path
from app_common import views


app_name = 'app_common'



urlpatterns = [
    path('about',views.AboutPage.as_view(),name="about"),    
]