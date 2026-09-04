from pathlib import Path
import json
import os
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

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

# ============================================================
# CHROME LOCATIONS
# ============================================================

CHROME_PATHS = [
    Path(
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ),
    Path(
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ),
    Path(
        os.path.expanduser(
            r"~\AppData\Local\Google\Chrome\Application\chrome.exe"
        )
    ),
]

# ============================================================
# CHROMIUM LOCATIONS
# ============================================================

CHROMIUM_PATHS = [
    Path(
        r"C:\Program Files\Chromium\Application\chromium.exe"
    ),
    Path(
        r"C:\Program Files (x86)\Chromium\Application\chromium.exe"
    ),
    Path(
        os.path.expanduser(
            r"~\AppData\Local\Chromium\Application\chromium.exe"
        )
    ),
]


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
# BRAVE PATH
# ============================================================

def find_brave():
    """
    Locate Brave Browser on Windows.
    """

    for path in BRAVE_PATHS:

        if path.is_file():

            return path

    raise FileNotFoundError(
        "Brave Browser could not be found.\n"
        "Checked:\n"
        + "\n".join(
            f"  {path}"
            for path in BRAVE_PATHS
        )
    )


def find_chrome():
    """
    Locate Google Chrome on Windows.
    """

    for path in CHROME_PATHS:

        if path.is_file():

            return path

    raise FileNotFoundError(
        "Google Chrome could not be found.\n"
        "Checked:\n"
        + "\n".join(
            f"  {path}"
            for path in CHROME_PATHS
        )
    )


def find_chromium():
    """
    Locate Chromium on Windows.
    """

    for path in CHROMIUM_PATHS:

        if path.is_file():

            return path

    raise FileNotFoundError(
        "Chromium could not be found.\n"
        "Checked:\n"
        + "\n".join(
            f"  {path}"
            for path in CHROMIUM_PATHS
        )
    )


def find_browser(browser_name="brave"):
    """
    Find browser executable by name.
    
    Supports: brave, chrome, chromium, auto, android-cdp, android-brave, termux, headless
    """
    
    browser_name = str(browser_name).lower().strip()
    
    if browser_name == "brave":
        return find_brave()
    elif browser_name == "chrome":
        return find_chrome()
    elif browser_name == "chromium":
        return find_chromium()
    elif browser_name == "android-cdp":
        # CDP remote debugging on Android device
        return "android-cdp"
    elif browser_name == "android-brave":
        # Brave on Android via CDP
        return "android-brave"
    elif browser_name == "termux":
        # Termux Chromium
        try:
            from android_browser import AndroidBrowserManager
            path = AndroidBrowserManager.find_termux_chromium()
            if path:
                return path
            raise FileNotFoundError("Termux Chromium not found")
        except ImportError:
            raise FileNotFoundError("Android browser module not available")
    elif browser_name == "auto":
        # Auto-detect: try in order
        try:
            return find_brave()
        except FileNotFoundError:
            pass
        
        try:
            return find_chrome()
        except FileNotFoundError:
            pass
        
        try:
            return find_chromium()
        except FileNotFoundError:
            pass
        
        raise FileNotFoundError(
            "No supported browser found.\n"
            "Checked: Brave, Chrome, Chromium"
        )
    else:
        raise ValueError(
            f"Unknown browser: {browser_name}\n"
            "Supported: brave, chrome, chromium, auto, android-cdp, android-brave, termux, headless"
        )


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

