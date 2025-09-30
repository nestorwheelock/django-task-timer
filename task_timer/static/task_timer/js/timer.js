// Django Task Timer JavaScript

const API_BASE = '/timer/api';
let timerInterval = null;
let currentSession = null;
let workDuration = 25 * 60; // 25 minutes in seconds
let timeRemaining = workDuration;

// DOM Elements
const timerDisplay = document.getElementById('timer');
const timerStatus = document.getElementById('timer-status');
const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const resumeBtn = document.getElementById('resume-btn');
const stopBtn = document.getElementById('stop-btn');
const taskForm = document.getElementById('task-form');
const taskInput = document.getElementById('task-input');
const notesInput = document.getElementById('notes-input');
const startSessionBtn = document.getElementById('start-session-btn');
const cancelBtn = document.getElementById('cancel-btn');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    checkActiveSession();
    loadSettings();
});

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Format time as MM:SS
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Update timer display
function updateDisplay() {
    timerDisplay.textContent = formatTime(timeRemaining);
}

// Load user settings
async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings/`, {
            credentials: 'same-origin'
        });
        if (response.ok) {
            const settings = await response.json();
            workDuration = settings.work_duration * 60;
            timeRemaining = workDuration;
            updateDisplay();
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Check for active session on page load
async function checkActiveSession() {
    try {
        const response = await fetch(`${API_BASE}/timer/active/`, {
            credentials: 'same-origin'
        });
        if (response.ok) {
            currentSession = await response.json();
            resumeFromActiveSession();
        }
    } catch (error) {
        // No active session, that's fine
    }
}

// Resume from active session
function resumeFromActiveSession() {
    if (!currentSession) return;

    timeRemaining = workDuration - currentSession.duration;
    updateDisplay();

    if (currentSession.status === 'running') {
        timerStatus.textContent = `Working on: ${currentSession.task}`;
        startTimer();
        showControls('running');
    } else if (currentSession.status === 'paused') {
        timerStatus.textContent = 'Paused';
        showControls('paused');
    }
}

// Show appropriate controls
function showControls(state) {
    startBtn.style.display = 'none';
    pauseBtn.style.display = 'none';
    resumeBtn.style.display = 'none';
    stopBtn.style.display = 'none';
    taskForm.classList.remove('active');

    if (state === 'idle') {
        startBtn.style.display = 'inline-block';
    } else if (state === 'form') {
        taskForm.classList.add('active');
    } else if (state === 'running') {
        pauseBtn.style.display = 'inline-block';
        stopBtn.style.display = 'inline-block';
    } else if (state === 'paused') {
        resumeBtn.style.display = 'inline-block';
        stopBtn.style.display = 'inline-block';
    }
}

// Start button - show task form
startBtn.addEventListener('click', function() {
    showControls('form');
    taskInput.focus();
});

// Cancel button - hide form
cancelBtn.addEventListener('click', function() {
    taskInput.value = '';
    notesInput.value = '';
    showControls('idle');
});

// Start session
startSessionBtn.addEventListener('click', async function() {
    const task = taskInput.value.trim();
    if (!task) {
        alert('Please enter a task description');
        return;
    }

    const notes = notesInput.value.trim();

    try {
        const response = await fetch(`${API_BASE}/timer/start/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin',
            body: JSON.stringify({ task, notes })
        });

        if (response.ok) {
            currentSession = await response.json();
            timerStatus.textContent = `Working on: ${task}`;
            taskInput.value = '';
            notesInput.value = '';
            timeRemaining = workDuration;
            startTimer();
            showControls('running');
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to start session');
        }
    } catch (error) {
        console.error('Error starting session:', error);
        alert('Failed to start session');
    }
});

// Start timer countdown
function startTimer() {
    if (timerInterval) clearInterval(timerInterval);

    timerInterval = setInterval(async function() {
        timeRemaining--;
        updateDisplay();

        // Update server every 5 seconds
        if (timeRemaining % 5 === 0 && currentSession) {
            await updateServerDuration();
        }

        // Timer complete
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            await completeSession();
        }
    }, 1000);
}

// Update duration on server
async function updateServerDuration() {
    const duration = workDuration - timeRemaining;
    try {
        await fetch(`${API_BASE}/timer/update-duration/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin',
            body: JSON.stringify({ duration })
        });
    } catch (error) {
        console.error('Error updating duration:', error);
    }
}

// Pause session
pauseBtn.addEventListener('click', async function() {
    if (timerInterval) clearInterval(timerInterval);

    try {
        const response = await fetch(`${API_BASE}/timer/pause/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin'
        });

        if (response.ok) {
            timerStatus.textContent = 'Paused';
            showControls('paused');
        }
    } catch (error) {
        console.error('Error pausing session:', error);
    }
});

// Resume session
resumeBtn.addEventListener('click', async function() {
    try {
        const response = await fetch(`${API_BASE}/timer/resume/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin'
        });

        if (response.ok) {
            currentSession = await response.json();
            timerStatus.textContent = `Working on: ${currentSession.task}`;
            startTimer();
            showControls('running');
        }
    } catch (error) {
        console.error('Error resuming session:', error);
    }
});

// Stop session
stopBtn.addEventListener('click', async function() {
    if (timerInterval) clearInterval(timerInterval);

    try {
        const response = await fetch(`${API_BASE}/timer/stop/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin'
        });

        if (response.ok) {
            resetTimer();
            alert('Session stopped');
        }
    } catch (error) {
        console.error('Error stopping session:', error);
    }
});

// Complete session
async function completeSession() {
    try {
        await fetch(`${API_BASE}/timer/stop/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin'
        });

        resetTimer();
        alert('🎉 Pomodoro Complete! Time for a break.');
        loadStats(); // Refresh stats
    } catch (error) {
        console.error('Error completing session:', error);
    }
}

// Reset timer to initial state
function resetTimer() {
    if (timerInterval) clearInterval(timerInterval);
    currentSession = null;
    timeRemaining = workDuration;
    updateDisplay();
    timerStatus.textContent = 'Ready to start';
    showControls('idle');
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/timer/stats/`, {
            credentials: 'same-origin'
        });
        if (response.ok) {
            const stats = await response.json();

            // Today's stats
            document.getElementById('today-sessions').textContent = stats.today.total_sessions;
            document.getElementById('today-completed').textContent = stats.today.completed_sessions;
            document.getElementById('today-minutes').textContent = stats.today.total_minutes + 'm';

            // Week's stats
            document.getElementById('week-sessions').textContent = stats.week.total_sessions;
            document.getElementById('week-completed').textContent = stats.week.completed_sessions;
            document.getElementById('week-minutes').textContent = stats.week.total_minutes + 'm';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}
