from django.urls import path
from users import views
from users import forms
from users.user_views import user_views,admin_views
from app_common.app_common_views import app_common_views
from django.contrib.auth import views as auth_view
from users.forms import CustomPasswordResetForm, PasswordChangeForm
app_name = 'users'


urlpatterns = [
    #Authentication urls
    path('', app_common_views.HomeView.as_view(), name='home'),
    path('admin/', admin_views.AdminDashboard.as_view(), name='admin_dashboard'),
    path('signup', views.Registration.as_view(), name = "signup"),
    path('login', views.Login.as_view(), name = "login"),
    path("passwordChange/",auth_view.PasswordChangeView.as_view(template_name = 'users/authtemp/changepassword.html',form_class = PasswordChangeForm,success_url = '/passwordchangedone'),name='passwordchange'),
    path("passwordchangedone/",auth_view.PasswordChangeDoneView.as_view(template_name = 'users/authtemp/changepassworddone.html'),name='passwordchangedone'),
    path('password-reset/', views.CustomPasswordResetView.as_view(),name='password-reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('password-reset-complete/',views.CustomPasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('logout/', views.Logout.as_view(), name = "logout"),
    path('logout-confirmation/', views.LogoutConfirmationView.as_view(), name='logout_confirmation'),
    path('cancel-logout/', views.CancelLogoutView.as_view(), name='cancel_logout'),
     path('account/delete/', views.AccountDeletionRequestView.as_view(), name='account_deletion_request'),
    path('account/deletion-status/', views.AccountDeletionStatusView.as_view(), name='account_deletion_status'),


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