"""
Update the Eclipse RPG map database.

This script is intended to be imported by search.py
or run independently after creating a Selenium driver.

The basic process is:

    map page
        ↓
    find "Detailed map info"
        ↓
    obtain detail URL
        ↓
    request detail page directly
        ↓
    parse .wild-pokes
        ↓
    save Pokémon to SQLite

Once the detail URLs are known, future updates can
skip the map clicking process entirely.
"""

import re
from datetime import datetime

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from map_database import (
    initialize_database,
    upsert_map,
    replace_map_pokemon,
)


def timestamp():
    """Return a database-friendly timestamp."""
    return datetime.now().isoformat(
        timespec="seconds"
    )


def absolute_url(driver, href):
    """Convert a relative URL into an absolute URL."""
    if not href:
        return ""

    href = href.strip()

    if href.startswith("http://"):
        return href

    if href.startswith("https://"):
        return href

    current = driver.current_url

    match = re.match(
        r"^(https?://[^/]+)",
        current,
        re.IGNORECASE,
    )

    if not match:
        return href

    base = match.group(1)

    if href.startswith("/"):
        return base + href

    return base + "/" + href


def find_detail_map_url(driver):
    """
    Find the Detailed map info link on the current page.

    Example:

        <a href="?info_id=3">
            Detailed map info
        </a>
    """

    # ------------------------------------------------------------
    # Selenium DOM
    # ------------------------------------------------------------

    try:

        links = driver.find_elements(
            By.TAG_NAME,
            "a",
        )

        for link in links:

            try:

                text = (
                    link.text
                    or ""
                ).strip().lower()

                if "detailed map info" not in text:
                    continue

                href = (
                    link.get_attribute("href")
                    or ""
                ).strip()

                if href:
                    return href

            except Exception:
                continue

    except Exception:
        pass

    # ------------------------------------------------------------
    # page_source fallback
    # ------------------------------------------------------------

    try:
        source = driver.page_source
    except Exception:
        source = ""

    if not source:
        return ""

    soup = BeautifulSoup(
        source,
        "html.parser",
    )

    for link in soup.find_all("a"):

        text = (
            link.get_text(
                " ",
                strip=True,
            )
            .lower()
        )

        if "detailed map info" not in text:
            continue

        href = (
            link.get("href")
            or ""
        ).strip()

        if href:
            return absolute_url(
                driver,
                href,
            )

    return ""


def parse_wild_pokemon_html(html):
    """
    Parse the .wild-pokes section.

    Example:

        <div class="wild-pokes">
            <a href="/amount_viewer?pokemon=Feebas"
               class="map-wild-poke dexed">
                <img
                    src="/images/icons/Feebas.png"
                    alt="Feebas">
            </a>
        </div>
    """

    results = []

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    container = soup.select_one(
        "div.wild-pokes"
    )

    if not container:
        return results

    links = container.select(
        "a.map-wild-poke"
    )

    for link in links:

        images = link.find_all(
            "img"
        )

        if not images:
            continue

        # The Pokémon image is normally
        # the first image with an alt.
        pokemon_image = None

        for image in images:

            alt = (
                image.get("alt")
                or ""
            ).strip()

            if alt:
                pokemon_image = image
                break

        if pokemon_image is None:
            continue

        name = (
            pokemon_image.get(
                "alt"
            )
            or ""
        ).strip()

        if not name:
            continue

        href = (
            link.get("href")
            or ""
        ).strip()

        species_param = ""

        match = re.search(
            r"[?&]pokemon=([^&]+)",
            href,
            re.IGNORECASE,
        )

        if match:
            species_param = (
                match.group(1)
                .strip()
            )

        classes = link.get(
            "class",
            [],
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
            }
        )

    return results


def fetch_detail_page(
    driver,
    detail_url,
):
    """
    Fetch a map detail page directly.

    Uses the existing Selenium session so the
    current login/session cookies remain available.
    """

    if not detail_url:
        return ""

    try:

        driver.get(
            detail_url
        )

    except Exception as exc:

        print(
            f"    [DB] Failed to open detail URL: "
            f"{exc}"
        )

        return ""

    return driver.page_source


def update_current_map(
    driver,
    map_name,
    map_url=None,
    exclusive=False,
    area_id=None,
):
    """
    Discover and update one map.

    The driver should already be on the map page.
    """

    print(
        f"    [DB] Updating: {map_name}"
    )

    detail_url = find_detail_map_url(
        driver
    )

    if not detail_url:

        print(
            "    [DB] Detailed map info "
            "link not found."
        )

        return False

    print(
        f"    [DB] Detail URL: {detail_url}"
    )

    # Save map information immediately.
    map_id = upsert_map(
        name=map_name,
        map_url=map_url,
        detail_url=detail_url,
        exclusive=exclusive,
        area_id=area_id,
    )

    html = fetch_detail_page(
        driver,
        detail_url,
    )

    if not html:

        return False

    pokemon = parse_wild_pokemon_html(
        html
    )

    print(
        f"    [DB] Found {len(pokemon)} "
        f"Pokémon entries."
    )

    if pokemon:

        replace_map_pokemon(
            map_id,
            pokemon,
            timestamp(),
        )

    else:

        print(
            "    [DB] WARNING: no "
            "wild-pokes entries found."
        )

    return True


def update_from_known_detail_url(
    driver,
    map_name,
):
    """
    Update a map using its previously saved
    detail URL.

    This is the fast path.

    No map clicking is required.
    """

    initialize_database()

    from map_database import get_connection

    conn = get_connection()

    try:

        row = conn.execute(
            """
            SELECT
                id,
                detail_url,
                map_url,
                exclusive,
                area_id
            FROM maps
            WHERE name = ?
            """,
            (map_name,),
        ).fetchone()

    finally:

        conn.close()

    if not row:
        return False

    detail_url = row["detail_url"]

    if not detail_url:
        return False

    print(
        f"    [DB] Fast update: {map_name}"
    )

    html = fetch_detail_page(
        driver,
        detail_url,
    )

    if not html:
        return False

    pokemon = parse_wild_pokemon_html(
        html
    )

    print(
        f"    [DB] Found {len(pokemon)} "
        f"Pokémon entries."
    )

    if pokemon:

        replace_map_pokemon(
            row["id"],
            pokemon,
            timestamp(),
        )

    return True


if __name__ == "__main__":

    initialize_database()

    print()
    print("=" * 60)
    print("ECLIPSE MAP DATABASE UPDATER")
    print("=" * 60)
    print()
    print(
        "Database initialized."
    )
    print()
    print(
        "This script is intended to be"
    )
    print(
        "used with the Selenium driver"
    )
    print(
        "from search.py."
    )
    print()