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
    get_capture_retry_limit,
    set_capture_retry_limit,
    get_skip_shiny_encounters,
    set_skip_shiny_encounters,
)
from break_timer import (
    get_break_settings,
    set_break_enabled,
    set_break_interval,
    set_break_duration,
)
from search import (
    get_auto_stop_consecutive_failures,
    set_auto_stop_consecutive_failures,
    get_log_level,
    set_log_level,
    get_search_encounter_timeout,
    set_search_encounter_timeout,
    get_encounter_detection_retry_delay,
    set_encounter_detection_retry_delay,
    get_max_connection_retries,
    set_max_connection_retries,
)
from training import (
    get_between_battles_wait,
    set_between_battles_wait,
)
from capture import (
    get_ball_selection_delay,
    set_ball_selection_delay,
)
from mining import (
    get_mine_result_poll_interval,
    set_mine_result_poll_interval,
    get_mining_encounter_auto_catch,
    set_mining_encounter_auto_catch,
    get_auto_stop_mining_on_area_cleared,
    set_auto_stop_mining_on_area_cleared,
)
from utils import (
    get_browser_timeout,
    set_browser_timeout,
    get_max_connection_retries,
    set_max_connection_retries,
    get_slow_network_mode,
    set_slow_network_mode,
)


def _capture_settings():

    print()
    print("=" * 60)
    print("CAPTURE SETTINGS")
    print("=" * 60)

    while True:

        print()
        print(f"Ball priority order: {', '.join(get_preferred_ball_order())}")
        print(f"Capture retry limit: {get_capture_retry_limit()}")
        print(f"Skip shiny encounters: {'YES' if get_skip_shiny_encounters() else 'NO'}")
        print()
        print("1. Set ball priority order")
        print("2. Set capture retry limit")
        print("3. Toggle skip shiny encounters")
        print("4. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":

            current = get_preferred_ball_order()

            print(
                "\nEnter a new priority order as comma-separated ball "
                "names, most preferred first (blank to keep current):"
            )

            answer = input("> ").strip()

            if not answer:
                print("Unchanged.")
                continue

            order = [
                name.strip()
                for name in answer.split(",")
                if name.strip()
            ]

            if set_preferred_ball_order(order):
                print(f"✓ Ball priority set to: {', '.join(order)}")
            else:
                print("✗ Invalid order.")

        elif choice == "2":

            try:
                limit = int(
                    input(
                        f"Capture retry limit? "
                        f"(currently {get_capture_retry_limit()}): "
                    ).strip()
                )

                if limit <= 0:
                    print("✗ Must be a positive number.")
                    continue

                if set_capture_retry_limit(limit):
                    print(f"✓ Capture retry limit set to {limit}.")
                else:
                    print("✗ Invalid value.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "3":

            current = get_skip_shiny_encounters()
            new_state = not current
            set_skip_shiny_encounters(new_state)
            status = "YES (skip shinies)" if new_state else "NO (capture shinies)"
            print(f"✓ Skip shiny encounters: {status}")

        elif choice == "4":

            input("\nPress Enter to return to settings...")
            return

        else:

            print("✗ Invalid choice.")


def _safety_settings():

    print()
    print("=" * 60)
    print("SAFETY SETTINGS")
    print("=" * 60)

    while True:

        current = get_auto_stop_consecutive_failures()
        status = f"{current} consecutive failures" if current else "DISABLED"

        print()
        print(f"Auto-stop on failures: {status}")
        print()
        print("1. Set auto-stop threshold")
        print("2. Disable auto-stop")
        print("3. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":

            try:
                threshold = int(
                    input(
                        "Stop after how many consecutive capture failures? "
                        "(or blank to keep current): "
                    ).strip()
                )

                if threshold <= 0:
                    print("✗ Must be a positive number.")
                    continue

                if set_auto_stop_consecutive_failures(threshold):
                    print(f"✓ Auto-stop set to {threshold} consecutive failures.")
                else:
                    print("✗ Invalid value.")

            except ValueError:
                if input().strip() == "":
                    print("Unchanged.")
                else:
                    print("✗ Invalid number.")

        elif choice == "2":

            if set_auto_stop_consecutive_failures(None):
                print("✓ Auto-stop disabled.")
            else:
                print("✗ Could not disable.")

        elif choice == "3":

            input("\nPress Enter to return to settings...")
            return

        else:

            print("✗ Invalid choice.")


def _system_settings():

    print()
    print("=" * 60)
    print("SYSTEM SETTINGS")
    print("=" * 60)

    while True:

        current_level = get_log_level()

        print()
        print(f"Log level: {current_level}")
        print("  (verbose = all logs, normal = important only, minimal = errors only)")
        print()
        print("1. Set log level")
        print("2. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":

            print()
            print("Log level options:")
            print("  1. verbose (all output)")
            print("  2. normal (important only)")
            print("  3. minimal (errors and milestones only)")

            level_choice = input("\nChoose: ").strip()

            if level_choice == "1":
                set_log_level("verbose")
                print("✓ Log level set to verbose.")

            elif level_choice == "2":
                set_log_level("normal")
                print("✓ Log level set to normal.")

            elif level_choice == "3":
                set_log_level("minimal")
                print("✓ Log level set to minimal.")

            else:
                print("✗ Invalid choice.")

        elif choice == "2":

            input("\nPress Enter to return to settings...")
            return

        else:

            print("✗ Invalid choice.")


def _advanced_timing_settings():

    print()
    print("=" * 60)
    print("ADVANCED SETTINGS — TIMING")
    print("=" * 60)

    while True:

        print()
        print(f"Search encounter timeout: {get_search_encounter_timeout()} seconds")
        print(f"Ball selection delay: {get_ball_selection_delay()} ms")
        print(f"Encounter detection retry: {get_encounter_detection_retry_delay()} ms")
        print()
        print("1. Set search encounter timeout")
        print("2. Set ball selection delay")
        print("3. Set encounter detection retry delay")
        print("4. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":

            try:
                seconds = int(
                    input(
                        f"Search encounter timeout (seconds)? "
                        f"(currently {get_search_encounter_timeout()}): "
                    ).strip()
                )

                if seconds <= 0:
                    print("✗ Must be a positive number.")
                    continue

                if set_search_encounter_timeout(seconds):
                    print(f"✓ Timeout set to {seconds} seconds.")
                else:
                    print("✗ Invalid value.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "2":

            try:
                ms = int(
                    input(
                        f"Ball selection delay (milliseconds)? "
                        f"(currently {get_ball_selection_delay()}): "
                    ).strip()
                )

                if ms <= 0:
                    print("✗ Must be a positive number.")
                    continue

                if set_ball_selection_delay(ms):
                    print(f"✓ Ball selection delay set to {ms} ms.")
                else:
                    print("✗ Invalid value.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "3":

            try:
                ms = int(
                    input(
                        f"Encounter detection retry delay (milliseconds)? "
                        f"(currently {get_encounter_detection_retry_delay()}): "
                    ).strip()
                )

                if ms <= 0:
                    print("✗ Must be a positive number.")
                    continue

                if set_encounter_detection_retry_delay(ms):
                    print(f"✓ Retry delay set to {ms} ms.")
                else:
                    print("✗ Invalid value.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "4":

            input("\nPress Enter to return to settings...")
            return

        else:

            print("✗ Invalid choice.")


def _mining_settings():

    print()
    print("=" * 60)
    print("MINING SETTINGS")
    print("=" * 60)

    while True:

        print()
        print(f"Poll interval: {get_mine_result_poll_interval()} ms")
        print(f"Auto-catch encounters: {'YES' if get_mining_encounter_auto_catch() else 'NO'}")
        print(f"Auto-stop on area cleared: {'YES' if get_auto_stop_mining_on_area_cleared() else 'NO'}")
        print()
        print("1. Set poll interval")
        print("2. Toggle auto-catch encounters")
        print("3. Toggle auto-stop on area cleared")
        print("4. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":

            try:
                ms = int(
                    input(
                        f"Poll interval (milliseconds)? "
                        f"(currently {get_mine_result_poll_interval()}): "
                    ).strip()
                )

                if ms <= 0:
                    print("✗ Must be a positive number.")
                    continue

                if set_mine_result_poll_interval(ms):
                    print(f"✓ Poll interval set to {ms} ms.")
                else:
                    print("✗ Invalid value.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "2":

            current = get_mining_encounter_auto_catch()
            new_state = not current
            set_mining_encounter_auto_catch(new_state)
            status = "YES (catch them)" if new_state else "NO (ignore them)"
            print(f"✓ Auto-catch encounters: {status}")

        elif choice == "3":

            current = get_auto_stop_mining_on_area_cleared()
            new_state = not current
            set_auto_stop_mining_on_area_cleared(new_state)
            status = "YES (stop)" if new_state else "NO (continue)"
            print(f"✓ Auto-stop on area cleared: {status}")

        elif choice == "4":

            input("\nPress Enter to return to settings...")
            return

        else:

            print("✗ Invalid choice.")


def _advanced_network_settings():

    print()
    print("=" * 60)
    print("ADVANCED SETTINGS — NETWORK")
    print("=" * 60)

    while True:

        print()
        print(f"Browser timeout: {get_browser_timeout()} seconds")
        print(f"Max connection retries: {get_max_connection_retries()}")
        print(f"Slow network mode: {'ON (delays × 1.5)' if get_slow_network_mode() else 'OFF (normal delays)'}")
        print()
        print("1. Set browser timeout")
        print("2. Set max connection retries")
        print("3. Toggle slow network mode")
        print("4. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":

            try:
                seconds = int(
                    input(
                        f"Browser timeout (seconds)? "
                        f"(currently {get_browser_timeout()}): "
                    ).strip()
                )

                if seconds <= 0:
                    print("✗ Must be a positive number.")
                    continue

                if set_browser_timeout(seconds):
                    print(f"✓ Timeout set to {seconds} seconds.")
                else:
                    print("✗ Invalid value.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "2":

            try:
                retries = int(
                    input(
                        f"Max connection retries? "
                        f"(currently {get_max_connection_retries()}): "
                    ).strip()
                )

                if retries <= 0:
                    print("✗ Must be a positive number.")
                    continue

                if set_max_connection_retries(retries):
                    print(f"✓ Max retries set to {retries}.")
                else:
                    print("✗ Invalid value.")

            except ValueError:
                print("✗ Invalid number.")

        elif choice == "3":

            current = get_slow_network_mode()
            new_state = not current
            set_slow_network_mode(new_state)
            status = "ON (all delays × 1.5)" if new_state else "OFF (normal delays)"
            print(f"✓ Slow network mode: {status}")

        elif choice == "4":

            input("\nPress Enter to return to settings...")
            return

        else:

            print("✗ Invalid choice.")


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
        print("4. Safety Settings")
        print("5. System Settings")
        print("6. Mining Settings")
        print("7. Advanced Settings")
        print("8. Break Timer Settings")
        print("9. Save Settings")
        print("10. Reset Settings")
        print("11. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            _search_settings()

        elif choice == "2":
            _training_settings()

        elif choice == "3":
            _capture_settings()

        elif choice == "4":
            _safety_settings()

        elif choice == "5":
            _system_settings()

        elif choice == "6":
            _mining_settings()

        elif choice == "7":
            _advanced_submenu()

        elif choice == "8":
            _break_settings()

        elif choice == "9":
            _save_settings()

        elif choice == "10":
            _reset_settings()

        elif choice == "11":
            return

        else:
            print("✗ Invalid choice.")


def _advanced_submenu():
    """Submenu for Advanced Settings with Timing and Network options."""
    
    while True:
        
        print()
        print("=" * 60)
        print("ADVANCED SETTINGS")
        print("=" * 60)
        print()
        print("1. Timing Settings")
        print("2. Network Settings")
        print("3. Back")
        
        choice = input("\nChoose: ").strip()
        
        if choice == "1":
            _advanced_timing_settings()
        
        elif choice == "2":
            _advanced_network_settings()
        
        elif choice == "3":
            return
        
        else:
            print("✗ Invalid choice.")
