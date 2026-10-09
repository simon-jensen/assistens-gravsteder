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
  kategori og **Læs mere**, et link til artiklen om personen på dansk
  Wikipedia (feltet `wiki` i `gravsteder.json`; knappen mangler, hvor der
  ingen artikel findes). **Del link** kopierer et link direkte til
  gravstedet, fx `#g=P1` (H. C. Andersen).
- **🧭 Hvor er jeg?** viser din GPS-position som en blå prik med
  usikkerhedsring og fortæller, hvilket gravsted du står nærmest. Med GPS tændt
  viser listen afstanden til hvert gravsted, og **📍 Nærmeste først** sorterer
  efter den.
- **➜ Rute hertil** på et gravsted tegner den korteste vej ad stierne fra din
  position, med afstand og gangtid, og regner om, mens du går. Står du uden for
  kirkegården, går ruten langs fortovene til den nærmeste *åbne* låge (se
  lågelisten nedenfor). De sidste meter fra stien til gravstedet er stiplede,
  fordi græsrækkerne mellem gravene ikke er kortlagt.
- **🔍 Forstør** gør kortet 2,5× og centrerer på det valgte gravsted. To fingre
  zoomer kortet (også som app på hjemmeskærmen), dobbelttryk forstørrer, træk
  flytter kortet. Prikkerne beholder deres størrelse, så de dækker mindre jord,
  jo tættere du zoomer.
- **📱 film** betyder, at der står en QR-kode på gravstedet, som fører til en
  film om personen (kommunens egen ordning).
- Siden virker **uden dækning**, når den har været åbnet én gang (service
  worker), og kan lægges på hjemmeskærmen som en app.
- **In English:** Knappen øverst skifter mellem dansk og engelsk. Siden vælger
  selv engelsk, når browserens sprog er engelsk (og dansk ikke står før), og
  husker valget. `#lang=en` i et link (fx `#g=P1&lang=en`) åbner siden på
  engelsk uanset valget; dansk er standard og står ikke i linket. Navne,
  gravstedsnumre og opslagslinkene (dansk Wikipedia) er de samme på begge sprog.

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

**Lågerne.** OpenStreetMap ved, hvor lågerne i muren er, men ikke om de er
åbne. `data/laager.json` er projektets egen liste: status *aaben*, *lukket*
(permanent lukket eller privat) eller *udgang* (sluse, kun ud), og `navn_en`
er lågens navn i den engelske rutetekst (mangler det, bruges det danske). Ruten går
aldrig gennem en lukket låge og aldrig ind gennem en sluse. Viser en låge sig
at være forkert, så ret listen, kør `python3 scripts/ruter.py`, bump
`VERSION`, og commit. En låge, OSM mangler, tilføjes med `lon`/`lat` på muren.

## Data og rettigheder

Intet her er juridisk rådgivning. Kort fortalt bruges kun åbne data til
kortet, og fortegnelsen stammer fra kommunens egen brochure.

- **Fortegnelsen** (navne, dødsår, gravstedsnumre, kategorier og
  QR-markering) er transskriberet fra Københavns Kommunes brochure *133
  gravsteder på Assistens Kirkegård* (2019). Navnene står som i brochuren,
  bortset fra fire stavefejl, der er rettet efter Dansk Biografisk Leksikon,
  Wikidata og gravsted.dk, som alle bekræfter person, dødsår og gravsted:
  Abilgaard → Abildgaard (A12), Magdelene → Magdalene Thoresen (D1), Matilde
  → Mathilde Malling Hauschultz (E4) og Finn Juul → Finn Juhl (K4).
  Brochurens stavning står i feltet `alias`, så den stadig kan søges.
  Familien Holtens fire poster på C-703 er skrevet ud, så de kan søges hver
  for sig. Tilladelse til at gengive fortegnelsen er ikke dokumenteret (se
  *Til opfølgning*).
- **Opslagslinkene** (`wiki` i `gravsteder.json`) er sat i hånden efter
  opslag: dansk Wikipedia, hvor der findes en artikel om personen; ellers
  Dansk Biografisk Leksikon eller Den Store Danske på lex.dk; ellers engelsk
  Wikipedia. Hvert link er kontrolleret mod dødsår og erhverv, og for de
  fleste mod Wikidatas eller gravsted.dk's oplysning om gravstedet. Sider,
  der kun nævner personen i forbifarten, linkes ikke; 21 gravsteder har
  derfor intet link.
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
- **Ruterne** (`ruter.json`) er en lille graf af stier og fortove på og omkring
  kirkegården, bygget af `scripts/ruter.py` ud fra OSM-udtrækket
  `data/osm_assistens.json` (kopi af Trækortets, © OpenStreetMap-bidragydere,
  ODbL) og lågelisten `data/laager.json`. Grafen er afledt af OSM-data og er
  derfor selv under **ODbL**; den ligger i sin egen fil med licensen i feltet
  `licens` og flettes aldrig ind i `gravsteder.json`. Hent aldrig koordinater
  fra `ruter.json` eller OSM ind i projektets egne data.
