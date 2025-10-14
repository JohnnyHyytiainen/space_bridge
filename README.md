# Space Bridge — Rookie-Advanced
Minimal, förklarbar mini-ETL: läs JSONL rad-för-rad, räkna planetnamn i en `dict`, skriv CSV, verifiera paritet och logga tider per steg. Byggd i cykler (C1–C4).


## Syfte
Träna kärnkompetenser i Data Engineering: strömmad läsning (JSONL), robust normalisering, enkel export (CSV/JSON), paritetstester och tidsmätning.


## Pipeline A–E (gäller C1)
- **A (read+count):** läs `data/space_logs.jsonl`, validera rad, normalisera (`strip().lower()`), safe increment.  
  - *Skippar:* tom rad, saknad `planet`, trasig JSON.
- **B (sort):** sortera `counts.items()` fallande på `count`.
- **C (write CSV):** skriv exakt samma ordning till `data/planet_counts.csv`.
- **D (verify parity):** läs tillbaka CSV → jämför längd, totalsumma och rad-för-rad.
- **E (write JSON):** skriv `data/planet_counts.json` endast efter gröna asserts.
- **T (total):** hela körningen. T ≈ A+B+C+D+E (± overhead).


## Cykel 1 (C1) - Counting
- **Publik funktion:** `pipeline_run(input_path, output_path)`
- **Komplexitet:** O(n) tid, O(U) minne (U≈8 planeter)
- **Mätning:** per steg i millisekunder (A–E) + total
- **Exempelutskrift:**
  - Done: 12 rows | A=0.34 B=0.01 C=0.88 D=2.35 E=0.97 | T=4.58 ms


## Cykel 2 (C2) - Enrichment 
- Läser `data/planet_counts.json` och skriver `data/counts_enriched.csv` med kolumner:
planet,count,share (share med 6 decimaler), sorterad fallande på count.
## Korrekthet (asserts)
- `len(rows) == len(counts)`  
- total>0 -> abs(sum(share) - 1.0) < 1e-6, annars alla share == 0.0
- count heltal och >= 0, planet icke-tom sträng
- icke-tilltagande count rad-för-rad


## Köra Cykel 2 (C2):
- python -c "`from counts_enrich import run; print(run())`"
- python `test_enrich_counts.py`

## Cykel 3 (C3) - Performance (syntetisk/synthetic)
- Dataset: `space_logs_100k.jsonl`(seed=42)
- Exempel (cold): rows = 99,378 | A=126.41 B=0.00 C=0.40 D=19.25 E=2.04 | T=148.15 ms | 670,781.8 rows/s
- Exempel (warm): rows = 99,378 | A=124.91 B=0.01 C=0.42 D=2.66 E=0.25 | T=128.28 ms | 774,721.3 rows/s
- Notering: Cold vs warm cache. D dominerar ofta små filer; A/C växer linjärt med rader.


## Artefakter 
- data/planet_counts.csv — counts i stabil ordning (C1)
- data/planet_counts.json — samma data i JSON (C1)
- data/counts_enriched.csv — planet,count,share (C2)
- runs.csv — automatisk körlogg: timestamp, rows, A–E, T, skips, unique, top (C2+)
- results.csv — manuell dagbok (datum, cykel, pomodoros, mode, compliance)
- space_bridge.png — enkel visual från tidigare övning


## Snabbstart
```bash
python run.py                  # kör C1 och loggar A–E + T
python tests_smoke.py          # ska skriva: OK
python -c "from counts_enrich import run; print(run())"  # C2
python test_enrich_counts.py   # ska skriva: Okej