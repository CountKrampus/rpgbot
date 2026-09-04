"""
Eclipse RPG - Account Management & Account Dashboard

Handles saved accounts, keyring storage, dynamic profile discovery,
and trainer dashboard views.
"""

from __future__ import annotations

import json
import os
import re
import sys
import platform
import time
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

try:
    from secure_storage import SecureStorage
    keyring_available = True
except ImportError:
    keyring_available = False


# ============================================================
# CONSOLE & COLOR SETUP
# ============================================================

def _init_console():
    """
    Ensure UTF-8 encoding and ANSI color support on Windows.
    """
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if platform.system() == "Windows":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            mode = ctypes.c_ulong()
            h_out = kernel32.GetStdHandle(-11)
            if kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
                kernel32.SetConsoleMode(h_out, mode.value | 0x0004)
        except Exception:
            pass
        os.system("")


_init_console()

# ANSI Color Palette
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

import unicodedata

ANSI_STRIP_REGEX = re.compile(r"\x1b\[[0-9;]*[mK]")


def _vis_len(text: str) -> int:
    """Calculate terminal display column width, handling ANSI and 2-column emojis."""
    clean = ANSI_STRIP_REGEX.sub("", text)
    w = 0
    for ch in clean:
        if unicodedata.east_asian_width(ch) in ("W", "F") or ord(ch) >= 0x1F300:
            w += 2
        elif ord(ch) == 0xFE0F:  # Variation selector (zero-width)
            continue
        else:
            w += 1
    return w


def _row(content: str, width: int = 71) -> str:
    v_len = _vis_len(content)
    pad = max(0, width - v_len)
    return f"{BORDER_COLOR}║{RESET}{content}{' ' * pad}{BORDER_COLOR}║{RESET}"


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://eclipserpg.com"
PROFILE_URL_TEMPLATE = f"{BASE_URL}/user?id={{user_id}}"
LEGENDARY_AREAS_URL = f"{BASE_URL}/legendary_areas"
ACCOUNT_FILE = Path.home() / ".eclipse_rpg_accounts.json"
KEYRING_SERVICE = "eclipse-rpg-automation"


# ============================================================
# ACCOUNT STORAGE
# ============================================================

def get_accounts() -> list[str]:
    try:
        if not ACCOUNT_FILE.exists():
            return []

        with ACCOUNT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return [str(item) for item in data if str(item).strip()]

        if isinstance(data, dict):
            accounts = data.get("accounts", [])
            if isinstance(accounts, list):
                return [str(item) for item in accounts if str(item).strip()]
    except Exception:
        pass

    return []


def _write_accounts(accounts: list[str]) -> None:
    ACCOUNT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with ACCOUNT_FILE.open("w", encoding="utf-8") as file:
        json.dump({"accounts": accounts}, file, indent=4)


def save_account_name(username: str) -> None:
    username = username.strip()
    if not username:
        return

    accounts = get_accounts()
    if username not in accounts:
        accounts.append(username)
        _write_accounts(accounts)


def remove_account_name(username: str) -> None:
    username = username.strip()
    accounts = get_accounts()

    if username in accounts:
        accounts.remove(username)
        _write_accounts(accounts)

    if keyring_available:
        try:
            SecureStorage.remove_credential(username)
        except Exception:
            pass


def get_saved_password(username: str) -> Optional[str]:
    if not username:
        return None

    if not keyring_available:
        return None

    try:
        return SecureStorage.get_credential(username)
    except Exception:
        return None


def save_password(username: str, password: str) -> None:
    if not username or not keyring_available:
        return

    try:
        SecureStorage.save_credential(username, password)
    except Exception:
        pass


