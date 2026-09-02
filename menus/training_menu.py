"""
Training submenu for Eclipse RPG Automation.

Start Training calls the exact same train_mode() battle loop
training.py already has. training.py itself has grown a lot
since this menu was first written (it now returns a stats dict
- battles/current_level/target_level/exp_gained - instead of a
plain battle count, and gained battle-difficulty support) - this
file is updated to match that shape.

Advanced options (train until level, etc.) are also exposed here.
"""

import re

from training import (
    train_mode,
    train_until_level,
    MAX_BATTLES,
    MAX_LEVEL_BATTLES,
    DIFFICULTY_VALUES,
    DIFFICULTY_LABELS,
    get_between_battles_wait as training_get_between_battles_wait,
    set_between_battles_wait as training_set_between_battles_wait,
)


# ============================================================
# ANSI COLOR PALETTE
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

# Text Colors
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
PURPLE = "\033[38;5;141m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"
GOLD = "\033[38;5;220m"

# Theme Elements
BORDER_COLOR = PURPLE
CATEGORY_COLOR = f"{BOLD}{CYAN}"
KEY_COLOR = f"{BOLD}{YELLOW}"
NAME_COLOR = f"{BOLD}{WHITE}"
DESC_COLOR = GRAY

ANSI_STRIP_REGEX = re.compile(
    r"\x1b\[[0-9;]*[mK]"
)


# ============================================================
# IN-MEMORY SETTINGS
# ============================================================

_battle_count_setting = MAX_BATTLES
_difficulty_setting = None
_last_session_result = None


# ============================================================
# DISPLAY HELPERS
# ============================================================

def _strip_ansi(text: str) -> str:
    """
    Strip ANSI escape sequences for accurate length calculation.
    """
    return ANSI_STRIP_REGEX.sub(
        "",
        text,
    )


def _row(
    content: str,
    width: int = 71,
) -> str:
    """
    Format a box row so visible characters match the inner width.
    """

    visible_length = len(
        _strip_ansi(content)
    )

    padding = max(
        0,
        width - visible_length,
    )

    return (
        f"{BORDER_COLOR}║{RESET}"
        f"{content}"
        f"{' ' * padding}"
        f"{BORDER_COLOR}║{RESET}"
    )


def _top_border(width: int = 71) -> str:
    return (
        f"{BORDER_COLOR}╔"
        f"{'═' * width}"
        f"╗{RESET}"
    )


def _mid_border(width: int = 71) -> str:
    return (
        f"{BORDER_COLOR}╠"
        f"{'═' * width}"
        f"╣{RESET}"
    )


def _bottom_border(width: int = 71) -> str:
    return (
        f"{BORDER_COLOR}╚"
        f"{'═' * width}"
        f"╝{RESET}"
    )


def _section(title: str):
    """
    Print a styled section divider.
    """

    print()

    line_length = max(
        0,
        45 - len(title),
    )

    print(
        f"  {BORDER_COLOR}{BOLD}"
        f"─── {title} "
        f"{'─' * line_length}"
        f"{RESET}"
    )


def _success(message: str):
    """
    Print a styled success message.
    """

    print(
        f"  {GREEN}{BOLD}●{RESET} "
        f"{GREEN}{message}{RESET}"
    )


def _info(message: str):
    """
    Print a styled informational message.
    """

    print(
        f"  {CYAN}{BOLD}●{RESET} "
        f"{WHITE}{message}{RESET}"
    )


def _warning(message: str):
    """
    Print a styled warning message.
    """

    print(
        f"  {YELLOW}{BOLD}▲{RESET} "
        f"{YELLOW}{message}{RESET}"
    )


def _error(message: str):
    """
    Print a styled error message.
    """

    print(
        f"  {RED}{BOLD}✖{RESET} "
        f"{RED}{message}{RESET}"
    )


def _print_title(
    title: str,
    subtitle: str = "",
):
    """
    Print the standard Eclipse RPG submenu header.
    """

    width = 71

    print()
    print(
        _top_border(width)
    )

    print(
        _row(
            f"  {MAGENTA}{BOLD}ECLIPSE RPG BOT{RESET}",
            width,
        )
    )

    print(
        _row(
            f"  {PURPLE}"
            f"────────────────────────────────────────────────────────────"
            f"{RESET}",
            width,
        )
    )

    print(
        _row(
            f"  {CATEGORY_COLOR}{title}{RESET}",
            width,
        )
    )

    if subtitle:

        print(
            _row(
                f"  {GRAY}{subtitle}{RESET}",
                width,
            )
        )

    print(
        _bottom_border(width)
    )


