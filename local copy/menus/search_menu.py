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
    search_pokemon_across_maps,
    get_encountered_pokemon_stats,
    target_pokemon_mode,
)
from capture import get_capture_stats
from box import search_box


BANNER = (
    "\n"
    + "=" * 60
    + "\nSEARCHING\n"
    + "=" * 60
    + "\n"
    "1. Normal Maps\n"
    "2. Exclusive Legendary Areas\n"
    "3. Search Pokemon (maps)\n"
    "4. Search Settings\n"
    "5. Search Statistics\n"
    "6. Search Box\n"
    "7. Hunt Specific Pokémon\n"
    "8. Back"
)


def _search_pokemon(driver):

    print()
    print("=" * 60)
    print("SEARCH POKEMON")
    print("=" * 60)

    query = input(
        "\nEnter a Pokemon name (or part of it, "
        "e.g. 'gastly' or 'shiny'): "
    ).strip()

    if not query:
        print("✗ Nothing entered.")
        input("\nPress Enter to return to the search menu...")
        return

    print(
        f"\nSearching all maps for '{query}'... "
        "this checks every map page, so it may take a while."
    )

    def progress(map_name, index, total):
        print(f"  [{index}/{total}] Checking {map_name}...")

    results = search_pokemon_across_maps(
        driver,
        query,
        progress_callback=progress,
    )

    print()
    print("=" * 60)
    print(f"RESULTS FOR '{query}'")
    print("=" * 60)

    if not results:

        print("\nNo matches found on any map.")

    else:

        for map_name, pokes in results.items():

            print(f"\n{map_name}:")

            for pokemon in pokes:

                dex_marker = (
                    " (dexed)" if pokemon["dexed"] else ""
                )

                print(f"  - {pokemon['name']}{dex_marker}")

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

    encountered_stats = get_encountered_pokemon_stats()

    if encountered_stats["by_name"]:

        print()
        print(
            f"Pokemon encountered "
            f"({encountered_stats['total']} total):"
        )

        for name, count in encountered_stats["by_name"].items():
            print(f"  {name}: {count}")

    if encountered_stats["caught"]:

        print()
        print(
            f"Pokemon caught "
            f"({encountered_stats['caught_total']} total):"
        )

        for name, count in encountered_stats["caught"].items():
            print(f"  {name}: {count}")

    if encountered_stats["rare"]:

        print()
        print("★ Rare/special encounters:")

        for pokemon in encountered_stats["rare"]:

            level_text = (
                f"Lv. {pokemon['level']}"
                if pokemon["level"] is not None
                else "Lv. ?"
            )

            print(f"  {pokemon['name']} {level_text}")

    input("\nPress Enter to return to the search menu...")


def _search_box(driver):

    print()
    print("=" * 60)
    print("SEARCH BOX")
    print("=" * 60)

    query = input(
        "\nEnter a Pokemon name (or part of it): "
    ).strip()

    if not query:
        print("✗ Nothing entered.")
        input("\nPress Enter to return to the search menu...")
        return

    print(f"\nSearching your box for '{query}'...")

    results = search_box(driver, query)

    print()
    print("=" * 60)
    print(f"BOX RESULTS FOR '{query}'")
    print("=" * 60)

    if not results:

        print("\nNo matches found in your box.")

    else:

        print()

        for pokemon in results:

            level_text = (
                f"Lv. {pokemon['level']}"
                if pokemon["level"] is not None
                else "Lv. ?"
            )

            gender_text = (
                f" ({pokemon['gender']})"
                if pokemon["gender"]
                else ""
            )

            print(
                f"  - {pokemon['name']} "
                f"{level_text}{gender_text}"
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
            _search_pokemon(driver)

        elif choice == "4":
            _search_settings()

        elif choice == "5":
            _search_statistics()

        elif choice == "6":
            _search_box(driver)

        elif choice == "7":
            target_pokemon_mode(driver)

        elif choice == "8":
            return

        else:
            print("✗ Invalid choice.")
