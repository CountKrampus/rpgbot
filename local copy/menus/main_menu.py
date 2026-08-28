"""
Categorized main menu for Eclipse RPG Automation.

Account is handled by account_menu(driver).
Other sections continue to use their existing menu modules.
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
    Placeholder for sections whose underlying feature module
    has not been built yet.
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

    input(
        "\nPress Enter to return to the main menu..."
    )


def main_menu(driver):

    while True:

        print(BANNER)

        choice = input(
            "Choose: "
        ).strip()

        # ----------------------------------------------------
        # TRAINING
        # ----------------------------------------------------

        if choice == "1":

            training_menu(
                driver
            )

        # ----------------------------------------------------
        # SEARCHING
        # ----------------------------------------------------

        elif choice == "2":

            search_menu(
                driver
            )

        # ----------------------------------------------------
        # A-MINER
        # ----------------------------------------------------

        elif choice == "3":

            miner_mode(
                driver
            )

        # ----------------------------------------------------
        # TRADING
        # ----------------------------------------------------

        elif choice == "4":

            trade_mode(
                driver
            )

        # ----------------------------------------------------
        # MESSAGES
        # ----------------------------------------------------

        elif choice == "5":

            messages_menu(
                driver
            )

        # ----------------------------------------------------
        # SHOPS
        # ----------------------------------------------------

        elif choice == "6":

            shop_menu(
                driver
            )

        # ----------------------------------------------------
        # POKEMON
        # ----------------------------------------------------

        elif choice == "7":

            _not_yet_implemented(
                "Pokemon"
            )

        # ----------------------------------------------------
        # ACCOUNT
        # ----------------------------------------------------

        elif choice == "8":

            account_menu(
                driver
            )

        # ----------------------------------------------------
        # UTILITIES
        # ----------------------------------------------------

        elif choice == "9":

            _not_yet_implemented(
                "Utilities"
            )

        # ----------------------------------------------------
        # SETTINGS
        # ----------------------------------------------------

        elif choice == "10":

            settings_menu(
                driver
            )

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        elif choice == "0":

            break

        # ----------------------------------------------------
        # INVALID
        # ----------------------------------------------------

        else:

            print()
            print(
                "✗ Invalid choice."
            )