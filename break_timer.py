"""
Break timer system for Eclipse RPG Automation.

Tracks session time and enforces periodic breaks to prevent user burnout.
Finishes the current action, then locks automation until break period expires.
Auto-resumes when break duration is over.
"""

import time
from datetime import datetime, timedelta


# ============================================================
# BREAK TIMER STATE
# ============================================================

_break_state = {
    "enabled": False,
    "break_interval_minutes": 120,  # Minutes before break is triggered
    "break_duration_minutes": 30,   # Duration of each break
    "session_start_time": None,
    "in_break_mode": False,
    "break_end_time": None,
}


def initialize_break_timer():
    """
    Start the session timer. Call this once at bot startup
    (from main.py after login).
    """
    global _break_state
    _break_state["session_start_time"] = time.time()
    _break_state["in_break_mode"] = False
    _break_state["break_end_time"] = None


def get_break_settings():
    """
    Return current break timer settings as a dict:
        {
            "enabled": bool,
            "break_interval_minutes": int,
            "break_duration_minutes": int,
        }
    """
    return {
        "enabled": _break_state["enabled"],
        "break_interval_minutes": _break_state["break_interval_minutes"],
        "break_duration_minutes": _break_state["break_duration_minutes"],
    }


def set_break_enabled(enabled):
    """Enable or disable break timer."""
    global _break_state
    _break_state["enabled"] = bool(enabled)
    return True


def set_break_interval(minutes):
    """Set minutes of automation before a break is triggered."""
    global _break_state
    if minutes <= 0:
        return False
    _break_state["break_interval_minutes"] = int(minutes)
    return True


def set_break_duration(minutes):
    """Set duration in minutes for each break period."""
    global _break_state
    if minutes <= 0:
        return False
    _break_state["break_duration_minutes"] = int(minutes)
    return True


def get_session_elapsed_time():
    """Return seconds elapsed since session started."""
    if _break_state["session_start_time"] is None:
        return 0
    return time.time() - _break_state["session_start_time"]


def get_session_elapsed_minutes():
    """Return minutes elapsed since session started."""
    return get_session_elapsed_time() / 60.0


def should_trigger_break():
    """
    Check if it's time to trigger a break.
    Returns True if break is enabled, not currently in break,
    and elapsed time exceeds the interval.
    """
    if not _break_state["enabled"]:
        return False

    if _break_state["in_break_mode"]:
        return False

    interval_seconds = _break_state["break_interval_minutes"] * 60
    elapsed = get_session_elapsed_time()

    return elapsed >= interval_seconds


def is_in_break_mode():
    """Return True if automation is currently locked in break mode."""
    return _break_state["in_break_mode"]


def enter_break_mode():
    """
    Enter break mode. Call this after finishing the current action
    (hunt/search/etc.) when should_trigger_break() returns True.
    """
    global _break_state

    if _break_state["in_break_mode"]:
        return  # Already in break

    _break_state["in_break_mode"] = True
    break_seconds = _break_state["break_duration_minutes"] * 60
    _break_state["break_end_time"] = time.time() + break_seconds

    elapsed_minutes = get_session_elapsed_minutes()
    break_duration = _break_state["break_duration_minutes"]
    resume_time = datetime.now() + timedelta(minutes=break_duration)

    print()
    print("=" * 60)
    print("⏰ BREAK TIME")
    print("=" * 60)
    print()
    print(
        f"You've been running for {elapsed_minutes:.1f} minutes. "
        f"Taking a {break_duration}-minute break."
    )
    print()
    print(
        f"Automation will resume at approximately "
        f"{resume_time.strftime('%I:%M %p')}."
    )
    print()
    print("=" * 60)


def check_break_timer():
    """
    Check if break period has ended. If so, exit break mode
    and return True. Otherwise, return False.

    Call this periodically during break (every few seconds).
    """
    global _break_state

    if not _break_state["in_break_mode"]:
        return False  # Not in break

    if _break_state["break_end_time"] is None:
        return False

    if time.time() >= _break_state["break_end_time"]:
        # Break is over
        _break_state["in_break_mode"] = False
        _break_state["break_end_time"] = None

        print()
        print("=" * 60)
        print("✅ BREAK OVER")
        print("=" * 60)
        print()
        print("Ready to resume automation.")
        print()
        print("=" * 60)
        print()

        return True  # Break ended

    return False  # Still in break


def get_break_time_remaining():
    """
    Return seconds remaining in current break, or 0 if not in break.
    """
    if not _break_state["in_break_mode"]:
        return 0

    if _break_state["break_end_time"] is None:
        return 0

    remaining = _break_state["break_end_time"] - time.time()
    return max(0, remaining)


def get_break_time_remaining_formatted():
    """
    Return a formatted string of time remaining in break,
    e.g. "15:32" for 15 minutes 32 seconds.
    """
    remaining = get_break_time_remaining()

    if remaining <= 0:
        return "0:00"

    minutes = int(remaining // 60)
    seconds = int(remaining % 60)

    return f"{minutes}:{seconds:02d}"
