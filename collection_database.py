"""
Pokemon Collection Database

Separate SQLite database for manually tracking Pokemon collections.

Database:
    pokemon_collections.db

This database is intentionally independent from eclipse_maps.db.

The collection system stores:
    - Users/accounts
    - Named collection logs
    - Pokemon master list
    - Pokemon entries within each collection

No Selenium, web requests, or automation are used here.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

DB_FILE = Path(__file__).resolve().parent / "eclipse_maps.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect() -> sqlite3.Connection:
    """
    Open a connection to the Pokemon collection database.

    The database is automatically created if it does not exist.
    """

    connection = sqlite3.connect(DB_FILE)

    # Return rows that can be accessed by column name.
    connection.row_factory = sqlite3.Row

    # Make SQLite enforce foreign-key relationships.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database() -> None:
    """
    Create the collection database and required tables.

    Safe to call every time the application starts.
    Existing data is preserved.
    """

    with connect() as connection:

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS collection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                UNIQUE(user_id, name)
            );

            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                national_dex INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS pokemon_collection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                collection_id INTEGER NOT NULL,
                pokemon_id INTEGER NOT NULL,

                variant TEXT NOT NULL,

                quantity INTEGER NOT NULL DEFAULT 1
                    CHECK(quantity > 0),

                FOREIGN KEY(collection_id)
                    REFERENCES collection_logs(id)
                    ON DELETE CASCADE,

                FOREIGN KEY(pokemon_id)
                    REFERENCES pokemon(id)
                    ON DELETE CASCADE,

                UNIQUE(collection_id, pokemon_id, variant)
            );
            """
        )

        connection.commit()


# ============================================================
# COLLECTION LOGS
# ============================================================

def create_collection(user_id: str, name: str) -> int:
    """
    Create a new collection for a user.

    Returns:
        The newly created collection ID.

    Raises:
        ValueError if the name is empty or already exists.
    """

    user_id = str(user_id).strip()
    name = str(name).strip()

    if not user_id:
        raise ValueError("User ID cannot be empty.")

    if not name:
        raise ValueError("Collection name cannot be empty.")

    with connect() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO collection_logs (user_id, name)
                VALUES (?, ?)
                """,
                (user_id, name),
            )

            connection.commit()

            return cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError(
                f"A collection named '{name}' already exists."
            )


def get_collections(user_id: str) -> list[sqlite3.Row]:
    """
    Return all collections belonging to a user.
    """

    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT
                id,
                user_id,
                name
            FROM collection_logs
            WHERE user_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            (str(user_id),),
        )

        return cursor.fetchall()


def get_collection(
    collection_id: int,
    user_id: Optional[str] = None,
) -> Optional[sqlite3.Row]:
    """
    Get one collection.

    If user_id is supplied, the collection must belong to that user.
    """

    with connect() as connection:

        if user_id is None:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    user_id,
                    name
                FROM collection_logs
                WHERE id = ?
                """,
                (collection_id,),
            )
        else:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    user_id,
                    name
                FROM collection_logs
                WHERE id = ?
                  AND user_id = ?
                """,
                (collection_id, str(user_id)),
            )

        return cursor.fetchone()


def rename_collection(
    collection_id: int,
    user_id: str,
    new_name: str,
) -> bool:
    """
    Rename an existing collection.

    Returns:
        True if renamed successfully.
        False if the collection does not exist.

    Raises:
        ValueError if the new name is empty or already exists.
    """

    new_name = str(new_name).strip()

    if not new_name:
        raise ValueError("Collection name cannot be empty.")

    with connect() as connection:

        existing = connection.execute(
            """
            SELECT id
            FROM collection_logs
            WHERE user_id = ?
              AND name = ?
              AND id != ?
            """,
            (str(user_id), new_name, collection_id),
        ).fetchone()

        if existing:
            raise ValueError(
                f"A collection named '{new_name}' already exists."
            )

        cursor = connection.execute(
            """
            UPDATE collection_logs
            SET name = ?
            WHERE id = ?
              AND user_id = ?
            """,
            (new_name, collection_id, str(user_id)),
        )

        connection.commit()

        return cursor.rowcount > 0


def delete_collection(
    collection_id: int,
    user_id: str,
) -> bool:
    """
    Delete a collection and all Pokemon entries inside it.

    Returns:
        True if deleted.
        False if the collection does not exist.
    """

    with connect() as connection:

        cursor = connection.execute(
            """
            DELETE FROM collection_logs
            WHERE id = ?
              AND user_id = ?
            """,
            (collection_id, str(user_id)),
        )

        connection.commit()

        return cursor.rowcount > 0


# ============================================================
# POKEMON MASTER LIST
# ============================================================

def add_pokemon(
    national_dex: int,
    name: str,
) -> int:
    """
    Add a Pokemon to the local master list.

    This does NOT add it to a collection.

    Returns:
        Pokemon ID.
    """

    name = str(name).strip()

    if national_dex <= 0:
        raise ValueError("National Dex number must be positive.")

    if not name:
        raise ValueError("Pokemon name cannot be empty.")

    with connect() as connection:

        existing = connection.execute(
            """
            SELECT id
            FROM pokemon
            WHERE national_dex = ?
            """,
            (national_dex,),
        ).fetchone()

        if existing:
            return existing["id"]

        try:
            cursor = connection.execute(
                """
                INSERT INTO pokemon (
                    national_dex,
                    name
                )
                VALUES (?, ?)
                """,
                (national_dex, name),
            )

            connection.commit()

            return cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError(
                f"Pokemon '{name}' or Dex #{national_dex} already exists."
            )


def get_pokemon_by_id(pokemon_id: int) -> Optional[sqlite3.Row]:
    """
    Get a Pokemon by database ID.
    """

    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT
                id,
                national_dex,
                name
            FROM pokemon
            WHERE id = ?
            """,
            (pokemon_id,),
        )

        return cursor.fetchone()


