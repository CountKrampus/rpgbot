"""
Box (Your Box / PC storage) module for Eclipse RPG Automation.

Built from the HTML of https://eclipserpg.com/your_box.
Uses BeautifulSoup for instant, 100% reliable DOM parsing and extraction of
Pokémon names, levels, variants, genders, and stats.
"""

import re
import os
import time
from urllib.parse import urlencode
from datetime import datetime
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
    NoSuchElementException,
)

from config import BASE_URL
from utils import wait_for_document_ready, sleep_random


BOX_URL = f"{BASE_URL}/your_box"

ROW_ID_PATTERN = re.compile(r"^YB_Pokemon(\d+)$")
NAME_LEVEL_PATTERN = re.compile(r"^(.*?)(?:\s+Lv\.?\s*([\d,]+))?$", re.IGNORECASE)

# Variant and Era lists derived from site and Gastly_Collection.txt
KNOWN_ERAS = [
    "hyper galaxy",
    "genesis",
    "relic",
    "retro",
    "hyper",
    "galaxy",
    "undead",
]

KNOWN_VARIANTS = [
    "shiny",
    "dark",
    "silver",
    "golden",
    "crystal",
    "ruby",
    "sapphire",
    "emerald",
    "shadow",
    "light",
    "legacy",
    "pearl",
    "astral",
    "rainbow",
    "metallic",
    "mystic",
    "amethyst",
    "platinum",
]


def open_box(driver, page: int = 1):
    """
    Navigate to the plain box page.
    """
    try:
        url = BOX_URL if page <= 1 else f"{BOX_URL}?page={page}"
        driver.get(url)
        wait_for_document_ready(driver)
        sleep_random(0.5, 0.9)
        return True
    except WebDriverException:
        return False


def get_account_user_id(driver):
    """
    Read the account's user ID from the box search form or window.UserID.
    """
    try:
        field = driver.find_element(
            By.CSS_SELECTOR,
            "input[name='user']",
        )
        value = field.get_attribute("value")
        if value:
            return value
    except (NoSuchElementException, WebDriverException):
        pass

    try:
        return driver.execute_script(
            "return window.UserID ? String(window.UserID) : null;"
        )
    except WebDriverException:
        return None


def get_box_total_pages(driver) -> int:
    """
    Detect the total number of pages in the box.
    """
    total_pages = 1
    try:
        links = driver.find_elements(
            By.CSS_SELECTOR,
            "a.page-number-link, a[href*='page='], .pagination a, a[href*='your_box?']"
        )
        for link in links:
            text = link.text.strip()
            if text.isdigit():
                total_pages = max(total_pages, int(text))
            else:
                href = link.get_attribute("href") or ""
                m = re.search(r"[?&]page=(\d+)", href)
                if m:
                    total_pages = max(total_pages, int(m.group(1)))
    except Exception:
        pass
    return total_pages


def parse_pokemon_details(name_text: str) -> dict:
    """
    Parse a full Pokémon name into its era, variant, and base species name.

    Examples:
        "Genesis Shiny Gastly" -> Era="Genesis", Variant="Shiny", Species="Gastly"
        "Dark Gastly"          -> Era="", Variant="Dark", Species="Gastly"
        "Pikachu"              -> Era="", Variant="Normal", Species="Pikachu"
    """
    if not name_text:
        return {"raw_name": "", "era": "", "variant": "Normal", "species": "", "display_category": "Normal"}

    cleaned = name_text.strip()
    words = cleaned.split()

    era = ""
    variant = ""

    # Check for two-word era (e.g. "Hyper Galaxy")
    if len(words) >= 3 and f"{words[0]} {words[1]}".lower() in KNOWN_ERAS:
        era = f"{words[0].title()} {words[1].title()}"
        words = words[2:]
    elif len(words) >= 2 and words[0].lower() in KNOWN_ERAS:
        era = words[0].title()
        words = words[1:]

    # Check for variant (e.g. "Shiny", "Dark", "Crystal", etc.)
    if words and words[0].lower() in KNOWN_VARIANTS:
        variant = words[0].title()
        words = words[1:]
    else:
        variant = "Normal"

    species = " ".join(words).strip()
    if not species:
        species = cleaned

    category_parts = [p for p in [era, variant if variant != "Normal" else ""] if p]
    display_category = " ".join(category_parts) if category_parts else "Normal"

    return {
        "raw_name": cleaned,
        "era": era,
        "variant": variant,
        "species": species,
        "display_category": display_category,
    }


