import json
import csv
import time

INPUT = "data/space_logs.jsonl"
OUTPUT = "data/planet_counts.csv"

counts: dict[str, int] = {}
rows = 0
skipped_blank = 0        # tom rad eller tomt planet-värde efter strip()
skipped_missing = 0      # nyckeln "planet" saknas
skipped_badjson = 0      # ogiltig JSON-rad

# --- A: Läs, validera, räkna ---
t0 = time.perf_counter()
with open(INPUT, "r", encoding="utf-8") as f:
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
            continue

        # saknad nyckel?
        if "planet" not in obj:
            skipped_missing += 1
            continue

        # hämta och normalisera planet
        planet = str(obj.get("planet", "")).strip()
        if not planet:
            skipped_blank += 1
            continue

        counts[planet] = counts.get(planet, 0) + 1
        rows += 1

valid_rows = rows
print(
    f"valid={valid_rows} "
    f"skipped_blank={skipped_blank} "
    f"skipped_missing={skipped_missing} "
    f"skipped_badjson={skipped_badjson}"
)

# sanity
assert rows > 0, "Inga giltiga rader processades (rows==0)."
assert rows == sum(
    counts.values()), f"Mismatch: rows={rows} ≠ sum(counts)={sum(counts.values())}"

dt_ms = (time.perf_counter() - t0) * 1000
print(f"tid_ms: {dt_ms:.2f}")

# --- B: Stabil sortering (count) + CSV + terminal ---


def nyckel(kv: tuple[str, int]) -> int:
    # kv = (planet, count) -> sortera på count
    return kv[1]


sorted_items = sorted(counts.items(), key=nyckel, reverse=True)

# skriv CSV i samma ordning
with open(OUTPUT, "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["planet", "count"])
    for planet, count in sorted_items:
        w.writerow([planet, count])

# skriv terminal i samma ordning
for planet, count in sorted_items:
    print(f"{planet},{count}")

# --- C: Paritetstest (CSV == minnesdata) ---
csv_items: list[tuple[str, int]] = []
with open(OUTPUT, "r", newline="", encoding="utf-8") as inf:
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
