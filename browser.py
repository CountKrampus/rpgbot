from pathlib import Path
import json
import os
import re
import shutil
import sys
import socket
import subprocess
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

from config import WAIT_MEDIUM
from helpers import wait_for_document_ready


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
# CONFIGURATION
# ============================================================

BASE_DIR = Path(
    r"F:\New folder\eclipse"
)

# One persistent Brave profile per Eclipse account.
PROFILE_ROOT = (
    BASE_DIR / "selenium_profiles"
)

PAGE_LOAD_TIMEOUT = 60

# Number of times Brave will be retried during startup.
STARTUP_RETRIES = 3

# Seconds between startup attempts.
RETRY_DELAY = 2


# ============================================================
# BRAVE LOCATIONS
# ============================================================

BRAVE_PATHS = [
    Path(
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    ),
    Path(
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
    ),
]

CHROME_PATHS = [
    Path(
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ),
    Path(
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ),
    Path(
        os.environ.get("LOCALAPPDATA", "")
    )
    / "Google"
    / "Chrome"
    / "Application"
    / "chrome.exe",
]

CHROMIUM_PATHS = [
    Path(
        r"C:\Program Files\Chromium\Application\chrome.exe"
    ),
    Path(
        r"C:\Program Files (x86)\Chromium\Application\chrome.exe"
    ),
    Path(
        os.environ.get("LOCALAPPDATA", "")
    )
    / "Chromium"
    / "Application"
    / "chrome.exe",
]

SUPPORTED_BROWSERS = (
    "brave",
    "chrome",
    "chromium",
    "termux",
    "headless",
)

AUTO_DETECT_ORDER = (
    "brave",
    "chrome",
    "chromium",
)

BROWSER_LABELS = {
    "auto": "Auto Detect",
    "brave": "Brave Browser",
    "chrome": "Google Chrome",
    "chromium": "Chromium",
    "termux": "Termux Chromium (headless)",
    "headless": "Headless Test Driver",
}

BROWSER_WHICH_NAMES = {
    "brave": (
        "brave.exe",
        "brave",
        "brave-browser",
    ),
    "chrome": (
        "chrome.exe",
        "chrome",
        "google-chrome",
    ),
    "chromium": (
        "chromium.exe",
        "chromium",
        "chromium-browser",
    ),
}

_browser_name = "auto"
_browser_allow_fallback = False
_termux_processes = {}


# ============================================================
# ACTIVE INSTANCES IN THIS PROCESS
# ============================================================

_active_instances = set()


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


