"""
Categorized, stylized main menu for Eclipse RPG Automation.

Account is handled by account_menu(driver).
Other sections continue to use their existing menu modules.
"""

import os
import sys
import platform
import time
import re

from mining import miner_mode
from trade import trade_mode
from menus.search_menu import search_menu
from menus.messages_menu import messages_menu
from menus.training_menu import training_menu
from menus.shop_menu import shop_menu
from menus.settings_menu import settings_menu
from menus.pokemon_menu import pokemon_menu
from menus.collection_menu import collection_menu
from menus.update_menu_unfinished import update_menu
from account import account_menu
from break_timer import get_break_settings, get_session_elapsed_time


# ============================================================
# CONSOLE & COLOR SETUP
# ============================================================

def _init_console():
    """
    Ensure UTF-8 encoding and ANSI color support on Windows.
    """
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if platform.system() == "Windows":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32

            # Enable ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004)
            mode = ctypes.c_ulong()
            h_out = kernel32.GetStdHandle(-11)

            if kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
                kernel32.SetConsoleMode(
                    h_out,
                    mode.value | 0x0004
                )

        except Exception:
            pass

        # Triggers ANSI support in Windows console
        os.system("")


_init_console()


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

ANSI_STRIP_REGEX = re.compile(r"\x1b\[[0-9;]*[mK]")


def _strip_ansi(text: str) -> str:
    """
    Strip ANSI escape sequences from string for accurate
    visible-length calculation.
    """
    return ANSI_STRIP_REGEX.sub("", text)


def _row(content: str, width: int = 71) -> str:
    """
    Format a box row such that visible characters match
    the box inner width.
    """
    v_len = len(_strip_ansi(content))
    pad = max(0, width - v_len)

    return (
        f"{BORDER_COLOR}║{RESET}"
        f"{content}"
        f"{' ' * pad}"
        f"{BORDER_COLOR}║{RESET}"
    )


def _get_status_hud():
    """
    Build a dynamic status bar strip reflecting session
    time & break settings.
    """

    try:
        elapsed_sec = int(get_session_elapsed_time())

        hours = elapsed_sec // 3600
        mins = (elapsed_sec % 3600) // 60

        uptime_str = f"{hours}h {mins:02d}m"

    except Exception:
        uptime_str = "0h 00m"

    try:
        bs = get_break_settings()

        if bs.get("enabled"):
            break_str = (
                f"{GREEN}Active "
                f"({bs.get('break_interval_minutes')}m/"
                f"{bs.get('break_duration_minutes')}m)"
                f"{RESET}"
            )
        else:
            break_str = f"{GRAY}Disabled{RESET}"

    except Exception:
        break_str = f"{GRAY}Disabled{RESET}"

    return (
        f"  {GRAY}STATUS:{RESET} {GREEN}● Online{RESET}   "
        f"{GRAY}SESSION:{RESET} {CYAN}{uptime_str}{RESET}   "
        f"{GRAY}BREAK TIMER:{RESET} {break_str}"
    )


def _render_menu():
    """
    Render the stylized dashboard and menu options.
    """

    w = 71

    top_border = (
        f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    )

    mid_border = (
        f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    )

    bot_border = (
        f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"
    )

    banner_art = [
        f"  {MAGENTA}███████╗ ██████╗██╗     ██╗██████╗ ███████╗    ██████╗ ██████╗  ██████╗{RESET}  ",
        f"  {MAGENTA}██╔════╝██╔════╝██║     ██║██╔══██╗██╔════╝    ██╔══██╗██╔══██╗██╔════╝{RESET}  ",
        f"  {PURPLE}█████╗  ██║     ██║     ██║██████╔╝███████╗    ██████╔╝██████╔╝██║  ███╗{RESET}  ",
        f"  {PURPLE}██╔══╝  ██║     ██║     ██║██╔═══╝ ╚════██║    ██╔══██╗██╔═══╝ ██║   ██║{RESET}  ",
        f"  {CYAN}███████╗╚██████╗███████╗██║██║     ███████║    ██║  ██║██║     ╚██████╔╝{RESET}  ",
        f"  {CYAN}╚══════╝ ╚═════╝╚══════╝╚═╝╚═╝     ╚══════╝    ╚═╝  ╚═╝╚═╝      ╚═════╝{RESET}  ",
    ]

    print()
    print(top_border)

    for line in banner_art:
        print(_row(line, w))

    print(mid_border)
    print(_row(_get_status_hud(), w))
    print(mid_border)
    print(_row("", w))

    # ========================================================
    # PLAY & AUTOMATION
    # ========================================================

    print(
        _row(
            f"  {CATEGORY_COLOR}PLAY & AUTOMATION{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 1]{RESET} "
            f"{NAME_COLOR}Training{RESET}     "
            f"{DESC_COLOR}— Auto-battle loop, level grind & EXP rewards{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 2]{RESET} "
            f"{NAME_COLOR}Searching{RESET}    "
            f"{DESC_COLOR}— Map exploration, encounters & exclusive areas{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 3]{RESET} "
            f"{NAME_COLOR}A-Miner{RESET}      "
            f"{DESC_COLOR}— Automated underground mining & fossil hunting{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 4]{RESET} "
            f"{NAME_COLOR}Trading{RESET}      "
            f"{DESC_COLOR}— Trade center automation & direct player trades{RESET}",
            w
        )
    )

    print(_row("", w))

    # ========================================================
    # MANAGEMENT & DATA
    # ========================================================

    print(
        _row(
            f"  {CATEGORY_COLOR}MANAGEMENT & DATA{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 5]{RESET} "
            f"{NAME_COLOR}Messages{RESET}     "
            f"{DESC_COLOR}— Private message inbox, reader & bulk cleanup{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 6]{RESET} "
            f"{NAME_COLOR}Shops{RESET}        "
            f"{DESC_COLOR}— Pokemon market search, filters & auto-purchase{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 7]{RESET} "
            f"{NAME_COLOR}Pokemon{RESET}      "
            f"{DESC_COLOR}— PC Box organizer, party inspector & checklist{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 8]{RESET} "
            f"{NAME_COLOR}Collections{RESET}  "
            f"{DESC_COLOR}— Manual Pokemon collection logs & quantity tracking{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[ 9]{RESET} "
            f"{NAME_COLOR}Account{RESET}      "
            f"{DESC_COLOR}— Profile statistics, keyring & account switch{RESET}",
            w
        )
    )

    print(_row("", w))

    # ========================================================
    # SYSTEM & CONFIG
    # ========================================================

    print(
        _row(
            f"  {CATEGORY_COLOR}SYSTEM & CONFIG{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[10]{RESET} "
            f"{NAME_COLOR}Update Center{RESET}    "
            f"{DESC_COLOR}— Map crawler, database updater & cache tools{RESET}",
            w
        )
    )

    print(
        _row(
            f"    {KEY_COLOR}[11]{RESET} "
            f"{NAME_COLOR}Settings{RESET}     "
            f"{DESC_COLOR}— Delays, Poké Ball priority order & break timer{RESET}",
            w
        )
    )

    print(_row("", w))

    # ========================================================
    # EXIT
    # ========================================================

    print(
        _row(
            f"    {RED}{BOLD}[ 0]{RESET} "
            f"{RED}Exit{RESET}         "
            f"{DESC_COLOR}— Disconnect session & close browser safely{RESET}",
            w
        )
    )

    print(_row("", w))
    print(bot_border)
    print()


