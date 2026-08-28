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