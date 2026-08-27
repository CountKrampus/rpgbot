import time
import random

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from config import MINES_URL, WAIT_LONG
from helpers import safe_click, wait_for_document_ready
from search import find_encounter_fight, click_encounter_fight
from capture import capture_encounter


# ============================================================
# MINING TIMING
# ============================================================

# Short polling keeps mining responsive without adding
# unnecessary delays between mines.
MINE_POLL_WAIT = 0.15

# Small delay after a successful click. Eclipse normally
# processes the result quickly, but this gives the page a
# chance to update before we inspect it.
MINE_RESULT_MIN_WAIT = 0.35
MINE_RESULT_MAX_WAIT = 0.75

# Maximum time to wait for a temporarily disabled Mine button
# to become usable.
MINE_BUTTON_WAIT = min(
    max(float(WAIT_LONG), 3.0),
    10.0,
)

# Maximum time to wait for a result after clicking Mine.
MINE_RESULT_WAIT = min(
    max(float(WAIT_LONG), 3.0),
    10.0,
)


# ============================================================
# MINE BUTTON
# ============================================================

def find_mine_button(
    driver,
    require_enabled=True,
):
    """
    Find the Eclipse Mine button.

    require_enabled=True:
        Only return a button that can currently be clicked.

    require_enabled=False:
        Return a visible Mine button even if Eclipse has
        temporarily disabled it.

    The latter is useful for distinguishing:
        - Mine button exists but is temporarily disabled
        - Mine button genuinely disappeared
    """

    selectors = [
        (
            By.CSS_SELECTOR,
            "button.mine-button",
        ),
        (
            By.XPATH,
            "//button[contains(@class,'mine-button') "
            "and .//img[contains(@src,'pickaxe')]]",
        ),
        (
            By.XPATH,
            "//button[.//img[contains(@src,'pickaxe')] "
            "and contains(normalize-space(.),'Mine')]",
        ),
        (
            By.XPATH,
            "//input[contains(@class,'mine-button') "
            "and contains(@value,'Mine')]",
        ),
        (
            By.XPATH,
            "//button[normalize-space()='Mine']",
        ),
    ]

    for by, selector in selectors:

        try:

            elements = driver.find_elements(
                by,
                selector,
            )

            for element in elements:

                try:

                    if not element.is_displayed():

                        continue

                    if require_enabled:

                        if not element.is_enabled():

                            continue

                    return element

                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):

                    continue

        except Exception:

            continue

    return None


# ============================================================
# PAGE STATE HELPERS
# ============================================================

def _body_text(
    driver,
):
    try:

        return driver.find_element(
            By.TAG_NAME,
            "body",
        ).text.lower()

    except Exception:

        return ""


def area_cleared_detected(
    driver,
):
    """
    Detect mining-area completion.

    Kept deliberately broad because Eclipse can change the
    exact wording of the completion message.
    """

    text = _body_text(
        driver
    )

    if not text:

        return False

    return any(
        phrase in text
        for phrase in (
            "area cleared",
            "mine area cleared",
            "mining area cleared",
            "you have cleared",
            "area has been cleared",
        )
    )


def encounter_detected(
    driver,
):
    """
    Quickly determine whether a Pokémon encounter appeared.
    """

    try:

        if find_encounter_fight(
            driver
        ):

            return True

    except Exception:

        pass

    return False


# ============================================================
# MINE CLICK
# ============================================================

