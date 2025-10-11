# Space Bridge
mini-ETL som läser JSONL rad-för-rad, räknar planetnamn i en `dict`, skriver CSV, verifierar paritet och loggar tider per steg. Byggd i cykler (C1–C4).

## Syfte
Träna kärnkompetenser för Data Engineering: strömmad läsning (JSONL), dictionary-räkning, enkel export (CSV) och tidsmätning.


# Cykeler 
- **En publik funktion:** `pipeline_run(input_path, output_path)`. (C1)
- **Strömmad läsning (JSONL):** en rad = en händelse → O(n) tid, O(U) minne (U≪n). (C1)
- **Normalisering:** `strip().lower()` för robusta namn. (C1)
- **Safe increment:** `counts[p] = counts.get(p, 0) + 1`. (C1)
- **Paritetstest:** läs tillbaka CSV → matcha antal, summa och ordning. (C1)
- **Mätning:** per steg i millisekunder (A–E) + total (T). (C1)


* Pipeline (A–E)
- Timing: A=read+count, B=sort, C=write CSV, D=verify parity, E=write JSON, T=total. T ≈ A+B+C+D+E (± overhead). Alla asserts måste vara gröna innan JSON skrivs.
- A = read+count: läs data/space_logs.jsonl, validera rad, räkna.
- skippar: tom rad, saknad nyckel "planet", trasig JSON.
- B = sort: sortera counts.items() på värde (fallande).
- C = write CSV: skriv data/planet_counts.csv i samma ordning som i minnet.
- D = verify parity: läs tillbaka CSV → jämför längd, totalsumma och rad-för-rad.
- E = write JSON: skriv data/planet_counts.json endast efter gröna asserts.
- T = total: hela körningen (inkl. asserts och E).


# Artefakter 
- data/planet_counts.csv — counts i stabil ordning. (C1)
- data/planet_counts.json — samma data i JSON (för vidare steg). (C1)
- results.csv — manuell dagbok (datum, cykel, pomodoros, mode, compliance). (C1)
- space_bridge.png — enkel visual (från tidigare övning). (C1)
- data/counts_enriched.csv (planet,count,share). (C2)


## Snabbstart
```bash
# kör pipeline via tunn runner (rekommenderat)
python run.py

# snabb sanity
python tests_smoke.py  # utskrift: OK

