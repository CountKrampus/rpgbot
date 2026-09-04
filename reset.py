import sqlite3

conn = sqlite3.connect("eclipse_maps.db")

conn.execute("PRAGMA foreign_keys = ON")

conn.execute(
    "DROP TABLE IF EXISTS pokemon_collection"
)

conn.execute(
    "DROP TABLE IF EXISTS collection_logs"
)

conn.commit()
conn.close()

print("Collection tables successfully reset.")