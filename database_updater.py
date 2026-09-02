import os
import re
import sqlite3
import time
from datetime import datetime
from urllib.parse import urljoin, unquote

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

# Persistent Chrome profile used ONLY by this updater.
#
# This allows the Eclipse login session/cookies to survive
# between runs.
CHROME_PROFILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "chrome_profile"
    )
)

# Selenium page timeout.
PAGE_TIMEOUT = 30

# How long to wait for the wild-pokes section to appear.
POKEMON_WAIT_TIMEOUT = 15

# Small delay after page loading.
PAGE_SETTLE_DELAY = 0.5

# Delay between maps.
MAP_DELAY = 1.0

# Number of attempts for a map if the page fails.
MAX_MAP_ATTEMPTS = 3

# Keep Chrome open after completion.
KEEP_BROWSER_OPEN = True

# Debug HTML is saved here if a page unexpectedly contains
# no wild Pokemon.
DEBUG_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "debug_pages"
    )
)


# ============================================================
# MAP CATALOG
#
# IMPORTANT:
#
# The detailed map information is accessed directly with:
#
#     ?info_id=<ID>
#
# We do NOT use:
#
#     ?area_id=<ID>
#
# to obtain the Pokemon list.
#
# The area_id and info_id happen to correspond for these
# currently known maps, but they are treated as separate
# concepts in the database.
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


def table_columns(conn, table_name):
    """
    Return the existing column names for a table.
    """

    rows = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return {
        row[1]
        for row in rows
    }


def migrate_database(conn):
    """
    Safely upgrade an older eclipse_maps.db.

    This is important because earlier versions of the updater
    created the database before info_id existed.
    """

    maps_columns = table_columns(
        conn,
        "maps"
    )

    if maps_columns:

        if "info_id" not in maps_columns:

            print(
                "  Migrating database: adding maps.info_id..."
            )

            conn.execute(
                """
                ALTER TABLE maps
                ADD COLUMN info_id INTEGER
                """
            )

        if "info_url" not in maps_columns:

            print(
                "  Migrating database: adding maps.info_url..."
            )

            conn.execute(
                """
                ALTER TABLE maps
                ADD COLUMN info_url TEXT
                """
            )

        if "unlocked" not in maps_columns:

            print(
                "  Migrating database: adding maps.unlocked..."
            )

            conn.execute(
                """
                ALTER TABLE maps
                ADD COLUMN unlocked INTEGER NOT NULL
                DEFAULT 0
                """
            )

        if "last_updated" not in maps_columns:

            print(
                "  Migrating database: adding maps.last_updated..."
            )

            conn.execute(
                """
                ALTER TABLE maps
                ADD COLUMN last_updated TEXT
                """
            )

    pokemon_columns = table_columns(
        conn,
        "pokemon"
    )

    if pokemon_columns:

        if "species_param" not in pokemon_columns:

            print(
                "  Migrating database: adding "
                "pokemon.species_param..."
            )

            conn.execute(
                """
                ALTER TABLE pokemon
                ADD COLUMN species_param TEXT
                """
            )

        if "dexed" not in pokemon_columns:

            print(
                "  Migrating database: adding "
                "pokemon.dexed..."
            )

            conn.execute(
                """
                ALTER TABLE pokemon
                ADD COLUMN dexed INTEGER NOT NULL
                DEFAULT 0
                """
            )

        if "icon_name" not in pokemon_columns:

            print(
                "  Migrating database: adding "
                "pokemon.icon_name..."
            )

            conn.execute(
                """
                ALTER TABLE pokemon
                ADD COLUMN icon_name TEXT
                """
            )

    conn.commit()


