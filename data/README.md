# data/ — kommunens gravstedsregister og placeringsrapporten

Filerne her bruges kun af `scripts/placer.py`; siden henter dem ikke, og de
udløser ikke et bump af `VERSION` i `sw.js`.

| Fil | Indhold | Kilde | Licens |
|---|---|---|---|
| `kk_gravsteder.json` | 8.567 gravsteder på Assistens Kirkegård med afdeling, nummer og polygonens midtpunkt (WGS84, seks decimaler) | Københavns Kommune, WFS-lag `k101:kirkegd_gravsteder` (wfs-kbhkort.kk.dk), hentet 5. oktober 2026, bearbejdet (slanket, reduceret til midtpunkter) | CC BY 4.0 *antaget* (ingen datasætside på opendata.dk; bekræftelse hos kommunen udestår, se Trækortets `data/README.md`) |
| `placering.md` | Sådan blev hvert af de 133 gravsteder placeret, med anslået usikkerhed | genereret af `scripts/placer.py` | — |

Formatet er en kompakt tabel: `{"kilde", "lag", "hentet", "felter": [...],
"rows": [[afd, nr, lon, lat], ...]}`. Filen er den samme som i
[assistens-traekort](https://github.com/simon-jensen/assistens-traekort/tree/main/data)
og genskabes derfra: hent WFS-laget som beskrevet i Trækortets `data/README.md`,
kør `scripts/kk_hent.py`, og kopiér `data/kk_gravsteder.json` hertil. Kør
derefter `python3 scripts/placer.py` her.

Kreditering: *Indeholder data fra Københavns Kommune (CC BY 4.0), hentet
oktober 2026, bearbejdet.*
