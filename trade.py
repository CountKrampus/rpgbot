import time
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
)

from config import WAIT_LONG
from utils import safe_click, normalize


# ============================================================
# TRADE HELPERS
# ============================================================

def wait_ready(driver, timeout=WAIT_LONG):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) in ("interactive", "complete")
        )
    except Exception:
        pass


def find_visible(driver, by, value, timeout=WAIT_LONG):
    try:
        return WebDriverWait(driver, timeout).until(
            lambda d: next(
                (
                    el
                    for el in d.find_elements(by, value)
                    if el.is_displayed() and el.is_enabled()
                ),
                None,
            )
        )
    except TimeoutException:
        return None


def find_first(driver, selectors, timeout=WAIT_LONG):
    end = time.time() + timeout

    while time.time() < end:
        for by, value in selectors:
            try:
                elements = driver.find_elements(by, value)

                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            return element
                    except StaleElementReferenceException:
                        continue

            except Exception:
                continue

        time.sleep(0.2)

    return None


def click_element(driver, element):
    if not element:
        return False

    try:
        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center',
                inline: 'center'
            });
            """,
            element,
        )
    except Exception:
        pass

    return safe_click(driver, element)


# ============================================================
# POKEMON NAME HELPERS
# ============================================================

def normalize_pokemon_name(name):
    """
    Convert Pokémon names into a comparison-friendly format.

    Examples:

        Crystal Gastly -> crystalgastly
        crystal gastly -> crystalgastly
        Shiny Gastly   -> shinygastly
    """

    return re.sub(
        r"[^a-z0-9]",
        "",
        normalize(name),
    )


def parse_pokemon_request(request):
    """
    Returns:

        variant, pokemon_name, all_variants

    Examples:

        gastly
            -> "", "gastly", False

        crystal gastly
            -> "crystal", "gastly", False

        all gastlys
            -> "", "gastly", True

        all crystal gastlys
            -> "crystal", "gastly", True
    """

    text = normalize(request)

    all_variants = False

    if text.startswith("all "):
        all_variants = True
        text = text[4:].strip()

    words = text.split()

    variants = {
        "crystal",
        "shiny",
        "dark",
        "golden",
        "emerald",
        "shadow",
        "metallic",
        "mystic",
        "ruby",
        "sapphire",
        "amethyst",
        "pearl",
        "platinum",
    }

    variant = ""

    if words and words[0] in variants:
        variant = words.pop(0)

    pokemon_name = "".join(words)

    # Handle simple plurals:
    #
    # gastlys -> gastly
    #
    if pokemon_name.endswith("s") and not pokemon_name.endswith("ss"):
        pokemon_name = pokemon_name[:-1]

    return variant, pokemon_name, all_variants


def option_matches(option_text, variant, pokemon_name):
    """
    Match the site's Pokémon option text.

    Examples:

        Gastly Lv. 5
        CrystalGastly Lv. 12
        ShinyGastly Lv. 7
    """

    text = normalize_pokemon_name(option_text)

    target = normalize_pokemon_name(pokemon_name)

    if not target:
        return False

    # Remove the level portion.
    text_without_level = re.sub(
        r"lv\d+.*$",
        "",
        text,
    )

    if variant:
        wanted = (
            normalize_pokemon_name(variant)
            + target
        )

        return text_without_level == wanted

    # A normal Pokémon request must only match
    # the normal species.
    #
    # gastly:
    #   Gastly       YES
    #   CrystalGastly NO
    #   ShinyGastly   NO
    #   DarkGastly    NO
    #
    return text_without_level == target


# ============================================================
# RECIPIENT
# ============================================================

def select_recipient_method(driver):
    print("Selecting recipient method...")

    method = find_first(
        driver,
        [
            (
                By.CSS_SELECTOR,
                "select[name='CAT_Method']",
            ),
            (
                By.ID,
                "CAT_Method",
            ),
        ],
    )

    if not method:
        print(
            "  ✗ Recipient method selector not found."
        )
        return False

    return method


def find_recipient_input(driver):
    """
    Find the recipient input used by CAT_Method.

    The known field is:

        #CAT_Choice
    """

    return find_first(
        driver,
        [
            (
                By.ID,
                "CAT_Choice",
            ),
            (
                By.NAME,
                "CAT_Choice",
            ),
            (
                By.CSS_SELECTOR,
                "input[name='CAT_Choice']",
            ),
            (
                By.CSS_SELECTOR,
                "input#CAT_Choice",
            ),
        ],
    )


def set_recipient(driver):
    print()
    print("=" * 60)
    print("TRADE RECIPIENT")
    print("=" * 60)

    print()
    print("1. Username")
    print("2. User ID")

    while True:
        choice = input(
            "\nChoose recipient type: "
        ).strip()

        if choice in ("1", "2"):
            break

        print("✗ Invalid choice.")

    recipient = input(
        "\nEnter username/User ID: "
    ).strip()

    if not recipient:
        print(
            "✗ Recipient cannot be empty."
        )
        return False

    method = select_recipient_method(driver)

    if not method:
        return False

    try:
        select = Select(method)

        if choice == "1":
            # Website:
            # value="2" = Username
            select.select_by_value("2")

            print(
                "  ✓ Username selected."
            )

        else:
            # Website:
            # value="1" = User ID
            select.select_by_value("1")

            print(
                "  ✓ User ID selected."
            )

    except Exception as e:
        print(
            f"  ✗ Could not select recipient method: {e}"
        )
        return False

    time.sleep(0.5)

    field = find_recipient_input(driver)

    if not field:
        print(
            "  ✗ Recipient input field not found."
        )
        print(
            "    Expected #CAT_Choice."
        )
        return False

    try:
        field.clear()
        field.send_keys(recipient)

        print(
            f"  ✓ Recipient entered: {recipient}"
        )

    except Exception as e:
        print(
            f"  ✗ Could not enter recipient: {e}"
        )
        return False

    return True


# ============================================================
# INITIATE TRADE
# ============================================================

def initiate_trade(driver):
    """
    Click the actual 'Initiate Trade' button.

    Website HTML:

        <input
            type="submit"
            id="CAT_Submit"
            value="Initiate Trade"
            ...
            onclick="... initiate_trade('F');"
        >

    This MUST happen before CAT_User / CAT_Recipient
    become available.
    """

    print()
    print("Initiating trade...")

    button = find_first(
        driver,
        [
            (
                By.ID,
                "CAT_Submit",
            ),
            (
                By.CSS_SELECTOR,
                "input[value='Initiate Trade']",
            ),
        ],
        timeout=WAIT_LONG,
    )

    if not button:
        print(
            "  ✗ Initiate Trade button not found."
        )
        return False

    value = button.get_attribute("value") or ""

    print(
        f"  ✓ Initiate Trade button found: '{value}'"
    )

    if not click_element(driver, button):
        print(
            "  ✗ Could not click Initiate Trade."
        )
        return False

    print(
        "  ✓ Initiate Trade clicked."
    )

    # Wait for the page/DOM to update.
    wait_ready(driver)

    time.sleep(1)

    # The trade inventory should now exist.
    pokemon_select = find_visible(
        driver,
        By.ID,
        "CAT_User",
        timeout=WAIT_LONG,
    )

    if not pokemon_select:
        print(
            "  ✗ Trade was initiated, but "
            "the Pokémon selector (#CAT_User) "
            "was not found."
        )
        return False

    print(
        "  ✓ Trade Pokémon selection loaded."
    )

    return True


# ============================================================
# POKEMON SEARCH
# ============================================================

def find_trade_search(driver):
    return find_first(
        driver,
        [
            (
                By.CSS_SELECTOR,
                "input.trade-search[data-target='#CAT_User']",
            ),
            (
                By.CSS_SELECTOR,
                "input[data-target='#CAT_User']",
            ),
            (
                By.XPATH,
                "//input[@placeholder='Search...' "
                "and @data-target='#CAT_User']",
            ),
        ],
    )


def clear_pokemon_search(driver):
    search = find_trade_search(driver)

    if not search:
        return False

    try:
        search.clear()

        driver.execute_script(
            """
            arguments[0].dispatchEvent(
                new Event('input', {bubbles: true})
            );

            arguments[0].dispatchEvent(
                new Event('change', {bubbles: true})
            );
            """,
            search,
        )

        time.sleep(0.5)

        return True

    except Exception:
        return False


def search_pokemon(driver, pokemon):
    search = find_trade_search(driver)

    if not search:
        print(
            "  ✗ Pokémon search box not found."
        )
        return False

    try:
        search.clear()
        search.send_keys(pokemon)

        driver.execute_script(
            """
            arguments[0].dispatchEvent(
                new Event('input', {bubbles: true})
            );

            arguments[0].dispatchEvent(
                new Event('keyup', {bubbles: true})
            );
            """,
            search,
        )

        time.sleep(0.8)

        print(
            f"  ✓ Searching trade inventory for "
            f"'{pokemon}'..."
        )

        return True

    except Exception as e:
        print(
            f"  ✗ Pokémon search failed: {e}"
        )
        return False


# ============================================================
# POKEMON OPTIONS
# ============================================================

def get_trade_options(driver):
    try:
        select = find_visible(
            driver,
            By.ID,
            "CAT_User",
            timeout=WAIT_LONG,
        )

        if not select:
            return []

        return select.find_elements(
            By.TAG_NAME,
            "option",
        )

    except Exception:
        return []


def select_pokemon(driver, request, quantity):
    variant, pokemon_name, all_variants = parse_pokemon_request(
        request
    )

    if not pokemon_name:
        print(
            "✗ Invalid Pokémon name."
        )
        return False

    print()
    print(
        f"Searching for: "
        f"{'all ' if all_variants else ''}"
        f"{variant + ' ' if variant else ''}"
        f"{pokemon_name}"
    )

    # Use the site's search box.
    if not search_pokemon(
        driver,
        request,
    ):
        return False

    select_element = find_visible(
        driver,
        By.ID,
        "CAT_User",
        timeout=WAIT_LONG,
    )

    if not select_element:
        print(
            "  ✗ Pokémon list not found."
        )
        return False

    options = select_element.find_elements(
        By.TAG_NAME,
        "option",
    )

    matches = []

    for option in options:
        try:
            text = option.text.strip()

            if not text:
                continue

            if normalize(text) == "trade nothing":
                continue

            if option_matches(
                text,
                variant,
                pokemon_name,
            ):
                matches.append(option)

        except StaleElementReferenceException:
            continue

    if not matches:
        print(
            f"  ✗ No matching Pokémon found "
            f"for '{request}'."
        )
        return False

    print(
        f"  ✓ Found {len(matches)} matching Pokémon."
    )

    # None means "all".
    if quantity is None:
        selected_count = len(matches)

    else:
        selected_count = min(
            quantity,
            len(matches),
        )

    if selected_count <= 0:
        print(
            "✗ Quantity must be greater than zero."
        )
        return False

    selected = matches[:selected_count]

    try:
        # First clear any previous selection.
        driver.execute_script(
            """
            const select =
                document.getElementById('CAT_User');

            if (select) {
                for (const option of select.options) {
                    option.selected = false;
                }
            }
            """
        )

        # Select requested Pokémon.
        for option in selected:
            driver.execute_script(
                """
                arguments[0].selected = true;

                arguments[0].dispatchEvent(
                    new Event('change', {
                        bubbles: true
                    })
                );
                """,
                option,
            )

        # Trigger the site's selection-count handler.
        driver.execute_script(
            """
            const select =
                document.getElementById('CAT_User');

            if (select) {
                select.dispatchEvent(
                    new Event('change', {
                        bubbles: true
                    })
                );

                select.dispatchEvent(
                    new Event('input', {
                        bubbles: true
                    })
                );
            }
            """
        )

    except Exception as e:
        print(
            f"  ✗ Could not select Pokémon: {e}"
        )
        return False

    print(
        f"  ✓ Selected {selected_count} Pokémon:"
    )

    for option in selected:
        try:
            print(
                f"      - {option.text.strip()}"
            )
        except Exception:
            pass

    return True


# ============================================================
# QUANTITY
# ============================================================

def ask_quantity(request):
    """
    Normal/specific requests:
        ask how many

    'all ...':
        Enter means all.
    """

    _, _, all_variants = parse_pokemon_request(
        request
    )

    while True:

        if all_variants:

            raw = input(
                "\nHow many? [Enter = all]: "
            ).strip()

            if not raw:
                return None

        else:

            raw = input(
                "\nHow many: "
            ).strip()

        try:
            quantity = int(raw)

            if quantity <= 0:
                print(
                    "✗ Quantity must be greater than zero."
                )
                continue

            return quantity

        except ValueError:
            print(
                "✗ Enter a valid number."
            )


# ============================================================
# CREATE TRADE
# ============================================================

def click_create_trade(driver):
    print()
    print("Creating trade...")

    button = find_first(
        driver,
        [
            (
                By.ID,
                "CAT_Submit2",
            ),
            (
                By.CSS_SELECTOR,
                "input[value='Create Trade']",
            ),
        ],
    )

    if not button:
        print(
            "  ✗ Create Trade button not found."
        )
        return False

    value = button.get_attribute("value") or ""

    print(
        f"  ✓ Create Trade button found: "
        f"'{value}'"
    )

    if not click_element(
        driver,
        button,
    ):
        print(
            "  ✗ Could not click Create Trade."
        )
        return False

    print(
        "  ✓ Create Trade clicked."
    )

    return True


def accept_trade_confirmation(driver):
    """
    The site uses JavaScript confirm():

        proceed with trade

        OK / Cancel

    Selenium exposes this as a browser alert.
    """

    print(
        "  Waiting for trade confirmation..."
    )

    try:
        WebDriverWait(
            driver,
            10,
        ).until(
            lambda d: d.switch_to.alert
        )

        alert = driver.switch_to.alert

        text = alert.text.strip()

        print(
            f"  Confirmation: {text}"
        )

        alert.accept()

        print(
            "  ✓ Trade confirmation accepted."
        )

        return True

    except TimeoutException:
        print(
            "  ⚠ No browser confirmation appeared."
        )

        return True

    except Exception as e:
        print(
            f"  ✗ Could not handle trade confirmation: {e}"
        )
        return False


# ============================================================
# OPEN CREATE-A-TRADE
# ============================================================

def open_create_trade(driver):
    print()
    print("Opening Create A Trade...")

    link = find_first(
        driver,
        [
            (
                By.XPATH,
                "//a[contains("
                "translate("
                "normalize-space(.),"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'"
                "),"
                "'create a trade'"
                ")]",
            ),
            (
                By.CSS_SELECTOR,
                "a[href*='create_a_trade']",
            ),
        ],
    )

    if not link:
        print(
            "  ✗ Create A Trade link not found."
        )
        return False

    print(
        f"  ✓ Create A Trade found: "
        f"'{link.text.strip()}'"
    )

    if not click_element(
        driver,
        link,
    ):
        print(
            "  ✗ Could not click Create A Trade."
        )
        return False

    wait_ready(driver)

    print(
        "✓ Create A Trade page opened."
    )

    return True


# ============================================================
# MAIN TRADE FLOW
# ============================================================

def trade_mode(driver):
    print(
        "\n"
        + "=" * 60
        + "\nTRADE MODE\n"
        + "=" * 60
    )

    try:

        # ----------------------------------------------------
        # Make sure we're on the Trading Center.
        # ----------------------------------------------------

        current_url = driver.current_url.lower()

        if "create_a_trade" not in current_url:

            trading_link = find_first(
                driver,
                [
                    (
                        By.CSS_SELECTOR,
                        "a[href*='trading_center']",
                    ),
                    (
                        By.XPATH,
                        "//a[normalize-space(.)='Trades']",
                    ),
                ],
            )

            if trading_link:

                print(
                    "Opening Trading Center..."
                )

                if not click_element(
                    driver,
                    trading_link,
                ):
                    print(
                        "  ✗ Could not open Trading Center."
                    )
                    return

                wait_ready(driver)

        # ----------------------------------------------------
        # Open Create A Trade.
        # ----------------------------------------------------

        if "create_a_trade" not in driver.current_url.lower():

            if not open_create_trade(driver):
                return

        # ----------------------------------------------------
        # Set recipient.
        # ----------------------------------------------------

        if not set_recipient(driver):
            return

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # The recipient is entered first.
        #
        # The website requires:
        #
        # CAT_Submit
        #
        # "Initiate Trade"
        #
        # before CAT_User / CAT_Recipient are
        # populated.
        # ----------------------------------------------------

        if not initiate_trade(driver):
            return

        # ----------------------------------------------------
        # Pokémon.
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("POKÉMON TO TRADE")
        print("=" * 60)

        print()
        print("Examples:")
        print("  gastly")
        print("  crystal gastly")
        print("  all gastlys")
        print("  all crystal gastlys")

        request = input(
            "\nPokemon to trade: "
        ).strip()

        if not request:
            print(
                "✗ Pokémon request cannot be empty."
            )
            return

        quantity = ask_quantity(
            request
        )

        # ----------------------------------------------------
        # Select Pokémon.
        # ----------------------------------------------------

        if not select_pokemon(
            driver,
            request,
            quantity,
        ):
            return

        # ----------------------------------------------------
        # Final confirmation from our bot.
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("TRADE READY")
        print("=" * 60)

        print(
            "The selected Pokémon are ready "
            "to be traded."
        )

        confirm = input(
            "\nCreate this trade? [Y/n]: "
        ).strip().lower()

        if confirm not in (
            "",
            "y",
            "yes",
        ):
            print(
                "Trade cancelled."
            )
            return

        # ----------------------------------------------------
        # Click Create Trade.
        # ----------------------------------------------------

        if not click_create_trade(
            driver
        ):
            return

        # ----------------------------------------------------
        # Website confirmation:
        #
        # "proceed with trade"
        #
        # OK / Cancel
        # ----------------------------------------------------

        if not accept_trade_confirmation(
            driver
        ):
            return

        wait_ready(driver)

        print()
        print("=" * 60)
        print("✓ TRADE SUBMITTED")
        print("=" * 60)

        print(
            "\nReturning to main menu..."
        )

    except Exception as e:
        print(
            f"\n✗ Trade mode error: {e}"
        )