"""
Training submenu for Eclipse RPG Automation.

Start Training calls train_mode() battle loop.
Supports battle counts, level grinding targets, and difficulty selection.
"""

import os
import sys
import platform
import time
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
# ANSI & STYLING
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
PURPLE = "\033[38;5;141m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"

BORDER_COLOR = PURPLE
CATEGORY_COLOR = f"{BOLD}{CYAN}"
KEY_COLOR = f"{BOLD}{YELLOW}"
NAME_COLOR = f"{BOLD}{WHITE}"
DESC_COLOR = GRAY

ANSI_STRIP_REGEX = re.compile(r"\x1b\[[0-9;]*[mK]")


def _strip_ansi(text: str) -> str:
    return ANSI_STRIP_REGEX.sub("", text)


def _row(content: str, width: int = 71) -> str:
    v_len = len(_strip_ansi(content))
    pad = max(0, width - v_len)
    return f"{BORDER_COLOR}║{RESET}{content}{' ' * pad}{BORDER_COLOR}║{RESET}"


# In-memory settings
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


def get_between_battles_wait():
    return training_get_between_battles_wait()


def set_menu_between_battles_wait(min_val, max_val):
    return training_set_between_battles_wait(min_val, max_val)


# ============================================================
# ACTIONS
# ============================================================

def _start_training(driver):
    global _last_session_result
    result = train_mode(
        driver,
        max_battles=_battle_count_setting,
        difficulty=_difficulty_setting,
    )
    _last_session_result = result


