"""
Pokémon & PC Box Management Submenu for Eclipse RPG Automation.

Provides a Virtual Box Organizer, Multi-page Box Indexer, Server Search,
Party Inspector, Fast Slot Swapper, Species Variant Checklist Tracker,
Duplicate Finder, and File Exporter.
"""

import os
import sys
import platform
import time
import re

from box import (
    open_box,
    get_box_pokemon,
    fetch_all_box_pokemon,
    search_box,
    move_to_party,
    get_party_pokemon,
    parse_pokemon_details,
    export_box_to_file,
    KNOWN_VARIANTS,
    KNOWN_ERAS,
)


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

# ANSI & STYLING
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


# In-memory box cache for fast browsing/sorting
_cached_box = []


# ============================================================
# 1. ORGANIZED BOX VIEWER
# ============================================================

def _organized_box_viewer(driver, force_reload: bool = False):
    global _cached_box
    w = 71

    if not _cached_box or force_reload:
        print(f"\n{CYAN}⚡ Scanning and indexing entire PC Box storage...{RESET}")

        def progress(page, total_pages, count):
            print(f"  {GRAY}Scanned Page [{page}/{total_pages}]:{RESET} {WHITE}{count}{RESET} Pokémon found...")

        _cached_box = fetch_all_box_pokemon(driver, progress_callback=progress)

    if not _cached_box:
        print(f"\n{YELLOW}No Pokémon found in PC Box or failed to load page.{RESET}")
        input(f"\n{GRAY}Press Enter to return...{RESET}")
        return

    sort_mode = "level_desc"
    filter_keyword = ""
    page = 1
    page_size = 12

    while True:
        # Apply active filter
        if filter_keyword:
            kw = filter_keyword.lower()
            filtered = [
                p for p in _cached_box
                if kw in p["name"].lower()
                or kw in p["species"].lower()
                or kw in p["display_category"].lower()
            ]
        else:
            filtered = _cached_box

        # Apply active sorting
        if sort_mode == "level_desc":
            sorted_list = sorted(filtered, key=lambda x: x["level"] or 0, reverse=True)
            sort_label = "Level (High ➔ Low)"
        elif sort_mode == "level_asc":
            sorted_list = sorted(filtered, key=lambda x: x["level"] or 0)
            sort_label = "Level (Low ➔ High)"
        elif sort_mode == "name_asc":
            sorted_list = sorted(filtered, key=lambda x: x["species"].lower())
            sort_label = "Species (A ➔ Z)"
        elif sort_mode == "variant_asc":
            sorted_list = sorted(filtered, key=lambda x: (x["display_category"].lower(), x["species"].lower()))
            sort_label = "Variant & Category"
        else:
            sorted_list = sorted(filtered, key=lambda x: int(x["id"]) if x["id"].isdigit() else 0, reverse=True)
            sort_label = "ID (Newest First)"

        total_pages = max(1, (len(sorted_list) + page_size - 1) // page_size)
        if page > total_pages:
            page = total_pages

        start_idx = (page - 1) * page_size
        page_items = sorted_list[start_idx:start_idx + page_size]

        top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
        mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
        bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

        filter_status = f"Filter: '{filter_keyword}'" if filter_keyword else "All"
        hud = f"  {GRAY}INDEXED:{RESET} {CYAN}{len(sorted_list)}/{len(_cached_box)}{RESET}  │  {GRAY}SORT:{RESET} {CYAN}{sort_label[:17]}{RESET}  │  {GRAY}PAGE:{RESET} {CYAN}{page}/{total_pages}{RESET}"

        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}📦  VIRTUAL ORGANIZED BOX VIEWER{RESET}", w))
        print(mid_border)
        print(_row(hud, w))
        print(mid_border)
        print(_row(f"  {GRAY}{'#':<4} {'ID':<10} {'POKÉMON':<20} {'VARIANT':<16} {'LEVEL':<10} {'GEN':<4}{RESET}", w))
        print(mid_border)

        if not page_items:
            print(_row(f"    {YELLOW}No Pokémon matching filter '{filter_keyword}'.{RESET}", w))
        else:
            for idx, p in enumerate(page_items, start_idx + 1):
                lvl = f"Lv. {p['level']:,}" if p.get("level") is not None else "Lv. ?"
                gen = "♂" if p.get("gender") == "male" else ("♀" if p.get("gender") == "female" else "-")
                var = p["display_category"]
                species = p["species"]

                line = f"  {KEY_COLOR}[{idx:2d}]{RESET} {GRAY}{p['id']:<10}{RESET} {WHITE}{species[:18]:<18}{RESET} {GOLD}{var[:14]:<14}{RESET} {YELLOW}{lvl:<10}{RESET} {CYAN}{gen}{RESET}"
                print(_row(line, w))

        print(mid_border)
        print(_row(f"  {KEY_COLOR}[N]{RESET} Next  {KEY_COLOR}[P]{RESET} Prev  {KEY_COLOR}[S]{RESET} Sort  {KEY_COLOR}[F]{RESET} Filter  {KEY_COLOR}[R]{RESET} Reload  {KEY_COLOR}[M]{RESET} Party  {RED}[B]{RESET} Back", w))
        print(bot_border)

        try:
            cmd = input(f"\n{BOLD}{CYAN}❯ Option / Action {GRAY}[N/P/S/F/R/M/B]:{RESET} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if cmd == "n":
            if page < total_pages:
                page += 1
            else:
                print(f"{YELLOW}Already on last page.{RESET}")
                time.sleep(0.6)
        elif cmd == "p":
            if page > 1:
                page -= 1
            else:
                print(f"{YELLOW}Already on first page.{RESET}")
                time.sleep(0.6)
        elif cmd == "r":
            _cached_box = []
            return _organized_box_viewer(driver, force_reload=True)
        elif cmd == "s":
            print(f"\n{CATEGORY_COLOR}Select Sorting Method:{RESET}")
            print(f"  {KEY_COLOR}[ 1]{RESET} Level (Highest ➔ Lowest)")
            print(f"  {KEY_COLOR}[ 2]{RESET} Level (Lowest ➔ Highest)")
            print(f"  {KEY_COLOR}[ 3]{RESET} Species Alphabetical (A ➔ Z)")
            print(f"  {KEY_COLOR}[ 4]{RESET} Variant & Category")
            print(f"  {KEY_COLOR}[ 5]{RESET} ID / Recent")
            s_choice = input(f"\n{BOLD}{CYAN}❯ Choose sort [1-5]:{RESET} ").strip()
            if s_choice == "1":
                sort_mode = "level_desc"
            elif s_choice == "2":
                sort_mode = "level_asc"
            elif s_choice == "3":
                sort_mode = "name_asc"
            elif s_choice == "4":
                sort_mode = "variant_asc"
            elif s_choice == "5":
                sort_mode = "id_desc"
            page = 1
        elif cmd == "f":
            print(f"\n{CATEGORY_COLOR}Filter Options:{RESET}")
            print(f"  {KEY_COLOR}[ 1]{RESET} Instant Keyword / Variant Filter (on indexed box)")
            print(f"  {KEY_COLOR}[ 2]{RESET} Deep Server Search (query Eclipse RPG server)")
            print(f"  {KEY_COLOR}[ 3]{RESET} Clear Active Filter")
            f_mode = input(f"\n{BOLD}{CYAN}❯ Choose filter mode [1-3]:{RESET} ").strip()

            if f_mode == "1":
                filter_keyword = input(f"\n{BOLD}{CYAN}❯ Filter keyword {GRAY}(e.g. 'shiny', 'crystal', 'gastly'){CYAN}:{RESET} ").strip()
                page = 1
            elif f_mode == "2":
                server_query = input(f"\n{BOLD}{CYAN}❯ Search term to query on server:{RESET} ").strip()
                if server_query:
                    print(f"\n{CYAN}⚡ Querying Eclipse RPG server across all pages for '{server_query}'...{RESET}")
                    results = search_box(driver, server_query)
                    if results:
                        # Append/merge into cached box if new
                        existing_ids = {p["id"] for p in _cached_box}
                        for r in results:
                            if r["id"] not in existing_ids:
                                _cached_box.append(r)
                                existing_ids.add(r["id"])
                        filter_keyword = server_query
                        page = 1
                        print(f"{GREEN}✓ Found {len(results)} matching Pokémon on server!{RESET}")
                    else:
                        print(f"{YELLOW}No matches found on server for '{server_query}'.{RESET}")
                    time.sleep(1.0)
            elif f_mode == "3":
                filter_keyword = ""
                page = 1
        elif cmd == "m":
            if not sorted_list:
                continue
            num_str = input(f"\n{BOLD}{CYAN}❯ Enter Pokémon list # to move into party {GRAY}[1-{len(sorted_list)}]{CYAN}:{RESET} ").strip()
            try:
                sel_idx = int(num_str) - 1
                target_poke = sorted_list[sel_idx]
            except (ValueError, IndexError):
                print(f"{RED}✗ Invalid Pokémon list number.{RESET}")
                time.sleep(1.0)
                continue

            slot_str = input(f"{BOLD}{CYAN}❯ Assign to Party Slot {GRAY}[1-6]{CYAN}:{RESET} ").strip()
            try:
                slot_num = int(slot_str)
            except ValueError:
                print(f"{RED}✗ Invalid slot number.{RESET}")
                time.sleep(1.0)
                continue

            print(f"\n{CYAN}⚡ Moving {target_poke['name']} into Party Slot {slot_num}...{RESET}")
            if move_to_party(driver, target_poke["id"], slot_num):
                print(f"{GREEN}✓ Successfully moved {target_poke['name']} into Party Slot {slot_num}!{RESET}")
            else:
                print(f"{RED}✗ Could not move Pokémon to party.{RESET}")
            time.sleep(1.2)
        elif cmd == "b":
            return


# ============================================================
# 2. PARTY INSPECTOR & SWAPPER
# ============================================================

def _party_inspector(driver):
    global _cached_box
    w = 71
    print(f"\n{CYAN}⚡ Inspecting current Battle Party...{RESET}")
    open_box(driver)
    party = get_party_pokemon(driver)

    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    print()
    print(top_border)
    print(_row(f"  {BOLD}{MAGENTA}⚔️  ACTIVE BATTLE PARTY (6 SLOTS){RESET}", w))
    print(mid_border)
    print(_row("", w))

    if not party:
        for i in range(1, 7):
            print(_row(f"    {KEY_COLOR}Slot {i}:{RESET} {GRAY}(Party members active on current session){RESET}", w))
    else:
        for p in party:
            lvl = f"Lv. {p['level']:,}" if p.get("level") is not None else "Lv. ?"
            print(_row(f"    {KEY_COLOR}Slot {p['slot']}:{RESET} {WHITE}{p['name']:<24}{RESET} {GOLD}{p['display_category']:<16}{RESET} {YELLOW}{lvl}{RESET}", w))

    print(_row("", w))
    print(mid_border)
    print(_row(f"  {KEY_COLOR}[ 1]{RESET} {WHITE}Swap a Pokémon into Party Slot (1-6){RESET}", w))
    print(_row(f"  {RED}[ 2]{RESET} {WHITE}Back{RESET}", w))
    print(bot_border)

    choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-2]{CYAN}:{RESET} ").strip()
    if choice == "1":
        query = input(f"\n{BOLD}{CYAN}❯ Search box for Pokémon to add to party:{RESET} ").strip()
        if not query:
            return
        results = search_box(driver, query)
        if not results:
            print(f"{YELLOW}No Pokémon found matching '{query}'.{RESET}")
            time.sleep(1.0)
            return

        print(f"\n{GOLD}Matching Pokémon in Box ({len(results)} found):{RESET}\n")
        for i, p in enumerate(results[:15], 1):
            lvl = f"Lv. {p['level']:,}" if p.get("level") is not None else "Lv. ?"
            print(f"  {KEY_COLOR}[{i:2d}]{RESET} {WHITE}{p['name']:<24}{RESET} {GOLD}{p['display_category']:<16}{RESET} {YELLOW}{lvl}{RESET}")

        pick = input(f"\n{BOLD}{CYAN}❯ Choose # to move into party {GRAY}[1-{len(results[:15])}]{CYAN}:{RESET} ").strip()
        try:
            chosen = results[int(pick) - 1]
        except (ValueError, IndexError):
            print(f"{RED}✗ Invalid selection.{RESET}")
            time.sleep(1.0)
            return

        slot = input(f"{BOLD}{CYAN}❯ Assign to Party Slot {GRAY}[1-6]{CYAN}:{RESET} ").strip()
        try:
            slot_num = int(slot)
        except ValueError:
            print(f"{RED}✗ Invalid slot number.{RESET}")
            time.sleep(1.0)
            return

        print(f"\n{CYAN}⚡ Moving {chosen['name']} to Slot {slot_num}...{RESET}")
        if move_to_party(driver, chosen["id"], slot_num):
            print(f"{GREEN}✓ Moved {chosen['name']} into Party Slot {slot_num}!{RESET}")
        else:
            print(f"{RED}✗ Failed to swap Pokémon into party.{RESET}")
        time.sleep(1.2)


