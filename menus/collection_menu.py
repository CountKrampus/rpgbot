"""
Manual Pokémon Collection Tracker for Eclipse RPG.

IMPORTANT:
    This module is intentionally completely independent of the Eclipse
    Pokémon master database.

    It does NOT:
        - Query the `pokemon` table
        - Use pokemon_id
        - Use map_id
        - Use species_param
        - Use dexed
        - Use icon_name
        - Use Selenium/browser automation
        - Automatically detect Pokémon

Every Pokémon name and variant is entered manually by the user.

Database:
    eclipse_maps.db

Collection tables created/used by this module:
    collection_logs
    pokemon_collection
"""

import os
import sqlite3
import csv
import json
from datetime import datetime, timezone

from box import fetch_all_box_pokemon


# ============================================================================
# DATABASE
# ============================================================================

DB_PATH = "eclipse_maps.db"


def _connect():
    """Open the collection database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _initialize_database():
    """
    Create only the tables required by the manual collection tracker.

    This function deliberately does not inspect, alter, or depend on the
    existing `pokemon` table.
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
        # Older installations predate box metadata.  Keep their rows intact
        # while allowing live-box imports to retain a box label.
        columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(pokemon_collection)"
            ).fetchall()
        }
        if "box" not in columns:
            conn.execute(
                "ALTER TABLE pokemon_collection ADD COLUMN box TEXT"
            )
        if "obtained_at" not in columns:
            conn.execute(
                "ALTER TABLE pokemon_collection ADD COLUMN obtained_at TEXT"
            )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pokemon_collection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                pokemon TEXT NOT NULL,
                variant TEXT NOT NULL DEFAULT 'Default',
                quantity INTEGER NOT NULL DEFAULT 1,

                FOREIGN KEY(collection_id)
                    REFERENCES collection_logs(id)
                    ON DELETE CASCADE,

                UNIQUE(
                    collection_id,
                    pokemon,
                    variant
                )
            )
            """
        )

        conn.commit()

    finally:
        conn.close()


# ============================================================================
# USER / ACCOUNT
# ============================================================================

def _get_user_id(user_id=None):
    """
    Resolve the account/user identifier.

    main.py passes the account object/string into the menu. This helper keeps
    the collection system compatible with the existing menu structure without
    requiring a specific account class.
    """
    if user_id is not None:
        if isinstance(user_id, str):
            return user_id

        for attr in ("username", "name", "account", "user_name"):
            value = getattr(user_id, attr, None)

            if value:
                return str(value)

        return str(user_id)

    return os.environ.get("RPGBOT_USER_ID", "default")


# ============================================================================
# COLLECTION DATABASE OPERATIONS
# ============================================================================

def _get_collections(user_id):
    conn = _connect()

    try:
        rows = conn.execute(
            """
            SELECT id, name
            FROM collection_logs
            WHERE user_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            (user_id,),
        ).fetchall()

        return rows

    finally:
        conn.close()


def _get_collection(collection_id, user_id):
    conn = _connect()

    try:
        return conn.execute(
            """
            SELECT id, name
            FROM collection_logs
            WHERE id = ?
              AND user_id = ?
            """,
            (collection_id, user_id),
        ).fetchone()

    finally:
        conn.close()


def _create_collection(user_id, name):
    name = name.strip()

    if not name:
        return False, "Collection name cannot be empty."

    conn = _connect()

    try:
        conn.execute(
            """
            INSERT INTO collection_logs (user_id, name)
            VALUES (?, ?)
            """,
            (user_id, name),
        )

        conn.commit()
        return True, f"Collection '{name}' created."

    except sqlite3.IntegrityError:
        return False, f"A collection named '{name}' already exists."

    finally:
        conn.close()


def _rename_collection(collection_id, user_id, new_name):
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
            (new_name, collection_id, user_id),
        )

        if cursor.rowcount == 0:
            return False, "Collection not found."

        conn.commit()
        return True, f"Collection renamed to '{new_name}'."

    except sqlite3.IntegrityError:
        return False, f"A collection named '{new_name}' already exists."

    finally:
        conn.close()


def _delete_collection(collection_id, user_id):
    collection = _get_collection(collection_id, user_id)

    if not collection:
        return False, "Collection not found."

    conn = _connect()

    try:
        conn.execute(
            """
            DELETE FROM collection_logs
            WHERE id = ?
              AND user_id = ?
            """,
            (collection_id, user_id),
        )

        conn.commit()

        return True, f"Collection '{collection[1]}' deleted."

    finally:
        conn.close()


# ============================================================================
# COLLECTION ENTRY DATABASE OPERATIONS
# ============================================================================

def _get_collection_entries(collection_id, search=None, box=None, include_box=False):
    conn = _connect()

    try:
        clauses = ["collection_id = ?"]
        params = [collection_id]
        if search:
            search_term = f"%{search}%"
            clauses.append(
                "(pokemon LIKE ? COLLATE NOCASE OR variant LIKE ? COLLATE NOCASE)"
            )
            params.extend([search_term, search_term])
        if box:
            clauses.append("COALESCE(box, 'Unassigned') = ? COLLATE NOCASE")
            params.append(str(box).strip())
        return conn.execute(
            f"""
            SELECT id, pokemon, variant, quantity
                   {", box, obtained_at" if include_box else ""}
            FROM pokemon_collection
            WHERE {' AND '.join(clauses)}
            ORDER BY pokemon COLLATE NOCASE, variant COLLATE NOCASE
            """,
            params,
        ).fetchall()

    finally:
        conn.close()


