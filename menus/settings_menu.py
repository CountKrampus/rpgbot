"""
Central Settings menu for Eclipse RPG Automation.

This doesn't duplicate any setting logic - it's a hub that opens
the existing Search Settings and Training Settings screens,
adds a Capture Settings screen (ball priority already had
get/set functions in capture.py but no menu of its own), and
adds Save/Reset for persistence across runs via settings.py.
"""

import os
import platform
import re
import sys

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
    get_slow_network_mode,
    set_slow_network_mode,
    get_session_time_limit,
    set_session_time_limit,
    get_auto_logout_after_session,
    set_auto_logout_after_session,
    get_notify_on_shiny_encounter,
    set_notify_on_shiny_encounter,
)

from browser import (
    BROWSER_LABELS,
    detect_installed_browsers,
    get_browser_allow_fallback,
    get_browser_name,
    set_browser_allow_fallback,
    set_browser_name,
)


# ============================================================
# CONSOLE INITIALIZATION
# ============================================================

def _init_console():
    """
    Ensure UTF-8 encoding and ANSI color support on Windows.
    """

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            pass

    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            pass

    if platform.system() == "Windows":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32

            mode = ctypes.c_ulong()
            h_out = kernel32.GetStdHandle(-11)

            if kernel32.GetConsoleMode(
                h_out,
                ctypes.byref(mode),
            ):
                kernel32.SetConsoleMode(
                    h_out,
                    mode.value | 0x0004,
                )

        except Exception:
            pass

        try:
            os.system("")
        except Exception:
            pass


_init_console()


# ============================================================
# ANSI COLOR PALETTE
# Same palette as the main menu
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

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

ANSI_STRIP_REGEX = re.compile(
    r"\x1b\[[0-9;]*[mK]"
)


# ============================================================
# BOX HELPERS
# ============================================================

