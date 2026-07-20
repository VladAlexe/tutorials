"""Filtreaza reteaua Thiers13 la o felie lizibila si scrie un JSON mic.
Ruleaza din data/:  python build_network.py"""
import json, collections, os

CLASSES    = ["2BIO1", "2BIO2", "MP*1"]  # 2 clase de bio care se amesteca + 1 separata
DAY        = 1
MIN_WEIGHT = 20

HERE = os.path.dirname(os.path.abspath(__file__))
klass = {}
with open(os.path.join(HERE, "HighSchool2013_metadata.txt"), encoding="utf-8") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2: klass[int(p[0])] = p[1]

rows = []
with open(os.path.join(HERE, "High-School_data_2013.csv"), encoding="utf-8") as f:
    for line in f:
        p = line.split()
        if len(p) >= 3: rows.append((int(p[0]), int(p[1]), int(p[2])))

times = sorted(set(r[0] for r in rows))
bounds, start, prev = [], times[0], times[0]
for t in times[1:]:
    if t - prev > 7200:
        bounds.append((start, prev)); start = t
    prev = t
bounds.append((start, prev))
day_start, day_end = bounds[DAY - 1]

keep = {n for n, c in klass.items() if c in CLASSES}
w = collections.Counter()
for t, i, j in rows:
    if day_start <= t <= day_end and i in keep and j in keep:
        a, b = (i, j) if i < j else (j, i)
        w[(a, b)] += 1

edges = [{"source": a, "target": b, "weight": c} for (a, b), c in w.items() if c >= MIN_WEIGHT]
used = set()
for e in edges: used.add(e["source"]); used.add(e["target"])
nodes = [{"id": n, "group": klass[n]} for n in sorted(used)]

json.dump({"nodes": nodes, "edges": edges,
    "meta": {"classes": CLASSES, "day": DAY, "min_weight": MIN_WEIGHT,
             "source": "SocioPatterns Thiers13",
             "cite": "R. Mastrandrea, J. Fournet, A. Barrat, PLoS ONE 10(9): e0136497 (2015)"}},
    open(os.path.join(HERE, "highschool-network.json"), "w", encoding="utf-8"),
    ensure_ascii=False, indent=0)
print(f"{len(nodes)} noduri, {len(edges)} muchii.")
