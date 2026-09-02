"""
RPGBot Login Module

Handles logging into Eclipse RPG and detecting whether
the current Selenium session is already authenticated.
"""

import os
import platform
import re
import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import BASE_URL, LOGIN_URL, WAIT_LONG
from helpers import (
    normalize,
    page_contains,
    safe_click,
    wait_for_document_ready,
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

            # ENABLE_VIRTUAL_TERMINAL_PROCESSING
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
# Same palette as the main menu / Update Center
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

def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences for length calculations."""

    return ANSI_STRIP_REGEX.sub("", text)


def _row(
    content: str,
    width: int = 71,
) -> str:
    """
    Create a properly padded box row.

    ANSI color codes are ignored when calculating
    visible text width.
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


def _top_border(
    width: int = 71,
) -> str:
    """Return the top border."""

    return (
        f"{BORDER_COLOR}╔"
        f"{'═' * width}"
        f"╗{RESET}"
    )


def _middle_border(
    width: int = 71,
) -> str:
    """Return the middle border."""

    return (
        f"{BORDER_COLOR}╠"
        f"{'═' * width}"
        f"╣{RESET}"
    )


def _bottom_border(
    width: int = 71,
) -> str:
    """Return the bottom border."""

    return (
        f"{BORDER_COLOR}╚"
        f"{'═' * width}"
        f"╝{RESET}"
    )


def _print_title(
    title: str,
    subtitle: str = "",
    width: int = 71,
    close_box: bool = True,
):
    """
    Print a centered title.

    close_box=False leaves the box open so additional
    content can be printed inside it.
    """

    print()
    print(_top_border(width))

    visible_title_length = len(title)

    left_padding = max(
        0,
        (width - visible_title_length) // 2,
    )

    right_padding = max(
        0,
        width
        - visible_title_length
        - left_padding,
    )

    print(
        f"{BORDER_COLOR}║{RESET}"
        f"{' ' * left_padding}"
        f"{BOLD}{MAGENTA}{title}{RESET}"
        f"{' ' * right_padding}"
        f"{BORDER_COLOR}║{RESET}"
    )

    if subtitle:
        visible_subtitle_length = len(
            subtitle
        )

        left_padding = max(
            0,
            (width - visible_subtitle_length) // 2,
        )

        right_padding = max(
            0,
            width
            - visible_subtitle_length
            - left_padding,
        )

        print(
            f"{BORDER_COLOR}║{RESET}"
            f"{' ' * left_padding}"
            f"{DIM}{CYAN}{subtitle}{RESET}"
            f"{' ' * right_padding}"
            f"{BORDER_COLOR}║{RESET}"
        )

    if close_box:
        print(_bottom_border(width))


def _print_status(
    symbol: str,
    message: str,
    color: str = GREEN,
):
    """
    Print a status message inside the login box.
    """

    content = (
        f"{color}{BOLD}"
        f"{symbol} {message}"
        f"{RESET}"
    )

    print(
        _row(
            f" {content}"
        )
    )


def _print_info(
    message: str,
):
    """Print an informational message inside the box."""

    print(
        _row(
            f" {CYAN}{message}{RESET}"
        )
    )


def _close_login_box():
    """Close the login display box."""

    print(_bottom_border())


# ============================================================
# LOGIN DETECTION
# ============================================================

def is_logged_in(driver):
    """
    Determine whether the current Selenium session is logged in.

    Checks visible party-Pokémon elements first, then falls back
    to common logged-in page text.

    Args:
        driver: Selenium WebDriver instance.

    Returns:
        True if the session appears authenticated.
        False otherwise.
    """

    selectors = [
        ".party-pokemon-header",
        ".party-pokemon-name",
        ".party-pokemon-level",
    ]

    for selector in selectors:
        try:
            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selector,
            )

            if any(
                element.is_displayed()
                for element in elements
            ):
                return True

        except Exception:
            pass

    return (
        page_contains(
            driver,
            "Your Profile",
        )
        or page_contains(
            driver,
            "Log Out",
        )
    )


# ============================================================
# LOGIN
# ============================================================

