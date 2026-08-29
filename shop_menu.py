"""
Shop menu for Eclipse RPG Automation.

Handles Item Shop placeholder and Buy Pokémon marketplace queries.
"""

import os
import sys
import platform
import time
import re
import requests

from buy_pokemon import (
    PokemonShop,
    POKEMON_TYPES,
    format_listing,
)


# ============================================================
# ANSI & STYLING
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

ANSI_STRIP_REGEX = re.compile(r"\x1b\[[0-9;]*[mK]")


def _strip_ansi(text: str) -> str:
    return ANSI_STRIP_REGEX.sub("", text)


def _row(content: str, width: int = 71) -> str:
    v_len = len(_strip_ansi(content))
    pad = max(0, width - v_len)
    return f"{BORDER_COLOR}║{RESET}{content}{' ' * pad}{BORDER_COLOR}║{RESET}"


def _build_session_from_driver(driver):
    session = requests.Session()
    session.headers.update({
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
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
    w = 56
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {YELLOW}✦ FEATURE IN DEVELOPMENT ✦{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  Section: {BOLD}{WHITE}Item Shop & Market{RESET}"))
    print(_drow(""))
    print(_drow(f"  {GRAY}Item Shop automation has not been implemented yet.{RESET}"))
    print(_drow(f"  {GRAY}Requires HTML evidence of /item_shop in Ideas.md.{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()

    input(f"{GRAY}Press Enter to return to the shop menu...{RESET}")


def _prompt_pokemon_type():
    print()
    print(f"{CATEGORY_COLOR}Filter by Pokémon Variant / Type (optional):{RESET}")
    print(f"  {KEY_COLOR}[ 0]{RESET} All types")

    for i, pokemon_type in enumerate(POKEMON_TYPES, 1):
        print(f"  {KEY_COLOR}[{i:2d}]{RESET} {pokemon_type}")

    choice = input(f"\n{BOLD}{CYAN}❯ Choose variant number {GRAY}[blank for all]{CYAN}:{RESET} ").strip()

    if not choice:
        return ""

    try:
        index = int(choice)
    except ValueError:
        print(f"{YELLOW}⚠ Invalid choice - showing all types.{RESET}")
        return ""

    if index == 0:
        return ""

    if 1 <= index <= len(POKEMON_TYPES):
        return POKEMON_TYPES[index - 1]

    print(f"{YELLOW}⚠ Invalid choice - showing all types.{RESET}")
    return ""


def _buy_pokemon_menu(driver):
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}🛒  BUY POKÉMON MARKETPLACE{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Search & filter player market listings.{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()

    name_filter = input(f"{BOLD}{CYAN}❯ Pokémon Name {GRAY}[blank for any]{CYAN}:{RESET} ").strip()
    type_filter = _prompt_pokemon_type()

    print(f"\n{CYAN}⚡ Searching the marketplace...{RESET}")

    try:
        session = _build_session_from_driver(driver)
        shop = PokemonShop(session)
        listings = shop.search(
            pokemon_name=name_filter,
            pokemon_type=type_filter,
        )
    except requests.RequestException as error:
        print(f"{RED}✗ Request failed: {error}{RESET}")
        print(f"{GRAY}  (Cloudflare may be challenging requests - see notes in shop_menu.py){RESET}")
        input(f"\n{GRAY}Press Enter to return to the shop menu...{RESET}")
        return

    if not listings:
        print(f"\n{YELLOW}No marketplace listings found matching your search.{RESET}")
        input(f"\n{GRAY}Press Enter to return to the shop menu...{RESET}")
        return

    print()
    print(f"{GOLD}Marketplace Listings ({len(listings)} found):{RESET}\n")
    for index, listing in enumerate(listings, 1):
        print(f"  {KEY_COLOR}[{index:2d}]{RESET} {WHITE}{format_listing(listing)}{RESET}")

    choice = input(f"\n{BOLD}{CYAN}❯ Enter listing number to inspect/buy {GRAY}[or press Enter to return]{CYAN}:{RESET} ").strip()
    if not choice:
        return

    try:
        index = int(choice)
        listing = listings[index - 1]
    except (ValueError, IndexError):
        print(f"{RED}✗ Invalid selection.{RESET}")
        time.sleep(1.0)
        return

    dw = 60
    def _ddrow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, dw - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * dw}╮{RESET}")
    print(_ddrow(f"  {BOLD}{MAGENTA}LISTING DETAIL{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * dw}┤{RESET}")
    print(_ddrow(f"  {WHITE}{format_listing(listing)}{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * dw}╯{RESET}")

    if not listing.can_buy:
        print(f"\n{YELLOW}⚠ This listing does not have a valid direct Buy ID.{RESET}")
        input(f"\n{GRAY}Press Enter to return to the shop menu...{RESET}")
        return

    confirm = input(f"\n{BOLD}{CYAN}❯ Attempt to buy this Pokémon? [y/N]:{RESET} ").strip().lower()
    if confirm != "y":
        print(f"\n{GRAY}Cancelled.{RESET}")
        time.sleep(0.8)
        return

    try:
        shop.buy(listing)
        print(f"\n{GREEN}✓ Purchase request successfully sent.{RESET}")
    except NotImplementedError:
        print(f"\n{YELLOW}⚠ Direct purchase endpoint payload is not yet wired up.{RESET}")
    except requests.RequestException as error:
        print(f"\n{RED}✗ Purchase request failed: {error}{RESET}")

    input(f"\n{GRAY}Press Enter to return to the shop menu...{RESET}")


def shop_menu(driver):
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    while True:
        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}🛒  SHOPS & MARKETPLACE{RESET}", w))
        print(mid_border)
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 1]{RESET} {NAME_COLOR}Item Shop{RESET}        {DESC_COLOR}— Poké Balls, potions & stones (WIP){RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 2]{RESET} {NAME_COLOR}Buy Pokémon{RESET}      {DESC_COLOR}— Search & purchase Pokémon from player market{RESET}", w))
        print(_row("", w))
        print(_row(f"    {RED}{BOLD}[ 3]{RESET} {RED}Back{RESET}             {DESC_COLOR}— Return to main menu{RESET}", w))
        print(_row("", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-3]{CYAN}:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            _item_shop()
        elif choice == "2":
            _buy_pokemon_menu(driver)
        elif choice == "3":
            return
        else:
            print(f"\n{RED}✗ Invalid choice '{choice}'. Please choose 1-3.{RESET}")
            time.sleep(1.0)
