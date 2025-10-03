# Space Bridge
Mikro-pipeline: JSONL → räknare (dict) → CSV. Byggt i cykler (C1–C4) med mätbar prestanda och körlogg i `results.csv`.

## Syfte
Träna kärnkompetenser för Data Engineering: strömmad läsning (JSONL), dictionary-räkning, enkel export (CSV) och tidsmätning.

## Snabbstart
```bash
python count_planets.py
C1 – Count & Persist (pipeline_run)
Entrypoint: python count_planets.py

A: Läs data/space_logs.jsonl rad för rad → validera → räkna förekomster i en dict.

Ignoreras: tom rad, saknad nyckel "planet", trasig JSON

Normalisering: strip().lower() på planetnamn

Räknelogik: counts[name] = counts.get(name, 0) + 1 (startar på 1, undviker KeyError)

B: Sortera på count (fallande) och skriv data/planet_counts.csv.

C: Paritetstest: läs tillbaka CSV och verifiera att antal, summa och ordning matchar minnet.
