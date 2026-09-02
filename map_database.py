"""
SQLite database for Eclipse RPG map / Pokémon data.

The database stores:
    - Maps
    - Map detail URLs
    - Pokémon display names
    - Internal species parameters
    - Whether the Pokémon is dexed
    - Last time the map was scanned

The database file is created automatically:
    eclipse_maps.db
"""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "eclipse_maps.db"


def get_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create the database tables and indexes."""
    conn = get_connection()

    try:
        conn.executescript(
            """
            PRAGMA journal_mode = WAL;

            CREATE TABLE IF NOT EXISTS maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                map_url TEXT,
                detail_url TEXT,
                exclusive INTEGER NOT NULL DEFAULT 0,
                area_id INTEGER,
                last_scanned TEXT
            );

            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                species_param TEXT,
                normalized_species_param TEXT,
                dexed INTEGER NOT NULL DEFAULT 0,
                UNIQUE(name, species_param)
            );

            CREATE TABLE IF NOT EXISTS map_pokemon (
                map_id INTEGER NOT NULL,
                pokemon_id INTEGER NOT NULL,
                first_seen TEXT,
                last_seen TEXT,
                PRIMARY KEY(map_id, pokemon_id),
                FOREIGN KEY(map_id) REFERENCES maps(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(pokemon_id) REFERENCES pokemon(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_pokemon_name
                ON pokemon(normalized_name);

            CREATE INDEX IF NOT EXISTS idx_pokemon_species
                ON pokemon(normalized_species_param);

            CREATE INDEX IF NOT EXISTS idx_map_pokemon_pokemon
                ON map_pokemon(pokemon_id);

            CREATE INDEX IF NOT EXISTS idx_maps_name
                ON maps(name);
            """
        )

        conn.commit()

    finally:
        conn.close()


def normalize(value):
    """Normalize a Pokémon name for searching."""
    if not value:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace("'", "")
        .replace("’", "")
    )


def upsert_map(
    name,
    map_url=None,
    detail_url=None,
    exclusive=False,
    area_id=None,
):
    """Insert or update a map."""
    initialize_database()

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO maps (
                name,
                map_url,
                detail_url,
                exclusive,
                area_id
            )
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(name)
            DO UPDATE SET
                map_url = COALESCE(
                    excluded.map_url,
                    maps.map_url
                ),
                detail_url = COALESCE(
                    excluded.detail_url,
                    maps.detail_url
                ),
                exclusive = excluded.exclusive,
                area_id = excluded.area_id
            """,
            (
                name,
                map_url,
                detail_url,
                int(exclusive),
                area_id,
            ),
        )

        conn.commit()

        row = conn.execute(
            "SELECT id FROM maps WHERE name = ?",
            (name,),
        ).fetchone()

        return row["id"]

    finally:
        conn.close()


def upsert_pokemon(
    name,
    species_param="",
    dexed=False,
):
    """Insert or update a Pokémon."""
    initialize_database()

    normalized_name = normalize(name)
    normalized_species = normalize(species_param)

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO pokemon (
                name,
                normalized_name,
                species_param,
                normalized_species_param,
                dexed
            )
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(name, species_param)
            DO UPDATE SET
                normalized_name =
                    excluded.normalized_name,
                normalized_species_param =
                    excluded.normalized_species_param,
                dexed =
                    MAX(
                        pokemon.dexed,
                        excluded.dexed
                    )
            """,
            (
                name,
                normalized_name,
                species_param,
                normalized_species,
                int(dexed),
            ),
        )

        conn.commit()

        row = conn.execute(
            """
            SELECT id
            FROM pokemon
            WHERE name = ?
              AND species_param = ?
            """,
            (
                name,
                species_param,
            ),
        ).fetchone()

        return row["id"]

    finally:
        conn.close()


def link_map_pokemon(
    map_id,
    pokemon_id,
    timestamp,
):
    """Associate a Pokémon with a map."""
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO map_pokemon (
                map_id,
                pokemon_id,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(map_id, pokemon_id)
            DO UPDATE SET
                last_seen = excluded.last_seen
            """,
            (
                map_id,
                pokemon_id,
                timestamp,
                timestamp,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def replace_map_pokemon(
    map_id,
    pokemon_list,
    timestamp,
):
    """
    Replace all Pokémon currently associated
    with a map.

    This is useful when refreshing a map because
    Pokémon can potentially be added or removed.
    """

    conn = get_connection()

    try:
        for pokemon in pokemon_list:

            name = (
                pokemon.get("name", "")
                .strip()
            )

            species_param = (
                pokemon.get(
                    "species_param",
                    "",
                )
                .strip()
            )

            if not name:
                continue

            normalized_name = normalize(name)
            normalized_species = normalize(
                species_param
            )

            dexed = bool(
                pokemon.get("dexed", False)
            )

            conn.execute(
                """
                INSERT INTO pokemon (
                    name,
                    normalized_name,
                    species_param,
                    normalized_species_param,
                    dexed
                )
                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(name, species_param)
                DO UPDATE SET
                    dexed = MAX(
                        pokemon.dexed,
                        excluded.dexed
                    )
                """,
                (
                    name,
                    normalized_name,
                    species_param,
                    normalized_species,
                    int(dexed),
                ),
            )

            pokemon_row = conn.execute(
                """
                SELECT id
                FROM pokemon
                WHERE name = ?
                  AND species_param = ?
                """,
                (
                    name,
                    species_param,
                ),
            ).fetchone()

            pokemon_id = pokemon_row["id"]

            conn.execute(
                """
                INSERT INTO map_pokemon (
                    map_id,
                    pokemon_id,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT(map_id, pokemon_id)
                DO UPDATE SET
                    last_seen = excluded.last_seen
                """,
                (
                    map_id,
                    pokemon_id,
                    timestamp,
                    timestamp,
                ),
            )

        conn.execute(
            """
            UPDATE maps
            SET last_scanned = ?
            WHERE id = ?
            """,
            (
                timestamp,
                map_id,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def search_pokemon(query):
    """
    Search the database for a Pokémon.

    Searches BOTH:
        display name
        internal species parameter
    """

    wanted = normalize(query)

    if not wanted:
        return []

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                maps.name AS map_name,
                maps.detail_url,
                maps.exclusive,
                pokemon.name,
                pokemon.species_param,
                pokemon.dexed
            FROM map_pokemon
            JOIN maps
                ON maps.id = map_pokemon.map_id
            JOIN pokemon
                ON pokemon.id = map_pokemon.pokemon_id
            WHERE
                pokemon.normalized_name LIKE ?
                OR pokemon.normalized_species_param LIKE ?
            ORDER BY maps.name, pokemon.name
            """,
            (
                f"%{wanted}%",
                f"%{wanted}%",
            ),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_all_maps():
    """Return every map stored in the database."""
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT *
            FROM maps
            ORDER BY name
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_map_pokemon(map_name):
    """Return Pokémon recorded for a specific map."""
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                pokemon.name,
                pokemon.species_param,
                pokemon.dexed
            FROM map_pokemon
            JOIN maps
                ON maps.id = map_pokemon.map_id
            JOIN pokemon
                ON pokemon.id = map_pokemon.pokemon_id
            WHERE maps.name = ?
            ORDER BY pokemon.name
            """,
            (map_name,),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


if __name__ == "__main__":

    initialize_database()

    print()
    print("=" * 60)
    print("ECLIPSE MAP DATABASE")
    print("=" * 60)
    print()
    print(f"Database: {DB_PATH}")
    print()
    print("Database initialized successfully.")
    print()