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

from break_check import check_and_handle_break
from cancellation import is_cancel_requested
from utils import (
    safe_click,
    normalize,
    wait_for_document_ready,
)


# ============================================================
# CONSOLE STYLE
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
PURPLE = "\033[38;5;141m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"
GOLD = "\033[38;5;220m"

BORDER_COLOR = PURPLE
CATEGORY_COLOR = f"{BOLD}{CYAN}"
KEY_COLOR = f"{BOLD}{YELLOW}"
NAME_COLOR = f"{BOLD}{WHITE}"
DESC_COLOR = GRAY

BOX_WIDTH = 71


def _strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", str(text))


def _row(label="", value="", label_color=KEY_COLOR, value_color=NAME_COLOR):
    content = (
        f"{label_color}{label}{RESET}"
        f"{' ' if label else ''}"
        f"{value_color}{value}{RESET}"
    )
    padding = BOX_WIDTH - 2 - len(_strip_ansi(content))
    return f"{BORDER_COLOR}║{RESET} {content}{' ' * max(0, padding)} {BORDER_COLOR}║{RESET}"


def _border(char="═"):
    return f"{BORDER_COLOR}╔{char * BOX_WIDTH}╗{RESET}"


def _middle_border(char="═"):
    return f"{BORDER_COLOR}╠{char * BOX_WIDTH}╣{RESET}"


def _bottom_border(char="═"):
    return f"{BORDER_COLOR}╚{char * BOX_WIDTH}╝{RESET}"


def _title(title, subtitle=None):
    print(_border())
    print(_row(title.center(BOX_WIDTH - 2), "", CATEGORY_COLOR, CATEGORY_COLOR))
    if subtitle:
        print(_row(subtitle.center(BOX_WIDTH - 2), "", DESC_COLOR, DESC_COLOR))


def _print_status(message, kind="info", indent=False):
    prefix = {
        "success": f"{GREEN}✓{RESET}",
        "warning": f"{YELLOW}⚠{RESET}",
        "error": f"{RED}✗{RESET}",
        "info": f"{CYAN}•{RESET}",
    }.get(kind, f"{CYAN}•{RESET}")
    text = f"{prefix} {message}"
    if indent:
        text = f"  {text}"
    print(f"{BORDER_COLOR}║{RESET} {_color_status_text(text, kind)}{' ' * max(0, BOX_WIDTH - 2 - len(_strip_ansi(text)))} {BORDER_COLOR}║{RESET}")


def _color_status_text(text, kind):
    color = {
        "success": GREEN,
        "warning": YELLOW,
        "error": RED,
        "info": WHITE,
    }.get(kind, WHITE)
    return f"{color}{text}{RESET}"


def _print_training_box(title, rows=None, status=None, subtitle=None):
    _title(title, subtitle)
    if rows:
        for label, value, color in rows:
            print(_row(label, value, KEY_COLOR, color))
    if status:
        print(_middle_border())
        message, kind = status
        _print_status(message, kind)
    print(_bottom_border())


def _print_training_progress_box(
    current_level,
    target_level,
    last_level_gain=None,
    total_exp_gained=0,
):
    if current_level is None:
        progress = f"Unknown / {target_level:,}"
        remaining = "Unknown"
    else:
        progress = f"{current_level:,} / {target_level:,}"
        remaining = f"{max(0, target_level - current_level):,}"

    rows = [
        ("PROGRESS:", progress, NAME_COLOR),
        ("LEVELS REMAINING:", remaining, NAME_COLOR),
    ]

    if last_level_gain is not None:
        rows.append(("LAST BATTLE:", f"+{last_level_gain:,} levels", GREEN))

    if total_exp_gained:
        rows.append(("TOTAL EXP GAINED:", f"{total_exp_gained:,}", GOLD))

    _print_training_box(
        "TRAINING PROGRESS",
        rows,
        subtitle="Current training session progress",
    )