def parse_tooltip_stats(tooltip_text: str) -> dict:
    """
    Extract HP/MP/ATK/DEF/SPD stats from tooltip text if available.
    """
    stats = {}
    if not tooltip_text:
        return stats

    patterns = {
        "hp": r"HP:\s*([\d,]+)",
        "mp": r"MP:\s*([\d,]+)",
        "attack": r"Attack:\s*([\d,]+)",
        "defense": r"Defense:\s*([\d,]+)",
        "sp_attack": r"Sp\.\s*Atk:\s*([\d,]+)",
        "sp_defense": r"Sp\.\s*Def:\s*([\d,]+)",
        "speed": r"Speed:\s*([\d,]+)",
    }

    for stat_name, pat in patterns.items():
        m = re.search(pat, tooltip_text, re.IGNORECASE)
        if m:
            try:
                stats[stat_name] = int(m.group(1).replace(",", ""))
            except ValueError:
                pass

    return stats


def get_box_pokemon(driver):
    """
    Scrape the Pokémon listed on the CURRENTLY LOADED box page using BeautifulSoup
    for 100% DOM extraction accuracy, complete immunity to Selenium visibility bugs,
    and fast parsing.
    """
    results = []

    try:
        html = driver.page_source
    except WebDriverException:
        return results

    if not html:
        return results

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr", id=re.compile(r"^YB_Pokemon(\d+)"))

    for row in rows:
        try:
            row_id = row.get("id") or ""
            m_id = ROW_ID_PATTERN.match(row_id)
            if not m_id:
                continue
            pokemon_id = m_id.group(1)

            # 1. Extract link text
            link = row.find("a", href=re.compile(rf"/pokemon\?id={pokemon_id}"))
            raw_text = ""
            if link:
                raw_text = link.get_text(separator=" ", strip=True)

            # Fallback to second td if link was empty
            if not raw_text:
                tds = row.find_all("td", class_="tnav_left")
                if len(tds) >= 2:
                    raw_text = tds[1].get_text(separator=" ", strip=True)

            # 2. Parse level and name
            level = None
            name = raw_text

            if raw_text:
                lvl_match = re.search(r"Lv\.?\s*([\d,]+)", raw_text, re.IGNORECASE)
                if lvl_match:
                    try:
                        level = int(lvl_match.group(1).replace(",", ""))
                    except ValueError:
                        pass
                    # Strip the level portion from the name
                    name = re.sub(r"\s*Lv\.?\s*[\d,]+.*$", "", raw_text, flags=re.IGNORECASE).strip()

            # 3. Fallback to icon image alt or filename if name is still empty
            if not name:
                icon_img = row.find("img", src=re.compile(r"/icons/"))
                if icon_img:
                    alt = icon_img.get("alt") or icon_img.get("title")
                    if alt:
                        name = alt.strip()
                    else:
                        src = icon_img.get("src") or ""
                        filename = os.path.basename(src).replace(".png", "").replace(".gif", "")
                        if filename:
                            name = re.sub(r"([a-z])([A-Z])", r"\1 \2", filename).strip()

            # 4. Extract Gender
            gender = None
            gender_img = row.find("img", src=re.compile(r"gender-(male|female)"))
            if gender_img:
                src = gender_img.get("src") or ""
                if "gender-male" in src:
                    gender = "male"
                elif "gender-female" in src:
                    gender = "female"

            # 5. Extract Tooltip Stats
            stats = {}
            tooltip = row.find("div", id=re.compile(rf"^BoxTooltip{pokemon_id}"))
            if tooltip:
                stats = parse_tooltip_stats(tooltip.get_text(separator=" ", strip=True))

            details = parse_pokemon_details(name)

            results.append({
                "id": pokemon_id,
                "name": name if name else "Unknown",
                "species": details["species"] if details["species"] else (name if name else "Unknown"),
                "era": details["era"],
                "variant": details["variant"],
                "display_category": details["display_category"],
                "level": level,
                "gender": gender,
                "stats": stats,
            })

        except Exception:
            continue

    return results


