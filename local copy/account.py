"""
Eclipse RPG - Account Management & Account Dashboard

Account profile:
    https://eclipserpg.com/user?id=<USER_ID>

The user's profile ID is discovered dynamically. No account ID
is hard-coded.

Existing saved-account/password management is preserved.
"""

from __future__ import annotations

import json
import re
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
    import keyring
except ImportError:
    keyring = None


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://eclipserpg.com"

# Do NOT put a user's ID here.
# The ID is discovered dynamically.
PROFILE_URL_TEMPLATE = (
    f"{BASE_URL}/user?id={{user_id}}"
)

LEGENDARY_AREAS_URL = (
    f"{BASE_URL}/legendary_areas"
)

ACCOUNT_FILE = (
    Path.home()
    / ".eclipse_rpg_accounts.json"
)

KEYRING_SERVICE = (
    "eclipse-rpg-automation"
)


# ============================================================
# ACCOUNT STORAGE
# ============================================================

def get_accounts() -> list[str]:

    try:

        if not ACCOUNT_FILE.exists():

            return []

        with ACCOUNT_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, list):

            return [
                str(item)
                for item in data
                if str(item).strip()
            ]

        if isinstance(data, dict):

            accounts = data.get(
                "accounts",
                [],
            )

            if isinstance(accounts, list):

                return [
                    str(item)
                    for item in accounts
                    if str(item).strip()
                ]

    except Exception:

        pass

    return []


def _write_accounts(
    accounts: list[str],
) -> None:

    ACCOUNT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ACCOUNT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "accounts": accounts,
            },
            file,
            indent=4,
        )


def save_account_name(
    username: str,
) -> None:

    username = username.strip()

    if not username:

        return

    accounts = get_accounts()

    if username not in accounts:

        accounts.append(
            username
        )

        _write_accounts(
            accounts
        )


def remove_account_name(
    username: str,
) -> None:

    username = username.strip()

    accounts = get_accounts()

    if username in accounts:

        accounts.remove(
            username
        )

        _write_accounts(
            accounts
        )

    if keyring is not None:

        try:

            keyring.delete_password(
                KEYRING_SERVICE,
                username,
            )

        except Exception:

            pass


def get_saved_password(
    username: str,
) -> Optional[str]:

    if not username:

        return None

    if keyring is None:

        return None

    try:

        return keyring.get_password(
            KEYRING_SERVICE,
            username,
        )

    except Exception:

        return None


def save_password(
    username: str,
    password: str,
) -> None:

    if not username:

        return

    if keyring is None:

        return

    try:

        keyring.set_password(
            KEYRING_SERVICE,
            username,
            password,
        )

    except Exception:

        pass


