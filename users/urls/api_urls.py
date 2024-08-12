from django.urls import path
from users.user_views import api_views_users

from django.contrib.auth import views 

app_name = 'users'

urlpatterns = [
path('api/register/', api_views_users.SignupApi.as_view(), name='api_register'),
path('api/login/', api_views_users.LoginApi.as_view(), name='api_login'),


]