def _pause(
    message="Press Enter to return to the training menu..."
):
    """
    Styled pause prompt.
    """

    input(
        f"\n{GRAY}{message}{RESET}"
    )


# ============================================================
# SETTINGS ACCESSORS
# ============================================================

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


def get_between_battles_wait():
    """
    Return (min, max) tuple for wait between battles.
    """

    return training_get_between_battles_wait()


def set_menu_between_battles_wait(
    min_val,
    max_val,
):
    """
    Set wait time between battles.
    """

    return training_set_between_battles_wait(
        min_val,
        max_val,
    )


def set_difficulty_setting(value):

    global _difficulty_setting

    if (
        value is not None
        and value not in DIFFICULTY_VALUES
    ):
        return False

    _difficulty_setting = value

    return True


# ============================================================
# START TRAINING
# ============================================================

def _start_training(driver):

    global _last_session_result

    _section(
        "TRAINING SESSION"
    )

    _info(
        f"Starting training for "
        f"{_battle_count_setting:,} battles..."
    )

    difficulty_label = (
        DIFFICULTY_LABELS.get(
            _difficulty_setting,
            _difficulty_setting,
        )
        if _difficulty_setting
        else "Site default"
    )

    _info(
        f"Difficulty: {difficulty_label}"
    )

    min_wait, max_wait = (
        training_get_between_battles_wait()
    )

    _info(
        f"Battle wait: "
        f"{min_wait:.2f} - {max_wait:.2f} seconds"
    )

    print()

    result = train_mode(
        driver,
        max_battles=_battle_count_setting,
        difficulty=_difficulty_setting,
    )

    _last_session_result = result

    print()

    if result:

        battles = result.get(
            "battles",
            0,
        )

        exp_gained = result.get(
            "exp_gained",
            0,
        )

        current_level = result.get(
            "current_level"
        )

        _success(
            f"Training session completed — "
            f"{battles:,} battles."
        )

        if current_level is not None:

            _info(
                f"Ending level: {current_level:,}"
            )

        if exp_gained:

            _info(
                f"EXP gained: {exp_gained:,}"
            )

    else:

        _warning(
            "Training session returned no result."
        )


# ============================================================
# TRAIN UNTIL LEVEL
# ============================================================

def _train_until_level_menu(driver):

    global _last_session_result

    _print_title(
        "TRAIN UNTIL LEVEL",
        "Automatically battle until the selected level is reached.",
    )

    _section(
        "TARGET"
    )

    target_level_input = input(
        f"  {KEY_COLOR}Target level:{RESET} "
    ).strip()

    try:

        target_level = int(
            target_level_input
        )

    except ValueError:

        _error(
            "Invalid level number."
        )

        return

    if target_level <= 0:

        _error(
            "Level must be greater than 0."
        )

        return

    _section(
        "SAFETY LIMIT"
    )

    max_safety_battles = input(
        f"  {KEY_COLOR}Safety limit in battles "
        f"{GRAY}[default {MAX_LEVEL_BATTLES:,}]:{RESET} "
    ).strip()

    if max_safety_battles:

        try:

            max_safety_battles = int(
                max_safety_battles
            )

        except ValueError:

            _warning(
                "Invalid number — using default."
            )

            max_safety_battles = (
                MAX_LEVEL_BATTLES
            )

    else:

        max_safety_battles = (
            MAX_LEVEL_BATTLES
        )

    if max_safety_battles <= 0:

        _error(
            "Safety limit must be greater than 0."
        )

        return

    print()

    print(
        f"  {CATEGORY_COLOR}"
        f"TRAINING PLAN"
        f"{RESET}"
    )

    print(
        f"  {GRAY}Target level:{RESET} "
        f"{GOLD}{BOLD}{target_level:,}{RESET}"
    )

    print(
        f"  {GRAY}Safety limit:{RESET} "
        f"{YELLOW}{max_safety_battles:,} battles{RESET}"
    )

    difficulty_label = (
        DIFFICULTY_LABELS.get(
            _difficulty_setting,
            _difficulty_setting,
        )
        if _difficulty_setting
        else "Site default"
    )

    print(
        f"  {GRAY}Difficulty:{RESET} "
        f"{CYAN}{difficulty_label}{RESET}"
    )

    print()

    _info(
        f"Starting training until level "
        f"{target_level:,}..."
    )

    result = train_until_level(
        driver,
        target_level=target_level,
        max_battles=max_safety_battles,
        difficulty=_difficulty_setting,
    )

    _last_session_result = result

    print()

    if result:

        battles = result.get(
            "battles",
            0,
        )

        current_level = result.get(
            "current_level"
        )

        exp_gained = result.get(
            "exp_gained",
            0,
        )

        _success(
            "Train-until-level session completed."
        )

        _info(
            f"Battles completed: {battles:,}"
        )

        if current_level is not None:

            _info(
                f"Ending level: {current_level:,}"
            )

        if exp_gained:

            _info(
                f"EXP gained: {exp_gained:,}"
            )

    else:

        _warning(
            "Training session returned no result."
        )

    _pause()


