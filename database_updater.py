import os
import re
import sqlite3
import time
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://eclipserpg.com"

DB_FILE = "eclipse_maps.db"

# Persistent Chrome profile.
# DO NOT use your normal Chrome profile.
# This profile belongs exclusively to this updater.
CHROME_PROFILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "chrome_profile"
    )
)

PAGE_TIMEOUT = 30
WAIT_FOR_POKEMON = 5

# Delay between maps.
# This is deliberately modest so we don't hammer Eclipse.
MAP_DELAY = 1.0

# If True, Selenium will remain open after the updater finishes.
KEEP_BROWSER_OPEN = True


# ============================================================
# MAP CATALOG
#
# info_id is used directly.
#
# These are NOT limited to maps currently unlocked by the
# account. The detailed info pages are what we are collecting.
# ============================================================

MAPS = [

    # --------------------------------------------------------
    # NORMAL LEGENDARY AREAS
    # --------------------------------------------------------

    (1, "Jirachi's Park", "normal"),
    (2, "Entei's Tower", "normal"),
    (3, "Kyogre's Temple", "normal"),
    (4, "Groudon's Palace", "normal"),
    (5, "Mesprit's Lake", "normal"),
    (6, "Mewtwo's Cavern", "normal"),
    (7, "Manaphy's Haven", "normal"),
    (8, "Eternal Garden", "normal"),
    (9, "Heatran's Mountain", "normal"),
    (10, "Spear Pillar", "normal"),
    (11, "Regigigas' Domain", "normal"),

    (21, "Deep Mewtwo's Cave", "normal"),
    (25, "Moon Gaze Mountain", "normal"),
    (26, "Icebound Cave", "normal"),
    (27, "Sky Pillar", "normal"),
    (28, "Mirage Ruins", "normal"),
    (29, "Latias Heaven", "normal"),
    (44, "Ruins of Alph", "normal"),

    # --------------------------------------------------------
    # EXCLUSIVE AREAS
    # --------------------------------------------------------

    (12, "Great Volcano", "exclusive"),
    (13, "Distortion World", "exclusive"),
    (14, "Enigma Island", "exclusive"),
    (17, "Newmoon Island", "exclusive"),
    (22, "Burned Tower", "exclusive"),
    (23, "Pokemon Mansion", "exclusive"),
]


# ============================================================
# DATABASE
# ============================================================

def connect_db():

    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "PRAGMA journal_mode=WAL"
    )

    conn.execute(
        "PRAGMA foreign_keys=ON"
    )

    return conn


