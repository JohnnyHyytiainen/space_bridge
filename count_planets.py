import json

counts = {}
rows = 0

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

print("rader:", rows)
for k, v in counts.items():
    print(k, v)
