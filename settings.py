"""
Persistent settings storage for Eclipse RPG Automation.

Settings are stored in settings.json next to this file and
loaded once at startup (see main.py). Each feature module still
owns its own runtime setting - search.py's SEARCH_DELAY,
capture.py's PREFERRED_BALL_ORDER, the training menu's battle
count/difficulty. This module's only job is reading/writing the
JSON file and pushing values through those existing getters/
setters - it never duplicates or replaces that logic.
"""

import json
import os
import tempfile

SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "settings.json",
)

DEFAULT_SETTINGS = {
    "search_delay_min": 0.7,
    "search_delay_max": 1.2,
    "preferred_ball_order": [
        "Ultra Ball",
        "Great Ball",
        "Pokeball",
    ],
    "training_battles_per_session": 100,
    "training_battle_difficulty": None,
    "training_between_battles_min": 0.5,
    "training_between_battles_max": 0.8,
    "break_enabled": False,
    "break_interval_minutes": 120,
    "break_duration_minutes": 30,
    "capture_retry_limit": 3,
    "skip_shiny_encounters": False,
    "auto_stop_on_consecutive_failures": None,
    "log_level": "normal",
    "search_encounter_timeout_seconds": 20,
    "ball_selection_delay_ms": 300,
    "encounter_detection_retry_delay_ms": 250,
    "mine_result_poll_interval_ms": 150,
    "mining_encounter_auto_catch": True,
    "auto_stop_mining_on_area_cleared": True,
    "browser_timeout_seconds": 20,
    "max_connection_retries": 3,
    "slow_network_mode": False,
    "session_time_limit_minutes": None,
    "auto_logout_after_session": False,
    "notify_on_shiny_encounter": True,
    "cancellation_hotkey": "Q",
    "browser_name": "auto",
    "browser_allow_fallback": False,
       # ================================================================
        # AUTO-UPDATE SETTINGS (Option 3)
        # ================================================================
        "auto_update_enabled": False,
        "auto_update_check_frequency_hours": 24,
        "auto_update_restart_after": True,
        "auto_update_quiet_mode": False,
        "auto_update_last_check": None,
        "auto_update_notify": True,
}


def load_settings():
    """
    Load settings from settings.json, filling in any missing
    keys with defaults. Never raises - falls back to defaults
    if the file is missing, unreadable, or invalid JSON.
    """

    settings = dict(DEFAULT_SETTINGS)

    if not os.path.exists(SETTINGS_FILE):
        return settings

    try:

        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            settings.update(data)
        else:
            raise ValueError("settings root must be an object")

    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        # Keep the bad file available for diagnosis, but recover immediately.
        try:
            os.replace(SETTINGS_FILE, SETTINGS_FILE + ".corrupt")
        except OSError:
            pass

    return settings


