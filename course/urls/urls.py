from django import views
from django.urls import path
from certificate.certificate_view import admin_view
from course.course_views import admin_views, user_views
from course.models import Exam
from users import forms
from app_common.app_common_views import app_common_views
from django.contrib.auth import views as auth_view
app_name = 'course'

urlpatterns = [
    path('award-categories/', admin_views.AwardCategoryListView.as_view(), name='award_categories'),
    path('award-categories/add/', admin_views.AwardCategoryCreateView.as_view(), name='add_award_categories'),
    path('award-categories/edit/<int:category_id>/', admin_views.EditAwardCategoryView.as_view(), name='edit_award_category'),
    path('delete_award_category/<int:category_id>/', admin_views.AwardCategoryDeleteView.as_view(), name='delete_award_category'),
    path('course-list/', admin_views.CourseListView.as_view(), name='course_list'),
    path('course/add/', admin_views.CourseCreateView.as_view(), name='add_course'),
    path('course/<int:pk>/edit/', admin_views.CourseEditView.as_view(), name='edit_course'), 
    path('course/<int:pk>/delete/', admin_views.CourseDeleteView.as_view(), name='delete_course'),
    path('exams/', admin_views.ExamListView.as_view(), name='exam_list'),
    path('exams/examapply/', admin_views.ExamApply.as_view(), name='exam_apply'),
    path('get-course-subjects/<int:course_id>/', admin_views.GetCourseSubjectsView.as_view(), name='get-course-subjects'),
    #path('exams/', admin_views.ExamListView.as_view(), name='exam_list'),
    path('exam_list/', admin_views.ExamListView.as_view(), name='exam_list'),
    path('courseexam-result/', admin_views.ExamResultListView.as_view(), name='exam_results_list'),
    path('add-exam-result/', admin_views.AddStudentResultsView.as_view(), name='add_exam_result'),
    path('delete-exam-result/<int:pk>/', admin_views.ExamResultDeleteView.as_view(), name='delete_exam_result'),
    # path('exam-result/update/<int:pk>/', admin_views.UpdateExamResultView.as_view(), name='update_exam_result'),
    path('get-subjects/<int:course_id>/', admin_views.GetSubjectsView.as_view(), name='get_subjects'),
    #path('exam-results/add/<int:pk>/', AddResultView.as_view(), name='add_result'),
    path('exams-results/update/<int:pk>/', admin_views.UpdateStudentResultsView.as_view(), name='update_result'),
    path('edit/<int:pk>/', admin_views.EditExamView.as_view(), name='edit_exam'),
    path('delete/<int:pk>/', admin_views.DeleteExamView.as_view(), name='delete_exam'),
    path('get-students/<int:course_id>/', admin_views.get_students_by_course, name='get_students_by_course'),
    path('get-subjects/<int:course_id>/', admin_views.get_subjects_by_course, name='get_subjects_by_course'),

        #user side
    path('user-courses/', user_views.UserCourseListView.as_view(), name='user_course_list'),
]