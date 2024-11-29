from django.urls import path
from users import views
from django.conf import settings
from django.conf.urls.static import static
from users import forms
from users.user_views import user_views,admin_views,authentication_views
from app_common.app_common_views import app_common_views
from django.contrib.auth import views as auth_view
from users.user_views.admin_views import course_selection_view
from users.user_views import admin_views
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
    path('profile/update/', user_views.UpdateProfileView.as_view(), name='update_profile'),
    # path('account-details',user_views.AccountDetails.as_view(),name='account_details'),
    path('profile/alladdress',user_views.AllAddress.as_view(),name="alladdress"),
    path('profile/addaddress',user_views.ProfileAddAddress.as_view(),name="profile_addaddress"),
    path('profile/update-address/<str:address_id>/', user_views.ProfileUpdateAddress.as_view(), name='profile_update_address'),
    path('profile/delete-address/<str:address_id>/', user_views.ProfileDeleteAddress.as_view(), name='profile_delete_address'),
    path('support/', user_views.SupportView.as_view(), name='support'),


    # admin 
    path('students/', admin_views.StudentListView.as_view(), name='student_list'),
    path('add-new-student/', admin_views.AddNewStudentView.as_view(), name='add_new_student'),
    path('student/update/<int:pk>/', admin_views.StudentUpdateView.as_view(), name='update_student'),
    path('get_course_details/<int:course_id>/', admin_views.CourseDetailsView.as_view(), name='get_course_details'),
    path('student-payments/', admin_views.StudentPaymentListView.as_view(), name='student_payment_list'),
    path('export-students/', admin_views.ExportStudentsView.as_view(), name='export_students'),
    path('delete-student/<int:pk>/', admin_views.StudentDeleteView.as_view(), name='delete_student'),
    path('payments/export/', admin_views.ExportPaymentsView.as_view(), name='export_payments'),
    path('payments/add/<int:student_id>/', admin_views.AddNewPaymentView.as_view(), name='add_new_payment'),
    path('students/delete/<int:student_id>/', admin_views.DeleteStudentView.as_view(), name='student_delete'),
    path('student/edit/<int:pk>/', admin_views.StudentpaymentEdit.as_view(), name='student_payment_edit'),
    path('take-attendance/', admin_views.TakeAttendanceView.as_view(), name='take_attendance'),
    path('attendance-report/', admin_views.AttendanceReportView.as_view(), name='attendance_report'),
    path('student-attendance-report/', admin_views.StudentAttendanceReportView.as_view(), name='student_attendance_report'),
    path('batch-details/', admin_views.BatchDetailsView.as_view(), name='batch_details'),
    path('referral-amount/', admin_views.ReferralAmountView.as_view(), name='referral_amount'),
    path('user/user_detail/<int:user_id>', admin_views.StudentDetailView.as_view(), name='user_detail'),
    path('online_class_filter/', admin_views.FilterClass.as_view(), name='online_class_filter'),
    path('batches/', admin_views.BatchListView.as_view(), name='list_batches'),
    path('batches/add', admin_views.AddNewBatchView.as_view(), name='add_new_batch'),
    path('batches/<int:pk>/edit/', admin_views.BatchUpdateView.as_view(), name='edit_batch'),
    path('batches/<int:pk>/delete/', admin_views.BatchDeleteView.as_view(), name='delete_batch'),
    path('student-fees/', admin_views.StudentFeesListView.as_view(), name='student_fees_list'),
    path('get-course-fee/', admin_views.get_course_fee, name='get_course_fee'),
    path('select-course/', admin_views.course_selection_view, name='select_course'),
    path('re-admission/', admin_views.ReAdmissionView.as_view(), name='re-admission'),
    path('get-course-fees/<int:course_id>/', admin_views.GetCourseFeesView.as_view(), name='get-course-fees'),
    path('get-batch-seats/<int:batch_id>/', admin_views.GetBatchRemainingSeatsView.as_view(), name='get-batch-seats'),
    path('re-admission-list/', admin_views.ReAdmissionListView.as_view(), name='re-admission-list'),
    path('re-admission/delete/<int:pk>/', admin_views.ReAdmissionDeleteView.as_view(), name='re-admission-delete'),
    path('re-admission/update/<int:pk>/', admin_views.ReAdmissionUpdateView.as_view(), name='re-admission-update'),
    path('all-users/', admin_views.AllUserListView.as_view(), name='all_user_list'),
    path('user/edit/<int:pk>/', admin_views.UserEditView.as_view(), name='user_edit'),
    path('delete_user/<int:user_id>/', admin_views.DeleteUserView.as_view(), name='delete_user'),
    path('student-details/<int:pk>/', admin_views.StudentsDetailView.as_view(), name='student_details'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)