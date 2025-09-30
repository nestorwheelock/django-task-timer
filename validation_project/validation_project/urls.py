"""
URL configuration for validation_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("timer/", include("task_timer.urls")),
]
