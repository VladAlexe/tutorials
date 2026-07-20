"""Filtreaza reteaua Thiers13 la o felie lizibila si scrie doua JSON-uri:
   highschool-network.json (nodurile, cu nume romanesti) si
   highschool-stats.json (distributia gradelor).
   Ruleaza din data/:  py build_network.py"""
import json, collections, os, statistics

CLASSES    = ["2BIO1", "2BIO2", "MP*1"]
DAY        = 1
MIN_WEIGHT = 3

NAMES = [
    "Ana", "Andrei", "Bianca", "Bogdan", "Carla", "Cristi", "Dana", "Doru", "Elena", "Florin",
    "Gabi", "Horia", "Ioana", "Radu", "Maria", "Matei", "Nadia", "Octav", "Paula", "Rares",
    "Sorina", "Tudor", "Vlad", "Zina", "Alex", "Bea", "Cezar", "Delia", "Emil", "Flavia",
    "George", "Hana", "Irina", "Luca", "Miruna", "Nicu", "Oana", "Petru", "Roxana", "Sandu",
    "Teo", "Ursu", "Vera", "David", "Ema", "Fabi", "Geta", "Iulia", "Liviu", "Mara",
    "Nelu", "Otilia", "Pavel", "Rux", "Stef", "Toma", "Ada", "Beni", "Codrin", "Denis",
    "Eva", "Filip", "Greta", "Ilinca", "Jan", "Kira", "Lia", "Mihnea", "Nora", "Ovidiu",
    "Patrick", "Rica", "Silviu", "Tania", "Uta", "Vio", "Alin", "Boga", "Ciprian", "Doina",
    "Edi", "Fana", "Gina", "Hodo", "Inga", "Jeni", "Laur", "Momo", "Nuti", "Olga",
    "Puiu", "Ramona", "Sabin", "Timea", "Ulise", "Viorel"
]

HERE = os.path.dirname(os.path.abspath(__file__))

# --- load class metadata
klass = {}
with open(os.path.join(HERE, "HighSchool2013_metadata.txt"), encoding="utf-8") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            klass[int(p[0])] = p[1]

# --- load contact events (t i j Ci Cj)
rows = []
with open(os.path.join(HERE, "High-School_data_2013.csv"), encoding="utf-8") as f:
    for line in f:
        p = line.split()
        if len(p) >= 3:
            rows.append((int(p[0]), int(p[1]), int(p[2])))

# --- split into days by gaps > 2h
times = sorted(set(r[0] for r in rows))
bounds, start, prev = [], times[0], times[0]
for t in times[1:]:
    if t - prev > 7200:
        bounds.append((start, prev))
        start = t
    prev = t
bounds.append((start, prev))
day_start, day_end = bounds[DAY - 1]

# --- filter by day + classes, aggregate weights
keep = {n for n, c in klass.items() if c in CLASSES}
w = collections.Counter()
for t, i, j in rows:
    if day_start <= t <= day_end and i in keep and j in keep:
        a, b = (i, j) if i < j else (j, i)
        w[(a, b)] += 1

edges = [{"source": a, "target": b, "weight": c} for (a, b), c in w.items() if c >= MIN_WEIGHT]

used = set()
for e in edges:
    used.add(e["source"])
    used.add(e["target"])

# --- nodes with names assigned deterministically by sorted id
nodes = [{"id": n, "group": klass[n]} for n in sorted(used)]
for i, n in enumerate(nodes):
    n["name"] = NAMES[i % len(NAMES)]

meta = {
    "classes": CLASSES,
    "day": DAY,
    "min_weight": MIN_WEIGHT,
    "source": "SocioPatterns Thiers13",
    "cite": "R. Mastrandrea, J. Fournet, A. Barrat, PLoS ONE 10(9): e0136497 (2015)"
}

with open(os.path.join(HERE, "highschool-network.json"), "w", encoding="utf-8") as f:
    json.dump({"nodes": nodes, "edges": edges, "meta": meta}, f, ensure_ascii=False, indent=0)

# --- stats on the same slice
degrees = collections.Counter()
weighted = collections.Counter()
for e in edges:
    degrees[e["source"]] += 1
    degrees[e["target"]] += 1
    weighted[e["source"]] += e["weight"]
    weighted[e["target"]] += e["weight"]
for n in nodes:
    degrees.setdefault(n["id"], 0)
    weighted.setdefault(n["id"], 0)

deg_list = sorted(degrees[n["id"]] for n in nodes)
mean_deg = round(sum(deg_list) / len(deg_list), 2)
median_deg = statistics.median(deg_list)
max_deg = max(deg_list)

# --- friendship paradox
adj = {n["id"]: set() for n in nodes}
for e in edges:
    adj[e["source"]].add(e["target"])
    adj[e["target"]].add(e["source"])
friends_mean = []
n_below = 0
for n in nodes:
    nid = n["id"]
    fs = adj[nid]
    if fs:
        fm = sum(degrees[f] for f in fs) / len(fs)
        friends_mean.append(fm)
        if degrees[nid] < fm:
            n_below += 1
mean_friends = round(sum(friends_mean) / len(friends_mean), 2) if friends_mean else 0.0
frac_below = round(n_below / len(nodes), 2)

# --- top by degree, by weighted degree
top_deg = sorted(nodes, key=lambda n: -degrees[n["id"]])[:5]
top_weighted = sorted(nodes, key=lambda n: -weighted[n["id"]])[:5]

stats = {
    "total": len(nodes),
    "edges": len(edges),
    "degrees": deg_list,
    "meanDegree": mean_deg,
    "medianDegree": median_deg,
    "maxDegree": max_deg,
    "friendshipParadox": {
        "meanNodeDegree": mean_deg,
        "meanFriendsDegree": mean_friends,
        "fractionBelow": frac_below
    },
    "topByDegree": [
        {"id": n["id"], "name": n["name"], "group": n["group"], "value": degrees[n["id"]]}
        for n in top_deg
    ],
    "topByWeighted": [
        {"id": n["id"], "name": n["name"], "group": n["group"], "value": weighted[n["id"]]}
        for n in top_weighted
    ]
}

with open(os.path.join(HERE, "highschool-stats.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print(f"{len(nodes)} noduri, {len(edges)} muchii.")
print(f"grad: mean={mean_deg}  median={median_deg}  max={max_deg}")
print(f"paradoxul prieteniei: elevii {mean_deg} vs prietenii {mean_friends} (fract sub media prietenilor: {frac_below})")
print("top grad:")
for t in top_deg[:3]:
    print(f"  {t['name']} (id {t['id']}, {t['group']}) grad {degrees[t['id']]}")
print("top timp petrecut (sum ponderi):")
for t in top_weighted[:3]:
    print(f"  {t['name']} (id {t['id']}, {t['group']}) suma {weighted[t['id']]}")
