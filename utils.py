import random
import time

from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException,
)


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize(text):
    """
    Normalize text for reliable comparisons.

    Example:
        "  Use   Another (95 left) "
        -> "use another (95 left)"
    """

    if text is None:
        return ""

    return " ".join(
        str(text).split()
    ).strip().lower()


# ============================================================
# ELEMENT HELPERS
# ============================================================

def visible_enabled(element):
    """
    Return True when an element is visible and enabled.
    """

    try:
        return (
            element.is_displayed()
            and element.is_enabled()
        )

    except (
        StaleElementReferenceException,
        WebDriverException,
    ):
        return False


# ============================================================
# HUMAN-LIKE CLICK
# ============================================================

def human_like_click(
    driver,
    element
):
    """
    Attempt a normal Selenium click with a small delay.

    Falls back to JavaScript if the normal click fails.
    """

    try:

        actions = ActionChains(
            driver
        )

        actions.move_to_element(
            element
        )

        actions.pause(
            random.uniform(
                0.15,
                0.4
            )
        )

        actions.click()

        actions.perform()

        return True

    except Exception:

        # JavaScript fallback.
        try:

            driver.execute_script(
                "arguments[0].click();",
                element
            )

            return True

        except Exception:

            return False


# ============================================================
# SAFE CLICK
# ============================================================

def safe_click(
    driver,
    element
):
    """
    Safely click an element.

    Returns:
        True  - click succeeded
        False - click failed
    """

    try:

        return human_like_click(
            driver,
            element
        )

    except (
        StaleElementReferenceException,
        ElementClickInterceptedException,
        WebDriverException,
    ):

        return False


# ============================================================
# DOCUMENT READY
# ============================================================

def wait_for_document_ready(
    driver,
    timeout=20
):
    """
    Wait for the current page to finish loading.
    """

    try:

        from selenium.webdriver.support.ui import (
            WebDriverWait
        )

        WebDriverWait(
            driver,
            timeout
        ).until(
            lambda d:
            d.execute_script(
                "return document.readyState"
            )
            in (
                "interactive",
                "complete"
            )
        )

    except Exception:

        pass


# ============================================================
# RANDOM DELAY
# ============================================================

def sleep_random(
    low,
    high
):
    """
    Sleep for a random amount of time.
    """

    time.sleep(
        random.uniform(
            low,
            high
        )
    )


# ============================================================
# ELEMENT FINDERS
# ============================================================

def find_first_visible(driver, by, value):
    """
    Find the first visible element matching selector.
    
    Returns the element if found and visible, else None.
    
    Example:
        elem = find_first_visible(driver, By.CLASS_NAME, "button")
    """
    
    try:
        
        elements = driver.find_elements(by, value)
        
        for element in elements:
            
            try:
                
                if element.is_displayed():
                    return element
                
            except (
                StaleElementReferenceException,
                WebDriverException,
            ):
                
                continue
        
        return None
    
    except Exception:
        
        return None


def find_all_visible(driver, by, value):
    """
    Find all visible elements matching selector.
    
    Returns list of visible elements.
    
    Example:
        buttons = find_all_visible(driver, By.TAG_NAME, "button")
    """
    
    try:
        
        elements = driver.find_elements(by, value)
        visible = []
        
        for element in elements:
            
            try:
                
                if element.is_displayed():
                    visible.append(element)
                
            except (
                StaleElementReferenceException,
                WebDriverException,
            ):
                
                continue
        
        return visible
    
    except Exception:
        
        return []


def get_element_text(element, default=""):
    """
    Safely get text from an element.
    
    Returns element text or default if text is empty/error.
    
    Example:
        text = get_element_text(elem, default="N/A")
    """
    
    try:
        
        text = element.text.strip()
        
        return text if text else default
    
    except (
        StaleElementReferenceException,
        WebDriverException,
    ):
        
        return default


# ============================================================
# FORMATTING HELPERS
# ============================================================

def format_duration_seconds(seconds):
    """
    Convert seconds to human-readable duration.
    
    Returns string like "1h 30m 45s" or "2m 30s".
    
    Example:
        format_duration_seconds(5745)  # "1h 35m 45s"
    """
    
    seconds = int(seconds)
    
    if seconds < 0:
        return "0s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    
    if hours > 0:
        parts.append(f"{hours}h")
    
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def print_divider(width=60, char="="):
    """
    Print a divider line.
    
    Example:
        print_divider()          # "============================================================"
        print_divider(40, "-")   # "----------------------------------------"
    """
    
    print(char * width)