def get_pokemon_by_dex(
    national_dex: int,
) -> Optional[sqlite3.Row]:
    """
    Get a Pokemon by National Dex number.
    """

    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT
                id,
                national_dex,
                name
            FROM pokemon
            WHERE national_dex = ?
            """,
            (national_dex,),
        )

        return cursor.fetchone()


def search_pokemon(search_term: str) -> list[sqlite3.Row]:
    """
    Search the local Pokemon list by name or National Dex number.
    """

    search_term = str(search_term).strip()

    if not search_term:
        return []

    with connect() as connection:

        like_term = f"%{search_term}%"

        cursor = connection.execute(
            """
            SELECT
                id,
                national_dex,
                name
            FROM pokemon
            WHERE name LIKE ? COLLATE NOCASE
               OR CAST(national_dex AS TEXT) LIKE ?
            ORDER BY national_dex
            """,
            (like_term, like_term),
        )

        return cursor.fetchall()


def get_all_pokemon() -> list[sqlite3.Row]:
    """
    Return the entire local Pokemon master list.
    """

    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT
                id,
                national_dex,
                name
            FROM pokemon
            ORDER BY national_dex
            """
        )

        return cursor.fetchall()


# ============================================================
# COLLECTION ENTRIES
# ============================================================

def add_to_collection(
    collection_id: int,
    pokemon_id: int,
    variant: str,
    quantity: int = 1,
) -> int:
    """
    Add a Pokemon to a collection.

    If the same Pokemon + variant already exists,
    its quantity is increased.

    Returns:
        Collection entry ID.
    """

    variant = str(variant).strip()

    if not variant:
        raise ValueError("Variant is required.")

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        raise ValueError("Quantity must be a whole number.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    with connect() as connection:

        # Make sure the collection exists.
        collection = connection.execute(
            """
            SELECT id
            FROM collection_logs
            WHERE id = ?
            """,
            (collection_id,),
        ).fetchone()

        if not collection:
            raise ValueError("Collection does not exist.")

        # Make sure the Pokemon exists.
        pokemon = connection.execute(
            """
            SELECT id
            FROM pokemon
            WHERE id = ?
            """,
            (pokemon_id,),
        ).fetchone()

        if not pokemon:
            raise ValueError("Pokemon does not exist.")

        existing = connection.execute(
            """
            SELECT id
            FROM pokemon_collection
            WHERE collection_id = ?
              AND pokemon_id = ?
              AND variant = ?
            """,
            (
                collection_id,
                pokemon_id,
                variant,
            ),
        ).fetchone()

        if existing:

            connection.execute(
                """
                UPDATE pokemon_collection
                SET quantity = quantity + ?
                WHERE id = ?
                """,
                (
                    quantity,
                    existing["id"],
                ),
            )

            connection.commit()

            return existing["id"]

        cursor = connection.execute(
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
                quantity,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def update_collection_entry(
    entry_id: int,
    collection_id: int,
    variant: str,
    quantity: int,
) -> bool:
    """
    Update an existing collection entry.

    Returns:
        True if updated.
        False if the entry does not exist.
    """

    variant = str(variant).strip()

    if not variant:
        raise ValueError("Variant is required.")

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        raise ValueError("Quantity must be a whole number.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    with connect() as connection:

        try:
            cursor = connection.execute(
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
                    collection_id,
                ),
            )

            connection.commit()

            return cursor.rowcount > 0

        except sqlite3.IntegrityError:
            raise ValueError(
                "That Pokemon and variant already exists in this collection."
            )


def remove_from_collection(
    entry_id: int,
    collection_id: int,
) -> bool:
    """
    Remove one Pokemon entry from a collection.
    """

    with connect() as connection:

        cursor = connection.execute(
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

        connection.commit()

        return cursor.rowcount > 0


def get_collection_entries(
    collection_id: int,
) -> list[sqlite3.Row]:
    """
    Return only the Pokemon connected to the specified collection.
    """

    with connect() as connection:

        cursor = connection.execute(
            """
            SELECT
                pc.id,
                pc.collection_id,
                pc.pokemon_id,
                p.national_dex,
                p.name,
                pc.variant,
                pc.quantity
            FROM pokemon_collection pc
            INNER JOIN pokemon p
                ON p.id = pc.pokemon_id
            WHERE pc.collection_id = ?
            ORDER BY
                p.national_dex,
                p.name COLLATE NOCASE,
                pc.variant COLLATE NOCASE
            """,
            (collection_id,),
        )

        return cursor.fetchall()


def search_collection(
    collection_id: int,
    search_term: str,
) -> list[sqlite3.Row]:
    """
    Search only within one collection.
    """

    search_term = str(search_term).strip()

    if not search_term:
        return []

    like_term = f"%{search_term}%"

    with connect() as connection:

        cursor = connection.execute(
            """
            SELECT
                pc.id,
                pc.collection_id,
                pc.pokemon_id,
                p.national_dex,
                p.name,
                pc.variant,
                pc.quantity
            FROM pokemon_collection pc
            INNER JOIN pokemon p
                ON p.id = pc.pokemon_id
            WHERE pc.collection_id = ?
              AND (
                    p.name LIKE ? COLLATE NOCASE
                    OR CAST(p.national_dex AS TEXT) LIKE ?
                    OR pc.variant LIKE ? COLLATE NOCASE
              )
            ORDER BY
                p.national_dex,
                p.name COLLATE NOCASE,
                pc.variant COLLATE NOCASE
            """,
            (
                collection_id,
                like_term,
                like_term,
                like_term,
            ),
        )

        return cursor.fetchall()


# ============================================================
# COLLECTION STATISTICS
# ============================================================

def get_collection_stats(
    collection_id: int,
) -> dict:
    """
    Return basic statistics for one collection.
    """

    with connect() as connection:

        result = connection.execute(
            """
            SELECT
                COUNT(*) AS unique_entries,
                COUNT(DISTINCT pokemon_id) AS unique_pokemon,
                COALESCE(SUM(quantity), 0) AS total_quantity
            FROM pokemon_collection
            WHERE collection_id = ?
            """,
            (collection_id,),
        ).fetchone()

        return {
            "unique_entries": result["unique_entries"],
            "unique_pokemon": result["unique_pokemon"],
            "total_quantity": result["total_quantity"],
        }


# ============================================================
# DATABASE MAINTENANCE
# ============================================================

def clear_collection(
    collection_id: int,
) -> bool:
    """
    Remove every Pokemon from a collection without deleting
    the collection itself.

    Returns:
        True if the collection exists.
    """

    with connect() as connection:

        exists = connection.execute(
            """
            SELECT id
            FROM collection_logs
            WHERE id = ?
            """,
            (collection_id,),
        ).fetchone()

        if not exists:
            return False

        connection.execute(
            """
            DELETE FROM pokemon_collection
            WHERE collection_id = ?
            """,
            (collection_id,),
        )

        connection.commit()

        return True


# ============================================================
# STARTUP
# ============================================================

# Automatically create the database/tables when this module
# is imported.
initialize_database()