def login(
    driver,
    username,
    password,
):
    """
    Log into Eclipse RPG.

    Args:
        driver: Selenium WebDriver instance.
        username: Eclipse RPG username.
        password: Eclipse RPG password.

    Returns:
        True if already logged in or login succeeds.
        False if login fails or cannot be confirmed.
    """

    # ========================================================
    # OPEN LOGIN BOX
    # ========================================================

    _print_title(
        "LOGIN",
        "Eclipse RPG authentication",
        close_box=False,
    )

    print(_middle_border())

    # ========================================================
    # OPEN MAIN SITE
    # ========================================================

    _print_info(
        "Connecting to Eclipse RPG..."
    )

    try:
        driver.get(BASE_URL)

        wait_for_document_ready(driver)

        time.sleep(1)

    except Exception as e:
        _print_status(
            "✗",
            f"Could not open Eclipse RPG: {e}",
            RED,
        )

        _close_login_box()

        return False

    # ========================================================
    # CHECK EXISTING SESSION
    # ========================================================

    if is_logged_in(driver):

        _print_status(
            "✓",
            "Already logged in.",
            GREEN,
        )

        _close_login_box()

        return True

    # ========================================================
    # OPEN LOGIN PAGE
    # ========================================================

    _print_info(
        "Opening login page..."
    )

    try:
        link = WebDriverWait(
            driver,
            WAIT_LONG,
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[normalize-space()='Log In']",
                )
            )
        )

        safe_click(
            driver,
            link,
        )

    except TimeoutException:

        try:
            driver.get(LOGIN_URL)

        except Exception as e:

            _print_status(
                "✗",
                f"Could not open login page: {e}",
                RED,
            )

            _close_login_box()

            return False

    except Exception as e:

        _print_status(
            "✗",
            f"Could not open login page: {e}",
            RED,
        )

        _close_login_box()

        return False

    # ========================================================
    # WAIT FOR LOGIN PAGE
    # ========================================================

    try:
        wait_for_document_ready(driver)

    except Exception:
        pass

    # ========================================================
    # LOGIN FORM
    # ========================================================

    _print_info(
        "Loading login form..."
    )

    try:
        user = WebDriverWait(
            driver,
            WAIT_LONG,
        ).until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "L_UserID",
                )
            )
        )

        pwd = WebDriverWait(
            driver,
            WAIT_LONG,
        ).until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "L_Password",
                )
            )
        )

    except TimeoutException:

        _print_status(
            "✗",
            "Login form not found.",
            RED,
        )

        _close_login_box()

        return False

    except Exception as e:

        _print_status(
            "✗",
            f"Error locating login form: {e}",
            RED,
        )

        _close_login_box()

        return False

    # ========================================================
    # ENTER CREDENTIALS
    # ========================================================

    try:
        user.clear()
        user.send_keys(username)

        pwd.clear()
        pwd.send_keys(password)

    except Exception as e:

        _print_status(
            "✗",
            f"Could not enter login credentials: {e}",
            RED,
        )

        _close_login_box()

        return False

    # ========================================================
    # LOGIN BUTTON
    # ========================================================

    _print_info(
        "Submitting login..."
    )

    try:
        button = WebDriverWait(
            driver,
            WAIT_LONG,
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[normalize-space()='Login']",
                )
            )
        )

        safe_click(
            driver,
            button,
        )

    except TimeoutException:

        _print_status(
            "✗",
            "Login button not found.",
            RED,
        )

        _close_login_box()

        return False

    except Exception as e:

        _print_status(
            "✗",
            f"Could not click login button: {e}",
            RED,
        )

        _close_login_box()

        return False

    # ========================================================
    # CONFIRM LOGIN
    # ========================================================

    _print_info(
        "Confirming login..."
    )

    try:
        WebDriverWait(
            driver,
            WAIT_LONG,
        ).until(
            is_logged_in
        )

    except TimeoutException:

        _print_status(
            "✗",
            "Login could not be confirmed.",
            RED,
        )

        _close_login_box()

        return False

    except Exception as e:

        _print_status(
            "✗",
            f"Error confirming login: {e}",
            RED,
        )

        _close_login_box()

        return False

    # ========================================================
    # SUCCESS
    # ========================================================

    print(_middle_border())

    _print_status(
        "✓",
        "LOGIN SUCCESSFUL",
        GREEN,
    )

    _close_login_box()

    return True