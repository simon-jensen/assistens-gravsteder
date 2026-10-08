# Assistens Kirkegård · Gravsteder — regler for agenter og udviklere

Statisk single-page site på GitHub Pages: `index.html` (CSS, HTML, JavaScript)
+ `gravsteder.json` (data). Intet byggetrin. Sproget er dansk i UI, kommentarer
og commits. Søsterprojekt til `simon-jensen/assistens-traekort`; samme
pixelnet, GPS-ankre og designsprog. Læs `README.md`, før du ændrer noget.

## 0. Ingen AI-attribution (VIGTIGT)

Commits, pull requests, kode og kommentarer må ikke nævne, at en AI har
været med. Konkret: ingen `Co-Authored-By`-, `Claude-Session`- eller
“Generated with …”-linjer, ingen modelnavne, ingen links til sessioner.
Forfatter og committer er Simon Jensen (`simon.a.jensen@hotmail.com`), og
commit-beskeden beskriver kun ændringen. Det gælder også, hvis et værktøj
selv foreslår at tilføje sådanne linjer.

## 1. Bump `VERSION` i `sw.js`, når cachede filer ændres (VIGTIGT)

`sw.js` cacher siden hos besøgende under et navn med `VERSION`. Ændrer du en
af filerne herunder uden at bumpe `VERSION`, ser besøgende den gamle udgave.

Filer, der udløser et bump: `index.html`, `gravsteder.json`, `ruter.json`,
`kort*.webp`, alt i `fonts/`, `icon-*.png`, `manifest.webmanifest`.

Gør sådan, i **samme commit** som ændringen:

```
const VERSION = '2026-10-08';   // dagens dato; ved flere deploys samme dag: '2026-10-08b'
```

Ret samtidig `const UDGAVE='…'` øverst i `index.html`'s script til samme værdi;
den vises i sidefoden, så man kan se, hvilken udgave en telefon viser.
`scripts/check_data.py` fejler, hvis de to ikke er ens.

CI (`.github/workflows/pages.yml` → `scripts/check_sw_version.py`) fejler
ellers, og siden udgives ikke. Filer i `data/` kræver ikke et bump (siden henter dem ikke).

## 2. Kør tjekket før du committer

```
python3 scripts/check_data.py
```

