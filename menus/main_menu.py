"""
New categorized main menu for Eclipse RPG Automation.

This module is purely a navigation layer. It does not change the
behavior of training, searching, mining, or trading in any way -
it calls the exact same functions that main.py used to call
directly (train_mode, search_mode, miner_mode, trade_mode).

Sections that don't have an underlying implementation yet
(Messages, Shops, Pokemon, Account, Utilities, Settings) show a
clear "not yet implemented" stub and return to the menu, rather
than pretending to do something they can't.
"""

from mining import miner_mode
from trade import trade_mode
from menus.search_menu import search_menu
from menus.messages_menu import messages_menu
from menus.training_menu import training_menu
from menus.shop_menu import shop_menu
from menus.settings_menu import settings_menu
from account import account_menu


BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║                 ECLIPSE RPG AUTOMATION                    ║
╠══════════════════════════════════════════════════════════╣
║                                                            ║
║  PLAY                                                     ║
║    1. Training                                            ║
║    2. Searching                                           ║
║    3. A-Miner                                             ║
║    4. Trading                                             ║
║                                                            ║
║  MANAGEMENT                                                ║
║    5. Messages                                             ║
║    6. Shops                                                ║
║    7. Pokemon                                              ║
║    8. Account                                              ║
║                                                            ║
║  TOOLS                                                      ║
║    9. Utilities                                            ║
║   10. Settings                                             ║
║                                                            ║
║    0. Exit                                                 ║
║                                                            ║
╚══════════════════════════════════════════════════════════╝
"""


def _not_yet_implemented(section_name):
    """
    Placeholder for sections whose underlying feature modules
    (messages.py, shops.py, pokemon.py, account settings UI,
    utilities.py, settings.py) haven't been built yet.

    Intentionally does nothing fake - just says so and returns.
    """

    print()
    print("=" * 60)
    print(section_name.upper())
    print("=" * 60)
    print()
    print(
        f"{section_name} isn't implemented yet. "
        "This will be added in a later phase."
    )
    input("\nPress Enter to return to the main menu...")


def main_menu(driver):
    while True:

        print(BANNER)

        choice = input("Choose: ").strip()

        if choice == "1":
            training_menu(driver)

        elif choice == "2":
            search_menu(driver)

        elif choice == "3":
            miner_mode(driver)

        elif choice == "4":
            trade_mode(driver)

        elif choice == "5":
            messages_menu(driver)

        elif choice == "6":
            shop_menu(driver)

        elif choice == "7":
            _not_yet_implemented("Pokemon")

        elif choice == "8":
            account_menu(driver)

        elif choice == "9":
            _not_yet_implemented("Utilities")

        elif choice == "10":
            settings_menu(driver)

        elif choice == "0":
            break

        else:
            print("✗ Invalid choice.")
