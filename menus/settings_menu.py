"""
Central Settings menu for Eclipse RPG Automation.

This doesn't duplicate any setting logic - it's a hub that opens
the existing Search Settings and Training Settings screens,
adds a Capture Settings screen (ball priority already had
get/set functions in capture.py but no menu of its own), and
adds Save/Reset for persistence across runs via settings.py.
"""

import settings
from menus.search_menu import _search_settings
from menus.training_menu import _training_settings
from capture import (
    get_preferred_ball_order,
    set_preferred_ball_order,
)
from break_timer import (
    get_break_settings,
    set_break_enabled,
    set_break_interval,
    set_break_duration,
)


def _capture_settings():

    print()
    print("=" * 60)
    print("CAPTURE SETTINGS")
    print("=" * 60)

    current = get_preferred_ball_order()

    print()
    print(f"Ball priority order: {', '.join(current)}")

    print(
        "\nEnter a new priority order as comma-separated ball "
        "names, most preferred first (blank to keep current):"
    )

    answer = input("> ").strip()

    if not answer:
        print("Unchanged.")
        input("\nPress Enter to return to settings...")
        return

    order = [
        name.strip()
        for name in answer.split(",")
        if name.strip()
    ]

    if set_preferred_ball_order(order):
        print(f"✓ Ball priority set to: {', '.join(order)}")
    else:
        print("✗ Invalid order.")

    input("\nPress Enter to return to settings...")


def _save_settings():

    current = settings.gather_current_settings()

    if settings.save_settings(current):

        print(
            "\n✓ Settings saved - they'll load automatically "
            "next run."
        )

    else:

        print("\n✗ Could not save settings to disk.")

    input("\nPress Enter to return to settings...")


def _reset_settings():

    confirm = input(
        "\nReset all settings to defaults? [y/N]: "
    ).strip().lower()

    if confirm != "y":

        print("Cancelled.")
        input("\nPress Enter to return to settings...")
        return

    settings.apply_settings(settings.DEFAULT_SETTINGS)
    settings.save_settings(settings.DEFAULT_SETTINGS)

    print("✓ Settings reset to defaults.")
    input("\nPress Enter to return to settings...")


def _break_settings():

    print()
    print("=" * 60)
    print("BREAK TIMER SETTINGS")
    print("=" * 60)

    current = get_break_settings()

    while True:

        print()
        print(f"Break Timer: {'ENABLED' if current['enabled'] else 'DISABLED'}")
        print(f"Break after: {current['break_interval_minutes']} minutes")
        print(f"Break duration: {current['break_duration_minutes']} minutes")
        print()
        print("1. Toggle break timer on/off")
        print("2. Set break interval (minutes)")
        print("3. Set break duration (minutes)")
        print("4. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":

            new_state = not current["enabled"]
            set_break_enabled(new_state)
            current["enabled"] = new_state
            status = "enabled" if new_state else "disabled"
            print(f"✓ Break timer {status}.")

        elif choice == "2":

            try:
                minutes = int(
                    input(
                        f"Break after how many minutes? "
                        f"(currently {current['break_interval_minutes']}): "
                    ).strip()
                )

                if minutes <= 0:
                    print("✗ Must be a positive number.")
                    continue

                set_break_interval(minutes)
                current["break_interval_minutes"] = minutes
                print(f"✓ Break interval set to {minutes} minutes.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "3":

            try:
                minutes = int(
                    input(
                        f"Break duration in minutes? "
                        f"(currently {current['break_duration_minutes']}): "
                    ).strip()
                )

                if minutes <= 0:
                    print("✗ Must be a positive number.")
                    continue

                set_break_duration(minutes)
                current["break_duration_minutes"] = minutes
                print(f"✓ Break duration set to {minutes} minutes.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "4":

            input("\nPress Enter to return to settings...")
            return

        else:

            print("✗ Invalid choice.")


def settings_menu(driver):
    while True:

        print()
        print("=" * 60)
        print("SETTINGS")
        print("=" * 60)
        print()
        print("1. Search Settings")
        print("2. Training Settings")
        print("3. Capture Settings")
        print("4. Break Timer Settings")
        print("5. Save Settings")
        print("6. Reset Settings")
        print("7. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            _search_settings()

        elif choice == "2":
            _training_settings()

        elif choice == "3":
            _capture_settings()

        elif choice == "4":
            _break_settings()

        elif choice == "5":
            _save_settings()

        elif choice == "6":
            _reset_settings()

        elif choice == "7":
            return

        else:
            print("✗ Invalid choice.")
