# Assistens Kirkegård · Gravsteder — regler for agenter og udviklere

Statisk single-page site på GitHub Pages: `index.html` (CSS, HTML, JavaScript)
+ `gravsteder.json` (data). Intet byggetrin. Sproget er dansk i UI, kommentarer
og commits. Søsterprojekt til `simon-jensen/assistens-traekort`; samme
pixelnet, GPS-ankre og designsprog. Læs `README.md`, før du ændrer noget.

## 1. Bump `VERSION` i `sw.js`, når cachede filer ændres (VIGTIGT)

`sw.js` cacher siden hos besøgende under et navn med `VERSION`. Ændrer du en
af filerne herunder uden at bumpe `VERSION`, ser besøgende den gamle udgave.

Filer, der udløser et bump: `index.html`, `gravsteder.json`, `kort*.webp`,
alt i `fonts/`, `icon-*.png`, `manifest.webmanifest`.

Gør sådan, i **samme commit** som ændringen:

```
const VERSION = '2026-10-08';   // dagens dato; ved flere deploys samme dag: '2026-10-08b'
```

CI (`.github/workflows/check.yml` → `scripts/check_sw_version.py`) fejler
ellers. Filer i `data/` kræver ikke et bump (siden henter dem ikke).

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
  `qr` (1, hvis der er QR-kode på gravstedet), `fx`/`fy` (brøkdele af
  kortbilledet), `src` (`kk` = beregnet af `scripts/placer.py`; `kort` =
  manuel placering med `ts`), `acc` (anslået usikkerhed i meter), `note`.
- `navn`, `plot` og `kat` er kildens (brochurens) oplysninger. Ret dem kun
  med en begrundelse i commit-beskeden. `alias` (valgfri) giver ekstra
  søgeord, fx en anden stavemåde.
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

## 6. Lokal test

```
python3 -m http.server 8000     # åbn http://localhost:8000/
```

Service workeren cacher også lokalt: ser du ikke dine ændringer, bump
`VERSION`, eller afregistrér workeren og ryd cachen i DevTools → Application.

## 7. Deploy

GitHub Pages udgiver `main` direkte; ændringer kan være op til 10 minutter om
at slå igennem, og første besøg efter et deploy kan vise den gamle side én
gang (service workeren opdaterer i baggrunden).
