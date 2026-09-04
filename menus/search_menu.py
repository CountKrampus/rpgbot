"""
Search submenu for Eclipse RPG Automation.

Normal Maps and Exclusive Legendary Areas call into search.py.
Includes Pokemon search across maps, Box search, settings & statistics.
"""

import os
import sys
import platform
import time
import re

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
from capture import get_preferred_ball_order, set_preferred_ball_order
from box import search_box


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


# ============================================================
# ACTIONS & HELPERS
# ============================================================

def _search_pokemon(driver):
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}🔍  SEARCH POKÉMON ACROSS MAPS{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Search all unlocked maps for wild spawn locations.{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()

    query = input(
        f"{BOLD}{CYAN}❯ Pokémon name or keyword {GRAY}(e.g. 'gastly', 'shiny'){CYAN}:{RESET} "
    ).strip()

    if not query:
        print(f"{YELLOW}✗ Nothing entered.{RESET}")
        time.sleep(0.8)
        return

    print(f"\n{CYAN}⚡ Scanning all map pages for '{query}'...{RESET} {GRAY}(this may take a moment){RESET}")

    def progress(map_name, index, total):
        print(f"  {GRAY}[{index}/{total}]{RESET} Checking {WHITE}{map_name}{RESET}...")

    results = search_pokemon_across_maps(
        driver,
        query,
        progress_callback=progress,
    )

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}RESULTS FOR '{query.upper()}'{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    if not results:
        print(_drow(f"  {RED}No matches found across scanned maps.{RESET}"))
    else:
        for map_name, pokes in results.items():
            print(_drow(f"  {GOLD}● {map_name}:{RESET}"))
            for pokemon in pokes:
                dex_marker = f" {GREEN}(dexed){RESET}" if pokemon.get("dexed") else ""
                print(_drow(f"    - {WHITE}{pokemon['name']}{RESET}{dex_marker}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return to the search menu...{RESET}")


def _search_settings():
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    current_min, current_max = get_search_delay()

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}⚙️  SEARCH SETTINGS{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Current Delay Range:{RESET} {CYAN}{current_min:.2f}s - {current_max:.2f}s{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()

    answer = input(
        f"{BOLD}{CYAN}❯ New delay range as 'min,max' {GRAY}[blank to keep current]{CYAN}:{RESET} "
    ).strip()

    if not answer:
        print(f"{GRAY}Unchanged.{RESET}")
        time.sleep(0.8)
        return

    parts = answer.split(",")

    if len(parts) != 2:
        print(f"{RED}✗ Enter two numbers separated by a comma (e.g. 1.5,2.5){RESET}")
        time.sleep(1.2)
        return

    try:
        new_min = float(parts[0].strip())
        new_max = float(parts[1].strip())
    except ValueError:
        print(f"{RED}✗ Invalid numbers.{RESET}")
        time.sleep(1.2)
        return

    if set_search_delay(new_min, new_max):
        print(f"{GREEN}✓ Delay set to {new_min:.2f}s - {new_max:.2f}s.{RESET}")
        time.sleep(1.0)
    else:
        print(f"{RED}✗ Invalid range - min must be <= max and both >= 0.{RESET}")
        time.sleep(1.2)


def _search_ball_settings():
    current = get_preferred_ball_order()
    answer = input(
        "Poké Ball priority (comma-separated) "
        f"[{', '.join(current)}]: "
    ).strip()
    if not answer:
        return
    balls = [item.strip() for item in answer.split(",") if item.strip()]
    if set_preferred_ball_order(balls):
        print(f"{GREEN}✓ Ball priority updated.{RESET}")
    else:
        print(f"{RED}✗ Ball priority cannot be empty.{RESET}")
    time.sleep(0.8)


def _search_statistics():
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    search_stats = get_search_stats()
    capture_stats = get_capture_stats()
    encountered_stats = get_encountered_pokemon_stats()

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}📊  SEARCH & ENCOUNTER STATISTICS{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Total Searches this session:{RESET} {CYAN}{search_stats['total_searches']}{RESET}"))
    print(_drow(f"  {GRAY}Encounters:{RESET} {WHITE}{capture_stats['encounters']}{RESET}  │  {GRAY}Caught:{RESET} {GREEN}{capture_stats['captured']}{RESET}  │  {GRAY}Failed:{RESET} {RED}{capture_stats['failed']}{RESET}"))

    if capture_stats["encounters"] > 0:
        rate = (capture_stats["captured"] / capture_stats["encounters"]) * 100
        print(_drow(f"  {GRAY}Capture Success Rate:{RESET} {YELLOW}{rate:.1f}%{RESET}"))

    if search_stats.get("history"):
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {GOLD}Searches by Map:{RESET}"))
        for entry in search_stats["history"]:
            print(_drow(f"    - {WHITE}{entry['map']}:{RESET} {CYAN}{entry['searches']}{RESET}"))

    if capture_stats.get("balls_used"):
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {GOLD}Poké Balls Used:{RESET}"))
        for ball, count in capture_stats["balls_used"].items():
            print(_drow(f"    - {WHITE}{ball}:{RESET} {CYAN}{count}{RESET}"))

    if encountered_stats.get("rare"):
        print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
        print(_drow(f"  {YELLOW}★ Rare Encounters:{RESET}"))
        for p in encountered_stats["rare"]:
            lvl = f"Lv. {p['level']}" if p.get("level") is not None else "Lv. ?"
            print(_drow(f"    ★ {GOLD}{p['name']}{RESET} {GRAY}({lvl}){RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return to the search menu...{RESET}")


def _search_box(driver):
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}📦  SEARCH PC BOX{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Search your stored Pokémon storage directly.{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()

    query = input(f"{BOLD}{CYAN}❯ Pokémon name to query in box:{RESET} ").strip()

    if not query:
        print(f"{YELLOW}✗ Nothing entered.{RESET}")
        time.sleep(0.8)
        return

    print(f"\n{CYAN}⚡ Querying PC box storage for '{query}'...{RESET}")

    results = search_box(driver, query)

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}BOX RESULTS FOR '{query.upper()}'{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")

    if not results:
        print(_drow(f"  {RED}No matching Pokémon found in box.{RESET}"))
    else:
        for pokemon in results:
            level_text = f"Lv. {pokemon['level']}" if pokemon.get("level") is not None else "Lv. ?"
            gender_text = f" ({pokemon['gender']})" if pokemon.get("gender") else ""
            print(_drow(f"  - {WHITE}{pokemon['name']}{RESET} {YELLOW}{level_text}{RESET}{GRAY}{gender_text}{RESET}"))

    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return to the search menu...{RESET}")


def search_menu(driver):
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    while True:
        min_d, max_d = get_search_delay()
        s_stats = get_search_stats()
        c_stats = get_capture_stats()
        hud = f"  {GRAY}DELAY:{RESET} {CYAN}{min_d:.1f}-{max_d:.1f}s{RESET}  │  {GRAY}SEARCHES:{RESET} {CYAN}{s_stats['total_searches']}{RESET}  │  {GRAY}CAUGHT:{RESET} {GREEN}{c_stats['captured']}{RESET}"

        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}🧭  SEARCHING & EXPLORATION{RESET}", w))
        print(mid_border)
        print(_row(hud, w))
        print(mid_border)
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 1]{RESET} {NAME_COLOR}Normal Maps{RESET}          {DESC_COLOR}— Explore standard world maps and wild zones{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 2]{RESET} {NAME_COLOR}Exclusive Areas{RESET}      {DESC_COLOR}— Search unlocked legendary exclusive zones{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 3]{RESET} {NAME_COLOR}Search Pokémon (Maps){RESET}{DESC_COLOR}— Find which map spawns a specific Pokémon{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 4]{RESET} {NAME_COLOR}Hunt Specific Pokémon{RESET}{DESC_COLOR}— Auto-navigate and search for a targeted species{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 5]{RESET} {NAME_COLOR}Search PC Box{RESET}        {DESC_COLOR}— Filter and check stored Pokémon in your PC box{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 6]{RESET} {NAME_COLOR}Search Settings{RESET}      {DESC_COLOR}— Customize delay intervals between searches{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 7]{RESET} {NAME_COLOR}Search Statistics{RESET}    {DESC_COLOR}— View session search counts, captures & rares{RESET}", w))
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 8]{RESET} {NAME_COLOR}Ball Settings{RESET}       {DESC_COLOR}— Choose capture ball priority{RESET}", w))
        print(_row(f"    {RED}{BOLD}[ 9]{RESET} {RED}Back{RESET}                 {DESC_COLOR}— Return to main menu{RESET}", w))
        print(_row("", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-9]{CYAN}:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            normal_maps_mode(driver)
        elif choice == "2":
            exclusive_maps_mode(driver)
        elif choice == "3":
            _search_pokemon(driver)
        elif choice == "4":
            target_pokemon_mode(driver)
        elif choice == "5":
            _search_box(driver)
        elif choice == "6":
            _search_settings()
        elif choice == "7":
            _search_statistics()
        elif choice == "8":
            _search_ball_settings()
        elif choice == "9":
            return
        else:
            print(f"\n{RED}✗ Invalid choice '{choice}'. Please choose 1-9.{RESET}")
            time.sleep(1.0)
