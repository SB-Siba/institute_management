from django.urls import path
from users import views
from app_common.app_common_views import user_views,admin_views


app_name = 'app_common'



urlpatterns = [
    path('', user_views.HomeView.as_view(), name='home'),
    path('admin/', admin_views.AdminDashboard.as_view(), name='admin_dashboard'),
]