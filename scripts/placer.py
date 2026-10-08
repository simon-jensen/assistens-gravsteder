#!/usr/bin/env python3
"""Placerer gravstederne i gravsteder.json på kortet ud fra Københavns Kommunes gravstedsdata.

Kør:  python3 scripts/placer.py            # skriver fx/fy ind i gravsteder.json og data/placering.md
      python3 scripts/placer.py --toer     # viser kun resultatet, skriver intet

Brochurens numre er kirkegårdens gravstedsnumre. Findes gravstedet i data/kk_gravsteder.json
(afdeling + nummer), bruges dets midtpunkt; ellers anslås det mellem nærmeste lavere og højere
nummer i samme afdeling (numrene ligger fortløbende i rækkerne; 0,6 m median-fejl på kendte
gravsteder, målt i trækort-projektet). Et nummer som "A-315/16" er to gravsteder: midtpunktet
mellem dem bruges. GPS → kortbrøk er den samme affine omregning som i trækortet (fire hjørneankre).

Brochurens afdelingsnavne afviger fra kommunens koder: U→UU, V→UV, X→UX, Z→UZ, Ø→UØ, Iris→IRIS,
"Ny russisk"→NY.RUS, "Gadens folk"→GADEN; "K-5-2-51/55" er afdeling K5 (række 2, nr. 51–55).

Scriptet rører kun sine egne poster (src "kk"): en post, der er placeret manuelt (src "kort"),
bevares altid. Resultatet pr. gravsted står i data/placering.md; poster med acc > 5 m bør tjekkes.
"""
import json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMGW, IMGH, LON0, LAT0, M_PER_PX = 1400, 1216, 12.55, 55.69, 0.46
KX, KY = 111320 * math.cos(math.radians(55.69)), 111320  # grader -> meter
# Hjørneankre (samme som trækortets SEED_ANCHORS): OSM way 3099111 parret med kortets pixelnet.
ANCHORS = [
    dict(lat=55.690688, lon=12.544873, fx=336 / IMGW, fy=48 / IMGH),    # Jagtvej / Hans Tavsens Gade
    dict(lat=55.688026, lon=12.551794, fx=303 / IMGW, fy=1186 / IMGH),  # Hans Tavsens Gade / Kapelvej
    dict(lat=55.690514, lon=12.554329, fx=1001 / IMGW, fy=1146 / IMGH), # Kapelvej / Nørrebrogade
    dict(lat=55.693494, lon=12.549890, fx=1272 / IMGW, fy=252 / IMGH),  # Nørrebros Runddel
]
AFD_MAP = {"U": "UU", "V": "UV", "X": "UX", "Z": "UZ", "Ø": "UØ", "IRIS": "IRIS", "NY RUSSISK": "NY.RUS",
           "GADENS FOLK": "GADEN", "1": "01", "2": "02"}


def fit_affine(anchors):
    def lsq(get):
        S = [[0.0] * 4 for _ in range(3)]
        for a in anchors:
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


TF = fit_affine(ANCHORS)


def ll_to_frac(lat, lon):
    u, v = lon - LON0, lat - LAT0
    return (TF[0][0] * u + TF[0][1] * v + TF[0][2], TF[1][0] * u + TF[1][1] * v + TF[1][2])


def dist_m(a, b):  # (lon, lat) -> meter
    return math.hypot((a[0] - b[0]) * KX, (a[1] - b[1]) * KY)


def parse_plot(plot):
    """'A-315/16' -> ('A', [(315,''),(316,'')]); 'K-5-2-51/55' -> ('K5', [(51,''),(55,'')]); 'B-333b' -> ('B', [(333,'B')]).
    Giver (afd, numre, bemærkning) eller None, hvis nummeret ikke kan tolkes."""
    p = plot.strip()
    if p.lower() == "gadens folk":
        return ("GADEN", [], "afdelingens midtpunkt")
    parts = p.split("-")
    afd = parts[0].strip().upper()
    rest = parts[1:]
    note = ""
    if afd == "K" and rest and rest[0].strip().upper().startswith("NY RUSSISK"):
        afd, rest = "NY.RUS", rest[1:]
    elif afd == "K" and len(rest) >= 3 and rest[0].isdigit():      # K-5-2-51/55, K-6-1-1: underafdeling K5/K6, række, nr
        afd, rest = "K" + rest[0], rest[2:]
        note = "underafdeling " + afd + ", række " + parts[2]
    elif afd == "D" and len(rest) >= 3 and rest[0].upper() in ("I", "1"):  # D-I-ML-15: tolkes som D1 (usikkert)
        afd, rest = "D1", rest[-1:]
        note = "tolket som D1 nr. " + rest[0] + " — tjek i felten"
    afd = AFD_MAP.get(afd, afd)
    if not rest:
        return None
    nums = []
    for tok in rest[0].split("/"):
        m = re.fullmatch(r"\s*(\d+)\s*([A-Za-z]?)\s*", tok)
        if not m:
            return None
        n = int(m.group(1))
        if nums and n < nums[-1][0]:            # "315/16" -> 316, "1026/27" -> 1027, "108/09" -> 109
            base = nums[-1][0]
            k = 10 ** len(m.group(1))
            n = base - base % k + n
            if n <= base:
                n += k
        nums.append((n, m.group(2).upper()))
    return (afd, nums, note)


