from django.urls import path
from users import views
from users import forms
from users.user_views import user_views,admin_views
from django.contrib.auth import views as auth_view

app_name = 'users'


urlpatterns = [
    #Authentication urls
    path('', user_views.HomeView.as_view(), name='home'),
    path('admin/', admin_views.AdminDashboard.as_view(), name='admin_dashboard'),
    path('signup', views.Registration.as_view(), name = "signup"),
    path('login', views.Login.as_view(), name = "login"),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('logout/', views.Logout.as_view(), name = "logout"),


    #user profile
    path('profile',user_views.ProfileView.as_view(),name="profile"),
    path('alladdress',user_views.AllAddress.as_view(),name="alladdress"),
    path('addaddress',user_views.AddAddress.as_view(),name="addaddress"),
    path('delete-address/<str:address_id>/', user_views.DeleteAddress.as_view(), name='delete_address'),
    path('updateprofile/',user_views.UpdateProfileView.as_view(),name="updateprofile"),
]