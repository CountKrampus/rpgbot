"""Cooperative cancellation for long-running automation tasks."""

import ctypes
import platform
import threading
from contextlib import contextmanager


_cancel_event = threading.Event()
_monitor_thread = None
_monitor_stop = None
_cancel_key = "Q"
_monitor_lock = threading.Lock()


def get_cancel_key():
    """Return the configured cancellation key."""
    return _cancel_key


def set_cancel_key(key):
    """Set the cancellation key to one alphanumeric character."""
    global _cancel_key

    value = str(key or "").strip().upper()
    if len(value) != 1 or not value.isalnum():
        return False

    _cancel_key = value
    return True


def request_cancel():
    """Request that the active automation task stop at its next safe point."""
    _cancel_event.set()


def is_cancel_requested():
    """Return whether the active task has been asked to stop."""
    return _cancel_event.is_set()


def reset_cancel():
    """Clear cancellation state before starting a new task."""
    _cancel_event.clear()


def wait(seconds):
    """Wait for up to ``seconds`` while remaining responsive to cancellation."""
    try:
        seconds = max(0.0, float(seconds))
    except (TypeError, ValueError):
        return is_cancel_requested()
    _cancel_event.wait(seconds)
    return is_cancel_requested()


def interruptible_wait(seconds):
    """Compatibility name for callers that prefer an explicit API."""
    return wait(seconds)


def get_cancel_status():
    """Return a compact status suitable for displaying in menus."""
    return "REQUESTED" if is_cancel_requested() else "READY"


def _q_is_down():
    if platform.system() != "Windows":
        return False

    return bool(
        ctypes.windll.user32.GetAsyncKeyState(
            ord(_cancel_key)
        ) & 0x8000
    )


def _monitor():
    was_down = False
    stop = _monitor_stop
    while stop is not None and not stop.is_set():
        down = _q_is_down()
        if down and not was_down:
            request_cancel()
            print("\n⚠ Cancel requested. Finishing the current safe step...")
        was_down = down
        stop.wait(0.05)


@contextmanager
def automation_task():
    """Run one menu task with Q-key cancellation enabled."""
    global _monitor_thread, _monitor_stop

    reset_cancel()
    print(
        f"  Press {_cancel_key} at any time to cancel this task "
        "and return to the main menu."
    )
    with _monitor_lock:
        _monitor_stop = threading.Event()
        _monitor_thread = threading.Thread(
            target=_monitor,
            name="automation-cancel-monitor",
            daemon=True,
        )
        thread = _monitor_thread
        thread.start()
    try:
        yield
    finally:
        with _monitor_lock:
            stop = _monitor_stop
            thread = _monitor_thread
            _monitor_stop = None
            _monitor_thread = None
        if stop is not None:
            stop.set()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=1)
        reset_cancel()