def _train_until_level_menu(driver):
    global _last_session_result

    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}🎯  TRAIN UNTIL LEVEL{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Auto-battle continuously until target level is reached.{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()

    target_level_input = input(
        f"{BOLD}{CYAN}❯ Target Level:{RESET} "
    ).strip()

    try:
        target_level = int(target_level_input)
    except ValueError:
        print(f"{RED}✗ Invalid level number.{RESET}")
        time.sleep(1.2)
        return

    if target_level <= 0:
        print(f"{RED}✗ Level must be greater than 0.{RESET}")
        time.sleep(1.2)
        return

    max_safety_battles = input(
        f"{BOLD}{CYAN}❯ Safety limit in battles {GRAY}[default {MAX_LEVEL_BATTLES:,}]{CYAN}:{RESET} "
    ).strip()

    if max_safety_battles:
        try:
            max_safety_battles = int(max_safety_battles)
        except ValueError:
            print(f"{YELLOW}⚠ Invalid number - using default ({MAX_LEVEL_BATTLES:,}).{RESET}")
            max_safety_battles = MAX_LEVEL_BATTLES
    else:
        max_safety_battles = MAX_LEVEL_BATTLES

    print()
    print(f"{GREEN}✓ Target set:{RESET} Level {BOLD}{WHITE}{target_level:,}{RESET} {GRAY}(Max safety limit: {max_safety_battles:,} battles){RESET}")
    time.sleep(0.8)

    result = train_until_level(
        driver,
        target_level=target_level,
        max_battles=max_safety_battles,
        difficulty=_difficulty_setting,
    )

    _last_session_result = result

    print()
    input(f"{GRAY}Press Enter to return to training menu...{RESET}")


def _training_settings():
    global _battle_count_setting, _difficulty_setting

    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    while True:
        min_wait, max_wait = training_get_between_battles_wait()
        diff_name = (
            DIFFICULTY_LABELS.get(_difficulty_setting, _difficulty_setting)
            if _difficulty_setting
            else "(site default)"
        )

        print()
        print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
        print(_drow(f"  {BOLD}{MAGENTA}⚙️  TRAINING SETTINGS{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {GRAY}Battles / Session:{RESET} {CYAN}{_battle_count_setting}{RESET}"))
        print(_drow(f"  {GRAY}Battle Difficulty:{RESET} {CYAN}{diff_name}{RESET}"))
        print(_drow(f"  {GRAY}Delay / Battles:  {RESET} {CYAN}{min_wait:.2f}s - {max_wait:.2f}s{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {KEY_COLOR}[ 1]{RESET} {WHITE}Set Battles Per Session{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 2]{RESET} {WHITE}Set Battle Difficulty{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 3]{RESET} {WHITE}Set Wait Between Battles{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 4]{RESET} {WHITE}Back{RESET}"))
        print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")

        choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-4]{CYAN}:{RESET} ").strip()

        if choice == "1":
            answer = input(
                f"\n{BOLD}{CYAN}❯ New battles-per-session value {GRAY}[currently {_battle_count_setting}]{CYAN}:{RESET} "
            ).strip()

            if answer:
                try:
                    value = int(answer)
                except ValueError:
                    print(f"{RED}✗ Invalid number - unchanged.{RESET}")
                    time.sleep(1.0)
                    continue

                if value <= 0:
                    print(f"{RED}✗ Must be a positive number - unchanged.{RESET}")
                    time.sleep(1.0)
                else:
                    _battle_count_setting = value
                    print(f"{GREEN}✓ Battles per session set to {value}.{RESET}")
                    time.sleep(1.0)

        elif choice == "2":
            print()
            print(f"{CATEGORY_COLOR}Select Battle Difficulty:{RESET}")
            print(f"  {KEY_COLOR}[ 0]{RESET} Don't change (site default)")
            for i, value in enumerate(DIFFICULTY_VALUES, 1):
                print(f"  {KEY_COLOR}[ {i}]{RESET} {DIFFICULTY_LABELS[value]}")

            difficulty_choice = input(f"\n{BOLD}{CYAN}❯ Choose difficulty {GRAY}[0-5]{CYAN}:{RESET} ").strip()

            if difficulty_choice:
                try:
                    index = int(difficulty_choice)
                except ValueError:
                    print(f"{RED}✗ Invalid choice - difficulty unchanged.{RESET}")
                    time.sleep(1.0)
                    continue

                if index == 0:
                    _difficulty_setting = None
                    print(f"{GREEN}✓ Difficulty set to site default.{RESET}")
                    time.sleep(1.0)
                elif 1 <= index <= len(DIFFICULTY_VALUES):
                    _difficulty_setting = DIFFICULTY_VALUES[index - 1]
                    print(f"{GREEN}✓ Difficulty set to {DIFFICULTY_LABELS[_difficulty_setting]}.{RESET}")
                    time.sleep(1.0)
                else:
                    print(f"{RED}✗ Invalid choice - difficulty unchanged.{RESET}")
                    time.sleep(1.0)

        elif choice == "3":
            try:
                min_input = float(input(f"{BOLD}{CYAN}❯ Min wait seconds {GRAY}[currently {min_wait:.2f}]{CYAN}:{RESET} ").strip())
                max_input = float(input(f"{BOLD}{CYAN}❯ Max wait seconds {GRAY}[currently {max_wait:.2f}]{CYAN}:{RESET} ").strip())

                if min_input <= 0 or max_input <= 0:
                    print(f"{RED}✗ Values must be positive.{RESET}")
                    time.sleep(1.0)
                    continue

                if min_input > max_input:
                    min_input, max_input = max_input, min_input

                if training_set_between_battles_wait(min_input, max_input):
                    print(f"{GREEN}✓ Wait between battles set to {min_input:.2f}s - {max_input:.2f}s.{RESET}")
                    time.sleep(1.0)
                else:
                    print(f"{RED}✗ Invalid values.{RESET}")
                    time.sleep(1.0)
            except ValueError:
                print(f"{RED}✗ Invalid number.{RESET}")
                time.sleep(1.0)

        elif choice == "4":
            return

        else:
            print(f"{RED}✗ Invalid choice.{RESET}")
            time.sleep(1.0)


def _training_status():
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    diff_label = (
        DIFFICULTY_LABELS.get(_difficulty_setting, _difficulty_setting)
        if _difficulty_setting
        else "(site default)"
    )

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}📊  TRAINING STATUS & STATS{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Battles / Session (Setting):{RESET} {CYAN}{_battle_count_setting}{RESET}"))
    print(_drow(f"  {GRAY}Battle Difficulty (Setting):{RESET} {CYAN}{diff_label}{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    if _last_session_result is None:
        print(_drow(f"  {GRAY}No training run recorded yet this session.{RESET}"))
    else:
        battles = _last_session_result.get("battles", 0)
        current_level = _last_session_result.get("current_level")
        exp_gained = _last_session_result.get("exp_gained", 0)

        print(_drow(f"  {WHITE}Last Session Completed:{RESET} {GREEN}{battles}{RESET} battles"))
        if current_level is not None:
            print(_drow(f"  {WHITE}Ending Level:{RESET}           {YELLOW}Lv. {current_level:,}{RESET}"))
        if exp_gained:
            print(_drow(f"  {WHITE}EXP Gained:             {RESET} {GREEN}+{exp_gained:,}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return to the training menu...{RESET}")


def training_menu(driver):
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    while True:
        diff_label = (
            DIFFICULTY_LABELS.get(_difficulty_setting, _difficulty_setting)
            if _difficulty_setting
            else "Site Default"
        )
        min_w, max_w = training_get_between_battles_wait()
        hud = f"  {GRAY}CONFIG:{RESET} {CYAN}{_battle_count_setting} Battles{RESET}  │  {GRAY}DIFFICULTY:{RESET} {CYAN}{diff_label}{RESET}  │  {GRAY}DELAY:{RESET} {CYAN}{min_w:.1f}-{max_w:.1f}s{RESET}"

        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}⚔️  TRAINING & AUTO-BATTLE{RESET}", w))
        print(mid_border)
        print(_row(hud, w))
        print(mid_border)
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 1]{RESET} {NAME_COLOR}Start Training{RESET}     {DESC_COLOR}— Run auto-battle loop ({_battle_count_setting} battles){RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 2]{RESET} {NAME_COLOR}Train Until Level{RESET}  {DESC_COLOR}— Automatically battle until target level reached{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 3]{RESET} {NAME_COLOR}Training Settings{RESET}  {DESC_COLOR}— Adjust battles, difficulty & delay intervals{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 4]{RESET} {NAME_COLOR}View Status & Stats{RESET}{DESC_COLOR}— Check last session battle & EXP outcomes{RESET}", w))
        print(_row("", w))
        print(_row(f"    {RED}{BOLD}[ 5]{RESET} {RED}Back{RESET}               {DESC_COLOR}— Return to main menu{RESET}", w))
        print(_row("", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-5]{CYAN}:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            _start_training(driver)
        elif choice == "2":
            _train_until_level_menu(driver)
        elif choice == "3":
            _training_settings()
        elif choice == "4":
            _training_status()
        elif choice == "5":
            return
        else:
            print(f"\n{RED}✗ Invalid choice '{choice}'. Please choose 1-5.{RESET}")
            time.sleep(1.0)
