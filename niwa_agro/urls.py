from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path("", include("app_common.urls.urls")),
    path("authentication", include("users.urls.urls")),  
]