def click_mine(
    driver,
):
    """
    Wait for the Mine button to become enabled and click it.

    IMPORTANT:
    A visible-but-disabled Mine button is NOT treated as an
    error. Eclipse temporarily disables the button while its
    previous action is processing.

    While waiting, we also check for:
        - Pokémon encounters
        - Area completion
    """

    end_time = (
        time.time()
        + MINE_BUTTON_WAIT
    )

    disabled_seen = False

    while time.time() < end_time:

        # ----------------------------------------------------
        # Check for an encounter first.
        #
        # This prevents us from sitting around waiting for the
        # Mine button when Eclipse has actually moved into an
        # encounter state.
        # ----------------------------------------------------

        if encounter_detected(
            driver
        ):

            return False

        # ----------------------------------------------------
        # Check for area completion.
        # ----------------------------------------------------

        if area_cleared_detected(
            driver
        ):

            return False

        # ----------------------------------------------------
        # Look for an enabled Mine button.
        # ----------------------------------------------------

        element = find_mine_button(
            driver,
            require_enabled=True,
        )

        if element:

            try:

                # Tiny randomized delay helps avoid hammering
                # the same JavaScript button repeatedly.
                time.sleep(
                    random.uniform(
                        0.15,
                        0.30,
                    )
                )

                if safe_click(
                    driver,
                    element,
                ):

                    print(
                        "  ✓ Mine clicked."
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        else:

            # ------------------------------------------------
            # The button may exist but still be disabled.
            # That's normal during Eclipse processing.
            # ------------------------------------------------

            disabled_element = find_mine_button(
                driver,
                require_enabled=False,
            )

            if disabled_element:

                if not disabled_seen:

                    print(
                        "  ⏳ Mine temporarily disabled; "
                        "waiting..."
                    )

                    disabled_seen = True

        time.sleep(
            MINE_POLL_WAIT
        )

    return False


# ============================================================
# WAIT FOR MINING RESULT
# ============================================================

def wait_for_mining_result(
    driver,
):
    """
    Wait for Eclipse to finish processing a Mine click.

    Returns:
        True  - normal mining result detected
        False - encounter or area completion detected
    """

    # Give Eclipse a small amount of time to start updating
    # the page. This is much faster than the old 1.2-2.0 sec
    # fixed delay.
    time.sleep(
        random.uniform(
            MINE_RESULT_MIN_WAIT,
            MINE_RESULT_MAX_WAIT,
        )
    )

    end_time = (
        time.time()
        + MINE_RESULT_WAIT
    )

    while time.time() < end_time:

        if encounter_detected(
            driver
        ):

            return False

        if area_cleared_detected(
            driver
        ):

            return False

        # If Mine is enabled again, Eclipse has normally
        # finished processing the previous result.
        if find_mine_button(
            driver,
            require_enabled=True,
        ):

            return True

        time.sleep(
            MINE_POLL_WAIT
        )

    # Don't automatically consider a timeout fatal.
    # The caller will check encounter/completion state.
    return True


# ============================================================
# AREA COMPLETION
# ============================================================

def handle_area_cleared(
    driver,
):
    """
    Handle the mining-area completion screen.
    """

    if not area_cleared_detected(
        driver
    ):

        return False

    print(
        "⚠ Mining area completion detected."
    )

    completion_selectors = [
        (
            By.XPATH,
            "//button[normalize-space()='OK']",
        ),
        (
            By.XPATH,
            "//input[@value='OK']",
        ),
        (
            By.XPATH,
            "//button[normalize-space()='Continue']",
        ),
        (
            By.XPATH,
            "//input[@value='Continue']",
        ),
    ]

    for by, selector in completion_selectors:

        try:

            elements = driver.find_elements(
                by,
                selector,
            )

            for element in elements:

                try:

                    if (
                        element.is_displayed()
                        and element.is_enabled()
                    ):

                        if safe_click(
                            driver,
                            element,
                        ):

                            time.sleep(
                                0.5
                            )

                            return True

                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):

                    continue

        except Exception:

            continue

    return True


# ============================================================
# MINING CONTINUE
# ============================================================

