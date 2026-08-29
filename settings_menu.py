"""
Central Settings menu for Eclipse RPG Automation.

Hub for Search, Training, Capture, Safety, System, and Break Timer settings.
Supports persistent saving and resetting to defaults.
"""

import os
import sys
import platform
import time
import re

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
)
from training import (
    get_between_battles_wait,
    set_between_battles_wait,
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
GOLD = "\033[38;5;220m"

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


# ============================================================
# SETTINGS SUBMENUS
# ============================================================

def _capture_settings():
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    while True:
        balls = ", ".join(get_preferred_ball_order())
        limit = get_capture_retry_limit()
        skip = "YES (skip shinies)" if get_skip_shiny_encounters() else "NO (capture shinies)"

        print()
        print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
        print(_drow(f"  {BOLD}{MAGENTA}🎯  CAPTURE SETTINGS{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {GRAY}Ball Priority:{RESET} {CYAN}{balls}{RESET}"))
        print(_drow(f"  {GRAY}Retry Limit:  {RESET} {CYAN}{limit} attempts / encounter{RESET}"))
        print(_drow(f"  {GRAY}Skip Shinies: {RESET} {YELLOW}{skip}{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {KEY_COLOR}[ 1]{RESET} {WHITE}Set Poké Ball Priority Order{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 2]{RESET} {WHITE}Set Capture Retry Limit{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 3]{RESET} {WHITE}Toggle Skip Shiny Encounters{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 4]{RESET} {WHITE}Back{RESET}"))
        print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")

        choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-4]{CYAN}:{RESET} ").strip()

        if choice == "1":
            print(f"\n{GRAY}Enter new priority order as comma-separated ball names (e.g. Ultra Ball, Great Ball, Pokeball):{RESET}")
            answer = input(f"{BOLD}{CYAN}❯ Priority order [blank to keep current]:{RESET} ").strip()

            if not answer:
                print(f"{GRAY}Unchanged.{RESET}")
                time.sleep(0.8)
                continue

            order = [name.strip() for name in answer.split(",") if name.strip()]
            if set_preferred_ball_order(order):
                print(f"{GREEN}✓ Ball priority set to: {', '.join(order)}{RESET}")
                time.sleep(1.0)
            else:
                print(f"{RED}✗ Invalid order.{RESET}")
                time.sleep(1.0)

        elif choice == "2":
            try:
                limit_in = int(input(f"{BOLD}{CYAN}❯ Capture retry limit [currently {limit}]:{RESET} ").strip())
                if limit_in <= 0:
                    print(f"{RED}✗ Must be a positive number.{RESET}")
                    time.sleep(1.0)
                    continue

                if set_capture_retry_limit(limit_in):
                    print(f"{GREEN}✓ Capture retry limit set to {limit_in}.{RESET}")
                    time.sleep(1.0)
                else:
                    print(f"{RED}✗ Invalid value.{RESET}")
                    time.sleep(1.0)
            except ValueError:
                print(f"{RED}✗ Invalid number.{RESET}")
                time.sleep(1.0)

        elif choice == "3":
            current = get_skip_shiny_encounters()
            new_state = not current
            set_skip_shiny_encounters(new_state)
            status = "YES (skip shinies)" if new_state else "NO (capture shinies)"
            print(f"{GREEN}✓ Skip shiny encounters set to: {status}{RESET}")
            time.sleep(1.0)

        elif choice == "4":
            return
        else:
            print(f"{RED}✗ Invalid choice.{RESET}")
            time.sleep(1.0)


def _safety_settings():
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    while True:
        current = get_auto_stop_consecutive_failures()
        status = f"{current} consecutive failures" if current else "DISABLED"

        print()
        print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
        print(_drow(f"  {BOLD}{MAGENTA}🛡️  SAFETY & AUTO-STOP SETTINGS{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {GRAY}Auto-stop on Failures:{RESET} {CYAN}{status}{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {KEY_COLOR}[ 1]{RESET} {WHITE}Set Auto-Stop Failure Threshold{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 2]{RESET} {WHITE}Disable Auto-Stop{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 3]{RESET} {WHITE}Back{RESET}"))
        print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")

        choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-3]{CYAN}:{RESET} ").strip()

        if choice == "1":
            try:
                threshold = int(input(f"{BOLD}{CYAN}❯ Stop after how many consecutive capture failures?:{RESET} ").strip())
                if threshold <= 0:
                    print(f"{RED}✗ Must be a positive number.{RESET}")
                    time.sleep(1.0)
                    continue

                if set_auto_stop_consecutive_failures(threshold):
                    print(f"{GREEN}✓ Auto-stop set to {threshold} consecutive failures.{RESET}")
                    time.sleep(1.0)
                else:
                    print(f"{RED}✗ Invalid value.{RESET}")
                    time.sleep(1.0)
            except ValueError:
                print(f"{RED}✗ Invalid number.{RESET}")
                time.sleep(1.0)

        elif choice == "2":
            if set_auto_stop_consecutive_failures(None):
                print(f"{GREEN}✓ Auto-stop disabled.{RESET}")
                time.sleep(1.0)
            else:
                print(f"{RED}✗ Could not disable.{RESET}")
                time.sleep(1.0)

        elif choice == "3":
            return
        else:
            print(f"{RED}✗ Invalid choice.{RESET}")
            time.sleep(1.0)