def add_account(
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Optional[str]:

    if username is None:

        username = input(
            "Username: "
        ).strip()

    if not username:

        print(
            "✗ Username cannot be blank."
        )

        return None

    if password is None:

        try:

            from getpass import getpass

            password = getpass(
                "Password: "
            )

        except Exception:

            password = input(
                "Password: "
            )

    save_account_name(
        username
    )

    if password:

        save_password(
            username,
            password,
        )

    print(
        f"✓ Account '{username}' saved."
    )

    return username


# ============================================================
# ACCOUNT SELECTOR
# ============================================================

def account_selector() -> Optional[str]:

    while True:

        accounts = get_accounts()

        print()
        print("=" * 60)
        print("ACCOUNT SELECTOR")
        print("=" * 60)
        print()

        if accounts:

            for index, username in enumerate(
                accounts,
                1,
            ):

                print(
                    f"{index}. {username}"
                )

            print()

            print(
                "A. Add account"
            )

            print(
                "R. Remove account"
            )

            print(
                "0. Back"
            )

            choice = input(
                "\nChoose: "
            ).strip()

            if choice == "0":

                return None

            if choice.lower() == "a":

                add_account()

                continue

            if choice.lower() == "r":

                remove_choice = input(
                    "Enter account number to remove: "
                ).strip()

                try:

                    index = int(
                        remove_choice
                    )

                    if not (
                        1
                        <= index
                        <= len(accounts)
                    ):

                        raise ValueError

                    username = accounts[
                        index - 1
                    ]

                    confirm = input(
                        f"Remove '{username}'? [y/N]: "
                    ).strip().lower()

                    if confirm == "y":

                        remove_account_name(
                            username
                        )

                        print(
                            "✓ Account removed."
                        )

                except ValueError:

                    print(
                        "✗ Invalid account number."
                    )

                continue

            try:

                index = int(choice)

                if not (
                    1
                    <= index
                    <= len(accounts)
                ):

                    raise ValueError

                return accounts[
                    index - 1
                ]

            except ValueError:

                print(
                    "✗ Invalid choice."
                )

        else:

            print(
                "No saved accounts."
            )

            print()

            print(
                "1. Add account"
            )

            print(
                "0. Back"
            )

            choice = input(
                "\nChoose: "
            ).strip()

            if choice == "1":

                username = add_account()

                if username:

                    return username

            elif choice == "0":

                return None

            else:

                print(
                    "✗ Invalid choice."
                )


# ============================================================
# GENERAL HELPERS
# ============================================================

def _clean_text(
    value: str,
) -> str:

    return re.sub(
        r"\s+",
        " ",
        value or "",
    ).strip()


def _get_soup(
    driver,
) -> BeautifulSoup:

    try:

        return BeautifulSoup(
            driver.page_source,
            "html.parser",
        )

    except Exception:

        return BeautifulSoup(
            "",
            "html.parser",
        )


def _parse_user_id(
    url: str,
) -> Optional[str]:

    try:

        parsed = urlparse(
            url
        )

        params = parse_qs(
            parsed.query
        )

        values = params.get(
            "id"
        )

        if values:

            user_id = str(
                values[0]
            ).strip()

            if user_id.isdigit():

                return user_id

    except Exception:

        pass

    return None


# ============================================================
# DYNAMIC PROFILE LOOKUP
# ============================================================

def find_user_profile_url(
    driver,
) -> Optional[str]:
    """
    Find the currently logged-in user's /user?id=... profile
    URL without hard-coding an account ID.

    We inspect the current authenticated page for links pointing
    to /user?id=NUMBER.

    Preference is given to links that appear to represent the
    logged-in user's own profile.
    """

    try:

        current_url = driver.current_url

    except Exception:

        current_url = ""

    # --------------------------------------------------------
    # If we're already on the user's profile, use it.
    # --------------------------------------------------------

    current_id = _parse_user_id(
        current_url
    )

    if (
        current_id
        and "/user" in current_url.lower()
    ):

        return (
            f"{BASE_URL}/user?id={current_id}"
        )

    # --------------------------------------------------------
    # Look through links on the current authenticated page.
    # --------------------------------------------------------

    selectors = [
        (
            By.CSS_SELECTOR,
            "a[href*='/user?id=']",
        ),
        (
            By.XPATH,
            "//a[contains(@href,'/user?id=')]",
        ),
    ]

    candidates = []

    for by, selector in selectors:

        try:

            elements = driver.find_elements(
                by,
                selector,
            )

        except Exception:

            continue

        for element in elements:

            try:

                href = (
                    element.get_attribute(
                        "href"
                    )
                    or ""
                )

                text = _clean_text(
                    element.text
                )

                user_id = _parse_user_id(
                    href
                )

                if user_id:

                    candidates.append(
                        {
                            "id": user_id,
                            "href": href,
                            "text": text,
                        }
                    )

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                continue

    if not candidates:

        return None

    # --------------------------------------------------------
    # First look for links whose text suggests "profile",
    # "account", or the currently logged-in user.
    # --------------------------------------------------------

    preferred_words = (
        "profile",
        "account",
        "my profile",
        "my account",
    )

    for candidate in candidates:

        text = candidate[
            "text"
        ].lower()

        if any(
            word in text
            for word in preferred_words
        ):

            return (
                f"{BASE_URL}/user?id="
                f"{candidate['id']}"
            )

    # --------------------------------------------------------
    # If no obvious profile link exists, use the first unique
    # user profile link. Eclipse commonly exposes the user's
    # profile through the navigation/header.
    # --------------------------------------------------------

    seen_ids = set()

    for candidate in candidates:

        user_id = candidate[
            "id"
        ]

        if user_id in seen_ids:

            continue

        seen_ids.add(
            user_id
        )

        return (
            f"{BASE_URL}/user?id="
            f"{user_id}"
        )

    return None


def get_logged_in_user_id(
    driver,
) -> Optional[str]:
    """
    Return the current logged-in user's Eclipse profile ID.
    """

    url = find_user_profile_url(
        driver
    )

    if not url:

        return None

    return _parse_user_id(
        url
    )


def open_user_profile(
    driver,
) -> Optional[str]:
    """
    Dynamically find and open the current user's profile.

    Returns the profile URL if successful.
    """

    profile_url = find_user_profile_url(
        driver
    )

    if not profile_url:

        print(
            "✗ Could not locate the logged-in user's profile link."
        )

        print(
            "  Eclipse did not expose a /user?id=... link "
            "on the current page."
        )

        return None

    try:

        print(
            f"  ✓ User profile found: {profile_url}"
        )

        driver.get(
            profile_url
        )

        time.sleep(
            0.5
        )

        return profile_url

    except Exception as error:

        print(
            f"✗ Could not open user profile: {error}"
        )

        return None


# ============================================================
# VALUE PARSING
# ============================================================

def _find_value_by_label(
    soup: BeautifulSoup,
    label: str,
) -> str:
    """
    Parse Eclipse's common:

        <td>Label:</td>
        <td>Value</td>

    structure.
    """

    wanted = _clean_text(
        label
    ).rstrip(
        ":"
    ).lower()

    for cell in soup.find_all(
        "td"
    ):

        cell_text = _clean_text(
            cell.get_text(
                " ",
                strip=True,
            )
        )

        normalized = (
            cell_text
            .rstrip(":")
            .lower()
        )

        if normalized != wanted:

            continue

        next_cell = (
            cell.find_next_sibling(
                "td"
            )
        )

        if next_cell is not None:

            value = _clean_text(
                next_cell.get_text(
                    " ",
                    strip=True,
                )
            )

            if value:

                return value

    return "Unknown"


def _find_first_value(
    soup: BeautifulSoup,
    labels: list[str],
) -> str:

    for label in labels:

        value = _find_value_by_label(
            soup,
            label,
        )

        if value != "Unknown":

            return value

    return "Unknown"


# ============================================================
# ACCOUNT PROFILE
# ============================================================

def get_account_profile(
    driver,
) -> dict[str, str]:
    """
    Open and parse the logged-in user's actual Eclipse profile.

    Example:

        https://eclipserpg.com/user?id=345230

    The 345230 value is discovered dynamically.
    """

    print(
        "\nLoading account information..."
    )

    profile_url = open_user_profile(
        driver
    )

    if not profile_url:

        return {}

    soup = _get_soup(
        driver
    )

    user_id = _parse_user_id(
        profile_url
    )

    return {
        "User ID": (
            user_id
            if user_id
            else "Unknown"
        ),

        "Username": _find_first_value(
            soup,
            [
                "Username",
                "User Name",
            ],
        ),

        "Trainer Title": _find_first_value(
            soup,
            [
                "Trainer Title",
                "Trainer title",
                "Title",
            ],
        ),

        "Trainer Gender": _find_first_value(
            soup,
            [
                "Trainer Gender",
                "Gender",
            ],
        ),

        "User Group": _find_first_value(
            soup,
            [
                "User Group",
                "Group",
            ],
        ),

        "Map Level": _find_first_value(
            soup,
            [
                "Map Level",
            ],
        ),

        "Trainer Level": _find_first_value(
            soup,
            [
                "Trainer Level",
                "Level",
            ],
        ),

        "Trainer EXP": _find_first_value(
            soup,
            [
                "Trainer EXP",
                "Trainer Experience",
                "EXP",
                "Experience",
            ],
        ),

        "Mining Level": _find_first_value(
            soup,
            [
                "Mining Level",
            ],
        ),

        "AP / Team": _find_first_value(
            soup,
            [
                "AP / Team",
                "AP",
                "Team",
            ],
        ),

        "Battles Won": _find_first_value(
            soup,
            [
                "Battles Won",
                "Battle Wins",
            ],
        ),

        "Date Registered": _find_first_value(
            soup,
            [
                "Date Registered",
                "Registered",
            ],
        ),

        "Last Login": _find_first_value(
            soup,
            [
                "Last Login",
            ],
        ),

        "Play Time": _find_first_value(
            soup,
            [
                "Play Time",
                "Playtime",
            ],
        ),

        "Betas": _find_first_value(
            soup,
            [
                "Betas",
            ],
        ),
    }


def display_account_overview(
    driver,
) -> None:

    data = get_account_profile(
        driver
    )

    print()
    print("=" * 60)
    print("ACCOUNT OVERVIEW")
    print("=" * 60)
    print()

    if not data:

        print(
            "✗ Could not load account profile."
        )

        input(
            "\nPress Enter to return..."
        )

        return

    for label, value in data.items():

        print(
            f"{label:<20}: {value}"
        )

    input(
        "\nPress Enter to return..."
    )


# ============================================================
# CURRENCY & RESOURCES
# ============================================================

def get_account_currencies(
    driver,
) -> dict[str, str]:

    # Ensure we're on the real profile.
    profile_url = find_user_profile_url(
        driver
    )

    if profile_url:

        try:

            if driver.current_url != profile_url:

                driver.get(
                    profile_url
                )

                time.sleep(
                    0.4
                )

        except Exception:

            pass

    soup = _get_soup(
        driver
    )

    return {
        "Platinum Coins": _find_first_value(
            soup,
            [
                "Platinum Coins",
                "Platinum",
            ],
        ),

        "Diamond Coins": _find_first_value(
            soup,
            [
                "Diamond Coins",
                "Diamond",
            ],
        ),

        "Moon Points": _find_first_value(
            soup,
            [
                "Moon Points",
                "Moon",
            ],
        ),
    }


def display_account_currencies(
    driver,
) -> None:

    print(
        "\nLoading currency information..."
    )

    currencies = get_account_currencies(
        driver
    )

    print()
    print("=" * 60)
    print("CURRENCY & RESOURCES")
    print("=" * 60)
    print()

    for name, value in currencies.items():

        print(
            f"{name:<20}: {value}"
        )

    input(
        "\nPress Enter to return..."
    )


# ============================================================
# MAP STATISTICS
# ============================================================

def get_map_statistics(
    driver,
) -> list[dict[str, str]]:

    try:

        driver.get(
            LEGENDARY_AREAS_URL
        )

        time.sleep(
            0.5
        )

    except Exception as error:

        print(
            f"✗ Could not open map statistics: {error}"
        )

        return []

    soup = _get_soup(
        driver
    )

    results = []

    for table in soup.find_all(
        "table"
    ):

        rows = table.find_all(
            "tr"
        )

        if not rows:

            continue

        header_cells = rows[0].find_all(
            ["th", "td"]
        )

        headers = [
            _clean_text(
                cell.get_text(
                    " ",
                    strip=True,
                )
            ).lower()
            for cell in header_cells
        ]

        if not any(
            "map name" in header
            for header in headers
        ):

            continue

        for row in rows[1:]:

            cells = row.find_all(
                ["td", "th"]
            )

            if len(cells) < 2:

                continue

            values = [
                _clean_text(
                    cell.get_text(
                        " ",
                        strip=True,
                    )
                )
                for cell in cells
            ]

            map_name = values[0]

            if not map_name:

                continue

            if map_name.lower() in (
                "total",
                "totals",
            ):

                continue

            results.append(
                {
                    "map": map_name,
                    "total": (
                        values[1]
                        if len(values) > 1
                        else "0"
                    ),
                    "today": (
                        values[2]
                        if len(values) > 2
                        else "0"
                    ),
                }
            )

    return results


def display_map_statistics(
    driver,
) -> None:

    print(
        "\nLoading map statistics..."
    )

    maps = get_map_statistics(
        driver
    )

    print()
    print("=" * 70)
    print("MAP STATISTICS")
    print("=" * 70)
    print()

    if not maps:

        print(
            "No map statistics were found."
        )

        input(
            "\nPress Enter to return..."
        )

        return

    print(
        f"{'Map':<35}"
        f"{'Total':>12}"
        f"{'Today':>12}"
    )

    print(
        "-" * 59
    )

    total_searches = 0
    today_searches = 0

    for item in maps:

        try:

            total = int(
                re.sub(
                    r"[^\d]",
                    "",
                    item["total"],
                )
                or "0"
            )

        except ValueError:

            total = 0

        try:

            today = int(
                re.sub(
                    r"[^\d]",
                    "",
                    item["today"],
                )
                or "0"
            )

        except ValueError:

            today = 0

        total_searches += total
        today_searches += today

        print(
            f"{item['map']:<35}"
            f"{total:>12,}"
            f"{today:>12,}"
        )

    print(
        "-" * 59
    )

    print(
        f"{'TOTAL':<35}"
        f"{total_searches:>12,}"
        f"{today_searches:>12,}"
    )

    input(
        "\nPress Enter to return..."
    )


# ============================================================
# POKEMON STATISTICS
# ============================================================

def get_pokemon_statistics(
    driver,
) -> dict[str, str]:

    profile_url = find_user_profile_url(
        driver
    )

    if profile_url:

        try:

            if driver.current_url != profile_url:

                driver.get(
                    profile_url
                )

                time.sleep(
                    0.4
                )

        except Exception:

            pass

    soup = _get_soup(
        driver
    )

    return {
        "Pokémon Owned": _find_first_value(
            soup,
            [
                "Pokémon Owned",
                "Pokemon Owned",
                "Pokémon",
                "Pokemon",
            ],
        ),

        "Pokémon Caught": _find_first_value(
            soup,
            [
                "Pokémon Caught",
                "Pokemon Caught",
                "Caught",
            ],
        ),

        "Unique Pokémon": _find_first_value(
            soup,
            [
                "Unique Pokémon",
                "Unique Pokemon",
            ],
        ),

        "Shiny": _find_first_value(
            soup,
            [
                "Shiny",
            ],
        ),

        "Dark": _find_first_value(
            soup,
            [
                "Dark",
            ],
        ),

        "Golden": _find_first_value(
            soup,
            [
                "Golden",
            ],
        ),

        "Crystal": _find_first_value(
            soup,
            [
                "Crystal",
            ],
        ),
    }


def display_pokemon_statistics(
    driver,
) -> None:

    print(
        "\nLoading Pokémon statistics..."
    )

    stats = get_pokemon_statistics(
        driver
    )

    print()
    print("=" * 60)
    print("POKÉMON STATISTICS")
    print("=" * 60)
    print()

    for name, value in stats.items():

        print(
            f"{name:<20}: {value}"
        )

    print()
    print(
        "Bot session capture statistics are shown"
    )

    print(
        "under Account Activity."
    )

    input(
        "\nPress Enter to return..."
    )


# ============================================================
# BATTLE STATISTICS
# ============================================================

def get_battle_statistics(
    driver,
) -> dict[str, str]:

    profile_url = find_user_profile_url(
        driver
    )

    if profile_url:

        try:

            if driver.current_url != profile_url:

                driver.get(
                    profile_url
                )

                time.sleep(
                    0.4
                )

        except Exception:

            pass

    soup = _get_soup(
        driver
    )

    return {
        "Battles Won": _find_first_value(
            soup,
            [
                "Battles Won",
                "Battle Wins",
            ],
        ),

        "Trainer Level": _find_first_value(
            soup,
            [
                "Trainer Level",
                "Level",
            ],
        ),

        "Trainer EXP": _find_first_value(
            soup,
            [
                "Trainer EXP",
                "Trainer Experience",
                "EXP",
            ],
        ),

        "Mining Level": _find_first_value(
            soup,
            [
                "Mining Level",
            ],
        ),
    }


def display_battle_statistics(
    driver,
) -> None:

    print(
        "\nLoading battle statistics..."
    )

    stats = get_battle_statistics(
        driver
    )

    print()
    print("=" * 60)
    print("BATTLE STATISTICS")
    print("=" * 60)
    print()

    for name, value in stats.items():

        print(
            f"{name:<20}: {value}"
        )

    input(
        "\nPress Enter to return..."
    )


# ============================================================
# MARKETPLACE
# ============================================================

def display_marketplace(
    driver,
) -> None:

    print()
    print("=" * 60)
    print("MARKETPLACE")
    print("=" * 60)
    print()

    print(
        "Marketplace tools will be connected here."
    )

    print()
    print(
        "Planned:"
    )

    print(
        "  1. Evaluate Pokémon"
    )

    print(
        "  2. Check current listings"
    )

    print(
        "  3. Price comparison"
    )

    print(
        "  4. Back"
    )

    input(
        "\nPress Enter to return..."
    )


# ============================================================
# ACCOUNT ACTIVITY
# ============================================================

def _get_capture_stats() -> dict:

    try:

        import capture

        stats = getattr(
            capture,
            "_capture_stats",
            {},
        )

        if isinstance(
            stats,
            dict,
        ):

            return {
                str(key): int(value)
                for key, value in stats.items()
                if isinstance(
                    value,
                    (int, float),
                )
            }

    except Exception:

        pass

    return {}


def _get_search_stats() -> dict:

    try:

        import search

        for name in (
            "_search_stats",
            "search_stats",
            "SEARCH_STATS",
        ):

            stats = getattr(
                search,
                name,
                None,
            )

            if isinstance(
                stats,
                dict,
            ):

                result = {}

                for key, value in stats.items():

                    if isinstance(
                        value,
                        (int, float),
                    ):

                        result[
                            str(key)
                        ] = int(value)

                if result:

                    return result

    except Exception:

        pass

    return {}


def display_account_activity(
    driver,
) -> None:

    capture_stats = (
        _get_capture_stats()
    )

    search_stats = (
        _get_search_stats()
    )

    print()
    print("=" * 60)
    print("ACCOUNT ACTIVITY")
    print("=" * 60)
    print()

    print(
        "BOT SESSION"
    )

    print(
        "-" * 60
    )

    print(
        "Pokémon encounters: "
        f"{capture_stats.get('encounters', 0):,}"
    )

    print(
        "Pokémon captured:   "
        f"{capture_stats.get('captured', 0):,}"
    )

    print(
        "Capture failures:   "
        f"{capture_stats.get('failed', 0):,}"
    )

    if search_stats:

        print()
        print(
            "SEARCH SESSION"
        )

        print(
            "-" * 60
        )

        for key, value in search_stats.items():

            label = (
                key
                .replace(
                    "_",
                    " ",
                )
                .title()
            )

            print(
                f"{label:<22}: {value:,}"
            )

    print()
    print(
        "These numbers are bot-session statistics."
    )

    print(
        "They are separate from Eclipse's account totals."
    )

    input(
        "\nPress Enter to return..."
    )


# ============================================================
# ACCOUNT MENU
# ============================================================

def account_menu(
    driver,
) -> None:

    while True:

        print()
        print("=" * 60)
        print("ACCOUNT")
        print("=" * 60)
        print()

        print(
            "1. Account Overview"
        )

        print(
            "2. Currency & Resources"
        )

        print(
            "3. Map Statistics"
        )

        print(
            "4. Pokémon Statistics"
        )

        print(
            "5. Battle Statistics"
        )

        print(
            "6. Marketplace"
        )

        print(
            "7. Account Activity"
        )

        print(
            "8. Back"
        )

        choice = input(
            "\nChoose: "
        ).strip()

        if choice == "1":

            display_account_overview(
                driver
            )

        elif choice == "2":

            display_account_currencies(
                driver
            )

        elif choice == "3":

            display_map_statistics(
                driver
            )

        elif choice == "4":

            display_pokemon_statistics(
                driver
            )

        elif choice == "5":

            display_battle_statistics(
                driver
            )

        elif choice == "6":

            display_marketplace(
                driver
            )

        elif choice == "7":

            display_account_activity(
                driver
            )

        elif choice == "8":

            return

        else:

            print()
            print(
                "✗ Invalid choice."
            )


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "account.py provides account management and"
    )

    print(
        "the account_menu(driver) dashboard."
    )