# Kommentarer: Svenska
# Kod: Engelska

# Cykel 3. Förberedelser för att stresstesta pipeline med syntetiskt dataset
# bench_100k.py - Mäta A-E + T och rows/s

# importer
from time import perf_counter
from pathlib import Path
import csv
import json
import time
from count_planets import pipeline_run

# _var... <-- = FAAFO
# _ innan namnet indikerar att den är "privat" och bör ej användas direkt


def _write_counts_snapshot(inp: str, counts: dict[str, int]) -> None:
    """Skriv planet_counts_{stem}.{csv,json} utan att röra C1-filerna."""
    stem = Path(inp).stem  # t.ex. "space_logs_100k"
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    # CSV-snapshot
    with open(f"data/planet_counts_{stem}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["planet", "count"])
        for k, v in items:
            w.writerow([k, v])

    # JSON-snapshot
    with open(f"data/planet_counts_{stem}.json", "w", encoding="utf-8") as jf:
        json.dump(dict(items), jf, ensure_ascii=False, indent=2)

# _var... <-- = FAAFO
# _ innan namnet indikerar att den är "privat" och bör ej användas direkt


def _append_bench_row(path="runs_bench.csv", res=None, dataset="", label=""):
    p = Path(path)
    new = (not p.exists()) or (p.stat().st_size == 0)
    rows = res["rows"]
    total_ms = res["total_ms"]
    rps = rows / (total_ms / 1000.0) if total_ms else 0.0
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "dataset", "rows",
                        "A_ms", "B_ms", "C_ms", "D_ms", "E_ms", "T_ms", "rows_per_s",
                        "label"])

        w.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            dataset, rows,
            f"{res['read_ms']:.2f}", f"{res['sort_ms']:.2f}",
            f"{res['write_ms']:.2f}", f"{res['verify_ms']:.2f}",
            f"{res['e_ms']:.2f}", f"{total_ms:.2f}", f"{rps:.1f}",
            label
        ])


def bench(inp="data/space_logs_100k.jsonl", outp="data/planet_counts_bench.csv", label=""):
    t0 = perf_counter()
    res = pipeline_run(inp, outp)
    # total inkluderar A–E redan i res['total_ms'], men vi tar om hela för säkerhets skull:
    total_ms = (perf_counter() - t0) * 1000.0
    res["total_ms"] = total_ms  # överstyr om så behövs för konsistens
    rps = res["rows"] / (total_ms / 1000.0) if total_ms else 0.0
    print(
        f"rows={res['rows']} | "
        f"A={res['read_ms']:.2f} B={res['sort_ms']:.2f} "
        f"C={res['write_ms']:.2f} D={res['verify_ms']:.2f} "
        f"E={res['e_ms']:.2f} | T={total_ms:.2f} ms | {rps:.1f} rows/s"
    )

    _append_bench_row(res=res, dataset=Path(inp).name, label=label)
    _write_counts_snapshot(inp, res["counts"])
    return res


if __name__ == "__main__":
    import sys
    lab = sys.argv[1] if len(sys.argv) > 1 else ""
    bench(label=lab)
