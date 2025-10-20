# Kommentarer: Svenska.
# Kod: Engelska.
# Cykel 5 i mitt Cykelprojekt (Github repo = space_bridge)

# ÖVERSIKT vad sql_sink.py gör:
# Skapar eller öppnar en liten SQLite databas. space_bridge.db
# Ser till att två tabeller finns.
# planet_counts(planet PRIMARY KEY, count, updated_at)
# counts_enriched(planet PRIMARY KEY, count, share, updated_at)

# laddar in: data/planet_counts.json -> planet_counts (UPSERT per planet)
# laddar in: data/counts_enriched.csv -> counts_enriched (UPSERT per planet)

# BLOCK 1
import sqlite3  # Pythons inbyggda SQLite klient
from pathlib import Path  # Filväg som är robust
import json  # läsa in artefakt
import csv  # läsa in artefakt
from datetime import datetime  # datum/tid för "senast uppdaterad"

SCHEMA = """
CREATE TABLE IF NOT EXISTS planet_counts (
  planet TEXT PRIMARY KEY,
  count  INTEGER NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS counts_enriched (
  planet TEXT PRIMARY KEY,
  count  INTEGER NOT NULL,
  share  REAL NOT NULL,
  updated_at TEXT NOT NULL
);
"""
# VIKTIGT: PRIMARY KEY på planet → varje planet max en rad.
# Det gör UPSERT naturligt: om den finns, uppdatera; annars skapa.

# BLOCK 2 init_db


def init_db(db_path: str, debug: bool = False) -> sqlite3.Connection:
    # 1) Säkerställ att mappen finns
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # 2) Öppna en (1) connection mot rätt fil
    conn = sqlite3.connect(db_path)

    # 3) Slå på WAL för denna DB-fil (per connection); läs tillbaka för att vara säker
    mode = conn.execute("PRAGMA journal_mode=WAL;").fetchone()[0]
    if debug:
        print("journal_mode:", mode)  # ska vara 'wal' om allt lirat

    # 4) Kör vårt schema (idempotent)
    conn.executescript(SCHEMA)

    # 5) (Valfritt) visa vilken fil som är 'main' i just DENNA connection
    if debug:
        dbs = conn.execute("PRAGMA database_list;").fetchall()
        print("database_list:", dbs)
    return conn


def upsert_counts(conn: sqlite3.Connection, counts_json_path: str) -> int:
    with open(counts_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # dict[planet]=count

    now = datetime.utcnow().isoformat(timespec="seconds")
    cur = conn.cursor()
    n = 0
    for planet, cnt in data.items():
        cur.execute(
            """
            INSERT INTO planet_counts(planet, count, updated_at)
            VALUES(?, ?, ?)
            ON CONFLICT(planet) DO UPDATE SET
              count=excluded.count,
              updated_at=excluded.updated_at
            """,
            (planet, int(cnt), now),
        )
        n += 1
    conn.commit()
    return n


if __name__ == "__main__":
    c = sqlite3.connect("data/space_bridge.db")
    print(c.execute("PRAGMA journal_mode;").fetchone())
    c.close()
