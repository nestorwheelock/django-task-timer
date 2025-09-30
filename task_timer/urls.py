"""
URL configuration for task_timer app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.pagination import PageNumberPagination
from task_timer.views import TimerViewSet, SessionViewSet, SettingsViewSet

app_name = 'task_timer'


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination: 20 items per page"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Configure router
router = DefaultRouter()
router.register(r'timer', TimerViewSet, basename='timer')
router.register(r'sessions', SessionViewSet, basename='session')

# Apply pagination to SessionViewSet
SessionViewSet.pagination_class = StandardResultsSetPagination

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/settings/', SettingsViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='settings-detail'),
]