def _box_row(
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


def _print_header(
    title: str,
    subtitle: str = "",
):
    """
    Print a consistent Eclipse RPG browser header.
    """

    width = 71

    top = (
        f"{BORDER_COLOR}╔"
        f"{'═' * width}"
        f"╗{RESET}"
    )

    bottom = (
        f"{BORDER_COLOR}╚"
        f"{'═' * width}"
        f"╝{RESET}"
    )

    print()
    print(top)

    print(
        _box_row(
            f"  {MAGENTA}{BOLD}ECLIPSE RPG BOT{RESET}",
            width,
        )
    )

    print(
        _box_row(
            f"  {PURPLE}"
            f"────────────────────────────────────────────────────────────"
            f"{RESET}",
            width,
        )
    )

    print(
        _box_row(
            f"  {CATEGORY_COLOR}{title}{RESET}",
            width,
        )
    )

    if subtitle:

        print(
            _box_row(
                f"  {GRAY}{subtitle}{RESET}",
                width,
            )
        )

    print(bottom)
    print()


def _status(
    label: str,
    message: str,
    color=WHITE,
):
    """
    Print a styled status message.
    """

    print(
        f"  {GRAY}{label}:{RESET} "
        f"{color}{message}{RESET}"
    )


def _success(message: str):
    """
    Print a successful operation.
    """

    print(
        f"  {GREEN}{BOLD}●{RESET} "
        f"{GREEN}{message}{RESET}"
    )


def _info(message: str):
    """
    Print an informational message.
    """

    print(
        f"  {CYAN}{BOLD}●{RESET} "
        f"{WHITE}{message}{RESET}"
    )


def _warning(message: str):
    """
    Print a warning message.
    """

    print(
        f"  {YELLOW}{BOLD}▲{RESET} "
        f"{YELLOW}{message}{RESET}"
    )


def _error(message: str):
    """
    Print an error message.
    """

    print(
        f"  {RED}{BOLD}✖{RESET} "
        f"{RED}{message}{RESET}"
    )


def _section(title: str):
    """
    Print a section divider.
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


# ============================================================
# BROWSER SETTINGS
# ============================================================

def get_browser_name():
    return _browser_name


def set_browser_name(name):
    global _browser_name

    _browser_name = normalize_browser_name(
        name
    )

    return True


def get_browser_allow_fallback():
    return _browser_allow_fallback


def set_browser_allow_fallback(enabled):
    global _browser_allow_fallback

    _browser_allow_fallback = bool(
        enabled
    )

    return True


def normalize_browser_name(name):
    if name is None:
        return "auto"

    normalized = str(
        name
    ).strip().lower()

    if not normalized:
        return "auto"

    if normalized in (
        "auto",
        *SUPPORTED_BROWSERS,
    ):
        return normalized

    return "auto"


def candidate_paths(browser_name):
    name = normalize_browser_name(
        browser_name
    )

    if name == "auto":
        return []

    program_files = Path(
        os.environ.get(
            "ProgramFiles",
            r"C:\Program Files",
        )
    )

    program_files_x86 = Path(
        os.environ.get(
            "ProgramFiles(x86)",
            r"C:\Program Files (x86)",
        )
    )

    local_app = Path(
        os.environ.get(
            "LOCALAPPDATA",
            "",
        )
    )

    if name == "brave":
        paths = list(
            BRAVE_PATHS
        )

        if str(local_app):
            paths.append(
                local_app
                / "BraveSoftware"
                / "Brave-Browser"
                / "Application"
                / "brave.exe"
            )

        return paths

    if name == "chrome":
        return [
            program_files
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",
            program_files_x86
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",
            local_app
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",
        ]

    if name == "chromium":
        return [
            program_files
            / "Chromium"
            / "Application"
            / "chrome.exe",
            program_files_x86
            / "Chromium"
            / "Application"
            / "chrome.exe",
            local_app
            / "Chromium"
            / "Application"
            / "chrome.exe",
        ]

    if name == "termux":
        return [
            Path("/data/data/com.termux/files/usr/bin/chromium"),
            Path("/data/data/com.termux/files/usr/bin/chromium-browser"),
            Path("/data/data/com.termux/files/usr/bin/chrome"),
        ]

    return []


def find_browser_executable(browser_name):
    name = normalize_browser_name(
        browser_name
    )

    if name == "auto":
        return None

    if name == "headless":
        return None

    for path in candidate_paths(name):

        try:

            if path.is_file():
                return path

        except OSError:
            continue

    for command in BROWSER_WHICH_NAMES.get(
        name,
        (),
    ):

        found = shutil.which(
            command
        )

        if found:
            return Path(
                found
            )

    return None


def detect_installed_browsers():
    found = {}

    for name in SUPPORTED_BROWSERS:

        path = find_browser_executable(
            name
        )

        if path is not None:
            found[name] = path

    return found


def resolve_browser(
    requested=None,
    allow_fallback=None,
):
    requested_name = normalize_browser_name(
        requested
    )

    if allow_fallback is None:
        allow_fallback = get_browser_allow_fallback()
    else:
        allow_fallback = bool(
            allow_fallback
        )

    installed = detect_installed_browsers()

    if requested_name == "headless":
        return "headless", None

    if requested_name == "termux":
        path = find_browser_executable("termux")
        if path is None:
            raise FileNotFoundError(
                "Termux Chromium could not be detected. "
                "Install it with: pkg install tur-repo && "
                "pkg install chromium"
            )
        return "termux", path

    if requested_name == "auto":

        for name in AUTO_DETECT_ORDER:

            if name in installed:
                return name, installed[name]

        raise FileNotFoundError(
            "No supported browser could be detected.\n"
            "Looked for Brave, Chrome, and Chromium."
        )

    if requested_name in installed:
        return requested_name, installed[requested_name]

    if allow_fallback:

        for name in AUTO_DETECT_ORDER:

            if name in installed:
                return name, installed[name]

    label = BROWSER_LABELS.get(
        requested_name,
        requested_name,
    )

    raise FileNotFoundError(
        f"{label} could not be detected."
    )


def find_brave():
    """
    Locate Brave Browser on Windows.
    """

    path = find_browser_executable(
        "brave"
    )

    if path is not None:
        return path

    raise FileNotFoundError(
        "Brave Browser could not be found.\n"
        "Checked:\n"
        + "\n".join(
            f"  {path}"
            for path in candidate_paths(
                "brave"
            )
        )
    )


def _find_legacy_browser(paths, label):
    for path in paths:
        if path.is_file():
            return path

    raise FileNotFoundError(
        f"{label} could not be found."
    )


def find_chrome():
    return _find_legacy_browser(
        CHROME_PATHS,
        "Google Chrome",
    )


def find_chromium():
    return _find_legacy_browser(
        CHROMIUM_PATHS,
        "Chromium",
    )


def find_browser(browser_name):
    name = str(browser_name or "").strip().lower()

    if name == "auto":
        for finder in (find_brave, find_chrome, find_chromium):
            try:
                return finder()
            except FileNotFoundError:
                continue
        raise FileNotFoundError(
            "No supported browser could be detected."
        )

    finders = {
        "brave": find_brave,
        "chrome": find_chrome,
        "chromium": find_chromium,
    }

    if name not in finders:
        raise ValueError(
            f"Unsupported browser: {browser_name}"
        )

    return finders[name]()


# ============================================================
# INSTANCE NAME
# ============================================================

def sanitize_instance_name(instance):
    """
    Convert an account name into a safe Windows folder name.
    """

    if instance is None:

        instance = "default"

    name = str(
        instance
    ).strip()

    if not name:

        name = "default"

    name = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        name,
    )

    name = name.rstrip(
        ". "
    )

    if not name:

        name = "default"

    return name


# ============================================================
# PROFILE PATH
# ============================================================

def get_profile_path(instance=None, browser="brave"):
    """
    Return the persistent profile directory for an account.

    Brave keeps the legacy path:

        selenium_profiles\\instance_goldisduck

    Chrome and Chromium use a browser-specific folder so
    they never share Brave's cookies and session data.
    """

    instance_name = sanitize_instance_name(
        instance
    )

    browser_name = normalize_browser_name(
        browser
    )

    if browser_name in (
        "auto",
        "brave",
    ):

        profile_path = (
            PROFILE_ROOT
            / f"instance_{instance_name}"
        )

    else:

        profile_path = (
            PROFILE_ROOT
            / browser_name
            / f"instance_{instance_name}"
        )

    profile_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return profile_path


# ============================================================
# LOCK PATH
# ============================================================

def get_lock_path(instance=None):
    """
    Return the cross-process lock file for an account.
    """

    profile_path = get_profile_path(
        instance
    )

    return profile_path / ".instance.lock"


# ============================================================
# PROCESS CHECK
# ============================================================

def is_process_running(pid):
    """
    Check whether a Windows process is still running.

    Uses tasklist so this works without additional packages.
    """

    if not pid:

        return False

    try:

        result = os.system(
            f'tasklist /FI "PID eq {int(pid)}" '
            ">nul 2>&1"
        )

        return result == 0

    except Exception:

        return False


# ============================================================
# READ LOCK
# ============================================================

def read_lock(lock_path):
    """
    Read lock information.

    Returns:
        dict or None
    """

    try:

        with lock_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(
                file
            )

    except Exception:

        return None


# ============================================================
# CHECK EXISTING LOCK
# ============================================================

def check_existing_lock(instance=None):
    """
    Check whether another process currently owns this account.

    Returns:
        None if available.

        dict containing lock information if active.
    """

    lock_path = get_lock_path(
        instance
    )

    if not lock_path.exists():

        return None

    lock_info = read_lock(
        lock_path
    )

    # --------------------------------------------------------
    # Invalid lock file
    # --------------------------------------------------------

    if not lock_info:

        try:

            lock_path.unlink()

        except Exception:

            pass

        return None

    pid = lock_info.get(
        "pid"
    )

    # --------------------------------------------------------
    # Process still running
    # --------------------------------------------------------

    if is_process_running(
        pid
    ):

        return lock_info

    # --------------------------------------------------------
    # Stale lock
    # --------------------------------------------------------

    _warning(
        "Removing stale account lock."
    )

    try:

        lock_path.unlink()

    except Exception:

        pass

    return None


# ============================================================
# ACQUIRE ACCOUNT LOCK
# ============================================================

def acquire_instance_lock(instance=None):
    """
    Acquire a cross-process lock for an account.

    Returns:
        True if successfully acquired.

    Raises:
        RuntimeError if another bot instance owns it.
    """

    instance_name = sanitize_instance_name(
        instance
    )

    lock_path = get_lock_path(
        instance_name
    )

    # --------------------------------------------------------
    # Check existing lock
    # --------------------------------------------------------

    existing = check_existing_lock(
        instance_name
    )

    if existing:

        pid = existing.get(
            "pid",
            "unknown",
        )

        started = existing.get(
            "started",
            "unknown",
        )

        raise RuntimeError(
            f"Account '{instance_name}' "
            f"is already running.\n"
            f"PID: {pid}\n"
            f"Started: {started}\n"
            f"Lock: {lock_path}"
        )

    # --------------------------------------------------------
    # Create lock atomically
    # --------------------------------------------------------

    lock_data = {
        "account": instance_name,
        "pid": os.getpid(),
        "started": time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

    try:

        # 'x' is important:
        # it fails if another process creates the file first.
        with lock_path.open(
            "x",
            encoding="utf-8",
        ) as file:

            json.dump(
                lock_data,
                file,
                indent=4,
            )

    except FileExistsError:

        existing = check_existing_lock(
            instance_name
        )

        if existing:

            raise RuntimeError(
                f"Account '{instance_name}' "
                f"is already running in another "
                f"Eclipse RPG bot instance."
            )

        # A race occurred with a stale lock.
        # Try once more.

        with lock_path.open(
            "x",
            encoding="utf-8",
        ) as file:

            json.dump(
                lock_data,
                file,
                indent=4,
            )

    _active_instances.add(
        instance_name
    )

    _success(
        f"Account lock acquired: {instance_name}"
    )

    return True


# ============================================================
# RELEASE ACCOUNT LOCK
# ============================================================

def release_instance_lock(instance=None):
    """
    Release the account lock.
    """

    instance_name = sanitize_instance_name(
        instance
    )

    lock_path = get_lock_path(
        instance_name
    )

    # Only remove the lock if it belongs to this process.
    lock_info = read_lock(
        lock_path
    )

    if lock_info:

        lock_pid = lock_info.get(
            "pid"
        )

        if lock_pid == os.getpid():

            try:

                lock_path.unlink()

            except FileNotFoundError:

                pass

            except Exception as error:

                _warning(
                    f"Could not remove account lock: "
                    f"{error}"
                )

    _active_instances.discard(
        instance_name
    )

    _success(
        f"Account lock released: {instance_name}"
    )


# ============================================================
# INSTANCE STATUS
# ============================================================

def is_instance_active(instance=None):
    """
    Check whether an account is currently locked.
    """

    return (
        check_existing_lock(
            instance
        ) is not None
    )


# ============================================================
# CREATE BRAVE DRIVER
# ============================================================

def _create_driver(
    profile_path,
    binary_path,
):
    """
    Create a Chromium-based Selenium instance.
    """

    options = Options()

    # --------------------------------------------------------
    # BROWSER EXECUTABLE
    # --------------------------------------------------------

    options.binary_location = str(
        binary_path
    )

    # --------------------------------------------------------
    # UNIQUE PERSISTENT PROFILE
    # --------------------------------------------------------

    options.add_argument(
        f"--user-data-dir={profile_path}"
    )

    options.add_argument(
        "--profile-directory=Default"
    )

    # --------------------------------------------------------
    # BROWSER SETTINGS
    # --------------------------------------------------------

    options.add_argument(
        "--start-maximized"
    )

    options.add_argument(
        "--disable-notifications"
    )

    options.add_argument(
        "--disable-popup-blocking"
    )

    options.add_argument(
        "--no-first-run"
    )

    options.add_argument(
        "--no-default-browser-check"
    )

    # --------------------------------------------------------
    # PASSWORD PROMPTS
    # --------------------------------------------------------

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }

    options.add_experimental_option(
        "prefs",
        prefs,
    )

    # --------------------------------------------------------
    # START BROWSER
    # --------------------------------------------------------

    driver = webdriver.Chrome(
        options=options
    )

    driver.set_page_load_timeout(
        PAGE_LOAD_TIMEOUT
    )

    return driver


BROWSER_TEST_URL = (
    "data:text/html;charset=utf-8,"
    "<html><body>"
    "<h1 id='rpgbot-probe'>RPGBot</h1>"
    "<input id='rpgbot-input'>"
    "<button id='rpgbot-btn'>Go</button>"
    "</body></html>"
)


def _diagnostic_check(label, ok, detail=""):
    return {
        "label": label,
        "ok": bool(ok),
        "detail": "" if detail is None else str(detail),
    }


def environment_diagnostics():
    results = []

    results.append(
        _diagnostic_check(
            "Python",
            True,
            sys.version.split()[0],
        )
    )

    try:

        import selenium

        results.append(
            _diagnostic_check(
                "Selenium",
                True,
                getattr(
                    selenium,
                    "__version__",
                    "",
                ),
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "Selenium",
                False,
                error,
            )
        )

    try:

        installed = detect_installed_browsers()
        names = ", ".join(
            installed.keys()
        ) or "none"

        results.append(
            _diagnostic_check(
                "Browser detected",
                bool(installed),
                names,
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "Browser detected",
                False,
                error,
            )
        )

    try:

        name, _path = resolve_browser(
            get_browser_name(),
            allow_fallback=get_browser_allow_fallback(),
        )

        results.append(
            _diagnostic_check(
                "Browser resolved",
                True,
                name,
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "Browser resolved",
                False,
                error,
            )
        )

    return results


def driver_diagnostics(driver):
    results = []

    alive = BrowserManager.is_alive(
        driver
    )

    results.append(
        _diagnostic_check(
            "Driver connection",
            alive,
        )
    )

    if not alive:
        return results

    try:

        capabilities = driver.capabilities or {}
        version = (
            capabilities.get("browserVersion")
            or capabilities.get("version")
            or ""
        )

        results.append(
            _diagnostic_check(
                "Browser version",
                bool(version),
                version,
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "Browser version",
                False,
                error,
            )
        )

    try:

        driver.get(
            BROWSER_TEST_URL
        )

        current_url = driver.current_url or ""
        navigated = (
            "rpgbot-probe" in current_url
            or current_url.startswith("data:")
            or BROWSER_TEST_URL in current_url
        )

        results.append(
            _diagnostic_check(
                "Navigation",
                navigated,
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "Navigation",
                False,
                error,
            )
        )

        return results

    try:

        value = driver.execute_script(
            "return 2 + 2;"
        )

        results.append(
            _diagnostic_check(
                "JavaScript",
                value == 4,
                value,
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "JavaScript",
                False,
                error,
            )
        )

    try:

        element = driver.find_element(
            By.CSS_SELECTOR,
            "#rpgbot-probe",
        )

        results.append(
            _diagnostic_check(
                "CSS selector",
                element is not None,
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "CSS selector",
                False,
                error,
            )
        )

    try:

        element = driver.find_element(
            By.XPATH,
            "//h1[@id='rpgbot-probe']",
        )

        results.append(
            _diagnostic_check(
                "XPath",
                element is not None,
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "XPath",
                False,
                error,
            )
        )

    try:

        WebDriverWait(
            driver,
            WAIT_MEDIUM,
        ).until(
            EC.presence_of_element_located(
                (By.ID, "rpgbot-probe")
            )
        )

        results.append(
            _diagnostic_check(
                "WebDriverWait",
                True,
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "WebDriverWait",
                False,
                error,
            )
        )

    try:

        field = driver.find_element(
            By.CSS_SELECTOR,
            "#rpgbot-input",
        )

        field.send_keys(
            "eclipse"
        )

        typed = field.get_attribute(
            "value"
        )

        button = driver.find_element(
            By.CSS_SELECTOR,
            "#rpgbot-btn",
        )

        button.click()

        results.append(
            _diagnostic_check(
                "Browser interaction",
                typed == "eclipse",
            )
        )

    except Exception as error:

        results.append(
            _diagnostic_check(
                "Browser interaction",
                False,
                error,
            )
        )

    return results


def _print_diagnostic_report(results):
    _print_header(
        "BROWSER TEST",
        "Automation interface diagnostics",
    )

    all_ok = True

    for item in results:

        extra = ""

        if item.get("detail"):
            extra = f" ({item['detail']})"

        if item["ok"]:

            print(
                f"  {GREEN}{BOLD}●{RESET} "
                f"{GREEN}{item['label']}{extra}{RESET}"
            )

        else:

            all_ok = False

            print(
                f"  {RED}{BOLD}✖{RESET} "
                f"{RED}{item['label']}{extra}{RESET}"
            )

    print()

    if all_ok:

        _success(
            "Browser test successful."
        )

    else:

        _error(
            "Browser test failed."
        )

    print()

    return all_ok


def _free_local_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_devtools(port, timeout=20):
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/json/version"

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except (OSError, ValueError):
            time.sleep(0.25)

    raise RuntimeError(
        f"Termux Chromium did not expose DevTools on port {port}."
    )


def _create_termux_driver(profile_path, binary_path, instance_name):
    port = _free_local_port()
    command = [
        str(binary_path),
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        f"--remote-debugging-address=127.0.0.1",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_path}",
        "about:blank",
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_devtools(port)
        options = Options()
        options.debugger_address = f"127.0.0.1:{port}"
        chromedriver = shutil.which("chromedriver")
        if chromedriver:
            from selenium.webdriver.chrome.service import Service

            driver = webdriver.Chrome(
                service=Service(chromedriver),
                options=options,
            )
        else:
            driver = webdriver.Chrome(options=options)
        _termux_processes[instance_name] = process
        return driver
    except Exception:
        process.terminate()
        process.wait(timeout=5)
        raise


def _stop_termux_process(instance_name):
    process = _termux_processes.pop(instance_name, None)
    if process is None:
        return
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


# ============================================================
# BROWSER MANAGER
# ============================================================

class BrowserManager:
    """Windows Chromium-family Selenium lifecycle. Eclipse modules receive a driver."""

    @classmethod
    def is_alive(cls, driver):
        """
        Check whether the Selenium Brave session is responding.
        """

        if driver is None:

            return False

        try:

            _ = driver.current_url

            return True

        except Exception:

            return False

    @classmethod
    def test(cls, driver=None):
        """
        Run browser diagnostics without logging into Eclipse.

        When a live driver is provided, checks run in a temporary
        tab so the current game page is restored afterward.
        """

        if getattr(driver, "title", "") == "Headless Mode":
            _success("Headless driver is available.")
            return True

        results = list(
            environment_diagnostics()
        )

        opened_tab = False
        original = None

        if cls.is_alive(driver):

            try:

                original = driver.current_window_handle
                driver.switch_to.new_window(
                    "tab"
                )
                opened_tab = True

            except Exception as error:

                results.append(
                    _diagnostic_check(
                        "Probe tab",
                        False,
                        error,
                    )
                )

            try:

                results.extend(
                    driver_diagnostics(
                        driver
                    )
                )

            finally:

                if opened_tab:

                    try:

                        driver.close()

                    except Exception:

                        pass

                    try:

                        if original is not None:

                            driver.switch_to.window(
                                original
                            )

                    except Exception:

                        pass

        else:

            results.append(
                _diagnostic_check(
                    "Driver connection",
                    False,
                    "No active Selenium session",
                )
            )

        ok = all(
            item["ok"]
            for item in results
        )

        _print_diagnostic_report(
            results
        )

        return ok

    @classmethod
    def create(cls, instance=None, browser_name=None):
        """
        Start an independent persistent browser instance.

        Example:

            driver = setup_driver("goldisduck")

        Every account receives its own persistent profile and
        cross-process lock.
        """

        instance_name = sanitize_instance_name(
            instance
        )

        # --------------------------------------------------------
        # ACQUIRE ACCOUNT LOCK BEFORE STARTING THE BROWSER
        # --------------------------------------------------------

        acquire_instance_lock(
            instance_name
        )

        try:

            selected_name, binary_path = resolve_browser(
                browser_name
                if browser_name is not None
                else get_browser_name(),
                allow_fallback=get_browser_allow_fallback(),
            )

        except Exception:

            release_instance_lock(
                instance_name
            )

            raise

        profile_path = get_profile_path(
            instance_name,
            browser=selected_name,
        )

        engine_label = BROWSER_LABELS.get(
            selected_name,
            selected_name,
        )

        _print_header(
            "BROWSER STARTUP",
            f"Initializing {engine_label} for account: {instance_name}",
        )

        _status(
            "ENGINE",
            engine_label,
            GOLD,
        )

        _status(
            "ACCOUNT",
            instance_name,
            WHITE,
        )

        _status(
            "PROFILE",
            str(profile_path),
            CYAN,
        )

        _status(
            "STATUS",
            "Starting browser instance...",
            CYAN,
        )

        last_error = None

        # --------------------------------------------------------
        # STARTUP RETRIES
        # --------------------------------------------------------

        for attempt in range(
            1,
            STARTUP_RETRIES + 1,
        ):

            driver = None

            try:

                _info(
                    f"Startup attempt "
                    f"{attempt}/{STARTUP_RETRIES}"
                )

                if selected_name == "headless":
                    from headless_mode import create_headless_driver

                    driver = create_headless_driver(instance_name)
                elif selected_name == "termux":
                    driver = _create_termux_driver(
                        profile_path,
                        binary_path,
                        instance_name,
                    )
                else:
                    driver = _create_driver(
                        profile_path,
                        binary_path,
                    )

                time.sleep(
                    1
                )

                if not is_driver_alive(
                    driver
                ):

                    raise WebDriverException(
                        f"{engine_label} started but the "
                        "Selenium session is not responding."
                    )

                _success(
                    f"{engine_label} instance "
                    f"'{instance_name}' is running."
                )

                print()

                return driver

            except Exception as error:

                last_error = error

                _error(
                    f"Startup attempt {attempt} failed."
                )

                print(
                    f"  {GRAY}{error}{RESET}"
                )

                if driver is not None:

                    try:
                        driver.quit()

                    except Exception:

                        pass

                _stop_termux_process(instance_name)

                if attempt < STARTUP_RETRIES:

                    _warning(
                        f"Retrying in "
                        f"{RETRY_DELAY} seconds..."
                    )

                    time.sleep(
                        RETRY_DELAY
                    )

        # --------------------------------------------------------
        # STARTUP FAILED
        # --------------------------------------------------------

        release_instance_lock(
            instance_name
        )

        raise RuntimeError(
            f"Unable to start {engine_label} for account "
            f"'{instance_name}'.\n"
            f"Profile: {profile_path}\n"
            f"Last error: {last_error}"
        )

    @classmethod
    def close(cls, driver, instance=None):
        """
        Safely close Brave and release the account lock.
        """

        instance_name = sanitize_instance_name(
            instance
        )

        _section(
            "BROWSER SHUTDOWN"
        )

        _status(
            "ACCOUNT",
            instance_name,
            WHITE,
        )

        if driver is not None:

            _status(
                "STATUS",
                "Closing Brave session...",
                CYAN,
            )

            try:
                driver.quit()

                _success(
                    "Brave session closed."
                )

            except Exception:

                _warning(
                    "Brave session was already closed."
                )

        _stop_termux_process(instance_name)

        release_instance_lock(
            instance_name
        )

    @classmethod
    def restart(cls, driver, instance=None):
        """
        Restart Brave for an account.

        The persistent profile is preserved.

        The caller should perform the application's login
        procedure again if the website session was lost.
        """

        instance_name = sanitize_instance_name(
            instance
        )

        _section(
            "BROWSER RECOVERY"
        )

        _warning(
            f"Restarting Brave instance '{instance_name}'..."
        )

        cls.close(
            driver,
            instance_name,
        )

        time.sleep(
            1
        )

        new_driver = cls.create(
            instance_name
        )

        _success(
            "Browser recovery completed."
        )

        return new_driver


def is_driver_alive(driver):
    return BrowserManager.is_alive(driver)


def setup_driver(instance=None, browser_name="auto"):
    return BrowserManager.create(instance, browser_name)


def close_driver(driver, instance=None):
    return BrowserManager.close(driver, instance)


def restart_driver(driver, instance=None):
    return BrowserManager.restart(driver, instance)


# ============================================================
# WAIT FOR BROWSER
# ============================================================

def wait_for_browser(
    driver,
    timeout=10,
):
    """
    Wait for Brave to become responsive.

    Returns:
        True when the browser responds.
        False if it remains unavailable.
    """

    end_time = (
        time.time()
        + timeout
    )

    while time.time() < end_time:

        if is_driver_alive(
            driver
        ):

            return True

        time.sleep(
            0.5
        )

    return False