def save_settings(settings):
    """
    Write a settings dict to settings.json. Returns True on
    success, False if the write failed for any reason.
    """

    try:
        if not isinstance(settings, dict):
            return False
        folder = os.path.dirname(SETTINGS_FILE) or "."
        fd, temporary = tempfile.mkstemp(
            prefix=".settings-", suffix=".json", dir=folder
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
                f.write("\n")
            os.replace(temporary, SETTINGS_FILE)
        finally:
            try:
                os.unlink(temporary)
            except OSError:
                pass
        return True
    except OSError:
        return False


def export_settings(path):
    """Export the current live configuration to a separate JSON file."""
    target = os.fspath(path)
    try:
        with open(target, "w", encoding="utf-8") as stream:
            json.dump(gather_current_settings(), stream, indent=2)
            stream.write("\n")
        return True
    except (OSError, TypeError):
        return False


def import_settings(path):
    """Import, validate, apply, and persist settings from a JSON file."""
    try:
        with open(os.fspath(path), "r", encoding="utf-8") as stream:
            data = json.load(stream)
        if not isinstance(data, dict):
            return False
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        if not isinstance(merged.get("cancellation_hotkey"), str):
            merged["cancellation_hotkey"] = DEFAULT_SETTINGS["cancellation_hotkey"]
        from cancellation import set_cancel_key
        if not set_cancel_key(merged["cancellation_hotkey"]):
            merged["cancellation_hotkey"] = DEFAULT_SETTINGS["cancellation_hotkey"]
        apply_settings(merged)
        return save_settings(gather_current_settings())
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return False


def gather_current_settings():
    """
    Collect the live in-memory values from each feature module
    into a dict ready to save.
    """

    from search import (
        get_search_delay,
        get_auto_stop_consecutive_failures,
        get_log_level,
        get_search_encounter_timeout,
        get_encounter_detection_retry_delay,
        get_max_connection_retries,
        set_max_connection_retries,
    )
    from capture import (
        get_preferred_ball_order,
        get_capture_retry_limit,
        get_skip_shiny_encounters,
        get_ball_selection_delay,
    )
    from mining import (
        get_mine_result_poll_interval,
        get_mining_encounter_auto_catch,
        get_auto_stop_mining_on_area_cleared,
    )
    from menus.training_menu import (
        get_battle_count_setting,
        get_difficulty_setting,
    )
    from training import get_between_battles_wait
    from break_timer import get_break_settings
    from utils import (
        get_browser_timeout,
        get_slow_network_mode,
        get_session_time_limit,
        get_auto_logout_after_session,
        get_notify_on_shiny_encounter,
    )
    from browser import (
        get_browser_name,
        get_browser_allow_fallback,
    )
    from cancellation import get_cancel_key
 # Import auto-update getters (Option 3)
    try:
        from auto_update_settings_unfinished import (
            AutoUpdateSettings as AutoUpdateSettings_,
        )
        _auto_update_settings = AutoUpdateSettings_()
        def get_auto_update_enabled():
            return _auto_update_settings.is_auto_update_enabled()
        def get_auto_update_frequency():
            return _auto_update_settings.get_check_frequency_hours()
        def get_auto_update_restart():
            return _auto_update_settings.should_restart_after_update()
        def get_auto_update_quiet_mode():
            return _auto_update_settings.is_quiet_mode_enabled()
        def get_auto_update_last_check():
            return _auto_update_settings.get_last_check_time()
        def get_auto_update_notify():
            return _auto_update_settings.should_notify_on_update()
    except ImportError:
        # Fallback if auto_update_settings_unfinished not available
        def get_auto_update_enabled():
            return DEFAULT_SETTINGS.get("auto_update_enabled", False)
        def get_auto_update_frequency():
            return DEFAULT_SETTINGS.get("auto_update_check_frequency_hours", 24)
        def get_auto_update_restart():
            return DEFAULT_SETTINGS.get("auto_update_restart_after", True)
        def get_auto_update_quiet_mode():
            return DEFAULT_SETTINGS.get("auto_update_quiet_mode", False)
        def get_auto_update_last_check():
            return DEFAULT_SETTINGS.get("auto_update_last_check", None)
        def get_auto_update_notify():
            return DEFAULT_SETTINGS.get("auto_update_notify", True)

    delay_min, delay_max = get_search_delay()
    break_settings = get_break_settings()
    between_battles = get_between_battles_wait()


    return {
        "search_delay_min": delay_min,
        "search_delay_max": delay_max,
        "preferred_ball_order": get_preferred_ball_order(),
        "training_battles_per_session": get_battle_count_setting(),
        "training_battle_difficulty": get_difficulty_setting(),
        "training_between_battles_min": between_battles[0],
        "training_between_battles_max": between_battles[1],
        "break_enabled": break_settings["enabled"],
        "break_interval_minutes": break_settings["break_interval_minutes"],
        "break_duration_minutes": break_settings["break_duration_minutes"],
        "capture_retry_limit": get_capture_retry_limit(),
        "skip_shiny_encounters": get_skip_shiny_encounters(),
        "auto_stop_on_consecutive_failures": get_auto_stop_consecutive_failures(),
        "log_level": get_log_level(),
        "search_encounter_timeout_seconds": get_search_encounter_timeout(),
        "ball_selection_delay_ms": get_ball_selection_delay(),
        "encounter_detection_retry_delay_ms": get_encounter_detection_retry_delay(),
        "mine_result_poll_interval_ms": get_mine_result_poll_interval(),
        "mining_encounter_auto_catch": get_mining_encounter_auto_catch(),
        "auto_stop_mining_on_area_cleared": get_auto_stop_mining_on_area_cleared(),
        "browser_timeout_seconds": get_browser_timeout(),
        "max_connection_retries": get_max_connection_retries(),
        "slow_network_mode": get_slow_network_mode(),
        "session_time_limit_minutes": get_session_time_limit(),
        "auto_logout_after_session": get_auto_logout_after_session(),
        "notify_on_shiny_encounter": get_notify_on_shiny_encounter(),
        "cancellation_hotkey": get_cancel_key(),
        "browser_name": get_browser_name(),
        "browser_allow_fallback": get_browser_allow_fallback(),
        # Auto-update settings (Option 3)
                "auto_update_enabled": get_auto_update_enabled(),
                "auto_update_check_frequency_hours": get_auto_update_frequency(),
                "auto_update_restart_after": get_auto_update_restart(),
                "auto_update_quiet_mode": get_auto_update_quiet_mode(),
                "auto_update_last_check": get_auto_update_last_check(),
                "auto_update_notify": get_auto_update_notify(),
            
    }


def apply_settings(settings):
    """
    Push a settings dict into each feature module's live
    getter/setter. Used at startup (after load_settings()) and
    after a reset.
    """

    from search import (
        set_search_delay,
        set_auto_stop_consecutive_failures,
        set_log_level,
        set_search_encounter_timeout,
        set_encounter_detection_retry_delay,
        set_max_connection_retries,
    )
    from capture import (
        set_preferred_ball_order,
        set_capture_retry_limit,
        set_skip_shiny_encounters,
        set_ball_selection_delay,
    )
    from mining import (
        set_mine_result_poll_interval,
        set_mining_encounter_auto_catch,
        set_auto_stop_mining_on_area_cleared,
    )
    from menus.training_menu import (
        set_battle_count_setting,
        set_difficulty_setting,
    )
    from training import set_between_battles_wait
    from break_timer import (
        set_break_enabled,
        set_break_interval,
        set_break_duration,
    )
    from utils import (
        set_browser_timeout,
        set_slow_network_mode,
        set_session_time_limit,
        set_auto_logout_after_session,
        set_notify_on_shiny_encounter,
    )
    from browser import (
        set_browser_name,
        set_browser_allow_fallback,
    )
    from cancellation import set_cancel_key
   # Import auto-update setters (Option 3)
    try:
        from auto_update_settings_unfinished import AutoUpdateSettings as AutoUpdateSettings_
        _auto_update_settings = AutoUpdateSettings_()
    except ImportError:
        _auto_update_settings = None

    set_search_delay(
        settings.get(
            "search_delay_min",
            DEFAULT_SETTINGS["search_delay_min"],
        ),
        settings.get(
            "search_delay_max",
            DEFAULT_SETTINGS["search_delay_max"],
        ),
    )

    set_cancel_key(
        settings.get(
            "cancellation_hotkey",
            DEFAULT_SETTINGS["cancellation_hotkey"],
        )
    )

    ball_order = settings.get("preferred_ball_order")

    if ball_order:
        set_preferred_ball_order(ball_order)

    battles = settings.get("training_battles_per_session")

    if battles:
        set_battle_count_setting(battles)

    set_difficulty_setting(
        settings.get("training_battle_difficulty")
    )

    set_between_battles_wait(
        settings.get(
            "training_between_battles_min",
            DEFAULT_SETTINGS["training_between_battles_min"],
        ),
        settings.get(
            "training_between_battles_max",
            DEFAULT_SETTINGS["training_between_battles_max"],
        ),
    )

    set_break_enabled(
        settings.get(
            "break_enabled",
            DEFAULT_SETTINGS["break_enabled"],
        )
    )

    set_break_interval(
        settings.get(
            "break_interval_minutes",
            DEFAULT_SETTINGS["break_interval_minutes"],
        )
    )

    set_break_duration(
        settings.get(
            "break_duration_minutes",
            DEFAULT_SETTINGS["break_duration_minutes"],
        )
    )

    set_capture_retry_limit(
        settings.get(
            "capture_retry_limit",
            DEFAULT_SETTINGS["capture_retry_limit"],
        )
    )

    set_skip_shiny_encounters(
        settings.get(
            "skip_shiny_encounters",
            DEFAULT_SETTINGS["skip_shiny_encounters"],
        )
    )

    set_auto_stop_consecutive_failures(
        settings.get(
            "auto_stop_on_consecutive_failures",
            DEFAULT_SETTINGS["auto_stop_on_consecutive_failures"],
        )
    )

    set_log_level(
        settings.get(
            "log_level",
            DEFAULT_SETTINGS["log_level"],
        )
    )

    set_search_encounter_timeout(
        settings.get(
            "search_encounter_timeout_seconds",
            DEFAULT_SETTINGS["search_encounter_timeout_seconds"],
        )
    )

    set_ball_selection_delay(
        settings.get(
            "ball_selection_delay_ms",
            DEFAULT_SETTINGS["ball_selection_delay_ms"],
        )
    )

    set_encounter_detection_retry_delay(
        settings.get(
            "encounter_detection_retry_delay_ms",
            DEFAULT_SETTINGS["encounter_detection_retry_delay_ms"],
        )
    )

    set_mine_result_poll_interval(
        settings.get(
            "mine_result_poll_interval_ms",
            DEFAULT_SETTINGS["mine_result_poll_interval_ms"],
        )
    )

    set_mining_encounter_auto_catch(
        settings.get(
            "mining_encounter_auto_catch",
            DEFAULT_SETTINGS["mining_encounter_auto_catch"],
        )
    )

    set_auto_stop_mining_on_area_cleared(
        settings.get(
            "auto_stop_mining_on_area_cleared",
            DEFAULT_SETTINGS["auto_stop_mining_on_area_cleared"],
        )
    )

    set_browser_timeout(
        settings.get(
            "browser_timeout_seconds",
            DEFAULT_SETTINGS["browser_timeout_seconds"],
        )
    )

    set_max_connection_retries(
        settings.get(
            "max_connection_retries",
            DEFAULT_SETTINGS["max_connection_retries"],
        )
    )

    set_slow_network_mode(
        settings.get(
            "slow_network_mode",
            DEFAULT_SETTINGS["slow_network_mode"],
        )
    )

    set_session_time_limit(
        settings.get(
            "session_time_limit_minutes",
            DEFAULT_SETTINGS["session_time_limit_minutes"],
        )
    )

    set_auto_logout_after_session(
        settings.get(
            "auto_logout_after_session",
            DEFAULT_SETTINGS["auto_logout_after_session"],
        )
    )

    set_notify_on_shiny_encounter(
        settings.get(
            "notify_on_shiny_encounter",
            DEFAULT_SETTINGS["notify_on_shiny_encounter"],
        )
    )

    set_browser_name(
        settings.get(
            "browser_name",
            DEFAULT_SETTINGS["browser_name"],
        )
    )

    set_browser_allow_fallback(
        settings.get(
            "browser_allow_fallback",
            DEFAULT_SETTINGS["browser_allow_fallback"],
        )
    )
    # Apply auto-update settings (Option 3)
    if _auto_update_settings:
        _auto_update_settings.set_auto_update_enabled(
            settings.get(
                "auto_update_enabled",
                DEFAULT_SETTINGS["auto_update_enabled"],
            )
        )
        _auto_update_settings.set_check_frequency_hours(
            settings.get(
                "auto_update_check_frequency_hours",
                DEFAULT_SETTINGS["auto_update_check_frequency_hours"],
            )
        )
        _auto_update_settings.set_restart_after_update(
            settings.get(
                "auto_update_restart_after",
                DEFAULT_SETTINGS["auto_update_restart_after"],
            )
        )
        _auto_update_settings.set_quiet_mode(
            settings.get(
                "auto_update_quiet_mode",
                DEFAULT_SETTINGS["auto_update_quiet_mode"],
            )
        )
        _auto_update_settings.set_last_check_time(
            settings.get(
                "auto_update_last_check",
                DEFAULT_SETTINGS["auto_update_last_check"],
            )
        )
        _auto_update_settings.set_notify_on_update(
            settings.get(
                "auto_update_notify",
                DEFAULT_SETTINGS["auto_update_notify"],
            )
        )