import json
import csv
import operator

counts = {}
rows = 0
# för jsonl filen. .jsonl = en json per rad.
# encoding="utf-8" säkerhet för att få med åäö
with open("data/space_logs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        obj = json.loads(line)
        planet = obj["planet"]
        if planet in counts:
            counts[planet] += 1
        else:
            counts[planet] = 1
        rows += 1
# --- skriv planet_counts.csv ---
with open("data/planet_counts.csv", "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["planet", "count"])        # header
    # key=operator.itemgetter(1) = sortera på element nr 2 i tuplen (count)
    # reverse=True ger störst först.
    for planet, count in sorted(counts.items(), key=operator.itemgetter(1), reverse=True):  # rader
        w.writerow([planet, count])


print("rader:", rows)
for k, v in counts.items():
    print(k, v)