def create_database():

    conn = connect_db()

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS maps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            area_id INTEGER NOT NULL UNIQUE,

            info_id INTEGER,

            name TEXT NOT NULL,

            map_type TEXT NOT NULL,

            unlocked INTEGER NOT NULL DEFAULT 0,

            info_url TEXT,

            last_updated TEXT
        );


        CREATE TABLE IF NOT EXISTS pokemon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            map_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            species_param TEXT,

            dexed INTEGER NOT NULL DEFAULT 0,

            icon_name TEXT,

            FOREIGN KEY(map_id)
                REFERENCES maps(id)
                ON DELETE CASCADE,

            UNIQUE(
                map_id,
                name,
                species_param
            )
        );


        CREATE INDEX IF NOT EXISTS idx_pokemon_name
        ON pokemon(name);


        CREATE INDEX IF NOT EXISTS idx_pokemon_species
        ON pokemon(species_param);


        CREATE INDEX IF NOT EXISTS idx_pokemon_map
        ON pokemon(map_id);


        CREATE INDEX IF NOT EXISTS idx_maps_area
        ON maps(area_id);


        CREATE INDEX IF NOT EXISTS idx_maps_info
        ON maps(info_id);
        """
    )

    conn.commit()
    conn.close()


# ============================================================
# CHROME / SELENIUM
# ============================================================

def create_driver():

    print()
    print("Starting Chrome...")
    print()
    print(
        f"Chrome profile:"
    )
    print(
        f"  {CHROME_PROFILE}"
    )
    print()

    os.makedirs(
        CHROME_PROFILE,
        exist_ok=True
    )

    options = Options()

    # Persistent profile.
    options.add_argument(
        f"--user-data-dir={CHROME_PROFILE}"
    )

    # Normal browser window.
    options.add_argument(
        "--start-maximized"
    )

    # Make Selenium look less like a blank automated browser.
    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_argument(
        "--disable-notifications"
    )

    options.add_argument(
        "--disable-popup-blocking"
    )

    options.add_argument(
        "--no-first-run"
    )

    options.add_argument(
        "--no-default-browser-check"
    )

    # Selenium Manager handles ChromeDriver.
    try:

        driver = webdriver.Chrome(
            options=options
        )

    except WebDriverException as exc:

        print()
        print(
            "ERROR: Chrome could not be started."
        )
        print()
        print(exc)
        print()

        raise

    driver.set_page_load_timeout(
        PAGE_TIMEOUT
    )

    return driver


# ============================================================
# PAGE HELPERS
# ============================================================

def get_current_url(driver):

    try:
        return driver.current_url

    except WebDriverException:
        return ""


def is_login_page(driver):

    url = get_current_url(
        driver
    ).lower()

    if "/login" in url:
        return True

    try:

        html = driver.page_source.lower()

    except WebDriverException:

        return False

    # These are intentionally broad checks.
    # We primarily rely on the URL.
    if (
        'name="password"' in html
        and 'name="username"' in html
    ):
        return True

    if (
        'name="password"' in html
        and "login" in html
    ):
        return True

    return False


def wait_for_page(driver):

    try:

        WebDriverWait(
            driver,
            PAGE_TIMEOUT
        ).until(
            lambda d:
                d.execute_script(
                    "return document.readyState"
                )
                in (
                    "interactive",
                    "complete"
                )
        )

    except TimeoutException:

        print(
            "  ! Page load wait timed out."
        )


def get_page_html(driver, url):

    print(
        f"  Loading: {url}"
    )

    try:

        driver.get(url)

    except TimeoutException:

        print(
            "  ! Page load timed out; "
            "checking page anyway."
        )

    except WebDriverException as exc:

        print(
            f"  ✗ Browser error: {exc}"
        )

        return None

    wait_for_page(
        driver
    )

    current_url = get_current_url(
        driver
    )

    print(
        f"  Current URL: {current_url}"
    )

    if is_login_page(
        driver
    ):

        print()
        print(
            "  ! Eclipse redirected to LOGIN."
        )
        print(
            "  ! Please log into Eclipse in "
            "the Chrome window."
        )
        print()

        return None

    # Give the page a moment to finish any
    # client-side rendering.
    time.sleep(
        WAIT_FOR_POKEMON
    )

    try:

        html = driver.page_source

    except WebDriverException as exc:

        print(
            f"  ✗ Could not read page: {exc}"
        )

        return None

    return html


# ============================================================
# AUTHENTICATION
# ============================================================

def ensure_logged_in(driver):

    print()
    print(
        "Checking Eclipse login..."
    )

    try:

        driver.get(
            BASE_URL
        )

    except TimeoutException:

        pass

    except WebDriverException as exc:

        print(
            f"Could not open Eclipse: {exc}"
        )

        return False

    wait_for_page(
        driver
    )

    if not is_login_page(
        driver
    ):

        print(
            "✓ Existing Eclipse session detected."
        )

        return True

    print()
    print("=" * 60)
    print("ECLIPSE LOGIN REQUIRED")
    print("=" * 60)
    print()
    print(
        "Chrome is using the updater's persistent"
    )
    print(
        "profile:"
    )
    print()
    print(
        CHROME_PROFILE
    )
    print()
    print(
        "Log into Eclipse in the Chrome window."
    )
    print(
        "You only need to do this the first time"
    )
    print(
        "unless Eclipse expires the session."
    )
    print()
    print(
        "When you are completely logged in,"
    )
    print(
        "return here and press ENTER."
    )
    print()

    input(
        "Press ENTER after logging in..."
    )

    # Verify login again.
    try:

        driver.get(
            BASE_URL
        )

    except TimeoutException:

        pass

    wait_for_page(
        driver
    )

    if is_login_page(
        driver
    ):

        print()
        print(
            "✗ Eclipse still appears to be logged out."
        )
        print()

        return False

    print(
        "✓ Eclipse login detected."
    )

    return True


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value):

    if not value:
        return ""

    value = str(
        value
    ).strip().lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "",
        value
    )

    return value


# ============================================================
# PARSE WILD POKEMON
# ============================================================

def parse_wild_pokemon(html):

    if not html:
        return []

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # This is the exact structure from the HTML
    # you supplied:
    #
    # <div class="wild-pokes">
    #   <a class="map-wild-poke ...">
    #       <img ... alt="Glalie">
    #   </a>
    # </div>

    containers = soup.select(
        "div.wild-pokes"
    )

    if not containers:

        return []

    results = []

    for container in containers:

        links = container.select(
            "a.map-wild-poke"
        )

        for link in links:

            href = (
                link.get("href")
                or ""
            )

            # ------------------------------------------------
            # Pokemon parameter
            # ------------------------------------------------

            species_param = ""

            match = re.search(
                r"[?&]pokemon=([^&]+)",
                href,
                re.IGNORECASE
            )

            if match:

                species_param = (
                    match.group(1)
                    .strip()
                )

            # ------------------------------------------------
            # Pokemon image
            # ------------------------------------------------

            image = link.find(
                "img",
                alt=True
            )

            if image is None:

                continue

            name = (
                image.get("alt")
                or ""
            ).strip()

            if not name:

                continue

            # ------------------------------------------------
            # Icon filename
            # ------------------------------------------------

            icon_src = (
                image.get("src")
                or ""
            )

            icon_name = ""

            if icon_src:

                icon_name = (
                    icon_src
                    .rsplit(
                        "/",
                        1
                    )[-1]
                )

                icon_name = (
                    icon_name
                    .split(
                        "?",
                        1
                    )[0]
                )

            # ------------------------------------------------
            # Dexed
            # ------------------------------------------------

            classes = (
                link.get("class")
                or []
            )

            dexed = (
                "dexed"
                in classes
            )

            results.append(
                {
                    "name": name,
                    "species_param":
                        species_param,
                    "dexed": dexed,
                    "icon_name":
                        icon_name,
                }
            )

    # --------------------------------------------------------
    # Deduplicate
    #
    # IMPORTANT:
    # We DO NOT deduplicate solely by species_param.
    #
    # Eclipse can have:
    #
    # pokemon=Baltoy
    # alt="Baltoy"
    #
    # and
    #
    # pokemon=Baltoy
    # alt="Shiny Baltoy"
    #
    # Those are different displayed Pokemon.
    # --------------------------------------------------------

    unique = []

    seen = set()

    for pokemon in results:

        key = (
            normalize(
                pokemon["name"]
            ),
            normalize(
                pokemon["species_param"]
            ),
            normalize(
                pokemon["icon_name"]
            ),
        )

        if key in seen:

            continue

        seen.add(
            key
        )

        unique.append(
            pokemon
        )

    return unique


# ============================================================
# MAP DATABASE OPERATIONS
# ============================================================

def upsert_map(
    conn,
    area_id,
    name,
    map_type,
    info_id,
    info_url,
    unlocked=0
):

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    conn.execute(
        """
        INSERT INTO maps (
            area_id,
            info_id,
            name,
            map_type,
            unlocked,
            info_url,
            last_updated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(area_id)
        DO UPDATE SET
            info_id = excluded.info_id,
            name = excluded.name,
            map_type = excluded.map_type,
            info_url = excluded.info_url,
            last_updated = excluded.last_updated
        """,
        (
            area_id,
            info_id,
            name,
            map_type,
            unlocked,
            info_url,
            now,
        )
    )

    conn.commit()


def get_existing_pokemon_count(
    conn,
    area_id
):

    row = conn.execute(
        """
        SELECT COUNT(*)
        FROM pokemon p
        JOIN maps m
            ON p.map_id = m.id
        WHERE m.area_id = ?
        """,
        (area_id,)
    ).fetchone()

    if row is None:

        return 0

    return row[0]


def save_pokemon(
    conn,
    area_id,
    pokemon_list
):

    row = conn.execute(
        """
        SELECT id
        FROM maps
        WHERE area_id = ?
        """,
        (area_id,)
    ).fetchone()

    if row is None:

        return

    map_id = row[0]

    # We only replace the list when we actually
    # received Pokemon data.
    #
    # This prevents a login failure, timeout,
    # Cloudflare page, etc. from destroying
    # previously collected data.

    conn.execute(
        """
        DELETE FROM pokemon
        WHERE map_id = ?
        """,
        (map_id,)
    )

    for pokemon in pokemon_list:

        conn.execute(
            """
            INSERT OR IGNORE INTO pokemon (
                map_id,
                name,
                species_param,
                dexed,
                icon_name
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                map_id,

                pokemon[
                    "name"
                ],

                pokemon[
                    "species_param"
                ],

                int(
                    pokemon[
                        "dexed"
                    ]
                ),

                pokemon[
                    "icon_name"
                ],
            )
        )

    conn.commit()


