import time
import random
import re
from collections import defaultdict

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

MINE_POLL_WAIT = 0.15

MINE_RESULT_MIN_WAIT = 0.35
MINE_RESULT_MAX_WAIT = 0.75

MINE_BUTTON_WAIT = min(
    max(float(WAIT_LONG), 3.0),
    10.0,
)

MINE_RESULT_WAIT = min(
    max(float(WAIT_LONG), 3.0),
    10.0,
)


# ============================================================
# SESSION STATISTICS
# ============================================================

def create_mining_stats():
    return {
        "mines": 0,
        "encounters": 0,
        "captured": 0,
        "capture_failed": 0,
        "mining_xp": 0,
        "pickaxe_xp": 0.0,
        "resources": defaultdict(int),
        "items": defaultdict(int),
        "rocks": defaultdict(int),
        "started": time.time(),
        "area_completed": False,
    }


# ============================================================
# MINE BUTTON
# ============================================================

def find_mine_button(
    driver,
    require_enabled=True,
):
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
# PAGE STATE
# ============================================================

def _body_text(driver):

    try:

        return driver.find_element(
            By.TAG_NAME,
            "body",
        ).text.lower()

    except Exception:

        return ""


def area_cleared_detected(driver):

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


def encounter_detected(driver):

    try:

        return bool(
            find_encounter_fight(
                driver
            )
        )

    except Exception:

        return False


# ============================================================
# MINING RESULT PARSING
# ============================================================

def get_mining_result(driver):

    try:

        result = driver.find_element(
            By.ID,
            "M_Result",
        )

        return result

    except Exception:

        return None


