import sqlite3

conn = sqlite3.connect("eclipse_maps.db")

print("POKEMON TABLE COLUMNS:")
print(conn.execute("PRAGMA table_info(pokemon)").fetchall())

print()
print("GASTLY ENTRIES:")

rows = conn.execute(
    """
    SELECT *
    FROM pokemon
    WHERE LOWER(name) = LOWER(?)
    """,
    ("Gastly",)
).fetchall()

for row in rows:
    print(row)

conn.close()

input("\nPress Enter to close...")