"""
Search submenu for Eclipse RPG Automation.

Normal Maps and Exclusive Legendary Areas call into the split
functions in search.py (normal_maps_mode / exclusive_maps_mode).

Search Settings and Search Statistics are now real. Search
Pokemon stays a stub - it needs the actual HTML of a map's
wild-Pokémon listing to scrape reliably, which hasn't been
provided yet.
"""

from search import (
    normal_maps_mode,
    exclusive_maps_mode,
    get_search_delay,
    set_search_delay,
    get_search_stats,
)
from capture import get_capture_stats


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


def _search_settings():

    print()
    print("=" * 60)
    print("SEARCH SETTINGS")
    print("=" * 60)

    current_min, current_max = get_search_delay()

    print()
    print(
        f"Delay between searches: "
        f"{current_min}-{current_max} seconds"
    )

    answer = input(
        "\nNew delay range as 'min,max' "
        "(blank to keep current): "
    ).strip()

    if not answer:
        print("Unchanged.")
        input("\nPress Enter to return to the search menu...")
        return

    parts = answer.split(",")

    if len(parts) != 2:
        print("✗ Enter two numbers separated by a comma, e.g. 1.5,2.5")
        input("\nPress Enter to return to the search menu...")
        return

    try:
        new_min = float(parts[0].strip())
        new_max = float(parts[1].strip())

    except ValueError:
        print("✗ Invalid numbers.")
        input("\nPress Enter to return to the search menu...")
        return

    if set_search_delay(new_min, new_max):
        print(f"✓ Delay set to {new_min}-{new_max} seconds.")
    else:
        print("✗ Invalid range - min must be <= max, both >= 0.")

    input("\nPress Enter to return to the search menu...")


def _search_statistics():

    print()
    print("=" * 60)
    print("SEARCH STATISTICS")
    print("=" * 60)

    search_stats = get_search_stats()
    capture_stats = get_capture_stats()

    print()
    print(f"Total searches this session: {search_stats['total_searches']}")

    if search_stats["history"]:

        print()
        print("By map:")

        for entry in search_stats["history"]:
            print(f"  {entry['map']}: {entry['searches']}")

    else:

        print("No searches run yet this session.")

    print()
    print(f"Encounters: {capture_stats['encounters']}")
    print(f"Caught:     {capture_stats['captured']}")
    print(f"Failed:     {capture_stats['failed']}")

    if capture_stats["encounters"] > 0:

        rate = (
            capture_stats["captured"]
            / capture_stats["encounters"]
            * 100
        )

        print(f"Capture rate: {rate:.1f}%")

    if capture_stats["balls_used"]:

        print()
        print("Balls used:")

        for ball, count in capture_stats["balls_used"].items():
            print(f"  {ball}: {count}")

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
            _search_settings()

        elif choice == "5":
            _search_statistics()

        elif choice == "6":
            return

        else:
            print("✗ Invalid choice.")
