# Kommentarer: Svenska.
# Kod: Engelska.
import argparse
import sys
import csv
from pathlib import Path
from count_planets import pipeline_run
from counts_enrich import run as enrich_run
# run(inp, outp) -> dict

#
# A-cli


def cmd_count(args) -> int:
    res = pipeline_run(args.inp, args.outp)
    print(
        "COUNT:",
        f"rows={res['rows']} | "
        f"A={res['read_ms']:.2f} B={res['sort_ms']:.2f} "
        f"C={res['write_ms']:.2f} D={res['verify_ms']:.2f} "
        f"E={res['e_ms']:.2f} | T={res['total_ms']:.2f} ms"
    )
    # snäll extra: visa filen som skrevs
    print(f"-> wrote: {Path(args.outp).as_posix()}")
    return 0  # Varför return 0?

#
# B-cli


def _read_enriched(path: str) -> list[tuple[str, int, float]]:
    rows: list[tuple[str, int, float]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        header = next(r, None)
        for p, c, s in r:
            rows.append((p, int(c), float(s)))
    return rows

#
# C-cli


def cmd_enrich(args) -> int:
    res = enrich_run(args.inp, args.outp)
    print(f"ENRICH: rows={res['rows']} total={res['total']}")
    # Visa topp N från enriched (planet, count, share)
    top_n = max(1, args.top)
    rows = _read_enriched(args.outp)
    print(f"Top {top_n}:")
    for p, c, s in rows[:top_n]:
        print(f"  {p:10s}  count={c:5d}  share={s:.6f}")
    print(f"-> wrote: {Path(args.outp).as_posix()}")
    return 0

#
# D-cli


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="space-bridge",
        description="Mini-ETL tools (rookie-advanced CLI)"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # C1: count
    p_count = sub.add_parser(
        "count", help="Read JSONL -> write planet_counts.csv/json")
    p_count.add_argument("--in", dest="inp", default="data/space_logs.jsonl")
    p_count.add_argument("--out", dest="outp",
                         default="data/planet_counts.csv")
    p_count.set_defaults(func=cmd_count)

    # C2: enrich
    p_en = sub.add_parser(
        "enrich", help="Read planet_counts.json -> write counts_enriched.csv")
    p_en.add_argument("--in", dest="inp", default="data/planet_counts.json")
    p_en.add_argument("--out", dest="outp", default="data/counts_enriched.csv")
    p_en.add_argument("--top", type=int, default=3,
                      help="print top-N after writing (default 3)")
    p_en.set_defaults(func=cmd_enrich)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
