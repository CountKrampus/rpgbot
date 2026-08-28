import sqlite3
import re
import os


DB_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "eclipse_maps.db"
)


# ============================================================
# NORMALIZE
# ============================================================

def normalize(value):
    if not value:
        return ""

    return re.sub(
        r"[^a-z0-9]+",
        "",
        str(value).lower()
    )


# ============================================================
# DATABASE
# ============================================================

def connect():
    return sqlite3.connect(
        DB_FILE
    )


# ============================================================
# SEARCH POKEMON
# ============================================================

def search_pokemon(
    query,
    include_locked=True
):
    wanted = normalize(query)

    if not wanted:
        return []

    conn = connect()

    try:
        rows = conn.execute(
            """
            SELECT
                maps.area_id,
                maps.info_id,
                maps.name,
                maps.map_type,
                maps.unlocked,
                pokemon.name,
                pokemon.species_param,
                pokemon.dexed,
                pokemon.icon_name

            FROM pokemon

            JOIN maps
                ON maps.id = pokemon.map_id

            ORDER BY
                maps.map_type,
                maps.area_id,
                pokemon.name
            """
        ).fetchall()

        results = []

        for row in rows:
            (
                area_id,
                info_id,
                map_name,
                map_type,
                unlocked,
                pokemon_name,
                species_param,
                dexed,
                icon_name,
            ) = row

            name_normalized = normalize(
                pokemon_name
            )

            species_normalized = normalize(
                species_param
            )

            if (
                wanted in name_normalized
                or wanted in species_normalized
            ):
                results.append(
                    {
                        "area_id": area_id,
                        "info_id": info_id,
                        "map_name": map_name,
                        "map_type": map_type,

                        # Kept for compatibility with existing code.
                        # DO NOT use this for live access decisions.
                        "unlocked": bool(unlocked),

                        "name": pokemon_name,
                        "species_param": species_param,
                        "dexed": bool(dexed),
                        "icon_name": icon_name,
                    }
                )

        return results

    finally:
        conn.close()


# ============================================================
# HUNT
# ============================================================

def hunt_pokemon(
    query
):

    results = search_pokemon(
        query,
        include_locked=True
    )

    print()
    print("=" * 60)
    print(
        f"HUNT RESULTS: {query}"
    )
    print("=" * 60)

    if not results:

        print()
        print(
            f"No database matches found "
            f"for '{query}'."
        )

        return []

    current_map = None

    for result in results:

        map_name = result[
            "map_name"
        ]

        if map_name != current_map:

            current_map = map_name

            print()
            print(
                f"📍 {map_name}"
            )

            print(
                f"   area_id: "
                f"{result['area_id']}"
            )

            print(
                f"   info_id: "
                f"{result['info_id']}"
            )

            print(
                f"   type: "
                f"{result['map_type']}"
            )

            if result["unlocked"]:

                print(
                    "   🔓 Unlocked"
                )

            else:

                print(
                    "   🔒 Not currently unlocked"
                )

        print(
            f"      • {result['name']}"
        )

        if result[
            "species_param"
        ]:

            print(
                f"        "
                f"species="
                f"{result['species_param']}"
            )

    print()
    print(
        f"Total matches: "
        f"{len(results)}"
    )

    return results


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    query = input(
        "Pokémon to hunt: "
    ).strip()

    hunt_pokemon(
        query
    )