def click_mining_continue(
    driver,
):
    """
    Click Continue after a mining Pokémon capture.

    Eclipse may use document.location='mines#mine', which can
    leave the browser URL effectively unchanged. Therefore we
    do NOT require a URL change to consider this successful.
    """

    selectors = [
        (
            By.XPATH,
            "//button[normalize-space()='Continue']",
        ),
        (
            By.XPATH,
            "//input[@value='Continue']",
        ),
    ]

    end_time = (
        time.time()
        + min(
            max(float(WAIT_LONG), 2.0),
            8.0,
        )
    )

    while time.time() < end_time:

        for by, selector in selectors:

            try:

                elements = driver.find_elements(
                    by,
                    selector,
                )

                for element in elements:

                    try:

                        if (
                            not element.is_displayed()
                            or not element.is_enabled()
                        ):

                            continue

                        if safe_click(
                            driver,
                            element,
                        ):

                            print(
                                "  ✓ Continue clicked."
                            )

                            # Eclipse disables Continue and
                            # navigates to mines#mine through
                            # JavaScript. Wait briefly for the
                            # mining interface to return instead
                            # of requiring a URL change.
                            ready_end = (
                                time.time()
                                + min(
                                    max(
                                        float(WAIT_LONG),
                                        2.0,
                                    ),
                                    5.0,
                                )
                            )

                            while (
                                time.time()
                                < ready_end
                            ):

                                if (
                                    find_mine_button(
                                        driver,
                                        require_enabled=False,
                                    )
                                    or encounter_detected(
                                        driver
                                    )
                                    or area_cleared_detected(
                                        driver
                                    )
                                ):

                                    print(
                                        "  ✓ Returned to mining."
                                    )

                                    return True

                                time.sleep(
                                    MINE_POLL_WAIT
                                )

                            # The click itself succeeded.
                            # Do not produce a scary warning just
                            # because Eclipse did not expose a
                            # detectable state immediately.
                            print(
                                "  ✓ Continue accepted."
                            )

                            return True

                    except (
                        StaleElementReferenceException,
                        WebDriverException,
                    ):

                        continue

            except Exception:

                continue

        time.sleep(
            MINE_POLL_WAIT
        )

    return False


# ============================================================
# MINING ENCOUNTER
# ============================================================

def handle_mining_encounter(
    driver,
    catch_pokemon,
):
    """
    Handle a Pokémon encountered while mining.
    """

    if not find_encounter_fight(
        driver
    ):

        return False

    print(
        "\n  Pokémon encounter while mining!"
    )

    # --------------------------------------------------------
    # Mine-only mode.
    # --------------------------------------------------------

    if not catch_pokemon:

        try:

            driver.get(
                MINES_URL
            )

            wait_for_document_ready(
                driver
            )

            time.sleep(
                random.uniform(
                    0.6,
                    1.0,
                )
            )

            print(
                "  ✓ Returning to mining."
            )

            return True

        except Exception as error:

            print(
                f"  ✗ Could not return to mining: {error}"
            )

            return False

    # --------------------------------------------------------
    # Enter encounter.
    # --------------------------------------------------------

    if not click_encounter_fight(
        driver
    ):

        return False

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # capture_encounter() contains the latest capture fixes,
    # including the Use Another logic.
    # --------------------------------------------------------

    if not capture_encounter(
        driver
    ):

        print(
            "  ✗ Mining encounter capture failed."
        )

        print(
            "  → Returning to mining area..."
        )

        try:

            driver.get(
                MINES_URL
            )

            wait_for_document_ready(
                driver
            )

            time.sleep(
                random.uniform(
                    0.6,
                    1.0,
                )
            )

        except Exception:

            pass

        return False

    print(
        "  ✓ Mining Pokémon captured."
    )

    # --------------------------------------------------------
    # Return from capture result.
    #
    # Do not require the URL to change because Eclipse uses
    # mines#mine JavaScript navigation.
    # --------------------------------------------------------

    if not click_mining_continue(
        driver
    ):

        # As a fallback, reload the mining page.
        try:

            driver.get(
                MINES_URL
            )

            wait_for_document_ready(
                driver
            )

            time.sleep(
                random.uniform(
                    0.6,
                    1.0,
                )
            )

        except Exception:

            return False

    return True


# ============================================================
# MINER MODE
# ============================================================

