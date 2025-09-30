# Django Task Timer

A reusable Django app that implements the Pomodoro Technique for time tracking and productivity.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Django Version](https://img.shields.io/badge/django-4.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🚀 Project Status

**Current Version:** v0.1.0 "Foundation" (In Development)

**Development Phase:** 🔨 **BUILD PHASE** - TDD Implementation

**Roadmap:**
- **v0.1.0 "Foundation"** (Current) - Core Pomodoro timer functionality
- **v0.2.0 "Intelligence"** (Planned) - AI-powered productivity insights with Ollama
- **v0.3.0 "Integration"** (Planned) - Taskflow integration and task linking

## 📖 Overview

Django Task Timer is a reusable Django app that helps developers track their work using the Pomodoro Technique. It provides a simple timer interface, session tracking, and productivity statistics.

### What is the Pomodoro Technique?

The Pomodoro Technique is a time management method:
1. Work for 25 minutes (one "Pomodoro")
2. Take a 5-minute break
3. After 4 Pomodoros, take a longer 15-minute break

This app implements this technique with:
- Configurable work and break durations
- Automatic timer countdown
- Session history tracking
- Daily and weekly statistics

## ✨ Features (v0.1.0)

### Core Timer Functionality
- ⏱️ **Pomodoro Timer** - Configurable work/break intervals (default 25/5 minutes)
- ▶️ **Timer Controls** - Start, pause, resume, stop, and reset
- 📝 **Task Tracking** - Add task description and notes per session
- 🔔 **Notifications** - Audio/visual alerts when timer completes

### Session Management
- 📊 **Session History** - View all past work sessions with filtering
- 📈 **Statistics Dashboard** - Daily and weekly productivity metrics
- 🎯 **Session Status** - Track running, paused, completed, and stopped sessions

### Integration
- 🌐 **REST API** - Complete API for all timer operations
- 🖥️ **Web Dashboard** - Clean, responsive interface
- 🔧 **Django Admin** - Full admin interface for session management

### Quality
- ✅ **Test Coverage** - 95%+ test coverage target
- 📚 **Documentation** - Complete installation and usage guides
- 📦 **Reusable Package** - Install via pip in any Django project

## 🚧 Coming in Future Versions

### v0.2.0 "Intelligence" (Planned)
- 🤖 AI-powered productivity insights via Ollama
- 📊 Automatic productivity summaries
- 🔍 Pattern detection (most productive hours)
- 💡 Personalized work recommendations

### v0.3.0 "Integration" (Planned)
- 🔗 Taskflow integration
- 📋 Link sessions to taskflow tasks
- ⏲️ Time tracking per task
- 📊 Taskflow dashboard integration

### Future/Backlog
- 🔄 WebSocket real-time updates
- 📱 Mobile app
- 👥 Team/multi-user features
- 📅 Calendar integration
- 📊 Advanced charts and visualizations

## 📋 Installation

**Note:** This project is currently in development (v0.1.0). Installation instructions will be available after CLIENT APPROVAL GATE #2 and release.

Once released, installation will be:

```bash
# Install from GitHub
pip install git+https://github.com/nestorwheelock/django-task-timer.git

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'rest_framework',
    'task_timer',
]

# Include URLs
urlpatterns = [
    path('timer/', include('task_timer.urls')),
]

# Run migrations
python manage.py migrate
```

## 📚 Documentation

Complete documentation is available in the [`docs/`](docs/) directory:

- **[SPEC Document](docs/specs/v0.1.0-spec.md)** - Complete v0.1.0 specification
- **[Approval Forms](docs/approvals/)** - Client approval tracking
- **[Documentation Index](docs/README.md)** - Full documentation overview

## 🔄 Development Process

This project follows a rigorous AI-Native Development Workflow with client approval gates:

1. **SPEC Phase** - Requirements and planning ✅ Complete
2. **🚦 CLIENT APPROVAL GATE #1** - Client approves spec ✅ **Approved** (Sept 30, 2025)
3. **BUILD Phase** - TDD implementation 🔨 **Current Phase**
4. **VALIDATION Phase** - Internal QA ⬜ Not started
5. **ACCEPTANCE TEST Phase** - Client hands-on testing ⬜ Not started
6. **🚦 CLIENT APPROVAL GATE #2** - Client approves before ship ⬜ Not started
7. **SHIP Phase** - Release to production ⬜ Not started

See [`docs/README.md`](docs/README.md) for detailed phase information.

## 🧪 Testing

This project follows Test-Driven Development (TDD):
- Write tests first
- Implement features to pass tests
- Refactor while keeping tests green
- Target: 95%+ test coverage

Testing will use:
- pytest
- pytest-django
- pytest-cov

## 🤝 Contributing

Contributions will be welcome after v0.1.0 release. Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**Nestor Wheelock**
- GitHub: [@nestorwheelock](https://github.com/nestorwheelock)
- Project: [django-task-timer](https://github.com/nestorwheelock/django-task-timer)

## 🙏 Credits

- Built with Django and Django REST Framework
- Developed using Claude Code AI-assisted workflow
- Inspired by the Pomodoro Technique by Francesco Cirillo

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review documentation in [`docs/`](docs/)
- Check acceptance criteria in SPEC document

---

**Status:** 🔨 BUILD PHASE - TDD Implementation

**Client Approval:** ✅ SPEC Approved (Sept 30, 2025) - Scope locked for v0.1.0

**Next Milestone:** Internal VALIDATION phase after BUILD complete

Made with ⏱️ and 🤖