def add_account(username: Optional[str] = None, password: Optional[str] = None) -> Optional[str]:
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}➕  ADD NEW ECLIPSE RPG ACCOUNT{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Credentials are encrypted securely via system keyring.{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()

    if username is None:
        username = input(f"{BOLD}{CYAN}❯ Username:{RESET} ").strip()

    if not username:
        print(f"{RED}✗ Username cannot be blank.{RESET}")
        time.sleep(1.0)
        return None

    if password is None:
        try:
            from getpass import getpass
            password = getpass(f"{BOLD}{CYAN}❯ Password (hidden):{RESET} ")
        except Exception:
            password = input(f"{BOLD}{CYAN}❯ Password:{RESET} ")

    save_account_name(username)

    if password:
        save_password(username, password)

    print(f"\n{GREEN}✓ Account '{username}' saved securely to keyring!{RESET}\n")
    time.sleep(1.0)
    return username


# ============================================================
# ACCOUNT SELECTOR (LAUNCHER SCREEN)
# ============================================================

def account_selector() -> Optional[str]:
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    banner_art = [
        f"  {MAGENTA}███████╗ ██████╗██╗     ██╗██████╗ ███████╗    ██████╗ ██████╗  ██████╗{RESET}  ",
        f"  {MAGENTA}██╔════╝██╔════╝██║     ██║██╔══██╗██╔════╝    ██╔══██╗██╔══██╗██╔════╝{RESET}  ",
        f"  {PURPLE}█████╗  ██║     ██║     ██║██████╔╝███████╗    ██████╔╝██████╔╝██║  ███╗{RESET}  ",
        f"  {PURPLE}██╔══╝  ██║     ██║     ██║██╔═══╝ ╚════██║    ██╔══██╗██╔═══╝ ██║   ██║{RESET}  ",
        f"  {CYAN}███████╗╚██████╗███████╗██║██║     ███████║    ██║  ██║██║     ╚██████╔╝{RESET}  ",
        f"  {CYAN}╚══════╝ ╚═════╝╚══════╝╚═╝╚═╝     ╚══════╝    ╚═╝  ╚═╝╚═╝      ╚═════╝{RESET}  ",
    ]

    while True:
        accounts = get_accounts()
        sec_status = f"{GREEN}Keyring (Encrypted){RESET}" if keyring_available else f"{YELLOW}File Storage{RESET}"
        hud = f"  {GRAY}PROFILES:{RESET} {CYAN}{len(accounts)} Saved{RESET}  │  {GRAY}SECURITY:{RESET} {sec_status}  │  {GRAY}STATUS:{RESET} {GREEN}Ready{RESET}"

        print()
        print(top_border)
        for line in banner_art:
            print(_row(line, w))
        print(mid_border)
        print(_row(f"  {BOLD}{MAGENTA}👤  ACCOUNT MANAGER & PROFILE SELECTOR{RESET}", w))
        print(mid_border)
        print(_row(hud, w))
        print(mid_border)
        print(_row("", w))

        if accounts:
            print(_row(f"  {CATEGORY_COLOR}SAVED PROFILES{RESET}", w))
            for index, username in enumerate(accounts, 1):
                disp_user = username[:16]
                print(_row(f"    {KEY_COLOR}[{index:2d}]{RESET} {NAME_COLOR}{disp_user:<16}{RESET} {DESC_COLOR}— Active profile with encrypted credentials{RESET}", w))
            print(_row("", w))
            print(_row(f"  {CATEGORY_COLOR}PROFILE ACTIONS{RESET}", w))
            print(_row(f"    {KEY_COLOR}[ A]{RESET} {WHITE}Add New Account{RESET}   {DESC_COLOR}— Register username & encrypted password{RESET}", w))
            print(_row(f"    {KEY_COLOR}[ R]{RESET} {WHITE}Remove Account{RESET}    {DESC_COLOR}— Delete saved profile from keyring{RESET}", w))
            print(_row("", w))
            print(_row(f"    {RED}{BOLD}[ 0]{RESET} {RED}Exit Launcher{RESET}     {DESC_COLOR}— Close automation suite{RESET}", w))
            print(_row("", w))
            print(bot_border)

            try:
                choice = input(f"\n{BOLD}{CYAN}❯ Select Account {GRAY}[1-{len(accounts)}, A, R, 0]{CYAN}:{RESET} ").strip()
            except (KeyboardInterrupt, EOFError):
                return None

            if choice == "0":
                return None

            if choice.lower() == "a":
                add_account()
                continue

            if choice.lower() == "r":
                dw = 60
                def _drow(content):
                    vlen = len(_strip_ansi(content))
                    pad = max(0, dw - vlen)
                    return f"{RED}│{RESET}{content}{' ' * pad}{RED}│{RESET}"

                remove_choice = input(f"\n{BOLD}{RED}❯ Enter account list # to remove {GRAY}[1-{len(accounts)}]{RED}:{RESET} ").strip()
                try:
                    index = int(remove_choice)
                    if not (1 <= index <= len(accounts)):
                        raise ValueError
                    username = accounts[index - 1]

                    print()
                    print(f"{RED}╭{'─' * dw}╮{RESET}")
                    print(_drow(f"  {BOLD}{RED}⚠  CONFIRM PROFILE DELETION{RESET}"))
                    print(f"{RED}├{'─' * dw}┤{RESET}")
                    print(_drow(f"  Target Account: {WHITE}{username}{RESET}"))
                    print(_drow(f"  {GRAY}This removes saved credentials from your system keyring.{RESET}"))
                    print(f"{RED}╰{'─' * dw}╯{RESET}")
                    print()

                    confirm = input(f"{BOLD}{RED}❯ Remove '{username}'? [y/N]:{RESET} ").strip().lower()
                    if confirm == "y":
                        remove_account_name(username)
                        print(f"\n{GREEN}✓ Account '{username}' removed successfully.{RESET}")
                        time.sleep(1.0)
                except ValueError:
                    print(f"{RED}✗ Invalid account number.{RESET}")
                    time.sleep(1.0)
                continue

            try:
                index = int(choice)
                if not (1 <= index <= len(accounts)):
                    raise ValueError
                return accounts[index - 1]
            except ValueError:
                print(f"\n{RED}✗ Invalid selection. Please choose an account number or A/R/0.{RESET}")
                time.sleep(1.0)

        else:
            print(_row(f"    {YELLOW}No saved accounts found. Please add an account to begin.{RESET}", w))
            print(_row("", w))
            print(_row(f"    {KEY_COLOR}[ 1]{RESET} {WHITE}Add New Account{RESET}       {DESC_COLOR}— Enter username & password{RESET}", w))
            print(_row(f"    {RED}{BOLD}[ 0]{RESET} {RED}Exit Launcher{RESET}         {DESC_COLOR}— Close automation suite{RESET}", w))
            print(_row("", w))
            print(bot_border)

            try:
                choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1, 0]{CYAN}:{RESET} ").strip()
            except (KeyboardInterrupt, EOFError):
                return None

            if choice == "1":
                username = add_account()
                if username:
                    return username
            elif choice == "0":
                return None
            else:
                print(f"\n{RED}✗ Invalid choice.{RESET}")
                time.sleep(1.0)


# ============================================================
# GENERAL HELPERS
# ============================================================

def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _strip_ansi(text: str) -> str:
    """Remove ANSI color codes from text for accurate length calculation."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def _get_soup(driver) -> BeautifulSoup:
    try:
        return BeautifulSoup(driver.page_source, "html.parser")
    except Exception:
        return BeautifulSoup("", "html.parser")


def _parse_user_id(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        values = params.get("id")
        if values:
            user_id = str(values[0]).strip()
            if user_id.isdigit():
                return user_id
    except Exception:
        pass
    return None


# ============================================================
# DYNAMIC PROFILE LOOKUP
# ============================================================

def find_user_profile_url(driver) -> Optional[str]:
    try:
        current_url = driver.current_url
    except Exception:
        current_url = ""

    current_id = _parse_user_id(current_url)
    if current_id and "/user" in current_url.lower():
        return f"{BASE_URL}/user?id={current_id}"

    selectors = [
        (By.CSS_SELECTOR, "a[href*='/user?id=']"),
        (By.XPATH, "//a[contains(@href,'/user?id=')]"),
    ]

    candidates = []
    for by, selector in selectors:
        try:
            elements = driver.find_elements(by, selector)
        except Exception:
            continue

        for element in elements:
            try:
                href = element.get_attribute("href") or ""
                text = _clean_text(element.text)
                user_id = _parse_user_id(href)
                if user_id:
                    candidates.append({"id": user_id, "href": href, "text": text})
            except (StaleElementReferenceException, WebDriverException):
                continue

    if not candidates:
        return None

    preferred_words = ("profile", "account", "my profile", "my account")
    for candidate in candidates:
        text = candidate["text"].lower()
        if any(word in text for word in preferred_words):
            return f"{BASE_URL}/user?id={candidate['id']}"

    return f"{BASE_URL}/user?id={candidates[0]['id']}"


def open_user_profile(driver) -> Optional[str]:
    profile_url = find_user_profile_url(driver)
    if not profile_url:
        return None

    try:
        if driver.current_url != profile_url:
            driver.get(profile_url)
            time.sleep(0.6)
        return profile_url
    except Exception:
        return None


def _find_value_by_label(soup: BeautifulSoup, label: str) -> str:
    wanted = label.strip().rstrip(":").lower()
    for cell in soup.find_all(["td", "th", "div", "span", "strong", "b"]):
        text = _clean_text(cell.get_text(" ", strip=True))
        if text.rstrip(":").lower() != wanted:
            continue

        next_cell = cell.find_next_sibling(["td", "th", "div", "span"])
        if next_cell is not None:
            value = _clean_text(next_cell.get_text(" ", strip=True))
            if value:
                return value

    return "Unknown"


def _find_first_value(soup: BeautifulSoup, labels: list[str]) -> str:
    for label in labels:
        value = _find_value_by_label(soup, label)
        if value != "Unknown":
            return value
    return "Unknown"


# ============================================================
# ACCOUNT DASHBOARD STATS
# ============================================================

def get_account_profile(driver) -> dict[str, str]:
    profile_url = open_user_profile(driver)
    if not profile_url:
        return {}

    soup = _get_soup(driver)
    user_id = _parse_user_id(profile_url)

    return {
        "User ID": user_id if user_id else "Unknown",
        "Username": _find_first_value(soup, ["Username", "User Name"]),
        "Trainer Title": _find_first_value(soup, ["Trainer Title", "Title"]),
        "Trainer Gender": _find_first_value(soup, ["Trainer Gender", "Gender"]),
        "User Group": _find_first_value(soup, ["User Group", "Group"]),
        "Map Level": _find_first_value(soup, ["Map Level"]),
        "Trainer Level": _find_first_value(soup, ["Trainer Level", "Level"]),
        "Trainer EXP": _find_first_value(soup, ["Trainer EXP", "Trainer Experience", "EXP", "Experience"]),
        "Mining Level": _find_first_value(soup, ["Mining Level"]),
        "AP / Team": _find_first_value(soup, ["AP / Team", "AP", "Team"]),
        "Battles Won": _find_first_value(soup, ["Battles Won", "Battle Wins"]),
        "Date Registered": _find_first_value(soup, ["Date Registered", "Registered"]),
        "Last Login": _find_first_value(soup, ["Last Login"]),
        "Play Time": _find_first_value(soup, ["Play Time", "Playtime"]),
    }


def display_account_overview(driver) -> None:
    print(f"\n{CYAN}⚡ Loading account profile details...{RESET}")
    data = get_account_profile(driver)

    w = 64
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}👤  ACCOUNT OVERVIEW{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    if not data:
        print(_drow(f"  {RED}✗ Could not load account profile.{RESET}"))
    else:
        for label, value in data.items():
            print(_drow(f"  {GRAY}{label:<18}:{RESET} {WHITE}{value}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


def get_account_currencies(driver) -> dict[str, str]:
    profile_url = find_user_profile_url(driver)
    if profile_url:
        try:
            if driver.current_url != profile_url:
                driver.get(profile_url)
                time.sleep(0.4)
        except Exception:
            pass

    soup = _get_soup(driver)
    return {
        "Platinum Coins": _find_first_value(soup, ["Platinum Coins", "Platinum"]),
        "Diamond Coins": _find_first_value(soup, ["Diamond Coins", "Diamond"]),
        "Moon Points": _find_first_value(soup, ["Moon Points", "Moon"]),
    }


def display_account_currencies(driver) -> None:
    print(f"\n{CYAN}⚡ Loading currency and resource balances...{RESET}")
    currencies = get_account_currencies(driver)

    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}💰  CURRENCY & RESOURCES{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    for name, value in currencies.items():
        print(_drow(f"  {GOLD}● {name:<18}:{RESET} {WHITE}{value}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


def get_map_statistics(driver) -> list[dict[str, str]]:
    try:
        driver.get(LEGENDARY_AREAS_URL)
        time.sleep(0.5)
    except Exception:
        return []

    soup = _get_soup(driver)
    results = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        header_cells = rows[0].find_all(["th", "td"])
        headers = [_clean_text(cell.get_text(" ", strip=True)).lower() for cell in header_cells]

        if not any("map name" in header for header in headers):
            continue

        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            values = [_clean_text(cell.get_text(" ", strip=True)) for cell in cells]
            map_name = values[0]
            if not map_name or map_name.lower() in ("total", "totals"):
                continue

            results.append({
                "map": map_name,
                "total": values[1] if len(values) > 1 else "0",
                "today": values[2] if len(values) > 2 else "0",
            })

    return results


def display_map_statistics(driver) -> None:
    print(f"\n{CYAN}⚡ Loading legendary area and map statistics...{RESET}")
    maps = get_map_statistics(driver)

    w = 68
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}🗺️   MAP & LEGENDARY AREA STATISTICS{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}{'MAP NAME':<34} {'TOTAL':>12} {'TODAY':>14}{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    if not maps:
        print(_drow(f"  {YELLOW}No map statistics found.{RESET}"))
    else:
        total_searches = 0
        today_searches = 0
        for item in maps:
            try:
                total = int(re.sub(r"[^\d]", "", item["total"]) or "0")
            except ValueError:
                total = 0
            try:
                today = int(re.sub(r"[^\d]", "", item["today"]) or "0")
            except ValueError:
                today = 0
            total_searches += total
            today_searches += today
            print(_drow(f"  {WHITE}{item['map'][:32]:<34}{RESET} {CYAN}{total:>12,}{RESET} {GREEN}{today:>14,}{RESET}"))

        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {GOLD}{'TOTALS':<34}{RESET} {CYAN}{total_searches:>12,}{RESET} {GREEN}{today_searches:>14,}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


def get_pokemon_statistics(driver) -> dict[str, str]:
    profile_url = find_user_profile_url(driver)
    if profile_url:
        try:
            if driver.current_url != profile_url:
                driver.get(profile_url)
                time.sleep(0.4)
        except Exception:
            pass

    soup = _get_soup(driver)
    return {
        "Pokémon Owned": _find_first_value(soup, ["Pokémon Owned", "Pokemon Owned", "Pokémon", "Pokemon"]),
        "Pokémon Caught": _find_first_value(soup, ["Pokémon Caught", "Pokemon Caught", "Caught"]),
        "Unique Pokémon": _find_first_value(soup, ["Unique Pokémon", "Unique Pokemon"]),
        "Shiny": _find_first_value(soup, ["Shiny"]),
        "Dark": _find_first_value(soup, ["Dark"]),
        "Golden": _find_first_value(soup, ["Golden"]),
        "Crystal": _find_first_value(soup, ["Crystal"]),
    }


def display_pokemon_statistics(driver) -> None:
    print(f"\n{CYAN}⚡ Loading Pokémon collection statistics...{RESET}")
    stats = get_pokemon_statistics(driver)

    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}📊  POKÉMON COLLECTION STATISTICS{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    for name, value in stats.items():
        print(_drow(f"  {GRAY}{name:<20}:{RESET} {WHITE}{value}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


def get_battle_statistics(driver) -> dict[str, str]:
    profile_url = find_user_profile_url(driver)
    if profile_url:
        try:
            if driver.current_url != profile_url:
                driver.get(profile_url)
                time.sleep(0.4)
        except Exception:
            pass

    soup = _get_soup(driver)
    return {
        "Battles Won": _find_first_value(soup, ["Battles Won", "Battle Wins"]),
        "Trainer Level": _find_first_value(soup, ["Trainer Level", "Level"]),
        "Trainer EXP": _find_first_value(soup, ["Trainer EXP", "Trainer Experience", "EXP", "Experience"]),
        "Mining Level": _find_first_value(soup, ["Mining Level"]),
    }


def display_battle_statistics(driver) -> None:
    print(f"\n{CYAN}⚡ Loading battle records...{RESET}")
    stats = get_battle_statistics(driver)

    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}⚔️   BATTLE & TRAINER STATISTICS{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    for name, value in stats.items():
        print(_drow(f"  {GRAY}{name:<18}:{RESET} {WHITE}{value}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


def display_marketplace(driver) -> None:
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}🛒  MARKETPLACE VALUATION{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Advanced market valuation & listing analysis.{RESET}"))
    print(_drow(""))
    print(_drow(f"  {WHITE}● Evaluate Pokémon values based on market prices{RESET}"))
    print(_drow(f"  {WHITE}● Check live competitor listings & price floors{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


def _get_capture_stats() -> dict:
    try:
        import capture
        stats = getattr(capture, "_capture_stats", {})
        if isinstance(stats, dict):
            return {str(k): int(v) for k, v in stats.items() if isinstance(v, (int, float))}
    except Exception:
        pass
    return {}


def _get_search_stats() -> dict:
    try:
        import search
        for name in ("_search_stats", "search_stats", "SEARCH_STATS"):
            stats = getattr(search, name, None)
            if isinstance(stats, dict):
                result = {str(k): int(v) for k, v in stats.items() if isinstance(v, (int, float))}
                if result:
                    return result
    except Exception:
        pass
    return {}


def display_account_activity(driver) -> None:
    capture_stats = _get_capture_stats()
    search_stats = _get_search_stats()

    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}📈  BOT SESSION ACTIVITY{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Encounters:  {RESET} {WHITE}{capture_stats.get('encounters', 0):,}{RESET}"))
    print(_drow(f"  {GRAY}Captured:    {RESET} {GREEN}{capture_stats.get('captured', 0):,}{RESET}"))
    print(_drow(f"  {GRAY}Failed:      {RESET} {RED}{capture_stats.get('failed', 0):,}{RESET}"))

    if search_stats:
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        for key, value in search_stats.items():
            label = key.replace("_", " ").title()
            print(_drow(f"  {GRAY}{label:<14}:{RESET} {CYAN}{value:,}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


# ============================================================
# ACCOUNT DASHBOARD MENU
# ============================================================

def account_menu(driver) -> None:
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    while True:
        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}👤  ACCOUNT & TRAINER DASHBOARD{RESET}", w))
        print(mid_border)
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 1]{RESET} {NAME_COLOR}Account Overview{RESET}      {DESC_COLOR}— View trainer stats, levels, title & play time{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 2]{RESET} {NAME_COLOR}Currency & Resources{RESET}  {DESC_COLOR}— Platinum coins, diamond coins & moon points{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 3]{RESET} {NAME_COLOR}Map Statistics{RESET}        {DESC_COLOR}— Lifetime & daily searches across areas{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 4]{RESET} {NAME_COLOR}Pokémon Statistics{RESET}    {DESC_COLOR}— Total caught, unique species & variants owned{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 5]{RESET} {NAME_COLOR}Battle Statistics{RESET}     {DESC_COLOR}— Battle win records, trainer level & mining EXP{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 6]{RESET} {NAME_COLOR}Marketplace{RESET}           {DESC_COLOR}— Market valuation & price comparison tools{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 7]{RESET} {NAME_COLOR}Account Activity{RESET}      {DESC_COLOR}— Live session search & capture milestones{RESET}", w))
        print(_row("", w))
        print(_row(f"    {RED}{BOLD}[ 8]{RESET} {RED}Back{RESET}                  {DESC_COLOR}— Return to main menu{RESET}", w))
        print(_row("", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-8]{CYAN}:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            display_account_overview(driver)
        elif choice == "2":
            display_account_currencies(driver)
        elif choice == "3":
            display_map_statistics(driver)
        elif choice == "4":
            display_pokemon_statistics(driver)
        elif choice == "5":
            display_battle_statistics(driver)
        elif choice == "6":
            display_marketplace(driver)
        elif choice == "7":
            display_account_activity(driver)
        elif choice == "8":
            return
        else:
            print(f"\n{RED}✗ Invalid choice '{choice}'. Please choose 1-8.{RESET}")
            time.sleep(1.0)


if __name__ == "__main__":
    _init_console()
    account_selector()

# ================================================================
# BROWSER SELECTOR
# ================================================================

def browser_selector():
    """Quick browser selection before login."""
    import settings
    
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║           SELECT BROWSER                                      ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    
    # Get available browsers for Android
    browsers = ["headless", "android-cdp", "android-brave", "termux", "auto"]
    
    for i, browser in enumerate(browsers, 1):
        if browser == "auto":
            desc = "Auto Detect (Tries all available)"
        elif browser == "android-cdp":
            desc = "Android Chrome/Brave (via CDP)"
        elif browser == "android-brave":
            desc = "Android Brave Specific"
        elif browser == "termux":
            desc = "Termux Chromium"
        elif browser == "headless":
            desc = "HTTP Requests (No Browser)"
        else:
            desc = browser
        
        print(f"  [{i}] {browser:15} - {desc}")
    
    print()
    choice = input("Select browser [1-5, or press Enter for auto]: ").strip()
    
    try:
        if choice == "":
            return "auto"
        idx = int(choice) - 1
        if 0 <= idx < len(browsers):
            selected = browsers[idx]
            settings.save_setting("browser_name", selected)
            print(f"✓ Browser set to: {selected}\n")
            return selected
    except (ValueError, IndexError):
        pass
    
    print("Invalid choice, using auto\n")
    settings.save_setting("browser_name", "auto")
    return "auto"