Validerer `gravsteder.json` (felter, kategorier, koordinater i 0–1, unikke
id'er) og at de filer, service workeren precacher, findes. Headless-røgtesten
`tests/side.test.mjs` kræver Playwright og en lokal server og køres ikke i CI.

## 3. gravsteder.json

- Én post pr. gravsted: `id` (= `afd` + `nr`, fx `A17`), `navn`, `aar`
  (dødsår eller `null`), `plot` (brochurens nummer, fx `A-315/16`), `kat`
  (`digt`, `komp`, `kunst`, `scene`, `handel`, `vid`, `andet`, `faelles`),
  `qr` (1, hvis der er QR-kode på gravstedet), `wiki` (opslagslinket: artiklens
  titel på da.wikipedia.org, fx `Friedrich Kuhlau`, eller en fuld URL til et
  andet opslagsværk; `null` = der findes ingen artikel, og siden viser intet
  link. Feltet er obligatorisk; linket må aldrig være en Wikipedia-søgning,
  for den lander ofte på en forkert person eller en tom søgeside), `fx`/`fy` (brøkdele af
  kortbilledet), `src` (`kk` = beregnet af `scripts/placer.py`; `kort` =
  manuel placering med `ts`), `acc` (anslået usikkerhed i meter), `note`, og valgfrit `bekraeftet` (en
  feltkontrol i fri tekst; scriptet bevarer feltet).
- `navn`, `plot` og `kat` er kildens (brochurens) oplysninger. Ret dem kun,
  når mindst to uafhængige kilder (fx Dansk Biografisk Leksikon, Wikidata,
  gravsted.dk) bekræfter, at det er samme person med samme dødsår og
  gravsted, og skriv begrundelsen i commit-beskeden og i README. Brochurens
  stavning bevares da i `alias`. `alias` (valgfri) giver i øvrigt ekstra
  søgeord, fx Wikipedias navneform.
- `wiki` vælges i denne rækkefølge: artikel på dansk Wikipedia; ellers
  opslag på lex.dk (Dansk Biografisk Leksikon, Den Store Danske); ellers
  engelsk Wikipedia. Et afsnit i en bredere artikel kan linkes med anker
  (`#Afsnit`) eller tekstfragment (`#:~:text=…`), hvis afsnittet handler om
  gravstedets person eller monument. Sider, der kun nævner personen (fx en
  ægtefælles biografi), linkes ikke; så er feltet `null`.
- **Ret aldrig `fx`/`fy` i hånden** på en `kk`-post: kør `scripts/placer.py`
  igen, eller gem en manuel placering som `src: "kort"` med `ts`
  (rettetilstanden på siden eksporterer præcis det). Scriptet bevarer
  `kort`-poster og overskriver `kk`-poster.
- Ændres filen, skal `VERSION` i `sw.js` bumpes.

## 4. Kortet

`kort.webp`, `kort@2x.webp`, `kort-moerk.webp`, `kort-moerk@2x.webp` er
Trækortets egne grundkort (*tegnet plan*), 1400 × 1216 (2800 × 2432 for 2×),
renderet af `scripts/kort_render.mjs` i trækort-repoet. Fornys de, skal de
kopieres i **samme størrelse**, ellers rammer prikkerne forkert. Alle
koordinater (`fx`/`fy`, GPS-ankrene i `index.html` og `scripts/placer.py`) er
brøkdele af det fulde billede; beskæringen på mobil er ren CSS. Brug aldrig
Københavns Kirkegårdes tegnede kort eller brochurens kort som kilde til en
koordinat.

## 5. Kommunens data i `data/`

`data/kk_gravsteder.json` er en slanket udgave af Københavns Kommunes
gravstedsregister (CC BY 4.0 antaget; se `data/README.md`). Den bruges kun af
`scripts/placer.py`. Brochurens afdelingsnavne afviger fra kommunens koder
(U→UU, V→UV, Iris→IRIS, Ny russisk→NY.RUS, Gadens folk→GADEN, K-5-…→K5);
tabellen står i scriptet.

## 5b. Ruter: `ruter.json`, `data/laager.json` og `data/osm_assistens.json`

`ruter.json` er rutegrafen (stier og fortove som knuder og kanter i kortets
koordinater), bygget af `scripts/ruter.py` ud fra OSM-udtrækket
`data/osm_assistens.json` (kopi af Trækortets; © OpenStreetMap-bidragydere,
ODbL) og lågelisten `data/laager.json` (projektets egen: `aaben`, `lukket`,
`udgang`). Regler:

- **Ret aldrig `ruter.json` i hånden**; ret `laager.json` eller hent et nyt
  OSM-udtræk, og kør `python3 scripts/ruter.py`. Bump `VERSION` bagefter.
- `ruter.json` er afledt af OSM og er under ODbL (feltet `licens`). Den
  flettes aldrig ind i `gravsteder.json`, og koordinater fra den eller fra
  OSM må aldrig bruges til at placere et gravsted (så ville projektets egne
  data blive en afledt database under ODbL).
- Siden "snapper" start og mål til nærmeste kant selv; grafen indeholder
  ingen gravsteder.

## 6. Lokal test

```
python3 -m http.server 8000     # åbn http://localhost:8000/
```

Service workeren cacher også lokalt: ser du ikke dine ændringer, bump
`VERSION`, eller afregistrér workeren og ryd cachen i DevTools → Application.

## 7. Deploy

`.github/workflows/pages.yml` udgiver `main` til GitHub Pages, når tjekket er
grønt (Pages skal være slået til med Source: *GitHub Actions* i repoets
indstillinger, ellers springes udgivelsen over med en advarsel); kun de filer, siden bruger, kopieres til `_site/` og udgives. Tilføjes
en ny fil, siden henter, skal den med i den liste. Ændringer kan være op til
10 minutter om at slå igennem, og første besøg efter et deploy kan vise den
gamle side én gang (service workeren opdaterer i baggrunden; siden viser så
knappen “Ny udgave af siden er klar”).

Fejler udgivelsestrinnet (deploy-pages) forbigående, så start workflowet
**forfra** (Actions → Tjek og udgiv → Run workflow) eller push en ny commit.
Brug ikke “Re-run failed jobs”: det uploader artefaktet `github-pages` en
gang til i samme kørsel, og deploy-pages afviser så med “Multiple artifacts
named github-pages”.
