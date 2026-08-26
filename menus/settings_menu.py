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
        print("4. Save Settings")
        print("5. Reset Settings")
        print("6. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            _search_settings()

        elif choice == "2":
            _training_settings()

        elif choice == "3":
            _capture_settings()

        elif choice == "4":
            _save_settings()

        elif choice == "5":
            _reset_settings()

        elif choice == "6":
            return

        else:
            print("✗ Invalid choice.")