def miner_mode(
    driver,
):
    print(
        "\n"
        + "=" * 60
        + "\nA-MINER\n"
        + "=" * 60
    )

    choice = input(
        "\n"
        "1. Mine and catch Pokémon\n"
        "2. Mine only\n"
        "\n"
        "Choose: "
    ).strip()

    catch_pokemon = (
        choice != "2"
    )

    # --------------------------------------------------------
    # Open mining page.
    # --------------------------------------------------------

    try:

        driver.get(
            MINES_URL
        )

        wait_for_document_ready(
            driver
        )

        time.sleep(
            random.uniform(
                0.8,
                1.3,
            )
        )

    except Exception as error:

        print(
            f"✗ Could not open mining page: {error}"
        )

        return

    mine_count = 0

    while True:

        mine_count += 1

        print(
            f"\n=== Mine #{mine_count} ==="
        )

        # ----------------------------------------------------
        # Check whether we're already in an encounter.
        # ----------------------------------------------------

        if encounter_detected(
            driver
        ):

            if not handle_mining_encounter(
                driver,
                catch_pokemon,
            ):

                print(
                    "✗ Mining encounter handling failed."
                )

                return

            continue

        # ----------------------------------------------------
        # Check for area completion.
        # ----------------------------------------------------

        if handle_area_cleared(
            driver
        ):

            print(
                "✓ Mining area completed."
            )

            break

        # ----------------------------------------------------
        # Click Mine.
        #
        # click_mine() now waits for a grayed-out button instead
        # of treating it as an immediate failure.
        # ----------------------------------------------------

        if click_mine(
            driver
        ):

            # ------------------------------------------------
            # Wait for Eclipse to process the mining action.
            # ------------------------------------------------

            wait_for_mining_result(
                driver
            )

        # ----------------------------------------------------
        # An encounter may have appeared while the Mine button
        # was disabled/processing.
        # ----------------------------------------------------

        if encounter_detected(
            driver
        ):

            if not handle_mining_encounter(
                driver,
                catch_pokemon,
            ):

                print(
                    "✗ Mining encounter handling failed."
                )

                return

            continue

        # ----------------------------------------------------
        # Check for area completion.
        # ----------------------------------------------------

        if handle_area_cleared(
            driver
        ):

            print(
                "✓ Mining area completed."
            )

            break

        # ----------------------------------------------------
        # If Mine is still disabled, give Eclipse another short
        # opportunity to finish processing rather than looping
        # rapidly and printing false errors.
        # ----------------------------------------------------

        mine_button = find_mine_button(
            driver,
            require_enabled=True,
        )

        if mine_button is None:

            disabled_button = find_mine_button(
                driver,
                require_enabled=False,
            )

            if disabled_button:

                print(
                    "  ⏳ Mining action still processing..."
                )

                processing_end = (
                    time.time()
                    + min(
                        max(
                            float(WAIT_LONG),
                            2.0,
                        ),
                        6.0,
                    )
                )

                while (
                    time.time()
                    < processing_end
                ):

                    if encounter_detected(
                        driver
                    ):

                        break

                    if handle_area_cleared(
                        driver
                    ):

                        break

                    if find_mine_button(
                        driver,
                        require_enabled=True,
                    ):

                        break

                    time.sleep(
                        MINE_POLL_WAIT
                    )

                # Re-check the important states after waiting.
                if encounter_detected(
                    driver
                ):

                    if not handle_mining_encounter(
                        driver,
                        catch_pokemon,
                    ):

                        print(
                            "✗ Mining encounter handling failed."
                        )

                        return

                    continue

                if handle_area_cleared(
                    driver
                ):

                    print(
                        "✓ Mining area completed."
                    )

                    break

                if find_mine_button(
                    driver,
                    require_enabled=True,
                ):

                    print(
                        "  ✓ Mining result processed."
                    )

                    continue

        else:

            print(
                "  ✓ Mining result processed."
            )

        # ----------------------------------------------------
        # Very short pause before the next iteration.
        #
        # This is intentionally much shorter than the old
        # .8-1.4 second fixed delay.
        # ----------------------------------------------------

        time.sleep(
            random.uniform(
                0.15,
                0.35,
            )
        )