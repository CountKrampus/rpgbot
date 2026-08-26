import time
import random
import re

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
    NoSuchElementException,
)

from capture import capture_encounter
from utils import (
    safe_click,
    normalize,
    wait_for_document_ready,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://eclipserpg.com"

WAIT_LONG = 20

SEARCH_DELAY = (
    1.5,
    2.5,
)


def get_search_delay():
    """
    Return the current (min, max) random delay range used
    between search clicks.
    """

    return SEARCH_DELAY


def set_search_delay(min_seconds, max_seconds):
    """
    Set the (min, max) random delay range used between search
    clicks. Both values must be non-negative and min <= max.
    """

    global SEARCH_DELAY

    if min_seconds < 0 or max_seconds < 0:
        return False

    if min_seconds > max_seconds:
        return False

    SEARCH_DELAY = (min_seconds, max_seconds)

    return True

EXCLUSIVE_AREAS_URL = (
    f"{BASE_URL}/legendary_areas?kind=exclusive"
)


# ============================================================
# SEARCH STATISTICS / HISTORY
# ============================================================
#
# In-memory session tracking. run_searches() below appends one
# history entry per map session and updates the running totals.

_search_stats = {
    "total_searches": 0,
    "history": [],
}


def get_search_stats():
    """
    Return a copy of the current session's search statistics:

        {
            "total_searches": 340,
            "history": [
                {"map": "Great Volcano", "searches": 120},
                {"map": "Jirachi's Park", "searches": 220},
            ],
        }
    """

    return {
        "total_searches": _search_stats["total_searches"],
        "history": list(_search_stats["history"]),
    }


def reset_search_stats():

    _search_stats["total_searches"] = 0
    _search_stats["history"] = []


def _record_search_session(map_name, searches_completed):

    _search_stats["total_searches"] += searches_completed

    _search_stats["history"].append({
        "map": map_name,
        "searches": searches_completed,
    })


# ============================================================
# NEWLY UNLOCKED EXCLUSIVE MAP DETECTION
# ============================================================
#
# Tracks which exclusive maps have been seen this session so
# get_exclusive_maps() can call out ones that just appeared,
# instead of only ever showing the current full list.

_previously_seen_exclusive_maps = set()


# ============================================================
# REGULAR MAP ORDER
# ============================================================

MAPS = [
    "Jirachi's Park",
    "Entei's Tower",
    "Kyogre's Temple",
    "Groudon's Palace",
    "Mesprit's Lake",
    "Mewtwo's Cavern",
    "Manaphy's Haven",
    "Eternal Garden",
    "Heatran's Mountain",
    "Spear Pillar",
    "Regigigas' Domain",
    "Deep Mewtwo's Cave",
    "Moon Gaze Mountain",
    "Icebound Cave",
    "Sky Pillar",
    "Mirage Ruins",
    "Latias Heaven",
    "Ruins of Alph",
]


# ============================================================
# DISCOVER EXCLUSIVE MAPS
# ============================================================

def get_exclusive_maps(driver):
    """
    Open the Exclusive Legendary Areas listing and discover
    which exclusive maps are actually available to this account.

    We intentionally do NOT hard-code the map list.

    The page contains entries like:

        <table class="tnav_border maps-listing">
            ...
            <a href="/legendary_areas?area_id=12">
                Great Volcano
            </a>
            ...
        </table>

    Locked/unavailable areas should not appear as usable map
    links, so only actual legendary_areas?area_id= links found
    inside maps-listing tables are returned.

    Returns:

        [
            {
                "name": "Great Volcano",
                "href": "https://eclipserpg.com/legendary_areas?area_id=12"
            },
            ...
        ]
    """

    print()
    print(
        "Checking Exclusive Legendary Areas..."
    )

    try:

        driver.get(
            EXCLUSIVE_AREAS_URL
        )

        wait_for_document_ready(
            driver
        )

        time.sleep(1)

    except Exception as e:

        print(
            "  ✗ Could not open Exclusive "
            f"Legendary Areas: {e}"
        )

        return []

    exclusive_maps = []

    seen_urls = set()

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            links = driver.find_elements(
                By.XPATH,
                "//table[contains("
                "@class,'maps-listing'"
                ")]//a[@href]"
            )

            for link in links:

                try:

                    if not link.is_displayed():
                        continue

                    href = link.get_attribute(
                        "href"
                    )

                    if not href:
                        continue

                    # ------------------------------------------------
                    # Only accept actual legendary area links.
                    #
                    # This excludes:
                    #
                    # /moon_shop?area=legendary_areas
                    # /amount_viewer?pokemon=...
                    # etc.
                    # ------------------------------------------------

                    if "legendary_areas?area_id=" not in href:
                        continue

                    name = link.text.strip()

                    if not name:
                        continue

                    normalized_href = href.lower()

                    if normalized_href in seen_urls:
                        continue

                    seen_urls.add(
                        normalized_href
                    )

                    exclusive_maps.append(
                        {
                            "name": name,
                            "href": href,
                        }
                    )

                except StaleElementReferenceException:

                    continue

            # --------------------------------------------------------
            # Once we've found at least one map, the page has loaded.
            # --------------------------------------------------------

            if exclusive_maps:
                break

        except Exception:

            pass

        time.sleep(0.3)

    # ------------------------------------------------------------
    # Restore original page ordering.
    # ------------------------------------------------------------

    print()

    if exclusive_maps:

        print(
            f"✓ Found {len(exclusive_maps)} "
            "unlocked exclusive map(s)."
        )

        current_names = {
            area["name"] for area in exclusive_maps
        }

        is_first_check = not _previously_seen_exclusive_maps

        newly_unlocked = (
            set()
            if is_first_check
            else current_names - _previously_seen_exclusive_maps
        )

        for area in exclusive_maps:

            if area["name"] in newly_unlocked:

                print(
                    f"  - {area['name']}  ★ NEW"
                )

            else:

                print(
                    f"  - {area['name']}"
                )

        if newly_unlocked:

            print()
            print(
                f"★ {len(newly_unlocked)} newly unlocked "
                "since last check: "
                + ", ".join(sorted(newly_unlocked))
            )

        _previously_seen_exclusive_maps.update(
            current_names
        )

    else:

        print(
            "✓ No exclusive maps are currently unlocked."
        )

    return exclusive_maps


# ============================================================
# WILD POKEMON LISTING / CROSS-MAP SEARCH
# ============================================================
#
# Built from the real HTML of a map's wild-Pokemon listing
# (Manaphy's Haven):
#
#   <div class="wild-pokes">
#     <a href="/amount_viewer?pokemon=Slowpoke"
#        class="tooltip map-wild-poke dexed tooltipstered">
#       <img src="..." alt="Slowpoke" width="35" height="35">
#       <img class="map-wild-dex-icon" src="/favicon.ico">
#     </a>
#     ...
#   </div>
#
# The <img alt="..."> holds the FULL display name, including
# any variant/form prefix (Shiny, Hyper, Crystal, Genesis,
# Astral, Ruby, Rainbow, Pearl, Sapphire, Golden, Emerald,
# Relic, Legacy, Light, Shadow, Silver Star, Star, etc). A
# "dexed" class on the <a> (plus an extra dex-icon <img>) marks
# a species already registered in the Pokedex.
#
# Since the display name already includes variant/form, a
# single substring search over these names covers both
# "search for a Pokemon" and "search for a variant/form" -
# they're the same underlying data.

def get_wild_pokemon(driver):
    """
    Scrape the wild Pokemon listing on the CURRENTLY LOADED map
    page. Returns a list of dicts:

        {
            "name": "Shiny Hyper Totodile",
            "species_param": "HyperTotodile",
            "dexed": True,
        }

    species_param is the site's internal ?pokemon= key (form
    modifiers like Hyper/Genesis, but not color variants like
    Shiny/Crystal/Pearl - those only show up in the display
    name).
    """

    results = []

    try:

        links = driver.find_elements(
            By.CSS_SELECTOR,
            "div.wild-pokes a.map-wild-poke",
        )

    except WebDriverException:

        return results

    for link in links:

        try:

            href = link.get_attribute("href") or ""

            param_match = re.search(
                r"pokemon=([^&]+)",
                href,
            )

            species_param = (
                param_match.group(1)
                if param_match
                else ""
            )

            class_attr = link.get_attribute("class") or ""

            dexed = "dexed" in class_attr.split()

            image = link.find_element(
                By.TAG_NAME,
                "img",
            )

            name = (
                image.get_attribute("alt") or ""
            ).strip()

            if not name:
                continue

            results.append({
                "name": name,
                "species_param": species_param,
                "dexed": dexed,
            })

        except (
            StaleElementReferenceException,
            WebDriverException,
            NoSuchElementException,
        ):

            continue

    return results


def search_pokemon_across_maps(
    driver,
    query,
    progress_callback=None,
):
    """
    Search every known map (regular + unlocked exclusive) for
    wild Pokemon whose display name contains `query`
    (case-insensitive substring match, so "gastly" matches
    "Gastly", "Shiny Gastly", "Crystal Gastly", etc - this
    covers variant/form search too, since the variant is part
    of the display name).

    This visits every map page to build the result, since
    there's no known site-wide search endpoint - it can take a
    while for a large map list.

    progress_callback(map_name, index, total), if given, is
    called right before each map is checked, so a caller can
    show live progress.

    Returns a dict of only the maps with at least one match:

        {
            "Manaphy's Haven": [
                {"name": "Shiny Totodile", ...},
                ...
            ],
        }
    """

    wanted = normalize(query)

    matches_by_map = {}

    exclusive_maps = get_exclusive_maps(driver)

    total = len(MAPS) + len(exclusive_maps)

    index = 0

    for map_name in MAPS:

        index += 1

        if progress_callback:
            progress_callback(map_name, index, total)

        if not open_map(driver, map_name):
            continue

        wild = get_wild_pokemon(driver)

        found = [
            pokemon for pokemon in wild
            if wanted in normalize(pokemon["name"])
        ]

        if found:
            matches_by_map[map_name] = found

    for area in exclusive_maps:

        index += 1

        if progress_callback:
            progress_callback(area["name"], index, total)

        if not open_exclusive_area(driver, area):
            continue

        wild = get_wild_pokemon(driver)

        found = [
            pokemon for pokemon in wild
            if wanted in normalize(pokemon["name"])
        ]

        if found:
            matches_by_map[area["name"]] = found

    return matches_by_map


# ============================================================
# SEARCH BUTTON
# ============================================================

def find_search_button(driver):

    selectors = [

        (
            By.XPATH,
            "//button[normalize-space()='Search']"
        ),

        (
            By.XPATH,
            "//input[@value='Search']"
        ),

        (
            By.XPATH,
            "//*[self::button or self::input]"
            "[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'search')]"
        ),

    ]

    for by, selector in selectors:

        try:

            elements = driver.find_elements(
                by,
                selector
            )

            for element in elements:

                try:

                    if (
                        element.is_displayed()
                        and element.is_enabled()
                    ):

                        return element

                except StaleElementReferenceException:

                    continue

        except Exception:

            continue

    return None


def click_search(driver):

    print(
        "  Clicking Search..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        button = find_search_button(
            driver
        )

        if button is not None:

            try:

                if safe_click(
                    driver,
                    button
                ):

                    print(
                        "  ✓ Search clicked."
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(0.3)

    print(
        "  ✗ Search button not found."
    )

    return False


# ============================================================
# ENCOUNTERED POKEMON TRACKING
# ============================================================
#
# Built from the real HTML of the wild-Pokemon encounter
# announcement:
#
#   <div class="wild-pokemon-message">
#     <div style="display: flex; ...">
#       <font size="3"><b>Shellder</b> Lv. 43</font>
#       <img src=".../gender-male.png">
#       <img src="/favicon.ico" title="Registered in Pokedex">
#     </div>
#     A wild <b>Shellder</b> appeared!
#   </div>
#
# The dex-icon <img> with title="Registered in Pokedex" only
# appears if that species is already dexed (same pattern as the
# map wild-pokes listing). "Rare" here is a best-effort keyword
# match on the same variant/color prefixes seen in the map wild
# listing (Shiny, Crystal, Golden, Rainbow, etc) - the site
# doesn't have an explicit "rare" flag we've seen.

RARE_KEYWORDS = [
    "shiny",
    "crystal",
    "golden",
    "rainbow",
    "astral",
    "genesis",
    "ruby",
    "sapphire",
    "pearl",
    "emerald",
    "relic",
    "legacy",
    "light",
    "shadow",
    "silver star",
    "star",
]

_encountered_pokemon = {
    "total": 0,
    "by_name": {},
    "rare": [],
    "caught": {},
}


def get_encounter_pokemon(driver):
    """
    Scrape the wild Pokemon encounter announcement on the
    currently loaded page, if present. Returns None if there's
    no encounter message (nothing to scrape).

    Returns:

        {
            "name": "Shellder",
            "level": 43,
            "gender": "male",   # "male" / "female" / None
            "dexed": False,
        }
    """

    try:

        container = driver.find_element(
            By.CSS_SELECTOR,
            "div.wild-pokemon-message",
        )

    except (
        NoSuchElementException,
        WebDriverException,
    ):

        return None

    try:

        font = container.find_element(
            By.TAG_NAME,
            "font",
        )

        text = font.text.strip()

    except (
        NoSuchElementException,
        WebDriverException,
    ):

        return None

    name = text
    level = None

    level_match = re.match(
        r"^(.*)\s+Lv\.\s*([\d,]+)$",
        text,
    )

    if level_match:

        name = level_match.group(1).strip()

        level = int(
            level_match.group(2).replace(",", "")
        )

    gender = None
    dexed = False

    try:

        images = container.find_elements(
            By.TAG_NAME,
            "img",
        )

        for image in images:

            src = image.get_attribute("src") or ""
            title = image.get_attribute("title") or ""

            if "gender-male" in src:
                gender = "male"
            elif "gender-female" in src:
                gender = "female"

            if title == "Registered in Pokedex":
                dexed = True

    except WebDriverException:

        pass

    return {
        "name": name,
        "level": level,
        "gender": gender,
        "dexed": dexed,
    }


def is_rare_pokemon(name):
    """
    Best-effort check for whether a Pokemon's display name
    includes one of the known rare/special variant keywords.
    """

    lowered = normalize(name)

    return any(
        keyword in lowered
        for keyword in RARE_KEYWORDS
    )


def get_encountered_pokemon_stats():
    """
    Return a copy of the current session's encountered-Pokemon
    statistics:

        {
            "total": 47,
            "by_name": {"Shellder": 12, "Slowpoke": 8, ...},
            "rare": [
                {"name": "Shiny Goldeen", "level": 22, ...},
                ...
            ],
            "caught": {"Shellder": 10, "Slowpoke": 7, ...},
            "caught_total": 17,
        }

    "caught" is only incremented when capture_encounter()
    actually returned True for that encounter - see
    handle_search_encounter() below.
    """

    return {
        "total": _encountered_pokemon["total"],
        "by_name": dict(_encountered_pokemon["by_name"]),
        "rare": list(_encountered_pokemon["rare"]),
        "caught": dict(
            _encountered_pokemon.get("caught", {})
        ),
        "caught_total": sum(
            _encountered_pokemon.get("caught", {}).values()
        ),
    }


def reset_encountered_pokemon_stats():

    _encountered_pokemon["total"] = 0
    _encountered_pokemon["by_name"] = {}
    _encountered_pokemon["rare"] = []
    _encountered_pokemon["caught"] = {}


def _record_encounter(pokemon):

    if not pokemon:
        return

    name = pokemon["name"]

    _encountered_pokemon["total"] += 1

    _encountered_pokemon["by_name"][name] = (
        _encountered_pokemon["by_name"].get(name, 0) + 1
    )

    if is_rare_pokemon(name):

        _encountered_pokemon["rare"].append(
            pokemon
        )


# ============================================================
# ENCOUNTER FIGHT
# ============================================================

def find_encounter_fight(driver):

    try:

        links = driver.find_elements(
            By.XPATH,
            "//a[contains(@class,'inputsubmit') "
            "and normalize-space()='Fight!']"
        )

        for link in links:

            try:

                href = link.get_attribute(
                    "href"
                )

                if (
                    link.is_displayed()
                    and link.is_enabled()
                    and href
                    and "create_battle" in href
                ):

                    return link

            except StaleElementReferenceException:

                continue

    except Exception:

        pass

    return None


def click_encounter_fight(driver):

    print(
        "  Looking for encounter Fight!..."
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        fight = find_encounter_fight(
            driver
        )

        if fight is not None:

            print(
                "✓ Encounter Fight! found."
            )

            try:

                if safe_click(
                    driver,
                    fight
                ):

                    print(
                        "✓ Encounter Fight! clicked."
                    )

                    wait_for_document_ready(
                        driver
                    )

                    return True

            except (
                StaleElementReferenceException,
                WebDriverException,
            ):

                pass

        time.sleep(0.3)

    return False


# ============================================================
# SEARCH PROGRESS
# ============================================================

def get_search_progress(driver):

    """
    Read the CURRENT MAP's real search progress directly
    from Eclipse RPG.

    The map page contains:

        <td class="tnav map-stat">
            <div id="times-searched">
                <div id="times-searched-number">651</div>/2,500
            </div>
        </td>

    Returns:

        (651, 2500)

    instead of searching the entire page for the first
    number/number combination (which could pick up any
    unrelated x/y pair on the page).
    """

    try:

        # ----------------------------------------------------
        # Current searches completed.
        # ----------------------------------------------------

        current_element = driver.find_element(
            By.ID,
            "times-searched-number"
        )

        current_text = (
            current_element.text
            .strip()
            .replace(",", "")
        )

        if not current_text:

            return (
                None,
                None
            )

        current = int(
            current_text
        )

        # ----------------------------------------------------
        # Find the parent #times-searched element.
        #
        # The maximum is text outside the child div:
        #
        #     <div id="times-searched-number">651</div>/2,500
        # ----------------------------------------------------

        progress_element = driver.find_element(
            By.ID,
            "times-searched"
        )

        progress_text = (
            progress_element.text
            .strip()
        )

        # Example:
        #
        #     651/2,500
        #
        match = re.search(
            r"/\s*([\d,]+)",
            progress_text
        )

        if not match:

            return (
                current,
                None
            )

        maximum = int(
            match.group(1).replace(
                ",",
                ""
            )
        )

        return (
            current,
            maximum
        )

    except (
        NoSuchElementException,
        ValueError,
        WebDriverException,
    ):

        return (
            None,
            None
        )


# ============================================================
# REGULAR MAP OPENING
# ============================================================

def open_map(driver, map_name):

    print()
    print(
        f"Opening map: {map_name}"
    )

    wanted = normalize(
        map_name
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            links = driver.find_elements(
                By.TAG_NAME,
                "a"
            )

            for link in links:

                try:

                    text = normalize(
                        link.text
                    )

                    if (
                        text == wanted
                        and link.is_displayed()
                        and link.is_enabled()
                    ):

                        if safe_click(
                            driver,
                            link
                        ):

                            print(
                                f"  ✓ {map_name} clicked."
                            )

                            wait_for_document_ready(
                                driver
                            )

                            time.sleep(1)

                            print(
                                f"✓ {map_name} loaded."
                            )

                            return True

                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):

                    continue

        except Exception:

            pass

        time.sleep(0.3)

    print(
        f"✗ Map '{map_name}' not found."
    )

    return False


# ============================================================
# EXCLUSIVE MAP OPENING
# ============================================================

def open_exclusive_area(
    driver,
    area
):

    map_name = area["name"]
    href = area["href"]

    print()
    print(
        f"Opening exclusive map: {map_name}"
    )

    print(
        f"  → {href}"
    )

    # --------------------------------------------------------
    # First open the exclusive listing page.
    #
    # This is intentional. We don't simply jump directly to
    # the area URL because you specifically want the bot to
    # click the map link to load the page.
    # --------------------------------------------------------

    try:

        driver.get(
            EXCLUSIVE_AREAS_URL
        )

        wait_for_document_ready(
            driver
        )

        time.sleep(1)

    except Exception as e:

        print(
            "  ✗ Could not open Exclusive "
            f"Legendary Areas: {e}"
        )

        return False

    wanted = normalize(
        map_name
    )

    start = time.time()

    while time.time() - start < WAIT_LONG:

        try:

            links = driver.find_elements(
                By.XPATH,
                "//table[contains("
                "@class,'maps-listing'"
                ")]//a[@href]"
            )

            for link in links:

                try:

                    text = normalize(
                        link.text
                    )

                    if text != wanted:
                        continue

                    current_href = link.get_attribute(
                        "href"
                    )

                    if not current_href:
                        continue

                    if (
                        "legendary_areas?area_id="
                        not in current_href
                    ):
                        continue

                    if not (
                        link.is_displayed()
                        and link.is_enabled()
                    ):
                        continue

                    print(
                        f"  ✓ {map_name} link found."
                    )

                    if not safe_click(
                        driver,
                        link
                    ):

                        print(
                            "  ✗ Could not click "
                            f"{map_name}."
                        )

                        return False

                    print(
                        f"  ✓ {map_name} link clicked."
                    )

                    wait_for_document_ready(
                        driver
                    )

                    time.sleep(1)

                    print(
                        f"✓ {map_name} loaded."
                    )

                    return True

                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):

                    continue

        except Exception:

            pass

        time.sleep(0.3)

    print(
        f"✗ Could not find exclusive map "
        f"'{map_name}'."
    )

    return False


# ============================================================
# HANDLE ENCOUNTER
# ============================================================

def handle_search_encounter(driver):

    encountered = get_encounter_pokemon(
        driver
    )

    if encountered:

        rarity_marker = (
            " ★ RARE"
            if is_rare_pokemon(encountered["name"])
            else ""
        )

        print(
            f"  Wild {encountered['name']} "
            f"Lv. {encountered['level']}"
            f"{rarity_marker}"
        )

        _record_encounter(
            encountered
        )

    if not click_encounter_fight(
        driver
    ):

        print(
            "✗ Could not start encounter."
        )

        return False

    result = capture_encounter(
        driver
    )

    if result:

        print(
            "✓ Encounter capture completed."
        )

        # ----------------------------------------------------
        # Record the actual Pokémon as caught.
        #
        # capture_encounter() only returns True after the
        # Pokémon has actually been captured successfully.
        # ----------------------------------------------------

        if encountered:

            caught = _encountered_pokemon.setdefault(
                "caught",
                {}
            )

            pokemon_name = encountered["name"]

            caught[pokemon_name] = (
                caught.get(pokemon_name, 0) + 1
            )

        return True

    print(
        "✗ Encounter capture failed."
    )

    return False


# ============================================================
# SEARCH SESSION
# ============================================================

def run_searches(
    driver,
    map_name,
    searches,
    is_exclusive=False,
    area=None,
):

    print()
    print(
        f"Starting {searches} searches "
        f"on {map_name}."
    )

    completed = 0

    search_number = 1

    while search_number <= searches:

        current, maximum = get_search_progress(
            driver
        )

        if current is not None:

            print()
            print(
                f"Progress: "
                f"{current}/{maximum}"
            )

        print(
            f"  Search "
            f"{search_number}/{searches}"
        )

        # ----------------------------------------------------
        # ONLY ONE Search click per iteration.
        # ----------------------------------------------------

        if not click_search(
            driver
        ):

            print(
                "✗ Search button disappeared."
            )

            _record_search_session(
                map_name,
                completed
            )

            return False

        time.sleep(
            random.uniform(
                SEARCH_DELAY[0],
                SEARCH_DELAY[1]
            )
        )

        # ----------------------------------------------------
        # Check for Pokémon encounter.
        # ----------------------------------------------------

        fight = find_encounter_fight(
            driver
        )

        if fight is not None:

            print(
                "✓ Pokémon encounter detected."
            )

            if not handle_search_encounter(
                driver
            ):

                print(
                    "✗ Encounter handling failed."
                )

                # ----------------------------------------------------
                # Better encounter recovery: the battle page may
                # have changed unexpectedly (stale element,
                # navigation glitch, etc). Try reopening the
                # current map once before giving up on the whole
                # search session.
                # ----------------------------------------------------

                print(
                    "  Attempting recovery by "
                    "reopening the map..."
                )

                if is_exclusive and area is not None:

                    recovered = open_exclusive_area(
                        driver,
                        area
                    )

                else:

                    recovered = open_map(
                        driver,
                        map_name
                    )

                if not recovered:

                    print(
                        "  ✗ Recovery failed. "
                        "Stopping search session."
                    )

                    _record_search_session(
                        map_name,
                        completed
                    )

                    return False

                print(
                    "  ✓ Recovered - resuming search."
                )

                time.sleep(
                    random.uniform(
                        1.0,
                        1.5
                    )
                )

                search_number += 1

                continue

            time.sleep(
                random.uniform(
                    1.0,
                    1.5
                )
            )

        completed += 1

        search_number += 1

    print()
    print(
        f"✓ Finished {searches} searches "
        f"on {map_name}."
    )

    _record_search_session(
        map_name,
        completed
    )

    return True


# ============================================================
# ASK WHAT TO DO AFTER SEARCHES
# ============================================================

def search_complete_menu(
    driver,
    map_name
):

    while True:

        print()
        print(
            "=" * 60
        )

        print(
            "SEARCHES COMPLETE"
        )

        print(
            "=" * 60
        )

        print()
        print(
            f"Current map: {map_name}"
        )

        encountered_stats = get_encountered_pokemon_stats()

        if encountered_stats["caught_total"] > 0:

            print()
            print(
                "POKEMON CAUGHT"
            )

            print(
                "-" * 60
            )

            for name, count in encountered_stats["caught"].items():

                print(
                    f"{name:<25} x{count}"
                )

            print(
                "-" * 60
            )

            print(
                f"Total caught:      "
                f"{encountered_stats['caught_total']}"
            )

            print(
                f"Total encounters:  "
                f"{encountered_stats['total']}"
            )

            if encountered_stats["total"] > 0:

                rate = (
                    encountered_stats["caught_total"]
                    / encountered_stats["total"]
                    * 100
                )

                print(
                    f"Capture rate:      "
                    f"{rate:.1f}%"
                )

        print()
        print(
            "1. Continue searching this map"
        )

        print(
            "2. Return to main menu"
        )

        choice = input(
            "\nChoose: "
        ).strip()

        if choice == "1":

            return "continue"

        if choice == "2":

            return "menu"

        print(
            "✗ Invalid choice."
        )


# ============================================================
# SEARCH MODE
# ============================================================

def search_mode(driver):

    print()
    print(
        "=" * 60
    )

    print(
        "SEARCH MODE"
    )

    print(
        "=" * 60
    )

    # ========================================================
    # Discover exclusive maps FIRST.
    # ========================================================

    exclusive_maps = get_exclusive_maps(
        driver
    )

    # ========================================================
    # REGULAR MAPS
    # ========================================================

    print()
    print(
        "REGULAR MAPS"
    )

    print(
        "-" * 60
    )

    for i, map_name in enumerate(
        MAPS,
        1
    ):

        print(
            f"{i:2}. {map_name}"
        )

    # ========================================================
    # EXCLUSIVE MAPS
    # ========================================================

    print()
    print(
        "EXCLUSIVE LEGENDARY AREAS"
    )

    print(
        "-" * 60
    )

    if exclusive_maps:

        exclusive_start = (
            len(MAPS) + 1
        )

        for i, area in enumerate(
            exclusive_maps,
            exclusive_start
        ):

            print(
                f"{i:2}. {area['name']}"
            )

    else:

        print(
            "No exclusive maps unlocked."
        )

    # ========================================================
    # TOTAL AVAILABLE MAPS
    # ========================================================

    total_maps = (
        len(MAPS)
        + len(exclusive_maps)
    )

    # ========================================================
    # SELECT MAP
    # ========================================================

    while True:

        choice = input(
            "\nChoose map number "
            f"(1-{total_maps}): "
        ).strip()

        try:

            number = int(
                choice
            )

            if 1 <= number <= total_maps:

                break

        except ValueError:

            pass

        print(
            "✗ Please enter a number from "
            f"1 to {total_maps}."
        )

    # ========================================================
    # REGULAR MAP
    # ========================================================

    if number <= len(MAPS):

        map_index = (
            number - 1
        )

        is_exclusive = False

        area = None

    # ========================================================
    # EXCLUSIVE MAP
    # ========================================================

    else:

        exclusive_index = (
            number
            - len(MAPS)
            - 1
        )

        is_exclusive = True

        area = exclusive_maps[
            exclusive_index
        ]

        map_index = None

    # ========================================================
    # SEARCH LOOP
    # ========================================================

    while True:

        if is_exclusive:

            map_name = area["name"]

            opened = open_exclusive_area(
                driver,
                area
            )

        else:

            map_name = MAPS[
                map_index
            ]

            opened = open_map(
                driver,
                map_name
            )

        if not opened:

            print()
            print(
                "✗ Could not open selected map."
            )

            print(
                "Returning to main menu."
            )

            return

        # ----------------------------------------------------
        # Get current progress.
        # ----------------------------------------------------

        current, maximum = get_search_progress(
            driver
        )

        if current is not None:

            print()
            print(
                f"Current progress: "
                f"{current}/{maximum}"
            )

            remaining = max(
                0,
                maximum - current
            )

            print(
                f"Remaining searches: "
                f"{remaining}"
            )

        else:

            maximum = 500
            remaining = 500

        default_amount = (
            remaining
            if remaining > 0
            else maximum
        )

        # ----------------------------------------------------
        # Ask how many searches.
        # ----------------------------------------------------

        answer = input(
            f"\nHow many searches on "
            f"{map_name}? "
            f"[default {default_amount}]: "
        ).strip()

        if answer:

            try:

                searches = int(
                    answer
                )

            except ValueError:

                print(
                    "✗ Invalid number."
                )

                continue

        else:

            searches = default_amount

        searches = max(
            0,
            searches
        )

        # ----------------------------------------------------
        # Zero searches.
        # ----------------------------------------------------

        if searches == 0:

            print()
            print(
                f"No searches selected for "
                f"{map_name}."
            )

            print(
                "Returning to main menu."
            )

            return

        # ----------------------------------------------------
        # Run searches.
        # ----------------------------------------------------

        if not run_searches(
            driver,
            map_name,
            searches,
            is_exclusive=is_exclusive,
            area=area
        ):

            print()
            print(
                "✗ Search session stopped."
            )

            return

        # ----------------------------------------------------
        # Continue / menu.
        # ----------------------------------------------------

        action = search_complete_menu(
            driver,
            map_name
        )

        if action == "continue":

            continue

        print()
        print(
            "Returning to main menu."
        )

        return


# ============================================================
# PHASE 3 - SPLIT SEARCH FLOWS (Search submenu)
# ============================================================
#
# The functions below give the new Search submenu separate
# "Normal Maps" and "Exclusive Legendary Areas" entries.
#
# They do NOT change any existing behavior - they reuse the
# exact same helper functions (open_map, open_exclusive_area,
# get_search_progress, run_searches, search_complete_menu)
# that search_mode() above already uses. search_mode() itself
# is left completely untouched.
# ============================================================

def _run_search_session(
    driver,
    map_name,
    is_exclusive,
    area=None
):
    """
    Shared search loop for a single already-selected map.

    This is the same loop body that lives inside search_mode()
    above (open map -> check progress -> ask how many -> run
    searches -> ask continue/back), factored out so both the
    Normal Maps and Exclusive Areas submenu entries share
    identical, already-tested behavior instead of duplicating it.
    """

    while True:

        if is_exclusive:

            opened = open_exclusive_area(
                driver,
                area
            )

        else:

            opened = open_map(
                driver,
                map_name
            )

        if not opened:

            print()
            print(
                "✗ Could not open selected map."
            )

            print(
                "Returning to search menu."
            )

            return

        current, maximum = get_search_progress(
            driver
        )

        if current is not None:

            print()
            print(
                f"Current progress: "
                f"{current}/{maximum}"
            )

            remaining = max(
                0,
                maximum - current
            )

            print(
                f"Remaining searches: "
                f"{remaining}"
            )

        else:

            maximum = 500
            remaining = 500

        default_amount = (
            remaining
            if remaining > 0
            else maximum
        )

        answer = input(
            f"\nHow many searches on "
            f"{map_name}? "
            f"[default {default_amount}]: "
        ).strip()

        if answer:

            try:

                searches = int(
                    answer
                )

            except ValueError:

                print(
                    "✗ Invalid number."
                )

                continue

        else:

            searches = default_amount

        searches = max(
            0,
            searches
        )

        if searches == 0:

            print()
            print(
                f"No searches selected for "
                f"{map_name}."
            )

            print(
                "Returning to search menu."
            )

            return

        if not run_searches(
            driver,
            map_name,
            searches,
            is_exclusive=is_exclusive,
            area=area
        ):

            print()
            print(
                "✗ Search session stopped."
            )

            return

        action = search_complete_menu(
            driver,
            map_name
        )

        if action == "continue":

            continue

        print()
        print(
            "Returning to search menu."
        )

        return


def normal_maps_mode(driver):
    """
    Search submenu -> Normal Maps.

    Lists only the regular MAPS list (unchanged), lets the
    user pick one, then runs the same tested search session.
    """

    print()
    print(
        "=" * 60
    )

    print(
        "NORMAL MAPS"
    )

    print(
        "=" * 60
    )

    print()

    for i, map_name in enumerate(
        MAPS,
        1
    ):

        print(
            f"{i:2}. {map_name}"
        )

    back_number = len(MAPS) + 1

    print(
        f"{back_number:2}. Back"
    )

    while True:

        choice = input(
            f"\nChoose map number "
            f"(1-{back_number}): "
        ).strip()

        try:

            number = int(
                choice
            )

        except ValueError:

            print(
                "✗ Please enter a number from "
                f"1 to {back_number}."
            )

            continue

        if number == back_number:
            return

        if 1 <= number <= len(MAPS):
            break

        print(
            "✗ Please enter a number from "
            f"1 to {back_number}."
        )

    map_name = MAPS[
        number - 1
    ]

    _run_search_session(
        driver,
        map_name,
        is_exclusive=False
    )


def exclusive_maps_mode(driver):
    """
    Search submenu -> Exclusive Legendary Areas.

    Dynamically discovers unlocked exclusive maps via
    get_exclusive_maps() (unchanged) rather than a hard-coded
    list. If nothing is unlocked, says so clearly and returns.
    """

    print()
    print(
        "=" * 60
    )

    print(
        "EXCLUSIVE LEGENDARY AREAS"
    )

    print(
        "=" * 60
    )

    exclusive_maps = get_exclusive_maps(
        driver
    )

    if not exclusive_maps:

        print()
        print(
            "No exclusive maps are currently unlocked."
        )

        input(
            "\nPress Enter to return to the search menu..."
        )

        return

    print()

    for i, area in enumerate(
        exclusive_maps,
        1
    ):

        print(
            f"{i:2}. {area['name']}"
        )

    back_number = len(exclusive_maps) + 1

    print(
        f"{back_number:2}. Back"
    )

    while True:

        choice = input(
            f"\nChoose map number "
            f"(1-{back_number}): "
        ).strip()

        try:

            number = int(
                choice
            )

        except ValueError:

            print(
                "✗ Please enter a number from "
                f"1 to {back_number}."
            )

            continue

        if number == back_number:
            return

        if 1 <= number <= len(exclusive_maps):
            break

        print(
            "✗ Please enter a number from "
            f"1 to {back_number}."
        )

    area = exclusive_maps[
        number - 1
    ]

    _run_search_session(
        driver,
        area["name"],
        is_exclusive=True,
        area=area
    )