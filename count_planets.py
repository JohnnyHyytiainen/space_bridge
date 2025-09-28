import json  # importerar json modulen i python för att jag ska kunna skriva/hämta data ur .json filer
import csv  # se ovan. Importerar csv modulen i python för att jag ska kunna skriva/hämta data ur .csv filer
import operator  # importerar operator modulen i python för att jag ska kunna använda funktioner som t.ex key=operator.itemgetter
# import operator används för sortering.
import time  # importerar time modulen i python för att jag ska kolla benchmark tider

counts = {}
rows = 0

# sätter en timer i början -INNAN- for looparna för att mäta hur lång tid for looparna under tar.
t0 = time.perf_counter()
# time.perf_counter står för time(säger sig självt) perf_counter(performance_counter) tid.prestanda_räknare.
# för jsonl filen. .jsonl = en json per rad.
# encoding="utf-8" säkerhet för att få med åäö
with open("data/space_logs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue

        obj = json.loads(line)
        planet = str(obj.get("planet", "")).strip()
        # skydd mot saknad/felaktig data
        if not planet:
            continue

        if planet in counts:
            counts[planet] += 1
        else:
            counts[planet] = 1
        rows += 1

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
with open("data/planet_counts.csv", "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["planet", "count"])        # header.
    # key=operator.itemgetter(1) = sortera på element nr 2 i tuplen (count)
    # reverse=True ger störst först.
    # rader.
    for planet, count in sorted(counts.items(), key=operator.itemgetter(1), reverse=True):
        w.writerow([planet, count])


print("rader:", rows)
for k, v in counts.items():
    print(k, v)
