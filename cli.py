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
#########################################
############# TO DO : ###################
###### C1: count # C2: enrich ###########
