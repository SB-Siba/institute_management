from django.urls import path
from users import views
from users import forms
from users.user_views import user_views,admin_views,authentication_views
from app_common.app_common_views import app_common_views
from django.contrib.auth import views as auth_view
app_name = 'users'


urlpatterns = [
    #Authentication urls
    path('', app_common_views.HomeView.as_view(), name='home'),
    path('admin/', admin_views.AdminDashboard.as_view(), name='admin_dashboard'),
    path('signup', authentication_views.Registration.as_view(), name = "signup"),
    path('login', authentication_views.Login.as_view(), name = "login"),
    path('forgot_password/', authentication_views.ForgotPasswordView.as_view(), name = "forgot_password"),
    path('reset-password/<uuid:token>/', authentication_views.ResetPasswordView.as_view(), name='reset_password'),  # Ensure this matches
    path('logout/', authentication_views.Logout.as_view(), name = "logout"),
    path('account-deletion/', authentication_views.AccountDeletionView.as_view(), name='account_deletion'),


    #user
    path('profile',user_views.ProfileView.as_view(),name="profile"),
    path('updateprofile/',user_views.UpdateProfileView.as_view(),name="updateprofile"),
    path('account-details',user_views.AccountDetails.as_view(),name='account_details'),
    path('profile/alladdress',user_views.AllAddress.as_view(),name="alladdress"),
    path('profile/addaddress',user_views.ProfileAddAddress.as_view(),name="profile_addaddress"),
    path('profile/update-address/<str:address_id>/', user_views.ProfileUpdateAddress.as_view(), name='profile_update_address'),
    path('profile/delete-address/<str:address_id>/', user_views.ProfileDeleteAddress.as_view(), name='profile_delete_address'),

    # admin 
    path("user/userslist", admin_views.UserList.as_view(), name="userslist"),
    path("user/deleteuser/<int:user_id>", admin_views.DeleteUser.as_view(), name="deleteuser"),
    path('user/user_detail/<int:user_id>', admin_views.UserDetailView.as_view(), name='user_detail'),
    path('edit_user/<int:user_id>',admin_views.Edit_User.as_view(),name="edit_userrr"),
    path('add_user/', admin_views.AddUserView.as_view(), name='add_user'),
]