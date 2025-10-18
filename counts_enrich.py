# Kommentarer: Svenska
# Kod: Engelska

import json
import csv


def run(inp: str = "data/planet_counts.json",
        outp: str = "data/counts_enriched.csv"):

    # --- A: Läs .JSON (counts: dict[str, int]) ---

    with open(inp, "r", encoding="utf-8") as f:
        counts: dict[str, int] = json.load(f)

    # --- B: Beräkna total + share ---
    total = sum(counts.values())
    rows = []
    # sortera samma som C1, fallande count
    for p, c in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        share = (c / total) if total else 0.0
        rows.append((p, c, share))

    # --- C: Skriva enriched CSV ---
    with open(outp, "w", newline="", encoding="utf-8") as g:
        w = csv.writer(g)
        w.writerow(["planet", "count", "share"])
        for p, c, s in rows:
            w.writerow([p, c, f"{s:.6f}"])  # 6st decimaler för stabil diff

    # --- D: Asserts för direkt feedback om något står galet till ---
    assert len(rows) == len(counts)  # antal rader ska vara samma
    if total:
        assert abs(sum(s for _, _, s in rows) - 1.0) < 1e-6  # sum(share)~1
    else:
        assert all(s == 0.0 for *_, s in rows)  # om total är == 0
    # heltal, ej negativa
    assert all(isinstance(c, int) and c >= 0 for _, c, _ in rows)
    assert all(isinstance(p, str) and p for p, _,
               _ in rows)  # strings, icke tomma

    # sorterings asserts: ej tilltagande counts
    assert all(rows[i][1] >= rows[i+1][1] for i in range(len(rows)-1))

    return {"total": total, "rows": len(rows)}