# ============================================================
# TRAINING SETTINGS
# ============================================================

def _training_settings():

    global _battle_count_setting
    global _difficulty_setting

    _print_title(
        "TRAINING SETTINGS",
        "Configure battle count, difficulty and battle timing.",
    )

    while True:

        min_wait, max_wait = (
            training_get_between_battles_wait()
        )

        difficulty_label = (
            DIFFICULTY_LABELS.get(
                _difficulty_setting,
                _difficulty_setting,
            )
            if _difficulty_setting
            else "(site default - unchanged)"
        )

        print()
        print(
            _mid_border()
        )

        print(
            _row(
                f"  {CATEGORY_COLOR}CURRENT CONFIGURATION{RESET}",
                71,
            )
        )

        print(
            _row(
                f"    {GRAY}Battles per session:{RESET} "
                f"{GOLD}{_battle_count_setting:,}{RESET}",
                71,
            )
        )

        print(
            _row(
                f"    {GRAY}Battle difficulty:{RESET} "
                f"{CYAN}{difficulty_label}{RESET}",
                71,
            )
        )

        print(
            _row(
                f"    {GRAY}Wait between battles:{RESET} "
                f"{WHITE}{min_wait:.2f} - {max_wait:.2f} seconds{RESET}",
                71,
            )
        )

        print(
            _mid_border()
        )

        print(
            _row(
                f"  {CATEGORY_COLOR}OPTIONS{RESET}",
                71,
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 1]{RESET} "
                f"{NAME_COLOR}Battles per session{RESET} "
                f"{DESC_COLOR}— Set maximum battles for a normal session{RESET}",
                71,
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 2]{RESET} "
                f"{NAME_COLOR}Battle difficulty{RESET} "
                f"{DESC_COLOR}— Choose the difficulty used during training{RESET}",
                71,
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 3]{RESET} "
                f"{NAME_COLOR}Battle wait{RESET} "
                f"{DESC_COLOR}— Configure the minimum and maximum delay{RESET}",
                71,
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 4]{RESET} "
                f"{NAME_COLOR}Back{RESET}",
                71,
            )
        )

        print(
            _bottom_border()
        )

        choice = input(
            f"\n  {KEY_COLOR}Choose:{RESET} "
        ).strip()

        # ----------------------------------------------------
        # BATTLE COUNT
        # ----------------------------------------------------

        if choice == "1":

            answer = input(
                f"\n  {KEY_COLOR}"
                f"New battles-per-session value "
                f"{GRAY}(currently {_battle_count_setting:,}):"
                f"{RESET} "
            ).strip()

            if not answer:
                continue

            try:

                value = int(
                    answer
                )

            except ValueError:

                _error(
                    "Invalid number — unchanged."
                )

                continue

            if value <= 0:

                _error(
                    "Must be a positive number — unchanged."
                )

            else:

                _battle_count_setting = value

                _success(
                    f"Battles per session set to "
                    f"{value:,}."
                )

        # ----------------------------------------------------
        # DIFFICULTY
        # ----------------------------------------------------

        elif choice == "2":

            print()

            print(
                f"  {CATEGORY_COLOR}"
                f"BATTLE DIFFICULTY"
                f"{RESET}"
            )

            print()

            print(
                f"  {KEY_COLOR}[ 0]{RESET} "
                f"{NAME_COLOR}Don't change{RESET} "
                f"{GRAY}— Use site's current difficulty{RESET}"
            )

            for i, value in enumerate(
                DIFFICULTY_VALUES,
                1,
            ):

                print(
                    f"  {KEY_COLOR}[{i:2}]{RESET} "
                    f"{NAME_COLOR}"
                    f"{DIFFICULTY_LABELS[value]}"
                    f"{RESET}"
                )

            difficulty_choice = input(
                f"\n  {KEY_COLOR}"
                f"Choose a number "
                f"{GRAY}(blank to keep current):"
                f"{RESET} "
            ).strip()

            if difficulty_choice:

                try:

                    index = int(
                        difficulty_choice
                    )

                except ValueError:

                    _error(
                        "Invalid choice — difficulty unchanged."
                    )

                    continue

                if index == 0:

                    _difficulty_setting = None

                    _success(
                        "Difficulty set to site default."
                    )

                elif 1 <= index <= len(
                    DIFFICULTY_VALUES
                ):

                    _difficulty_setting = (
                        DIFFICULTY_VALUES[
                            index - 1
                        ]
                    )

                    _success(
                        "Difficulty set to "
                        f"{DIFFICULTY_LABELS[_difficulty_setting]}."
                    )

                else:

                    _error(
                        "Invalid choice — difficulty unchanged."
                    )

        # ----------------------------------------------------
        # BATTLE WAIT
        # ----------------------------------------------------

        elif choice == "3":

            print()

            print(
                f"  {CATEGORY_COLOR}"
                f"WAIT BETWEEN BATTLES"
                f"{RESET}"
            )

            print()

            try:

                min_input = float(
                    input(
                        f"  {KEY_COLOR}"
                        f"Min wait seconds "
                        f"{GRAY}(currently {min_wait:.2f}):"
                        f"{RESET} "
                    ).strip()
                )

                max_input = float(
                    input(
                        f"  {KEY_COLOR}"
                        f"Max wait seconds "
                        f"{GRAY}(currently {max_wait:.2f}):"
                        f"{RESET} "
                    ).strip()
                )

                if (
                    min_input <= 0
                    or max_input <= 0
                ):

                    _error(
                        "Values must be positive."
                    )

                    continue

                if min_input > max_input:

                    min_input, max_input = (
                        max_input,
                        min_input,
                    )

                    _info(
                        "Minimum and maximum values were swapped."
                    )

                if training_set_between_battles_wait(
                    min_input,
                    max_input,
                ):

                    _success(
                        f"Wait between battles set to "
                        f"{min_input:.2f} - "
                        f"{max_input:.2f} seconds."
                    )

                else:

                    _error(
                        "Invalid values."
                    )

            except ValueError:

                _error(
                    "Invalid number."
                )

        # ----------------------------------------------------
        # BACK
        # ----------------------------------------------------

        elif choice == "4":

            return

        else:

            _error(
                "Invalid choice."
            )