def parse_mining_result(
    driver,
    stats,
):
    """
    Read Eclipse's #M_Result and record:

        - Resources
        - Mining XP
        - Pickaxe XP
        - Items
        - Rocks

    Example Eclipse HTML:

        <img alt="Sapphire">
        <b>+2</b>
        <div>Sapphire</div>

        You gained <b>15</b> mining experience.

        <b>+0.6</b> Pickaxe XP

        You have obtained a(n)
        <b>Great Ball</b> (x1).

        You found 6
        <a>Green</a> rocks.
    """

    result = get_mining_result(
        driver
    )

    if result is None:
        return False

    try:

        html = result.get_attribute(
            "innerHTML"
        )

        text = result.text

    except Exception:

        return False

    if not html:
        return False

    # --------------------------------------------------------
    # RESOURCE
    #
    # Eclipse identifies the resource using the image alt:
    #
    # <img ... alt="Sapphire">
    # <b>+2</b>
    # --------------------------------------------------------

    resource_images = re.findall(
        r'<img[^>]+alt=["\']([^"\']+)["\'][^>]*>',
        html,
        flags=re.IGNORECASE,
    )

    for resource in resource_images:

        resource = resource.strip()

        if not resource:
            continue

        # Ignore unrelated images such as rocks.
        if resource.lower() in {
            "great ball",
            "ultra ball",
            "poke ball",
            "pokeball",
            "pickaxe",
        }:
            continue

        # Look for the +amount near this resource image.
        match = re.search(
            r'<img[^>]+alt=["\']'
            + re.escape(resource)
            + r'["\'][^>]*>'
            r'.{0,500}?'
            r'<b[^>]*>\s*\+?([\d,.]+)\s*</b>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if match:

            try:

                amount = int(
                    float(
                        match.group(1).replace(
                            ",",
                            "",
                        )
                    )
                )

                stats["resources"][
                    resource
                ] += amount

            except ValueError:
                pass

    # --------------------------------------------------------
    # MINING XP
    # --------------------------------------------------------

    match = re.search(
        r"You gained\s+"
        r"<b[^>]*>\s*([\d,.]+)\s*</b>"
        r"\s*mining experience",
        html,
        flags=re.IGNORECASE,
    )

    if match:

        try:

            stats["mining_xp"] += int(
                float(
                    match.group(1).replace(
                        ",",
                        "",
                    )
                )
            )

        except ValueError:
            pass

    # --------------------------------------------------------
    # PICKAXE XP
    # --------------------------------------------------------

    match = re.search(
        r"<b[^>]*>\s*\+?([\d,.]+)\s*</b>"
        r"\s*Pickaxe XP",
        html,
        flags=re.IGNORECASE,
    )

    if match:

        try:

            stats["pickaxe_xp"] += float(
                match.group(1).replace(
                    ",",
                    "",
                )
            )

        except ValueError:
            pass

    # --------------------------------------------------------
    # ITEMS
    #
    # Example:
    #
    # You have obtained a(n)
    # <b>Great Ball</b> (x1).
    # --------------------------------------------------------

    item_matches = re.findall(
        r"You have obtained\s+"
        r"a(?:n)?\s+"
        r"<b[^>]*>(.*?)</b>"
        r"\s*\(x\s*([\d,.]+)\)",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    for item, amount in item_matches:

        item = re.sub(
            r"<[^>]+>",
            "",
            item,
        ).strip()

        try:

            amount = int(
                float(
                    amount.replace(
                        ",",
                        "",
                    )
                )
            )

        except ValueError:

            continue

        if item:
            stats["items"][item] += amount

    # --------------------------------------------------------
    # ROCKS
    #
    # Example:
    #
    # You found 6 <a>Green</a> rocks.
    # --------------------------------------------------------

    rock_matches = re.findall(
        r"You found\s+"
        r"([\d,.]+)\s+"
        r"<a[^>]*>(.*?)</a>"
        r"\s+rocks?",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    for amount, rock in rock_matches:

        rock = re.sub(
            r"<[^>]+>",
            "",
            rock,
        ).strip()

        try:

            amount = int(
                float(
                    amount.replace(
                        ",",
                        "",
                    )
                )
            )

        except ValueError:

            continue

        if rock:
            stats["rocks"][rock] += amount

    return True


# ============================================================
# MINE CLICK
# ============================================================

def click_mine(driver):

    end_time = (
        time.time()
        + MINE_BUTTON_WAIT
    )

    disabled_seen = False

    while time.time() < end_time:

        if encounter_detected(
            driver
        ):
            return False

        if area_cleared_detected(
            driver
        ):
            return False

        element = find_mine_button(
            driver,
            require_enabled=True,
        )

        if element:

            try:

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

            disabled_element = find_mine_button(
                driver,
                require_enabled=False,
            )

            if disabled_element and not disabled_seen:

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

def wait_for_mining_result(driver):

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

        result = get_mining_result(
            driver
        )

        if result:

            return True

        if find_mine_button(
            driver,
            require_enabled=True,
        ):

            return True

        time.sleep(
            MINE_POLL_WAIT
        )

    return True


# ============================================================
# AREA COMPLETION
# ============================================================

def handle_area_cleared(driver):

    if not area_cleared_detected(
        driver
    ):
        return False

    print(
        "⚠ Mining area completion detected."
    )

    selectors = [
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

    for by, selector in selectors:

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

def click_mining_continue(driver):

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

                            while time.time() < ready_end:

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
    stats,
):

    if not find_encounter_fight(
        driver
    ):

        return False

    stats["encounters"] += 1

    print(
        "\n  Pokémon encounter while mining!"
    )

    # --------------------------------------------------------
    # Mine-only mode
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
    # Enter encounter
    # --------------------------------------------------------

    if not click_encounter_fight(
        driver
    ):

        return False

    # capture.py contains the current Use Another fixes.
    if capture_encounter(
        driver
    ):

        stats["captured"] += 1

        print(
            "  ✓ Mining Pokémon captured."
        )

        if not click_mining_continue(
            driver
        ):

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

    stats["capture_failed"] += 1

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

        print(
            "  ✓ Returned to mining."
        )

        return True

    except Exception:

        return False


# ============================================================
# INPUT HELPERS
# ============================================================

def get_positive_integer(prompt):

    while True:

        try:

            value = int(
                input(prompt).strip()
            )

            if value > 0:
                return value

        except ValueError:
            pass

        print(
            "  ✗ Please enter a positive whole number."
        )


def parse_duration(value):

    """
    Supports:

        30
        30s
        5m
        2h
        1h 30m
        90m
        2h 15m 30s

    A number without a suffix is treated as minutes.
    """

    value = value.strip().lower()

    if not value:
        return None

    total_seconds = 0.0

    matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes|s|sec|secs|second|seconds)?",
        value,
    )

    if not matches:
        return None

    consumed = "".join(
        number + (unit or "")
        for number, unit in matches
    )

    normalized = re.sub(
        r"\s+",
        "",
        value,
    )

    # Remove separators that don't affect parsing.
    normalized = normalized.replace(
        ",",
        "",
    )

    # Simple plain number = minutes.
    if re.fullmatch(
        r"\d+(?:\.\d+)?",
        normalized,
    ):

        return float(normalized) * 60

    for number, unit in matches:

        amount = float(number)

        if not unit:
            # Unsuffixed values inside a compound duration
            # are interpreted as minutes.
            total_seconds += (
                amount * 60
            )

        elif unit in {
            "h",
            "hr",
            "hrs",
            "hour",
            "hours",
        }:

            total_seconds += (
                amount * 3600
            )

        elif unit in {
            "m",
            "min",
            "mins",
            "minute",
            "minutes",
        }:

            total_seconds += (
                amount * 60
            )

        else:

            total_seconds += amount

    return total_seconds if total_seconds > 0 else None


def format_duration(seconds):

    seconds = max(
        0,
        int(seconds),
    )

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    secs = seconds % 60

    if hours:
        return (
            f"{hours}h "
            f"{minutes:02d}m "
            f"{secs:02d}s"
        )

    return (
        f"{minutes}m "
        f"{secs:02d}s"
    )


# ============================================================
# MINING RESULTS
# ============================================================

def print_mining_results(
    stats,
    mode_description,
):

    elapsed = (
        time.time()
        - stats["started"]
    )

    print()
    print(
        "=" * 60
    )
    print(
        "MINING COMPLETE"
    )
    print(
        "=" * 60
    )
    print()

    print(
        f"Mining mode       : {mode_description}"
    )

    print(
        f"Mines completed   : {stats['mines']}"
    )

    print(
        f"Time elapsed      : {format_duration(elapsed)}"
    )

    print(
        f"Area completed    : "
        f"{'Yes' if stats['area_completed'] else 'No'}"
    )

    print()

    # --------------------------------------------------------
    # Resources
    # --------------------------------------------------------

    print(
        "RESOURCES GATHERED"
    )

    print(
        "-" * 60
    )

    if stats["resources"]:

        for name, amount in sorted(
            stats["resources"].items()
        ):

            print(
                f"{name:<25}: {amount:,}"
            )

    else:

        print(
            "None"
        )

    print()

    # --------------------------------------------------------
    # Items
    # --------------------------------------------------------

    print(
        "ITEMS OBTAINED"
    )

    print(
        "-" * 60
    )

    if stats["items"]:

        for name, amount in sorted(
            stats["items"].items()
        ):

            print(
                f"{name:<25}: {amount:,}"
            )

    else:

        print(
            "None"
        )

    print()

    # --------------------------------------------------------
    # Rocks
    # --------------------------------------------------------

    print(
        "ROCKS FOUND"
    )

    print(
        "-" * 60
    )

    if stats["rocks"]:

        for name, amount in sorted(
            stats["rocks"].items()
        ):

            print(
                f"{name + ' rocks':<25}: {amount:,}"
            )

    else:

        print(
            "None"
        )

    print()

    # --------------------------------------------------------
    # XP
    # --------------------------------------------------------

    print(
        "EXPERIENCE"
    )

    print(
        "-" * 60
    )

    print(
        f"{'Mining XP':<25}: "
        f"{stats['mining_xp']:,}"
    )

    print(
        f"{'Pickaxe XP':<25}: "
        f"{stats['pickaxe_xp']:,.2f}"
    )

    print()

    # --------------------------------------------------------
    # Pokémon
    # --------------------------------------------------------

    print(
        "POKÉMON"
    )

    print(
        "-" * 60
    )

    print(
        f"{'Encounters':<25}: "
        f"{stats['encounters']:,}"
    )

    print(
        f"{'Captured':<25}: "
        f"{stats['captured']:,}"
    )

    print(
        f"{'Capture failures':<25}: "
        f"{stats['capture_failed']:,}"
    )

    print()

    print(
        "=" * 60
    )


# ============================================================
# MINER MODE
# ============================================================

def miner_mode(driver):

    print()
    print(
        "=" * 60
    )
    print(
        "A-MINER"
    )
    print(
        "=" * 60
    )

    print()
    print(
        "1. Mine and catch Pokémon"
    )
    print(
        "2. Mine only"
    )
    print(
        "3. Mine a specific amount"
    )
    print(
        "4. Mine for a specific amount of time"
    )
    print(
        "5. Mine until area is completed"
    )
    print(
        "6. Back"
    )

    print()

    mode = input(
        "Choose: "
    ).strip()

    if mode == "6":
        return

    if mode not in {
        "1",
        "2",
        "3",
        "4",
        "5",
    }:

        print(
            "✗ Invalid choice."
        )

        return

    # --------------------------------------------------------
    # Pokémon option
    #
    # Modes 1, 3, 4 and 5 catch Pokémon.
    # Mode 2 is mine-only.
    # --------------------------------------------------------

    catch_pokemon = (
        mode != "2"
    )

    target_mines = None
    target_seconds = None

    if mode == "3":

        target_mines = get_positive_integer(
            "\nHow many mines? "
        )

        mode_description = (
            f"{target_mines:,} mines"
        )

    elif mode == "4":

        while True:

            duration_text = input(
                "\nHow long would you like to mine? "
                "(examples: 30s, 5m, 2h, 1h 30m): "
            )

            target_seconds = parse_duration(
                duration_text
            )

            if target_seconds:

                break

            print(
                "  ✗ Invalid duration."
            )

        mode_description = (
            f"{duration_text.strip()}"
        )

    elif mode == "5":

        mode_description = (
            "Until area completed"
        )

    elif mode == "2":

        mode_description = (
            "Continuous mining"
        )

    else:

        mode_description = (
            "Continuous mining + Pokémon"
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

    stats = create_mining_stats()

    print()
    print(
        "=" * 60
    )
    print(
        "MINING STARTED"
    )
    print(
        "=" * 60
    )

    print(
        f"Mode              : {mode_description}"
    )

    print(
        f"Pokémon catching  : "
        f"{'Yes' if catch_pokemon else 'No'}"
    )

    if target_mines:

        print(
            f"Target mines      : "
            f"{target_mines:,}"
        )

    if target_seconds:

        print(
            f"Duration          : "
            f"{format_duration(target_seconds)}"
        )

    print()

    # --------------------------------------------------------
    # Main mining loop.
    # --------------------------------------------------------

    while True:

        # ----------------------------------------------------
        # Time limit.
        # ----------------------------------------------------

        if target_seconds is not None:

            elapsed = (
                time.time()
                - stats["started"]
            )

            if elapsed >= target_seconds:

                print()
                print(
                    "✓ Mining time limit reached."
                )

                break

        # ----------------------------------------------------
        # Mine count limit.
        #
        # This counts actual successful Mine clicks, NOT loop
        # iterations.
        # ----------------------------------------------------

        if (
            target_mines is not None
            and stats["mines"] >= target_mines
        ):

            print()
            print(
                "✓ Mining target reached."
            )

            break

        # ----------------------------------------------------
        # Existing encounter.
        # ----------------------------------------------------

        if encounter_detected(
            driver
        ):

            if not handle_mining_encounter(
                driver,
                catch_pokemon,
                stats,
            ):

                print(
                    "✗ Mining encounter handling failed."
                )

                break

            continue

        # ----------------------------------------------------
        # Area completion.
        # ----------------------------------------------------

        if handle_area_cleared(
            driver
        ):

            stats["area_completed"] = True

            print(
                "✓ Mining area completed."
            )

            break

        # ----------------------------------------------------
        # Click Mine.
        # ----------------------------------------------------

        mine_clicked = click_mine(
            driver
        )

        # ----------------------------------------------------
        # If Mine wasn't clicked, determine why.
        # ----------------------------------------------------

        if not mine_clicked:

            if encounter_detected(
                driver
            ):

                if not handle_mining_encounter(
                    driver,
                    catch_pokemon,
                    stats,
                ):

                    print(
                        "✗ Mining encounter handling failed."
                    )

                    break

                continue

            if handle_area_cleared(
                driver
            ):

                stats["area_completed"] = True

                print(
                    "✓ Mining area completed."
                )

                break

            # Give a temporarily disabled button another
            # opportunity rather than treating it as fatal.
            disabled_button = find_mine_button(
                driver,
                require_enabled=False,
            )

            if disabled_button:

                time.sleep(
                    MINE_POLL_WAIT
                )

                continue

            time.sleep(
                MINE_POLL_WAIT
            )

            continue

        # ----------------------------------------------------
        # A real Mine action occurred.
        # ----------------------------------------------------

        stats["mines"] += 1

        if target_mines:

            print(
                f"  Mine progress: "
                f"{stats['mines']}/{target_mines}"
            )

        # ----------------------------------------------------
        # Wait for Eclipse's result.
        # ----------------------------------------------------

        wait_for_mining_result(
            driver
        )

        # ----------------------------------------------------
        # Parse #M_Result.
        # ----------------------------------------------------

        parse_mining_result(
            driver,
            stats,
        )

        # ----------------------------------------------------
        # Encounter after mining result.
        # ----------------------------------------------------

        if encounter_detected(
            driver
        ):

            if not handle_mining_encounter(
                driver,
                catch_pokemon,
                stats,
            ):

                print(
                    "✗ Mining encounter handling failed."
                )

                break

            continue

        # ----------------------------------------------------
        # Area completion after mining result.
        # ----------------------------------------------------

        if handle_area_cleared(
            driver
        ):

            stats["area_completed"] = True

            print(
                "✓ Mining area completed."
            )

            break

        print(
            "  ✓ Mining result processed."
        )

        # ----------------------------------------------------
        # Short pause before next mine.
        # ----------------------------------------------------

        time.sleep(
            random.uniform(
                0.15,
                0.35,
            )
        )

    # --------------------------------------------------------
    # Final session report.
    # --------------------------------------------------------

    print_mining_results(
        stats,
        mode_description,
    )