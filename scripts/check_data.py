#!/usr/bin/env python3
"""Tjekker gravsteder.json, før den når GitHub Pages: en fejl i filen ville ellers tavst tømme siden.

Kør:  python3 scripts/check_data.py
Kører også i GitHub Actions ved push og pull request (.github/workflows/pages.yml), før siden udgives.
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
    # Filer, service workeren precacher, skal findes; udgaven i sidefoden skal være sw.js' VERSION
    sw = open(os.path.join(ROOT, "sw.js"), encoding="utf-8").read()
    idx = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    v_sw = re.search(r"const VERSION\s*=\s*['\"]([^'\"]+)['\"]", sw)
    v_idx = re.search(r"const UDGAVE='([^']+)'", idx)
    if not v_sw or not v_idx or v_sw.group(1) != v_idx.group(1):
        err.append(f"UDGAVE i index.html ({v_idx.group(1) if v_idx else '?'}) skal være lig VERSION i sw.js ({v_sw.group(1) if v_sw else '?'})")
    for f in re.findall(r"'\./([^']+)'", sw):
        if not os.path.exists(os.path.join(ROOT, f)):
            err.append(f"sw.js precacher '{f}', men filen findes ikke")
    for f in ("kort.webp", "kort@2x.webp", "kort-moerk.webp", "kort-moerk@2x.webp", "icon-192.png", "icon-512.png", "icon-180.png"):
        if not os.path.exists(os.path.join(ROOT, f)):
            err.append(f"filen '{f}' mangler")
    # ruter.json (bygget af scripts/ruter.py) og data/laager.json
    try:
        R = json.load(open(os.path.join(ROOT, "ruter.json"), encoding="utf-8"))
        N = len(R["n"])
        if N < 100 or not R["e"]:
            err.append("ruter.json: grafen er tom eller alt for lille")
        for a, b in R["e"] + R.get("u", []):
            if not (0 <= a < N and 0 <= b < N):
                err.append(f"ruter.json: kant ({a}, {b}) peger uden for knuderne"); break
        if "ODbL" not in R.get("licens", ""):
            err.append("ruter.json: licensfeltet skal nævne ODbL (afledt af OpenStreetMap)")
    except Exception as e:
        err.append(f"ruter.json kan ikke læses: {e}")
    try:
        L = json.load(open(os.path.join(ROOT, "data", "laager.json"), encoding="utf-8"))["laager"]
        for l in L:
            if l.get("status") not in ("aaben", "lukket", "udgang"):
                err.append(f"laager.json: {l.get('navn')}: status skal være aaben, lukket eller udgang")
            if "osm" not in l and not (isinstance(l.get("lon"), float) and isinstance(l.get("lat"), float)):
                err.append(f"laager.json: {l.get('navn')}: en låge uden osm-id skal have lon/lat")
    except Exception as e:
        err.append(f"data/laager.json kan ikke læses: {e}")
    if err:
        print("✗ gravsteder.json har fejl:")
        for e in err:
            print("   -", e)
        return 1
    n_kort = sum(1 for g in gs if g.get("src") == "kort")
    n_usikre = sum(1 for g in gs if g.get("src") == "kk" and (g.get("acc") or 0) > 3)
    print(f"✓ gravsteder.json: {len(gs)} gravsteder, {n_kort} manuelt placeret, {n_usikre} anslåede (acc > 3 m, se data/placering.md); ruter.json: {N} knuder, {len(R['e'])} kanter, {len(L)} låger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
