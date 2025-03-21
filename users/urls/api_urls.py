from django.urls import path
from users.user_views import api_views_users

from django.contrib.auth import views 

app_name = 'users'

urlpatterns = [
path('api/register/', api_views_users.RegistrationApi.as_view(), name='api_register'),
path('api/login/', api_views_users.LoginApi.as_view(), name='api_login'),
path('api/logout/', api_views_users.LogoutApi.as_view(), name='api_logout'),

path('api/forgot-password/', api_views_users.ForgotPasswordAPIView.as_view(), name='forgot-password-api'),
path('api/reset-password/<str:token>/', api_views_users.ResetPasswordAPIView.as_view(), name='reset_password_api'),
path('api/profile/', api_views_users.ProfileApiView.as_view(), name='profile_api'),
path('api/update-profile/', api_views_users.UpdateProfileApiView.as_view(), name='update-profile'),



]