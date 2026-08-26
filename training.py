import re
import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
    NoSuchElementException,
)

from utils import (
    safe_click,
    normalize,
    wait_for_document_ready,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_BATTLES = 1000

# Absolute safety limit for "battle until level".
MAX_LEVEL_BATTLES = 10_000


# ============================================================
# BATTLE DIFFICULTY
# ============================================================
#
# Real site structure (from Ideas.md's HTML evidence):
#
#   <select name="B_Difficulty" class="formselect"
#           onchange="battle_difficulty(this.value);">
#     <option value="veryeasy">Very Easy Mode</option>
#     <option value="easy">Easy Mode</option>
#     <option value="normal">Normal Mode</option>
#     <option value="hard">Hard Mode</option>
#     <option value="veryhard" id="B_DifficultySelected" selected>
#         Very Hard Mode
#     </option>
#   </select>
#
# Higher difficulty = harder battles but more EXP/Platinum Coins.

DIFFICULTY_VALUES = [
    "veryeasy",
    "easy",
    "normal",
    "hard",
    "veryhard",
]

DIFFICULTY_LABELS = {
    "veryeasy": "Very Easy Mode",
    "easy": "Easy Mode",
    "normal": "Normal Mode",
    "hard": "Hard Mode",
    "veryhard": "Very Hard Mode",
}


def get_battle_difficulty(driver):
    """
    Read the currently selected battle difficulty value
    (e.g. "veryhard"), or None if the difficulty selector isn't
    present on the current page.
    """

    try:

        select_element = driver.find_element(
            By.NAME,
            "B_Difficulty",
        )

        select = Select(select_element)

        selected = select.first_selected_option

        return selected.get_attribute("value")

    except (
        NoSuchElementException,
        StaleElementReferenceException,
        WebDriverException,
    ):

        return None


def set_battle_difficulty(driver, difficulty):
    """
    Set the battle difficulty via the site's own B_Difficulty
    select (fires the same battle_difficulty() JS the site
    itself uses). Returns True on success.

    difficulty must be one of DIFFICULTY_VALUES.
    """

    if difficulty not in DIFFICULTY_VALUES:

        print(
            f"  ✗ Unknown difficulty: {difficulty}"
        )

        return False

    try:

        select_element = driver.find_element(
            By.NAME,
            "B_Difficulty",
        )

        select = Select(select_element)

        select.select_by_value(difficulty)

        print(
            f"  ✓ Battle difficulty set to "
            f"{DIFFICULTY_LABELS.get(difficulty, difficulty)}."
        )

        time.sleep(
            random.uniform(0.5, 1.0)
        )

        return True

    except (
        NoSuchElementException,
        StaleElementReferenceException,
        WebDriverException,
    ) as error:

        print(
            f"  ✗ Could not set battle difficulty: {error}"
        )

        return False

WAIT_LONG = 10
BATTLE_END_TIMEOUT = 60

BETWEEN_BATTLES_WAIT = (0.5, 0.8)
ATTACK_PROCESSING_WAIT = (0.2, 0.4)
BATTLE_POLL_WAIT = (0.10, 0.20)

# Max time to confirm an attack click was actually processed by
# the site (the battle button briefly shows stale text before
# updating). Polls at BATTLE_POLL_WAIT intervals, same as the
# rest of the battle loop - this used to have its own separate,
# slower hardcoded poll interval.
ATTACK_CONFIRM_TIMEOUT = 4


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

        <td class="tnav_battle"
            align="center"
            width="100%">
            Level <b>10135</b>
        </td>

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
    Read the level gain from the Battle Results.

    Example:

        +30 levels
        Lv. 10,255
    """

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "table.outcome"
        )

        for table in elements:

            try:

                if not table.is_displayed():
                    continue

                rows = table.find_elements(
                    By.CSS_SELECTOR,
                    "tr"
                )

                for row in rows:

                    try:

                        text = row.get_attribute(
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
                                match.group(1).replace(
                                    ",",
                                    ""
                                )
                            )

                    except (
                        StaleElementReferenceException,
                        WebDriverException,
                    ):

                        continue

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
    Read EXP from the Battle Results table.

    Real Eclipse RPG structure:

        <table class="outcome">
            ...
            <tr>
                <td class="left_s">
                    +<b>16549731</b> EXP
                </td>
                <td class="right_s">
                    0/543,434
                </td>
            </tr>
        </table>

    Returns the integer EXP gain, or None if it cannot
    be found.
    """

    try:

        outcome_tables = driver.find_elements(
            By.CSS_SELECTOR,
            "table.outcome"
        )

        for table in outcome_tables:

            try:

                if not table.is_displayed():
                    continue

                rows = table.find_elements(
                    By.CSS_SELECTOR,
                    "tr"
                )

                for row in rows:

                    try:

                        text = row.get_attribute(
                            "textContent"
                        ) or ""

                        text = normalize(text)

                        match = re.search(
                            r"\+([\d,]+)\s+EXP",
                            text,
                            re.IGNORECASE
                        )

                        if match:

                            return int(
                                match.group(1).replace(
                                    ",",
                                    ""
                                )
                            )

                    except (
                        StaleElementReferenceException,
                        WebDriverException,
                    ):

                        continue

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

def wait_for_attack_processing(driver, clicked_element):

    """
    Confirm an attack click was actually processed before
    letting the caller poll/click again.

    This checks the SPECIFIC element that was clicked, not a
    fresh driver.find_element lookup. The reason: two genuinely
    different turns can legitimately show the same button label
    (e.g. "Fight" twice in a row) - comparing text alone can't
    tell that apart from a click that hasn't been processed by
    the site yet. A stale element reference (Selenium raises
    StaleElementReferenceException when the DOM node it's
    holding onto gets replaced/removed) is a much more reliable
    "the page has genuinely moved on" signal, since it doesn't
    depend on the new state's text differing from the old one.

    Previously this treated a blank text read as automatic
    confirmation, which could fire while a click was still
    mid-processing (a blank/loading render can appear briefly
    before the real next state settles) - that let the outer
    loop re-click the same still-processing turn. Blank reads
    are no longer treated as confirmation on their own.

    Always returns within ATTACK_CONFIRM_TIMEOUT regardless, so
    this can't hang even if staleness never fires for some
    reason.
    """

    start = time.time()

    try:

        initial_state = normalize(
            clicked_element.text
        )

    except (
        StaleElementReferenceException,
        WebDriverException,
    ):

        # Already gone right after the click - processed.
        return True

    while time.time() - start < ATTACK_CONFIRM_TIMEOUT:

        try:

            current_state = normalize(
                clicked_element.text
            )

            if current_state and current_state != initial_state:

                return True

        except (
            StaleElementReferenceException,
            WebDriverException,
        ):

            # The exact element we clicked is gone - the page
            # moved on to a new state, even if the new button's
            # text happens to match the old one.
            return True

        time.sleep(
            random.uniform(
                BATTLE_POLL_WAIT[0],
                BATTLE_POLL_WAIT[1]
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

            wait_for_attack_processing(
                driver,
                button
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

        if state and state != last_state:

            print(
                f"  Battle button state: "
                f"'{state}'"
            )

            last_state = state

        # ----------------------------------------------------
        # BATTLE FINISHED
        # ----------------------------------------------------

        if state in RESTART_STATES:

            return True

        # ----------------------------------------------------
        # ATTACK
        # ----------------------------------------------------

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

        time.sleep(
            random.uniform(
                BATTLE_POLL_WAIT[0],
                BATTLE_POLL_WAIT[1]
            )
        )

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
    difficulty=None,
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
    # Apply preferred battle difficulty, if requested.
    # --------------------------------------------------------

    if difficulty is not None:

        set_battle_difficulty(
            driver,
            difficulty,
        )

    # --------------------------------------------------------
    # Read actual level from battle page.
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

    # --------------------------------------------------------
    # Already at or above target.
    # --------------------------------------------------------

    if current_level >= target_level:

        print()
        print(
            "✓ Target level already reached."
        )

        print(
            f"  Current level: {current_level:,}"
        )

        print(
            f"  Target level:  {target_level:,}"
        )

        return {
            "battles": 0,
            "current_level": current_level,
            "target_level": target_level,
            "exp_gained": 0,
        }

    # --------------------------------------------------------
    # Session totals.
    # --------------------------------------------------------

    battles_completed = 0
    total_exp_gained = 0

    last_level_gain = None

    # --------------------------------------------------------
    # Initial progress.
    # --------------------------------------------------------

    print_training_progress(
        current_level,
        target_level,
    )

    # --------------------------------------------------------
    # Battle loop.
    # --------------------------------------------------------

    while (
        current_level < target_level
        and battles_completed < max_battles
    ):

        print()
        print(
            f"=== Battle "
            f"{battles_completed + 1}/"
            f"{max_battles:,} safety limit ==="
        )

        # ----------------------------------------------------
        # Wait for and complete current battle.
        # ----------------------------------------------------

        if not wait_for_battle_to_finish(driver):

            print()
            print(
                "✗ Battle did not finish "
                "within the timeout."
            )

            break

        print(
            "  ✓ Battle finished."
        )

        # ----------------------------------------------------
        # Read Battle Results BEFORE navigating away.
        # ----------------------------------------------------

        level_gain = get_battle_level_gain(
            driver
        )

        exp_gain = get_battle_exp_gain(
            driver
        )

        # ----------------------------------------------------
        # Count battle.
        # ----------------------------------------------------

        battles_completed += 1

        # ----------------------------------------------------
        # Record level gain.
        # ----------------------------------------------------

        if level_gain is not None:

            last_level_gain = level_gain

            print(
                f"  Levels gained: "
                f"+{level_gain:,}"
            )

        else:

            print(
                "  ⚠ Could not read level gain."
            )

        # ----------------------------------------------------
        # Record EXP gain.
        # ----------------------------------------------------

        if exp_gain is not None:

            total_exp_gained += exp_gain

            print(
                f"  EXP gained: "
                f"+{exp_gain:,}"
            )

            print(
                f"  Total EXP gained: "
                f"{total_exp_gained:,}"
            )

        else:

            print(
                "  ⚠ Could not read EXP gain."
            )

        # ----------------------------------------------------
        # Read authoritative current level.
        #
        # The battle page's:
        #
        #   Level <b>xxxxx</b>
        #
        # is used instead of calculating the level ourselves.
        # ----------------------------------------------------

        new_level = wait_for_current_level(
            driver,
            timeout=WAIT_LONG,
        )

        if new_level is not None:

            current_level = new_level

        elif level_gain is not None:

            # Fallback only if the page level cannot be read.

            current_level += level_gain

            print(
                "  ⚠ Battle-page level unavailable; "
                "using level gain fallback."
            )

        else:

            print()
            print(
                "✗ Could not determine the new level."
            )

            break

        # ----------------------------------------------------
        # Display progress.
        # ----------------------------------------------------

        print(
            f"  Current level: "
            f"{current_level:,}/"
            f"{target_level:,}"
        )

        # ----------------------------------------------------
        # TARGET REACHED
        # ----------------------------------------------------

        if current_level >= target_level:

            print()
            print(
                "✓ Battle complete!"
            )

            break

        # ----------------------------------------------------
        # Prepare next battle.
        # ----------------------------------------------------

        print()
        print(
            "✓ Battle "
            f"{battles_completed} complete!"
        )

        print(
            "  Preparing next battle..."
        )

        # ----------------------------------------------------
        # Click Restart / Fight Again / Battle Again.
        # ----------------------------------------------------

        if not click_restart_battle(driver):

            print()
            print(
                "✗ Could not start the next battle."
            )

            break

        print(
            "  ✓ Next battle started."
        )

        # ----------------------------------------------------
        # Allow page to settle.
        # ----------------------------------------------------

        time.sleep(
            random.uniform(
                BETWEEN_BATTLES_WAIT[0],
                BETWEEN_BATTLES_WAIT[1]
            )
        )

        # ----------------------------------------------------
        # Read level again after next battle starts.
        # ----------------------------------------------------

        refreshed_level = get_current_battle_level(
            driver
        )

        if refreshed_level is not None:

            current_level = refreshed_level

        print_training_progress(
            current_level,
            target_level,
            last_level_gain,
            total_exp_gained,
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 60)

    if current_level >= target_level:

        print(
            "✓ TARGET LEVEL REACHED!"
        )

    elif battles_completed >= max_battles:

        print(
            "⚠ TRAINING STOPPED AT SAFETY LIMIT!"
        )

    else:

        print(
            "⚠ TRAINING STOPPED!"
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
        f"{battles_completed:,}"
    )

    print(
        f"  Total EXP gained: "
        f"{total_exp_gained:,}"
    )

    print("=" * 60)

    return {
        "battles": battles_completed,
        "current_level": current_level,
        "target_level": target_level,
        "exp_gained": total_exp_gained,
    }


# ============================================================
# BATTLE FOR X BATTLES
# ============================================================

def train_mode(
    driver,
    max_battles=MAX_BATTLES,
    difficulty=None,
):

    print()
    print("=" * 60)
    print("BATTLE TRAINING")
    print("=" * 60)
    print()

    print(
        f"Battle limit: {max_battles:,}"
    )

    # --------------------------------------------------------
    # Validate battle limit.
    # --------------------------------------------------------

    if max_battles <= 0:

        print(
            "✗ Battle limit must be greater than 0."
        )

        return {
            "battles": 0,
            "current_level": None,
            "target_level": None,
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
            "target_level": None,
            "exp_gained": 0,
        }

    # --------------------------------------------------------
    # Apply preferred battle difficulty, if requested.
    # --------------------------------------------------------

    if difficulty is not None:

        set_battle_difficulty(
            driver,
            difficulty,
        )

    # --------------------------------------------------------
    # Read starting level.
    # --------------------------------------------------------

    current_level = wait_for_current_level(
        driver
    )

    # --------------------------------------------------------
    # Session totals.
    # --------------------------------------------------------

    battles_completed = 0
    total_exp_gained = 0

    # --------------------------------------------------------
    # Battle loop.
    # --------------------------------------------------------

    while battles_completed < max_battles:

        print()
        print(
            f"=== Battle "
            f"{battles_completed + 1}/"
            f"{max_battles:,} ==="
        )

        # ----------------------------------------------------
        # Fight.
        # ----------------------------------------------------

        if not wait_for_battle_to_finish(driver):

            print()
            print(
                "✗ Battle did not finish "
                "within the timeout."
            )

            break

        print(
            "  ✓ Battle finished."
        )

        # ----------------------------------------------------
        # Read Battle Results.
        # ----------------------------------------------------

        level_gain = get_battle_level_gain(
            driver
        )

        exp_gain = get_battle_exp_gain(
            driver
        )

        # ----------------------------------------------------
        # Count battle.
        # ----------------------------------------------------

        battles_completed += 1

        print()
        print(
            f"✓ Battle "
            f"{battles_completed} complete!"
        )

        # ----------------------------------------------------
        # Level gain.
        # ----------------------------------------------------

        if level_gain is not None:

            print(
                f"  Levels gained: "
                f"+{level_gain:,}"
            )

        else:

            print(
                "  ⚠ Could not read level gain."
            )

        # ----------------------------------------------------
        # EXP gain.
        # ----------------------------------------------------

        if exp_gain is not None:

            total_exp_gained += exp_gain

            print(
                f"  EXP gained: "
                f"+{exp_gain:,}"
            )

            print(
                f"  Total EXP gained: "
                f"{total_exp_gained:,}"
            )

        else:

            print(
                "  ⚠ Could not read EXP gain."
            )

        # ----------------------------------------------------
        # Current level.
        # ----------------------------------------------------

        new_level = get_current_battle_level(
            driver
        )

        if new_level is not None:

            current_level = new_level

            print(
                f"  Current level: "
                f"{current_level:,}"
            )

        # ----------------------------------------------------
        # Requested number of battles completed.
        # ----------------------------------------------------

        if battles_completed >= max_battles:

            break

        # ----------------------------------------------------
        # Start next battle.
        # ----------------------------------------------------

        print(
            "  Preparing next battle..."
        )

        if not click_restart_battle(driver):

            print()
            print(
                "✗ Could not start the next battle."
            )

            break

        print(
            "  ✓ Next battle started."
        )

        time.sleep(
            random.uniform(
                BETWEEN_BATTLES_WAIT[0],
                BETWEEN_BATTLES_WAIT[1]
            )
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 60)
    print("✓ BATTLE TRAINING COMPLETE")
    print("=" * 60)

    print(
        f"  Battles completed: "
        f"{battles_completed:,}"
    )

    if current_level is not None:

        print(
            f"  Current level: "
            f"{current_level:,}"
        )

    print(
        f"  Total EXP gained: "
        f"{total_exp_gained:,}"
    )

    print("=" * 60)

    return {
        "battles": battles_completed,
        "current_level": current_level,
        "target_level": None,
        "exp_gained": total_exp_gained,
    }