# ============================================================
# TRAINING STATUS
# ============================================================

def _training_status():

    _print_title(
        "TRAINING STATUS",
        "Review your current training configuration and last session.",
    )

    print()

    print(
        _mid_border()
    )

    print(
        _row(
            f"  {CATEGORY_COLOR}CURRENT SETTINGS{RESET}",
            71,
        )
    )

    print(
        _row(
            f"    {GRAY}Battles per session:{RESET} "
            f"{GOLD}{_battle_count_setting:,}{RESET}",
            71,
        )
    )

    difficulty_label = (
        DIFFICULTY_LABELS.get(
            _difficulty_setting,
            _difficulty_setting,
        )
        if _difficulty_setting
        else "(site default)"
    )

    print(
        _row(
            f"    {GRAY}Battle difficulty:{RESET} "
            f"{CYAN}{difficulty_label}{RESET}",
            71,
        )
    )

    min_wait, max_wait = (
        training_get_between_battles_wait()
    )

    print(
        _row(
            f"    {GRAY}Battle wait:{RESET} "
            f"{WHITE}{min_wait:.2f} - "
            f"{max_wait:.2f} seconds{RESET}",
            71,
        )
    )

    print(
        _mid_border()
    )

    print(
        _row(
            f"  {CATEGORY_COLOR}LAST SESSION{RESET}",
            71,
        )
    )

    if _last_session_result is None:

        print(
            _row(
                f"    {GRAY}"
                f"No training run yet this session."
                f"{RESET}",
                71,
            )
        )

    else:

        battles = _last_session_result.get(
            "battles",
            0,
        )

        current_level = (
            _last_session_result.get(
                "current_level"
            )
        )

        exp_gained = _last_session_result.get(
            "exp_gained",
            0,
        )

        target_level = (
            _last_session_result.get(
                "target_level"
            )
        )

        print(
            _row(
                f"    {GRAY}Battles completed:{RESET} "
                f"{GREEN}{battles:,}{RESET}",
                71,
            )
        )

        if current_level is not None:

            print(
                _row(
                    f"    {GRAY}Ending level:{RESET} "
                    f"{GOLD}{current_level:,}{RESET}",
                    71,
                )
            )

        if target_level is not None:

            print(
                _row(
                    f"    {GRAY}Target level:{RESET} "
                    f"{YELLOW}{target_level:,}{RESET}",
                    71,
                )
            )

        if exp_gained:

            print(
                _row(
                    f"    {GRAY}EXP gained:{RESET} "
                    f"{CYAN}{exp_gained:,}{RESET}",
                    71,
                )
            )

    print(
        _bottom_border()
    )

    _pause()


