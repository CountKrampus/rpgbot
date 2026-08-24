import time
import random

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from utils import (
    safe_click,
    normalize,
)


# ============================================================
# CONFIGURATION
# ============================================================

WAIT_LONG = 20


# ============================================================
# CAPTURE PREFERENCES
# ============================================================

PREFERRED_BALL_ORDER = [
    "Ultra Ball",
    "Great Ball",
    "Pokeball",
]


def get_preferred_ball_order():
    """
    Return the current ball priority order (a copy, so callers
    can't accidentally mutate the live list).
    """

    return list(PREFERRED_BALL_ORDER)


def set_preferred_ball_order(order):
    """
    Replace the ball priority order used by select_best_ball().

    order: a list of ball names, most-preferred first. A ball
    not in this list is still usable as a fallback if none of
    the preferred balls are available - this only controls
    priority, not what's allowed.
    """

    global PREFERRED_BALL_ORDER

    if not order:
        return False

    PREFERRED_BALL_ORDER = list(order)

    return True


# ============================================================
# CAPTURE STATISTICS
# ============================================================
#
# In-memory session counters, incremented at the natural points
# in select_best_ball() / capture_encounter() below.

_capture_stats = {
    "encounters": 0,
    "captured": 0,
    "failed": 0,
    "balls_used": {},
}


def get_capture_stats():
    """
    Return a copy of the current session's capture statistics:

        {
            "encounters": 12,
            "captured": 9,
            "failed": 3,
            "balls_used": {"Ultra Ball": 7, "Great Ball": 2},
        }
    """

    return {
        "encounters": _capture_stats["encounters"],
        "captured": _capture_stats["captured"],
        "failed": _capture_stats["failed"],
        "balls_used": dict(_capture_stats["balls_used"]),
    }


def reset_capture_stats():

    _capture_stats["encounters"] = 0
    _capture_stats["captured"] = 0
    _capture_stats["failed"] = 0
    _capture_stats["balls_used"] = {}


def _record_ball_used(ball_name):

    _capture_stats["balls_used"][ball_name] = (
        _capture_stats["balls_used"].get(ball_name, 0) + 1
    )


# ============================================================
# HELPERS
# ============================================================

def wait_for_document_ready(driver, timeout=WAIT_LONG):

    start = time.time()

    while time.time() - start < timeout:

        try:

            state = driver.execute_script(
                "return document.readyState"
            )

            if state in (
                "interactive",
                "complete",
            ):
                return True

        except Exception:
            pass

        time.sleep(0.2)

    return False


# ============================================================
# FIND ELEMENT
# ============================================================

def find_first_visible(
    driver,
    selectors,
    timeout=WAIT_LONG,
):

    start = time.time()

    while time.time() - start < timeout:

        for by, selector in selectors:

            try:

                elements = driver.find_elements(
                    by,
                    selector
                )

                for element in elements:

                    try:

                        if (
                            element.is_displayed()
                            and element.is_enabled()
                        ):

                            return element

                    except StaleElementReferenceException:

                        continue

            except Exception:

                continue

        time.sleep(0.2)

    return None


# ============================================================
# ITEM
# ============================================================

def find_item_action(driver):

    selectors = [

        (
            By.XPATH,
            "//a[contains(@href,'battle') "
            "and normalize-space()='Item']"
        ),

        (
            By.XPATH,
            "//input[@value='Item']"
        ),

        (
            By.XPATH,
            "//button[normalize-space()='Item']"
        ),

        (
            By.XPATH,
            "//*[self::a or self::button or self::input]"
            "[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'item')]"
        ),

    ]

    return find_first_visible(
        driver,
        selectors,
        timeout=WAIT_LONG,
    )


def click_item(driver):

    print(
        "  Looking for Item..."
    )

    item = find_item_action(
        driver
    )

    if not item:

        print(
            "  ✗ Item action not found."
        )

        return False

    print(
        "  ✓ Item action found."
    )

    try:

        if safe_click(
            driver,
            item
        ):

            print(
                "  ✓ Item clicked."
            )

            return True

    except (
        StaleElementReferenceException,
        WebDriverException,
    ):

        pass

    print(
        "  ✗ Could not click Item."
    )

    return False


