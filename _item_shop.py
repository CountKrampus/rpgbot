r"""
Eclipse RPG Item Shop.

Handles the Item Shop at /item_shop and purchases items using
the site's shop_purchase(item_id, shop_number) JavaScript function.
"""

import re
import time

__all__ = ["_item_shop", "_moon_shop"]


# ============================================================
# ANSI & STYLING
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"

CYAN = "\033[96m"
MAGENTA = "\033[95m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"
GOLD = "\033[38;5;220m"
PURPLE = "\033[38;5;141m"

BORDER_COLOR = PURPLE

KEY_COLOR = f"{BOLD}{YELLOW}"
NAME_COLOR = f"{BOLD}{WHITE}"

ANSI_STRIP_REGEX = re.compile(r"\x1b\[[0-9;]*[mK]")


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences before calculating display width."""
    return ANSI_STRIP_REGEX.sub("", text)


# ============================================================
# ITEM SHOP DATA
# ============================================================

ITEM_SHOP = {
    1:  {"name": "PokeBall",        "item_id": 1,   "price": 200},
    2:  {"name": "Great Ball",      "item_id": 2,   "price": 600},
    3:  {"name": "Ultra Ball",      "item_id": 3,   "price": 1200},
    4:  {"name": "Potion",          "item_id": 4,   "price": 150},
    5:  {"name": "Super Potion",    "item_id": 5,   "price": 350},
    6:  {"name": "Hyper Potion",    "item_id": 6,   "price": 500},
    7:  {"name": "Max Potion",      "item_id": 7,   "price": 1000},
    8:  {"name": "MP Restore Lv 1", "item_id": 8,   "price": 100},
    9:  {"name": "MP Restore Lv 2", "item_id": 9,   "price": 200},
    10: {"name": "MP Restore Lv 3", "item_id": 10,  "price": 300},
    11: {"name": "Focus Scarf",     "item_id": 197, "price": 5000},
    12: {"name": "Razor Claw",      "item_id": 198, "price": 7500},
    13: {"name": "Type Boost",      "item_id": 199, "price": 7500},
    14: {"name": "Soothe Bell",     "item_id": 286, "price": 10000},
    15: {"name": "Venusaurite",     "item_id": 290, "price": 5000000},
    16: {"name": "Charizardite X",  "item_id": 292, "price": 5000000},
    17: {"name": "Charizardite Y",  "item_id": 293, "price": 5000000},
    18: {"name": "Blastoisinite",   "item_id": 294, "price": 5000000},
    19: {"name": "Sceptilite",      "item_id": 295, "price": 5000000},
    20: {"name": "Blazikenite",     "item_id": 296, "price": 5000000},
    21: {"name": "Swampertite",     "item_id": 297, "price": 5000000},
    22: {"name": "Diancite",        "item_id": 312, "price": 100000000},
    23: {"name": "Zygardite",       "item_id": 313, "price": 100000000},
    24: {"name": "Mewtwonite X",    "item_id": 314, "price": 100000000},
}


# ============================================================
# ITEM SHOP
# ============================================================

def _load_moon_shop_catalog(driver):
    """Read the current Moon Shop catalog from the rendered shop table."""
    rows = driver.execute_script(
        r"""
        return Array.from(
            document.querySelectorAll('[id^="S_ItemNumber"]')
        ).map(function (item) {
            const row = item.closest('tr');
            const button = row && row.querySelector('button[onclick*="shop_purchase"]');
            const priceCell = row && row.querySelector('td:nth-child(3)');
            const match = button && button.getAttribute('onclick').match(
                /shop_purchase\((\d+),\s*(\d+)\)/
            );

            if (!row || !button || !priceCell || !match) {
                return null;
            }

            return {
                name: item.textContent.trim(),
                item_id: Number(match[1]),
                shop_number: Number(match[2]),
                price: Number(
                    priceCell.textContent.replace(/[^\d]/g, '')
                ),
                owned: Boolean(item.querySelector('s, del')),
            };
        }).filter(Boolean);
        """
    )

    if not rows:
        raise RuntimeError("No Moon Shop items were found on the page.")

    return {
        row["shop_number"]: {
            "name": row["name"],
            "item_id": row["item_id"],
            "price": row["price"],
            "owned": row["owned"],
        }
        for row in rows
    }


def _item_shop(
    driver,
    catalog=None,
    shop_path="/item_shop",
    shop_title="ECLIPSE RPG ITEM SHOP",
    currency="Platinum Coins",
):
    """
    Display and operate the Eclipse RPG Item Shop.

    Each shop_purchase() call prompts for a quantity, up to 99.
    Larger requested quantities are automatically split into
    multiple purchases.
    """

    # --------------------------------------------------------
    # Open Item Shop
    # --------------------------------------------------------

    try:
        current_url = driver.current_url

        if shop_path not in current_url:
            base_url = current_url.split("/", 3)

            if len(base_url) >= 3:
                item_shop_url = f"{base_url[0]}//{base_url[2]}{shop_path}"
            else:
                raise RuntimeError(
                    "Unable to determine the Eclipse RPG base URL."
                )

            driver.get(item_shop_url)

    except Exception as error:
        print(
            f"\n{RED}✗ Could not open Item Shop: "
            f"{error}{RESET}"
        )
        input(
            f"\n{GRAY}Press Enter to return to the shop menu..."
            f"{RESET}"
        )
        return

    if catalog is None:
        catalog = ITEM_SHOP

    if shop_path.startswith("/moon_shop"):
        try:
            catalog = _load_moon_shop_catalog(driver)
        except Exception as error:
            print(
                f"\n{RED}✗ Could not load Moon Shop items: "
                f"{error}{RESET}"
            )
            input(
                f"\n{GRAY}Press Enter to return to the shop menu..."
                f"{RESET}"
            )
            return

    # --------------------------------------------------------
    # Display menu
    # --------------------------------------------------------

    w = 71

    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)

        return (
            f"{BORDER_COLOR}║{RESET}"
            f"{content}"
            f"{' ' * pad}"
            f"{BORDER_COLOR}║{RESET}"
        )

    while True:

        print()
        print(f"{BORDER_COLOR}╔{'═' * w}╗{RESET}")
        print(
            _drow(
                f"  {BOLD}{MAGENTA}"
                f"🛒  {shop_title}"
                f"{RESET}"
            )
        )

        print(f"{BORDER_COLOR}╠{'═' * w}╣{RESET}")

        print(
            _drow(
                f"  {GRAY}"
                f"Select an item to purchase."
                f"{RESET}"
            )
        )

        print(
            _drow(
                f"  {GRAY}"
                f"Maximum quantity per purchase: "
                f"{1 if shop_path.startswith('/moon_shop') else 99}"
                f"{RESET}"
            )
        )

        print(f"{BORDER_COLOR}╠{'═' * w}╣{RESET}")

        # ----------------------------------------------------
        # Items
        # ----------------------------------------------------

        for index, item in catalog.items():

            price = f"${item['price']:,}"
            owned = item.get("owned", False)
            ownership = (
                f"{GREEN}Owned{RESET}"
                if owned
                else f"{GRAY}{currency}{RESET}"
            )

            line = (
                f"  {KEY_COLOR}[{index:2d}]{RESET} "
                f"{NAME_COLOR}{item['name']:<18}{RESET} "
                f"{GOLD}{price:>15}{RESET} "
                f"{ownership}"
            )

            print(_drow(line))

        print(f"{BORDER_COLOR}╠{'═' * w}╣{RESET}")

        print(
            _drow(
                f"  {RED}{BOLD}[ 0]{RESET} "
                f"{RED}Back{RESET}"
            )
        )

        print(f"{BORDER_COLOR}╚{'═' * w}╝{RESET}")

        # ----------------------------------------------------
        # Select item
        # ----------------------------------------------------

        try:
            choice = input(
                f"\n{BOLD}{CYAN}"
                f"❯ Select Item "
                f"{GRAY}[1-{len(catalog)}, 0=Back]"
                f"{CYAN}:{RESET} "
            ).strip()

        except (KeyboardInterrupt, EOFError):
            return

        if choice == "0":
            return

        try:
            item_number = int(choice)
            item = catalog[item_number]

        except (ValueError, KeyError):
            print(
                f"\n{RED}"
                f"✗ Invalid item selection."
                f"{RESET}"
            )
            time.sleep(1.0)
            continue

        if item.get("owned", False):
            print(
                f"\n{YELLOW}⚠ You already own "
                f"{item['name']}.{RESET}"
            )
            time.sleep(1.0)
            continue

        # ----------------------------------------------------
        # Item details
        # ----------------------------------------------------

        print()
        print(
            f"{BORDER_COLOR}╭{'─' * 55}╮{RESET}"
        )

        print(
            f"{BORDER_COLOR}│{RESET} "
            f"{BOLD}{WHITE}{item['name']}{RESET}"
        )

        print(
            f"{BORDER_COLOR}│{RESET} "
            f"Price: "
            f"{GOLD}${item['price']:,}"
            f"{RESET} {currency}"
        )

        print(
            f"{BORDER_COLOR}╰{'─' * 55}╯{RESET}"
        )

        # ----------------------------------------------------
        # Quantity
        # ----------------------------------------------------

        try:
            quantity_text = input(
                f"\n{BOLD}{CYAN}"
                f"❯ Quantity "
                f"{GRAY}[1+]"
                f"{CYAN}:{RESET} "
            ).strip()

        except (KeyboardInterrupt, EOFError):
            return

        try:
            quantity = int(quantity_text)

        except ValueError:
            print(
                f"\n{RED}"
                f"✗ Quantity must be a whole number."
                f"{RESET}"
            )
            time.sleep(1.0)
            continue

        if quantity <= 0:
            print(
                f"\n{RED}"
                f"✗ Quantity must be greater than 0."
                f"{RESET}"
            )
            time.sleep(1.0)
            continue

        # ----------------------------------------------------
        # Cost
        # ----------------------------------------------------

        total_cost = item["price"] * quantity

        print()
        print(f"{WHITE}Purchase Summary{RESET}")
        print(
            f"  Item:     "
            f"{NAME_COLOR}{item['name']}{RESET}"
        )
        print(
            f"  Quantity: "
            f"{YELLOW}{quantity:,}{RESET}"
        )
        print(
            f"  Cost:     "
            f"{GOLD}${total_cost:,}"
            f"{RESET} {currency}"
        )

        # ----------------------------------------------------
        # Calculate batches
        # ----------------------------------------------------

        batches = []
        batch_limit = 1 if shop_path.startswith("/moon_shop") else 99

        remaining = quantity

        while remaining > 0:
            batch = min(remaining, batch_limit)
            batches.append(batch)
            remaining -= batch

        if quantity > 99:

            print(
                f"\n{YELLOW}"
                f"⚠ The site allows a maximum of 99 "
                f"per purchase."
                f"{RESET}"
            )

            print(
                f"{GRAY}"
                f"This will be split into "
                f"{len(batches)} purchase(s): "
                f"{' + '.join(map(str, batches))}"
                f"{RESET}"
            )

        # ----------------------------------------------------
        # Confirmation
        # ----------------------------------------------------

        try:
            confirm = input(
                f"\n{BOLD}{CYAN}"
                f"❯ Confirm purchase? [y/N]:"
                f"{RESET} "
            ).strip().lower()

        except (KeyboardInterrupt, EOFError):
            return

        if confirm != "y":
            print(
                f"\n{GRAY}"
                f"Purchase cancelled."
                f"{RESET}"
            )
            time.sleep(0.8)
            continue

        # ----------------------------------------------------
        # Execute purchases
        # ----------------------------------------------------

        purchased = 0

        print()

        for batch_number, batch_quantity in enumerate(
            batches,
            start=1,
        ):

            print(
                f"{CYAN}"
                f"⚡ Purchase "
                f"{batch_number}/{len(batches)}: "
                f"{batch_quantity} × "
                f"{item['name']}..."
                f"{RESET}"
            )

            try:
                driver.execute_script(
                    """
                    if (typeof shop_purchase !== "function") {
                        throw new Error(
                            "shop_purchase() was not found on the page."
                        );
                    }

                    shop_purchase(arguments[0], arguments[1]);
                    """,
                    item["item_id"],
                    item["shop_number"] if "shop_number" in item else item_number,
                )

                purchase_prompt = driver.switch_to.alert
                prompt_text = purchase_prompt.text.lower()

                if "how many" in prompt_text:
                    purchase_prompt.send_keys(str(batch_quantity))
                    purchase_prompt.accept()

                    confirmation_prompt = driver.switch_to.alert
                    confirmation_prompt.accept()
                else:
                    # Moon Shop entries are purchased one at a time and
                    # present only a confirmation alert.
                    purchase_prompt.accept()

                purchased += batch_quantity

                print(
                    f"{GREEN}"
                    f"✓ Purchase request sent: "
                    f"{batch_quantity} × "
                    f"{item['name']}"
                    f"{RESET}"
                )

            except Exception as error:
                print(
                    f"{RED}"
                    f"✗ Purchase request failed: "
                    f"{error}"
                    f"{RESET}"
                )
                print(
                    f"{YELLOW}"
                    f"⚠ Purchased "
                    f"{purchased:,} of "
                    f"{quantity:,} before the error."
                    f"{RESET}"
                )
                break

            # Give the site's JavaScript request time to finish.
            if batch_number < len(batches):
                time.sleep(1.0)

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        if purchased == quantity:

            print(
                f"\n{GREEN}{BOLD}"
                f"✓ Purchase complete!"
                f"{RESET}"
            )

            print(
                f"{WHITE}"
                f"{purchased:,} × {item['name']}"
                f"{RESET} purchased."
            )

        elif purchased > 0:

            print(
                f"\n{YELLOW}"
                f"⚠ Purchase partially completed."
                f"{RESET}"
            )

            print(
                f"{GRAY}"
                f"{purchased:,} of "
                f"{quantity:,} purchased."
                f"{RESET}"
            )

        else:

            print(
                f"\n{RED}"
                f"✗ No items were purchased."
                f"{RESET}"
            )

        input(
            f"\n{GRAY}"
            f"Press Enter to return to the {shop_title.title()}..."
            f"{RESET}"
        )


MOON_SHOP_AREAS = {
    "1": ("legendary_areas", "Legendary Areas"),
    "2": ("avatars", "Avatars"),
    "3": ("items", "Items"),
}


def _moon_shop(driver):
    """Display and operate one of the live Eclipse RPG Moon Shop areas."""
    while True:
        print()
        print(f"{BOLD}{MAGENTA}ECLIPSE RPG MOON SHOP{RESET}")
        print(f"  {KEY_COLOR}[1]{RESET} Legendary Areas")
        print(f"  {KEY_COLOR}[2]{RESET} Avatars")
        print(f"  {KEY_COLOR}[3]{RESET} Items")
        print(f"  {RED}{BOLD}[0]{RESET} Back")

        try:
            choice = input(
                f"\n{BOLD}{CYAN}❯ Select Moon Shop area "
                f"{GRAY}[0-3]{CYAN}:{RESET} "
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return

        if choice == "0":
            return

        area = MOON_SHOP_AREAS.get(choice)
        if area is None:
            print(f"\n{RED}✗ Invalid Moon Shop area.{RESET}")
            time.sleep(1.0)
            continue

        area_key, area_title = area
        _item_shop(
            driver,
            shop_path=f"/moon_shop?area={area_key}",
            shop_title=f"ECLIPSE RPG MOON SHOP - {area_title.upper()}",
            currency="Moon Points",
        )