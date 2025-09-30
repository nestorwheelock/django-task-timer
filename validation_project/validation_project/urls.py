"""
URL configuration for validation_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # Login/logout URLs
    path("timer/", include("task_timer.urls")),
]
