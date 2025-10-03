import json
import csv
import time

INPUT = "data/space_logs.jsonl"
OUTPUT = "data/planet_counts.csv"

# Code: English • Comments: Svenska • C1 = EN (1) publik funktion


def pipeline_run(input_path: str = INPUT, output_path: str = OUTPUT):
    # --- A: Läs, validera, räkna ---
    counts: dict[str, int] = {}
    rows = 0
    skipped_blank = 0        # tom rad eller tomt planet-värde efter strip()
    skipped_missing = 0      # nyckeln "planet" saknas
    skipped_badjson = 0      # ogiltig JSON-rad

    t0 = time.perf_counter()
    with open(input_path, "r", encoding="utf-8") as f:  # <-- använd input_path
        for line in f:
            # hoppa helt tom rad
            if not line.strip():
                skipped_blank += 1
                continue

            # försök tolka raden som JSON
            try:
                obj = json.loads(line)
            except ValueError:
                skipped_badjson += 1
                continue  # <-- måste vara inuti except-blocket

            # saknad nyckel?
            if "planet" not in obj:
                skipped_missing += 1
                continue

            # hämta och normalisera planet (bara strip i C1)
            planet = str(obj.get("planet", "")).strip()
            if not planet:
                skipped_blank += 1
                continue

            # safe increment
            counts[planet] = counts.get(planet, 0) + 1
            rows += 1

    valid_rows = rows
    print(
        f"valid={valid_rows} "
        f"skipped_blank={skipped_blank} "
        f"skipped_missing={skipped_missing} "
        f"skipped_badjson={skipped_badjson}"
    )

    # sanity (in-memory)
    assert rows > 0, "Inga giltiga rader processades (rows==0)."
    assert rows == sum(counts.values()), (
        f"Mismatch: rows={rows} ≠ sum(counts)={sum(counts.values())}"
    )

    dt_ms = (time.perf_counter() - t0) * 1000
    print(f"tid_ms: {dt_ms:.2f}")

    # --- B: Stabil sortering (count) + CSV + terminal ---
    sorted_items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)

    # skriv CSV i samma ordning
    with open(output_path, "w", newline="", encoding="utf-8") as out:  # <-- output_path
        w = csv.writer(out)
        w.writerow(["planet", "count"])
        for planet, count in sorted_items:
            w.writerow([planet, count])

    # skriv terminal i samma ordning
    for planet, count in sorted_items:
        print(f"{planet},{count}")

    # --- C: Paritetstest (CSV == minnesdata) ---
    csv_items: list[tuple[str, int]] = []
    with open(output_path, "r", newline="", encoding="utf-8") as inf:
        reader = csv.reader(inf)
        next(reader, None)  # hoppa header
        for row in reader:
            csv_items.append((row[0], int(row[1])))

    # antal rader
    assert len(csv_items) == len(sorted_items), (
        f"Antal skiljer: csv={len(csv_items)} vs mem={len(sorted_items)}"
    )

    # totalsumma
    csv_sum = sum(c for _, c in csv_items)
    mem_sum = sum(c for _, c in sorted_items)
    assert csv_sum == mem_sum, f"Summa skiljer: csv={csv_sum} vs mem={mem_sum}"

    # ordning rad-för-rad
    for i, (mem_pair, csv_pair) in enumerate(zip(sorted_items, csv_items), start=1):
        assert mem_pair == csv_pair, f"Rad {i} mismatch: mem={mem_pair} vs csv={csv_pair}"

    print(f"CSV_OK rows={len(csv_items)} sum={csv_sum}")

    # Returnera lite nytta till ev. test/print
    return {
        "counts": counts,
        "rows": rows,
        "skipped_blank": skipped_blank,
        "skipped_missing": skipped_missing,
        "skipped_badjson": skipped_badjson,
        "ms": dt_ms,
    }


if __name__ == "__main__":
    # C1-körning (ingen extra funktion, bara anrop)
    res = pipeline_run()
    print("DONE:", res["rows"], "rows,", f"{res['ms']:.2f} ms")
