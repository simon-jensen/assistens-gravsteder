#!/usr/bin/env python3
"""Tjekker gravsteder.json, før den når GitHub Pages: en fejl i filen ville ellers tavst tømme siden.

Kør:  python3 scripts/check_data.py
Kører også i GitHub Actions ved push og pull request (.github/workflows/check.yml).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAT = {"digt", "komp", "kunst", "scene", "handel", "vid", "andet", "faelles"}
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?Z)?$")


def main():
    err = []
    try:
        doc = json.load(open(os.path.join(ROOT, "gravsteder.json"), encoding="utf-8"))
    except Exception as e:
        print("✗ gravsteder.json kan ikke læses:", e)
        return 1
    gs = doc.get("gravsteder")
    if not isinstance(gs, list) or not gs:
        print("✗ gravsteder.json: feltet 'gravsteder' mangler eller er tomt")
        return 1
    ids, nr_in_afd = set(), set()
    for g in gs:
        gid = g.get("id", "?")
        for k in ("id", "afd", "nr", "navn", "plot", "kat"):
            if k not in g or g[k] in ("", None):
                err.append(f"{gid}: feltet '{k}' mangler")
        if gid in ids:
            err.append(f"{gid}: id'et bruges to gange")
        ids.add(gid)
        if g.get("afd") and isinstance(g.get("nr"), int):
            key = (g["afd"], g["nr"])
            if key in nr_in_afd:
                err.append(f"{gid}: afd + nr bruges to gange")
            nr_in_afd.add(key)
            if gid != f"{g['afd']}{g['nr']}":
                err.append(f"{gid}: id skal være afd + nr ({g['afd']}{g['nr']})")
        if g.get("kat") not in KAT:
            err.append(f"{gid}: ukendt kategori '{g.get('kat')}' (gyldige: {', '.join(sorted(KAT))})")
        if g.get("aar") is not None and not (isinstance(g["aar"], int) and 1700 <= g["aar"] <= 2100):
            err.append(f"{gid}: 'aar' skal være et årstal eller null")
        if "qr" in g and g["qr"] not in (0, 1, True, False):
            err.append(f"{gid}: 'qr' skal være 1 eller udelades")
        fx, fy = g.get("fx"), g.get("fy")
        if not (isinstance(fx, (int, float)) and isinstance(fy, (int, float)) and 0 <= fx <= 1 and 0 <= fy <= 1):
            err.append(f"{gid}: fx/fy mangler eller ligger uden for 0–1 (kør scripts/placer.py)")
        if g.get("src") not in ("kk", "kort"):
            err.append(f"{gid}: 'src' skal være 'kk' (scriptets) eller 'kort' (manuel)")
        if g.get("src") == "kort" and not TS_RE.match(str(g.get("ts", ""))):
            err.append(f"{gid}: en manuel placering (src kort) skal have et tidsstempel 'ts'")
    # Filer, service workeren precacher, skal findes
    sw = open(os.path.join(ROOT, "sw.js"), encoding="utf-8").read()
    for f in re.findall(r"'\./([^']+)'", sw):
        if not os.path.exists(os.path.join(ROOT, f)):
            err.append(f"sw.js precacher '{f}', men filen findes ikke")
    for f in ("kort.webp", "kort@2x.webp", "kort-moerk.webp", "kort-moerk@2x.webp", "icon-192.png", "icon-512.png", "icon-180.png"):
        if not os.path.exists(os.path.join(ROOT, f)):
            err.append(f"filen '{f}' mangler")
    if err:
        print("✗ gravsteder.json har fejl:")
        for e in err:
            print("   -", e)
        return 1
    n_kort = sum(1 for g in gs if g.get("src") == "kort")
    n_usikre = sum(1 for g in gs if g.get("src") == "kk" and (g.get("acc") or 0) > 3)
    print(f"✓ gravsteder.json: {len(gs)} gravsteder, {n_kort} manuelt placeret, {n_usikre} anslåede (acc > 3 m, se data/placering.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
