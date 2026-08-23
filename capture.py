import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException,
)

from utils import safe_click, normalize


WAIT_LONG = 20


# ============================================================
# BATTLE BUTTON
# ============================================================

def get_battle_button(driver):

    try:

        buttons = driver.find_elements(
            By.ID,
            "battlebtn"
        )

        for button in buttons:

            try:

                if button.is_displayed():

                    return button

            except StaleElementReferenceException:

                continue

    except Exception:

        pass

    return None


# ============================================================
# ITEM ACTION
# ============================================================

def find_item_action(driver):

    """
    Eclipse RPG capture screen uses:

    <div class="battle_link">
        <span id="B_ItemAction">
            <a href="javascript: change_action('item');">
                Item
            </a>
        </span>
    </div>

    IMPORTANT:
    We specifically target B_ItemAction.

    This prevents the bot from accidentally clicking
    unrelated buttons or advertisements.
    """

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "#B_ItemAction a"
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

        pass

    return None


def click_item_action(driver):

    print(
        "  Looking for Item..."
    )

    start = time.time()

    while (
        time.time() - start
        < WAIT_LONG
    ):

        item = find_item_action(
            driver
        )

        if item is not None:

            try:

                print(
                    "  ✓ Item action found."
                )

                if safe_click(
                    driver,
                    item
                ):

                    print(
                        "  ✓ Item clicked."
                    )

                    time.sleep(
                        random.uniform(
                            0.5,
                            0.9
                        )
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(0.3)

    print(
        "  ✗ Item action not found."
    )

    return False


# ============================================================
# BALL SELECTION
# ============================================================

def get_ball_elements(driver):

    try:

        holder = driver.find_element(
            By.ID,
            "B_ItemHolder"
        )

        spans = holder.find_elements(
            By.XPATH,
            "./span[@onclick]"
        )

        result = []

        for span in spans:

            try:

                if not span.is_displayed():

                    continue

                img = span.find_element(
                    By.TAG_NAME,
                    "img"
                )

                name = img.get_attribute(
                    "alt"
                )

                if name:

                    result.append(
                        (
                            normalize(name),
                            span
                        )
                    )

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                continue

        return result

    except Exception:

        return []


def verify_ball_selected(
    driver,
    ball_name
):

    wanted = normalize(
        ball_name
    )

    try:

        elements = driver.find_elements(
            By.ID,
            "B_CurrentSelection1"
        )

        for element in elements:

            try:

                text = normalize(
                    element.text
                )

                if wanted in text:

                    return True

                images = element.find_elements(
                    By.TAG_NAME,
                    "img"
                )

                for image in images:

                    alt = normalize(
                        image.get_attribute(
                            "alt"
                        )
                    )

                    title = normalize(
                        image.get_attribute(
                            "title"
                        )
                    )

                    src = normalize(
                        image.get_attribute(
                            "src"
                        )
                    )

                    if (
                        wanted == alt
                        or wanted == title
                        or wanted.replace(
                            " ",
                            "_"
                        ) in src
                    ):

                        return True

            except Exception:

                continue

    except Exception:

        pass

    return False


def select_ball(
    driver,
    preferred=(
        "Ultra Ball",
        "Great Ball",
        "PokeBall",
    )
):

    print(
        "  Waiting for ball selection..."
    )

    start = time.time()

    while (
        time.time() - start
        < WAIT_LONG
    ):

        balls = get_ball_elements(
            driver
        )

        if balls:

            print(
                "  Balls available: "
                + ", ".join(
                    name.title()
                    for name, _ in balls
                )
            )

            for wanted in preferred:

                wanted_normal = normalize(
                    wanted
                )

                for name, element in balls:

                    if name != wanted_normal:

                        continue

                    print(
                        f"  Selecting {wanted}..."
                    )

                    try:

                        if safe_click(
                            driver,
                            element
                        ):

                            print(
                                f"  ✓ {wanted} clicked."
                            )

                            time.sleep(
                                random.uniform(
                                    0.4,
                                    0.7
                                )
                            )

                            if verify_ball_selected(
                                driver,
                                wanted
                            ):

                                print(
                                    f"  ✓ {wanted} confirmed."
                                )

                                return True

                            # Some versions of the site don't
                            # update B_CurrentSelection1 reliably.
                            #
                            # If the element was successfully
                            # clicked, allow the capture flow
                            # to continue.

                            print(
                                f"  ⚠ {wanted} selection "
                                "could not be visually confirmed."
                            )

                            return True

                    except (
                        StaleElementReferenceException,
                        WebDriverException,
                    ):

                        continue

            print(
                "  ✗ Preferred balls were not available."
            )

            return False

        time.sleep(0.3)

    print(
        "  ✗ Ball holder never appeared."
    )

    return False


# ============================================================
# ATTACK BUTTON
# ============================================================

def click_capture_attack(driver):

    print(
        "  Waiting for Attack/Fight..."
    )

    start = time.time()

    while (
        time.time() - start
        < WAIT_LONG
    ):

        button = get_battle_button(
            driver
        )

        if button is not None:

            try:

                state = normalize(
                    button.text
                )

                if state in (
                    "attack",
                    "fight",
                ):

                    print(
                        f"  Battle button: "
                        f"'{button.text.strip()}'"
                    )

                    if safe_click(
                        driver,
                        button
                    ):

                        print(
                            f"  ✓ '{state}' clicked."
                        )

                        return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(0.3)

    print(
        "  ✗ Attack/Fight button not found."
    )

    return False


# ============================================================
# USE ANOTHER
# ============================================================

def find_use_another(driver):

    """
    Eclipse RPG capture failure uses:

    <button
        onclick="document.getElementById('B_Action').value = 'Item';
        return create_attack(this, event.pageX, event.pageY, event);"
        class="forward">

        Use Another (95 left)

    </button>

    We deliberately search for a BUTTON whose visible text
    contains "Use Another".

    This avoids generic links/buttons and advertisements.
    """

    try:

        buttons = driver.find_elements(
            By.XPATH,
            "//button[contains("
            "translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'use another'"
            ")]"
        )

        for button in buttons:

            try:

                if (
                    button.is_displayed()
                    and button.is_enabled()
                ):

                    return button

            except StaleElementReferenceException:

                continue

    except Exception:

        pass

    return None


def click_use_another(driver):

    print(
        "  Looking for Use Another..."
    )

    start = time.time()

    while (
        time.time() - start
        < WAIT_LONG
    ):

        button = find_use_another(
            driver
        )

        if button is not None:

            try:

                print(
                    f"  ✓ Use Another found: "
                    f"'{button.text.strip()}'"
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
                            0.7,
                            1.2
                        )
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(0.3)

    print(
        "  ✗ Use Another button not found."
    )

    return False


# ============================================================
# CAPTURE CONTINUE
# ============================================================

def find_capture_continue(driver):

    """
    Successful capture uses:

    <button class="enterclass"
        onclick="this.disabled= true;
        this.value='Loading...';
        document.location='legendary_areas?area_id=3#search';">
        Continue
    </button>

    We target the actual Continue button.

    We also verify that it points back toward the search
    results when possible.
    """

    try:

        buttons = driver.find_elements(
            By.XPATH,
            "//button[normalize-space()='Continue']"
        )

        for button in buttons:

            try:

                if not (
                    button.is_displayed()
                    and button.is_enabled()
                ):

                    continue

                onclick = normalize(
                    button.get_attribute(
                        "onclick"
                    )
                )

                value = normalize(
                    button.get_attribute(
                        "value"
                    )
                )

                # Preferred exact site behavior.
                if (
                    "legendary_areas" in onclick
                    and "area_id=3" in onclick
                ):

                    return button

                # Fallback: visible Continue button.
                if (
                    value == "continue"
                    or normalize(button.text)
                    == "continue"
                ):

                    return button

            except StaleElementReferenceException:

                continue

    except Exception:

        pass

    return None


def click_capture_continue(driver):

    print(
        "  Looking for capture Continue..."
    )

    start = time.time()

    while (
        time.time() - start
        < WAIT_LONG
    ):

        button = find_capture_continue(
            driver
        )

        if button is not None:

            try:

                print(
                    "  ✓ Capture Continue found."
                )

                if safe_click(
                    driver,
                    button
                ):

                    print(
                        "  ✓ Continue clicked."
                    )

                    time.sleep(
                        random.uniform(
                            1.0,
                            1.8
                        )
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
# CAPTURE RESULT
# ============================================================

def capture_completed(driver):

    """
    Determine whether the encounter has finished.

    A successful capture should eventually expose Continue.

    A failed capture should expose Use Another.
    """

    if find_capture_continue(
        driver
    ) is not None:

        return "success"

    if find_use_another(
        driver
    ) is not None:

        return "failed"

    return None


# ============================================================
# FULL CAPTURE FLOW
# ============================================================

def capture_encounter(driver):

    print()
    print(
        "  Pokémon encounter!"
    )

    attempt = 0

    while True:

        attempt += 1

        print()
        print(
            f"  Capture attempt #{attempt}"
        )

        # ====================================================
        # OPEN ITEM MENU
        # ====================================================

        if not click_item_action(
            driver
        ):

            print(
                "  ✗ Could not open Item menu."
            )

            return False

        # ====================================================
        # SELECT BALL
        # ====================================================

        if not select_ball(
            driver
        ):

            print(
                "  ✗ Ball selection failed."
            )

            return False

        # ====================================================
        # THROW BALL / ATTACK
        # ====================================================

        if not click_capture_attack(
            driver
        ):

            print(
                "  ✗ Could not throw ball."
            )

            return False

        print(
            "  Waiting for capture result..."
        )

        # ====================================================
        # WAIT FOR RESULT
        # ====================================================

        result_start = time.time()

        result = None

        while (
            time.time() - result_start
            < WAIT_LONG
        ):

            result = capture_completed(
                driver
            )

            if result is not None:

                break

            time.sleep(0.3)

        # ====================================================
        # SUCCESS
        # ====================================================

        if result == "success":

            print()
            print(
                "  ✓ Pokémon captured!"
            )

            print(
                "  Continuing back to search..."
            )

            if click_capture_continue(
                driver
            ):

                print(
                    "  ✓ Returned to search."
                )

                return True

            print(
                "  ✗ Capture succeeded, but "
                "Continue could not be clicked."
            )

            return False

        # ====================================================
        # FAILED CAPTURE
        # ====================================================

        if result == "failed":

            button = find_use_another(
                driver
            )

            if button is not None:

                try:

                    print()
                    print(
                        "  ⚠ Capture failed."
                    )

                    print(
                        f"  {button.text.strip()}"
                    )

                except Exception:

                    pass

            if click_use_another(
                driver
            ):

                print(
                    "  ✓ Preparing another capture attempt..."
                )

                time.sleep(
                    random.uniform(
                        0.8,
                        1.4
                    )
                )

                continue

            print(
                "  ✗ Could not click Use Another."
            )

            return False

        # ====================================================
        # UNKNOWN RESULT
        # ====================================================

        print(
            "  ⚠ Capture result could not be determined."
        )

        # Give the page a little longer before declaring
        # failure.

        time.sleep(1)

        if find_capture_continue(
            driver
        ) is not None:

            print(
                "  ✓ Capture completed."
            )

            if click_capture_continue(
                driver
            ):

                return True

        if find_use_another(
            driver
        ) is not None:

            print(
                "  ⚠ Capture failed; trying another ball."
            )

            if click_use_another(
                driver
            ):

                continue

        print(
            "  ✗ Could not determine capture result."
        )

        return False