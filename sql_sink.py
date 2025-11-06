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
from datetime import datetime, UTC  # datum/tid för "senast uppdaterad"

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
# VIKTIGT: PRIMARY KEY på planet -> varje planet max en rad.
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

# BLOCK 3 upsert_counts


def upsert_counts(conn: sqlite3.Connection, counts_json_path: str) -> int:
    with open(counts_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # dict[planet]=count

    now = datetime.now(UTC).isoformat(timespec="seconds")
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

# BLOCK 4 upsert_enriched CSV -> DB


def upsert_enriched(conn: sqlite3.Connection, enriched_csv_path: str) -> int:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    cur = conn.cursor()
    n = 0
    with open(enriched_csv_path, "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        header = next(r, None)
        assert header == ["planet", "count", "share"], f"bad header: {header}"
        for planet, cnt, share in r:
            cur.execute(
                """
                INSERT INTO counts_enriched(planet, count, share, updated_at)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(planet) DO UPDATE SET
                  count=excluded.count,
                  share=excluded.share,
                  updated_at=excluded.updated_at
                """,
                (planet, int(cnt), float(share), now),
            )
            n += 1
    conn.commit()
    return n

# BLOCK 5: quick_checks


def quick_checks(conn: sqlite3.Connection, top: int = 3) -> dict[str, float | int | list[tuple[str, int]]]:
    cur = conn.cursor()
    cur.execute(
        "SELECT planet, count FROM planet_counts ORDER BY count DESC LIMIT ?;", (int(top),))
    topn = cur.fetchall()
    cur.execute("SELECT ROUND(SUM(share), 6) FROM counts_enriched;")
    share_sum = cur.fetchone()[0] or 0.0
    return {"top": topn, "share_sum": float(share_sum)}

# BLOCK 6: run() med mini QA-grind


def run(db_path="data/space_bridge.db",
        counts_json="data/planet_counts.json",
        enriched_csv="data/counts_enriched.csv",
        top: int = 3,
        max_share_sum: float = 1.000001) -> dict[str, float | int | list[tuple[str, int]]]:
    conn = init_db(db_path)
    try:
        n1 = upsert_counts(conn, counts_json)
        n2 = upsert_enriched(conn, enriched_csv)
        qc = quick_checks(conn, top=top)
    finally:
        conn.close()

    # mini-QA: Shares ska inte "spränga" 1.0, lite slack för float
    assert qc["share_sum"] <= max_share_sum, f"share_sum too high: {qc['share_sum']}"
    return {"db": db_path, "counts_rows": n1, "enriched_rows": n2, **qc}

# Block 7: Wrapper


def run_from_config(config_path="config.json") -> dict:
    c = load_config(config_path)
    return run(db_path=c["db"],
               counts_json=c["counts_json"],
               enriched_csv=c["enriched_csv"],
               top=int(c.get("top", 3)),
               max_share_sum=float(c.get("max_share_sum", 1.000001)))


def load_config(path="config.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    print(run())