# ============================================================
# 3. VARIANT CHECKLIST TRACKER
# ============================================================

def _variant_checklist(driver):
    w = 64
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    species = input(f"\n{BOLD}{CYAN}❯ Enter Pokémon Species to track {GRAY}(e.g. Gastly, Pikachu, Eevee){CYAN}:{RESET} ").strip()
    if not species:
        return

    print(f"\n{CYAN}⚡ Scanning entire PC box for all '{species}' variants across all pages...{RESET}")
    matches = search_box(driver, species)

    owned_categories = set()
    for p in matches:
        if p["species"].lower() == species.lower():
            owned_categories.add(p["display_category"].lower())

    target_variants = [
        "Normal", "Shiny", "Dark", "Silver", "Golden",
        "Crystal", "Ruby", "Sapphire", "Emerald",
        "Shadow", "Light", "Legacy", "Pearl", "Astral", "Rainbow",
        "Genesis Normal", "Genesis Shiny", "Genesis Dark", "Genesis Crystal", "Genesis Shadow",
        "Relic Normal", "Relic Shiny", "Relic Crystal", "Relic Rainbow",
        "Retro Normal", "Retro Shiny", "Retro Crystal",
        "Hyper Normal", "Hyper Shiny", "Hyper Shadow",
        "Undead Normal", "Undead Shiny", "Undead Dark", "Undead Rainbow",
    ]

    owned_count = 0
    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}📋  {species.upper()} VARIANT COLLECTION CHECKLIST{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    for v in target_variants:
        if v.lower() in owned_categories or any(v.lower() in p["name"].lower() for p in matches):
            owned_count += 1
            print(_drow(f"  {GREEN}[✓] {v:<26}{RESET} {CYAN}OWNED{RESET}"))
        else:
            print(_drow(f"  {GRAY}[✗] {v:<26} MISSING{RESET}"))

    pct = (owned_count / len(target_variants)) * 100
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GOLD}Collection Progress:{RESET} {WHITE}{owned_count}/{len(target_variants)}{RESET} ({YELLOW}{pct:.1f}%{RESET})"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