# ============================================================
# BALL SELECTION
# ============================================================

def get_available_balls(driver):

    balls = []

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "span[onclick*='item_choice(']"
        )

        for element in elements:

            try:

                if not element.is_displayed():
                    continue

                image = element.find_element(
                    By.TAG_NAME,
                    "img"
                )

                alt = (
                    image.get_attribute("alt")
                    or ""
                ).strip()

                if not alt:
                    continue

                lowered = normalize(alt)

                if (
                    "pokeball" in lowered
                    or "great ball" in lowered
                    or "ultra ball" in lowered
                    or "premier ball" in lowered
                    or "luxury ball" in lowered
                    or "quick ball" in lowered
                    or "repeat ball" in lowered
                    or "dusk ball" in lowered
                    or "timer ball" in lowered
                    or "net ball" in lowered
                    or "nest ball" in lowered
                    or "heal ball" in lowered
                    or "friend ball" in lowered
                    or "love ball" in lowered
                    or "moon ball" in lowered
                    or "level ball" in lowered
                    or "lure ball" in lowered
                    or "heavy ball" in lowered
                    or "fast ball" in lowered
                    or "master ball" in lowered
                ):

                    if alt not in balls:
                        balls.append(alt)

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                continue

    except Exception:

        pass

    return balls


def has_usable_ball(driver):

    return bool(
        get_available_balls(
            driver
        )
    )


def select_best_ball(driver):

    print(
        "  Waiting for ball selection..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        balls = get_available_balls(
            driver
        )

        if balls:

            print(
                "  Balls available: "
                + ", ".join(balls)
            )

            selected = None

            for wanted in PREFERRED_BALL_ORDER:

                for ball in balls:

                    if normalize(ball) == normalize(
                        wanted
                    ):

                        selected = ball
                        break

                if selected:
                    break

            if not selected:

                selected = balls[0]

            print(
                f"  Selecting {selected}..."
            )

            try:

                elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    "span[onclick*='item_choice(']"
                )

                for element in elements:

                    try:

                        if not element.is_displayed():
                            continue

                        image = element.find_element(
                            By.TAG_NAME,
                            "img"
                        )

                        alt = (
                            image.get_attribute(
                                "alt"
                            )
                            or ""
                        ).strip()

                        if normalize(alt) != normalize(
                            selected
                        ):
                            continue

                        print(
                            f"  ✓ Found {selected} "
                            "selection."
                        )

                        if safe_click(
                            driver,
                            element
                        ):

                            print(
                                f"  ✓ {selected} clicked."
                            )

                            _record_ball_used(selected)

                            return True

                    except (
                        StaleElementReferenceException,
                        WebDriverException,
                    ):

                        continue

            except Exception as e:

                print(
                    f"  ⚠ Ball selection error: {e}"
                )

        time.sleep(0.3)

    print(
        "  ✗ No usable Poké Ball found."
    )

    return False


# ============================================================
# ATTACK / FIGHT
# ============================================================

def find_attack_button(driver):

    """
    Eclipse RPG can use either "Attack" or "Fight"
    depending on the battle page.

    The current battle page also provides:

        <button id="battlebtn" ...>
            <img ...>
            Fight
        </button>

    #battlebtn is therefore the most reliable selector.
    """

    selectors = [

        # ----------------------------------------------------
        # BEST / MOST RELIABLE:
        # Eclipse RPG battle button.
        # ----------------------------------------------------

        (
            By.ID,
            "battlebtn"
        ),

        (
            By.CSS_SELECTOR,
            "button#battlebtn"
        ),

        # ----------------------------------------------------
        # Attack
        # ----------------------------------------------------

        (
            By.XPATH,
            "//input[@value='Attack']"
        ),

        (
            By.XPATH,
            "//button[normalize-space()='Attack']"
        ),

        (
            By.XPATH,
            "//a[normalize-space()='Attack']"
        ),

        # ----------------------------------------------------
        # Fight
        # ----------------------------------------------------

        (
            By.XPATH,
            "//input[@value='Fight']"
        ),

        (
            By.XPATH,
            "//button[normalize-space()='Fight']"
        ),

        (
            By.XPATH,
            "//a[normalize-space()='Fight']"
        ),

        # ----------------------------------------------------
        # Generic Attack/Fight fallback.
        # ----------------------------------------------------

        (
            By.XPATH,
            "//*[self::input or self::button or self::a]"
            "[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'attack') "
            "or contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'fight')]"
        ),

    ]

    return find_first_visible(
        driver,
        selectors,
        timeout=WAIT_LONG,
    )


