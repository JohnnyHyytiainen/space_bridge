# Kommentarer: Svenska
# Kod: Engelska

from typing import Dict, List, TypedDict
# Class Row (TypedDict): är ett sätt att skapa en dict. I detta fall är det ett
# sätt att sätta upp en dict.
# planet, count och share = keys i dicten
# string, int och float blir values i dicten.


class Row(TypedDict):
    planet: str
    count: int
    share: float

# d: ska vara en dict som mappar string till en int.
# t.ex "mars" <- string : 2 <- int


# -> är en type hint, gör det enklare för både python och någon att se vad som "förväntas" att returneras
def enrich_counts(d: Dict[str, int]) -> List[Row]:
    # 1) total
    total = 0
    for c in d.values():
        total = total + int(c)
    # 2) bygg rader
    rows = []
    if total == 0:
        for p, c in d.items():
            rows.append({"planet": p, "count": int(c), "share": 0.0})
    else:
        for p, c in d.items():
            share = float(c) / float(total)
            rows.append({"planet": p, "count": int(c), "share": share})

    # 3) sortera på count fallande
    rows_sorted = sorted(rows, key=lambda r: r["count"], reverse=True)
    return rows_sorted


# Normalfall

rows = enrich_counts({"mars": 2, "venus": 1})
assert [r["planet"] for r in rows] == ["mars", "venus"]
assert [r["count"] for r in rows] == [2, 1]
assert abs(sum(r["share"] for r in rows) - 1.0) < 1e-6

# Tom dict
assert enrich_counts({}) == []

# Noll summa
r2 = enrich_counts({"mars": 0, "venus": 0})
assert [r["share"] for r in r2] == [0.0, 0.0]


# Sortering
r3 = enrich_counts({"earth": 5, "mars": 7, "venus": 1})
assert [r["planet"] for r in r3] == ["mars", "earth", "venus"]