# ============================================================
# 4. DUPLICATE FINDER
# ============================================================

def _duplicate_finder(driver):
    global _cached_box
    w = 64
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    if not _cached_box:
        print(f"\n{CYAN}⚡ Indexing entire PC Box storage for duplicates...{RESET}")
        _cached_box = fetch_all_box_pokemon(driver)

    from collections import defaultdict
    grouped = defaultdict(list)
    for p in _cached_box:
        key = (p["species"], p["display_category"])
        grouped[key].append(p)

    duplicates = {k: v for k, v in grouped.items() if len(v) > 1}

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}🔍  DUPLICATE POKÉMON FINDER{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    if not duplicates:
        print(_drow(f"  {GREEN}✓ No duplicate Pokémon found in box!{RESET}"))
    else:
        print(_drow(f"  {YELLOW}Found {len(duplicates)} Pokémon species with duplicate copies:{RESET}"))
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        for (species, var), p_list in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True):
            print(_drow(f"  {GOLD}● {species}{RESET} {GRAY}({var}){RESET}: {CYAN}{len(p_list)} copies{RESET}"))
            levels_str = ", ".join(f"Lv.{p['level'] or '?'}" for p in p_list[:5])
            if len(p_list) > 5:
                levels_str += f" +{len(p_list)-5} more"
            print(_drow(f"    {GRAY}Levels: {levels_str}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return...{RESET}")


# ============================================================
# 5. EXPORT BOX INVENTORY
# ============================================================

def _export_box_inventory(driver):
    global _cached_box
    print(f"\n{CYAN}⚡ Indexing full box across all pages for export...{RESET}")
    _cached_box = fetch_all_box_pokemon(driver)

    if not _cached_box:
        print(f"{YELLOW}No Pokémon found to export.{RESET}")
        time.sleep(1.0)
        return

    filepath = export_box_to_file(_cached_box)
    print(f"\n{GREEN}✓ Successfully exported all {len(_cached_box)} Pokémon across your box to:{RESET}")
    print(f"  {WHITE}{filepath}{RESET}")
    time.sleep(1.0)
    input(f"\n{GRAY}Press Enter to return...{RESET}")


# ============================================================
# MAIN POKEMON MENU
# ============================================================

def pokemon_menu(driver):
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    while True:
        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}📦  POKÉMON & PC BOX MANAGER{RESET}", w))
        print(mid_border)
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 1]{RESET} {NAME_COLOR}Organized Box Viewer{RESET}   {DESC_COLOR}— Index, multi-sort & filter all stored Pokémon{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 2]{RESET} {NAME_COLOR}Party Inspector & Swap{RESET} {DESC_COLOR}— View active battle team & swap slots (1-6){RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 3]{RESET} {NAME_COLOR}Variant Checklist{RESET}      {DESC_COLOR}— Track owned vs missing variant forms{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 4]{RESET} {NAME_COLOR}Duplicate Finder{RESET}       {DESC_COLOR}— Identify duplicate species taking up box space{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 5]{RESET} {NAME_COLOR}Export Box Inventory{RESET}   {DESC_COLOR}— Export full box catalog to Box_Inventory.txt{RESET}", w))
        print(_row("", w))
        print(_row(f"    {RED}{BOLD}[ 6]{RESET} {RED}Back{RESET}                   {DESC_COLOR}— Return to main menu{RESET}", w))
        print(_row("", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-6]{CYAN}:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            _organized_box_viewer(driver)
        elif choice == "2":
            _party_inspector(driver)
        elif choice == "3":
            _variant_checklist(driver)
        elif choice == "4":
            _duplicate_finder(driver)
        elif choice == "5":
            _export_box_inventory(driver)
        elif choice == "6":
            return
        else:
            print(f"\n{RED}✗ Invalid choice '{choice}'. Please choose 1-6.{RESET}")
            time.sleep(1.0)
