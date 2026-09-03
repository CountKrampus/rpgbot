"""
Manual Pokémon Collection Log Manager for Eclipse RPG.

This module is intentionally 100% manual.

Users can:
    - Create named collection logs
    - Select a collection log
    - Rename collection logs
    - Delete collection logs
    - Add Pokémon to a selected collection
    - Edit Pokémon quantity / variant
    - Remove Pokémon from a collection
    - View only Pokémon belonging to the selected collection
    - Search the selected collection
    - View missing Pokémon
    - View collection statistics

Collection entry data is intentionally limited to:

    Pokémon
    Variant
    Quantity

No Selenium, browser automation, automatic detection, automatic
collection updates, or individual-Pokémon tracking is performed here.
"""

import os
import sys
import platform
import sqlite3
import re
import time


# ============================================================
# DATABASE
# ============================================================

DB_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "eclipse_maps.db"
)


def _connect():
    """Open the shared Eclipse RPG SQLite database."""
    return sqlite3.connect(DB_FILE)


def _initialize_database():
    """
    Create the collection tables if they do not already exist.

    Existing database tables are not modified.
    """

    conn = _connect()

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS collection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                UNIQUE(user_id, name)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pokemon_collection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                pokemon_id INTEGER NOT NULL,
                variant TEXT NOT NULL DEFAULT 'Default',
                quantity INTEGER NOT NULL DEFAULT 1,

                FOREIGN KEY(collection_id)
                    REFERENCES collection_logs(id)
                    ON DELETE CASCADE,

                UNIQUE(
                    collection_id,
                    pokemon_id,
                    variant
                )
            )
            """
        )

        conn.commit()

    finally:
        conn.close()


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

            if kernel32.GetConsoleMode(
                h_out,
                ctypes.byref(mode)
            ):
                kernel32.SetConsoleMode(
                    h_out,
                    mode.value | 0x0004
                )

        except Exception:
            pass

        os.system("")


_init_console()


# ============================================================
# ANSI & STYLING
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

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

ANSI_STRIP_REGEX = re.compile(
    r"\x1b\[[0-9;]*[mK]"
)


def _strip_ansi(text: str) -> str:
    """Strip ANSI escape sequences for visible-length calculations."""
    return ANSI_STRIP_REGEX.sub("", text)


def _row(content: str, width: int = 71) -> str:
    """Create a correctly padded ANSI-aware box row."""

    visible_length = len(
        _strip_ansi(content)
    )

    padding = max(
        0,
        width - visible_length
    )

    return (
        f"{BORDER_COLOR}║{RESET}"
        f"{content}"
        f"{' ' * padding}"
        f"{BORDER_COLOR}║{RESET}"
    )


def _borders(width: int = 71):
    """Return the standard collection menu borders."""

    return (
        f"{BORDER_COLOR}╔{'═' * width}╗{RESET}",
        f"{BORDER_COLOR}╠{'═' * width}╣{RESET}",
        f"{BORDER_COLOR}╚{'═' * width}╝{RESET}",
    )


# ============================================================
# USER ID
# ============================================================

def _get_user_id():
    """
    Determine the current RPGBot account/user identifier.

    The collection system accepts a user identifier supplied by
    the caller. When none is available, the local account name
    can be supplied through the environment.

    The main menu can later pass the actual selected account
    directly without changing this module's database structure.
    """

    value = os.environ.get(
        "RPGBOT_USER_ID"
    )

    if value:
        return str(value)

    return "default"


# ============================================================
# COLLECTION LOG DATABASE FUNCTIONS
# ============================================================

def _get_collections(user_id):
    """Return all collection logs belonging to the user."""

    conn = _connect()

    try:
        return conn.execute(
            """
            SELECT
                id,
                name
            FROM collection_logs
            WHERE user_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            (str(user_id),)
        ).fetchall()

    finally:
        conn.close()


def _get_collection(
    collection_id,
    user_id
):
    """Return one collection only if it belongs to the user."""

    conn = _connect()

    try:
        return conn.execute(
            """
            SELECT
                id,
                name
            FROM collection_logs
            WHERE id = ?
              AND user_id = ?
            """,
            (
                collection_id,
                str(user_id)
            )
        ).fetchone()

    finally:
        conn.close()


def _create_collection(
    user_id,
    name
):
    """Create a new collection log."""

    name = name.strip()

    if not name:
        return False, "Collection name cannot be empty."

    conn = _connect()

    try:
        conn.execute(
            """
            INSERT INTO collection_logs (
                user_id,
                name
            )
            VALUES (?, ?)
            """,
            (
                str(user_id),
                name
            )
        )

        conn.commit()

        return True, "Collection created successfully."

    except sqlite3.IntegrityError:
        return (
            False,
            "You already have a collection with that name."
        )

    finally:
        conn.close()


