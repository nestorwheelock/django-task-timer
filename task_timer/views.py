"""
API Views for task_timer
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from task_timer.models import TimerSession, TimerSettings
from task_timer.serializers import TimerSessionSerializer, TimerSettingsSerializer
from task_timer.services import TimerEngine


class TimerViewSet(viewsets.ViewSet):
    """
    ViewSet for timer operations (start, pause, resume, stop)
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new timer session"""
        task = request.data.get('task')
        notes = request.data.get('notes', '')

        if not task:
            return Response(
                {'error': 'Task is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        engine = TimerEngine(user=request.user)

        try:
            session = engine.start_session(task=task, notes=notes)
            serializer = TimerSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active session"""
        engine = TimerEngine(user=request.user)
        session = engine.get_active_session()

        if not session:
            return Response(
                {'detail': 'No active session'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TimerSessionSerializer(session)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def pause(self, request):
        """Pause the active session"""
        engine = TimerEngine(user=request.user)

        try:
            session = engine.pause_session()
            serializer = TimerSessionSerializer(session)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def resume(self, request):
        """Resume a paused session"""
        engine = TimerEngine(user=request.user)

        try:
            session = engine.resume_session()
            serializer = TimerSessionSerializer(session)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def stop(self, request):
        """Stop the active session"""
        engine = TimerEngine(user=request.user)

        try:
            session = engine.stop_session()
            serializer = TimerSessionSerializer(session)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['patch'], url_path='update-duration')
    def update_duration(self, request):
        """Update the duration of active session"""
        duration = request.data.get('duration')

        if duration is None:
            return Response(
                {'error': 'Duration is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        engine = TimerEngine(user=request.user)

        try:
            session = engine.update_session_duration(duration)
            serializer = TimerSessionSerializer(session)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get daily and weekly statistics"""
        engine = TimerEngine(user=request.user)

        daily_stats = engine.get_daily_stats()
        weekly_stats = engine.get_weekly_stats()

        return Response({
            'today': daily_stats,
            'week': weekly_stats
        })


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing session history
    """
    serializer_class = TimerSessionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Will be set in urls.py

    def get_queryset(self):
        """Return sessions for authenticated user only"""
        return TimerSession.objects.filter(created_by=self.request.user)


class SettingsViewSet(viewsets.ViewSet):
    """
    ViewSet for user timer settings
    """
    permission_classes = [IsAuthenticated]

    def retrieve(self, request):
        """Get user settings"""
        engine = TimerEngine(user=request.user)
        settings = engine.get_or_create_settings()
        serializer = TimerSettingsSerializer(settings)
        return Response(serializer.data)

    def update(self, request):
        """Update user settings"""
        engine = TimerEngine(user=request.user)
        settings = engine.get_or_create_settings()

        serializer = TimerSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Frontend views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


@login_required
def dashboard_view(request):
    """Dashboard with timer interface"""
    return render(request, 'task_timer/dashboard.html')


@login_required
def history_view(request):
    """Session history page"""
    sessions = TimerSession.objects.filter(created_by=request.user)
    paginator = Paginator(sessions, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'task_timer/history.html', {
        'sessions': page_obj
    })


@login_required
def settings_view(request):
    """User settings page"""
    engine = TimerEngine(user=request.user)
    settings = engine.get_or_create_settings()

    if request.method == 'POST':
        settings.work_duration = int(request.POST.get('work_duration', 25))
        settings.short_break_duration = int(request.POST.get('short_break_duration', 5))
        settings.long_break_duration = int(request.POST.get('long_break_duration', 15))
        settings.auto_start_breaks = 'auto_start_breaks' in request.POST
        settings.save()
        return redirect('task_timer:settings-view')

    return render(request, 'task_timer/settings.html', {
        'settings': settings
    })
