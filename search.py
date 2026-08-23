import time
import random

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from capture import capture_encounter
from utils import (
    safe_click,
    normalize,
    wait_for_document_ready,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://eclipserpg.com"

WAIT_LONG = 20

SEARCH_DELAY = (
    1.5,
    2.5,
)


# ============================================================
# MAP ORDER
# ============================================================

MAPS = [
    "Jirachi's Park",
    "Entei's Tower",
    "Kyogre's Temple",
    "Groudon's Palace",
    "Mesprit's Lake",
    "Mewtwo's Cavern",
    "Manaphy's Haven",
    "Eternal Garden",
    "Heatran's Mountain",
    "Spear Pillar",
    "Regigigas' Domain",
    "Deep Mewtwo's Cave",
    "Moon Gaze Mountain",
    "Icebound Cave",
    "Sky Pillar",
    "Mirage Ruins",
    "Latias Heaven",
    "Ruins of Alph",
]


# ============================================================
# SEARCH BUTTON
# ============================================================

def find_search_button(driver):

    selectors = [

        (
            By.XPATH,
            "//button[normalize-space()='Search']"
        ),

        (
            By.XPATH,
            "//input[@value='Search']"
        ),

        (
            By.XPATH,
            "//*[self::button or self::input]"
            "[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'search')]"
        ),

    ]

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

    return None


def click_search(driver):

    print(
        "  Clicking Search..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        button = find_search_button(
            driver
        )

        if button is not None:

            try:

                if safe_click(
                    driver,
                    button
                ):

                    print(
                        "  ✓ Search clicked."
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(0.3)

    print(
        "  ✗ Search button not found."
    )

    return False


# ============================================================
# ENCOUNTER FIGHT
# ============================================================

def find_encounter_fight(driver):

    try:

        links = driver.find_elements(
            By.XPATH,
            "//a[contains(@class,'inputsubmit') "
            "and normalize-space()='Fight!']"
        )

        for link in links:

            try:

                href = link.get_attribute(
                    "href"
                )

                if (
                    link.is_displayed()
                    and link.is_enabled()
                    and href
                    and "create_battle" in href
                ):

                    return link

            except StaleElementReferenceException:

                continue

    except Exception:

        pass

    return None


def click_encounter_fight(driver):

    print(
        "  Looking for encounter Fight!..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        fight = find_encounter_fight(
            driver
        )

        if fight is not None:

            print(
                "✓ Encounter Fight! found."
            )

            try:

                if safe_click(
                    driver,
                    fight
                ):

                    print(
                        "✓ Encounter Fight! clicked."
                    )

                    wait_for_document_ready(
                        driver
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(0.3)

    return False


# ============================================================
# SEARCH PROGRESS
# ============================================================

def get_search_progress(driver):

    try:

        text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        import re

        matches = re.findall(
            r"\b(\d+)\s*/\s*(\d+)\b",
            text
        )

        if matches:

            current, maximum = matches[0]

            return (
                int(current),
                int(maximum)
            )

    except Exception:

        pass

    return (
        None,
        None
    )


# ============================================================
# MAP OPENING
# ============================================================

def open_map(driver, map_name):

    print()
    print(
        f"Opening map: {map_name}"
    )

    wanted = normalize(
        map_name
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            links = driver.find_elements(
                By.TAG_NAME,
                "a"
            )

            for link in links:

                try:

                    text = normalize(
                        link.text
                    )

                    if (
                        text == wanted
                        and link.is_displayed()
                        and link.is_enabled()
                    ):

                        if safe_click(
                            driver,
                            link
                        ):

                            print(
                                f"  ✓ {map_name} clicked."
                            )

                            wait_for_document_ready(
                                driver
                            )

                            time.sleep(1)

                            print(
                                f"✓ {map_name} loaded."
                            )

                            return True

                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):

                    continue

        except Exception:

            pass

        time.sleep(0.3)

    print(
        f"✗ Map '{map_name}' not found."
    )

    return False


# ============================================================
# HANDLE ENCOUNTER
# ============================================================

def handle_search_encounter(driver):

    if not click_encounter_fight(
        driver
    ):

        print(
            "✗ Could not start encounter."
        )

        return False

    result = capture_encounter(
        driver
    )

    if result:

        print(
            "✓ Encounter capture completed."
        )

        return True

    print(
        "✗ Encounter capture failed."
    )

    return False


# ============================================================
# SEARCH SESSION
# ============================================================

def run_searches(
    driver,
    map_name,
    searches
):

    print()
    print(
        f"Starting {searches} searches "
        f"on {map_name}."
    )

    for search_number in range(
        1,
        searches + 1
    ):

        current, maximum = get_search_progress(
            driver
        )

        if current is not None:

            print()
            print(
                f"Progress: "
                f"{current}/{maximum}"
            )

        print(
            f"  Search "
            f"{search_number}/{searches}"
        )

        # ----------------------------------------------------
        # ONLY ONE Search click per iteration.
        #
        # IMPORTANT:
        # Do not call click_search() twice.
        # ----------------------------------------------------

        if not click_search(
            driver
        ):

            print(
                "✗ Search button disappeared."
            )

            return False

        time.sleep(
            random.uniform(
                SEARCH_DELAY[0],
                SEARCH_DELAY[1]
            )
        )

        # ----------------------------------------------------
        # Check for Pokémon encounter.
        # ----------------------------------------------------

        fight = find_encounter_fight(
            driver
        )

        if fight is not None:

            print(
                "✓ Pokémon encounter detected."
            )

            if not handle_search_encounter(
                driver
            ):

                print(
                    "✗ Encounter handling failed."
                )

                return False

            # Give the Continue navigation time to finish.
            time.sleep(
                random.uniform(
                    1.0,
                    1.5
                )
            )

        # ----------------------------------------------------
        # Continue to the next search.
        # ----------------------------------------------------

    print()
    print(
        f"✓ Finished {searches} searches "
        f"on {map_name}."
    )

    return True


# ============================================================
# ASK WHAT TO DO AFTER SEARCHES
# ============================================================

def search_complete_menu(
    driver,
    map_name
):

    while True:

        print()
        print(
            "=" * 60
        )

        print(
            "SEARCHES COMPLETE"
        )

        print(
            "=" * 60
        )

        print()
        print(
            f"Current map: {map_name}"
        )

        print()
        print(
            "1. Continue searching this map"
        )

        print(
            "2. Return to main menu"
        )

        choice = input(
            "\nChoose: "
        ).strip()

        if choice == "1":

            return "continue"

        if choice == "2":

            return "menu"

        print(
            "✗ Invalid choice."
        )


# ============================================================
# SEARCH MODE
# ============================================================

def search_mode(driver):

    print()
    print(
        "=" * 60
    )

    print(
        "SEARCH MODE"
    )

    print(
        "=" * 60
    )

    for i, map_name in enumerate(
        MAPS,
        1
    ):

        print(
            f"{i:2}. {map_name}"
        )

    while True:

        choice = input(
            "\nChoose starting map number (1-18): "
        ).strip()

        try:

            number = int(
                choice
            )

            if 1 <= number <= len(MAPS):

                break

        except ValueError:

            pass

        print(
            "✗ Please enter a number from "
            f"1 to {len(MAPS)}."
        )

    map_index = number - 1

    # ========================================================
    # IMPORTANT
    #
    # We DO NOT automatically advance to the next map.
    #
    # The user must explicitly choose another map from the
    # main menu.
    # ========================================================

    while True:

        map_name = MAPS[
            map_index
        ]

        if not open_map(
            driver,
            map_name
        ):

            print()
            print(
                "✗ Could not open selected map."
            )

            print(
                "Returning to main menu."
            )

            return

        # ----------------------------------------------------
        # Get current progress.
        # ----------------------------------------------------

        current, maximum = get_search_progress(
            driver
        )

        if current is not None:

            print()
            print(
                f"Current progress: "
                f"{current}/{maximum}"
            )

            remaining = max(
                0,
                maximum - current
            )

            print(
                f"Remaining searches: "
                f"{remaining}"
            )

        else:

            maximum = 500
            remaining = 500

        default_amount = (
            remaining
            if remaining > 0
            else maximum
        )

        # ----------------------------------------------------
        # Ask how many searches.
        # ----------------------------------------------------

        answer = input(
            f"\nHow many searches on "
            f"{map_name}? "
            f"[default {default_amount}]: "
        ).strip()

        if answer:

            try:

                searches = int(
                    answer
                )

            except ValueError:

                print(
                    "✗ Invalid number."
                )

                continue

        else:

            searches = default_amount

        searches = max(
            0,
            searches
        )

        # ----------------------------------------------------
        # Zero searches:
        #
        # Do NOT automatically move to the next map.
        # Return to the search menu/main menu.
        # ----------------------------------------------------

        if searches == 0:

            print()
            print(
                f"No searches selected for "
                f"{map_name}."
            )

            print(
                "Returning to main menu."
            )

            return

        # ----------------------------------------------------
        # Run requested searches.
        # ----------------------------------------------------

        if not run_searches(
            driver,
            map_name,
            searches
        ):

            print()
            print(
                "✗ Search session stopped."
            )

            return

        # ----------------------------------------------------
        # User chooses whether to continue.
        #
        # We NEVER automatically move to MAPS[map_index + 1].
        # ----------------------------------------------------

        action = search_complete_menu(
            driver,
            map_name
        )

        if action == "continue":

            continue

        # ----------------------------------------------------
        # Return to main menu.
        # ----------------------------------------------------

        print()
        print(
            "Returning to main menu."
        )

        return