def _print_battle_result_box(
    battle_number,
    max_battles,
    level_gain=None,
    exp_gain=None,
    total_exp_gained=0,
    current_level=None,
    target_level=None,
    safety_limit=False,
):
    rows = []

    if level_gain is not None:
        rows.append(("LEVELS GAINED:", f"+{level_gain:,}", GREEN))

    if exp_gain is not None:
        rows.append(("EXP GAINED:", f"+{exp_gain:,}", GREEN))

    rows.append(("TOTAL EXP GAINED:", f"{total_exp_gained:,}", GOLD))

    if current_level is not None:
        current = f"{current_level:,}"
        if target_level is not None:
            current += f" / {target_level:,}"
        rows.append(("CURRENT LEVEL:", current, NAME_COLOR))

        if target_level is not None:
            rows.append(
                ("LEVELS REMAINING:", f"{max(0, target_level - current_level):,}", NAME_COLOR)
            )

    title = f"BATTLE {battle_number:,}"
    subtitle = "Training battle results"
    if safety_limit:
        subtitle = "Training battle results • safety limit"

    _print_training_box(title, rows, subtitle=subtitle)


def _print_training_action(message, kind="info"):
    """Print a compact training status line using the bot's ANSI palette."""
    prefix = {
        "success": "✓",
        "warning": "⚠",
        "error": "✗",
        "info": "•",
    }.get(kind, "•")
    color = {
        "success": GREEN,
        "warning": YELLOW,
        "error": RED,
        "info": CYAN,
    }.get(kind, CYAN)
    print(f"{color}{prefix}{RESET} {WHITE}{message}{RESET}")

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

        _print_training_action(
            f"Unknown difficulty: {difficulty}",
            "error",
        )

        return False

    try:

        select_element = driver.find_element(
            By.NAME,
            "B_Difficulty",
        )

        select = Select(select_element)

        select.select_by_value(difficulty)

        _print_training_action(
            f"Battle difficulty set to {DIFFICULTY_LABELS.get(difficulty, difficulty)}.",
            "success",
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

        _print_training_action(
            f"Could not set battle difficulty: {error}",
            "error",
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
# BETWEEN BATTLES WAIT (Configurable)
# ============================================================

_between_battles_wait = BETWEEN_BATTLES_WAIT


def get_between_battles_wait():
    """Return (min, max) tuple for wait between battles."""
    return _between_battles_wait


def set_between_battles_wait(min_seconds, max_seconds):
    """Set wait time between battles."""
    global _between_battles_wait
    
    if min_seconds <= 0 or max_seconds <= 0:
        return False
    
    if min_seconds > max_seconds:
        min_seconds, max_seconds = max_seconds, min_seconds
    
    _between_battles_wait = (min_seconds, max_seconds)
    return True


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

    _print_training_action("Opening Your Profile...", "info")

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

                    _print_training_action(
                        f"Your Profile found: '{link.text.strip()}'",
                        "success",
                    )

                    if safe_click(driver, link):

                        _print_training_action(
                            "Your Profile clicked.",
                            "success",
                        )

                        wait_for_document_ready(driver)

                        time.sleep(
                            random.uniform(0.8, 1.5)
                        )

                        _print_training_action(
                            "Your Profile opened.",
                            "success",
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

    _print_training_action(
        "Your Profile link not found.",
        "error",
    )

    return False


# ============================================================
# OPEN PARTY
# ============================================================

def open_party(driver):

    _print_training_action("Opening Party...", "info")

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

                    _print_training_action("Party tab found.", "success")

                    if safe_click(driver, party):

                        _print_training_action("Party clicked.", "success")

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

    _print_training_action("Party tab not found.", "error")

    return False


# ============================================================
# CLICK FIRST POKEMON FIGHT
# ============================================================

def click_first_party_fight(driver):

    _print_training_action("Looking for first Pokémon Fight...", "info")

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

                _print_training_action(
                    f"Found {len(valid_fights)} valid Fight button(s).",
                    "success",
                )

                fight = valid_fights[0]

                _print_training_action(
                    "Clicking first Pokémon Fight...",
                    "info",
                )

                if safe_click(driver, fight):

                    _print_training_action(
                        "First Fight clicked.",
                        "success",
                    )

                    wait_for_document_ready(driver)

                    time.sleep(
                        random.uniform(0.8, 1.5)
                    )

                    return True

        except Exception:

            pass

        time.sleep(0.3)

    _print_training_action(
        "First Pokémon Fight not found.",
        "error",
    )

    return False


# ============================================================
# START INITIAL TRAINING BATTLE
# ============================================================

def start_training_battle(driver):

    _print_training_action(
        "Starting new training battle...",
        "info",
    )

    if not open_profile(driver):
        return False

    if not open_party(driver):
        return False

    if not click_first_party_fight(driver):
        return False

    _print_training_action("Training battle started.", "success")

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


def pokemon_has_fainted(driver):
    """Return True when the current page offers the Pokemon Center link."""
    try:
        page_text = driver.find_element(
            By.TAG_NAME,
            "body",
        ).text.lower()
        return "fainted" in page_text and "pokemon center" in page_text
    except (
        StaleElementReferenceException,
        WebDriverException,
    ):
        return False


def recover_from_faint(driver):
    """Heal the party and resume training after a fainted Pokemon."""
    _print_training_action(
        "Active Pokemon fainted. Going to the Pokemon Center...",
        "warning",
    )

    try:
        current_url = driver.current_url
        base_url = current_url.split("/", 3)
        if len(base_url) < 3:
            raise RuntimeError("Unable to determine the site base URL.")

        driver.get(f"{base_url[0]}//{base_url[2]}/pokemon_center")
    except (
        RuntimeError,
        WebDriverException,
    ) as error:
        _print_training_action(
            f"Could not open the Pokemon Center: {error}",
            "error",
        )
        return False

    start = time.time()
    while time.time() - start < WAIT_LONG:
        try:
            heal_button = driver.find_element(
                By.ID,
                "PC_HealPokemon",
            )
            if heal_button.is_displayed() and heal_button.is_enabled():
                if not safe_click(driver, heal_button):
                    _print_training_action(
                        "Could not click Heal Party Pokémon.",
                        "error",
                    )
                    return False

                time.sleep(random.uniform(0.8, 1.5))
                _print_training_action(
                    "Party healed. Resuming training...",
                    "success",
                )
                return start_training_battle(driver)
        except (
            StaleElementReferenceException,
            WebDriverException,
        ):
            pass

        time.sleep(0.3)

    _print_training_action(
        "Heal Party Pokémon button was not found.",
        "error",
    )
    return False


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

        _print_training_action(
            f"Clicking '{button.text.strip()}'...",
            "info",
        )

        if safe_click(driver, button):

            _print_training_action("Attack/Fight clicked.", "success")

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

    _print_training_action("Waiting for battle...", "info")

    battle_start = time.time()

    last_state = None

    while (
        time.time() - battle_start
        < BATTLE_END_TIMEOUT
    ):

        button = get_battle_button(driver)

        if button is None:
            if pokemon_has_fainted(driver):
                return "fainted"
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

            _print_training_action(
                f"Battle button state: '{state}'",
                "info",
            )

            last_state = state

        # ----------------------------------------------------
        # BATTLE FINISHED
        # ----------------------------------------------------

        if state in RESTART_STATES:

            return True

        if pokemon_has_fainted(driver):
            return "fainted"

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

    _print_training_action("Looking for next-battle button...", "info")

    start = time.time()

    while time.time() - start < WAIT_LONG:

        button = get_battle_button(driver)

        if button is not None:

            try:

                state = normalize(
                    button.text
                )

                if state in RESTART_STATES:

                    _print_training_action(
                        f"Next-battle button found: '{button.text.strip()}'",
                        "success",
                    )

                    if safe_click(
                        driver,
                        button
                    ):

                        _print_training_action(
                            "Next battle button clicked.",
                            "success",
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

    _print_training_action(
        "Restart/Battle Again/Fight Again button not found.",
        "error",
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
    _print_training_progress_box(
        current_level,
        target_level,
        last_level_gain,
        total_exp_gained,
    )


# ============================================================
# BATTLE UNTIL TARGET LEVEL
# ============================================================

def train_until_level(
    driver,
    target_level,
    max_battles=MAX_LEVEL_BATTLES,
    difficulty=None,
    account_name=None,
):

    # Initialize Discord notifications
    from training_notifications_integration import TrainingNotifier
    notifier = TrainingNotifier(account_name) if account_name else None
    if notifier and notifier.is_enabled():
        print("  ✅ Discord notifications enabled")

    _print_training_box(
        "TRAIN UNTIL LEVEL",
        [
            ("TARGET LEVEL:", f"{target_level:,}", NAME_COLOR),
            ("SAFETY LIMIT:", f"{max_battles:,} battles", NAME_COLOR),
        ],
        subtitle="Train until the selected level is reached",
    )

    # --------------------------------------------------------
    # Validate target.
    # --------------------------------------------------------

    if target_level <= 0:

        _print_training_action(
            "Target level must be greater than 0.",
            "error",
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

        _print_training_action(
            "Could not start training battle.",
            "error",
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

        _print_training_action(
            "Could not determine current level.",
            "error",
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

        _print_training_box(
            "TARGET ALREADY REACHED",
            [
                ("CURRENT LEVEL:", f"{current_level:,}", GREEN),
                ("TARGET LEVEL:", f"{target_level:,}", NAME_COLOR),
            ],
            status=("Target level already reached.", "success"),
            subtitle="No additional battles required",
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
    cancelled = False
    
    start_time = time.time()  # For speed calculation in notifications

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

        _print_training_action(
            f"Starting battle {battles_completed + 1}/{max_battles:,} (safety limit)",
            "info",
        )

        # ----------------------------------------------------
        # Wait for and complete current battle.
        # ----------------------------------------------------

        battle_result = wait_for_battle_to_finish(driver)

        if battle_result == "fainted":
            if not recover_from_faint(driver):
                break
            continue

        if not battle_result:

            _print_training_action(
                "Battle did not finish within the timeout.",
                "error",
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

            _print_training_action(
                f"Levels gained: +{level_gain:,}",
                "success",
            )

        else:

            _print_training_action(
                "Could not read level gain.",
                "warning",
            )

        # ----------------------------------------------------
        # Record EXP gain.
        # ----------------------------------------------------

        if exp_gain is not None:

            total_exp_gained += exp_gain

            _print_training_action(
                f"EXP gained: +{exp_gain:,}",
                "success",
            )

        else:

            _print_training_action(
                "Could not read EXP gain.",
                "warning",
            )


        # Send Discord notification at configured intervals
        if notifier:
            battles_per_hour = (battles_completed / (time.time() - start_time)) * 3600 if (time.time() - start_time) > 0 else 0
            notifier.on_battle_complete(battles_completed, total_exp_gained, battles_per_hour)

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

            _print_training_action(
                "Battle-page level unavailable; using level gain fallback.",
                "warning",
            )

        else:

            _print_training_action(
                "Could not determine the new level.",
                "error",
            )

            break

        # ----------------------------------------------------
        # Display progress.
        # ----------------------------------------------------

        _print_training_action(
            f"Current level: {current_level:,}/{target_level:,}",
            "info",
        )

        # ----------------------------------------------------
        # TARGET REACHED
        # ----------------------------------------------------

        if current_level >= target_level:

            _print_training_action("Battle complete!", "success")

            break

        # ----------------------------------------------------
        # Prepare next battle.
        # ----------------------------------------------------

        _print_training_action(
            f"Battle {battles_completed} complete!",
            "success",
        )

        _print_training_action(
            "Preparing next battle...",
            "info",
        )

        # ----------------------------------------------------
        # Click Restart / Fight Again / Battle Again.
        # ----------------------------------------------------

        if not click_restart_battle(driver):

            _print_training_action(
                "Could not start the next battle.",
                "error",
            )

            break

        _print_training_action("Next battle started.", "success")

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

    if current_level >= target_level:
        status = ("TARGET LEVEL REACHED!", "success")
    elif battles_completed >= max_battles:
        status = ("TRAINING STOPPED AT SAFETY LIMIT!", "warning")
    else:
        status = ("TRAINING STOPPED!", "warning")

    _print_training_box(
        "TRAINING COMPLETE",
        [
            ("CURRENT LEVEL:", f"{current_level:,}", NAME_COLOR),
            ("TARGET LEVEL:", f"{target_level:,}", NAME_COLOR),
            ("BATTLES COMPLETED:", f"{battles_completed:,}", NAME_COLOR),
            ("TOTAL EXP GAINED:", f"{total_exp_gained:,}", GOLD),
        ],
        status=status,
        subtitle="Train until level session summary",
    )

    # Send completion notification
    if notifier:
        duration_seconds = time.time() - start_time
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        notifier.on_training_complete(battles_completed, total_exp_gained, duration_str)

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
    duration_seconds=None,
):

    _print_training_box(
        "BATTLE TRAINING",
        [
            ("BATTLE LIMIT:", f"{max_battles:,}", NAME_COLOR),
        ],
        subtitle="Automated battle training",
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

        _print_training_action(
            "Could not start training battle.",
            "error",
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

    started_at = time.time()

    while battles_completed < max_battles:
        if is_cancel_requested():
            _print_training_action(
                "Training cancelled. Finishing the current result summary.",
                "warning",
            )
            cancelled = True
            break

        if (
            duration_seconds is not None
            and time.time() - started_at >= duration_seconds
        ):
            _print_training_action(
                "Training time limit reached.",
                "success",
            )
            break

        _print_training_action(
            f"Starting battle {battles_completed + 1}/{max_battles:,}",
            "info",
        )

        # ----------------------------------------------------
        # Fight.
        # ----------------------------------------------------

        battle_result = wait_for_battle_to_finish(driver)

        if battle_result == "fainted":
            if not recover_from_faint(driver):
                break
            continue

        if not battle_result:

            _print_training_action(
                "Battle did not finish within the timeout.",
                "error",
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

        _print_training_action(
            f"Battle {battles_completed} complete!",
            "success",
        )

        # ----------------------------------------------------
        # Level gain.
        # ----------------------------------------------------

        if level_gain is not None:

            _print_training_action(
                f"Levels gained: +{level_gain:,}",
                "success",
            )

        else:

            _print_training_action(
                "Could not read level gain.",
                "warning",
            )

        # ----------------------------------------------------
        # EXP gain.
        # ----------------------------------------------------

        if exp_gain is not None:

            total_exp_gained += exp_gain

            _print_training_action(
                f"EXP gained: +{exp_gain:,}",
                "success",
            )

        else:

            _print_training_action(
                "Could not read EXP gain.",
                "warning",
            )

        # ----------------------------------------------------
        # Current level.
        # ----------------------------------------------------

        new_level = get_current_battle_level(
            driver
        )

        if new_level is not None:

            current_level = new_level

            _print_training_action(
                f"Current level: {current_level:,}",
                "info",
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

            _print_training_action(
                "Could not start the next battle.",
                "error",
            )

            break

        _print_training_action("Next battle started.", "success")

        time.sleep(
            random.uniform(
                _between_battles_wait[0],
                _between_battles_wait[1]
            )
        )

        # Check if break mode is due
        check_and_handle_break()

    # ========================================================
    # FINAL RESULT
    # ========================================================

    rows = [
        ("BATTLES COMPLETED:", f"{battles_completed:,}", NAME_COLOR),
    ]

    if current_level is not None:
        rows.append(("CURRENT LEVEL:", f"{current_level:,}", NAME_COLOR))

    rows.append(("TOTAL EXP GAINED:", f"{total_exp_gained:,}", GOLD))

    _print_training_box(
        "BATTLE TRAINING STOPPED" if cancelled else "BATTLE TRAINING COMPLETE",
        rows,
        status=(
            "BATTLE TRAINING STOPPED" if cancelled
            else "BATTLE TRAINING COMPLETE",
            "warning" if cancelled else "success",
        ),
        subtitle=(
            "Training cancelled after the current battle"
            if cancelled
            else "Training session summary"
        ),
    )

    return {
        "battles": battles_completed,
        "current_level": current_level,
        "target_level": None,
        "exp_gained": total_exp_gained,
        "cancelled": cancelled,
    }