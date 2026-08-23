"""
Search submenu for Eclipse RPG Automation (Phase 3).

Normal Maps and Exclusive Legendary Areas call into the split
functions in search.py (normal_maps_mode / exclusive_maps_mode),
which reuse the exact same tested helpers as the original
search_mode(). search_mode() itself is untouched and still
exists in search.py.

Search Pokemon / Search Settings / Search Statistics don't have
an underlying implementation yet, so they show a clear
"not yet implemented" stub rather than fake data.
"""

from search import normal_maps_mode, exclusive_maps_mode


BANNER = (
    "\n"
    + "=" * 60
    + "\nSEARCHING\n"
    + "=" * 60
    + "\n"
    "1. Normal Maps\n"
    "2. Exclusive Legendary Areas\n"
    "3. Search Pokemon\n"
    "4. Search Settings\n"
    "5. Search Statistics\n"
    "6. Back"
)


def _not_yet_implemented(section_name):

    print()
    print("=" * 60)
    print(section_name.upper())
    print("=" * 60)
    print()
    print(
        f"{section_name} isn't implemented yet. "
        "This will be added in a later phase."
    )
    input("\nPress Enter to return to the search menu...")


def search_menu(driver):
    while True:

        print(BANNER)

        choice = input("\nChoose: ").strip()

        if choice == "1":
            normal_maps_mode(driver)

        elif choice == "2":
            exclusive_maps_mode(driver)

        elif choice == "3":
            _not_yet_implemented("Search Pokemon")

        elif choice == "4":
            _not_yet_implemented("Search Settings")

        elif choice == "5":
            _not_yet_implemented("Search Statistics")

        elif choice == "6":
            return

        else:
            print("✗ Invalid choice.")
