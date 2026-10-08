# Assistens Kirkegård · Gravsteder

Et lille, hurtigt kort over de 133 kendte gravsteder på Assistens Kirkegård i
København: søg et navn, tryk på en prik, og se hvor du selv står. Søsterprojekt
til [Trækortet](https://github.com/simon-jensen/assistens-traekort) og bygget med
det, vi lærte dér: eget grundkort af åbne data, placeringer beregnet fra
kommunens gravstedsregister, offline-drift og ingen byggetrin.

**Live:** https://simon-jensen.github.io/assistens-gravsteder/

## Brug

- **Søg** på navn, gravstedsnummer (fx `A-58`), afdeling eller kategori
  (“maler”, “videnskab”). Vælg en afdeling i rullemenuen, eller tryk på en
  kategori under kortet for kun at se den.
- **Tryk på en prik** på kortet eller på en række i listen: gravstedet
  fremhæves begge steder, og et lille kort viser navn, dødsår, gravsted,
  kategori og et opslagslink. **Del link** kopierer et link direkte til
  gravstedet, fx `#g=P1` (H. C. Andersen).
- **🧭 Hvor er jeg?** viser din GPS-position som en blå prik med
  usikkerhedsring og fortæller, hvilket gravsted du står nærmest. Med GPS tændt
  viser listen afstanden til hvert gravsted, og **📍 Nærmeste først** sorterer
  efter den.
- **🔍 Forstør** gør kortet 2,5× og centrerer på det valgte gravsted; to-finger-
  zoom virker også.
- **📱 film** betyder, at der står en QR-kode på gravstedet, som fører til en
  film om personen (kommunens egen ordning).
- Siden virker **uden dækning**, når den har været åbnet én gang (service
  worker), og kan lægges på hjemmeskærmen som en app.

## Rettelser af placeringer

Prikkerne er beregnet fra gravstedsnumrene (se nedenfor); 125 er fundet direkte i
kommunens register, 8 er anslåede og markeret i
[`data/placering.md`](data/placering.md). Sidder en prik forkert:

1. Tryk **Ret placeringer** nederst på siden (eller åbn linket med `#ret=1`).
2. Vælg gravstedet, og tryk på kortet dér, hvor det er, eller stil dig ved det
   med **🧭 Hvor er jeg?** tændt og tryk **📡 Her**. Rettelsen ligger kun i din
   browser, indtil du eksporterer.
3. **⬇ Eksportér gravsteder.json** henter den nyeste fil fra repoet, lægger
   dine rettelser oven på (som `src: "kort"` med tidsstempel) og deler/downloader
   den. Læg den i repoets rod, kør `python3 scripts/check_data.py`, bump
   `VERSION` i `sw.js`, og commit.

`scripts/placer.py` rører aldrig en manuel placering (`src: "kort"`), så den
kan køres igen, når kommunens data opdateres.

## Data og rettigheder

Intet her er juridisk rådgivning. Kort fortalt bruges kun åbne data til
kortet, og fortegnelsen stammer fra kommunens egen brochure.

- **Fortegnelsen** (navne, dødsår, gravstedsnumre, kategorier og
  QR-markering) er transskriberet fra Københavns Kommunes brochure *133
  gravsteder på Assistens Kirkegård* (2019). Navnene står som i brochuren;
  familien Holtens fire poster på C-703 er skrevet ud, så de kan søges hver
  for sig. Tilladelse til at gengive fortegnelsen er ikke dokumenteret (se
  *Til opfølgning*).
- **Placeringerne** (`fx`/`fy` i `gravsteder.json`) er beregnet af
  `scripts/placer.py` ud fra gravstedsnumrene og midtpunkterne i Københavns
  Kommunes gravstedsregister (`data/kk_gravsteder.json`, WFS-lag
  `k101:kirkegd_gravsteder`, hentet 5. oktober 2026, bearbejdet). Licensen er
  *antaget* CC BY 4.0 som kommunens øvrige åbne data; se
  [`data/README.md`](data/README.md). Brochurens kort er **ikke** brugt som
  kilde til nogen koordinat; det er kun brugt til at kontrollere resultatet
  med øjet.
- **Grundkortet** (`kort*.webp`) er Trækortets eget kort (*tegnet plan*),
  renderet af `scripts/kort_render.mjs` i
  [assistens-traekort](https://github.com/simon-jensen/assistens-traekort) ud
  fra OpenStreetMap (© OpenStreetMap-bidragydere,
  [ODbL](https://www.openstreetmap.org/copyright)) og Københavns Kommunes
  afdelingsgrænser, gravsteder og LiDAR-detekterede træer (CC BY 4.0,
  bearbejdet). Intet er aflæst fra Københavns Kirkegårdes tegnede kort.
  Krediteringen står synligt under kortet.
- **GPS-omregningen** bygger på fire hjørneankre (kirkegårdens hjørner fra OSM
  way 3099111), de samme som i Trækortet; de afviger 0,9–1,6 m fra kortet.
- **Skrifttyperne** Fraunces, Outfit og Spline Sans Mono er selv-hostede under
  SIL Open Font License 1.1 (`fonts/OFL-*.txt`).
- **Forslag til licens** (ikke besluttet, samme som Trækortet): koden
  (`index.html`, `sw.js`, `scripts/`, `tests/`) under MIT, projektets egne data
  (`gravsteder.json`'s placeringer) under CC BY 4.0. Fortegnelsen og
  kommunens data er ikke projektets. Indtil da gælder almindelig ophavsret.

*Til opfølgning:* (1) dokumentér tilladelsen til at gengive brochurens
fortegnelse (Københavns Kirkegårde / Københavns Kommune); (2) kommunens
bekræftelse af licensen for `kirkegd_gravsteder` (mail-udkast i Trækortets
`NOTAT-grundkort.md`); (3) tjek de 8 anslåede placeringer på stedet; (4) vælg
licens og læg en `LICENSE`-fil i roden.

## Udvikling

Der er intet byggetrin. `index.html` indeholder CSS (inkl. `@font-face`),
HTML og JavaScript; `gravsteder.json` er data; `fonts/` er skrifttyperne. Kør
`python3 -m http.server` i mappen og åbn `http://localhost:8000/` (GPS,
udklipsholder og service worker kræver HTTPS eller localhost).

**Offline:** `sw.js` cacher siden, data, kortet og fontene. **Bump `VERSION`
i `sw.js` ved hvert deploy**, der ændrer `index.html`, `gravsteder.json`,
kortet, fontene, ikonerne eller manifestet; ellers hænger gamle besøgende i
den gamle udgave. CI (`.github/workflows/check.yml`) fejler, hvis det glemmes.

**Data:** `python3 scripts/check_data.py` tjekker `gravsteder.json` (kører
også i CI). `python3 scripts/placer.py` beregner placeringerne på ny fra
`data/kk_gravsteder.json` og skriver `data/placering.md`; manuelle placeringer
bevares. Filen kan genskabes fra kommunens WFS med Trækortets
`scripts/kk_hent.py` (fremgangsmåde i `data/README.md`).

**Kortet** er fire webp-filer (lys/mørk, 1× og 2×) i 1400 × 1216 px. Skal det
fornys, renderes det i Trækort-repoet og kopieres hertil i samme størrelse;
alle koordinater er brøkdele af det billede.

**Test:** `tests/side.test.mjs` er en headless røgtest (Playwright/Chromium +
en lokal server), der tjekker prikker, søgning, links, GPS-visning og
rettetilstanden og tager skærmbilleder i lys og mørk tilstand. Den køres ikke i
CI; se kommentaren øverst i filen.

Siden udgives fra `main` med GitHub Pages. Pages sender `cache-control:
max-age=600`, så ændringer kan være op til 10 minutter om at slå igennem.
