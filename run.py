# Kommentarer: Svenska
# Kod: Engelska

# från count_planets import pipeline_run funktionen
# kan printa och se all relevant information härifrån.
# Import - anrop - utskrift.
from count_planets import pipeline_run

if __name__ == "__main__":
    res = pipeline_run(
        input_path="data/space_logs.jsonl",
        output_path="data/planet_counts.csv",
    )

    print("Done:",
          res["rows"], "rows |",
          f"A={res['read_ms']:.2f} B={res['sort_ms']:.2f} "
          f"C={res['write_ms']:.2f} D={res['verify_ms']:.2f} "
          f"E={res['e_ms']:.2f} | "
          f"T={res['total_ms']:.2f} ms")
