"""
RPGBot Update Center

In-game menu for checking and performing Git-based updates.

Features:
1. Check for updates from GitHub
2. View recent commits
3. Configure auto-update settings
4. Perform safe updates
5. View update history

Status: UNFINISHED - In development
"""

import os
import platform
import re
import subprocess
import sys
import json


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
                errors="replace"
            )
        except Exception:
            pass

    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(
                encoding="utf-8",
                errors="replace"
            )
        except Exception:
            pass

    if platform.system() == "Windows":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32

            # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            mode = ctypes.c_ulong()
            h_out = kernel32.GetStdHandle(-11)

            if kernel32.GetConsoleMode(
                h_out,
                ctypes.byref(mode)
            ):
                kernel32.SetConsoleMode(
                    h_out,
                    mode.value | 0x0004
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
# Matches the main menu
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
# AUTO-UPDATE SETTINGS
# ============================================================

try:
    from auto_update_settings_unfinished import AutoUpdateSettings
except ImportError:
    AutoUpdateSettings = None


# ============================================================
# DISPLAY HELPERS
# ============================================================

def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences for length calculations."""
    return ANSI_STRIP_REGEX.sub("", text)


def _row(content: str, width: int = 71) -> str:
    """
    Create a box row with ANSI-aware padding.
    """
    visible_length = len(_strip_ansi(content))
    padding = max(0, width - visible_length)

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


def _middle_border(width: int = 71) -> str:
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


def _print_title(
    title: str,
    subtitle: str = "",
    width: int = 71
):
    """Print a themed Update Center title."""

    print()

    print(_top_border(width))

    title_text = (
        f"{BOLD}{MAGENTA}{title}{RESET}"
    )

    visible_length = len(title)
    left = max(0, (width - visible_length) // 2)
    right = max(
        0,
        width - visible_length - left
    )

    print(
        f"{BORDER_COLOR}║{RESET}"
        f"{' ' * left}"
        f"{title_text}"
        f"{' ' * right}"
        f"{BORDER_COLOR}║{RESET}"
    )

    if subtitle:
        subtitle_text = (
            f"{DIM}{CYAN}{subtitle}{RESET}"
        )

        visible_length = len(subtitle)
        left = max(
            0,
            (width - visible_length) // 2
        )
        right = max(
            0,
            width - visible_length - left
        )

        print(
            f"{BORDER_COLOR}║{RESET}"
            f"{' ' * left}"
            f"{subtitle_text}"
            f"{' ' * right}"
            f"{BORDER_COLOR}║{RESET}"
        )

    print(_bottom_border(width))


def _print_section(title: str):
    """Print a section heading."""

    print()
    print(
        f"{CATEGORY_COLOR}"
        f"── {title} "
        f"{CYAN}{'─' * max(0, 50 - len(title))}"
        f"{RESET}"
    )


def _print_menu_option(
    number: str,
    name: str,
    description: str = ""
):
    """Print a menu option using the main menu palette."""

    content = (
        f"{KEY_COLOR}[{number}]{RESET} "
        f"{NAME_COLOR}{name}{RESET}"
    )

    if description:
        content += (
            f" {DESC_COLOR}- {description}{RESET}"
        )

    print(
        _row(
            f" {content}"
        )
    )


def _pause():
    """Pause before returning to the previous menu."""
    input(
        f"\n{DIM}{GRAY}"
        f"Press Enter to continue..."
        f"{RESET}"
    )


def _run_python_script(
    arguments,
    timeout=30
):
    """
    Run update.py using the same Python interpreter
    that is running the bot.
    """

    command = [
        sys.executable,
        "update.py",
        *arguments
    ]

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout
    )


# ============================================================
# MAIN UPDATE MENU
# ============================================================

def update_menu(driver):
    """
    Main Update Center menu.

    Args:
        driver: Selenium WebDriver instance.

    Returns:
        None
    """

    while True:
        current_version = get_current_version()

        print()

        # ========================================================
        # UPDATE CENTER HEADER
        # ========================================================

        print(_top_border())

        title = (
            f"{BOLD}{MAGENTA}"
            f"UPDATE CENTER"
            f"{RESET}"
        )

        title_padding = max(
            0,
            (71 - len("UPDATE CENTER")) // 2
        )

        title_right = max(
            0,
            71 - len("UPDATE CENTER") - title_padding
        )

        print(
            f"{BORDER_COLOR}║{RESET}"
            f"{' ' * title_padding}"
            f"{title}"
            f"{' ' * title_right}"
            f"{BORDER_COLOR}║{RESET}"
        )

        print(_middle_border())

        # ========================================================
        # CURRENT VERSION
        # ========================================================

        version_text = (
            f"{CATEGORY_COLOR}"
            f"Current Version:"
            f"{RESET} "
            f"{NAME_COLOR}"
            f"{current_version}"
            f"{RESET}"
        )

        print(_row(version_text))

        print(_middle_border())

        # ========================================================
        # MENU OPTIONS
        # ========================================================

        print(_row(""))

        _print_menu_option(
            "1",
            "Check for Updates",
            "Check GitHub for a newer version"
        )

        _print_menu_option(
            "2",
            "View Changelog",
            "View recent local commits"
        )

        _print_menu_option(
            "3",
            "Auto-Update Settings",
            "Configure automatic update behavior"
        )

        _print_menu_option(
            "4",
            "Update Now",
            "Safely update from GitHub"
        )

        _print_menu_option(
            "5",
            "View Update History",
            "View previous update attempts"
        )

        _print_menu_option(
            "6",
            "Back to Main Menu",
            "Return to the main menu"
        )

        print(_row(""))

        print(_bottom_border())

        # ========================================================
        # INPUT
        # ========================================================

        print()

        choice = input(
            f"{KEY_COLOR}"
            f"Choose option:"
            f"{RESET} "
        ).strip()

        if choice == "1":
            check_for_updates_menu()

        elif choice == "2":
            view_changelog_menu()

        elif choice == "3":
            configure_auto_update_menu()

        elif choice == "4":
            update_now_menu()

        elif choice == "5":
            view_update_history_menu()

        elif choice == "6":
            return

        else:
            print(
                f"\n{RED}"
                f"❌ Invalid choice."
                f"{RESET}"
            )


# ============================================================
# CHECK FOR UPDATES
# ============================================================

def check_for_updates_menu():
    """Check GitHub for updates."""

    _print_title(
        "CHECKING FOR UPDATES",
        "Checking GitHub safely"
    )

    print(
        f"\n{CYAN}📡 Fetching latest version "
        f"from GitHub...{RESET}"
    )

    try:
        result = _run_python_script(
            ["--check"],
            timeout=30
        )

        output = (
            (result.stdout or "") +
            "\n" +
            (result.stderr or "")
        )

        output_lower = output.lower()

        print()

        if result.returncode == 0:

            # Local version is authoritative when histories
            # are unrelated or the local repository is newer.
            if any(
                phrase in output_lower
                for phrase in [
                    "already up to date",
                    "local is newer",
                    "local version is newer",
                    "local version is authoritative",
                    "unrelated",
                    "no update",
                    "same version",
                    "already current",
                ]
            ):
                print(
                    f"{GREEN}{BOLD}"
                    f"✓ No update required"
                    f"{RESET}"
                )

                current = get_current_version()

                print(
                    f"\n{DESC_COLOR}"
                    f"Your local version is:"
                    f"{RESET} "
                    f"{NAME_COLOR}{current}"
                    f"{RESET}"
                )

                _show_safe_update_message(output)

            elif any(
                phrase in output_lower
                for phrase in [
                    "update available",
                    "github is newer",
                    "github version is newer",
                    "newer version available",
                ]
            ):
                print(
                    f"{GREEN}{BOLD}"
                    f"✓ Update available"
                    f"{RESET}"
                )

                show_update_details()

            else:
                print(
                    f"{GREEN}{BOLD}"
                    f"✓ Check complete"
                    f"{RESET}"
                )

                _show_safe_update_message(output)

        elif result.returncode == 1:

            # update.py may use return code 1 to explicitly
            # indicate that GitHub is newer.
            if any(
                phrase in output_lower
                for phrase in [
                    "update available",
                    "github is newer",
                    "github version is newer",
                    "newer version available",
                ]
            ):
                print(
                    f"{GREEN}{BOLD}"
                    f"✓ Update available"
                    f"{RESET}"
                )

                show_update_details()

            else:
                print(
                    f"{YELLOW}{BOLD}"
                    f"⚠ Update check returned a protected state"
                    f"{RESET}"
                )

                _show_safe_update_message(output)

        else:
            print(
                f"{RED}{BOLD}"
                f"❌ Update check failed"
                f"{RESET}"
            )

            _print_process_error(result)

    except subprocess.TimeoutExpired:
        print(
            f"\n{RED}"
            f"⏱️ Update check timed out."
            f"{RESET}"
        )

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error checking for updates:"
            f"{RESET} {e}"
        )

    _pause()


def _show_safe_update_message(output: str):
    """
    Display useful status information without dumping
    the entire updater output.
    """

    lines = [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]

    interesting = []

    for line in lines:
        lower = line.lower()

        if any(
            phrase in lower
            for phrase in [
                "[ok]",
                "[info]",
                "[warning]",
                "[error]",
                "local",
                "github",
                "history",
                "protected",
                "unrelated",
                "diverged",
                "up to date",
            ]
        ):
            interesting.append(line)

    if interesting:
        print(
            f"\n{DIM}{GRAY}"
            f"Updater status:"
            f"{RESET}"
        )

        for line in interesting[-6:]:
            print(
                f"  {DESC_COLOR}"
                f"{line}"
                f"{RESET}"
            )


def _print_process_error(result):
    """Display a shortened subprocess error."""

    error = (
        result.stderr.strip()
        if result.stderr
        else result.stdout.strip()
    )

    if error:
        lines = error.splitlines()

        for line in lines[-5:]:
            print(
                f"  {RED}{line[:300]}{RESET}"
            )


# ============================================================
# CHANGELOG
# ============================================================

def view_changelog_menu():
    """View recent local commits."""

    _print_title(
        "CHANGELOG",
        "Recent local Git commits"
    )

    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--oneline",
                "-10"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10
        )

        if result.returncode != 0:
            print(
                f"\n{RED}"
                f"❌ Could not fetch changelog."
                f"{RESET}"
            )

            _print_process_error(result)
            _pause()
            return

        lines = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        if not lines:
            print(
                f"\n{YELLOW}"
                f"📝 No commits found."
                f"{RESET}"
            )

            _pause()
            return

        _print_section("RECENT COMMITS")

        for index, line in enumerate(lines, 1):
            parts = line.split(" ", 1)

            if len(parts) == 2:
                sha, message = parts
            else:
                sha = line
                message = ""

            content = (
                f"{DIM}{GRAY}{index:>2}.{RESET} "
                f"{CYAN}{sha}{RESET} "
                f"{NAME_COLOR}{message}{RESET}"
            )

            print(_row(content))

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error reading changelog:"
            f"{RESET} {e}"
        )

    _pause()


# ============================================================
# AUTO UPDATE SETTINGS
# ============================================================

def configure_auto_update_menu():
    """Configure auto-update settings."""

    if AutoUpdateSettings is None:
        _print_title(
            "AUTO-UPDATE SETTINGS",
            "Settings unavailable"
        )

        print(
            f"\n{RED}"
            f"❌ Settings module is not available."
            f"{RESET}"
        )

        _pause()
        return

    try:
        settings = AutoUpdateSettings()
    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Could not load settings:"
            f"{RESET} {e}"
        )

        _pause()
        return

    while True:

        _print_title(
            "AUTO-UPDATE SETTINGS",
            "Configure automatic update behavior"
        )

        try:
            settings.display_current_settings()
        except Exception as e:
            print(
                f"\n{RED}"
                f"❌ Could not display settings:"
                f"{RESET} {e}"
            )

        print()

        _print_menu_option(
            "1",
            "Toggle Auto-Update"
        )

        _print_menu_option(
            "2",
            "Set Check Frequency"
        )

        _print_menu_option(
            "3",
            "Toggle Auto-Restart After Update"
        )

        _print_menu_option(
            "4",
            "Toggle Quiet Mode"
        )

        _print_menu_option(
            "5",
            "Toggle Notifications"
        )

        _print_menu_option(
            "6",
            "Back to Update Menu"
        )

        choice = input(
            f"\n{KEY_COLOR}"
            f"Choose option:{RESET} "
        ).strip()

        if choice == "1":
            _toggle_auto_update(settings)

        elif choice == "2":
            _set_frequency(settings)

        elif choice == "3":
            _toggle_restart(settings)

        elif choice == "4":
            _toggle_quiet_mode(settings)

        elif choice == "5":
            _toggle_notifications(settings)

        elif choice == "6":
            return

        else:
            print(
                f"\n{RED}"
                f"❌ Invalid choice."
                f"{RESET}"
            )

        _pause()


def _toggle_auto_update(settings):
    """Toggle automatic updates."""

    try:
        current = settings.is_auto_update_enabled()
        new_value = not current

        if settings.set_auto_update_enabled(new_value):
            status = (
                f"{GREEN}Enabled{RESET}"
                if new_value
                else f"{RED}Disabled{RESET}"
            )

            print(
                f"\n{GREEN}"
                f"✓ Auto-Update:"
                f"{RESET} {status}"
            )
        else:
            print(
                f"\n{RED}"
                f"❌ Failed to save setting."
                f"{RESET}"
            )

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error:"
            f"{RESET} {e}"
        )


def _set_frequency(settings):
    """Set automatic update frequency."""

    try:
        options = settings.get_frequency_options()

        print(
            f"\n{CATEGORY_COLOR}"
            f"AVAILABLE FREQUENCIES"
            f"{RESET}"
        )

        for i, option in enumerate(options, 1):
            hours, label = option

            print(
                _row(
                    f"{KEY_COLOR}[{i}]{RESET} "
                    f"{NAME_COLOR}{label}{RESET} "
                    f"{DESC_COLOR}({hours}h){RESET}"
                )
            )

        choice = input(
            f"\n{KEY_COLOR}"
            f"Select frequency:{RESET} "
        ).strip()

        try:
            index = int(choice) - 1
        except ValueError:
            print(
                f"\n{RED}"
                f"❌ Please enter a number."
                f"{RESET}"
            )
            return

        if not 0 <= index < len(options):
            print(
                f"\n{RED}"
                f"❌ Invalid choice."
                f"{RESET}"
            )
            return

        hours, label = options[index]

        if settings.set_check_frequency_hours(hours):
            print(
                f"\n{GREEN}"
                f"✓ Frequency set to:"
                f"{RESET} {NAME_COLOR}{label}{RESET}"
            )
        else:
            print(
                f"\n{RED}"
                f"❌ Failed to save setting."
                f"{RESET}"
            )

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error:"
            f"{RESET} {e}"
        )


def _toggle_restart(settings):
    """Toggle automatic restart."""

    try:
        current = settings.should_restart_after_update()
        new_value = not current

        if settings.set_restart_after_update(new_value):
            status = (
                f"{GREEN}Enabled{RESET}"
                if new_value
                else f"{RED}Disabled{RESET}"
            )

            print(
                f"\n{GREEN}"
                f"✓ Auto-Restart:"
                f"{RESET} {status}"
            )
        else:
            print(
                f"\n{RED}"
                f"❌ Failed to save setting."
                f"{RESET}"
            )

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error:"
            f"{RESET} {e}"
        )


def _toggle_quiet_mode(settings):
    """Toggle quiet mode."""

    try:
        current = settings.is_quiet_mode_enabled()
        new_value = not current

        if settings.set_quiet_mode(new_value):
            status = (
                f"{GREEN}Enabled{RESET}"
                if new_value
                else f"{RED}Disabled{RESET}"
            )

            print(
                f"\n{GREEN}"
                f"✓ Quiet Mode:"
                f"{RESET} {status}"
            )
        else:
            print(
                f"\n{RED}"
                f"❌ Failed to save setting."
                f"{RESET}"
            )

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error:"
            f"{RESET} {e}"
        )


def _toggle_notifications(settings):
    """Toggle update notifications."""

    try:
        current = settings.should_notify_on_update()
        new_value = not current

        if settings.set_notify_on_update(new_value):
            status = (
                f"{GREEN}Enabled{RESET}"
                if new_value
                else f"{RED}Disabled{RESET}"
            )

            print(
                f"\n{GREEN}"
                f"✓ Notifications:"
                f"{RESET} {status}"
            )
        else:
            print(
                f"\n{RED}"
                f"❌ Failed to save setting."
                f"{RESET}"
            )

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error:"
            f"{RESET} {e}"
        )


# ============================================================
# UPDATE NOW
# ============================================================

def update_now_menu():
    """Perform a safe update immediately."""

    _print_title(
        "UPDATE NOW",
        "Safe Git-based update"
    )

    print(
        f"\n{YELLOW}{BOLD}"
        f"⚠ UPDATE SAFETY"
        f"{RESET}"
    )

    print(
        _row(
            f"{DESC_COLOR}"
            f"• Your local files will not be force-overwritten."
            f"{RESET}"
        )
    )

    print(
        _row(
            f"{DESC_COLOR}"
            f"• Uncommitted changes will block the update."
            f"{RESET}"
        )
    )

    print(
        _row(
            f"{DESC_COLOR}"
            f"• A newer local version will be preserved."
            f"{RESET}"
        )
    )

    print(
        _row(
            f"{DESC_COLOR}"
            f"• Diverged/unrelated histories will be protected."
            f"{RESET}"
        )
    )

    print()

    response = input(
        f"{KEY_COLOR}"
        f"Continue with update? (yes/no):"
        f"{RESET} "
    ).strip().lower()

    if response not in ("yes", "y"):
        print(
            f"\n{YELLOW}"
            f"⚠ Update cancelled."
            f"{RESET}"
        )
        _pause()
        return

    print(
        f"\n{CYAN}"
        f"📥 Starting safe update..."
        f"{RESET}"
    )

    try:
        result = _run_python_script(
            ["--no-restart"],
            timeout=60
        )

        if result.returncode == 0:
            print(
                f"\n{GREEN}{BOLD}"
                f"✓ Update process completed."
                f"{RESET}"
            )

            if result.stdout:
                _show_update_output(
                    result.stdout
                )

        else:
            print(
                f"\n{RED}{BOLD}"
                f"❌ Update was not performed."
                f"{RESET}"
            )

            if result.stdout:
                _show_update_output(
                    result.stdout
                )

            if result.stderr:
                print(
                    f"\n{RED}"
                    f"Error:"
                    f"{RESET}"
                )

                for line in (
                    result.stderr
                    .strip()
                    .splitlines()[-5:]
                ):
                    print(
                        f"  {RED}{line[:300]}{RESET}"
                    )

    except subprocess.TimeoutExpired:
        print(
            f"\n{RED}"
            f"⏱️ Update timed out."
            f"{RESET}"
        )

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error performing update:"
            f"{RESET} {e}"
        )

    _pause()


def _show_update_output(output: str):
    """Display useful updater output."""

    lines = [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]

    for line in lines[-10:]:

        lower = line.lower()

        if (
            "[ok]" in lower
            or "success" in lower
            or "updated" in lower
            or "up to date" in lower
        ):
            print(
                f"  {GREEN}{line}{RESET}"
            )

        elif (
            "[error]" in lower
            or "failed" in lower
            or "error" in lower
        ):
            print(
                f"  {RED}{line}{RESET}"
            )

        elif (
            "warning" in lower
            or "protected" in lower
            or "blocked" in lower
            or "unrelated" in lower
            or "diverged" in lower
        ):
            print(
                f"  {YELLOW}{line}{RESET}"
            )

        else:
            print(
                f"  {DESC_COLOR}{line}{RESET}"
            )


# ============================================================
# UPDATE HISTORY
# ============================================================

def view_update_history_menu():
    """View update history from .update_log."""

    _print_title(
        "UPDATE HISTORY",
        "Previous update attempts"
    )

    try:
        if not os.path.exists(".update_log"):
            print(
                f"\n{YELLOW}"
                f"📝 No update history available."
                f"{RESET}"
            )

            print(
                f"{DIM}{GRAY}"
                f"The history file will be created after "
                f"the first update attempt."
                f"{RESET}"
            )

            _pause()
            return

        with open(
            ".update_log",
            "r",
            encoding="utf-8"
        ) as file:
            log_data = json.load(file)

        if not isinstance(log_data, list):
            print(
                f"\n{YELLOW}"
                f"📝 Update history is empty."
                f"{RESET}"
            )

            _pause()
            return

        if not log_data:
            print(
                f"\n{YELLOW}"
                f"📝 No updates recorded yet."
                f"{RESET}"
            )

            _pause()
            return

        _print_section("RECENT UPDATE ATTEMPTS")

        for entry in log_data[-10:]:

            if not isinstance(entry, dict):
                continue

            timestamp = entry.get(
                "timestamp",
                "unknown"
            )

            success_value = entry.get(
                "success",
                False
            )

            commit = entry.get(
                "commit",
                "unknown"
            )

            if success_value:
                status = (
                    f"{GREEN}✓ SUCCESS{RESET}"
                )
            else:
                status = (
                    f"{RED}✗ FAILED{RESET}"
                )

            content = (
                f"{status} "
                f"{DIM}{GRAY}{timestamp}{RESET} "
                f"{CYAN}{commit}{RESET}"
            )

            print(_row(content))

    except json.JSONDecodeError:
        print(
            f"\n{RED}"
            f"❌ Update history contains invalid JSON."
            f"{RESET}"
        )

    except Exception as e:
        print(
            f"\n{RED}"
            f"❌ Error reading update history:"
            f"{RESET} {e}"
        )

    _pause()


# ============================================================
# CURRENT VERSION
# ============================================================

def get_current_version():
    """Return the current Git commit SHA."""

    try:
        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5
        )

        if result.returncode == 0:
            sha = result.stdout.strip()

            if sha:
                return sha[:7]

    except Exception:
        pass

    return "unknown"


# ============================================================
# UPDATE DETAILS
# ============================================================

def show_update_details():
    """
    Show update details only when the histories are
    actually comparable.

    This deliberately avoids blindly running:
        git log HEAD..origin/main

    because local and GitHub histories may be unrelated.
    """

    try:
        fetch_result = subprocess.run(
            [
                "git",
                "fetch",
                "origin",
                "main"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )

        if fetch_result.returncode != 0:
            return

        relationship = subprocess.run(
            [
                "git",
                "merge-base",
                "HEAD",
                "origin/main"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10
        )

        if relationship.returncode != 0:
            print(
                f"\n{YELLOW}"
                f"⚠ Local and GitHub histories cannot be "
                f"compared safely."
                f"{RESET}"
            )

            return

        result = subprocess.run(
            [
                "git",
                "log",
                "--oneline",
                "HEAD..origin/main",
                "-5"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10
        )

        if result.returncode != 0:
            return

        lines = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        if not lines:
            return

        _print_section("NEW COMMITS")

        for line in lines:
            print(
                _row(
                    f"{GREEN}•{RESET} "
                    f"{NAME_COLOR}{line}{RESET}"
                )
            )

    except Exception:
        pass


# ============================================================
# TEST ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print(
        f"{MAGENTA}{BOLD}"
        f"RPGBot Update Center"
        f"{RESET}"
    )

    print(
        f"{DIM}{GRAY}"
        f"This module is meant to be imported from "
        f"main_menu.py."
        f"{RESET}"
    )

    print()
    print(
        f"{CYAN}"
        f"Usage:"
        f"{RESET}"
    )

    print(
        "  from menus.update_menu_unfinished "
        "import update_menu"
    )

    print(
        "  update_menu(driver)"
    )