BOX_WIDTH = 71


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences for visible-length calculations."""

    return ANSI_STRIP_REGEX.sub("", text)


def _row(
    content: str,
    width: int = BOX_WIDTH,
) -> str:
    """
    Create one padded row inside the box.

    ANSI escape sequences do not count toward visible width.
    """

    visible_length = len(
        _strip_ansi(content)
    )

    if visible_length > width:
        content = _strip_ansi(content)[:width]
        visible_length = width

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


def _top_border(
    width: int = BOX_WIDTH,
) -> str:
    """Return the top border of a menu box."""

    return (
        f"{BORDER_COLOR}╔"
        f"{'═' * width}"
        f"╗{RESET}"
    )


def _middle_border(
    width: int = BOX_WIDTH,
) -> str:
    """Return the middle border of a menu box."""

    return (
        f"{BORDER_COLOR}╠"
        f"{'═' * width}"
        f"╣{RESET}"
    )


def _bottom_border(
    width: int = BOX_WIDTH,
) -> str:
    """Return the bottom border of a menu box."""

    return (
        f"{BORDER_COLOR}╚"
        f"{'═' * width}"
        f"╝{RESET}"
    )


def _center_row(
    text: str,
    color: str = WHITE,
    width: int = BOX_WIDTH,
) -> str:
    """Create a centered colored row."""

    visible_length = len(
        _strip_ansi(text)
    )

    left_padding = max(
        0,
        (width - visible_length) // 2,
    )

    right_padding = max(
        0,
        width
        - visible_length
        - left_padding,
    )

    return (
        f"{BORDER_COLOR}║{RESET}"
        f"{' ' * left_padding}"
        f"{color}{text}{RESET}"
        f"{' ' * right_padding}"
        f"{BORDER_COLOR}║{RESET}"
    )


def _title(
    title: str,
    subtitle: str = "",
):
    """Print a complete menu title box."""

    print()
    print(_top_border())

    print(
        _center_row(
            title,
            f"{BOLD}{MAGENTA}",
        )
    )

    if subtitle:
        print(
            _center_row(
                subtitle,
                f"{DIM}{CYAN}",
            )
        )

    print(_middle_border())


def _blank_row():
    """Print an empty row inside the box."""

    print(_row(""))


def _info(
    message: str,
):
    """Print an informational message inside the box."""

    print(
        _row(
            f" {CYAN}{message}{RESET}"
        )
    )


def _success(
    message: str,
):
    """Print a success message inside the box."""

    print(
        _row(
            f" {GREEN}{BOLD}✓ {message}{RESET}"
        )
    )


def _error(
    message: str,
):
    """Print an error message inside the box."""

    print(
        _row(
            f" {RED}{BOLD}✗ {message}{RESET}"
        )
    )


def _warning(
    message: str,
):
    """Print a warning message inside the box."""

    print(
        _row(
            f" {YELLOW}{BOLD}! {message}{RESET}"
        )
    )


def _setting(
    name: str,
    value: str,
):
    """Print a setting name/value row."""

    content = (
        f" {NAME_COLOR}{name}:{RESET} "
        f"{WHITE}{value}{RESET}"
    )

    print(
        _row(content)
    )


def _option(
    key: str,
    name: str,
    description: str = "",
):
    """Print a boxed menu option."""

    if description:
        content = (
            f" {KEY_COLOR}[{key}]{RESET} "
            f"{NAME_COLOR}{name}{RESET}"
            f" {DESC_COLOR}- {description}{RESET}"
        )
    else:
        content = (
            f" {KEY_COLOR}[{key}]{RESET} "
            f"{NAME_COLOR}{name}{RESET}"
        )

    print(
        _row(content)
    )


def _section(
    title: str,
):
    """Print a section heading inside the box."""

    print(
        _row(
            f" {CATEGORY_COLOR}{title}{RESET}"
        )
    )


def _close_box():
    """Close the current menu box."""

    print(_bottom_border())


def _pause(
    message: str = "Press Enter to return...",
):
    """Pause while keeping the prompt outside the decorative box."""

    input(f"\n{DIM}{message}{RESET}")


# ============================================================
# CAPTURE SETTINGS
# ============================================================

def _capture_settings():

    while True:

        _title(
            "CAPTURE SETTINGS",
            "Pokémon capture behavior",
        )

        _setting(
            "Ball priority order",
            ", ".join(
                get_preferred_ball_order()
            ),
        )

        _setting(
            "Capture retry limit",
            str(
                get_capture_retry_limit()
            ),
        )

        _setting(
            "Skip shiny encounters",
            (
                f"{GREEN}YES{RESET}"
                if get_skip_shiny_encounters()
                else f"{RED}NO{RESET}"
            ),
        )

        _blank_row()

        _option(
            "1",
            "Set ball priority order",
        )

        _option(
            "2",
            "Set capture retry limit",
        )

        _option(
            "3",
            "Toggle skip shiny encounters",
        )

        _option(
            "4",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            current = get_preferred_ball_order()

            print()
            print(
                f"{CYAN}Enter a new priority order as "
                f"comma-separated ball names, most preferred first "
                f"(blank to keep current):{RESET}"
            )
            print(
                f"{DIM}Current: {', '.join(current)}{RESET}"
            )

            answer = input(
                f"{KEY_COLOR}>{RESET} "
            ).strip()

            if not answer:
                print(
                    f"{YELLOW}Unchanged.{RESET}"
                )
                continue

            order = [
                name.strip()
                for name in answer.split(",")
                if name.strip()
            ]

            if set_preferred_ball_order(order):

                print(
                    f"{GREEN}✓ Ball priority set to: "
                    f"{', '.join(order)}{RESET}"
                )

            else:

                print(
                    f"{RED}✗ Invalid order.{RESET}"
                )

        elif choice == "2":

            try:

                limit = int(
                    input(
                        f"\n{CYAN}Capture retry limit? "
                        f"(currently "
                        f"{get_capture_retry_limit()}): "
                    ).strip()
                )

                if limit <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_capture_retry_limit(limit):

                    print(
                        f"{GREEN}✓ Capture retry limit "
                        f"set to {limit}.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "3":

            current = get_skip_shiny_encounters()
            new_state = not current

            set_skip_shiny_encounters(
                new_state
            )

            status = (
                "YES (skip shinies)"
                if new_state
                else "NO (capture shinies)"
            )

            print(
                f"{GREEN}✓ Skip shiny encounters: "
                f"{status}{RESET}"
            )

        elif choice == "4":

            _pause(
                "Press Enter to return to settings..."
            )

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# SAFETY SETTINGS
# ============================================================

def _safety_settings():

    while True:

        current = (
            get_auto_stop_consecutive_failures()
        )

        status = (
            f"{current} consecutive failures"
            if current
            else "DISABLED"
        )

        _title(
            "SAFETY SETTINGS",
            "Automatic failure protection",
        )

        _setting(
            "Auto-stop on failures",
            status,
        )

        _blank_row()

        _option(
            "1",
            "Set auto-stop threshold",
        )

        _option(
            "2",
            "Disable auto-stop",
        )

        _option(
            "3",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            try:

                threshold_input = input(
                    "\nStop after how many consecutive "
                    "capture failures? "
                    "(or blank to keep current): "
                ).strip()

                if not threshold_input:

                    print(
                        f"{YELLOW}Unchanged.{RESET}"
                    )
                    continue

                threshold = int(
                    threshold_input
                )

                if threshold <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_auto_stop_consecutive_failures(
                    threshold
                ):

                    print(
                        f"{GREEN}✓ Auto-stop set to "
                        f"{threshold} consecutive failures.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "2":

            if set_auto_stop_consecutive_failures(
                None
            ):

                print(
                    f"{GREEN}✓ Auto-stop disabled.{RESET}"
                )

            else:

                print(
                    f"{RED}✗ Could not disable.{RESET}"
                )

        elif choice == "3":

            _pause(
                "Press Enter to return to settings..."
            )

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# SYSTEM SETTINGS
# ============================================================

def _system_settings():

    while True:

        current_level = get_log_level()
        time_limit = get_session_time_limit()

        time_limit_str = (
            f"{time_limit} minutes"
            if time_limit
            else "DISABLED"
        )

        _title(
            "SYSTEM SETTINGS",
            "Application and session behavior",
        )

        _setting(
            "Log level",
            current_level,
        )

        _setting(
            "Session time limit",
            time_limit_str,
        )

        _setting(
            "Auto-logout",
            (
                "YES"
                if get_auto_logout_after_session()
                else "NO"
            ),
        )

        _setting(
            "Notify on shiny",
            (
                "YES"
                if get_notify_on_shiny_encounter()
                else "NO"
            ),
        )

        _blank_row()

        _option(
            "1",
            "Set log level",
        )

        _option(
            "2",
            "Set session time limit",
        )

        _option(
            "3",
            "Toggle auto-logout",
        )

        _option(
            "4",
            "Toggle shiny notifications",
        )

        _option(
            "5",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            _title(
                "LOG LEVEL",
                "Choose how much output the bot displays",
            )

            _option(
                "1",
                "verbose",
                "all output",
            )

            _option(
                "2",
                "normal",
                "important only",
            )

            _option(
                "3",
                "minimal",
                "errors and milestones only",
            )

            _option(
                "4",
                "Back",
            )

            _close_box()

            level_choice = input(
                f"\n{KEY_COLOR}Choose:{RESET} "
            ).strip()

            if level_choice == "1":

                set_log_level(
                    "verbose"
                )

                print(
                    f"{GREEN}✓ Log level "
                    f"set to verbose.{RESET}"
                )

            elif level_choice == "2":

                set_log_level(
                    "normal"
                )

                print(
                    f"{GREEN}✓ Log level "
                    f"set to normal.{RESET}"
                )

            elif level_choice == "3":

                set_log_level(
                    "minimal"
                )

                print(
                    f"{GREEN}✓ Log level "
                    f"set to minimal.{RESET}"
                )

            elif level_choice == "4":

                continue

            else:

                print(
                    f"{RED}✗ Invalid choice.{RESET}"
                )

        elif choice == "2":

            try:

                limit_input = input(
                    f"\nSession time limit (minutes)? "
                    f"(currently {time_limit_str}, "
                    f"or 0 to disable): "
                ).strip()

                if (
                    limit_input == ""
                    or limit_input == "0"
                ):

                    if set_session_time_limit(
                        None
                    ):

                        print(
                            f"{GREEN}✓ Session time "
                            f"limit disabled.{RESET}"
                        )

                    else:

                        print(
                            f"{RED}✗ Invalid value.{RESET}"
                        )

                    continue

                limit = int(
                    limit_input
                )

                if limit <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_session_time_limit(
                    limit
                ):

                    print(
                        f"{GREEN}✓ Session time limit "
                        f"set to {limit} minutes.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "3":

            current = (
                get_auto_logout_after_session()
            )

            new_state = not current

            set_auto_logout_after_session(
                new_state
            )

            status = (
                "YES (logout after session)"
                if new_state
                else "NO (stay logged in)"
            )

            print(
                f"{GREEN}✓ Auto-logout: "
                f"{status}{RESET}"
            )

        elif choice == "4":

            current = (
                get_notify_on_shiny_encounter()
            )

            new_state = not current

            set_notify_on_shiny_encounter(
                new_state
            )

            status = (
                "YES (notify me)"
                if new_state
                else "NO (silent)"
            )

            print(
                f"{GREEN}✓ Shiny notifications: "
                f"{status}{RESET}"
            )

        elif choice == "5":

            _pause(
                "Press Enter to return to settings..."
            )

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# ADVANCED TIMING SETTINGS
# ============================================================

def _advanced_timing_settings():

    while True:

        _title(
            "ADVANCED SETTINGS — TIMING",
            "Fine-tune search and capture timing",
        )

        _setting(
            "Search encounter timeout",
            f"{get_search_encounter_timeout()} seconds",
        )

        _setting(
            "Ball selection delay",
            f"{get_ball_selection_delay()} ms",
        )

        _setting(
            "Encounter detection retry",
            f"{get_encounter_detection_retry_delay()} ms",
        )

        _blank_row()

        _option(
            "1",
            "Set search encounter timeout",
        )

        _option(
            "2",
            "Set ball selection delay",
        )

        _option(
            "3",
            "Set encounter detection retry delay",
        )

        _option(
            "4",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            try:

                seconds = int(
                    input(
                        f"\nSearch encounter timeout "
                        f"(seconds)? "
                        f"(currently "
                        f"{get_search_encounter_timeout()}): "
                    ).strip()
                )

                if seconds <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_search_encounter_timeout(
                    seconds
                ):

                    print(
                        f"{GREEN}✓ Timeout set to "
                        f"{seconds} seconds.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "2":

            try:

                ms = int(
                    input(
                        f"\nBall selection delay "
                        f"(milliseconds)? "
                        f"(currently "
                        f"{get_ball_selection_delay()}): "
                    ).strip()
                )

                if ms <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_ball_selection_delay(
                    ms
                ):

                    print(
                        f"{GREEN}✓ Ball selection delay "
                        f"set to {ms} ms.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "3":

            try:

                ms = int(
                    input(
                        f"\nEncounter detection retry "
                        f"delay (milliseconds)? "
                        f"(currently "
                        f"{get_encounter_detection_retry_delay()}): "
                    ).strip()
                )

                if ms <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_encounter_detection_retry_delay(
                    ms
                ):

                    print(
                        f"{GREEN}✓ Retry delay set to "
                        f"{ms} ms.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "4":

            _pause(
                "Press Enter to return to settings..."
            )

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# MINING SETTINGS
# ============================================================

def _mining_settings():

    while True:

        _title(
            "MINING SETTINGS",
            "Mining encounters and area behavior",
        )

        _setting(
            "Poll interval",
            f"{get_mine_result_poll_interval()} ms",
        )

        _setting(
            "Auto-catch encounters",
            (
                "YES"
                if get_mining_encounter_auto_catch()
                else "NO"
            ),
        )

        _setting(
            "Auto-stop on area cleared",
            (
                "YES"
                if get_auto_stop_mining_on_area_cleared()
                else "NO"
            ),
        )

        _blank_row()

        _option(
            "1",
            "Set poll interval",
        )

        _option(
            "2",
            "Toggle auto-catch encounters",
        )

        _option(
            "3",
            "Toggle auto-stop on area cleared",
        )

        _option(
            "4",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            try:

                ms = int(
                    input(
                        f"\nPoll interval "
                        f"(milliseconds)? "
                        f"(currently "
                        f"{get_mine_result_poll_interval()}): "
                    ).strip()
                )

                if ms <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_mine_result_poll_interval(
                    ms
                ):

                    print(
                        f"{GREEN}✓ Poll interval set to "
                        f"{ms} ms.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "2":

            current = (
                get_mining_encounter_auto_catch()
            )

            new_state = not current

            set_mining_encounter_auto_catch(
                new_state
            )

            status = (
                "YES (catch them)"
                if new_state
                else "NO (ignore them)"
            )

            print(
                f"{GREEN}✓ Auto-catch encounters: "
                f"{status}{RESET}"
            )

        elif choice == "3":

            current = (
                get_auto_stop_mining_on_area_cleared()
            )

            new_state = not current

            set_auto_stop_mining_on_area_cleared(
                new_state
            )

            status = (
                "YES (stop)"
                if new_state
                else "NO (continue)"
            )

            print(
                f"{GREEN}✓ Auto-stop on area cleared: "
                f"{status}{RESET}"
            )

        elif choice == "4":

            _pause(
                "Press Enter to return to settings..."
            )

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# ADVANCED NETWORK SETTINGS
# ============================================================

def _advanced_network_settings():

    while True:

        _title(
            "ADVANCED SETTINGS — NETWORK",
            "Browser and connection behavior",
        )

        _setting(
            "Browser timeout",
            f"{get_browser_timeout()} seconds",
        )

        _setting(
            "Max connection retries",
            str(
                get_max_connection_retries()
            ),
        )

        _setting(
            "Slow network mode",
            (
                "ON (delays × 1.5)"
                if get_slow_network_mode()
                else "OFF (normal delays)"
            ),
        )

        _blank_row()

        _option(
            "1",
            "Set browser timeout",
        )

        _option(
            "2",
            "Set max connection retries",
        )

        _option(
            "3",
            "Toggle slow network mode",
        )

        _option(
            "4",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            try:

                seconds = int(
                    input(
                        f"\nBrowser timeout "
                        f"(seconds)? "
                        f"(currently "
                        f"{get_browser_timeout()}): "
                    ).strip()
                )

                if seconds <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_browser_timeout(
                    seconds
                ):

                    print(
                        f"{GREEN}✓ Timeout set to "
                        f"{seconds} seconds.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "2":

            try:

                retries = int(
                    input(
                        f"\nMax connection retries? "
                        f"(currently "
                        f"{get_max_connection_retries()}): "
                    ).strip()
                )

                if retries <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                if set_max_connection_retries(
                    retries
                ):

                    print(
                        f"{GREEN}✓ Max retries set to "
                        f"{retries}.{RESET}"
                    )

                else:

                    print(
                        f"{RED}✗ Invalid value.{RESET}"
                    )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "3":

            current = (
                get_slow_network_mode()
            )

            new_state = not current

            set_slow_network_mode(
                new_state
            )

            status = (
                "ON (all delays × 1.5)"
                if new_state
                else "OFF (normal delays)"
            )

            print(
                f"{GREEN}✓ Slow network mode: "
                f"{status}{RESET}"
            )

        elif choice == "4":

            _pause(
                "Press Enter to return to settings..."
            )

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# BREAK TIMER SETTINGS
# ============================================================

def _break_settings():

    current = get_break_settings()

    while True:

        _title(
            "BREAK TIMER SETTINGS",
            "Automatic rest periods",
        )

        _setting(
            "Break timer",
            (
                "ENABLED"
                if current["enabled"]
                else "DISABLED"
            ),
        )

        _setting(
            "Break after",
            f"{current['break_interval_minutes']} minutes",
        )

        _setting(
            "Break duration",
            f"{current['break_duration_minutes']} minutes",
        )

        _blank_row()

        _option(
            "1",
            "Toggle break timer on/off",
        )

        _option(
            "2",
            "Set break interval",
            "minutes",
        )

        _option(
            "3",
            "Set break duration",
            "minutes",
        )

        _option(
            "4",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            new_state = not current["enabled"]

            set_break_enabled(
                new_state
            )

            current["enabled"] = new_state

            status = (
                "enabled"
                if new_state
                else "disabled"
            )

            print(
                f"{GREEN}✓ Break timer "
                f"{status}.{RESET}"
            )

        elif choice == "2":

            try:

                minutes = int(
                    input(
                        f"\nBreak after how many minutes? "
                        f"(currently "
                        f"{current['break_interval_minutes']}): "
                    ).strip()
                )

                if minutes <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                set_break_interval(
                    minutes
                )

                current[
                    "break_interval_minutes"
                ] = minutes

                print(
                    f"{GREEN}✓ Break interval set "
                    f"to {minutes} minutes.{RESET}"
                )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "3":

            try:

                minutes = int(
                    input(
                        f"\nBreak duration in minutes? "
                        f"(currently "
                        f"{current['break_duration_minutes']}): "
                    ).strip()
                )

                if minutes <= 0:

                    print(
                        f"{RED}✗ Must be a positive number.{RESET}"
                    )
                    continue

                set_break_duration(
                    minutes
                )

                current[
                    "break_duration_minutes"
                ] = minutes

                print(
                    f"{GREEN}✓ Break duration set "
                    f"to {minutes} minutes.{RESET}"
                )

            except ValueError:

                print(
                    f"{RED}✗ Invalid number.{RESET}"
                )

        elif choice == "4":

            _pause(
                "Press Enter to return to settings..."
            )

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# SAVE SETTINGS
# ============================================================

def _save_settings():

    current = (
        settings.gather_current_settings()
    )

    if settings.save_settings(
        current
    ):

        _title(
            "SAVE SETTINGS",
            "Persist configuration to disk",
        )

        _success(
            "Settings saved."
        )

        _info(
            "They will load automatically next run."
        )

        _close_box()

    else:

        _title(
            "SAVE SETTINGS",
            "Persist configuration to disk",
        )

        _error(
            "Could not save settings to disk."
        )

        _close_box()

    _pause(
        "Press Enter to return to settings..."
    )


# ============================================================
# RESET SETTINGS
# ============================================================

def _reset_settings():

    _title(
        "RESET SETTINGS",
        "Restore all settings to their defaults",
    )

    _warning(
        "This will replace your current settings."
    )

    _blank_row()

    _option(
        "Y",
        "Reset all settings",
    )

    _option(
        "N",
        "Cancel",
    )

    _close_box()

    confirm = input(
        f"\n{KEY_COLOR}Reset all settings to defaults? "
        f"[y/N]:{RESET} "
    ).strip().lower()

    if confirm != "y":

        _title(
            "RESET SETTINGS",
            "Operation cancelled",
        )

        _info(
            "No settings were changed."
        )

        _close_box()

        _pause(
            "Press Enter to return to settings..."
        )

        return

    settings.apply_settings(
        settings.DEFAULT_SETTINGS
    )

    settings.save_settings(
        settings.DEFAULT_SETTINGS
    )

    _title(
        "RESET SETTINGS",
        "Restore all settings to their defaults",
    )

    _success(
        "Settings reset to defaults."
    )

    _close_box()

    _pause(
        "Press Enter to return to settings..."
    )


# ============================================================
# BROWSER SETTINGS
# ============================================================

def _browser_settings(driver=None):

    while True:

        current_name = get_browser_name()
        fallback = get_browser_allow_fallback()
        installed = detect_installed_browsers()

        detected = (
            ", ".join(
                BROWSER_LABELS[name]
                for name in ("brave", "chrome", "chromium")
                if name in installed
            )
            or "none"
        )

        _title(
            "BROWSER SETTINGS",
            "Configure browser automation",
        )

        _setting(
            "Browser",
            BROWSER_LABELS.get(
                current_name,
                current_name,
            ),
        )

        _setting(
            "Fallback",
            "Enabled" if fallback else "Disabled",
        )

        _setting(
            "Detected",
            detected,
        )

        _blank_row()

        _option(
            "1",
            "Select Browser",
        )

        _option(
            "2",
            "Toggle Browser Fallback",
        )

        _option(
            "3",
            "Test Browser",
        )

        _option(
            "4",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            _title(
                "SELECT BROWSER",
                "Windows launch browser",
            )

            _option(
                "1",
                "Brave",
            )

            _option(
                "2",
                "Chrome",
            )

            _option(
                "3",
                "Chromium",
            )

            _option(
                "4",
                "Auto Detect",
            )

            _option(
                "5",
                "Back",
            )

            _close_box()

            browser_choice = input(
                f"\n{KEY_COLOR}Choose:{RESET} "
            ).strip()

            mapping = {
                "1": "brave",
                "2": "chrome",
                "3": "chromium",
                "4": "auto",
            }

            if browser_choice in mapping:

                selected = mapping[browser_choice]
                set_browser_name(selected)
                print(
                    f"{GREEN}✓ Browser set to "
                    f"{BROWSER_LABELS[selected]}.{RESET}"
                )

            elif browser_choice == "5":

                continue

            else:

                print(
                    f"{RED}✗ Invalid choice.{RESET}"
                )

        elif choice == "2":

            new_state = not get_browser_allow_fallback()
            set_browser_allow_fallback(new_state)
            status = (
                "Enabled"
                if new_state
                else "Disabled"
            )
            print(
                f"{GREEN}✓ Browser fallback: "
                f"{status}.{RESET}"
            )

        elif choice == "3":

            from browser import BrowserManager

            BrowserManager.test(
                driver
            )
            _pause(
                "Press Enter to return to browser settings..."
            )

        elif choice == "4":

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# ADVANCED SUBMENU
# ============================================================

def _advanced_submenu(driver=None):
    """
    Submenu for Advanced Settings with Timing
    and Network options.
    """

    while True:

        _title(
            "ADVANCED SETTINGS",
            "Timing and network configuration",
        )

        _option(
            "1",
            "Timing Settings",
            "search and capture timing",
        )

        _option(
            "2",
            "Network Settings",
            "browser and connection behavior",
        )

        _option(
            "3",
            "Browser Settings",
            "Brave, Chrome, Chromium, Auto Detect",
        )

        _option(
            "4",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

        if choice == "1":

            _advanced_timing_settings()

        elif choice == "2":

            _advanced_network_settings()

        elif choice == "3":

            _browser_settings(driver)

        elif choice == "4":

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )


# ============================================================
# MAIN SETTINGS MENU
# ============================================================

def settings_menu(driver):

    while True:

        _title(
            "SETTINGS",
            "Eclipse RPG Automation configuration",
        )

        _section(
            "CORE SETTINGS"
        )

        _option(
            "1",
            "Search Settings",
        )

        _option(
            "2",
            "Training Settings",
        )

        _option(
            "3",
            "Capture Settings",
        )

        _option(
            "4",
            "Safety Settings",
        )

        _option(
            "5",
            "System Settings",
        )

        _option(
            "6",
            "Mining Settings",
        )

        _blank_row()

        _section(
            "ADVANCED"
        )

        _option(
            "7",
            "Advanced Settings",
        )

        _option(
            "8",
            "Break Timer Settings",
        )

        _blank_row()

        _section(
            "PERSISTENCE"
        )

        _option(
            "9",
            "Save Settings",
            "save current configuration",
        )

        _option(
            "10",
            "Reset Settings",
            "restore defaults",
        )

        _option(
            "11",
            "Back",
        )

        _close_box()

        choice = input(
            f"\n{KEY_COLOR}Choose:{RESET} "
        ).strip()

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

            _advanced_submenu(driver)

        elif choice == "8":

            _break_settings()

        elif choice == "9":

            _save_settings()

        elif choice == "10":

            _reset_settings()

        elif choice == "11":

            return

        else:

            print(
                f"{RED}✗ Invalid choice.{RESET}"
            )