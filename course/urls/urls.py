from django.urls import path
from course.course_views import admin_views
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
]