def click_attack(driver):

    print(
        "  Waiting for Attack/Fight..."
    )

    button = find_attack_button(
        driver
    )

    if not button:

        print(
            "  ✗ Attack/Fight button not found."
        )

        return False

    try:

        text = (
            button.text.strip()
            or (
                button.get_attribute(
                    "value"
                )
                or ""
            ).strip()
        )

        if not text:

            text = "Attack/Fight"

        print(
            f"  Battle button: '{text}'"
        )

        if safe_click(
            driver,
            button
        ):

            print(
                f"  ✓ '{normalize(text)}' clicked."
            )

            return True

    except (
        StaleElementReferenceException,
        WebDriverException,
    ):

        pass

    print(
        "  ✗ Could not click Attack/Fight."
    )

    return False


# ============================================================
# CAPTURE RESULT
# ============================================================

def capture_succeeded(driver):

    try:

        body = driver.find_element(
            By.TAG_NAME,
            "body"
        )

        text = normalize(
            body.text
        )

        success_phrases = [
            "was caught",
            "was captured",
            "you have obtained",
            "pokemon obtained",
            "has been sent to your box",
            "has been registered",
        ]

        for phrase in success_phrases:

            if phrase in text:

                return True

    except Exception:

        pass

    return False


def capture_failed(driver):

    try:

        body = driver.find_element(
            By.TAG_NAME,
            "body"
        )

        text = normalize(
            body.text
        )

        failure_phrases = [
            "use another",
            "capture failed",
            "broke free",
            "escaped",
        ]

        for phrase in failure_phrases:

            if phrase in text:

                return True

    except Exception:

        pass

    return False


# ============================================================
# USE ANOTHER
# ============================================================

def find_use_another(driver):

    selectors = [

        (
            By.XPATH,
            "//*[self::a or self::button or self::input]"
            "[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'use another')]"
        ),

        (
            By.XPATH,
            "//*[self::a or self::button or self::input]"
            "[contains(translate(@value,"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'use another')]"
        ),

    ]

    return find_first_visible(
        driver,
        selectors,
        timeout=5,
    )


def click_use_another(driver):

    print(
        "  Looking for Use Another..."
    )

    button = find_use_another(
        driver
    )

    if not button:

        print(
            "  ✗ Use Another not found."
        )

        return False

    try:

        text = (
            button.text.strip()
            or (
                button.get_attribute(
                    "value"
                )
                or ""
            ).strip()
        )

        print(
            f"  ✓ Use Another found: '{text}'"
        )

        if safe_click(
            driver,
            button
        ):

            print(
                "  ✓ Use Another clicked."
            )

            time.sleep(
                random.uniform(
                    0.5,
                    1.0
                )
            )

            return True

    except (
        StaleElementReferenceException,
        WebDriverException,
    ):

        pass

    return False


# ============================================================
# CAPTURE CONTINUE
# ============================================================

def find_capture_continue(driver):

    selectors = [

        (
            By.XPATH,
            "//button[normalize-space()='Continue']"
        ),

        (
            By.XPATH,
            "//input[@value='Continue']"
        ),

        (
            By.XPATH,
            "//a[normalize-space()='Continue']"
        ),

        (
            By.XPATH,
            "//*[self::button or self::input or self::a]"
            "[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'continue')]"
        ),

    ]

    for by, selector in selectors:

        try:

            elements = driver.find_elements(
                by,
                selector
            )

            for button in elements:

                try:

                    if not (
                        button.is_displayed()
                        and button.is_enabled()
                    ):
                        continue

                    text = normalize(
                        button.text
                    )

                    value = normalize(
                        button.get_attribute(
                            "value"
                        )
                    )

                    onclick = normalize(
                        button.get_attribute(
                            "onclick"
                        )
                    )

                    if (
                        "legendary_areas" in onclick
                        and "document.location" in onclick
                    ):

                        return button

                    if (
                        text == "continue"
                        or value == "continue"
                    ):

                        return button

                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):

                    continue

        except Exception:

            continue

    return None