def _rename_collection(
    collection_id,
    user_id,
    new_name
):
    """Rename a user's collection."""

    new_name = new_name.strip()

    if not new_name:
        return False, "Collection name cannot be empty."

    conn = _connect()

    try:
        cursor = conn.execute(
            """
            UPDATE collection_logs
            SET name = ?
            WHERE id = ?
              AND user_id = ?
            """,
            (
                new_name,
                collection_id,
                str(user_id)
            )
        )

        conn.commit()

        if cursor.rowcount == 0:
            return False, "Collection could not be found."

        return True, "Collection renamed successfully."

    except sqlite3.IntegrityError:
        return (
            False,
            "You already have a collection with that name."
        )

    finally:
        conn.close()


def _delete_collection(
    collection_id,
    user_id
):
    """
    Delete a collection and all Pokémon entries belonging to it.
    """

    conn = _connect()

    try:
        conn.execute(
            """
            DELETE FROM pokemon_collection
            WHERE collection_id = ?
            """,
            (collection_id,)
        )

        cursor = conn.execute(
            """
            DELETE FROM collection_logs
            WHERE id = ?
              AND user_id = ?
            """,
            (
                collection_id,
                str(user_id)
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


# ============================================================
# POKÉMON DATABASE FUNCTIONS
# ============================================================

def _search_master_pokemon(query):
    """
    Search the existing Pokémon database.

    The collection system never changes the master Pokémon data.
    """

    query = query.strip()

    if not query:
        return []

    conn = _connect()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                name,
                species_param
            FROM pokemon
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()

    except sqlite3.Error:
        return []

    finally:
        conn.close()

    wanted = re.sub(
        r"[^a-z0-9]+",
        "",
        query.lower()
    )

    results = []

    for pokemon_id, name, species_param in rows:

        normalized_name = re.sub(
            r"[^a-z0-9]+",
            "",
            str(name or "").lower()
        )

        normalized_species = re.sub(
            r"[^a-z0-9]+",
            "",
            str(species_param or "").lower()
        )

        if (
            wanted in normalized_name
            or wanted in normalized_species
        ):
            results.append(
                {
                    "id": pokemon_id,
                    "name": name,
                    "species": species_param
                }
            )

    return results


def _get_pokemon_by_id(pokemon_id):
    """Return master Pokémon information."""

    conn = _connect()

    try:
        return conn.execute(
            """
            SELECT
                id,
                name,
                species_param
            FROM pokemon
            WHERE id = ?
            """,
            (pokemon_id,)
        ).fetchone()

    finally:
        conn.close()


# ============================================================
# COLLECTION ENTRY FUNCTIONS
# ============================================================

def _get_collection_entries(
    collection_id,
    search=None
):
    """
    Return ONLY Pokémon belonging to the selected collection.
    """

    conn = _connect()

    try:

        if search:

            wanted = f"%{search.lower()}%"

            return conn.execute(
                """
                SELECT
                    pc.id,
                    pc.pokemon_id,
                    p.name,
                    pc.variant,
                    pc.quantity
                FROM pokemon_collection pc
                JOIN pokemon p
                    ON p.id = pc.pokemon_id
                WHERE pc.collection_id = ?
                  AND (
                      LOWER(p.name) LIKE ?
                      OR LOWER(pc.variant) LIKE ?
                  )
                ORDER BY
                    p.name COLLATE NOCASE,
                    pc.variant COLLATE NOCASE
                """,
                (
                    collection_id,
                    wanted,
                    wanted
                )
            ).fetchall()

        return conn.execute(
            """
            SELECT
                pc.id,
                pc.pokemon_id,
                p.name,
                pc.variant,
                pc.quantity
            FROM pokemon_collection pc
            JOIN pokemon p
                ON p.id = pc.pokemon_id
            WHERE pc.collection_id = ?
            ORDER BY
                p.name COLLATE NOCASE,
                pc.variant COLLATE NOCASE
            """,
            (collection_id,)
        ).fetchall()

    finally:
        conn.close()


def _add_collection_entry(
    collection_id,
    pokemon_id,
    variant,
    quantity
):
    """Manually add Pokémon to a collection."""

    variant = variant.strip() or "Default"

    conn = _connect()

    try:
        existing = conn.execute(
            """
            SELECT
                id,
                quantity
            FROM pokemon_collection
            WHERE collection_id = ?
              AND pokemon_id = ?
              AND variant = ?
            """,
            (
                collection_id,
                pokemon_id,
                variant
            )
        ).fetchone()

        if existing:

            new_quantity = (
                existing[1] + quantity
            )

            conn.execute(
                """
                UPDATE pokemon_collection
                SET quantity = ?
                WHERE id = ?
                """,
                (
                    new_quantity,
                    existing[0]
                )
            )

        else:

            conn.execute(
                """
                INSERT INTO pokemon_collection (
                    collection_id,
                    pokemon_id,
                    variant,
                    quantity
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    collection_id,
                    pokemon_id,
                    variant,
                    quantity
                )
            )

        conn.commit()

        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def _update_collection_entry(
    entry_id,
    collection_id,
    variant,
    quantity
):
    """Manually update a collection entry."""

    variant = variant.strip() or "Default"

    conn = _connect()

    try:
        cursor = conn.execute(
            """
            UPDATE pokemon_collection
            SET
                variant = ?,
                quantity = ?
            WHERE id = ?
              AND collection_id = ?
            """,
            (
                variant,
                quantity,
                entry_id,
                collection_id
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def _remove_collection_entry(
    entry_id,
    collection_id
):
    """Remove one Pokémon entry from the selected collection."""

    conn = _connect()

    try:
        cursor = conn.execute(
            """
            DELETE FROM pokemon_collection
            WHERE id = ?
              AND collection_id = ?
            """,
            (
                entry_id,
                collection_id
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


def _get_collection_totals(collection_id):
    """Return entry count and total Pokémon quantity."""

    conn = _connect()

    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(quantity), 0),
                COUNT(DISTINCT pokemon_id)
            FROM pokemon_collection
            WHERE collection_id = ?
            """,
            (collection_id,)
        ).fetchone()

        return {
            "entries": row[0],
            "quantity": row[1],
            "species": row[2]
        }

    finally:
        conn.close()


# ============================================================
# MENU HELPERS
# ============================================================

def _pause(message="Press Enter to continue..."):
    input(
        f"\n{GRAY}{message}{RESET}"
    )


def _positive_integer(prompt):
    """Request a positive integer."""

    while True:

        value = input(prompt).strip()

        try:
            value = int(value)

            if value <= 0:
                raise ValueError

            return value

        except ValueError:

            print(
                f"{RED}✗ Please enter a number greater than 0.{RESET}"
            )


def _confirm(prompt):
    """Simple Y/N confirmation."""

    answer = input(
        f"{BOLD}{CYAN}{prompt} {GRAY}[y/n]:{RESET} "
    ).strip().lower()

    return answer in (
        "y",
        "yes"
    )


# ============================================================
# COLLECTION LOG LIST
# ============================================================

def _render_collection_list(
    user_id
):
    """Display the user's collection logs."""

    w = 71

    top, mid, bot = _borders(w)

    collections = _get_collections(
        user_id
    )

    print()
    print(top)
    print(
        _row(
            f"  {BOLD}{MAGENTA}📚  COLLECTION LOGS{RESET}",
            w
        )
    )
    print(mid)

    if not collections:

        print(
            _row(
                f"  {YELLOW}No collection logs have been created yet.{RESET}",
                w
            )
        )

    else:

        for index, collection in enumerate(
            collections,
            1
        ):

            collection_id = collection[0]
            name = collection[1]

            totals = _get_collection_totals(
                collection_id
            )

            line = (
                f"  {KEY_COLOR}[{index:2d}]{RESET} "
                f"{NAME_COLOR}{name[:30]:<30}{RESET} "
                f"{GRAY}{totals['species']} species  "
                f"•  {totals['quantity']} total{RESET}"
            )

            print(
                _row(line, w)
            )

    print(mid)

    print(
        _row(
            f"  {KEY_COLOR}[N]{RESET} New Collection"
            f"    {KEY_COLOR}[M]{RESET} Manage"
            f"    {RED}[0]{RESET} Back",
            w
        )
    )

    print(bot)

    return collections


# ============================================================
# CREATE COLLECTION
# ============================================================

def _create_collection_menu(
    user_id
):
    print()

    print(
        f"{CATEGORY_COLOR}Create New Collection Log{RESET}"
    )

    print(
        f"{GRAY}Give this collection its own name. "
        f"Examples: Main Collection, Shiny Collection, "
        f"Trade Binder.{RESET}"
    )

    name = input(
        f"\n{BOLD}{CYAN}❯ Collection name:{RESET} "
    ).strip()

    success, message = _create_collection(
        user_id,
        name
    )

    if success:
        print(
            f"\n{GREEN}✓ {message}{RESET}"
        )
    else:
        print(
            f"\n{RED}✗ {message}{RESET}"
        )

    _pause()


# ============================================================
# COLLECTION MANAGEMENT
# ============================================================

def _manage_collections(
    user_id
):
    while True:

        collections = _get_collections(
            user_id
        )

        w = 71
        top, mid, bot = _borders(w)

        print()
        print(top)
        print(
            _row(
                f"  {BOLD}{MAGENTA}⚙  MANAGE COLLECTIONS{RESET}",
                w
            )
        )
        print(mid)

        if not collections:

            print(
                _row(
                    f"  {YELLOW}No collections to manage.{RESET}",
                    w
                )
            )

            print(bot)
            _pause()
            return

        for index, collection in enumerate(
            collections,
            1
        ):

            print(
                _row(
                    f"  {KEY_COLOR}[{index:2d}]{RESET} "
                    f"{NAME_COLOR}{collection[1]}{RESET}",
                    w
                )
            )

        print(mid)

        print(
            _row(
                f"  {KEY_COLOR}[R]{RESET} Rename Collection"
                f"    {RED}[D]{RESET} Delete Collection"
                f"    {RED}[0]{RESET} Back",
                w
            )
        )

        print(bot)

        choice = input(
            f"\n{BOLD}{CYAN}"
            f"❯ Select Action [number/R/D/0]:"
            f"{RESET} "
        ).strip().lower()

        if choice == "0":
            return

        if choice == "r":

            selected = _select_collection(
                user_id,
                "Select collection to rename"
            )

            if not selected:
                continue

            collection_id, name = selected

            new_name = input(
                f"\n{BOLD}{CYAN}"
                f"❯ New name for '{name}':"
                f"{RESET} "
            ).strip()

            success, message = _rename_collection(
                collection_id,
                user_id,
                new_name
            )

            if success:
                print(
                    f"{GREEN}✓ {message}{RESET}"
                )
            else:
                print(
                    f"{RED}✗ {message}{RESET}"
                )

            _pause()
            continue

        if choice == "d":

            selected = _select_collection(
                user_id,
                "Select collection to delete"
            )

            if not selected:
                continue

            collection_id, name = selected

            print(
                f"\n{RED}{BOLD}"
                f"WARNING: This permanently deletes "
                f"'{name}' and all Pokémon entries inside it."
                f"{RESET}"
            )

            if not _confirm(
                "Delete this collection?"
            ):
                print(
                    f"{YELLOW}Cancelled.{RESET}"
                )
                time.sleep(0.7)
                continue

            if _delete_collection(
                collection_id,
                user_id
            ):
                print(
                    f"{GREEN}✓ Collection deleted.{RESET}"
                )
            else:
                print(
                    f"{RED}✗ Collection could not be deleted.{RESET}"
                )

            _pause()
            continue

        try:

            index = int(choice)

            if 1 <= index <= len(collections):

                collection_id = collections[
                    index - 1
                ][0]

                _collection_menu(
                    user_id,
                    collection_id
                )

        except ValueError:
            print(
                f"{RED}✗ Invalid selection.{RESET}"
            )
            time.sleep(0.7)


def _select_collection(
    user_id,
    title="Select Collection"
):
    collections = _get_collections(
        user_id
    )

    if not collections:

        print(
            f"\n{YELLOW}No collections exist yet.{RESET}"
        )

        _pause()

        return None

    print(
        f"\n{CATEGORY_COLOR}{title}:{RESET}"
    )

    for index, collection in enumerate(
        collections,
        1
    ):

        print(
            f"  {KEY_COLOR}[{index:2d}]{RESET} "
            f"{NAME_COLOR}{collection[1]}{RESET}"
        )

    print(
        f"  {RED}[0]{RESET} Cancel"
    )

    choice = input(
        f"\n{BOLD}{CYAN}"
        f"❯ Select Collection:"
        f"{RESET} "
    ).strip()

    try:

        index = int(choice)

        if index == 0:
            return None

        if 1 <= index <= len(collections):

            selected = collections[
                index - 1
            ]

            return (
                selected[0],
                selected[1]
            )

    except ValueError:
        pass

    print(
        f"{RED}✗ Invalid collection selection.{RESET}"
    )

    time.sleep(0.8)

    return None


# ============================================================
# VIEW COLLECTION
# ============================================================

def _view_collection(
    collection_id,
    collection_name,
    search=None
):
    """Display only entries belonging to this collection."""

    entries = _get_collection_entries(
        collection_id,
        search
    )

    totals = _get_collection_totals(
        collection_id
    )

    w = 71
    top, mid, bot = _borders(w)

    print()
    print(top)

    title = (
        f"  {BOLD}{MAGENTA}📖  {collection_name[:45]}{RESET}"
    )

    print(
        _row(title, w)
    )

    print(mid)

    status = (
        f"  {GRAY}SPECIES:{RESET} "
        f"{CYAN}{totals['species']}{RESET}"
        f"   {GRAY}TOTAL:{RESET} "
        f"{CYAN}{totals['quantity']}{RESET}"
        f"   {GRAY}ENTRIES:{RESET} "
        f"{CYAN}{totals['entries']}{RESET}"
    )

    if search:
        status += (
            f"   {GRAY}SEARCH:{RESET} "
            f"{YELLOW}{search}{RESET}"
        )

    print(
        _row(status, w)
    )

    print(mid)

    header = (
        f"  {GRAY}"
        f"{'#':<5}"
        f"{'POKÉMON':<25}"
        f"{'VARIANT':<22}"
        f"{'QTY':<8}"
        f"{RESET}"
    )

    print(
        _row(header, w)
    )

    print(mid)

    if not entries:

        message = (
            f"  {YELLOW}"
            f"No Pokémon are recorded in this collection."
            f"{RESET}"
        )

        if search:
            message = (
                f"  {YELLOW}"
                f"No matches found for '{search}'."
                f"{RESET}"
            )

        print(
            _row(message, w)
        )

    else:

        for index, entry in enumerate(
            entries,
            1
        ):

            entry_id = entry[0]
            pokemon_name = entry[2]
            variant = entry[3]
            quantity = entry[4]

            line = (
                f"  {KEY_COLOR}[{index:3d}]{RESET} "
                f"{WHITE}{str(pokemon_name)[:23]:<23}{RESET} "
                f"{GOLD}{str(variant)[:20]:<20}{RESET} "
                f"{YELLOW}{quantity:<8}{RESET}"
            )

            print(
                _row(line, w)
            )

    print(mid)

    print(
        _row(
            f"  {KEY_COLOR}[A]{RESET} Add"
            f"    {KEY_COLOR}[E]{RESET} Edit"
            f"    {KEY_COLOR}[R]{RESET} Remove"
            f"    {KEY_COLOR}[S]{RESET} Search"
            f"    {KEY_COLOR}[M]{RESET} Missing"
            f"    {RED}[B]{RESET} Back",
            w
        )
    )

    print(bot)


# ============================================================
# ADD POKÉMON
# ============================================================

def _add_pokemon(
    collection_id
):
    print()

    print(
        f"{CATEGORY_COLOR}Add Pokémon to Collection{RESET}"
    )

    query = input(
        f"\n{BOLD}{CYAN}"
        f"❯ Search Pokémon:"
        f"{RESET} "
    ).strip()

    if not query:
        return

    results = _search_master_pokemon(
        query
    )

    if not results:

        print(
            f"\n{YELLOW}"
            f"No Pokémon found for '{query}'."
            f"{RESET}"
        )

        _pause()

        return

    if len(results) > 25:
        results = results[:25]

    print()

    for index, pokemon in enumerate(
        results,
        1
    ):

        print(
            f"  {KEY_COLOR}[{index:2d}]{RESET} "
            f"{NAME_COLOR}{pokemon['name']}{RESET}"
            f"{GRAY}"
            f" ({pokemon['species'] or 'No species parameter'})"
            f"{RESET}"
        )

    print(
        f"  {RED}[0]{RESET} Cancel"
    )

    choice = input(
        f"\n{BOLD}{CYAN}"
        f"❯ Select Pokémon:"
        f"{RESET} "
    ).strip()

    try:

        index = int(choice)

        if index == 0:
            return

        if not 1 <= index <= len(results):
            raise ValueError

    except ValueError:

        print(
            f"{RED}✗ Invalid Pokémon selection.{RESET}"
        )

        time.sleep(0.8)

        return

    pokemon = results[
        index - 1
    ]

    variant = input(
        f"\n{BOLD}{CYAN}"
        f"❯ Variant {GRAY}[Default]:"
        f"{CYAN}:{RESET} "
    ).strip()

    if not variant:
        variant = "Default"

    quantity = _positive_integer(
        f"{BOLD}{CYAN}"
        f"❯ Quantity:"
        f"{RESET} "
    )

    success = _add_collection_entry(
        collection_id,
        pokemon["id"],
        variant,
        quantity
    )

    if success:

        print(
            f"\n{GREEN}✓ Added "
            f"{quantity} × {pokemon['name']} "
            f"({variant}) to collection.{RESET}"
        )

    else:

        print(
            f"\n{RED}"
            f"✗ Could not add Pokémon to collection."
            f"{RESET}"
        )

    _pause()


# ============================================================
# EDIT POKÉMON
# ============================================================

def _edit_pokemon(
    collection_id
):
    entries = _get_collection_entries(
        collection_id
    )

    if not entries:

        print(
            f"\n{YELLOW}"
            f"This collection is empty."
            f"{RESET}"
        )

        _pause()

        return

    print(
        f"\n{CATEGORY_COLOR}"
        f"Select Pokémon Entry to Edit:"
        f"{RESET}"
    )

    for index, entry in enumerate(
        entries,
        1
    ):

        print(
            f"  {KEY_COLOR}[{index:3d}]{RESET} "
            f"{WHITE}{entry[2]}{RESET} "
            f"{GOLD}({entry[3]}){RESET} "
            f"{YELLOW}×{entry[4]}{RESET}"
        )

    print(
        f"  {RED}[0]{RESET} Cancel"
    )

    choice = input(
        f"\n{BOLD}{CYAN}"
        f"❯ Select Entry:"
        f"{RESET} "
    ).strip()

    try:

        index = int(choice)

        if index == 0:
            return

        if not 1 <= index <= len(entries):
            raise ValueError

    except ValueError:

        print(
            f"{RED}✗ Invalid selection.{RESET}"
        )

        time.sleep(0.7)

        return

    entry = entries[
        index - 1
    ]

    entry_id = entry[0]

    new_variant = input(
        f"\n{BOLD}{CYAN}"
        f"❯ Variant {GRAY}[{entry[3]}]:"
        f"{CYAN}:{RESET} "
    ).strip()

    if not new_variant:
        new_variant = entry[3]

    new_quantity = _positive_integer(
        f"{BOLD}{CYAN}"
        f"❯ Quantity {GRAY}[{entry[4]}]:"
        f"{CYAN}:{RESET} "
    )

    success = _update_collection_entry(
        entry_id,
        collection_id,
        new_variant,
        new_quantity
    )

    if success:

        print(
            f"\n{GREEN}"
            f"✓ Collection entry updated."
            f"{RESET}"
        )

    else:

        print(
            f"\n{RED}"
            f"✗ Could not update entry."
            f" It may create a duplicate Pokémon/variant."
            f"{RESET}"
        )

    _pause()


# ============================================================
# REMOVE POKÉMON
# ============================================================

def _remove_pokemon(
    collection_id
):
    entries = _get_collection_entries(
        collection_id
    )

    if not entries:

        print(
            f"\n{YELLOW}"
            f"This collection is empty."
            f"{RESET}"
        )

        _pause()

        return

    print(
        f"\n{CATEGORY_COLOR}"
        f"Select Pokémon Entry to Remove:"
        f"{RESET}"
    )

    for index, entry in enumerate(
        entries,
        1
    ):

        print(
            f"  {KEY_COLOR}[{index:3d}]{RESET} "
            f"{WHITE}{entry[2]}{RESET} "
            f"{GOLD}({entry[3]}){RESET} "
            f"{YELLOW}×{entry[4]}{RESET}"
        )

    print(
        f"  {RED}[0]{RESET} Cancel"
    )

    choice = input(
        f"\n{BOLD}{CYAN}"
        f"❯ Select Entry:"
        f"{RESET} "
    ).strip()

    try:

        index = int(choice)

        if index == 0:
            return

        if not 1 <= index <= len(entries):
            raise ValueError

    except ValueError:

        print(
            f"{RED}✗ Invalid selection.{RESET}"
        )

        time.sleep(0.7)

        return

    entry = entries[
        index - 1
    ]

    if not _confirm(
        f"Remove {entry[2]} ({entry[3]}) ×{entry[4]}?"
    ):
        print(
            f"{YELLOW}Cancelled.{RESET}"
        )

        time.sleep(0.6)

        return

    success = _remove_collection_entry(
        entry[0],
        collection_id
    )

    if success:

        print(
            f"{GREEN}✓ Pokémon removed from collection.{RESET}"
        )

    else:

        print(
            f"{RED}✗ Could not remove Pokémon entry.{RESET}"
        )

    _pause()


# ============================================================
# SEARCH
# ============================================================

def _search_collection(
    collection_id,
    collection_name
):
    query = input(
        f"\n{BOLD}{CYAN}"
        f"❯ Search this collection:"
        f"{RESET} "
    ).strip()

    if not query:
        return

    _view_collection(
        collection_id,
        collection_name,
        query
    )

    _pause()


# ============================================================
# MISSING POKÉMON
# ============================================================

def _get_master_pokemon():
    """Return all Pokémon in the master database."""

    conn = _connect()

    try:
        return conn.execute(
            """
            SELECT
                id,
                name,
                species_param
            FROM pokemon
            ORDER BY
                name COLLATE NOCASE
            """
        ).fetchall()

    finally:
        conn.close()


def _get_owned_pokemon_ids(
    collection_id
):
    """Return Pokémon species already represented in collection."""

    conn = _connect()

    try:
        rows = conn.execute(
            """
            SELECT DISTINCT pokemon_id
            FROM pokemon_collection
            WHERE collection_id = ?
            """,
            (collection_id,)
        ).fetchall()

        return {
            row[0]
            for row in rows
        }

    finally:
        conn.close()


def _missing_pokemon(
    collection_id,
    collection_name
):
    """
    Display master Pokémon not represented in this collection.

    Variants are intentionally not treated as separate missing
    species. A Pokémon is considered present once it exists in
    the selected collection.
    """

    master = _get_master_pokemon()

    if not master:

        print(
            f"\n{YELLOW}"
            f"The master Pokémon database is empty or unavailable."
            f"{RESET}"
        )

        _pause()

        return

    owned_ids = _get_owned_pokemon_ids(
        collection_id
    )

    missing = [
        pokemon
        for pokemon in master
        if pokemon[0] not in owned_ids
    ]

    w = 71
    top, mid, bot = _borders(w)

    print()
    print(top)

    print(
        _row(
            f"  {BOLD}{MAGENTA}"
            f"❓  MISSING POKÉMON — {collection_name}"
            f"{RESET}",
            w
        )
    )

    print(mid)

    print(
        _row(
            f"  {GRAY}MISSING:{RESET} "
            f"{RED}{len(missing)}{RESET}"
            f"   {GRAY}COMPLETE:{RESET} "
            f"{GREEN}{len(master) - len(missing)}{RESET}"
            f"   {GRAY}TOTAL:{RESET} "
            f"{CYAN}{len(master)}{RESET}",
            w
        )
    )

    print(mid)

    if not missing:

        print(
            _row(
                f"  {GREEN}"
                f"✓ This collection contains every Pokémon "
                f"in the master database."
                f"{RESET}",
                w
            )
        )

    else:

        for index, pokemon in enumerate(
            missing,
            1
        ):

            line = (
                f"  {KEY_COLOR}[{index:4d}]{RESET} "
                f"{WHITE}{str(pokemon[1])[:35]:<35}{RESET}"
            )

            print(
                _row(line, w)
            )

    print(bot)

    _pause()


# ============================================================
# COLLECTION STATISTICS
# ============================================================

def _collection_statistics(
    collection_id,
    collection_name
):
    totals = _get_collection_totals(
        collection_id
    )

    master = _get_master_pokemon()

    master_count = len(
        master
    )

    species = totals[
        "species"
    ]

    if master_count:
        completion = (
            species / master_count
        ) * 100
    else:
        completion = 0.0

    w = 71
    top, mid, bot = _borders(w)

    print()
    print(top)

    print(
        _row(
            f"  {BOLD}{MAGENTA}"
            f"📊  COLLECTION STATISTICS"
            f"{RESET}",
            w
        )
    )

    print(mid)

    print(
        _row(
            f"  {GRAY}COLLECTION:{RESET} "
            f"{NAME_COLOR}{collection_name}{RESET}",
            w
        )
    )

    print(mid)

    stats = [
        (
            "Unique Pokémon",
            str(species)
        ),
        (
            "Total Quantity",
            str(totals["quantity"])
        ),
        (
            "Collection Entries",
            str(totals["entries"])
        ),
        (
            "Master Pokémon",
            str(master_count)
        ),
        (
            "Completion",
            f"{completion:.1f}%"
        ),
    ]

    for label, value in stats:

        print(
            _row(
                f"  {GRAY}{label:<25}{RESET} "
                f"{CYAN}{BOLD}{value}{RESET}",
                w
            )
        )

    print(bot)

    _pause()


# ============================================================
# SELECTED COLLECTION MENU
# ============================================================

def _collection_menu(
    user_id,
    collection_id
):
    """
    Menu for exactly one collection.

    Every operation here is scoped to collection_id.
    """

    collection = _get_collection(
        collection_id,
        user_id
    )

    if not collection:
        return

    collection_name = collection[
        1
    ]

    while True:

        collection = _get_collection(
            collection_id,
            user_id
        )

        if not collection:
            return

        collection_name = collection[
            1
        ]

        totals = _get_collection_totals(
            collection_id
        )

        master_count = len(
            _get_master_pokemon()
        )

        if master_count:
            completion = (
                totals["species"]
                / master_count
            ) * 100
        else:
            completion = 0.0

        w = 71
        top, mid, bot = _borders(w)

        print()
        print(top)

        print(
            _row(
                f"  {BOLD}{MAGENTA}"
                f"📖  {collection_name[:55]}"
                f"{RESET}",
                w
            )
        )

        print(mid)

        hud = (
            f"  {GRAY}POKÉMON:{RESET} "
            f"{CYAN}{totals['species']}/{master_count}{RESET}"
            f"   {GRAY}TOTAL:{RESET} "
            f"{CYAN}{totals['quantity']}{RESET}"
            f"   {GRAY}COMPLETE:{RESET} "
            f"{GREEN}{completion:.1f}%{RESET}"
        )

        print(
            _row(hud, w)
        )

        print(mid)
        print(
            _row("", w)
        )

        print(
            _row(
                f"  {CATEGORY_COLOR}COLLECTION{RESET}",
                w
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 1]{RESET} "
                f"{NAME_COLOR}View Collection{RESET}"
                f"    {DESC_COLOR}"
                f"— View only Pokémon in this log"
                f"{RESET}",
                w
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 2]{RESET} "
                f"{NAME_COLOR}Add Pokémon{RESET}"
                f"       {DESC_COLOR}"
                f"— Manually add Pokémon, variant & quantity"
                f"{RESET}",
                w
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 3]{RESET} "
                f"{NAME_COLOR}Edit Pokémon{RESET}"
                f"      {DESC_COLOR}"
                f"— Change variant or quantity"
                f"{RESET}",
                w
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 4]{RESET} "
                f"{NAME_COLOR}Remove Pokémon{RESET}"
                f"    {DESC_COLOR}"
                f"— Remove an entry from this log"
                f"{RESET}",
                w
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 5]{RESET} "
                f"{NAME_COLOR}Search{RESET}"
                f"             {DESC_COLOR}"
                f"— Search only this collection"
                f"{RESET}",
                w
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 6]{RESET} "
                f"{NAME_COLOR}Missing Pokémon{RESET}"
                f"    {DESC_COLOR}"
                f"— Show species not in this log"
                f"{RESET}",
                w
            )
        )

        print(
            _row(
                f"    {KEY_COLOR}[ 7]{RESET} "
                f"{NAME_COLOR}Statistics{RESET}"
                f"          {DESC_COLOR}"
                f"— Collection completion & totals"
                f"{RESET}",
                w
            )
        )

        print(
            _row("", w)
        )

        print(
            _row(
                f"    {RED}[ 0]{RESET} "
                f"{RED}Back{RESET}",
                w
            )
        )

        print(bot)

        choice = input(
            f"\n{BOLD}{CYAN}"
            f"❯ Select Option [0-7]:"
            f"{RESET} "
        ).strip()

        if choice == "0":
            return

        elif choice == "1":

            _view_collection(
                collection_id,
                collection_name
            )

            _pause()

        elif choice == "2":

            _add_pokemon(
                collection_id
            )

        elif choice == "3":

            _edit_pokemon(
                collection_id
            )

        elif choice == "4":

            _remove_pokemon(
                collection_id
            )

        elif choice == "5":

            _search_collection(
                collection_id,
                collection_name
            )

        elif choice == "6":

            _missing_pokemon(
                collection_id,
                collection_name
            )

        elif choice == "7":

            _collection_statistics(
                collection_id,
                collection_name
            )

        else:

            print(
                f"\n{RED}"
                f"✗ Invalid choice. Please select 0-7."
                f"{RESET}"
            )

            time.sleep(0.8)


