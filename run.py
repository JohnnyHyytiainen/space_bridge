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

    print("DONE:",
          res["rows"], "rows,",
          f"{res['ms']:.2f} ms,",
          "unique_planets=", len(res["counts"]))