def _get_collection_entry(entry_id, collection_id):
    conn = _connect()

    try:
        return conn.execute(
            """
            SELECT id, pokemon, variant, quantity
            FROM pokemon_collection
            WHERE id = ?
              AND collection_id = ?
            """,
            (entry_id, collection_id),
        ).fetchone()

    finally:
        conn.close()


def _add_collection_entry(collection_id, pokemon, variant, quantity, box=None):
    pokemon = pokemon.strip()
    variant = variant.strip() or "Default"

    if not pokemon:
        return False, "Pokémon name cannot be empty."

    if quantity < 1:
        return False, "Quantity must be at least 1."

    conn = _connect()

    try:
        existing = conn.execute(
            """
            SELECT id, quantity
            FROM pokemon_collection
            WHERE collection_id = ?
              AND pokemon = ?
              AND variant = ?
            """,
            (
                collection_id,
                pokemon,
                variant,
            ),
        ).fetchone()

        if existing:
            new_quantity = existing[1] + quantity

            conn.execute(
                """
                UPDATE pokemon_collection
                SET quantity = ?,
                    box = COALESCE(box, ?)
                WHERE id = ?
                  AND collection_id = ?
                """,
                (
                    new_quantity,
                    str(box).strip() if box else None,
                    existing[0],
                    collection_id,
                ),
            )

            conn.commit()

            return (
                True,
                f"Updated {pokemon} [{variant}] to {new_quantity}.",
            )

        conn.execute(
            """
            INSERT INTO pokemon_collection (
                collection_id,
                pokemon,
                variant,
                quantity,
                box
                , obtained_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                collection_id,
                pokemon,
                variant,
                quantity,
                str(box).strip() if box else None,
                datetime.now(timezone.utc).isoformat() if box else None,
            ),
        )

        conn.commit()

        return (
            True,
            f"Added {pokemon} [{variant}] x{quantity}.",
        )

    finally:
        conn.close()


def _update_collection_entry(
    entry_id,
    collection_id,
    pokemon,
    variant,
    quantity,
):
    pokemon = pokemon.strip()
    variant = variant.strip() or "Default"

    if not pokemon:
        return False, "Pokémon name cannot be empty."

    if quantity < 1:
        return False, "Quantity must be at least 1."

    conn = _connect()

    try:
        duplicate = conn.execute(
            """
            SELECT id
            FROM pokemon_collection
            WHERE collection_id = ?
              AND pokemon = ?
              AND variant = ?
              AND id != ?
            """,
            (
                collection_id,
                pokemon,
                variant,
                entry_id,
            ),
        ).fetchone()

        if duplicate:
            return (
                False,
                "That Pokémon and variant already exist in this collection.",
            )

        cursor = conn.execute(
            """
            UPDATE pokemon_collection
            SET pokemon = ?,
                variant = ?,
                quantity = ?
            WHERE id = ?
              AND collection_id = ?
            """,
            (
                pokemon,
                variant,
                quantity,
                entry_id,
                collection_id,
            ),
        )

        if cursor.rowcount == 0:
            return False, "Collection entry not found."

        conn.commit()

        return True, f"{pokemon} [{variant}] updated."

    finally:
        conn.close()


def _remove_collection_entry(entry_id, collection_id):
    conn = _connect()

    try:
        entry = conn.execute(
            """
            SELECT pokemon, variant
            FROM pokemon_collection
            WHERE id = ?
              AND collection_id = ?
            """,
            (
                entry_id,
                collection_id,
            ),
        ).fetchone()

        if not entry:
            return False, "Collection entry not found."

        conn.execute(
            """
            DELETE FROM pokemon_collection
            WHERE id = ?
              AND collection_id = ?
            """,
            (
                entry_id,
                collection_id,
            ),
        )

        conn.commit()

        return (
            True,
            f"Removed {entry[0]} [{entry[1]}].",
        )

    finally:
        conn.close()


def _get_collection_totals(collection_id):
    conn = _connect()

    try:
        total_quantity = conn.execute(
            """
            SELECT COALESCE(SUM(quantity), 0)
            FROM pokemon_collection
            WHERE collection_id = ?
            """,
            (collection_id,),
        ).fetchone()[0]

        unique_pokemon = conn.execute(
            """
            SELECT COUNT(DISTINCT LOWER(pokemon))
            FROM pokemon_collection
            WHERE collection_id = ?
            """,
            (collection_id,),
        ).fetchone()[0]

        total_entries = conn.execute(
            """
            SELECT COUNT(*)
            FROM pokemon_collection
            WHERE collection_id = ?
            """,
            (collection_id,),
        ).fetchone()[0]

        return (
            unique_pokemon,
            total_quantity,
            total_entries,
        )

    finally:
        conn.close()


# ============================================================================
# TERMINAL STYLING
# ============================================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

WIDTH = 72


def _clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def _pause():
    print()
    input(f"{DIM}Press ENTER to continue...{RESET}")


def _print_header(title, subtitle=None):
    print()
    print(f"{CYAN}{BOLD}{'═' * WIDTH}{RESET}")
    print(
        f"{CYAN}{BOLD}"
        f"{title.center(WIDTH)}"
        f"{RESET}"
    )
    print(f"{CYAN}{BOLD}{'═' * WIDTH}{RESET}")

    if subtitle:
        print(
            f"{DIM}"
            f"{subtitle.center(WIDTH)}"
            f"{RESET}"
        )

    print()


def _print_error(message):
    print(f"{RED}{BOLD}✖ {message}{RESET}")


def _print_success(message):
    print(f"{GREEN}{BOLD}✔ {message}{RESET}")


def _print_warning(message):
    print(f"{YELLOW}{BOLD}⚠ {message}{RESET}")


def _print_info(message):
    print(f"{BLUE}● {message}{RESET}")


def _print_divider():
    print(f"{DIM}{'─' * WIDTH}{RESET}")


def _print_menu_option(number, label, description=None):
    if description:
        print(
            f"  {CYAN}{BOLD}[{number}]{RESET} "
            f"{WHITE}{label:<24}{RESET}"
            f"{DIM}{description}{RESET}"
        )
    else:
        print(
            f"  {CYAN}{BOLD}[{number}]{RESET} "
            f"{WHITE}{label}{RESET}"
        )


# ============================================================================
# COLLECTION LIST
# ============================================================================

def _render_collection_list(user_id):
    collections = _get_collections(user_id)

    if not collections:
        print(
            f"{DIM}"
            f"No collections have been created yet."
            f"{RESET}"
        )
        return

    for index, (_, name) in enumerate(collections, 1):
        collection_id = collections[index - 1][0]
        unique_pokemon, total_quantity, total_entries = (
            _get_collection_totals(collection_id)
        )
        print(
            f"  {CYAN}{BOLD}[{index}]{RESET} "
            f"{WHITE}{name}{RESET} "
            f"{DIM}({unique_pokemon} Pokémon, "
            f"{total_entries} variants, "
            f"{total_quantity} total){RESET}"
        )


# ============================================================================
# CREATE COLLECTION
# ============================================================================

def _create_collection_menu(user_id):
    _clear_screen()

    _print_header(
        "CREATE COLLECTION",
        "Create a manual Pokémon collection log",
    )

    print(
        f"{DIM}"
        "Collections are completely independent of the Eclipse Pokémon database."
        f"{RESET}"
    )

    print()

    name = input(
        f"{CYAN}Collection name:{RESET} "
    ).strip()

    if not name:
        _print_error("Collection name cannot be empty.")
        _pause()
        return

    success, message = _create_collection(user_id, name)

    print()

    if success:
        _print_success(message)
    else:
        _print_error(message)

    _pause()


# ============================================================================
# MANAGE COLLECTIONS
# ============================================================================

def _manage_collections(user_id):
    while True:
        _clear_screen()

        _print_header(
            "MANAGE COLLECTIONS",
            "Create, rename, or delete your collection logs",
        )

        collections = _get_collections(user_id)

        if collections:
            print(f"{WHITE}{BOLD}YOUR COLLECTIONS{RESET}")
            print()

            for index, (_, name) in enumerate(collections, 1):
                collection_id = collections[index - 1][0]
                unique_pokemon, total_quantity, total_entries = (
                    _get_collection_totals(collection_id)
                )
                print(
                    f"  {CYAN}{BOLD}[{index}]{RESET} "
                    f"{WHITE}{name}{RESET} "
                    f"{DIM}({unique_pokemon} Pokémon, "
                    f"{total_entries} variants, "
                    f"{total_quantity} total){RESET}"
                )

            print()

        else:
            _print_info("You currently have no collections.")
            print()

        _print_divider()
        print()

        _print_menu_option(
            "1",
            "Create Collection",
            "Create a new collection",
        )

        _print_menu_option(
            "2",
            "Rename Collection",
            "Rename an existing collection",
        )

        _print_menu_option(
            "3",
            "Delete Collection",
            "Delete a collection and its entries",
        )

        _print_menu_option(
            "0",
            "Back",
            "Return to the collection menu",
        )

        print()

        choice = input(
            f"{CYAN}Select Option [0-3]:{RESET} "
        ).strip()

        if choice == "0":
            return

        if choice == "1":
            _create_collection_menu(user_id)
            continue

        if choice == "2":
            if not collections:
                _print_error("There are no collections to rename.")
                _pause()
                continue

            _clear_screen()

            _print_header("RENAME COLLECTION")

            for index, (_, name) in enumerate(collections, 1):
                print(
                    f"  {CYAN}{BOLD}[{index}]{RESET} "
                    f"{WHITE}{name}{RESET}"
                )

            print()

            selection = input(
                f"{CYAN}Select Collection:{RESET} "
            ).strip()

            try:
                index = int(selection)
                if index < 1 or index > len(collections):
                    raise ValueError

            except ValueError:
                _print_error("Invalid collection selection.")
                _pause()
                continue

            collection_id = collections[index - 1][0]
            old_name = collections[index - 1][1]

            new_name = input(
                f"{CYAN}New name for '{old_name}':{RESET} "
            ).strip()

            success, message = _rename_collection(
                collection_id,
                user_id,
                new_name,
            )

            print()

            if success:
                _print_success(message)
            else:
                _print_error(message)

            _pause()
            continue

        if choice == "3":
            if not collections:
                _print_error("There are no collections to delete.")
                _pause()
                continue

            _clear_screen()

            _print_header("DELETE COLLECTION")

            for index, (_, name) in enumerate(collections, 1):
                print(
                    f"  {CYAN}{BOLD}[{index}]{RESET} "
                    f"{WHITE}{name}{RESET}"
                )

            print()

            selection = input(
                f"{CYAN}Select Collection:{RESET} "
            ).strip()

            try:
                index = int(selection)

                if index < 1 or index > len(collections):
                    raise ValueError

            except ValueError:
                _print_error("Invalid collection selection.")
                _pause()
                continue

            collection_id = collections[index - 1][0]
            collection_name = collections[index - 1][1]

            print()

            _print_warning(
                f"This will permanently delete '{collection_name}' "
                "and every entry inside it."
            )

            confirm = input(
                f"{YELLOW}Type DELETE to confirm:{RESET} "
            ).strip()

            if confirm != "DELETE":
                _print_info("Deletion cancelled.")
                _pause()
                continue

            success, message = _delete_collection(
                collection_id,
                user_id,
            )

            print()

            if success:
                _print_success(message)
            else:
                _print_error(message)

            _pause()
            continue

        _print_error("Invalid option.")
        _pause()


# ============================================================================
# SELECT COLLECTION
# ============================================================================

def _select_collection(user_id, title="SELECT COLLECTION"):
    collections = _get_collections(user_id)

    if not collections:
        _clear_screen()

        _print_header(
            "SELECT COLLECTION",
            "Choose which collection to work with",
        )

        _print_warning(
            "You do not have any collections yet."
        )

        print()

        create = input(
            f"{CYAN}Create one now? [Y/N]:{RESET} "
        ).strip().lower()

        if create == "y":
            _create_collection_menu(user_id)

        return None

    _clear_screen()

    _print_header(
        title,
        "All collection operations apply only to the selected collection",
    )

    for index, (_, name) in enumerate(collections, 1):
        print(
            f"  {CYAN}{BOLD}[{index}]{RESET} "
            f"{WHITE}{name}{RESET}"
        )

    print()
    print(
        f"  {DIM}[0] Back{RESET}"
    )

    print()

    choice = input(
        f"{CYAN}Select Collection:{RESET} "
    ).strip()

    if choice == "0":
        return None

    try:
        index = int(choice)

        if index < 1 or index > len(collections):
            raise ValueError

    except ValueError:
        _print_error("Invalid collection selection.")
        _pause()
        return None

    return collections[index - 1]


# ============================================================================
# VIEW COLLECTION
# ============================================================================

def _view_collection(collection_id, collection_name, search=None, box=None):
    _clear_screen()

    title = f"COLLECTION: {collection_name}"

    if box:
        subtitle = f"Box: {box}"
    elif search:
        subtitle = f"Search results for: {search}"
    else:
        subtitle = "Manual Pokémon collection entries"

    _print_header(title, subtitle)

    entries = _get_collection_entries(
        collection_id,
        search,
        box,
    )

    unique_pokemon, total_quantity, total_entries = (
        _get_collection_totals(collection_id)
    )

    print(
        f"{CYAN}Unique Pokémon:{RESET} "
        f"{WHITE}{unique_pokemon}{RESET}"
        f"    "
        f"{CYAN}Total Quantity:{RESET} "
        f"{WHITE}{total_quantity}{RESET}"
        f"    "
        f"{CYAN}Entries:{RESET} "
        f"{WHITE}{total_entries}{RESET}"
    )

    print()

    if not entries:
        if search:
            _print_warning("No matching entries found.")
        else:
            _print_info(
                "This collection is empty. "
                "Use 'Add Pokémon' to begin tracking."
            )

        return

    _print_divider()

    print(
        f"{DIM}"
        f"{'#':<5}"
        f"{'POKÉMON':<28}"
        f"{'VARIANT':<25}"
        f"{'QTY':>8}"
        f"{RESET}"
    )

    _print_divider()

    for index, (_, pokemon, variant, quantity) in enumerate(
        entries,
        1,
    ):
        pokemon_display = pokemon[:26]
        variant_display = variant[:23]

        print(
            f"{CYAN}{index:<5}{RESET}"
            f"{WHITE}{pokemon_display:<28}{RESET}"
            f"{MAGENTA}{variant_display:<25}{RESET}"
            f"{YELLOW}{quantity:>8}{RESET}"
        )

    _print_divider()


# ============================================================================
# ADD POKÉMON
# ============================================================================

def _add_pokemon(collection_id):
    _clear_screen()

    _print_header(
        "ADD POKÉMON",
        "Manually add an entry to the selected collection",
    )

    print(
        f"{DIM}"
        "Enter the Pokémon exactly as you want it stored in your collection."
        f"{RESET}"
    )

    print()

    pokemon = input(
        f"{CYAN}Pokémon name:{RESET} "
    ).strip()

    if not pokemon:
        _print_error("Pokémon name cannot be empty.")
        _pause()
        return

    variant = input(
        f"{CYAN}Variant:{RESET} "
    ).strip()

    if not variant:
        variant = "Default"

    quantity_text = input(
        f"{CYAN}Quantity:{RESET} "
    ).strip()

    try:
        quantity = int(quantity_text)

        if quantity < 1:
            raise ValueError

    except ValueError:
        _print_error("Quantity must be a positive whole number.")
        _pause()
        return

    success, message = _add_collection_entry(
        collection_id,
        pokemon,
        variant,
        quantity,
    )

    print()

    if success:
        _print_success(message)
    else:
        _print_error(message)

    _pause()


# ============================================================================
# EDIT POKÉMON
# ============================================================================

def _edit_pokemon(collection_id):
    _clear_screen()

    _print_header(
        "EDIT POKÉMON",
        "Modify an existing manual collection entry",
    )

    entries = _get_collection_entries(collection_id)

    if not entries:
        _print_info("This collection is empty.")
        _pause()
        return

    for index, (_, pokemon, variant, quantity) in enumerate(
        entries,
        1,
    ):
        print(
            f"  {CYAN}{BOLD}[{index}]{RESET} "
            f"{WHITE}{pokemon}{RESET}"
            f" {MAGENTA}[{variant}]{RESET}"
            f" {YELLOW}x{quantity}{RESET}"
        )

    print()
    print(
        f"  {DIM}[0] Cancel{RESET}"
    )

    print()

    selection = input(
        f"{CYAN}Select Entry:{RESET} "
    ).strip()

    if selection == "0":
        return

    try:
        index = int(selection)

        if index < 1 or index > len(entries):
            raise ValueError

    except ValueError:
        _print_error("Invalid entry selection.")
        _pause()
        return

    entry_id, old_pokemon, old_variant, old_quantity = (
        entries[index - 1]
    )

    print()

    print(
        f"{DIM}"
        "Press ENTER to keep the current value."
        f"{RESET}"
    )

    print()

    pokemon = input(
        f"{CYAN}Pokémon name "
        f"{DIM}[{old_pokemon}]{RESET}{CYAN}:{RESET} "
    ).strip()

    if not pokemon:
        pokemon = old_pokemon

    variant = input(
        f"{CYAN}Variant "
        f"{DIM}[{old_variant}]{RESET}{CYAN}:{RESET} "
    ).strip()

    if not variant:
        variant = old_variant

    quantity_text = input(
        f"{CYAN}Quantity "
        f"{DIM}[{old_quantity}]{RESET}{CYAN}:{RESET} "
    ).strip()

    if quantity_text:
        try:
            quantity = int(quantity_text)

            if quantity < 1:
                raise ValueError

        except ValueError:
            _print_error(
                "Quantity must be a positive whole number."
            )
            _pause()
            return
    else:
        quantity = old_quantity

    success, message = _update_collection_entry(
        entry_id,
        collection_id,
        pokemon,
        variant,
        quantity,
    )

    print()

    if success:
        _print_success(message)
    else:
        _print_error(message)

    _pause()


# ============================================================================
# REMOVE POKÉMON
# ============================================================================

def _remove_pokemon(collection_id):
    _clear_screen()

    _print_header(
        "REMOVE POKÉMON",
        "Remove an entry from the selected collection",
    )

    entries = _get_collection_entries(collection_id)

    if not entries:
        _print_info("This collection is empty.")
        _pause()
        return

    for index, (_, pokemon, variant, quantity) in enumerate(
        entries,
        1,
    ):
        print(
            f"  {CYAN}{BOLD}[{index}]{RESET} "
            f"{WHITE}{pokemon}{RESET}"
            f" {MAGENTA}[{variant}]{RESET}"
            f" {YELLOW}x{quantity}{RESET}"
        )

    print()
    print(
        f"  {DIM}[0] Cancel{RESET}"
    )

    print()

    selection = input(
        f"{CYAN}Select Entry:{RESET} "
    ).strip()

    if selection == "0":
        return

    try:
        index = int(selection)

        if index < 1 or index > len(entries):
            raise ValueError

    except ValueError:
        _print_error("Invalid entry selection.")
        _pause()
        return

    entry_id, pokemon, variant, quantity = entries[index - 1]

    print()

    _print_warning(
        f"Remove {pokemon} [{variant}] x{quantity}?"
    )

    confirm = input(
        f"{YELLOW}Confirm [Y/N]:{RESET} "
    ).strip().lower()

    if confirm != "y":
        _print_info("Removal cancelled.")
        _pause()
        return

    success, message = _remove_collection_entry(
        entry_id,
        collection_id,
    )

    print()

    if success:
        _print_success(message)
    else:
        _print_error(message)

    _pause()


# ============================================================================
# SEARCH
# ============================================================================

def _search_collection(collection_id, collection_name):
    _clear_screen()

    _print_header(
        "SEARCH COLLECTION",
        f"Search only '{collection_name}'",
    )

    print(
        f"{DIM}"
        "Search checks the manually entered Pokémon and Variant fields only."
        f"{RESET}"
    )

    print()

    search = input(
        f"{CYAN}Search:{RESET} "
    ).strip()

    if not search:
        _print_error("Search cannot be empty.")
        _pause()
        return

    _view_collection(
        collection_id,
        collection_name,
        search,
    )

    _pause()


# ============================================================================
# STATISTICS
# ============================================================================

def _collection_statistics(collection_id, collection_name):
    _clear_screen()

    _print_header(
        "COLLECTION STATISTICS",
        collection_name,
    )

    unique_pokemon, total_quantity, total_entries = (
        _get_collection_totals(collection_id)
    )

    print(
        f"  {CYAN}{BOLD}Unique Pokémon{RESET}"
        f"      {WHITE}{unique_pokemon}{RESET}"
    )

    print(
        f"  {CYAN}{BOLD}Total Quantity{RESET}"
        f"      {YELLOW}{total_quantity}{RESET}"
    )

    print(
        f"  {CYAN}{BOLD}Total Entries{RESET}"
        f"       {WHITE}{total_entries}{RESET}"
    )

    print()

    _print_divider()

    entries = _get_collection_entries(collection_id)

    if entries:
        variant_totals = {}

        for _, _, variant, quantity in entries:
            key = variant.strip() or "Default"

            variant_totals[key] = (
                variant_totals.get(key, 0) + quantity
            )

        print()
        print(
            f"{WHITE}{BOLD}QUANTITY BY VARIANT{RESET}"
        )
        print()

        for variant, quantity in sorted(
            variant_totals.items(),
            key=lambda item: item[0].lower(),
        ):
            print(
                f"  {MAGENTA}{variant:<30}{RESET}"
                f"{YELLOW}{quantity:>8}{RESET}"
            )

    else:
        print()
        _print_info("No Pokémon have been added yet.")

    _pause()


# ============================================================================
# BOX COMPARISON AND SYNC
# ============================================================================

def _box_label(pokemon):
    """Return stable box metadata when a scraper supplies it."""
    value = (
        pokemon.get("box")
        or pokemon.get("box_number")
        or pokemon.get("box_name")
        or pokemon.get("page")
    )
    return str(value).strip() if value not in (None, "") else "Unassigned"


def _box_collection_key(pokemon, variant):
    normalized_variant = str(variant).strip() or "Default"
    if normalized_variant.casefold() == "normal":
        normalized_variant = "Default"

    return (
        str(pokemon).strip().casefold(),
        normalized_variant.casefold(),
    )


def _build_box_summary(box_pokemon):
    summary = {}

    for pokemon in box_pokemon:
        species = pokemon.get("species") or pokemon.get("name")
        variant = pokemon.get("display_category") or pokemon.get("variant")

        if not species:
            continue

        key = _box_collection_key(species, variant)
        display_variant = str(variant).strip() or "Default"
        if display_variant.casefold() == "normal":
            display_variant = "Default"
        summary[key] = {
            "pokemon": str(species).strip(),
            "variant": display_variant,
            "quantity": summary.get(key, {}).get("quantity", 0) + 1,
            "box": _box_label(pokemon),
        }

    return summary


def _filter_box_pokemon(box_pokemon, box=None):
    """Filter scraped box records without changing the scraper contract."""
    if not box:
        return list(box_pokemon or [])
    wanted = str(box).strip().casefold()
    return [
        pokemon for pokemon in (box_pokemon or [])
        if _box_label(pokemon).casefold() == wanted
    ]


def _compare_box_summaries(left, right):
    """Return entries unique to each box and entries present in both."""
    left = left or {}
    right = right or {}
    return {
        "left_only": [value for key, value in left.items() if key not in right],
        "right_only": [value for key, value in right.items() if key not in left],
        "shared": [value for key, value in left.items() if key in right],
    }


def _find_newly_obtained(box_pokemon, collection_entries):
    """Identify live-box entries absent from the manually tracked collection."""
    live = _build_box_summary(box_pokemon)
    tracked = {
        _box_collection_key(row[1], row[2]): row
        for row in (collection_entries or [])
    }
    return [value for key, value in live.items() if key not in tracked]


def _collection_export_data(collection_id, collection_name=None, box=None):
    entries = _get_collection_entries(collection_id, box=box, include_box=True)
    return [
        {
            "collection": collection_name,
            "pokemon": row[1],
            "variant": row[2],
            "quantity": row[3],
            "box": row[4] or "Unassigned",
            "obtained_at": row[5] if len(row) > 5 else None,
        }
        for row in entries
    ]


def _export_collection(collection_id, collection_name, path, fmt="json", box=None):
    """Export collection rows as JSON or CSV; returns the written path."""
    data = _collection_export_data(collection_id, collection_name, box)
    fmt = fmt.casefold()
    if fmt not in ("json", "csv"):
        raise ValueError("Format must be JSON or CSV.")
    if not path.lower().endswith("." + fmt):
        path += "." + fmt
    if fmt == "json":
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
    else:
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=data[0].keys() if data else
                                    ["collection", "pokemon", "variant", "quantity", "box"])
            writer.writeheader()
            writer.writerows(data)
    return path


def _get_collection_summary(collection_id):
    summary = {}

    for _, pokemon, variant, quantity in _get_collection_entries(collection_id):
        key = _box_collection_key(pokemon, variant)
        summary[key] = {
            "pokemon": pokemon,
            "variant": variant,
            "quantity": quantity,
        }

    return summary


def _box_collection_preview(driver, collection_id, collection_name):
    _clear_screen()
    _print_header(
        "BOX COLLECTION VIEW",
        f"{collection_name} | preview before sync",
    )

    print(f"{DIM}Reading all Pokémon from your live box...{RESET}")
    print()

    selected_box = input(
        f"{CYAN}Box filter (blank for all boxes):{RESET} "
    ).strip()
    box_pokemon = _filter_box_pokemon(
        fetch_all_box_pokemon(driver), selected_box
    )
    if not box_pokemon:
        _print_error("No Pokémon were found, or the box could not be loaded.")
        _pause()
        return

    box_summary = _build_box_summary(box_pokemon)
    collection_summary = _get_collection_summary(collection_id)
    box_only = [
        value for key, value in box_summary.items()
        if key not in collection_summary
    ]
    tracked = [
        value for key, value in box_summary.items()
        if key in collection_summary
    ]
    tracked_only = [
        value for key, value in collection_summary.items()
        if key not in box_summary
    ]

    print(f"{CYAN}{BOLD}BOX SUMMARY{RESET}")
    print(f"  Pokémon in box : {WHITE}{len(box_pokemon):,}{RESET}")
    print(f"  Unique entries : {WHITE}{len(box_summary):,}{RESET}")
    print(f"  Already tracked: {GREEN}{len(tracked):,}{RESET}")
    print(f"  New to import  : {YELLOW}{len(box_only):,}{RESET}")
    print(f"  Not in box     : {DIM}{len(tracked_only):,}{RESET}")

    if box_only:
        print()
        print(f"{YELLOW}{BOLD}BOX ENTRIES NOT IN COLLECTION{RESET}")
        for value in sorted(box_only, key=lambda item: (item["pokemon"].casefold(), item["variant"].casefold())):
            print(f"  {YELLOW}+{RESET} {value['pokemon']} [{value['variant']}] x{value['quantity']}")

    if tracked_only:
        print()
        print(f"{DIM}{BOLD}TRACKED ENTRIES NOT CURRENTLY IN BOX{RESET}")
        for value in sorted(tracked_only, key=lambda item: (item["pokemon"].casefold(), item["variant"].casefold())):
            print(f"  {DIM}- {value['pokemon']} [{value['variant']}] x{value['quantity']}{RESET}")

    if not box_only:
        print()
        _print_success("Your box is already represented in this collection.")
        _pause()
        return

    print()
    confirm = input(
        f"{YELLOW}Import the {len(box_only)} box-only entries? [y/N]:{RESET} "
    ).strip().lower()

    if confirm != "y":
        _print_info("Preview closed without changing the collection.")
        _pause()
        return

    imported = 0
    for value in box_only:
        success, _ = _add_collection_entry(
            collection_id,
            value["pokemon"],
            value["variant"],
            value["quantity"],
            value.get("box"),
        )
        if success:
            imported += 1

    print()
    _print_success(f"Imported {imported} new box entries into '{collection_name}'.")
    _pause()


def _compare_live_boxes(driver):
    _clear_screen()
    _print_header("COMPARE BOXES", "Compare two live box snapshots")
    first = fetch_all_box_pokemon(driver)
    second = fetch_all_box_pokemon(driver)
    comparison = _compare_box_summaries(
        _build_box_summary(first), _build_box_summary(second)
    )
    print(f"Only in first snapshot : {len(comparison['left_only'])}")
    print(f"Only in second snapshot: {len(comparison['right_only'])}")
    print(f"Shared entries         : {len(comparison['shared'])}")
    _pause()


def _export_collection_menu(collection_id, collection_name):
    _clear_screen()
    _print_header("EXPORT COLLECTION", collection_name)
    fmt = input(f"{CYAN}Format [json/csv]:{RESET} ").strip().lower()
    path = input(f"{CYAN}Output file:{RESET} ").strip()
    if not path:
        _print_error("Output file cannot be empty.")
    else:
        try:
            written = _export_collection(collection_id, collection_name, path, fmt)
            _print_success(f"Exported collection to {written}.")
        except (OSError, ValueError) as error:
            _print_error(str(error))
    _pause()


# ============================================================================
# SELECTED COLLECTION MENU
# ============================================================================

def _collection_menu(collection_id, collection_name, driver):
    while True:
        _clear_screen()

        unique_pokemon, total_quantity, total_entries = (
            _get_collection_totals(collection_id)
        )

        _print_header(
            f"COLLECTION: {collection_name}",
            "Manual Pokémon collection tracker",
        )

        print(
            f"  {CYAN}Unique Pokémon:{RESET} "
            f"{WHITE}{unique_pokemon}{RESET}"
            f"     "
            f"{CYAN}Total Qty:{RESET} "
            f"{YELLOW}{total_quantity}{RESET}"
            f"     "
            f"{CYAN}Entries:{RESET} "
            f"{WHITE}{total_entries}{RESET}"
        )

        print()

        _print_divider()

        print()

        _print_menu_option(
            "1",
            "View Collection",
            "Display every entry",
        )

        _print_menu_option(
            "2",
            "Add Pokémon",
            "Manually add Pokémon / variant / quantity",
        )

        _print_menu_option(
            "3",
            "Edit Pokémon",
            "Modify an existing entry",
        )

        _print_menu_option(
            "4",
            "Remove Pokémon",
            "Remove an existing entry",
        )

        _print_menu_option(
            "5",
            "Search Collection",
            "Search Pokémon and variants",
        )

        _print_menu_option(
            "6",
            "Statistics",
            "View collection totals",
        )

        _print_menu_option(
            "7",
            "View Box / Sync",
            "Preview live box differences and import safely",
        )
        _print_menu_option("8", "View by Box", "Filter entries by box label")
        _print_menu_option("9", "Compare Boxes", "Compare two live box snapshots")
        _print_menu_option("10", "Export Collection", "Write JSON or CSV")

        print()

        _print_divider()

        print()

        _print_menu_option(
            "0",
            "Back",
            "Return to collection selection",
        )

        print()

        choice = input(
            f"{CYAN}Select Option [0-10]:{RESET} "
        ).strip()

        if choice == "0":
            return

        if choice == "1":
            _view_collection(
                collection_id,
                collection_name,
            )
            _pause()
            continue

        if choice == "2":
            _add_pokemon(collection_id)
            continue

        if choice == "3":
            _edit_pokemon(collection_id)
            continue

        if choice == "4":
            _remove_pokemon(collection_id)
            continue

        if choice == "5":
            _search_collection(
                collection_id,
                collection_name,
            )
            continue

        if choice == "6":
            _collection_statistics(
                collection_id,
                collection_name,
            )
            continue

        if choice == "7":
            _box_collection_preview(
                driver,
                collection_id,
                collection_name,
            )
            continue

        if choice == "8":
            box = input(f"{CYAN}Box label:{RESET} ").strip()
            _view_collection(collection_id, collection_name, box=box)
            _pause()
            continue

        if choice == "9":
            _compare_live_boxes(driver)
            continue

        if choice == "10":
            _export_collection_menu(collection_id, collection_name)
            continue

        _print_error("Invalid option.")
        _pause()


# ============================================================================
# MAIN COLLECTION MENU
# ============================================================================

def collection_menu(driver=None, user_id=None):
    """
    Main entry point used by menus.main_menu.

    The collection tracker remains manual by default; option 7 can compare
    it with the live box and perform an explicit additive import.
    """

    _initialize_database()

    resolved_user_id = _get_user_id(user_id)

    while True:
        _clear_screen()

        collections = _get_collections(resolved_user_id)

        _print_header(
            "POKÉMON COLLECTIONS",
            "Manual collection tracking",
        )

        print(
            f"{DIM}"
            "Track your Pokémon manually using separate collection logs."
            f"{RESET}"
        )

        print()

        if collections:
            print(
                f"{WHITE}{BOLD}YOUR COLLECTIONS{RESET}"
            )

            print()

            for index, (_, name) in enumerate(
                collections,
                1,
            ):
                unique_pokemon, total_quantity, total_entries = (
                    _get_collection_totals(
                        collections[index - 1][0]
                    )
                )

                print(
                    f"  {CYAN}{BOLD}[{index}]{RESET} "
                    f"{WHITE}{name:<30}{RESET}"
                    f"{DIM}"
                    f"  {unique_pokemon} Pokémon"
                    f"  |  {total_quantity} total"
                    f"  |  {total_entries} entries"
                    f"{RESET}"
                )

            print()

        else:
            print(
                f"{DIM}"
                "No collection logs exist yet."
                f"{RESET}"
            )

            print()

        _print_divider()

        print()

        _print_menu_option(
            "1",
            "Open Collection",
            "Select a collection to manage",
        )

        _print_menu_option(
            "2",
            "Create Collection",
            "Create a new named collection",
        )

        _print_menu_option(
            "3",
            "Manage Collections",
            "Rename or delete collections",
        )

        print()

        _print_menu_option(
            "0",
            "Back",
            "Return to the main menu",
        )

        print()

        choice = input(
            f"{CYAN}Select Option [0-3]:{RESET} "
        ).strip()

        if choice == "0":
            return

        if choice == "1":
            selected = _select_collection(
                resolved_user_id,
                "OPEN COLLECTION",
            )

            if selected:
                collection_id, collection_name = selected

                _collection_menu(
                    collection_id,
                    collection_name,
                    driver,
                )

            continue

        if choice == "2":
            _create_collection_menu(
                resolved_user_id
            )
            continue

        if choice == "3":
            _manage_collections(
                resolved_user_id
            )
            continue

        _print_error("Invalid option.")
        _pause()