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

                # Only accept actual Poké Balls.
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

            # ----------------------------------------------------
            # Prefer the strongest commonly available ball.
            # ----------------------------------------------------

            preferred = [
                "Ultra Ball",
                "Great Ball",
                "Pokeball",
            ]

            selected = None

            for wanted in preferred:

                for ball in balls:

                    if normalize(ball) == normalize(
                        wanted
                    ):

                        selected = ball
                        break

                if selected:
                    break

            # ----------------------------------------------------
            # If none of the preferred balls exists, use the
            # first available ball.
            # ----------------------------------------------------

            if not selected:

                selected = balls[0]

            print(
                f"  Selecting {selected}..."
            )

            # ----------------------------------------------------
            # IMPORTANT:
            #
            # Eclipse RPG uses:
            #
            # <span onclick="item_choice(3803194);">
            #     <img src="/images/items/ultra_ball.png"
            #          alt="Ultra Ball">
            # </span>
            #
            # So we click the SPAN, not the image.
            # ----------------------------------------------------

            try:

                elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    "span[onclick*='item_choice(']"
                )

                for element in elements:

                    try:

                        if not (
                            element.is_displayed()
                        ):
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

        time.sleep(
            0.3
        )

    print(
        "  ✗ No usable Poké Ball found."
    )

    return False


# ============================================================
# ATTACK
# ============================================================

def find_attack_button(driver):

    selectors = [

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

        (
            By.XPATH,
            "//*[self::input or self::button or self::a]"
            "[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'attack')]"
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
            "  ✗ Attack button not found."
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

    """
    Find the Continue control shown after a
    successful capture.

    IMPORTANT:

    We do NOT hardcode an area_id.

    Examples:

        legendary_areas?area_id=3#search
        legendary_areas?area_id=12#search
        legendary_areas?area_id=17#search

    All of these must work.
    """

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

                    # ------------------------------------------------
                    # Best match:
                    #
                    # Continue button whose JavaScript returns
                    # to legendary_areas.
                    #
                    # DO NOT check area_id.
                    # ------------------------------------------------

                    if (
                        "legendary_areas" in onclick
                        and "document.location" in onclick
                    ):

                        return button

                    # ------------------------------------------------
                    # Generic Continue fallback.
                    # ------------------------------------------------

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

                    # ------------------------------------------------
                    # Wait for navigation back to the legendary
                    # area.
                    # ------------------------------------------------

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

                        time.sleep(
                            0.3
                        )

                    # ------------------------------------------------
                    # Click happened successfully even if URL
                    # verification timed out.
                    # ------------------------------------------------

                    print(
                        "  ⚠ Continue was clicked, "
                        "but navigation could not be verified."
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(
            0.3
        )

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

        time.sleep(
            0.3
        )

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

    max_attempts = 3

    for attempt in range(
        1,
        max_attempts + 1
    ):

        print()
        print(
            f"  Capture attempt #{attempt}"
        )

        # ----------------------------------------------------
        # First attempt or next attempt.
        # ----------------------------------------------------

        success = capture_attempt(
            driver
        )

        if success:

            print(
                "  ✓ Capture successful."
            )

            # ------------------------------------------------
            # IMPORTANT:
            #
            # After the Pokémon is caught, Eclipse RPG does
            # NOT automatically return to the search page.
            #
            # We MUST click Continue.
            # ------------------------------------------------

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

        # ----------------------------------------------------
        # Capture failed.
        #
        # Look for Use Another.
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # No retry option.
        # ----------------------------------------------------

        print(
            "  ✗ No further capture attempt "
            "available."
        )

        return False

    print(
        "  ✗ Capture attempts exhausted."
    )

    return False