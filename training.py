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

WAIT_LONG = 20
BATTLE_END_TIMEOUT = 120

BETWEEN_BATTLES_WAIT = (2.0, 3.0)


# ============================================================
# BATTLE STATES
# ============================================================

# These are ALL valid names the site may use for the button
# that starts the next battle.

RESTART_STATES = {
    "restart",
    "battle again",
    "fight again",
    "restart battle",
}


# These are the states used while the Pokémon is actually
# fighting.

ATTACK_STATES = {
    "attack",
    "fight",
}


# ============================================================
# OPEN YOUR PROFILE
# ============================================================

def open_profile(driver):

    print(
        "Opening Your Profile..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            # ------------------------------------------------
            # ACTUAL SITE STRUCTURE:
            #
            # <a href="/user?id=1102725">
            #     Your Profile (#1102725)
            # </a>
            #
            # We deliberately target the /user?id= link.
            #
            # DO NOT use a generic:
            #
            # //*[contains(., "Your Profile")]
            #
            # because that can hit unrelated page elements.
            # ------------------------------------------------

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

                    text = normalize(
                        link.text
                    )

                    if "your profile" not in text:

                        continue

                    href = link.get_attribute(
                        "href"
                    )

                    if not href:

                        continue

                    if "/user?id=" not in href:

                        continue

                    print(
                        f"  ✓ Your Profile found: "
                        f"'{link.text.strip()}'"
                    )

                    if safe_click(
                        driver,
                        link
                    ):

                        print(
                            "  ✓ Your Profile clicked."
                        )

                        wait_for_document_ready(
                            driver
                        )

                        time.sleep(
                            random.uniform(
                                0.8,
                                1.5
                            )
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

    print(
        "Opening Party..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            # ------------------------------------------------
            # ACTUAL SITE STRUCTURE:
            #
            # <span id="VP_PartyLink1"
            #       onclick="...set_profile_tab('Party',0);">
            #
            # We target this EXACT element.
            #
            # This prevents generic "Party" searches from
            # accidentally selecting an advertisement.
            # ------------------------------------------------

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

                    if safe_click(
                        driver,
                        party
                    ):

                        print(
                            "  ✓ Party clicked."
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

            # ------------------------------------------------
            # Actual party Fight links look like:
            #
            # <a class="inputsubmit"
            #    href="/create_battle?...">
            #    Fight
            # </a>
            #
            # We require ALL of the following:
            #
            # 1. <a>
            # 2. class contains inputsubmit
            # 3. exact visible text = Fight
            # 4. href contains create_battle
            #
            # This keeps ads and unrelated links out.
            # ------------------------------------------------

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

                    href = fight.get_attribute(
                        "href"
                    )

                    if not href:

                        continue

                    if "create_battle" not in href:

                        continue

                    valid_fights.append(
                        fight
                    )

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

                # Always use the first Pokémon.
                fight = valid_fights[0]

                print(
                    "  Clicking first Pokémon Fight..."
                )

                if safe_click(
                    driver,
                    fight
                ):

                    print(
                        "  ✓ First Fight clicked."
                    )

                    wait_for_document_ready(
                        driver
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

    # --------------------------------------------------------
    # THIS FUNCTION SHOULD ONLY BE CALLED ONCE PER TRAIN MODE
    # SESSION.
    #
    # Profile -> Party -> First Fight
    # --------------------------------------------------------

    if not open_profile(
        driver
    ):

        return False

    if not open_party(
        driver
    ):

        return False

    if not click_first_party_fight(
        driver
    ):

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

    button = get_battle_button(
        driver
    )

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
# CHECK FOR BATTLE COMPLETION
# ============================================================

def battle_has_ended(driver):

    state = get_battle_button_text(
        driver
    )

    return state in RESTART_STATES


# ============================================================
# CLICK ATTACK / FIGHT
# ============================================================

def click_attack(driver):

    button = get_battle_button(
        driver
    )

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

        if safe_click(
            driver,
            button
        ):

            print(
                "  ✓ Attack/Fight clicked."
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

        button = get_battle_button(
            driver
        )

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

        # ----------------------------------------------------
        # Only print when the button state changes.
        # ----------------------------------------------------

        if state != last_state:

            print(
                f"  Battle button state: "
                f"'{state}'"
            )

            last_state = state

        # ----------------------------------------------------
        # BATTLE FINISHED
        #
        # Valid examples:
        #
        # Restart
        # Battle Again
        # Fight Again
        # Restart Battle
        # ----------------------------------------------------

        if state in RESTART_STATES:

            return True

        # ----------------------------------------------------
        # ATTACK
        # ----------------------------------------------------

        if state in ATTACK_STATES:

            click_attack(
                driver
            )

            time.sleep(
                random.uniform(
                    0.7,
                    1.2
                )
            )

            continue

        time.sleep(
            random.uniform(
                0.4,
                0.8
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

        button = get_battle_button(
            driver
        )

        if button is not None:

            try:

                state = normalize(
                    button.text
                )

                # ------------------------------------------------
                # IMPORTANT:
                #
                # Only click #battlebtn.
                #
                # NEVER search the entire page for:
                #
                # "Restart"
                # "Battle Again"
                # "Fight Again"
                #
                # because advertisements can contain those words.
                # ------------------------------------------------

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

                        # Wait briefly for the new battle
                        # state to appear.

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
# TRAIN MODE
# ============================================================

def train_mode(driver, max_battles=None):

    if max_battles is None:
        max_battles = MAX_BATTLES

    print()
    print("=" * 60)
    print("TRAIN MODE")
    print("=" * 60)

    # ========================================================
    # INITIAL BATTLE
    #
    # Profile -> Party -> First Fight
    #
    # THIS HAPPENS ONLY ONCE.
    # ========================================================

    if not start_training_battle(
        driver
    ):

        print()
        print(
            "✗ Could not start training battle."
        )

        return 0

    print(
        "✓ First training battle started."
    )

    battle_count = 0

    # ========================================================
    # BATTLE LOOP
    #
    # From this point forward:
    #
    # NEVER:
    #
    #   Profile -> Party -> Fight
    #
    # Instead:
    #
    #   Finish battle
    #        ↓
    #   Restart / Battle Again / Fight Again
    #        ↓
    #   Next battle
    #
    # ========================================================

    while battle_count < max_battles:

        print()
        print(
            f"=== Battle "
            f"{battle_count + 1}/"
            f"{max_battles} ==="
        )

        # ----------------------------------------------------
        # Fight the current battle.
        # ----------------------------------------------------

        if not wait_for_battle_to_finish(
            driver
        ):

            print()
            print(
                "✗ Battle timed out."
            )

            return battle_count

        print(
            "  ✓ Battle finished."
        )

        # ----------------------------------------------------
        # Count the completed battle.
        # ----------------------------------------------------

        battle_count += 1

        print()
        print(
            f"✓ Battle "
            f"{battle_count} complete!"
        )

        # ----------------------------------------------------
        # Finished requested number of battles.
        # ----------------------------------------------------

        if battle_count >= max_battles:

            break

        # ----------------------------------------------------
        # DO NOT OPEN PROFILE.
        #
        # DO NOT OPEN PARTY.
        #
        # DO NOT CLICK THE FIRST FIGHT LINK AGAIN.
        #
        # Click the battle page's:
        #
        # Restart
        # Battle Again
        # Fight Again
        # ----------------------------------------------------

        print(
            "  Preparing next battle..."
        )

        if not click_restart_battle(
            driver
        ):

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
        f"✓ Completed {battle_count} battles."
    )
    print("=" * 60)

    return battle_count