def print_section(title, width=60, char="="):
    """
    Print a formatted section header.
    
    Example:
        print_section("MAIN MENU")
        # ============================================================
        # MAIN MENU
        # ============================================================
    """
    
    print()
    print_divider(width, char)
    print(title)
    print_divider(width, char)


def print_status(status, message=""):
    """
    Print a status line with emoji/symbol.
    
    Status values:
        "✓" / "success" / "ok"      → ✓ 
        "✗" / "error" / "fail"      → ✗ 
        "⚠" / "warning" / "warn"    → ⚠ 
        "ℹ" / "info"                 → ℹ 
    
    Example:
        print_status("✓", "Battle complete")  # ✓ Battle complete
        print_status("error", "Failed to load")  # ✗ Failed to load
    """
    
    status_map = {
        "✓": "✓",
        "success": "✓",
        "ok": "✓",
        "✗": "✗",
        "error": "✗",
        "fail": "✗",
        "⚠": "⚠",
        "warning": "⚠",
        "warn": "⚠",
        "ℹ": "ℹ",
        "info": "ℹ",
    }
    
    symbol = status_map.get(status.lower(), status)
    
    if message:
        print(f"{symbol} {message}")
    else:
        print(symbol)


# ============================================================
# RETRY HELPERS
# ============================================================

def retry_click(driver, element, max_attempts=3, delay=0.5):
    """
    Retry clicking an element multiple times.
    
    Useful for flaky elements that fail on first try.
    
    Returns True if click succeeded, False if all attempts failed.
    
    Example:
        if retry_click(driver, button, max_attempts=3):
            print("Click succeeded")
    """
    
    for attempt in range(max_attempts):
        
        if safe_click(driver, element):
            return True
        
        if attempt < max_attempts - 1:
            time.sleep(delay)
    
    return False


def wait_for_clickable(driver, element, timeout=10):
    """
    Wait until element is clickable (visible and enabled).
    
    Returns True if element became clickable, False if timeout.
    
    Example:
        if wait_for_clickable(driver, button):
            safe_click(driver, button)
    """
    
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(element)
        )
        
        return True
    
    except Exception:
        
        return False


# ============================================================
# NETWORK SETTINGS (Phase 3)
# ============================================================

_browser_timeout = 20  # seconds
_slow_network_mode = False


def get_browser_timeout():
    """Return default browser/element timeout (seconds)."""
    return _browser_timeout


def set_browser_timeout(seconds):
    """Set default browser/element timeout."""
    global _browser_timeout
    
    if seconds <= 0:
        return False
    
    _browser_timeout = int(seconds)
    return True


def get_slow_network_mode():
    """Return True if slow network mode is enabled (delays multiplied by 1.5x)."""
    return _slow_network_mode


def set_slow_network_mode(enabled):
    """Set slow network mode (auto-multiplies delays by 1.5x)."""
    global _slow_network_mode
    _slow_network_mode = bool(enabled)
    return True


def get_delay_multiplier():
    """
    Get the current delay multiplier based on slow network mode.
    
    Returns 1.5 if slow network mode enabled, 1.0 otherwise.
    """
    return 1.5 if _slow_network_mode else 1.0


# ============================================================
# SESSION MANAGEMENT SETTINGS (Phase 3)
# ============================================================

_session_time_limit = None  # None = no limit, int = minutes
_auto_logout_after_session = False
_notify_on_shiny_encounter = True


def get_session_time_limit():
    """Return session time limit in minutes, or None if disabled."""
    return _session_time_limit


def set_session_time_limit(minutes):
    """Set session time limit (None to disable)."""
    global _session_time_limit
    
    if minutes is None:
        _session_time_limit = None
        return True
    
    if isinstance(minutes, int) and minutes > 0:
        _session_time_limit = minutes
        return True
    
    return False


def get_auto_logout_after_session():
    """Return True if auto-logout is enabled."""
    return _auto_logout_after_session


def set_auto_logout_after_session(enabled):
    """Set whether to auto-logout when session ends."""
    global _auto_logout_after_session
    _auto_logout_after_session = bool(enabled)
    return True


def get_notify_on_shiny_encounter():
    """Return True if shiny encounter notifications are enabled."""
    return _notify_on_shiny_encounter


def set_notify_on_shiny_encounter(enabled):
    """Set whether to notify on shiny Pokémon encounters."""
    global _notify_on_shiny_encounter
    _notify_on_shiny_encounter = bool(enabled)
    return True