def create_database():
    """
    Create the database if necessary and migrate older versions.
    """

    conn = connect_db()

    try:

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

        # Upgrade an existing database created by an older
        # version of the updater.
        migrate_database(conn)

        # Indexes may have failed to exist on very old schemas
        # before migration, so create them again afterward.
        conn.executescript(
            """
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

    finally:

        conn.close()


# ============================================================
# CHROME / SELENIUM
# ============================================================

def create_driver():

    print()
    print(
        "Starting Chrome..."
    )
    print()

    print(
        "Persistent Chrome profile:"
    )

    print(
        f"  {CHROME_PROFILE}"
    )

    print()

    os.makedirs(
        CHROME_PROFILE,
        exist_ok=True
    )

    os.makedirs(
        DEBUG_DIR,
        exist_ok=True
    )

    options = Options()

    # Persistent Selenium Chrome profile.
    options.add_argument(
        f"--user-data-dir={CHROME_PROFILE}"
    )

    options.add_argument(
        "--start-maximized"
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

    # This prevents Chrome from restoring an old tab set.
    options.add_argument(
        "--disable-session-crashed-bubble"
    )

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
# SELENIUM PAGE HELPERS
# ============================================================

def get_current_url(driver):

    try:

        return driver.current_url

    except WebDriverException:

        return ""


def get_page_source(driver):

    try:

        return driver.page_source

    except WebDriverException as exc:

        print(
            f"  ✗ Could not read page source: {exc}"
        )

        return None


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


def is_login_page(driver):

    url = get_current_url(
        driver
    ).lower()

    if "/login" in url:

        return True

    html = get_page_source(
        driver
    )

    if not html:

        return False

    html_lower = html.lower()

    # Broad checks. URL is the primary check.
    if (
        'name="password"' in html_lower
        and 'name="username"' in html_lower
    ):

        return True

    if (
        'name="password"' in html_lower
        and "login" in html_lower
    ):

        return True

    return False


def wait_for_wild_pokemon(driver):

    """
    Wait for the actual wild Pokemon container.

    This is more reliable than simply waiting for
    document.readyState.

    Eclipse's page contains:

        <div class="wild-pokes">
            <a class="map-wild-poke ...">
                ...
            </a>
        </div>
    """

    try:

        WebDriverWait(
            driver,
            POKEMON_WAIT_TIMEOUT
        ).until(
            lambda d:
                len(
                    d.find_elements(
                        "css selector",
                        "div.wild-pokes "
                        "a.map-wild-poke"
                    )
                ) > 0
        )

        return True

    except TimeoutException:

        return False


def load_page(driver, url):

    print(
        f"  Loading: {url}"
    )

    try:

        driver.get(
            url
        )

    except TimeoutException:

        print(
            "  ! Browser page-load timeout; "
            "checking the page anyway."
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

        print(
            "  ! Eclipse redirected to LOGIN."
        )

        return None

    time.sleep(
        PAGE_SETTLE_DELAY
    )

    return get_page_source(
        driver
    )


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
    print(
        "=" * 60
    )
    print(
        "ECLIPSE LOGIN REQUIRED"
    )
    print(
        "=" * 60
    )
    print()

    print(
        "Chrome is using this persistent profile:"
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
        "Take as long as you need."
    )

    print()

    print(
        "When you are completely logged in,"
    )

    print(
        "return to this terminal and press ENTER."
    )

    print()

    input(
        "Press ENTER after logging in..."
    )

    print()
    print(
        "Verifying Eclipse login..."
    )

    try:

        driver.get(
            BASE_URL
        )

    except TimeoutException:

        pass

    except WebDriverException as exc:

        print(
            f"Could not verify login: {exc}"
        )

        return False

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
# POKEMON PARSER
# ============================================================

def parse_wild_pokemon(html):

    if not html:

        return []

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Exact Eclipse structure:
    #
    # <div class="wild-pokes">
    #
    #     <a
    #         class="tooltip map-wild-poke dexed ..."
    #         href="/amount_viewer?pokemon=Glalie"
    #     >
    #
    #         <img
    #             src="/images/icons/Glalie.png?15089"
    #             alt="Glalie"
    #         >
    #
    #     </a>
    #
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

            # ------------------------------------------------
            # Pokemon URL
            # ------------------------------------------------

            href = (
                link.get("href")
                or ""
            )

            species_param = ""

            match = re.search(
                r"[?&]pokemon=([^&]+)",
                href,
                re.IGNORECASE
            )

            if match:

                species_param = unquote(
                    match.group(1)
                ).strip()

            # ------------------------------------------------
            # Pokemon image
            # ------------------------------------------------

            images = link.find_all(
                "img",
                alt=True
            )

            if not images:

                continue

            # The first image is the Pokemon sprite.
            #
            # A second image may be the dexed favicon.
            image = images[0]

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
                    "species_param": species_param,
                    "dexed": dexed,
                    "icon_name": icon_name,
                }
            )

    # --------------------------------------------------------
    # Deduplicate
    #
    # IMPORTANT:
    #
    # species_param alone is NOT enough.
    #
    # Example:
    #
    #   Baltoy
    #   Shiny Baltoy
    #
    # can both use:
    #
    #   pokemon=Baltoy
    #
    # but they are different entries.
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
# DATABASE MAP FUNCTIONS
# ============================================================

def get_existing_pokemon_count(
    conn,
    area_id
):

    row = conn.execute(
        """
        SELECT COUNT(*)
        FROM pokemon p
        INNER JOIN maps m
            ON p.map_id = m.id
        WHERE m.area_id = ?
        """,
        (area_id,)
    ).fetchone()

    if row is None:

        return 0

    return row[0]


def upsert_map(
    conn,
    area_id,
    name,
    map_type,
    info_id,
    info_url
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

            info_id =
                excluded.info_id,

            name =
                excluded.name,

            map_type =
                excluded.map_type,

            info_url =
                excluded.info_url,

            last_updated =
                excluded.last_updated
        """,
        (
            area_id,
            info_id,
            name,
            map_type,
            0,
            info_url,
            now,
        )
    )

    conn.commit()


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

    # Only replace Pokemon data when we actually received
    # a valid list.
    #
    # This protects the database if Eclipse temporarily
    # returns an incomplete page.

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
                pokemon["name"],
                pokemon["species_param"],
                int(
                    pokemon["dexed"]
                ),
                pokemon["icon_name"],
            )
        )

    conn.commit()


