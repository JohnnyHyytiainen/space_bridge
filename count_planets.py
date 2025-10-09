# Kommentarer: Svenska.
# Kod: Engelska.
# C1, C2, C3, C4 = EN(1) publik funktion.

import json
import csv
import time


INPUT = "data/space_logs.jsonl"
OUTPUT = "data/planet_counts.csv"


def _read_counts(path: str):
    counts: dict[str, int] = {}
    rows = skipped_blank = skipped_missing = skipped_badjson = 0

    t0 = time.perf_counter()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                skipped_blank += 1
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                skipped_badjson += 1
                continue

            if "planet" not in obj:
                skipped_missing += 1
                continue
            planet = str(obj.get("planet", "")).strip().lower()
            if not planet:
                skipped_blank += 1
                continue
            counts[planet] = counts.get(planet, 0) + 1
            rows += 1

    ms = (time.perf_counter() - t0) * 1000.0
    return counts, rows, skipped_blank, skipped_missing, skipped_badjson, ms


def _write_counts(path: str, items: list[tuple[str, int]]):
    with open(path, "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["planet", "count"])
        for k, v in items:
            w.writerow([k, v])


def pipeline_run(input_path: str = INPUT, output_path: str = OUTPUT):
    # --- A: Läsa + räkna ---
    c, rows, skip_b, skip_miss, skip_bad, ms = _read_counts(input_path)

    # Sanity i minnet.
    assert rows > 0
    assert rows == sum(c.values())

    # --- B: Sortera + skriva CSV ---
    items = sorted(c.items(), key=lambda kv: kv[1], reverse=True)
    _write_counts(output_path, items)

    # ---C: Verifiering att CSV == minne ---
    csv_items: list[tuple[str, int]] = []
    with open(output_path, "r", newline="", encoding="utf-8") as inf:
        r = csv.reader(inf)
        next(r, None)
        for row in r:
            csv_items.append((row[0], int(row[1])))

    assert len(csv_items) == len(items)
    assert sum(v for _, v in csv_items) == sum(v for _, v in items)
    for i, (a, b) in enumerate(zip(items, csv_items), start=1):
        assert a == b, f"Rad {i} missmatch: mem={a} vs csv={b}"

    return {
        "counts": c,
        "rows": rows,
        "skipped_blank": skip_b,
        "skipped_missing": skip_miss,
        "skipped_badjson": skip_bad,
        "ms": ms,
    }


if __name__ == "__main__":
    res = pipeline_run()
    print("DONE:", res["rows"], "rows,", f"{res['ms']:.2f} ms")
