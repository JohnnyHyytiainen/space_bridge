# Kommentarer: Svenska
# Kod: Engelska

from counts_enrich import run
import csv


def test_enrich_basic():
    res = run()  # läser planet_counts.json och skriver counts_enriched.csv
    assert res["rows"] > 0
    assert res["total"] > 0

    # läser tillbaka enriched och gör 3 lätta kontroller
    rows = []
    with open("data/counts_enriched.csv", "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        assert header == ["planet", "count", "share"]
        for row in r:
            rows.append(row)

    # minst lika många rader som det finns unika planeter
    assert len(rows) == res["rows"]
    # share string kan parsas och har ~ rätt precision.
    shares = [float(x[2]) for x in rows]
    assert abs(sum(shares) - 1.0) < 1e-6


if __name__ == "__main__":
    test_enrich_basic()
    print("Okej")
