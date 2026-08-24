import re
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
    wait_for_document_ready,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_BATTLES = 100

# Absolute safety limit for "battle until level".
MAX_LEVEL_BATTLES = 10_000

WAIT_LONG = 20
BATTLE_END_TIMEOUT = 120

BETWEEN_BATTLES_WAIT = (2.0, 3.0)

# After clicking Fight/Attack, wait for the site's JavaScript
# to process the attack.
ATTACK_PROCESSING_WAIT = (0.8, 1.5)

# Polling interval while waiting for battle state changes.
BATTLE_POLL_WAIT = (0.35, 0.65)


# ============================================================
# BATTLE STATES
# ============================================================

RESTART_STATES = {
    "restart",
    "battle again",
    "fight again",
    "restart battle",
}

ATTACK_STATES = {
    "attack",
    "fight",
}


# ============================================================
# OPEN YOUR PROFILE
# ============================================================

def open_profile(driver):

    print("Opening Your Profile...")

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            links = driver.find_elements(
                By.XPATH,
                "//a[starts-with(@href,'/user?id=')]"
            )

            for link in links:

                try:

                    if not link.is_displayed():
                        continue

                    if not link.is_enabled():
                        continue

                    text = normalize(link.text)

                    if "your profile" not in text:
                        continue

                    href = link.get_attribute("href")

                    if not href:
                        continue

                    if "/user?id=" not in href:
                        continue

                    print(
                        f"  ✓ Your Profile found: "
                        f"'{link.text.strip()}'"
                    )

                    if safe_click(driver, link):

                        print(
                            "  ✓ Your Profile clicked."
                        )

                        wait_for_document_ready(driver)

                        time.sleep(
                            random.uniform(0.8, 1.5)
                        )

                        print(
                            "✓ Your Profile opened."
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
        "✗ Your Profile link not found."
    )

    return False


# ============================================================
# OPEN PARTY
# ============================================================

def open_party(driver):

    print("Opening Party...")

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            party_elements = driver.find_elements(
                By.ID,
                "VP_PartyLink1"
            )

            for party in party_elements:

                try:

                    if not party.is_displayed():
                        continue

                    if not party.is_enabled():
                        continue

                    print(
                        "  ✓ Party tab found."
                    )

                    if safe_click(driver, party):

                        print(
                            "  ✓ Party clicked."
                        )

                        time.sleep(
                            random.uniform(0.8, 1.5)
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
        "✗ Party tab not found."
    )

    return False


# ============================================================
# CLICK FIRST POKEMON FIGHT
# ============================================================

def click_first_party_fight(driver):

    print(
        "Looking for first Pokémon Fight..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            fights = driver.find_elements(
                By.XPATH,
                "//a["
                "contains("
                "concat(' ',normalize-space(@class),' '),"
                "' inputsubmit '"
                ")"
                "and normalize-space(.)='Fight'"
                "]"
            )

            valid_fights = []

            for fight in fights:

                try:

                    if not fight.is_displayed():
                        continue

                    if not fight.is_enabled():
                        continue

                    href = fight.get_attribute("href")

                    if not href:
                        continue

                    if "create_battle" not in href:
                        continue

                    valid_fights.append(fight)

                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):

                    continue

            if valid_fights:

                print(
                    f"✓ Found "
                    f"{len(valid_fights)} "
                    f"valid Fight button(s)."
                )

                fight = valid_fights[0]

                print(
                    "  Clicking first Pokémon Fight..."
                )

                if safe_click(driver, fight):

                    print(
                        "  ✓ First Fight clicked."
                    )

                    wait_for_document_ready(driver)

                    time.sleep(
                        random.uniform(0.8, 1.5)
                    )

                    return True

        except Exception:

            pass

        time.sleep(0.3)

    print(
        "✗ First Pokémon Fight not found."
    )

    return False


# ============================================================
# START INITIAL TRAINING BATTLE
# ============================================================

def start_training_battle(driver):

    print()
    print(
        "Starting new training battle..."
    )

    if not open_profile(driver):
        return False

    if not open_party(driver):
        return False

    if not click_first_party_fight(driver):
        return False

    print(
        "✓ Training battle started."
    )

    return True


# ============================================================
# GET BATTLE BUTTON
# ============================================================

