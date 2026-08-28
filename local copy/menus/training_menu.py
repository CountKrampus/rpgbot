"""
Training submenu for Eclipse RPG Automation.

Start Training calls the exact same train_mode() battle loop
training.py already has. training.py itself has grown a lot
since this menu was first written (it now returns a stats dict
- battles/current_level/target_level/exp_gained - instead of a
plain battle count, and gained battle-difficulty support) - this
file is updated to match that shape.
"""

from training import (
    train_mode,
    MAX_BATTLES,
    DIFFICULTY_VALUES,
    DIFFICULTY_LABELS,
)


# In-memory for now - see settings.py for the persistent layer
# used by the central Settings menu.
_battle_count_setting = MAX_BATTLES
_difficulty_setting = None  # None = don't change the site's current difficulty
_last_session_result = None


def get_battle_count_setting():
    return _battle_count_setting


def set_battle_count_setting(value):

    global _battle_count_setting

    if value <= 0:
        return False

    _battle_count_setting = value

    return True


def get_difficulty_setting():
    return _difficulty_setting


def set_difficulty_setting(value):

    global _difficulty_setting

    if value is not None and value not in DIFFICULTY_VALUES:
        return False

    _difficulty_setting = value

    return True


def _start_training(driver):

    global _last_session_result

    result = train_mode(
        driver,
        max_battles=_battle_count_setting,
        difficulty=_difficulty_setting,
    )

    _last_session_result = result


def _training_settings():

    global _battle_count_setting, _difficulty_setting

    print()
    print("=" * 60)
    print("TRAINING SETTINGS")
    print("=" * 60)
    print()
    print(f"Battles per session: {_battle_count_setting}")

    difficulty_label = (
        DIFFICULTY_LABELS.get(_difficulty_setting, _difficulty_setting)
        if _difficulty_setting
        else "(site default - unchanged)"
    )

    print(f"Battle difficulty: {difficulty_label}")

    answer = input(
        "\nNew battles-per-session value (blank to keep current): "
    ).strip()

    if answer:

        try:
            value = int(answer)

        except ValueError:
            print("✗ Invalid number - battles-per-session unchanged.")
            value = None

        if value is not None:

            if value <= 0:
                print("✗ Must be a positive number - unchanged.")
            else:
                _battle_count_setting = value
                print(f"✓ Battles per session set to {value}.")

    print()
    print("Battle difficulty options:")
    print("  0. Don't change (site default)")

    for i, value in enumerate(DIFFICULTY_VALUES, 1):
        print(f"  {i}. {DIFFICULTY_LABELS[value]}")

    difficulty_choice = input(
        "\nChoose a number (blank to keep current): "
    ).strip()

    if difficulty_choice:

        try:
            index = int(difficulty_choice)

        except ValueError:
            print("✗ Invalid choice - difficulty unchanged.")
            index = None

        if index == 0:
            _difficulty_setting = None
            print("✓ Difficulty set to site default.")

        elif index is not None and 1 <= index <= len(DIFFICULTY_VALUES):
            _difficulty_setting = DIFFICULTY_VALUES[index - 1]
            print(
                f"✓ Difficulty set to "
                f"{DIFFICULTY_LABELS[_difficulty_setting]}."
            )

        elif index is not None:
            print("✗ Invalid choice - difficulty unchanged.")


def _training_status():

    print()
    print("=" * 60)
    print("TRAINING STATUS")
    print("=" * 60)
    print()
    print(f"Battles per session (setting): {_battle_count_setting}")

    difficulty_label = (
        DIFFICULTY_LABELS.get(_difficulty_setting, _difficulty_setting)
        if _difficulty_setting
        else "(site default)"
    )

    print(f"Battle difficulty (setting): {difficulty_label}")

    if _last_session_result is None:

        print("\nLast session: no training run yet this session.")

    else:

        battles = _last_session_result.get("battles", 0)
        current_level = _last_session_result.get("current_level")
        exp_gained = _last_session_result.get("exp_gained", 0)

        print()
        print(f"Last session battles completed: {battles}")

        if current_level is not None:
            print(f"Level at end of session: {current_level:,}")

        if exp_gained:
            print(f"EXP gained: {exp_gained:,}")

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