# ============================================================
# UPDATE ONE MAP
# ============================================================

def update_map(
    driver,
    conn,
    area_id,
    name,
    map_type
):

    print()
    print(
        "-" * 60
    )

    print(
        f"[{area_id}] {name}"
    )

    print(
        f"Type: {map_type}"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # We go DIRECTLY to info_id.
    #
    # We do NOT visit area_id first.
    # --------------------------------------------------------

    info_url = (
        f"{BASE_URL}"
        f"/legendary_areas"
        f"?info_id={area_id}"
    )

    print(
        f"Info: {info_url}"
    )

    html = get_page_html(
        driver,
        info_url
    )

    if not html:

        existing = (
            get_existing_pokemon_count(
                conn,
                area_id
            )
        )

        print(
            "  ! Could not retrieve map."
        )

        print(
            f"  Existing database entries: "
            f"{existing}"
        )

        print(
            "  Existing data preserved."
        )

        return False

    # --------------------------------------------------------
    # Check that we actually received the
    # expected Eclipse page.
    # --------------------------------------------------------

    lower_html = html.lower()

    if (
        "wild-pokes" not in lower_html
    ):

        existing = (
            get_existing_pokemon_count(
                conn,
                area_id
            )
        )

        print(
            "  ! No wild-pokes container detected."
        )

        print(
            f"  Existing database entries: "
            f"{existing}"
        )

        print(
            "  Existing data preserved."
        )

        # Save the map itself, but don't
        # destroy its existing Pokemon data.
        upsert_map(
            conn,
            area_id,
            name,
            map_type,
            info_id=area_id,
            info_url=info_url,
            unlocked=0
        )

        return False

    pokemon = parse_wild_pokemon(
        html
    )

    print(
        f"  Pokémon found: "
        f"{len(pokemon)}"
    )

    if not pokemon:

        existing = (
            get_existing_pokemon_count(
                conn,
                area_id
            )
        )

        print(
            "  ! No wild Pokémon detected."
        )

        print(
            f"  Existing database entries: "
            f"{existing}"
        )

        print(
            "  Existing data preserved."
        )

        return False

    # --------------------------------------------------------
    # Print a quick sample.
    # --------------------------------------------------------

    print()

    for pokemon in pokemon[:10]:

        dex_status = (
            "DEXED"
            if pokemon["dexed"]
            else "undexed"
        )

        print(
            f"    {pokemon['name']}"
            f" [{dex_status}]"
            f" -> {pokemon['species_param']}"
        )

    if len(pokemon) > 10:

        print(
            f"    ... and "
            f"{len(pokemon) - 10} more"
        )

    # --------------------------------------------------------
    # Save map.
    # --------------------------------------------------------

    upsert_map(
        conn,
        area_id,
        name,
        map_type,
        info_id=area_id,
        info_url=info_url,
        unlocked=0
    )

    # --------------------------------------------------------
    # Save Pokemon.
    # --------------------------------------------------------

    save_pokemon(
        conn,
        area_id,
        pokemon
    )

    print()
    print(
        "  ✓ Database updated."
    )

    return True


# ============================================================
# DATABASE SUMMARY
# ============================================================

def print_database_summary():

    conn = connect_db()

    try:

        map_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM maps
            """
        ).fetchone()[0]

        pokemon_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM pokemon
            """
        ).fetchone()[0]

        print()
        print(
            "=" * 60
        )

        print(
            "DATABASE SUMMARY"
        )

        print(
            "=" * 60
        )

        print(
            f"Maps:    {map_count}"
        )

        print(
            f"Pokemon: {pokemon_count}"
        )

        print()

        rows = conn.execute(
            """
            SELECT
                m.area_id,
                m.name,
                m.map_type,
                COUNT(p.id)
            FROM maps m
            LEFT JOIN pokemon p
                ON p.map_id = m.id
            GROUP BY
                m.id
            ORDER BY
                m.area_id
            """
        ).fetchall()

        for (
            area_id,
            name,
            map_type,
            count
        ) in rows:

            print(
                f"{area_id:>3} | "
                f"{name:<25} | "
                f"{map_type:<9} | "
                f"{count} Pokemon"
            )

    finally:

        conn.close()


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "ECLIPSE MAP DATABASE UPDATER"
    )

    print(
        "=" * 60
    )

    print()

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    create_database()

    # --------------------------------------------------------
    # Chrome
    # --------------------------------------------------------

    driver = None

    conn = connect_db()

    successful = 0
    failed = 0

    try:

        driver = create_driver()

        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        if not ensure_logged_in(
            driver
        ):

            print()
            print(
                "Authentication was not confirmed."
            )
            print(
                "Nothing was changed."
            )

            return

        # ----------------------------------------------------
        # Update all maps
        # ----------------------------------------------------

        total = len(
            MAPS
        )

        print()
        print(
            "=" * 60
        )

        print(
            f"UPDATING {total} MAPS"
        )

        print(
            "=" * 60
        )

        for index, (
            area_id,
            name,
            map_type
        ) in enumerate(
            MAPS,
            1
        ):

            print()
            print(
                f"========== "
                f"{index}/{total} "
                f"=========="
            )

            try:

                success = update_map(
                    driver,
                    conn,
                    area_id,
                    name,
                    map_type
                )

                if success:

                    successful += 1

                else:

                    failed += 1

            except KeyboardInterrupt:

                print()
                print(
                    "Interrupted by user."
                )

                print(
                    "Already collected data "
                    "has been saved."
                )

                break

            except Exception as exc:

                failed += 1

                print()
                print(
                    f"  ✗ ERROR: {exc}"
                )

                print(
                    "  Existing database data "
                    "was not intentionally removed."
                )

            # Don't hammer Eclipse.
            time.sleep(
                MAP_DELAY
            )

    finally:

        conn.close()

        if driver is not None:

            if KEEP_BROWSER_OPEN:

                print()
                print(
                    "Chrome is being left open."
                )

                print(
                    "You can close it manually."
                )

                print()

            else:

                try:
                    driver.quit()

                except Exception:
                    pass

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "UPDATE COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed:     {failed}"
    )

    print()

    print(
        f"Database: {DB_FILE}"
    )

    print(
        f"Chrome profile: {CHROME_PROFILE}"
    )

    print_database_summary()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()