- **GPS-omregningen** bygger på fire hjørneankre (kirkegårdens hjørner fra OSM
  way 3099111), de samme som i Trækortet; de afviger 0,9–1,6 m fra kortet.
- **Skrifttyperne** Fraunces, Outfit og Spline Sans Mono er selv-hostede under
  SIL Open Font License 1.1 (`fonts/OFL-*.txt`).
- **Forslag til licens** (ikke besluttet, samme som Trækortet): koden
  (`index.html`, `sw.js`, `scripts/`, `tests/`) under MIT, projektets egne data
  (`gravsteder.json`'s placeringer og `data/laager.json`) under CC BY 4.0;
  `ruter.json` og `data/osm_assistens.json` forbliver ODbL. Fortegnelsen og
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

**Offline:** `sw.js` cacher siden, data, ruter, kortet og fontene. **Bump
`VERSION` i `sw.js` ved hvert deploy**, der ændrer `index.html`,
`gravsteder.json`, `ruter.json`, kortet, fontene, ikonerne eller manifestet; ellers hænger gamle besøgende i
den gamle udgave. CI (`.github/workflows/pages.yml`) fejler, hvis det glemmes.

**Sprog:** Alle tekster på siden ligger i ordbogen `SPROG` øverst i scriptet
(`da` er kilden, `en` oversættelsen) og slås op med `t('nøgle', {pladsholder})`;
statisk HTML mærkes med `data-t` (tekst), `data-th` (HTML) eller
`data-ta="attribut=nøgle"` og udfyldes af `anvendSprog()`. En ny tekst
tilføjes på begge sprog, aldrig som streng i koden. Kategorinavnene hedder
`kat_<nøgle>` og `kat_<nøgle>_k` og indgår på alle sprog i søgningen.
`placer.py`'s provenienstekster (feltet `note`) oversættes mønster for mønster
af `NOTE_EN`, og lågerne har `navn_en` i `data/laager.json`.

**Data:** `python3 scripts/check_data.py` tjekker `gravsteder.json` (kører
også i CI). `python3 scripts/placer.py` beregner placeringerne på ny fra
`data/kk_gravsteder.json` og skriver `data/placering.md`; manuelle placeringer
bevares. Filen kan genskabes fra kommunens WFS med Trækortets
`scripts/kk_hent.py` (fremgangsmåde i `data/README.md`).

**Ruter:** `python3 scripts/ruter.py` bygger `ruter.json` på ny fra
`data/osm_assistens.json` og `data/laager.json` og skriver statistik (knuder,
kanter, hvilke låger der er gennemgang ved). Et friskt OSM-udtræk hentes med
Trækortets `scripts/osm_slank.mjs` og kopieres hertil.

**Kortet** er fire webp-filer (lys/mørk, 1× og 2×) i 1400 × 1216 px. Skal det
fornys, renderes det i Trækort-repoet og kopieres hertil i samme størrelse;
alle koordinater er brøkdele af det billede.

**Test:** `tests/side.test.mjs` er en headless røgtest (Playwright/Chromium +
en lokal server), der tjekker prikker, søgning, links, GPS-visning, zoom, ruter,
rettetilstanden og den engelske udgave og tager skærmbilleder i lys og mørk tilstand. Den køres ikke i
CI; se kommentaren øverst i filen.

Siden udgives til GitHub Pages af `.github/workflows/pages.yml` ved hvert push
til `main`, men kun når tjekket af `gravsteder.json` og `VERSION` er grønt, så
en fejl aldrig når besøgende. Pages skal slås til én gang i repoets
indstillinger (Settings → Pages → Build and deployment → Source: *GitHub
Actions*); indtil da springer workflowet udgivelsen over med en advarsel (en lære fra Trækortet, hvor Pages udgiver
`main` direkte). Kun de filer, siden bruger, udgives (`_site/`); `data/`,
`scripts/` og `tests/` ligger kun i repoet. Pages sender `cache-control:
max-age=600`, så ændringer kan være op til 10 minutter om at slå igennem.
