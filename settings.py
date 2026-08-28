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

SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "settings.json",
)

DEFAULT_SETTINGS = {
    "search_delay_min": 1.5,
    "search_delay_max": 2.5,
    "preferred_ball_order": [
        "Ultra Ball",
        "Great Ball",
        "Pokeball",
    ],
    "training_battles_per_session": 100,
    "training_battle_difficulty": None,
    "break_enabled": False,
    "break_interval_minutes": 120,
    "break_duration_minutes": 30,
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

    except (json.JSONDecodeError, OSError):

        pass

    return settings


def save_settings(settings):
    """
    Write a settings dict to settings.json. Returns True on
    success, False if the write failed for any reason.
    """

    try:

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        return True

    except OSError:

        return False


def gather_current_settings():
    """
    Collect the live in-memory values from each feature module
    into a dict ready to save.
    """

    from search import get_search_delay
    from capture import get_preferred_ball_order
    from menus.training_menu import (
        get_battle_count_setting,
        get_difficulty_setting,
    )
    from break_timer import get_break_settings

    delay_min, delay_max = get_search_delay()
    break_settings = get_break_settings()

    return {
        "search_delay_min": delay_min,
        "search_delay_max": delay_max,
        "preferred_ball_order": get_preferred_ball_order(),
        "training_battles_per_session": get_battle_count_setting(),
        "training_battle_difficulty": get_difficulty_setting(),
        "break_enabled": break_settings["enabled"],
        "break_interval_minutes": break_settings["break_interval_minutes"],
        "break_duration_minutes": break_settings["break_duration_minutes"],
    }


def apply_settings(settings):
    """
    Push a settings dict into each feature module's live
    getter/setter. Used at startup (after load_settings()) and
    after a reset.
    """

    from search import set_search_delay
    from capture import set_preferred_ball_order
    from menus.training_menu import (
        set_battle_count_setting,
        set_difficulty_setting,
    )
    from break_timer import (
        set_break_enabled,
        set_break_interval,
        set_break_duration,
    )

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

    ball_order = settings.get("preferred_ball_order")

    if ball_order:
        set_preferred_ball_order(ball_order)

    battles = settings.get("training_battles_per_session")

    if battles:
        set_battle_count_setting(battles)

    set_difficulty_setting(
        settings.get("training_battle_difficulty")
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
