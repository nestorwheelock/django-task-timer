"""
Tests for task_timer REST API
Following TDD: Write tests first, then implement API endpoints
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from task_timer.models import TimerSession, TimerSettings


@pytest.mark.django_db
class TestTimerAPI:
    """Tests for Timer API endpoints"""

    def setup_method(self):
        """Setup test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

    def test_start_session(self):
        """Test POST /api/timer/start/"""
        url = reverse('task_timer:timer-start')
        data = {
            'task': 'Write API tests',
            'notes': 'Testing timer start endpoint'
        }

        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['task'] == 'Write API tests'
        assert response.data['status'] == 'running'
        assert response.data['duration'] == 0

    def test_start_session_without_task(self):
        """Test starting session without required task field"""
        url = reverse('task_timer:timer-start')
        data = {}

        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_start_session_while_active(self):
        """Test starting session when one is already active"""
        # Start first session
        TimerSession.objects.create(
            task='First task',
            created_by=self.user,
            status='running'
        )

        url = reverse('task_timer:timer-start')
        data = {'task': 'Second task'}

        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'active session' in str(response.data).lower()

    def test_get_active_session(self):
        """Test GET /api/timer/active/"""
        # Create active session
        session = TimerSession.objects.create(
            task='Active task',
            created_by=self.user,
            status='running'
        )

        url = reverse('task_timer:timer-active')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == session.id
        assert response.data['status'] == 'running'

    def test_get_active_session_when_none(self):
        """Test getting active session when none exists"""
        url = reverse('task_timer:timer-active')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_pause_session(self):
        """Test POST /api/timer/pause/"""
        # Create active session
        session = TimerSession.objects.create(
            task='Test task',
            created_by=self.user,
            status='running'
        )

        url = reverse('task_timer:timer-pause')
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'paused'

        session.refresh_from_db()
        assert session.status == 'paused'

    def test_pause_without_active_session(self):
        """Test pausing when no active session"""
        url = reverse('task_timer:timer-pause')
        response = self.client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_resume_session(self):
        """Test POST /api/timer/resume/"""
        # Create paused session
        session = TimerSession.objects.create(
            task='Test task',
            created_by=self.user,
            status='paused'
        )

        url = reverse('task_timer:timer-resume')
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'running'

        session.refresh_from_db()
        assert session.status == 'running'

    def test_stop_session(self):
        """Test POST /api/timer/stop/"""
        # Create active session
        session = TimerSession.objects.create(
            task='Test task',
            created_by=self.user,
            status='running',
            duration=600
        )

        url = reverse('task_timer:timer-stop')
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'stopped'
        assert response.data['end_time'] is not None

        session.refresh_from_db()
        assert session.status == 'stopped'
        assert session.end_time is not None

    def test_list_sessions(self):
        """Test GET /api/sessions/"""
        # Create some sessions
        for i in range(3):
            TimerSession.objects.create(
                task=f'Task {i+1}',
                created_by=self.user,
                status='completed',
                duration=1500
            )

        url = reverse('task_timer:session-list')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_get_session_detail(self):
        """Test GET /api/sessions/{id}/"""
        session = TimerSession.objects.create(
            task='Test task',
            created_by=self.user,
            status='completed',
            duration=1500
        )

        url = reverse('task_timer:session-detail', kwargs={'pk': session.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == session.id
        assert response.data['task'] == 'Test task'

    def test_get_stats(self):
        """Test GET /api/stats/"""
        # Create some completed sessions
        for i in range(3):
            TimerSession.objects.create(
                task=f'Task {i+1}',
                created_by=self.user,
                status='completed',
                duration=1500
            )

        url = reverse('task_timer:timer-stats')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'today' in response.data
        assert 'week' in response.data
        assert response.data['today']['total_sessions'] == 3
        assert response.data['week']['total_sessions'] == 3

    def test_get_settings(self):
        """Test GET /api/settings/"""
        url = reverse('task_timer:settings-detail')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['work_duration'] == 25
        assert response.data['short_break_duration'] == 5

    def test_update_settings(self):
        """Test PUT /api/settings/"""
        url = reverse('task_timer:settings-detail')
        data = {
            'work_duration': 50,
            'short_break_duration': 10,
            'long_break_duration': 20,
            'auto_start_breaks': True
        }

        response = self.client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['work_duration'] == 50
        assert response.data['short_break_duration'] == 10
        assert response.data['auto_start_breaks'] is True

    def test_update_session_duration(self):
        """Test PATCH /api/timer/update-duration/"""
        session = TimerSession.objects.create(
            task='Test task',
            created_by=self.user,
            status='running'
        )

        url = reverse('task_timer:timer-update-duration')
        data = {'duration': 900}  # 15 minutes

        response = self.client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['duration'] == 900

        session.refresh_from_db()
        assert session.duration == 900

    def test_unauthenticated_access(self):
        """Test that API requires authentication"""
        self.client.force_authenticate(user=None)

        url = reverse('task_timer:timer-start')
        data = {'task': 'Test'}

        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pagination(self):
        """Test that session list is paginated"""
        # Create 25 sessions (more than default page size)
        for i in range(25):
            TimerSession.objects.create(
                task=f'Task {i+1}',
                created_by=self.user,
                status='completed'
            )

        url = reverse('task_timer:session-list')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20  # Default page size