# ============================================================
# DEBUG
# ============================================================

def save_debug_html(
    area_id,
    html,
    attempt
):

    if not html:

        return

    os.makedirs(
        DEBUG_DIR,
        exist_ok=True
    )

    filename = (
        f"info_{area_id}"
        f"_attempt_{attempt}.html"
    )

    path = os.path.join(
        DEBUG_DIR,
        filename
    )

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                html
            )

        print(
            f"  Debug HTML saved: {path}"
        )

    except OSError as exc:

        print(
            f"  ! Could not save debug HTML: {exc}"
        )


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
        f"[{area_id}] {name}"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # We go DIRECTLY to info_id.
    #
    # We do NOT first visit:
    #
    #   ?area_id=<id>
    #
    # This is what allows the updater to retrieve detailed
    # Pokemon information without requiring the map to be
    # unlocked in the normal map interface.
    # --------------------------------------------------------

    info_url = (
        f"{BASE_URL}/legendary_areas"
        f"?info_id={area_id}"
    )

    print(
        f"  Info: {info_url}"
    )

    existing_count = get_existing_pokemon_count(
        conn,
        area_id
    )

    for attempt in range(
        1,
        MAX_MAP_ATTEMPTS + 1
    ):

        if attempt > 1:

            print(
                f"  Retry {attempt}/"
                f"{MAX_MAP_ATTEMPTS}..."
            )

            time.sleep(
                2
            )

        html = load_page(
            driver,
            info_url
        )

        if html is None:

            print(
                "  ! Could not retrieve page."
            )

            continue

        # ----------------------------------------------------
        # Check for login redirect.
        # ----------------------------------------------------

        if is_login_page(
            driver
        ):

            print(
                "  ! Session expired."
            )

            return False

        # ----------------------------------------------------
        # Wait specifically for the wild Pokemon section.
        # ----------------------------------------------------

        found_container = wait_for_wild_pokemon(
            driver
        )

        if found_container:

            # Get the newest DOM after waiting.
            html = get_page_source(
                driver
            )

        # ----------------------------------------------------
        # Parse Pokemon.
        # ----------------------------------------------------

        pokemon = parse_wild_pokemon(
            html
        )

        print(
            f"  Pokémon found: "
            f"{len(pokemon)}"
        )

        # ----------------------------------------------------
        # Successful result.
        # ----------------------------------------------------

        if pokemon:

            upsert_map(
                conn,
                area_id,
                name,
                map_type,
                info_id=area_id,
                info_url=info_url
            )

            save_pokemon(
                conn,
                area_id,
                pokemon
            )

            print(
                "  ✓ Database updated."
            )

            return True

        # ----------------------------------------------------
        # No Pokemon.
        #
        # NEVER wipe existing data here.
        # ----------------------------------------------------

        print(
            "  ! No wild Pokémon detected."
        )

        print(
            f"  Existing database entries: "
            f"{existing_count}"
        )

        if existing_count:

            print(
                "  Existing data preserved."
            )

        # Save HTML so we can inspect exactly what Eclipse
        # returned if the parser misses something.
        save_debug_html(
            area_id,
            html,
            attempt
        )

    # --------------------------------------------------------
    # All attempts failed.
    # --------------------------------------------------------

    print(
        "  ✗ Failed to obtain wild Pokémon "
        "data after all attempts."
    )

    return False


