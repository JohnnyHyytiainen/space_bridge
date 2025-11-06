**Självtest för egen 70%-regel**
- 1) Varför ger PRIMARY KEY(planet) + ON CONFLICT DO UPDATE idempotens i din sink?

- 2)  Varför kör du många execute(...) men en commit()?

- 3) Varför avrundar du SUM(share) innan QA-grind?

- 4) Vad skyddar placeholders ? mot, och varför är det snabbare än string-format?

- 5) Vad gör WAL för din typ av skrivmönster?

- 6) Varför lagrar du UTC i databasen istället för lokal tid?

- 7) Vad innebär “config-styrning” i C6, och vilken kodrad visar att Top-N kommer från config?

**Svar**
- 1) En rad per planet + "uppdatera istället för att lägga till" -> att köra samma lastning flera gånger ger samma slutläge.
  - planet är den enda nyckeln. Vid insert träffar konfliktregeln och gör UPDATE med de nya värdena. Det är semantiskt samma som 
  - d[planet] = value i Python. Formellt: apply(input, apply(input, state)) == apply(input, state)

- 2) Prestanda + atomik. Utan transaktion blir det implicit commit per rad -> många disk-fsyncs (långsamt) och risk för halvskrivet läge om något kraschar. En transaktion betyder: antingen skrivs allt eller inget.

- 3) Flyttal "grusar" (0.9999999998 / 1.0000000003). Jag avrundar till t.ex. 6 decimaler för att inte trigga falsklarm.
  - Riktiga fel (t.ex. 1.02) överlever avrundning + min tolerans ≤ 1.000001, men numeriskt brus filtreras bort.

- 4) Säkrare (förhindrar SQL-injektion) och snabbare (statement kan återanvändas med nya parametrar).
  - ? binder värden separat (ingen strängkonkat). SQLite kan cachea/optimera planen och du slipper problem med quoting/typer.

- 5) Skriver först till en WAL-logg ⇒ läsare blockeras inte av skrivare och kraschsäkerhet blir bättre. Bra default för mini-ETL.
  - Färre "exclusive" lås, smidigare samtidighet (du läser top-listor medan en batch committas). Trade-off: en extra .wal-fil och lite disk, men värt det.

- 6) En global, entydig tid utan sommartidskaos. Konvertera till lokal tid i presentation. UTC i lagret gör att all beräkning/korrelation blir deterministisk. Lokal tid = UI-fråga.

- 7) Data ut ur kod. top och max_share_sum kommer från config.json och trillar ner i run() -> quick_checks(top).
  - config.json -> load_config() -> run_from_config() -> run(..., top=..., max_share_sum=...) -> quick_checks(conn, top) -> LIMIT ?
  - Du kan alltså byta top-N och QA-gräns utan kodändring.