# ============================================================
# TRAINING MENU
# ============================================================

def training_menu(driver):

    while True:

        width = 71

        print()

        print(
            _top_border(width)
        )

        print(
            _row(
                f"  {MAGENTA}{BOLD}"
                f"████████╗██████╗  █████╗ ██╗███╗   ██╗██╗███╗   ██╗ ██████╗"
                f"{RESET}",
                width,
            )
        )

        print(
            _row(
                f"  {PURPLE}{BOLD}"
                f"╚══██╔══╝██╔══██╗██╔══██╗██║████╗  ██║██║████╗  ██║██╔════╝"
                f"{RESET}",
                width,
            )
        )

        print(
            _row(
                f"  {CYAN}{BOLD}"
                f"   ██║   ██████╔╝███████║██║██╔██╗ ██║██║██╔██╗ ██║██║  ███╗"
                f"{RESET}",
                width,
            )
        )

        print(
            _row(
                f"  {CYAN}{BOLD}"
                f"   ██║   ██╔══██╗██╔══██║██║██║╚██╗██║██║██║╚██╗██║██║   ██║"
                f"{RESET}",
                width,
            )
        )

        print(
            _row(
                f"  {PURPLE}{BOLD}"
                f"   ██║   ██║  ██║██║  ██║██║██║ ╚████║██║██║ ╚████║╚██████╔╝"
                f"{RESET}",
                width,
            )
        )

        print(
            _row(
                f"  {MAGENTA}{BOLD}"
                f"   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝"
                f"{RESET}",
                width,
            )
        )

        print(
            _mid_border(width)
        )

        print(
            _row(
                f"  {CATEGORY_COLOR}"
                f"PLAY & AUTOMATION"
                f"{RESET}",
                width,
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 1]{RESET} "
                f"{NAME_COLOR}Start Training{RESET} "
                f"{DESC_COLOR}— Run the configured battle session{RESET}",
                width,
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 2]{RESET} "
                f"{NAME_COLOR}Train Until Level{RESET} "
                f"{DESC_COLOR}— Continue training toward a target level{RESET}",
                width,
            )
        )

        print(
            _row(
                "",
                width,
            )
        )

        print(
            _row(
                f"  {CATEGORY_COLOR}"
                f"CONFIGURATION & STATUS"
                f"{RESET}",
                width,
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 3]{RESET} "
                f"{NAME_COLOR}Training Settings{RESET} "
                f"{DESC_COLOR}— Battles, difficulty & timing{RESET}",
                width,
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 4]{RESET} "
                f"{NAME_COLOR}Training Status{RESET} "
                f"{DESC_COLOR}— View settings and last session results{RESET}",
                width,
            )
        )

        print(
            _row(
                "",
                width,
            )
        )

        print(
            _row(
                f"    {RED}{BOLD}[ 5]{RESET} "
                f"{RED}Back{RESET} "
                f"{DESC_COLOR}— Return to the main menu{RESET}",
                width,
            )
        )

        print(
            _row(
                "",
                width,
            )
        )

        print(
            _bottom_border(width)
        )

        choice = input(
            f"\n  {KEY_COLOR}Choose:{RESET} "
        ).strip()

        # ----------------------------------------------------
        # START TRAINING
        # ----------------------------------------------------

        if choice == "1":

            _start_training(
                driver
            )

        # ----------------------------------------------------
        # TRAIN UNTIL LEVEL
        # ----------------------------------------------------

        elif choice == "2":

            _train_until_level_menu(
                driver
            )

        # ----------------------------------------------------
        # SETTINGS
        # ----------------------------------------------------

        elif choice == "3":

            _training_settings()

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        elif choice == "4":

            _training_status()

        # ----------------------------------------------------
        # BACK
        # ----------------------------------------------------

        elif choice == "5":

            return

        else:

            _error(
                "Invalid choice."
            )