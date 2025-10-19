# Kommentarer: Svenska.
# Kod: Engelska.
import argparse
import sys
import csv
from pathlib import Path
from count_planets import pipeline_run
from counts_enrich import run as enrich_run
# run(inp, outp) -> dict

VERSION = "0.4.1 (C4)"
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
    return 0

#
# B-cli


def _read_enriched(path: str) -> list[tuple[str, int, float]]:
    rows: list[tuple[str, int, float]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        header = next(r, None)
        if header != ["planet", "count", "share"]:
            print(f"Warning: unexpected header in {path}: {header}")
            return []
        for p, c, s in r:
            rows.append((p, int(c), float(s)))
    return rows

#
# C-cli


def cmd_enrich(args) -> int:
    res = enrich_run(args.inp, args.outp)
    print(f"ENRICH: rows={res['rows']} total={res['total']}")
    rows = _read_enriched(args.outp)
    top_n = max(0, args.top)  # tillåter 0
    print(f"Top {top_n}:")
    if top_n == 0:
        print("  (no rows)")
    else:
        for p, c, s in rows[:top_n]:
            print(f"  {p:10s}  count={c:5d}  share={s:.6f}")
    print(f"-> wrote: {Path(args.outp).as_posix()}")
    return 0

#
# D-cli


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="space-bridge",
        description="Mini-ETL tools (rookie-advanced CLI)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"Space Bridge {VERSION}"
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    # C1: count
    p_count = sub.add_parser(
        "count", help="Read JSONL -> write planet_counts.csv/json")

    p_count.add_argument("--in", dest="inp", metavar="INP",
                         default="data/space_logs.jsonl")
    p_count.add_argument("--out", dest="outp", metavar="OUT",
                         default="data/planet_counts.csv")
    p_count.set_defaults(func=cmd_count)

    # C2: enrich
    p_en = sub.add_parser(
        "enrich", help="Read planet_counts.json -> write counts_enriched.csv")
    p_en.add_argument("--in", dest="inp", metavar="INP",
                      default="data/planet_counts.json")
    p_en.add_argument("--out", dest="outp", metavar="OUT",
                      default="data/counts_enriched.csv")
    p_en.add_argument("--top", type=int, default=3,
                      help="print top-N after writing (default 3)")
    p_en.set_defaults(func=cmd_enrich)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # input guard - görs CENTRALT här
    if hasattr(args, "inp") and args.inp and not Path(args.inp).exists():
        print(f"Input not found:\n{args.inp}", file=sys.stderr)
        return 2

    try:
        return args.func(args)  # 0 på success
    except AssertionError as e:
        print(f"[assert failed] {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"[unexpected] {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