def get_profile_path(instance=None):
    """
    Return the persistent Brave profile directory.

    Example:

        setup_driver("goldisduck")

    uses:

        selenium_profiles\\instance_goldisduck
    """

    instance_name = sanitize_instance_name(
        instance
    )

    profile_path = (
        PROFILE_ROOT
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
# CREATE CHROMIUM-BASED DRIVER
# ============================================================

def _create_driver(
    profile_path,
    browser_path,
    browser_name="brave",
):
    """
    Create a Chromium-based browser Selenium instance.
    
    Works with: Brave, Chrome, Chromium
    (All use the same Chrome WebDriver)
    """

    options = Options()

    # --------------------------------------------------------
    # BROWSER EXECUTABLE
    # --------------------------------------------------------

    options.binary_location = str(
        browser_path
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
    # START BRAVE
    # --------------------------------------------------------

    driver = webdriver.Chrome(
        options=options
    )

    driver.set_page_load_timeout(
        PAGE_LOAD_TIMEOUT
    )

    return driver


# ============================================================
# BROWSER MANAGER
# ============================================================

class BrowserManager:
    """Windows Brave Selenium lifecycle. Eclipse modules receive a driver."""

    @classmethod
    def is_alive(cls, driver):
        """
        Check whether the Selenium browser session is responding.
        """

        if driver is None:

            return False

        try:

            _ = driver.current_url

            return True

        except Exception:

            return False

    @classmethod
    def create(cls, instance=None, browser="auto"):
        """
        Start an independent persistent browser instance.

        Supports: brave, chrome, chromium, auto, android-cdp, android-brave, termux, headless, headless

        Example:

            driver = BrowserManager.create("goldisduck", browser="brave")
            driver = BrowserManager.create("goldisduck", browser="android-cdp")
            driver = BrowserManager.create("goldisduck", browser="headless")

        Every account receives its own persistent profile and
        cross-process lock.
        
        For android-cdp: Requires CDP to be forwarded via ADB
        For termux: Requires Termux environment
        For headless: No browser needed (testing/framework verification)
        """

        instance_name = sanitize_instance_name(instance)
        browser_name = str(browser).lower().strip()

        # Handle headless mode (no browser)
        if browser_name == "headless":
            return cls._create_headless_driver(instance_name)

        # Handle Android CDP specially
        if browser_name == "android-cdp":
            return cls._create_android_cdp_driver(instance_name)
        
        # Handle Android Brave
        if browser_name == "android-brave":
            return cls._create_android_brave_driver(instance_name)
        
        # Handle Termux Chromium
        if browser_name == "termux":
            return cls._create_termux_driver(instance_name)

        # --------------------------------------------------------
        # ACQUIRE ACCOUNT LOCK BEFORE STARTING BROWSER
        # --------------------------------------------------------

        acquire_instance_lock(instance_name)

        profile_path = get_profile_path(instance_name)

        try:
            browser_path = find_browser(browser_name)

        except Exception:
            release_instance_lock(instance_name)
            raise

        # Determine display name for browser
        display_name = browser_name.title() if browser_name != "auto" else "Auto-detected Browser"

        _print_header(
            "BROWSER STARTUP",
            f"Initializing {display_name} for account: {instance_name}",
        )

        _status(
            "ENGINE",
            display_name,
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

                driver = _create_driver(
                    profile_path,
                    browser_path,
                    browser_name,
                )

                time.sleep(
                    1
                )

                if not is_driver_alive(
                    driver
                ):

                    raise WebDriverException(
                        f"{display_name} started but the Selenium "
                        "session is not responding."
                    )

                _success(
                    f"{display_name} instance '{instance_name}' "
                    f"is running."
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
            f"Unable to start Brave for account "
            f"'{instance_name}'.\n"
            f"Profile: {profile_path}\n"
            f"Last error: {last_error}"
        )

    @classmethod
    def _create_android_brave_driver(cls, instance_name):
        """Create driver for Brave on Android via CDP."""
        
        _print_header(
            "ANDROID BRAVE CONNECTION",
            f"Connecting to Brave on Android device: {instance_name}",
        )
        
        _status(
            "MODE",
            "Brave CDP Remote Debugging",
            GOLD,
        )
        
        try:
            from android_brave import AndroidBraveManager
            
            # Check if Brave is installed
            _status(
                "CHECK",
                "Verifying Brave installation...",
                CYAN,
            )
            
            if not AndroidBraveManager.is_brave_installed():
                _warning("Brave not detected, attempting to start anyway")
            else:
                _success("Brave detected on device")
            
            # Setup CDP forwarding
            _status(
                "SETUP",
                "Starting Brave in debug mode...",
                CYAN,
            )
            
            result = AndroidBraveManager.setup_brave_cdp_forwarding()
            
            if not result["success"]:
                _error(f"Brave setup failed: {result['error']}")
                raise Exception(result['error'])
            
            _success(f"Brave CDP ready: {result['url']}")
            
            # Create CDP driver
            _status(
                "CONNECTION",
                "Connecting to Brave...",
                CYAN,
            )
            
            driver_result = AndroidBraveManager.create_brave_cdp_driver(
                result['url']
            )
            
            if not driver_result["success"]:
                _error(f"Driver creation failed: {driver_result['error']}")
                raise Exception(driver_result['error'])
            
            _success("Connected to Brave on Android")
            print()
            
            return driver_result["driver"]
        
        except ImportError:
            _error("Android Brave module not available")
            raise

    @classmethod
    def _create_android_cdp_driver(cls, instance_name):
        """Create driver via Android CDP remote debugging."""
        
        _print_header(
            "ANDROID CDP CONNECTION",
            f"Connecting to remote Chrome/Brave on device: {instance_name}",
        )
        
        _status(
            "MODE",
            "CDP Remote Debugging",
            GOLD,
        )
        
        try:
            from android_browser import AndroidBrowserManager
            
            _status(
                "SETUP",
                "Configuring ADB forwarding...",
                CYAN,
            )
            
            result = AndroidBrowserManager.setup_cdp_forwarding()
            
            if not result["success"]:
                _error(f"CDP Setup Failed: {result['error']}")
                raise Exception(result['error'])
            
            _success(f"CDP forwarding ready: {result['url']}")
            
            _status(
                "CONNECTION",
                "Connecting to remote browser...",
                CYAN,
            )
            
            driver_result = AndroidBrowserManager.create_cdp_driver(
                result['url']
            )
            
            if not driver_result["success"]:
                _error(f"Driver creation failed: {driver_result['error']}")
                raise Exception(driver_result['error'])
            
            _success("Connected to remote browser")
            print()
            
            return driver_result["driver"]
        
        except ImportError:
            _error("Android browser module not available")
            raise

    @classmethod
    def _create_termux_driver(cls, instance_name):
        """Create driver for Termux Chromium."""
        
        acquire_instance_lock(instance_name)
        
        _print_header(
            "TERMUX CHROMIUM",
            f"Launching Termux Chromium for account: {instance_name}",
        )
        
        _status(
            "ENGINE",
            "Termux Chromium",
            GOLD,
        )
        
        try:
            from android_browser import AndroidBrowserManager
            
            chromium_path = AndroidBrowserManager.find_termux_chromium()
            
            if not chromium_path:
                _error("Termux Chromium not found")
                release_instance_lock(instance_name)
                raise FileNotFoundError("Termux Chromium not installed")
            
            profile_path = get_profile_path(instance_name)
            
            _status(
                "LAUNCH",
                "Starting Termux Chromium...",
                CYAN,
            )
            
            driver = _create_driver(
                profile_path,
                chromium_path,
                "termux",
            )
            
            _success("Termux Chromium started")
            print()
            
            return driver
        
        except Exception as e:
            release_instance_lock(instance_name)
            raise

    @classmethod
    def _create_headless_driver(cls, instance_name):
        """Create headless driver for testing without browser."""
        
        from headless_mode import create_headless_driver
        
        return create_headless_driver(instance_name)

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
                "Closing browser session...",
                CYAN,
            )

            try:

                driver.quit()

                _success(
                    "Browser session closed."
                )

            except Exception:

                _warning(
                    "Browser session was already closed."
                )

        release_instance_lock(
            instance_name
        )

    @classmethod
    def restart(cls, driver, instance=None):
        """
        Restart the browser for an account.

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
            f"Restarting browser instance '{instance_name}'..."
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


def setup_driver(instance=None, browser="auto"):
    """
    Create a browser driver instance.
    
    Supports: brave, chrome, chromium, auto
    """
    return BrowserManager.create(instance, browser)


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
    Wait for the browser to become responsive.

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

# ================================================================
# SESSION PERSISTENCE INTEGRATION
# ================================================================

def get_driver_with_recovery(instance_name, browser="auto"):
    """
    Get or recover a browser driver with crash detection.
    
    Attempts to recover from previous crashes if possible.
    """
    from session_manager import SessionManager, ProfileRecovery, CrashDetector
    
    # Check if we can recover from a previous crash
    if SessionManager.can_recover_session(instance_name):
        print(f"Previous session found for {instance_name}, attempting recovery...")
        SessionManager.resume_session(instance_name)
    
    # Start new session
    driver = BrowserManager.create(instance_name, browser=browser)
    
    if driver:
        # Start session tracking
        SessionManager.start_session(instance_name, browser)
        
        # Start crash monitoring
        CrashDetector.monitor_driver(driver, instance_name)
    
    return driver



# ================================================================
# HEADLESS MODE FOR TESTING
# ================================================================

def create_headless_driver(instance_name):
    """
    Create headless driver for testing without browser.
    
    Useful for mobile testing or framework verification.
    """
    from headless_mode import create_headless_driver as create_headless
    return create_headless(instance_name)