# ============================================================
# MAIN COLLECTION MENU
# ============================================================

def collection_menu(
    driver=None,
    user_id=None
):
    """
    Entry point used by main_menu.py.

    driver is accepted for compatibility with the existing menu
    architecture but is deliberately NOT used.

    The collection system is completely manual.
    """

    del driver

    _initialize_database()

    if user_id is None:
        user_id = _get_user_id()

    while True:

        collections = _render_collection_list(
            user_id
        )

        try:

            choice = input(
                f"\n{BOLD}{CYAN}"
                f"❯ Select Collection / Action "
                f"{GRAY}[1-{max(1, len(collections))}/N/M/0]"
                f"{CYAN}:{RESET} "
            ).strip().lower()

        except (KeyboardInterrupt, EOFError):

            print(
                f"\n{YELLOW}"
                f"Returning to main menu..."
                f"{RESET}"
            )

            return

        if choice == "0":
            return

        if choice == "n":

            _create_collection_menu(
                user_id
            )

            continue

        if choice == "m":

            _manage_collections(
                user_id
            )

            continue

        try:

            index = int(choice)

            if (
                1 <= index <= len(collections)
            ):

                collection_id = collections[
                    index - 1
                ][0]

                _collection_menu(
                    user_id,
                    collection_id
                )

            else:

                raise ValueError

        except ValueError:

            print(
                f"\n{RED}"
                f"✗ Invalid selection."
                f"{RESET}"
            )

            time.sleep(0.7)


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    collection_menu()