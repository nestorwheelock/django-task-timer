"""
URL configuration for task_timer app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'task_timer'

# Router will be populated with viewsets later
router = DefaultRouter()

urlpatterns = [
    path('api/', include(router.urls)),
]