def get_battle_button(driver):

    try:

        buttons = driver.find_elements(
            By.ID,
            "battlebtn"
        )

        for button in buttons:

            try:

                if not button.is_displayed():
                    continue

                if not button.is_enabled():
                    continue

                return button

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                continue

    except Exception:

        pass

    return None


# ============================================================
# GET BATTLE BUTTON TEXT
# ============================================================

def get_battle_button_text(driver):

    button = get_battle_button(driver)

    if button is None:
        return ""

    try:

        return normalize(
            button.text
        )

    except (
        StaleElementReferenceException,
        WebDriverException,
    ):

        return ""


# ============================================================
# GET CURRENT LEVEL FROM BATTLE PAGE
# ============================================================

def get_current_battle_level(driver):

    """
    Read the player's current level from the battle page.

    Real Eclipse RPG structure:

        <td class="tnav_battle" align="center" width="100%">
            Level <b>10135</b>
        </td>

    We intentionally read the visible text and extract the
    number following the word "Level".

    This is the authoritative level source for training.
    """

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "td.tnav_battle"
        )

        for element in elements:

            try:

                if not element.is_displayed():
                    continue

                text = element.get_attribute(
                    "textContent"
                ) or ""

                text = normalize(text)

                match = re.search(
                    r"\bLevel\s+([\d,]+)\b",
                    text,
                    re.IGNORECASE
                )

                if match:

                    return int(
                        match.group(1).replace(",", "")
                    )

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                continue

    except WebDriverException:

        pass

    return None


# ============================================================
# WAIT FOR CURRENT LEVEL
# ============================================================

def wait_for_current_level(
    driver,
    timeout=WAIT_LONG,
):

    start = time.time()

    while time.time() - start < timeout:

        level = get_current_battle_level(driver)

        if level is not None:

            return level

        time.sleep(0.3)

    return None


# ============================================================
# GET BATTLE RESULT LEVEL GAIN
# ============================================================

def get_battle_level_gain(driver):

    """
    Read the level gain from Battle Results.

    Example:

        +30 levels
        Lv. 10,045
    """

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "td.tnav_battle"
        )

        for element in elements:

            try:

                text = element.get_attribute(
                    "textContent"
                ) or ""

                text = normalize(text)

                match = re.search(
                    r"\+([\d,]+)\s+levels?",
                    text,
                    re.IGNORECASE
                )

                if match:

                    return int(
                        match.group(1).replace(",", "")
                    )

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                continue

    except WebDriverException:

        pass

    return None


# ============================================================
# GET EXP GAIN
# ============================================================

def get_battle_exp_gain(driver):

    """
    Read:

        +16209694 EXP

    from Battle Results.
    """

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "td.tnav_battle"
        )

        for element in elements:

            try:

                text = element.get_attribute(
                    "textContent"
                ) or ""

                text = normalize(text)

                match = re.search(
                    r"\+([\d,]+)\s+EXP\b",
                    text,
                    re.IGNORECASE
                )

                if match:

                    return int(
                        match.group(1).replace(",", "")
                    )

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                continue

    except WebDriverException:

        pass

    return None


# ============================================================
# CHECK FOR BATTLE COMPLETION
# ============================================================

def battle_has_ended(driver):

    state = get_battle_button_text(driver)

    return state in RESTART_STATES


# ============================================================
# WAIT FOR ATTACK PROCESSING
# ============================================================

def wait_for_attack_processing(driver):

    """
    Prevent duplicate attacks.

    The site can temporarily leave #battlebtn showing
    Fight/Attack after the click has already been accepted.
    """

    start = time.time()

    initial_state = get_battle_button_text(driver)

    while time.time() - start < 8:

        current_state = get_battle_button_text(driver)

        if not current_state:

            return True

        if current_state != initial_state:

            return True

        time.sleep(
            random.uniform(
                0.25,
                0.45
            )
        )

    return True


# ============================================================
# CLICK ATTACK / FIGHT
# ============================================================

