# Kommentarer: Svenska
# Kod: Engelska

# Cykel 3. Förberedelser för att stresstesta pipeline med syntetiskt dataset
# gen_space_logs.py — generera syntetisk JSONL (inkl. skräp)

# importer
from pathlib import Path
import random
import json


PLANETS = ["mercury", "venus", "earth", "mars",
           "jupiter", "saturn", "saturn", "uranus", "neptune"]


def generate(path="data/space_logs_100k.jsonl", n=100_000,
             p_blank=0.002, p_missing=0.002, p_badjson=0.002, seed=42):
    """Generate synthetic JSONL with blanks/missing/badjson for 100k bench."""
    random.seed(seed)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for _ in range(n):  # _ <-- normal variabel men vi använder den inte. Vi itererar bara över (n)
            r = random.random()
            if r < p_blank:
                f.write("\n")  # tom rad
            elif r < p_blank + p_missing:
                f.write(json.dumps({"junk": "noop"}) + "\n")  # Saknar "planet"
            elif r < p_blank + p_missing + p_badjson:
                f.write('{"planet": "mars"\n')               # trasig JSON
            else:
                f.write(json.dumps({"planet": random.choice(PLANETS)}) + "\n")
    return str(p)


if __name__ == "__main__":
    out = generate()
    print("Wrote:", out)
