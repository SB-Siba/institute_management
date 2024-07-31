from django.urls import path
from users import views
from users import forms
from users.user_views import user_views,admin_views,auth_views
from app_common.app_common_views import app_common_views
from django.contrib.auth import views as auth_view
app_name = 'users'


urlpatterns = [
    #Authentication urls
    path('', app_common_views.HomeView.as_view(), name='home'),
    path('admin/', admin_views.AdminDashboard.as_view(), name='admin_dashboard'),
    path('signup', auth_views.Registration.as_view(), name = "signup"),
    path('login', auth_views.Login.as_view(), name = "login"),
    path('forgot_password/', auth_views.ForgotPasswordView.as_view(), name = "forgot_password"),
    path('reset_password/<str:token>/', auth_views.ResetPasswordView.as_view(), name = "reset_password"),
    path('logout/', auth_views.Logout.as_view(), name = "logout"),
    path('account-deletion/', auth_views.AccountDeletionView.as_view(), name='account_deletion'),


    #user profile
    path('profile',user_views.ProfileView.as_view(),name="profile"),
    path('alladdress',user_views.AllAddress.as_view(),name="alladdress"),
    path('addaddress',user_views.AddAddress.as_view(),name="addaddress"),
    path('delete-address/<str:address_id>/', user_views.DeleteAddress.as_view(), name='delete_address'),
    path('updateprofile/',user_views.UpdateProfileView.as_view(),name="updateprofile"),

    # admin 
    path("user/userslist", admin_views.UserList.as_view(), name="userslist"),
    path("user/deleteuser/<int:user_id>", admin_views.DeleteUser.as_view(), name="deleteuser"),
    path('user/user_detail/<int:user_id>', admin_views.UserDetailView.as_view(), name='user_detail'),
    path('edit_user/<int:user_id>',admin_views.Edit_User.as_view(),name="edit_userrr"),
    path('add_user/', admin_views.AddUserView.as_view(), name='add_user'),
]