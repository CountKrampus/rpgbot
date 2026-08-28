"""
Shop menu for Eclipse RPG Automation.

Keeps the different shop systems separated:

    Item Shop     - not yet implemented (no real HTML seen yet)
    Buy Pokemon   - real, via buy_pokemon.py

IMPORTANT ARCHITECTURE NOTE:

Every other module in this bot (search.py, capture.py,
training.py, messages.py, box.py) drives the site through
Selenium - the login itself happens in the real browser
(login.py), and session state lives in the browser's cookies.

buy_pokemon.py was written against `requests` + BeautifulSoup
instead, which is a different HTTP client with no browser
session of its own. To make it actually work against the
logged-in account, this file copies the Selenium driver's
cookies into a requests.Session before using PokemonShop.

CAVEAT: Eclipse RPG sits behind Cloudflare (visible from the
Rocket Loader / __cfRLUnblockHandlers script patterns on every
page). Copying cookies gets a requests.Session the right
authentication, but Cloudflare can still challenge or block
plain `requests` traffic based on TLS/JS fingerprinting in ways
copying cookies doesn't fix. If Buy Pokemon searches start
failing or returning Cloudflare challenge pages instead of real
results, that's almost certainly why - the fix at that point
would be rewriting this module in Selenium like everything
else, not tweaking the cookie bridge.
"""

import requests

from buy_pokemon import (
    PokemonShop,
    POKEMON_TYPES,
    format_listing,
)


def _build_session_from_driver(driver):
    """
    Copy the Selenium driver's current cookies into a fresh
    requests.Session, so PokemonShop makes authenticated
    requests as the logged-in account instead of an anonymous
    session.
    """

    session = requests.Session()

    session.headers.update({
        "User-Agent": driver.execute_script(
            "return navigator.userAgent;"
        ),
    })

    for cookie in driver.get_cookies():

        session.cookies.set(
            cookie.get("name"),
            cookie.get("value"),
            domain=cookie.get("domain"),
            path=cookie.get("path", "/"),
        )

    return session


def _item_shop():

    print()
    print("=" * 60)
    print("ITEM SHOP")
    print("=" * 60)
    print()
    print(
        "Item Shop isn't implemented yet - no real HTML from "
        "/item_shop has been provided, so nothing here is built "
        "on guesses."
    )

    input("\nPress Enter to return to the shop menu...")


def _prompt_pokemon_type():

    print()
    print("Filter by type (optional):")
    print("  0. All types")

    for i, pokemon_type in enumerate(POKEMON_TYPES, 1):
        print(f"  {i}. {pokemon_type}")

    choice = input(
        "\nChoose a number (blank for all types): "
    ).strip()

    if not choice:
        return ""

    try:
        index = int(choice)

    except ValueError:
        print("✗ Invalid choice - using all types.")
        return ""

    if index == 0:
        return ""

    if 1 <= index <= len(POKEMON_TYPES):
        return POKEMON_TYPES[index - 1]

    print("✗ Invalid choice - using all types.")
    return ""


def _buy_pokemon_menu(driver):

    print()
    print("=" * 60)
    print("BUY POKEMON")
    print("=" * 60)

    name_filter = input(
        "\nPokemon name (blank for any): "
    ).strip()

    type_filter = _prompt_pokemon_type()

    print("\nSearching the marketplace...")

    try:

        session = _build_session_from_driver(driver)

        shop = PokemonShop(session)

        listings = shop.search(
            pokemon_name=name_filter,
            pokemon_type=type_filter,
        )

    except requests.RequestException as error:

        print(f"✗ Request failed: {error}")
        print(
            "  (If this keeps happening, it's likely "
            "Cloudflare blocking non-browser traffic - see "
            "the note at the top of this file.)"
        )

        input("\nPress Enter to return to the shop menu...")
        return

    if not listings:

        print("\nNo listings found.")
        input("\nPress Enter to return to the shop menu...")
        return

    print()

    for index, listing in enumerate(listings, 1):
        print(f"{index:3}. {format_listing(listing)}")

    choice = input(
        "\nEnter a number to view/buy, or press Enter to go back: "
    ).strip()

    if not choice:
        return

    try:
        index = int(choice)
        listing = listings[index - 1]

    except (ValueError, IndexError):
        print("✗ Invalid selection.")
        input("\nPress Enter to return to the shop menu...")
        return

    print()
    print("=" * 60)
    print(format_listing(listing))
    print("=" * 60)

    if not listing.can_buy:

        print("\nThis listing doesn't have a valid Buy ID.")
        input("\nPress Enter to return to the shop menu...")
        return

    confirm = input(
        "\nAttempt to buy this Pokemon? [y/N]: "
    ).strip().lower()

    if confirm != "y":
        print("\nCancelled.")
        input("\nPress Enter to return to the shop menu...")
        return

    try:

        shop.buy(listing)

        print("✓ Purchase request sent.")

    except NotImplementedError:

        print(
            "✗ Purchasing isn't wired up yet - the site's "
            "actual purchase request (endpoint/payload) hasn't "
            "been captured, so this deliberately doesn't guess "
            "at it rather than risk sending a bad request."
        )

    except requests.RequestException as error:

        print(f"✗ Purchase request failed: {error}")

    input("\nPress Enter to return to the shop menu...")


def shop_menu(driver):
    while True:

        print()
        print("=" * 60)
        print("SHOPS")
        print("=" * 60)
        print()
        print("1. Item Shop")
        print("2. Buy Pokemon")
        print("3. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            _item_shop()

        elif choice == "2":
            _buy_pokemon_menu(driver)

        elif choice == "3":
            return

        else:
            print("✗ Invalid choice.")