def fetch_all_box_pokemon(driver, query: str = "", progress_callback=None) -> list:
    """
    Fetch ALL Pokémon across ALL pages of the box (or all pages of a search query).
    Ensures 100% of the user's box is indexed.
    """
    user_id = get_account_user_id(driver)
    if not user_id:
        open_box(driver)
        user_id = get_account_user_id(driver)

    base_params = {
        "user": user_id or "",
        "special_eid": "",
        "input_search": query,
    }

    url = f"{BOX_URL}?{urlencode(base_params)}"

    try:
        driver.get(url)
        wait_for_document_ready(driver)
        sleep_random(0.5, 0.9)
    except WebDriverException:
        return []

    total_pages = get_box_total_pages(driver)
    all_pokemon = []

    # Page 1
    page1 = get_box_pokemon(driver)
    all_pokemon.extend(page1)
    if progress_callback:
        progress_callback(1, total_pages, len(all_pokemon))

    # Pages 2+
    for page in range(2, total_pages + 1):
        page_params = dict(base_params)
        page_params["page"] = page
        page_url = f"{BOX_URL}?{urlencode(page_params)}"

        try:
            driver.get(page_url)
            wait_for_document_ready(driver)
            sleep_random(0.3, 0.6)
            page_pokes = get_box_pokemon(driver)
            all_pokemon.extend(page_pokes)
            if progress_callback:
                progress_callback(page, total_pages, len(all_pokemon))
        except WebDriverException:
            break

    return all_pokemon


def search_box(driver, query):
    """
    Search the box using the site's own search form (GET request)
    and retrieve all matching pages across the entire account.
    """
    return fetch_all_box_pokemon(driver, query=query)


def move_to_party(driver, pokemon_id: str, slot: int) -> bool:
    """
    Move a Pokémon from the box into a specific team party slot (1-6).
    Executes the site's JavaScript `from_box(id, slot)` handler.
    """
    if slot < 1 or slot > 6:
        return False

    try:
        driver.execute_script(f"from_box({pokemon_id}, {slot});")
        time.sleep(0.8)
        wait_for_document_ready(driver)
        return True
    except WebDriverException:
        pass

    try:
        button = driver.find_element(
            By.XPATH,
            f"//tr[@id='YB_Pokemon{pokemon_id}']//button[normalize-space()='{slot}']",
        )
        button.click()
        time.sleep(0.8)
        wait_for_document_ready(driver)
        return True
    except Exception:
        return False


def get_party_pokemon(driver) -> list:
    """
    Scrape currently active party Pokémon from the page sidebar/header.
    """
    party = []
    try:
        html = driver.page_source
        if not html:
            return party

        soup = BeautifulSoup(html, "html.parser")
        names = soup.find_all(class_=re.compile(r"party-pokemon-name"))
        levels = soup.find_all(class_=re.compile(r"party-pokemon-level"))

        for i in range(len(names)):
            name_text = names[i].get_text(strip=True)
            level_text = levels[i].get_text(strip=True) if i < len(levels) else ""

            level = None
            lvl_match = re.search(r"(\d+)", level_text)
            if lvl_match:
                level = int(lvl_match.group(1))

            details = parse_pokemon_details(name_text)
            party.append({
                "slot": i + 1,
                "name": name_text,
                "species": details["species"],
                "display_category": details["display_category"],
                "level": level,
            })
    except Exception:
        pass

    return party


def export_box_to_file(pokemon_list: list, filepath: str = None) -> str:
    """
    Export a clean structured text file of the user's box collection.
    """
    if not filepath:
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Box_Inventory.txt",
        )

    lines = [
        "╔══════════════════════════════════════════════════════════════════════════════╗",
        "║                       ECLIPSE RPG POKÉMON BOX INVENTORY                      ║",
        "╠══════════════════════════════════════════════════════════════════════════════╣",
        f"║  Exported: {datetime.now().strftime('%B %d, %Y (%I:%M %p)'):<50}║",
        f"║  Total Pokémon: {len(pokemon_list):<54}║",
        "╚══════════════════════════════════════════════════════════════════════════════╝",
        "",
        f"{'ID':<12} {'SPECIES':<18} {'VARIANT / CATEGORY':<24} {'LEVEL':<10} {'GENDER':<8}",
        "-" * 78,
    ]

    for p in pokemon_list:
        lvl = f"Lv. {p['level']:,}" if p.get("level") is not None else "Lv. ?"
        gender = "Male (♂)" if p.get("gender") == "male" else ("Female (♀)" if p.get("gender") == "female" else "-")
        lines.append(
            f"{p['id']:<12} {p['species'][:16]:<18} {p['display_category'][:22]:<24} {lvl:<10} {gender:<8}"
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return filepath