# ============================================================
# DATABASE SUMMARY
# ============================================================

def print_database_summary(conn):

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

    print(
        f"Maps:     {map_count}"
    )

    print(
        f"Pokémon:  {pokemon_count}"
    )

    print()


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

    try:

        create_database()

    except sqlite3.Error as exc:

        print(
            "✗ Database initialization failed:"
        )

        print(
            exc
        )

        return

    print(
        f"Database: {DB_FILE}"
    )

    print()

    # --------------------------------------------------------
    # Selenium
    # --------------------------------------------------------

    driver = None

    try:

        driver = create_driver()

        # ----------------------------------------------------
        # Login
        # ----------------------------------------------------

        if not ensure_logged_in(
            driver
        ):

            print()
            print(
                "Updater stopped because Eclipse login "
                "could not be verified."
            )

            return

        # ----------------------------------------------------
        # Open database
        # ----------------------------------------------------

        conn = connect_db()

        successful = 0
        failed = 0

        try:

            total = len(
                MAPS
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
                    "=" * 60
                )

                print(
                    f"========== "
                    f"{index}/{total} "
                    f"=========="
                )

                print(
                    "=" * 60
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
                        "Updater interrupted by user."
                    )

                    raise

                except Exception as exc:

                    failed += 1

                    print(
                        f"  ✗ ERROR: {exc}"
                    )

                # Delay between maps.
                #
                # Don't sleep after the final map.
                if index < total:

                    time.sleep(
                        MAP_DELAY
                    )

            # ------------------------------------------------
            # Summary
            # ------------------------------------------------

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

            print_database_summary(
                conn
            )

            print(
                f"Database: {DB_FILE}"
            )

            print(
                f"Debug HTML: {DEBUG_DIR}"
            )

        finally:

            conn.close()

    except KeyboardInterrupt:

        print()
        print()
        print(
            "Updater stopped."
        )

    finally:

        if driver is not None:

            if KEEP_BROWSER_OPEN:

                print()
                print(
                    "Chrome is being kept open."
                )

                print(
                    "You can close it manually."
                )

                print()

                try:

                    input(
                        "Press ENTER to close Chrome..."
                    )

                except (
                    EOFError,
                    KeyboardInterrupt
                ):

                    pass

            try:

                driver.quit()

            except WebDriverException:

                pass


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()