def click_capture_continue(driver):

    print(
        "  Looking for capture Continue..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        button = find_capture_continue(
            driver
        )

        if button is not None:

            try:

                print(
                    "  ✓ Capture Continue found."
                )

                onclick = button.get_attribute(
                    "onclick"
                )

                if onclick:

                    print(
                        f"  Continue action: "
                        f"{onclick}"
                    )

                if safe_click(
                    driver,
                    button
                ):

                    print(
                        "  ✓ Continue clicked."
                    )

                    navigation_start = time.time()

                    while (
                        time.time()
                        - navigation_start
                        < WAIT_LONG
                    ):

                        try:

                            current_url = (
                                driver.current_url
                                .lower()
                            )

                            if (
                                "legendary_areas"
                                in current_url
                            ):

                                print(
                                    "  ✓ Returned to "
                                    "legendary area."
                                )

                                time.sleep(
                                    random.uniform(
                                        0.8,
                                        1.5
                                    )
                                )

                                return True

                        except Exception:

                            pass

                        time.sleep(0.3)

                    print(
                        "  ⚠ Continue was clicked, "
                        "but navigation could not "
                        "be verified."
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(0.3)

    print(
        "  ✗ Capture Continue button not found."
    )

    return False


# ============================================================
# SINGLE CAPTURE ATTEMPT
# ============================================================

def capture_attempt(driver):

    if not click_item(
        driver
    ):

        return False

    if not has_usable_ball(
        driver
    ):

        print(
            "  ✗ No usable Poke Ball in inventory."
        )

        return False

    if not select_best_ball(
        driver
    ):

        return False

    if not click_attack(
        driver
    ):

        return False

    print(
        "  Waiting for capture result..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        if capture_succeeded(
            driver
        ):

            print()
            print(
                "  ✓ Pokémon captured!"
            )

            return True

        if capture_failed(
            driver
        ):

            print()
            print(
                "  ⚠ Capture failed."
            )

            return False

        time.sleep(0.3)

    print(
        "  ⚠ Capture result timed out."
    )

    return False


# ============================================================
# MAIN ENCOUNTER CAPTURE
# ============================================================

def capture_encounter(driver):

    print()
    print(
        "  Pokémon encounter!"
    )

    _capture_stats["encounters"] += 1

    max_attempts = 3

    for attempt in range(
        1,
        max_attempts + 1
    ):

        print()
        print(
            f"  Capture attempt #{attempt}"
        )

        success = capture_attempt(
            driver
        )

        if success:

            print(
                "  ✓ Capture successful."
            )

            _capture_stats["captured"] += 1

            print(
                "  Continuing back to search..."
            )

            if not click_capture_continue(
                driver
            ):

                print(
                    "  ✗ Could not click capture Continue."
                )

                return False

            print(
                "  ✓ Returned to search."
            )

            return True

        if not has_usable_ball(
            driver
        ):

            print(
                "  ✗ Out of usable Poke Balls. "
                "Stopping encounter."
            )

            _capture_stats["failed"] += 1

            return False

        use_another = find_use_another(
            driver
        )

        if use_another:

            if click_use_another(
                driver
            ):

                print(
                    "  ✓ Preparing another "
                    "capture attempt..."
                )

                time.sleep(
                    random.uniform(
                        0.5,
                        1.0
                    )
                )

                continue

        print(
            "  ✗ No further capture attempt "
            "available."
        )

        _capture_stats["failed"] += 1

        return False

    print(
        "  ✗ Capture attempts exhausted."
    )

    _capture_stats["failed"] += 1

    return False