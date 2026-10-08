# data/ — kommunens gravstedsregister, OSM-udtrækket og lågelisten

Filerne her bruges kun af `scripts/placer.py` og `scripts/ruter.py`; siden
henter dem ikke, og de udløser ikke et bump af `VERSION` i `sw.js` (det gør
derimod `ruter.json` i roden, som `ruter.py` skriver).

| Fil | Indhold | Kilde | Licens |
|---|---|---|---|
| `kk_gravsteder.json` | 8.567 gravsteder på Assistens Kirkegård med afdeling, nummer og polygonens midtpunkt (WGS84, seks decimaler) | Københavns Kommune, WFS-lag `k101:kirkegd_gravsteder` (wfs-kbhkort.kk.dk), hentet 5. oktober 2026, bearbejdet (slanket, reduceret til midtpunkter) | CC BY 4.0 *antaget* (ingen datasætside på opendata.dk; bekræftelse hos kommunen udestår, se Trækortets `data/README.md`) |
| `placering.md` | Sådan blev hvert af de 133 gravsteder placeret, med anslået usikkerhed | genereret af `scripts/placer.py` | — |
| `osm_assistens.json` | Veje, stier, mure, låger, bygninger m.m. på og omkring kirkegården (bbox 55,687–55,695 N, 12,543–12,556 Ø) og kirkegårdens omrids (way 3099111); 2.798 elementer | OpenStreetMap-bidragydere via Overpass API, hentet 7. oktober 2026, slanket med Trækortets `scripts/osm_slank.mjs` (kopi af Trækortets `data/osm_assistens.json`) | [ODbL 1.0](https://www.openstreetmap.org/copyright) · © OpenStreetMap-bidragydere |
| `laager.json` | Lågerne i muren med status `aaben`, `lukket` eller `udgang`; OSM-låger refereres med node-id, en låge OSM mangler får `lon`/`lat` | projektets egen liste (Simon Jensen, oktober 2026) | projektets |

Formatet er en kompakt tabel: `{"kilde", "lag", "hentet", "felter": [...],
"rows": [[afd, nr, lon, lat], ...]}`. Filen er den samme som i
[assistens-traekort](https://github.com/simon-jensen/assistens-traekort/tree/main/data)
og genskabes derfra: hent WFS-laget som beskrevet i Trækortets `data/README.md`,
kør `scripts/kk_hent.py`, og kopiér `data/kk_gravsteder.json` hertil. Kør
derefter `python3 scripts/placer.py` her.

`scripts/ruter.py` bygger `ruter.json` i roden af `osm_assistens.json` og
`laager.json`; grafen er afledt af OSM og dermed selv under ODbL, adskilt fra
`gravsteder.json`.

Kreditering: *Indeholder data fra Københavns Kommune (CC BY 4.0), hentet
oktober 2026, bearbejdet. Ruter: kortdata © OpenStreetMap-bidragydere (ODbL).*