def _system_settings():
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    while True:
        current_level = get_log_level()

        print()
        print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
        print(_drow(f"  {BOLD}{MAGENTA}🖥️  SYSTEM & LOGGING SETTINGS{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {GRAY}Log Level:{RESET} {CYAN}{current_level.upper()}{RESET}"))
        print(_drow(f"  {GRAY}(verbose = all logs, normal = standard, minimal = errors only){RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {KEY_COLOR}[ 1]{RESET} {WHITE}Set Log Level{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 2]{RESET} {WHITE}Back{RESET}"))
        print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")

        choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-2]{CYAN}:{RESET} ").strip()

        if choice == "1":
            print()
            print(f"{CATEGORY_COLOR}Select Output Detail Level:{RESET}")
            print(f"  {KEY_COLOR}[ 1]{RESET} Verbose (Full debug logs)")
            print(f"  {KEY_COLOR}[ 2]{RESET} Normal  (Standard logs & milestones)")
            print(f"  {KEY_COLOR}[ 3]{RESET} Minimal (Errors & critical alerts only)")

            lvl_choice = input(f"\n{BOLD}{CYAN}❯ Choose {GRAY}[1-3]{CYAN}:{RESET} ").strip()

            if lvl_choice == "1":
                set_log_level("verbose")
                print(f"{GREEN}✓ Log level set to verbose.{RESET}")
                time.sleep(1.0)
            elif lvl_choice == "2":
                set_log_level("normal")
                print(f"{GREEN}✓ Log level set to normal.{RESET}")
                time.sleep(1.0)
            elif lvl_choice == "3":
                set_log_level("minimal")
                print(f"{GREEN}✓ Log level set to minimal.{RESET}")
                time.sleep(1.0)
            else:
                print(f"{RED}✗ Invalid choice.{RESET}")
                time.sleep(1.0)

        elif choice == "2":
            return
        else:
            print(f"{RED}✗ Invalid choice.{RESET}")
            time.sleep(1.0)


def _break_settings():
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    while True:
        current = get_break_settings()
        status = f"{GREEN}ENABLED{RESET}" if current["enabled"] else f"{GRAY}DISABLED{RESET}"

        print()
        print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
        print(_drow(f"  {BOLD}{MAGENTA}☕  BREAK TIMER SETTINGS{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {GRAY}Status:        {RESET} {status}"))
        print(_drow(f"  {GRAY}Interval:      {RESET} {CYAN}{current['break_interval_minutes']} minutes{RESET}"))
        print(_drow(f"  {GRAY}Break Duration:{RESET} {CYAN}{current['break_duration_minutes']} minutes{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {KEY_COLOR}[ 1]{RESET} {WHITE}Toggle Break Timer On / Off{RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 2]{RESET} {WHITE}Set Break Interval (minutes){RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 3]{RESET} {WHITE}Set Break Duration (minutes){RESET}"))
        print(_drow(f"  {KEY_COLOR}[ 4]{RESET} {WHITE}Back{RESET}"))
        print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")

        choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-4]{CYAN}:{RESET} ").strip()

        if choice == "1":
            new_state = not current["enabled"]
            set_break_enabled(new_state)
            state_str = f"{GREEN}enabled{RESET}" if new_state else f"{GRAY}disabled{RESET}"
            print(f"✓ Break timer {state_str}.")
            time.sleep(1.0)

        elif choice == "2":
            try:
                minutes = int(input(f"{BOLD}{CYAN}❯ Break after how many minutes? {GRAY}[currently {current['break_interval_minutes']}]{CYAN}:{RESET} ").strip())
                if minutes <= 0:
                    print(f"{RED}✗ Must be a positive number.{RESET}")
                    time.sleep(1.0)
                    continue

                set_break_interval(minutes)
                print(f"{GREEN}✓ Break interval set to {minutes} minutes.{RESET}")
                time.sleep(1.0)
            except ValueError:
                print(f"{RED}✗ Invalid number.{RESET}")
                time.sleep(1.0)

        elif choice == "3":
            try:
                minutes = int(input(f"{BOLD}{CYAN}❯ Break duration in minutes? {GRAY}[currently {current['break_duration_minutes']}]{CYAN}:{RESET} ").strip())
                if minutes <= 0:
                    print(f"{RED}✗ Must be a positive number.{RESET}")
                    time.sleep(1.0)
                    continue

                set_break_duration(minutes)
                print(f"{GREEN}✓ Break duration set to {minutes} minutes.{RESET}")
                time.sleep(1.0)
            except ValueError:
                print(f"{RED}✗ Invalid number.{RESET}")
                time.sleep(1.0)

        elif choice == "4":
            return
        else:
            print(f"{RED}✗ Invalid choice.{RESET}")
            time.sleep(1.0)


