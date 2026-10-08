#!/usr/bin/env python3
"""Bygger rutegrafen ruter.json: stierne på og omkring Assistens Kirkegård som knuder og kanter i kortets
koordinater, klippet ved muren alle steder undtagen de åbne låger. Siden regner korteste vej på den.

Kør:  python3 scripts/ruter.py            # skriver ruter.json (bump VERSION i sw.js bagefter)
      python3 scripts/ruter.py --toer     # viser kun statistik

Kilder: data/osm_assistens.json (OpenStreetMap-udtræk, ODbL) og data/laager.json (lågernes status).
Gangbare veje: highway = footway, path, pedestrian, steps, service, residential, living_street, cycleway,
tertiary, uden access=private/no eller foot=no. Knuder deles, hvor koordinaterne er ens (udtrækket har
geometri, ikke node-id'er). En kant, der krydser kirkegårdens omrids (OSM way 3099111), beholdes kun, hvis
den passerer højst 4 m fra en låge med status "aaben" (begge veje) eller "udgang" (kun indefra og ud);
alle kanter ved en "lukket" låge og ved OSM-låger tagget private/permit/no fjernes. En låge uden OSM-id
(fx en sluse, OSM mangler) sættes ind som en knude på muren og forbindes til nærmeste knude inde og ude.

ruter.json er afledt af OpenStreetMap-data og er derfor selv under ODbL (feltet "licens"); den holdes
adskilt fra gravsteder.json, som er projektets egne data. Format: n = knuder [[fx, fy], …] (brøkdele af
kortet, 4 decimaler), e = tovejskanter [[a, b], …], u = envejskanter [[a, b], …] (kun a → b),
laager = [{navn, status, n (knudeindeks eller null), fx, fy}, …]. Længder regnes på siden.
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMGW, IMGH, LON0, LAT0 = 1400, 1216, 12.55, 55.69
KX, KY = 111320 * math.cos(math.radians(55.69)), 111320
ANCHORS = [dict(lat=55.690688, lon=12.544873, fx=336 / IMGW, fy=48 / IMGH), dict(lat=55.688026, lon=12.551794, fx=303 / IMGW, fy=1186 / IMGH),
           dict(lat=55.690514, lon=12.554329, fx=1001 / IMGW, fy=1146 / IMGH), dict(lat=55.693494, lon=12.549890, fx=1272 / IMGW, fy=252 / IMGH)]
WALK = {"footway", "path", "pedestrian", "steps", "service", "residential", "living_street", "cycleway", "tertiary"}
GATE_M = 4.0      # en kant må krydse muren højst så langt fra en åben låge
LINK_M = 25.0     # en låge uden OSM-id forbindes til knuder højst så langt væk


def fit():
    def lsq(get):
        S = [[0.0] * 4 for _ in range(3)]
        for a in ANCHORS:
            r = [a["lon"] - LON0, a["lat"] - LAT0, 1]
            v = get(a)
            for i in range(3):
                for j in range(3):
                    S[i][j] += r[i] * r[j]
                S[i][3] += r[i] * v
        for i in range(3):
            m = max(range(i, 3), key=lambda k: abs(S[k][i]))
            S[i], S[m] = S[m], S[i]
            for k in range(i + 1, 3):
                f = S[k][i] / S[i][i]
                for j in range(i, 4):
                    S[k][j] -= f * S[i][j]
        x = [0, 0, 0]
        for i in range(2, -1, -1):
            x[i] = (S[i][3] - sum(S[i][j] * x[j] for j in range(i + 1, 3))) / S[i][i]
        return x
    return lsq(lambda a: a["fx"]), lsq(lambda a: a["fy"])


TX, TY = fit()


def frac(p):
    u, v = p[0] - LON0, p[1] - LAT0
    return (TX[0] * u + TX[1] * v + TX[2], TY[0] * u + TY[1] * v + TY[2])


def dist_m(a, b):
    return math.hypot((a[0] - b[0]) * KX, (a[1] - b[1]) * KY)


def seg_m(p, a, b):  # afstand i meter fra punkt til liniestykke (lon/lat)
    dx, dy = (b[0] - a[0]) * KX, (b[1] - a[1]) * KY
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * KX * dx + (p[1] - a[1]) * KY * dy) / L))
    return math.hypot((p[0] - a[0]) * KX - t * dx, (p[1] - a[1]) * KY - t * dy)


def inside(pt, ring):
    x, y, c = pt[0], pt[1], False
    for i in range(len(ring)):
        x1, y1 = ring[i - 1]
        x2, y2 = ring[i]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def main(argv):
    dry = "--toer" in argv
    osm = json.load(open(os.path.join(ROOT, "data", "osm_assistens.json"), encoding="utf-8"))
    els = [dict(zip(osm["felter"], r)) for r in osm["rows"]]
    laager = json.load(open(os.path.join(ROOT, "data", "laager.json"), encoding="utf-8"))["laager"]
    ring = next(e for e in els if e["type"] == "way" and e["id"] == 3099111)["geom"]
    nodes_osm = {e["id"]: e for e in els if e["type"] == "node"}

    key = lambda p: (round(p[0], 6), round(p[1], 6))
    pos, adj = {}, {}
    def add(a, b):
        pos.setdefault(a, a); pos.setdefault(b, b)
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    nways = 0
    for e in els:
        t = e.get("tags") or {}
        if e["type"] != "way" or t.get("highway") not in WALK:
            continue
        if t.get("access") in ("private", "no") or t.get("foot") == "no":
            continue
        g = e["geom"]
        nways += 1
        for i in range(1, len(g)):
            if key(g[i - 1]) != key(g[i]):
                add(key(g[i - 1]), key(g[i]))

    # Låger: status pr. punkt. OSM-låger uden plads i listen, men tagget private/permit/no, er lukkede.
    gates = []
    listed = {l["osm"] for l in laager if "osm" in l}
    for l in laager:
        if "osm" in l:
            n = nodes_osm.get(l["osm"])
            if not n:
                print(f"ADVARSEL: OSM-node {l['osm']} ({l['navn']}) findes ikke i udtrækket"); continue
            gates.append(dict(navn=l["navn"], status=l["status"], p=tuple(n["geom"][0]), osm=l["osm"]))
        else:
            gates.append(dict(navn=l["navn"], status=l["status"], p=(l["lon"], l["lat"]), osm=None))
    for e in els:
        t = e.get("tags") or {}
        if e["type"] == "node" and e["id"] not in listed and t.get("barrier") in ("gate", "swing_gate", "lift_gate") and t.get("access") in ("private", "permit", "no"):
            gates.append(dict(navn="privat låge (OSM)", status="lukket", p=tuple(e["geom"][0]), osm=e["id"]))
    for g in gates:
        g["inde"] = inside(g["p"], ring)

    # Lukkede låger: fjern alle kanter ved knuden
    cut_closed = 0
    for g in gates:
        if g["status"] != "lukket":
            continue
        k = key(g["p"])
        if k in adj:
            for m in list(adj[k]):
                adj[m].discard(k); cut_closed += 1
            adj[k] = set()

    # Kanter, der krydser muren: kun ved åbne låger (udgang: kun indefra og ud)
    inde = {k: inside(k, ring) for k in pos}
    oneway, cut_wall, via = set(), 0, {}
    for a in list(adj):
        for b in list(adj[a]):
            if a >= b:
                continue
            if inde[a] == inde[b]:
                continue
            near = [g for g in gates if g["status"] in ("aaben", "udgang") and seg_m(g["p"], a, b) <= GATE_M]
            if not near:
                adj[a].discard(b); adj[b].discard(a); cut_wall += 1; continue
            g = min(near, key=lambda g: seg_m(g["p"], a, b))
            via.setdefault(g["navn"], 0); via[g["navn"]] += 1
            if g["status"] == "udgang":
                i, o = (a, b) if inde[a] else (b, a)
                adj[o].discard(i); oneway.add((i, o))

    # Låger uden OSM-knude (fx en sluse, OSM mangler): sæt en knude på muren, forbind inde og ude
    for g in gates:
        if g["status"] == "lukket" or key(g["p"]) in adj:
            continue
        k = key(g["p"]); pos[k] = k; adj[k] = set(); inde[k] = None
        best = {True: None, False: None}
        for n in pos:
            if n == k or not adj.get(n):
                continue
            d = dist_m(n, k)
            side = inde[n]
            if side is None:
                continue
            if d <= LINK_M and (best[side] is None or d < best[side][0]):
                best[side] = (d, n)
        if not best[True] or not best[False]:
            print(f"ADVARSEL: {g['navn']}: ingen knude inden for {LINK_M:.0f} m på {'inder' if not best[True] else 'yder'}siden"); continue
        ni, no = best[True][1], best[False][1]
        adj[ni].add(k); adj[k].add(no)
        if g["status"] == "aaben":
            adj[k].add(ni); adj[no].add(k)
        else:
            oneway.update({(ni, k), (k, no)})
        via[g["navn"]] = 2
        print(f"· {g['navn']}: forbundet ({best[True][0]:.0f} m inde, {best[False][0]:.0f} m ude)")

    # Behold kun knuder på kortet med mindst én kant; nummerér
    keep = [k for k in pos if adj.get(k) or any(k in adj[m] for m in adj) ]
    keep = [k for k in keep if -0.02 <= frac(k)[0] <= 1.02 and -0.02 <= frac(k)[1] <= 1.02]
    keepset = set(keep)
    idx = {k: i for i, k in enumerate(keep)}
    E, U = set(), set()
    for a in keep:
        for b in adj.get(a, ()):
            if b not in keepset:
                continue
            if (a, b) in oneway or (b, a) in oneway:
                if (a, b) in oneway:
                    U.add((idx[a], idx[b]))
            elif a in adj.get(b, ()):
                E.add((min(idx[a], idx[b]), max(idx[a], idx[b])))
            else:
                U.add((idx[a], idx[b]))
    # Sammenhæng inde på kirkegården
    comp, seen = [], set()
    nb = {i: set() for i in range(len(keep))}
    for a, b in E:
        nb[a].add(b); nb[b].add(a)
    for a, b in U:
        nb[a].add(b)
    for i, k in enumerate(keep):
        if i in seen or not inde.get(k):
            continue
        st, c = [i], 0; seen.add(i)
        while st:
            v = st.pop(); c += 1
            for w in nb[v]:
                if w not in seen and inde.get(keep[w]):
                    seen.add(w); st.append(w)
        comp.append(c)
    comp.sort(reverse=True)
    lg = [dict(navn=g["navn"], status=g["status"], n=idx.get(key(g["p"])), fx=round(frac(g["p"])[0], 4), fy=round(frac(g["p"])[1], 4)) for g in gates if g["navn"] != "privat låge (OSM)"]
    print(f"{nways} gangbare veje → {len(keep)} knuder, {len(E)} tovejskanter, {len(U)} envejskanter; "
          f"{cut_wall} kanter klippet ved muren, {cut_closed} ved lukkede låger; delnet inde: {len(comp)} ({comp[:5]})")
    for navn, n in sorted(via.items()):
        print(f"  gennem {navn}: {n} kant(er)")
    if dry:
        return 0
    out = {"licens": "Afledt af OpenStreetMap-data: ODbL 1.0 · © OpenStreetMap-bidragydere · https://www.openstreetmap.org/copyright",
           "kilde": f"data/osm_assistens.json (hentet {osm.get('hentet', '?')}) og data/laager.json; bygget af scripts/ruter.py",
           "n": [[round(frac(k)[0], 4), round(frac(k)[1], 4)] for k in keep],
           "e": sorted(E), "u": sorted(U), "laager": lg}
    with open(os.path.join(ROOT, "ruter.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"skrev ruter.json ({os.path.getsize(os.path.join(ROOT, 'ruter.json')) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