def click_attack(driver):

    button = get_battle_button(driver)

    if button is None:

        return False

    try:

        state = normalize(
            button.text
        )

        if state not in ATTACK_STATES:

            return False

        print(
            f"  Clicking "
            f"'{button.text.strip()}'..."
        )

        if safe_click(driver, button):

            print(
                "  ✓ Attack/Fight clicked."
            )

            time.sleep(
                random.uniform(
                    ATTACK_PROCESSING_WAIT[0],
                    ATTACK_PROCESSING_WAIT[1]
                )
            )

            wait_for_attack_processing(
                driver
            )

            return True

    except (
        StaleElementReferenceException,
        WebDriverException,
    ):

        pass

    return False


# ============================================================
# WAIT FOR CURRENT BATTLE TO FINISH
# ============================================================

def wait_for_battle_to_finish(driver):

    print(
        "  Waiting for battle..."
    )

    battle_start = time.time()

    last_state = None

    while (
        time.time() - battle_start
        < BATTLE_END_TIMEOUT
    ):

        button = get_battle_button(driver)

        if button is None:

            time.sleep(0.4)

            continue

        try:

            state = normalize(
                button.text
            )

        except (
            StaleElementReferenceException,
            WebDriverException,
        ):

            continue

        if state != last_state:

            print(
                f"  Battle button state: "
                f"'{state}'"
            )

            last_state = state

        if state in RESTART_STATES:

            return True

        if state in ATTACK_STATES:

            if not click_attack(driver):

                time.sleep(
                    random.uniform(
                        0.4,
                        0.7
                    )
                )

            continue

        time.sleep(
            random.uniform(
                BATTLE_POLL_WAIT[0],
                BATTLE_POLL_WAIT[1]
            )
        )

    return False


# ============================================================
# CLICK RESTART / BATTLE AGAIN / FIGHT AGAIN
# ============================================================