def _save_settings():
    current = settings.gather_current_settings()

    print()
    if settings.save_settings(current):
        print(f"{GREEN}✓ Settings saved successfully to settings.json - they will persist across sessions.{RESET}")
    else:
        print(f"{RED}✗ Could not save settings to disk.{RESET}")

    time.sleep(1.0)
    input(f"\n{GRAY}Press Enter to return to settings...{RESET}")


def _reset_settings():
    print()
    confirm = input(f"{YELLOW}⚠ Reset all settings to factory defaults? [y/N]:{RESET} ").strip().lower()

    if confirm != "y":
        print(f"{GRAY}Cancelled.{RESET}")
        time.sleep(0.8)
        return

    settings.apply_settings(settings.DEFAULT_SETTINGS)
    settings.save_settings(settings.DEFAULT_SETTINGS)

    print(f"{GREEN}✓ Settings successfully reset to default values.{RESET}")
    time.sleep(1.0)
    input(f"\n{GRAY}Press Enter to return to settings...{RESET}")


def settings_menu(driver):
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    while True:
        bs = get_break_settings()
        brk_status = "ON" if bs["enabled"] else "OFF"
        lvl = get_log_level().upper()
        hud = f"  {GRAY}PROFILE:{RESET} {CYAN}Active Config{RESET}  │  {GRAY}LOGS:{RESET} {CYAN}{lvl}{RESET}  │  {GRAY}BREAKS:{RESET} {CYAN}{brk_status}{RESET}  │  {GRAY}AUTO-SAVE:{RESET} {GREEN}Ready{RESET}"

        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}⚙️  CENTRAL SETTINGS HUB{RESET}", w))
        print(mid_border)
        print(_row(hud, w))
        print(mid_border)
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 1]{RESET} {NAME_COLOR}Search Settings{RESET}      {DESC_COLOR}— Custom delay intervals between map searches{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 2]{RESET} {NAME_COLOR}Training Settings{RESET}    {DESC_COLOR}— Battles/session, difficulty & battle pauses{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 3]{RESET} {NAME_COLOR}Capture Settings{RESET}     {DESC_COLOR}— Poké Ball priority order & retry limits{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 4]{RESET} {NAME_COLOR}Safety Settings{RESET}      {DESC_COLOR}— Auto-stop thresholds on consecutive failures{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 5]{RESET} {NAME_COLOR}System Settings{RESET}      {DESC_COLOR}— Output detail level (verbose / normal / min){RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 6]{RESET} {NAME_COLOR}Break Timer{RESET}          {DESC_COLOR}— Periodic break interval and rest duration{RESET}", w))
        print(_row("", w))
        print(_row(f"    {GREEN}{BOLD}[ 7]{RESET} {GREEN}Save Settings{RESET}        {DESC_COLOR}— Write current settings to settings.json{RESET}", w))
        print(_row(f"    {YELLOW}{BOLD}[ 8]{RESET} {YELLOW}Reset to Defaults{RESET}    {DESC_COLOR}— Restore original out-of-the-box settings{RESET}", w))
        print(_row("", w))
        print(_row(f"    {RED}{BOLD}[ 9]{RESET} {RED}Back{RESET}                 {DESC_COLOR}— Return to main menu{RESET}", w))
        print(_row("", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-9]{CYAN}:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

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
            _break_settings()
        elif choice == "7":
            _save_settings()
        elif choice == "8":
            _reset_settings()
        elif choice == "9":
            return
        else:
            print(f"\n{RED}✗ Invalid choice '{choice}'. Please choose 1-9.{RESET}")
            time.sleep(1.0)