def _not_yet_implemented(section_name):
    """
    Stylized placeholder for sections whose feature module
    is in development.
    """

    w = 56

    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)

        return (
            f"{PURPLE}│{RESET}"
            f"{content}"
            f"{' ' * pad}"
            f"{PURPLE}│{RESET}"
        )

    print()
    print(f"{PURPLE}╭{'─' * w}╮{RESET}")

    print(
        _drow(
            f"  {YELLOW}✦ FEATURE IN DEVELOPMENT ✦{RESET}"
        )
    )

    print(f"{PURPLE}├{'─' * w}┤{RESET}")

    print(
        _drow(
            f"  Section: {BOLD}{WHITE}{section_name}{RESET}"
        )
    )

    print(_drow(""))

    print(
        _drow(
            f"  {GRAY}This feature has not been implemented yet.{RESET}"
        )
    )

    print(
        _drow(
            f"  {GRAY}It will be available in an upcoming update.{RESET}"
        )
    )

    print(f"{PURPLE}╰{'─' * w}╯{RESET}")
    print()

    input(
        f"{GRAY}Press Enter to return to the main menu...{RESET}"
    )


def main_menu(driver):

    while True:

        _render_menu()

        try:
            choice = input(
                f"{BOLD}{CYAN}❯ Select Option "
                f"{GRAY}[0-11]"
                f"{CYAN}:{RESET} "
            ).strip()

        except (KeyboardInterrupt, EOFError):
            print(f"\n{YELLOW}Exiting...{RESET}")
            break

        # ----------------------------------------------------
        # TRAINING
        # ----------------------------------------------------
        if choice == "1":
            training_menu(driver)

        # ----------------------------------------------------
        # SEARCHING
        # ----------------------------------------------------
        elif choice == "2":
            search_menu(driver)

        # ----------------------------------------------------
        # A-MINER
        # ----------------------------------------------------
        elif choice == "3":
            miner_mode(driver)

        # ----------------------------------------------------
        # TRADING
        # ----------------------------------------------------
        elif choice == "4":
            trade_mode(driver)

        # ----------------------------------------------------
        # MESSAGES
        # ----------------------------------------------------
        elif choice == "5":
            messages_menu(driver)

        # ----------------------------------------------------
        # SHOPS
        # ----------------------------------------------------
        elif choice == "6":
            shop_menu(driver)

        # ----------------------------------------------------
        # POKEMON
        # ----------------------------------------------------
        elif choice == "7":
            pokemon_menu(driver)

        # ----------------------------------------------------
        # COLLECTIONS
        # ----------------------------------------------------
        elif choice == "8":
            collection_menu(driver)

        # ----------------------------------------------------
        # ACCOUNT
        # ----------------------------------------------------
        elif choice == "9":
            account_menu(driver)

        # ----------------------------------------------------
        # UPDATE CENTER
        # ----------------------------------------------------
        elif choice == "10":
            update_menu(driver)

        # ----------------------------------------------------
        # SETTINGS
        # ----------------------------------------------------
        elif choice == "11":
            settings_menu(driver)

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------
        elif choice == "0":
            print(
                f"\n{GREEN}"
                f"✓ Exiting Eclipse RPG Automation. Goodbye!"
                f"{RESET}\n"
            )
            break

        # ----------------------------------------------------
        # INVALID
        # ----------------------------------------------------
        else:
            print()
            print(
                f"{RED}✗ Invalid choice '{choice}'. "
                f"Please select a number between 0 and 11."
                f"{RESET}"
            )
            time.sleep(1.2)