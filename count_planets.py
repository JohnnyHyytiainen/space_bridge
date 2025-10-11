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
    t0_total = time.perf_counter()

    # --- A: Läsa + räkna ---
    c, rows, skip_b, skip_miss, skip_bad, read_ms = _read_counts(input_path)

    # Sanity i minnet.
    assert rows > 0
    assert rows == sum(c.values())

    # --- B: Sortera ---
    t = time.perf_counter()
    items = sorted(c.items(), key=lambda kv: kv[1], reverse=True)
    sort_ms = (time.perf_counter() - t) * 1000.0

    # --- C: Skriva CSV ---
    t = time.perf_counter()
    _write_counts(output_path, items)
    write_ms = (time.perf_counter() - t) * 1000.0

    # --- D: Verifiera .CSV == minne ---
    t = time.perf_counter()
    csv_items: list[tuple[str, int]] = []
    with open(output_path, "r", newline="", encoding="utf-8") as inf:
        r = csv.reader(inf)
        next(r, None)
        for row in r:
            csv_items.append((row[0], int(row[1])))
    verify_ms = (time.perf_counter() - t) * 1000.0

    # Paritets asserts
    assert len(csv_items) == len(items)
    assert sum(v for _, v in csv_items) == sum(v for _, v in items)
    for i, (a, b) in enumerate(zip(items, csv_items), start=1):
        assert a == b, f"Rad {i} mismatch: mem={a} vs csv={b}"

    # --- E: Skriva JSON-artefakt (planet_counts.json EFTER lyckad verifiering) ---
    # --- E: Mäter tid separat ---
    t = time.perf_counter()
    with open("data/planet_counts.json", "w", encoding="utf-8") as jf:
        json.dump(c, jf, ensure_ascii=False, indent=2)
    e_ms = (time.perf_counter() - t) * 1000.0

    total_ms = (time.perf_counter() - t0_total) * 1000.0

    # Assert/sanity
    assert abs(total_ms - (read_ms + sort_ms +
               write_ms + verify_ms + e_ms)) < 1.0

    return {
        "counts": c,
        "rows": rows,
        "skipped_blank": skip_b,
        "skipped_missing": skip_miss,
        "skipped_badjson": skip_bad,
        "read_ms": read_ms,
        "sort_ms": sort_ms,
        "write_ms": write_ms,
        "verify_ms": verify_ms,
        "e_ms": e_ms,
        "total_ms": total_ms,
    }


if __name__ == "__main__":
    res = pipeline_run()
    print("Done:",
          res["rows"], "rows |",
          f"A={res['read_ms']:.2f} B={res['sort_ms']:.2f} "
          f"C={res['write_ms']:.2f} D={res['verify_ms']:.2f} E={res['e_ms']:.2f} | "
          f"Total={res['total_ms']:.2f} ms")
