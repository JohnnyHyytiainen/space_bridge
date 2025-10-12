# Kommentarer: Svenska
# Kod: Engelska

# från count_planets import pipeline_run funktionen
# kan printa och se all relevant information härifrån.
# Import - anrop - utskrift.
from count_planets import pipeline_run

# NYTT: Imports för telemetri
from pathlib import Path
import csv
import time


# NYTT: liten helper som appendar en rad till runs.csv
def _append_run_metrics(path="runs.csv", res=None, script="run.py"):
    p = Path(path)
    new = not p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow([
                "timestamp", "script", "rows",
                "read_ms", "sort_ms", "write_ms", "verify_ms", "e_ms", "total_ms",
                "skipped_blank", "skipped_missing", "skipped_badjson",
                "unique_planets", "top_planet"
            ])
        counts = res["counts"]
        top = max(counts.items(), key=lambda kv: kv[1])[0] if counts else ""
        w.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            script, res["rows"],
            f"{res['read_ms']:.2f}", f"{res['sort_ms']:.2f}",
            f"{res['write_ms']:.2f}", f"{res['verify_ms']:.2f}",
            f"{res['e_ms']:.2f}", f"{res['total_ms']:.2f}",
            res["skipped_blank"], res["skipped_missing"], res["skipped_badjson"],
            len(counts), top
        ])


if __name__ == "__main__":
    res = pipeline_run(
        input_path="data/space_logs.jsonl",
        output_path="data/planet_counts.csv",
    )

    # NYTT: skriv en rad telemetri
    _append_run_metrics(res=res, script="run.py")

    print("Done:",
          res["rows"], "rows |",
          f"A={res['read_ms']:.2f} B={res['sort_ms']:.2f} "
          f"C={res['write_ms']:.2f} D={res['verify_ms']:.2f} "
          f"E={res['e_ms']:.2f} | "
          f"T={res['total_ms']:.2f} ms")
