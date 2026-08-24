"""
Training submenu for Eclipse RPG Automation.

Start Training calls the exact same train_mode() battle loop
as before - the only change to training.py itself was making
the battle count an optional parameter (defaulting to the same
100 it always used) instead of a hardcoded constant, so this
menu can offer a configurable count without touching the loop
logic, selectors, or battle-state handling at all.
"""

from training import train_mode, MAX_BATTLES


# In-memory only for now (this session). Persistent settings
# storage is planned for a later Settings phase.
_battle_count_setting = MAX_BATTLES
_last_session_battles = None


def _start_training(driver):

    global _last_session_battles

    result = train_mode(driver, max_battles=_battle_count_setting)

    _last_session_battles = result


def _training_settings():

    global _battle_count_setting

    print()
    print("=" * 60)
    print("TRAINING SETTINGS")
    print("=" * 60)
    print()
    print(f"Battles per session: {_battle_count_setting}")

    answer = input(
        "\nNew battles-per-session value (blank to keep current): "
    ).strip()

    if not answer:
        print("Unchanged.")
        return

    try:
        value = int(answer)

    except ValueError:
        print("✗ Invalid number.")
        return

    if value <= 0:
        print("✗ Must be a positive number.")
        return

    _battle_count_setting = value

    print(f"✓ Battles per session set to {value}.")


def _training_status():

    print()
    print("=" * 60)
    print("TRAINING STATUS")
    print("=" * 60)
    print()
    print(f"Battles per session (setting): {_battle_count_setting}")

    if _last_session_battles is None:
        print("Last session: no training run yet this session.")
    else:
        print(f"Last session: {_last_session_battles} battle(s) completed.")

    input("\nPress Enter to return to the training menu...")


def training_menu(driver):
    while True:

        print()
        print("=" * 60)
        print("TRAINING")
        print("=" * 60)
        print()
        print("1. Start Training")
        print("2. Training Settings")
        print("3. View Training Status")
        print("4. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            _start_training(driver)

        elif choice == "2":
            _training_settings()

        elif choice == "3":
            _training_status()

        elif choice == "4":
            return

        else:
            print("✗ Invalid choice.")