def main(argv):
    dry = "--toer" in argv
    fil = os.path.join(ROOT, "gravsteder.json")
    doc = json.load(open(fil, encoding="utf-8"))
    kk = json.load(open(os.path.join(ROOT, "data", "kk_gravsteder.json"), encoding="utf-8"))
    hentet = kk.get("hentet", "?")
    gsec = {}
    for a, nr, lon, lat in kk["rows"]:
        m = re.match(r"0*(\d+)([A-Za-z]*)$", nr)
        if m:
            gsec.setdefault(a.upper(), {}).setdefault((int(m.group(1)), m.group(2).upper()), (lon, lat))

    def grav_pos(sec, n, suf):
        d = gsec.get(sec)
        if not d:
            return None
        if (n, suf) in d:
            return d[(n, suf)], 1.5, "direkte"
        if suf and (n, "") in d:
            return d[(n, "")], 2.0, "direkte (uden bogstav)"
        nums = sorted({k[0] for k in d})
        lo = max((k for k in nums if k < n), default=None)
        hi = min((k for k in nums if k > n), default=None)
        if lo is None or hi is None:
            return None
        p1 = d[next(k for k in d if k[0] == lo)]
        p2 = d[next(k for k in d if k[0] == hi)]
        gap = dist_m(p1, p2)
        w = (n - lo) / (hi - lo)
        pt = (p1[0] + (p2[0] - p1[0]) * w, p1[1] + (p2[1] - p1[1]) * w)
        how = f"anslået mellem {sec}-{lo} og {sec}-{hi} ({gap:.0f} m fra hinanden)"
        if gap <= 15 and hi - lo <= 12:
            return pt, 3.0, how
        if gap <= 40:
            return pt, 8.0, how
        return pt, 20.0, how

    rows, n_ok, n_est, n_miss, n_manual = [], 0, 0, 0, 0
    for g in doc["gravsteder"]:
        if g.get("src") == "kort":
            n_manual += 1
            rows.append((g, "manuelt placeret (src kort) — bevaret", g.get("acc")))
            continue
        for k in ("fx", "fy", "src", "acc", "note"):
            g.pop(k, None)
        parsed = parse_plot(g["plot"])
        if not parsed:
            n_miss += 1
            rows.append((g, "nummeret kan ikke tolkes", None))
            continue
        afd, nums, bem = parsed
        pts, accs, hows = [], [], []
        if not nums:  # afdelingens midtpunkt (fællesmonument)
            d = gsec.get(afd)
            if d:
                xs = [p[0] for p in d.values()]; ys = [p[1] for p in d.values()]
                pts.append((sum(xs) / len(xs), sum(ys) / len(ys))); accs.append(10.0); hows.append(f"midtpunkt af {afd} ({len(d)} gravsteder)")
        for n, suf in nums:
            r = grav_pos(afd, n, suf)
            if r:
                pts.append(r[0]); accs.append(r[1]); hows.append(f"{afd}-{n}{suf}: {r[2]}")
            else:
                hows.append(f"{afd}-{n}{suf}: ikke fundet")
        if not pts:
            n_miss += 1
            rows.append((g, "ikke fundet: " + "; ".join(hows), None))
            continue
        lon = sum(p[0] for p in pts) / len(pts); lat = sum(p[1] for p in pts) / len(pts)
        fx, fy = ll_to_frac(lat, lon)
        acc = max(accs)
        if len(pts) > 1:
            spread = max(dist_m(p, (lon, lat)) for p in pts)
            acc = max(acc, spread)
            hows.append(f"midt mellem {len(pts)} gravsteder, {spread:.0f} m spredning")
        if bem:
            hows.append(bem)
            acc = max(acc, 8.0)
        note = "KK: " + "; ".join(hows)
        g.update(fx=round(fx, 5), fy=round(fy, 5), src="kk", acc=round(acc, 1), note=note)
        if acc <= 3.0:
            n_ok += 1
        else:
            n_est += 1
        rows.append((g, note, acc))

    print(f"{n_ok} sikre, {n_est} anslåede/usikre (acc > 3 m), {n_miss} ikke fundet, {n_manual} manuelle — kommunens data hentet {hentet}")
    for g, note, acc in rows:
        if acc is None or acc > 3.0:
            print(f"  {g['id']:4s} {g['plot']:16s} {g['navn'][:32]:32s} acc={acc}  {note}")
    if dry:
        return 0
    doc["placeret"] = {"script": "scripts/placer.py", "kk_hentet": hentet}
    json.dump(doc, open(fil, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "data", "placering.md"), "w", encoding="utf-8") as f:
        f.write("# Placering af gravstederne (genereret af scripts/placer.py)\n\n")
        f.write(f"Kommunens gravstedsdata hentet {hentet}. {n_ok} sikre (acc ≤ 3 m), {n_est} anslåede/usikre, {n_miss} ikke fundet, {n_manual} manuelt placeret.\n\n")
        f.write("| Id | Gravsted | Navn | acc (m) | Sådan fundet |\n|---|---|---|--:|---|\n")
        for g, note, acc in rows:
            f.write(f"| {g['id']} | {g['plot']} | {g['navn']} | {'' if acc is None else acc} | {note} |\n")
    print("skrev gravsteder.json og data/placering.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