def click_restart_battle(driver):

    print(
        "  Looking for next-battle button..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        button = get_battle_button(driver)

        if button is not None:

            try:

                state = normalize(
                    button.text
                )

                if state in RESTART_STATES:

                    print(
                        f"  ✓ Next-battle button found: "
                        f"'{button.text.strip()}'"
                    )

                    if safe_click(
                        driver,
                        button
                    ):

                        print(
                            "  ✓ Next battle button clicked."
                        )

                        time.sleep(
                            random.uniform(
                                0.8,
                                1.5
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
        "  ✗ Restart/Battle Again/Fight Again "
        "button not found."
    )

    return False


# ============================================================
# DISPLAY TRAINING PROGRESS
# ============================================================

def print_training_progress(
    current_level,
    target_level,
    last_level_gain=None,
    total_exp_gained=0,
):

    print()

    if current_level is None:

        print(
            f"Progress: "
            f"Unknown/{target_level:,}"
        )

        return

    remaining = max(
        0,
        target_level - current_level
    )

    print(
        f"Progress: "
        f"{current_level:,}/"
        f"{target_level:,}"
    )

    print(
        f"Levels remaining: "
        f"{remaining:,}"
    )

    if last_level_gain is not None:

        print(
            f"Last battle: "
            f"+{last_level_gain:,} levels"
        )

    if total_exp_gained:

        print(
            f"Total EXP gained: "
            f"{total_exp_gained:,}"
        )


# ============================================================
# BATTLE UNTIL TARGET LEVEL
# ============================================================

def train_until_level(
    driver,
    target_level,
    max_battles=MAX_LEVEL_BATTLES,
):

    print()
    print("=" * 60)
    print("TRAIN UNTIL LEVEL")
    print("=" * 60)
    print()

    print(
        f"Target level: {target_level:,}"
    )

    print(
        f"Safety limit: {max_battles:,} battles"
    )

    # --------------------------------------------------------
    # Validate target.
    # --------------------------------------------------------

    if target_level <= 0:

        print(
            "✗ Target level must be greater than 0."
        )

        return {
            "battles": 0,
            "current_level": None,
            "target_level": target_level,
            "exp_gained": 0,
        }

    # --------------------------------------------------------
    # Start initial battle.
    # --------------------------------------------------------

    if not start_training_battle(driver):

        print()
        print(
            "✗ Could not start training battle."
        )

        return {
            "battles": 0,
            "current_level": None,
            "target_level": target_level,
            "exp_gained": 0,
        }

    # --------------------------------------------------------
    # Read the actual level from the battle page.
    # --------------------------------------------------------

    current_level = wait_for_current_level(
        driver
    )

    if current_level is None:

        print()
        print(
            "✗ Could not determine current level."
        )

        return {
            "battles": 0,
            "current_level": None,
            "target_level": target_level,
            "exp_gained": 0,
        }

    print()
    print(
        f"✓ Current level: "
        f"{current_level:,}"
    )

    # --------------------------------------------------------
    # Already at target.
    # --------------------------------------------------------

    if current_level >= target_level:

        print()
        print(
            f"✓ Target level already reached."
        )

        return {
            "battles": 0,
            "current_level": current_level,
            "target_level": target_level,
            "exp_gained": 0,
        }

    battle_count = 0
    total_exp_gained = 0
    last_level_gain = None

    # ========================================================
    # MAIN LEVEL TRAINING LOOP
    # ========================================================

    while battle_count < max_battles:

        print_training_progress(
            current_level,
            target_level,
            last_level_gain,
            total_exp_gained,
        )

        print()
        print(
            f"=== Battle "
            f"{battle_count + 1}/"
            f"{max_battles:,} safety limit ==="
        )

        # ----------------------------------------------------
        # Complete current battle.
        # ----------------------------------------------------

        if not wait_for_battle_to_finish(driver):

            print()
            print(
                "✗ Battle timed out."
            )

            return {
                "battles": battle_count,
                "current_level": current_level,
                "target_level": target_level,
                "exp_gained": total_exp_gained,
            }

        print(
            "  ✓ Battle finished."
        )

        # ----------------------------------------------------
        # Read battle results BEFORE clicking Restart Battle.
        #
        # The result page contains:
        #
        # +30 levels
        # +16209694 EXP
        #
        # and the current level.
        # ----------------------------------------------------

        level_gain = get_battle_level_gain(
            driver
        )

        exp_gain = get_battle_exp_gain(
            driver
        )

        if level_gain is not None:

            last_level_gain = level_gain

            print(
                f"  Levels gained: "
                f"+{level_gain:,}"
            )

        if exp_gain is not None:

            total_exp_gained += exp_gain

            print(
                f"  EXP gained: "
                f"+{exp_gain:,}"
            )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Read the authoritative level from:
        #
        # <td class="tnav_battle">
        #     Level <b>10135</b>
        # </td>
        #
        # This happens AFTER the battle result has been
        # processed.
        # ----------------------------------------------------

        updated_level = wait_for_current_level(
            driver,
            timeout=10,
        )

        if updated_level is not None:

            current_level = updated_level

            print(
                f"  Current level: "
                f"{current_level:,}/"
                f"{target_level:,}"
            )

        else:

            # ------------------------------------------------
            # If the level isn't readable, use the known level
            # gain as a fallback rather than falsely claiming
            # the old level is current.
            # ------------------------------------------------

            if (
                current_level is not None
                and level_gain is not None
            ):

                current_level += level_gain

                print(
                    f"  Current level estimated from "
                    f"battle result: "
                    f"{current_level:,}/"
                    f"{target_level:,}"
                )

            else:

                print(
                    "  ⚠ Could not determine updated level."
                )

        battle_count += 1

        print()
        print(
            f"✓ Battle "
            f"{battle_count} complete!"
        )

        # ----------------------------------------------------
        # TARGET REACHED
        #
        # Check immediately BEFORE starting another battle.
        # ----------------------------------------------------

        if (
            current_level is not None
            and current_level >= target_level
        ):

            print()
            print(
                "=" * 60
            )

            print(
                f"✓ TARGET LEVEL REACHED!"
            )

            print(
                f"  Current level: "
                f"{current_level:,}"
            )

            print(
                f"  Target level:  "
                f"{target_level:,}"
            )

            print(
                f"  Battles completed: "
                f"{battle_count}"
            )

            print(
                f"  Total EXP gained: "
                f"{total_exp_gained:,}"
            )

            print(
                "=" * 60
            )

            return {
                "battles": battle_count,
                "current_level": current_level,
                "target_level": target_level,
                "exp_gained": total_exp_gained,
            }

        # ----------------------------------------------------
        # Safety limit reached.
        # ----------------------------------------------------

        if battle_count >= max_battles:

            print()
            print(
                "⚠ Training stopped because the "
                "battle safety limit was reached."
            )

            return {
                "battles": battle_count,
                "current_level": current_level,
                "target_level": target_level,
                "exp_gained": total_exp_gained,
            }

        # ----------------------------------------------------
        # Start next battle.
        # ----------------------------------------------------

        print(
            "  Preparing next battle..."
        )

        if not click_restart_battle(driver):

            print()
            print(
                "✗ Could not start next battle."
            )

            return {
                "battles": battle_count,
                "current_level": current_level,
                "target_level": target_level,
                "exp_gained": total_exp_gained,
            }

        print(
            "  ✓ Next battle started."
        )

        time.sleep(
            random.uniform(
                BETWEEN_BATTLES_WAIT[0],
                BETWEEN_BATTLES_WAIT[1]
            )
        )

    return {
        "battles": battle_count,
        "current_level": current_level,
        "target_level": target_level,
        "exp_gained": total_exp_gained,
    }


# ============================================================
# TRAIN FOR X BATTLES
# ============================================================

def train_for_battles(
    driver,
    max_battles=MAX_BATTLES,
):

    print()
    print("=" * 60)
    print("TRAIN MODE")
    print("=" * 60)

    print()
    print(
        f"Battle limit: {max_battles:,}"
    )

    # --------------------------------------------------------
    # Start first battle.
    # --------------------------------------------------------

    if not start_training_battle(driver):

        print()
        print(
            "✗ Could not start training battle."
        )

        return 0

    battle_count = 0

    # ========================================================
    # BATTLE LOOP
    # ========================================================

    while battle_count < max_battles:

        print()
        print(
            f"=== Battle "
            f"{battle_count + 1}/"
            f"{max_battles:,} ==="
        )

        # ----------------------------------------------------
        # Fight current battle.
        # ----------------------------------------------------

        if not wait_for_battle_to_finish(driver):

            print()
            print(
                "✗ Battle timed out."
            )

            return battle_count

        print(
            "  ✓ Battle finished."
        )

        # ----------------------------------------------------
        # Collect battle statistics.
        # ----------------------------------------------------

        level_gain = get_battle_level_gain(
            driver
        )

        exp_gain = get_battle_exp_gain(
            driver
        )

        battle_count += 1

        print()
        print(
            f"✓ Battle "
            f"{battle_count} complete!"
        )

        if level_gain is not None:

            print(
                f"  Levels gained: "
                f"+{level_gain:,}"
            )

        if exp_gain is not None:

            print(
                f"  EXP gained: "
                f"+{exp_gain:,}"
            )

        # ----------------------------------------------------
        # Requested number completed.
        # ----------------------------------------------------

        if battle_count >= max_battles:

            break

        # ----------------------------------------------------
        # Restart the battle directly.
        # ----------------------------------------------------

        print(
            "  Preparing next battle..."
        )

        if not click_restart_battle(driver):

            print()
            print(
                "✗ Could not start next battle."
            )

            return battle_count

        print(
            "  ✓ Next battle started."
        )

        time.sleep(
            random.uniform(
                BETWEEN_BATTLES_WAIT[0],
                BETWEEN_BATTLES_WAIT[1]
            )
        )

    print()
    print("=" * 60)

    print(
        f"✓ Completed "
        f"{battle_count:,} battles."
    )

    print(
        "=" * 60
    )

    return battle_count


# ============================================================
# MAIN TRAINING ENTRY POINT
# ============================================================

def train_mode(
    driver,
    max_battles=MAX_BATTLES,
    target_level=None,
):

    """
    Main training entry point.

    Two modes are supported:

        train_mode(driver, max_battles=100)
            -> Battle for a fixed number of battles.

        train_mode(
            driver,
            max_battles=10000,
            target_level=10235
        )
            -> Battle until the Pokémon reaches level 10235,
               with the battle count acting as a safety limit.
    """

    # --------------------------------------------------------
    # LEVEL TARGET MODE
    # --------------------------------------------------------

    if target_level is not None:

        return train_until_level(
            driver,
            target_level=target_level,
            max_battles=max_battles,
        )

    # --------------------------------------------------------
    # NORMAL BATTLE COUNT MODE
    # --------------------------------------------------------

    return train_for_battles(
        driver,
        max_battles=max_battles,
    )