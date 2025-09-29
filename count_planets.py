import json  # importerar json modulen i python för att jag ska kunna skriva/hämta data ur .json filer
import csv  # se ovan. Importerar csv modulen i python för att jag ska kunna skriva/hämta data ur .csv filer
import time  # importerar time modulen i python för att jag ska kolla benchmark tider

INPUT = "data/space_logs.jsonl"
OUTPUT = "data/planet_counts.csv"
counts = {}
rows = 0
skipped_blank = 0  # räknare för tom rad / tomt planetvärde
skipped_missing = 0  # saknar 'planet' nyckeln


# sätter en timer i början -INNAN- for looparna för att mäta hur lång tid for looparna under tar.
# time.perf_counter står för time(säger sig självt) perf_counter(performance_counter) tid.prestanda_räknare.
t0 = time.perf_counter()
# för jsonl filen. .jsonl = en json per rad.
# encoding="utf-8" säkerhet för att få med åäö
with open(INPUT, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():  # tar bort whitespace till höger och vänster. "tvättar datan"
            skipped_blank += 1
            continue

        # obj = json.load string -> gör om JSON-texten till en Python-dict. line är en textsträng (en rad från filen)
        obj = json.loads(line)
        # om 'planet' inte(not) i(in) obj: så +1 pga skipped_missing += 1.
        if "planet" not in obj:
            # lägger till +1 i skipped_missing = 0 variabeln längre upp i programmet.
            skipped_missing += 1
            continue
        # planet = string obj.hämta("planet", "").strip. 'tvättar datan' se ovan om strip().
        planet = str(obj.get("planet", "")).strip()
        # skipped_blank += 1  <--- med denna så ger den skipped_blank = 12 varje gång.
        if not planet:
            continue

        if planet in counts:
            counts[planet] += 1
        else:
            counts[planet] = 1
        rows += 1


# valid_rows = rows (giltiga_rader = rader variabeln högt upp)
valid_rows = rows
print(f"valid={valid_rows} skipped_blank={skipped_blank} skipped_missing={skipped_missing}")
# printa giltiga_rader=rows. skippade_blanka=skipped_blank. skippade_saknade=skipped_missing

# asserts/sanity check för att underlätta debugging om filen är tom, tomma/blanka rader/alla rader är tomma.
# assert rows > 0 garanterar mig att MINST en giltig rad processas.
assert rows > 0, "Inga giltiga rader processades (rows==0). Kolla input/planet-fältet."
# asserts/sanity check för att varje giltig rad ska motsvara exakt en uppräkning i counts.
assert rows == sum(counts.values()), (
    f"Mismatch: rows={rows} ≠ sum(counts)={sum(counts.values())}"
)


# t0 = time.perf_counter(performance_counter) överst "startar" klockan. Denna rad "stoppar" klockan(Kallar på t0=time.perf raden)
dt_ms = ((time.perf_counter() - t0) * 1000)
# dt_ms = delta time_milliseconds = (time.perf_counter - t0 x 1000 för att göra om det till millisekunder istället för sekunder. Mer precist)
# printar ut resultatet från timern för att få en visuell bekräftelse. :.2f = endast 2 decimaler <--> :.2f
print(f"tid_ms: {dt_ms:.2f}")
# stoppar klockan FÖRE CSV för att endast mäta parse+aggregering - Tips ifrån coach.
# bättre att mäta logikens prestanda(parse+ aggregering). Mäta den totala tiden för skriptet kan vara en feature jag lägger till senare.

# --- skriv planet_counts.csv ---
with open(OUTPUT, "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["planet", "count"])        # header.
    # bytt .itemgetter till lambda istället.
    for planet, count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        w.writerow([planet, counts])

for planet, count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
    print(f"{planet},{count}")
