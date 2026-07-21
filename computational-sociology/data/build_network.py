"""Filtreaza reteaua Thiers13 la o felie lizibila si scrie mai multe JSON-uri:
   highschool-network.json       — noduri (cu nume) + muchii peste MIN_WEIGHT
   highschool-stats.json         — statistici agregate
   highschool-hours.json         — snapshoturi orare ale zilei
   highschool-pairs.json         — toate perechile (weight >= 1) intre nodurile pastrate
   highschool-three-networks.json — sub-retele: senzor, jurnal, prietenie, facebook

   Ruleaza din data/:  py build_network.py"""
import json, collections, os, statistics
from collections import defaultdict, Counter, deque

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

# --- 1. metadata (class + sex)
klass = {}
sex = {}
with open(os.path.join(HERE, "HighSchool2013_metadata.txt"), encoding="utf-8") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            klass[int(p[0])] = p[1]
        if len(p) >= 3:
            sex[int(p[0])] = p[2]

# --- 2. contact events
rows = []
with open(os.path.join(HERE, "High-School_data_2013.csv"), encoding="utf-8") as f:
    for line in f:
        p = line.split()
        if len(p) >= 3:
            rows.append((int(p[0]), int(p[1]), int(p[2])))

# --- 3. split days by gaps > 2h
times = sorted(set(r[0] for r in rows))
bounds, start, prev = [], times[0], times[0]
for t in times[1:]:
    if t - prev > 7200:
        bounds.append((start, prev))
        start = t
    prev = t
bounds.append((start, prev))
day_start, day_end = bounds[DAY - 1]

# --- 4. aggregate weights on day 1 for pairs in the chosen classes
keep = {n for n, c in klass.items() if c in CLASSES}
w = Counter()
for t, i, j in rows:
    if day_start <= t <= day_end and i in keep and j in keep:
        a, b = (i, j) if i < j else (j, i)
        w[(a, b)] += 1

edges = [{"source": a, "target": b, "weight": c} for (a, b), c in w.items() if c >= MIN_WEIGHT]

used = set()
for e in edges:
    used.add(e["source"])
    used.add(e["target"])

# --- 5. nodes (sorted by id, names assigned deterministically)
nodes = [{"id": n, "group": klass[n], "sex": sex.get(n, "Unknown")} for n in sorted(used)]
for i, n in enumerate(nodes):
    n["name"] = NAMES[i % len(NAMES)]

group_by = {n["id"]: n["group"] for n in nodes}
sex_by   = {n["id"]: n["sex"]   for n in nodes}
name_by  = {n["id"]: n["name"]  for n in nodes}

# --- 6. basic degree stats
degrees, weighted = Counter(), Counter()
adj = defaultdict(set)
for e in edges:
    degrees[e["source"]]  += 1
    degrees[e["target"]]  += 1
    weighted[e["source"]] += e["weight"]
    weighted[e["target"]] += e["weight"]
    adj[e["source"]].add(e["target"])
    adj[e["target"]].add(e["source"])
for n in nodes:
    degrees.setdefault(n["id"], 0)
    weighted.setdefault(n["id"], 0)

deg_list       = sorted(degrees[n["id"]] for n in nodes)
mean_deg_raw   = sum(deg_list) / len(deg_list)
mean_deg       = round(mean_deg_raw, 1)
median_deg     = statistics.median(deg_list)
max_deg        = max(deg_list)

# --- 7. friendship paradox
friends_mean = []
n_below = 0
for n in nodes:
    fs = adj[n["id"]]
    if fs:
        fm = sum(degrees[f] for f in fs) / len(fs)
        friends_mean.append(fm)
        if degrees[n["id"]] < fm:
            n_below += 1
mean_friends = round(sum(friends_mean) / len(friends_mean), 1) if friends_mean else 0.0
pct_below    = round(100 * n_below / len(nodes))
frac_below   = round(n_below / len(nodes), 2)

# --- 8. top by degree, top by weighted degree
top_deg      = sorted(nodes, key=lambda n: -degrees[n["id"]])[:5]
top_weighted = sorted(nodes, key=lambda n: -weighted[n["id"]])[:5]

# --- 9. class frequencies (per class: n, nF, nM, nUnk)
class_freq = {}
for c in CLASSES:
    kn = [n for n in nodes if n["group"] == c]
    class_freq[c] = {
        "n":    len(kn),
        "nF":   sum(1 for n in kn if n["sex"] == "F"),
        "nM":   sum(1 for n in kn if n["sex"] == "M"),
        "nUnk": sum(1 for n in kn if n["sex"] not in ("F", "M")),
    }

# --- 10. class mean degree + list for strip overlay
class_mean_degree = {}
for c in CLASSES:
    cd = [degrees[n["id"]] for n in nodes if n["group"] == c]
    class_mean_degree[c] = {
        "mean":    round(sum(cd) / len(cd), 1) if cd else 0.0,
        "degrees": cd,
    }

# --- 11. class contact split (% intern vs extern) + global inter-class %
total_weight = sum(e["weight"] for e in edges)
class_contact_split = {}
for c in CLASSES:
    internal, external = 0, 0
    for e in edges:
        gs, gt = group_by[e["source"]], group_by[e["target"]]
        if gs == c and gt == c:
            internal += e["weight"]
        elif gs == c or gt == c:
            external += e["weight"]
    tot = internal + external
    class_contact_split[c] = {
        "internalPct": round(100 * internal / tot, 1) if tot else 0.0,
        "externalPct": round(100 * external / tot, 1) if tot else 0.0,
    }
inter_class_weight = sum(e["weight"] for e in edges if group_by[e["source"]] != group_by[e["target"]])
inter_class_pct    = round(100 * inter_class_weight / total_weight, 1) if total_weight else 0.0
# alias for JSON placeholder syntax used in cards
class_contact_split["globalBetweenPct"] = inter_class_pct

# --- 12. majority illusion (seed = top 4 by degree)
seed_ids = [n["id"] for n in top_deg[:4]]
seed_set = set(seed_ids)
n_with_nb, n_illusion = 0, 0
for n in nodes:
    nbs = adj[n["id"]]
    if not nbs:
        continue
    n_with_nb += 1
    if sum(1 for x in nbs if x in seed_set) / len(nbs) >= 0.5:
        n_illusion += 1
pct_exposed = round(100 * n_illusion / n_with_nb, 1) if n_with_nb else 0.0
majority_illusion = {
    "seedIds":         seed_ids,
    "seedNames":       [name_by[s] for s in seed_ids],
    "nSeeds":          len(seed_ids),
    "seedCount":       len(seed_ids),
    "nWithNeighbors":  n_with_nb,
    "pctExposed":      pct_exposed,
    "pctSeeMajority":  pct_exposed,
}

# --- 13. small-world on largest component
def find_components(adj_map, ids):
    seen, comps = set(), []
    for start_id in ids:
        if start_id in seen:
            continue
        comp, stack = [], [start_id]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x); comp.append(x)
            for y in adj_map.get(x, ()):
                if y not in seen:
                    stack.append(y)
        comps.append(comp)
    return comps

def bfs_dists(source, adj_map):
    dist = {source: 0}
    q = deque([source])
    while q:
        x = q.popleft()
        for y in adj_map.get(x, ()):
            if y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)
    return dist

comps = find_components(adj, [n["id"] for n in nodes])
comps.sort(key=len, reverse=True)
big = set(comps[0]) if comps else set()

if big:
    all_dists, diameter = [], 0
    for s in big:
        dists = bfs_dists(s, adj)
        for t, d in dists.items():
            if t != s and t in big:
                all_dists.append(d)
                if d > diameter:
                    diameter = d
    mean_path = round(sum(all_dists) / len(all_dists), 1) if all_dists else 0.0
    small_world = {
        "n": len(big),
        "meanPathLen": mean_path,
        "avgPath":     mean_path,
        "diameter":    diameter,
    }
else:
    small_world = {"n": 0, "meanPathLen": 0.0, "avgPath": 0.0, "diameter": 0}

# --- 14. homofilie sex: % timp de contact same-sex vs asteptat la amestec aleator
same_sex_weight, known_pair_weight = 0, 0
for e in edges:
    s1, s2 = sex_by[e["source"]], sex_by[e["target"]]
    if s1 in ("F", "M") and s2 in ("F", "M"):
        known_pair_weight += e["weight"]
        if s1 == s2:
            same_sex_weight += e["weight"]
observed_same_sex_pct = round(100 * same_sex_weight / known_pair_weight, 1) if known_pair_weight else 0.0
nF = sum(1 for n in nodes if n["sex"] == "F")
nM = sum(1 for n in nodes if n["sex"] == "M")
n_known = nF + nM
if n_known >= 2:
    p_FF = nF * (nF - 1) / (n_known * (n_known - 1))
    p_MM = nM * (nM - 1) / (n_known * (n_known - 1))
    expected_same_sex_pct = round(100 * (p_FF + p_MM), 1)
else:
    expected_same_sex_pct = 0.0
homophily_sex = {
    "observedPct": observed_same_sex_pct,
    "expectedPct": expected_same_sex_pct,
    "nF": nF,
    "nM": nM,
}

# --- 15. spread ranking (BFS reachability = componenta pentru prag = MIN_WEIGHT)
spread = {n["id"]: len(bfs_dists(n["id"], adj)) for n in nodes}
top_spread = sorted(nodes, key=lambda x: -spread[x["id"]])[:5]
spread_ranking = {
    "threshold": MIN_WEIGHT,
    "max":       max(spread.values()) if spread else 0,
    "champions": [
        {"id": n["id"], "name": n["name"], "group": n["group"], "value": spread[n["id"]]}
        for n in top_spread
    ],
}

# --- 16. edgeCountByThreshold (asupra celor 93 elevi)
edge_count_by_threshold = {}
for t in range(1, 11):
    edge_count_by_threshold[str(t)] = sum(
        1 for (a, b), c in w.items() if c >= t and a in used and b in used
    )

# --- 17. hourly snapshots (ziua 1 impartita in ore) -> highschool-hours.json
hour_len = 3600
hour_edges_by_hour = defaultdict(Counter)
for t, i, j in rows:
    if day_start <= t <= day_end and i in used and j in used:
        h = (t - day_start) // hour_len
        a, b = (i, j) if i < j else (j, i)
        hour_edges_by_hour[h][(a, b)] += 1
hourly = []
for h in sorted(hour_edges_by_hour):
    hourly.append({
        "hour":  int(h),
        "edges": [
            {"source": a, "target": b, "weight": c}
            for (a, b), c in hour_edges_by_hour[h].items()
        ],
    })

# --- 18. edgesAllWeights (weight >= 1 pe cei 93 elevi) -> highschool-pairs.json
all_pairs = [
    {"source": a, "target": b, "weight": c}
    for (a, b), c in w.items() if c >= 1 and a in used and b in used
]

# --- 19. three networks: diaries, friendship, facebook
def load_pairs(fname, kind):
    """kind: 'weight' (i j w), 'flag' (i j 0/1), 'plain' (i j)"""
    path = os.path.join(HERE, fname)
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) < 2:
                continue
            i, j = int(p[0]), int(p[1])
            if kind == "weight":
                out.append((i, j, int(p[2]) if len(p) >= 3 else 1))
            elif kind == "flag":
                out.append((i, j, int(p[2]) if len(p) >= 3 else 1))
            else:
                out.append((i, j, 1))
    return out

diaries_raw    = load_pairs("Contact-diaries-network_data_2013.csv", "weight")
friendship_raw = load_pairs("Friendship-network_data_2013.csv",      "plain")
facebook_raw   = load_pairs("Facebook-known-pairs_data_2013.csv",    "flag")

diaries_edges    = [(i, j, ww) for (i, j, ww) in diaries_raw    if i in used and j in used]
friendship_edges = [(i, j, ww) for (i, j, ww) in friendship_raw if i in used and j in used]
facebook_edges   = [(i, j, ww) for (i, j, ww) in facebook_raw   if i in used and j in used and ww == 1]

def sym_pairs(triples):
    s = set()
    for (i, j, _) in triples:
        a, b = (i, j) if i < j else (j, i)
        s.add((a, b))
    return s

diaries_sym    = sym_pairs(diaries_edges)
friendship_sym = sym_pairs(friendship_edges)
facebook_sym   = sym_pairs(facebook_edges)
sensor_sym     = set((e["source"], e["target"]) if e["source"] < e["target"] else (e["target"], e["source"]) for e in edges)

def reciprocity_pct(triples):
    forward = set((i, j) for (i, j, _) in triples)
    if not forward:
        return 0.0
    return round(100 * sum(1 for (i, j) in forward if (j, i) in forward) / len(forward), 1)

def overlap_pct(A, B):
    if not A or not B:
        return 0.0
    return round(100 * len(A & B) / min(len(A), len(B)), 1)

def nodes_of(triples):
    s = set()
    for (i, j, _) in triples:
        s.add(i); s.add(j)
    return s

friendship_recip = reciprocity_pct(friendship_edges)
diaries_recip    = reciprocity_pct(diaries_edges)
ovl_sensor_diaries  = overlap_pct(sensor_sym, diaries_sym)
ovl_sensor_facebook = overlap_pct(sensor_sym, facebook_sym)
ovl_diaries_facebook = overlap_pct(diaries_sym, facebook_sym)

three_networks = {
    "sensorPairs":              len(sensor_sym),
    "diariesPairs":             len(diaries_sym),
    "friendshipPairs":          len(friendship_sym),
    "facebookPairs":            len(facebook_sym),
    "diariesReciprocityPct":    diaries_recip,
    "friendshipReciprocityPct": friendship_recip,
    "reciprocityPct":           friendship_recip,
    "overlaps": {
        "sensorVsDiaries":   ovl_sensor_diaries,
        "sensorVsFacebook":  ovl_sensor_facebook,
        "diariesVsFacebook": ovl_diaries_facebook,
    },
    "overlapSensorDeclared": ovl_sensor_diaries,
    "overlapSensorFacebook": ovl_sensor_facebook,
    "overlapDeclaredFacebook": ovl_diaries_facebook,
    "nodesInSensor":     len(used),
    "nodesInDiaries":    len(nodes_of(diaries_edges) & used),
    "nodesInFriendship": len(nodes_of(friendship_edges) & used),
    "nodesInFacebook":   len(nodes_of(facebook_edges) & used),
}

three_networks_data = {
    "nodes": [{"id": n["id"], "name": n["name"], "group": n["group"]} for n in nodes],
    "sensor":     [{"source": a, "target": b} for (a, b) in sorted(sensor_sym)],
    "diaries":    [{"source": a, "target": b} for (a, b) in sorted(diaries_sym)],
    "friendship": [{"source": a, "target": b} for (a, b) in sorted(friendship_sym)],
    "facebook":   [{"source": a, "target": b} for (a, b) in sorted(facebook_sym)],
}

# --- 20. meta pentru highschool-network.json
meta = {
    "classes":    CLASSES,
    "day":        DAY,
    "min_weight": MIN_WEIGHT,
    "source":     "SocioPatterns Thiers13",
    "cite":       "R. Mastrandrea, J. Fournet, A. Barrat, PLoS ONE 10(9): e0136497 (2015)",
}

with open(os.path.join(HERE, "highschool-network.json"), "w", encoding="utf-8") as f:
    json.dump({"nodes": nodes, "edges": edges, "meta": meta}, f, ensure_ascii=False, indent=0)

# --- 21. stats
stats = {
    "total":         len(nodes),
    "edges":         len(edges),
    "degrees":       deg_list,
    "meanDegree":    mean_deg,
    "medianDegree":  median_deg,
    "maxDegree":     max_deg,
    "friendshipParadox": {
        # keys per spec (rounded 1 decimal, %)
        "meanDegree":       mean_deg,
        "meanFriendDegree": mean_friends,
        "pctBelow":         pct_below,
        # legacy keys pastrate ca nu spargem randari existente
        "meanNodeDegree":    mean_deg,
        "meanFriendsDegree": mean_friends,
        "fractionBelow":     frac_below,
    },
    "topByDegree": [
        {"id": n["id"], "name": n["name"], "group": n["group"], "value": degrees[n["id"]]}
        for n in top_deg
    ],
    "topByWeighted": [
        {"id": n["id"], "name": n["name"], "group": n["group"], "value": weighted[n["id"]]}
        for n in top_weighted
    ],
    "classFreq":            class_freq,
    "classMeanDegree":      class_mean_degree,
    "classContactSplit":    class_contact_split,
    "interClassPct":        inter_class_pct,
    "majorityIllusion":     majority_illusion,
    "smallWorld":           small_world,
    "homophilySex":         homophily_sex,
    "spreadRanking":        spread_ranking,
    "edgeCountByThreshold": edge_count_by_threshold,
    "hoursCount":           len(hourly),
    "threeNetworks":        three_networks,
}

with open(os.path.join(HERE, "highschool-stats.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

with open(os.path.join(HERE, "highschool-hours.json"), "w", encoding="utf-8") as f:
    json.dump({
        "nodes": [{"id": n["id"], "name": n["name"], "group": n["group"]} for n in nodes],
        "hours": hourly,
    }, f, ensure_ascii=False, indent=0)

with open(os.path.join(HERE, "highschool-pairs.json"), "w", encoding="utf-8") as f:
    json.dump({
        "nodes": [{"id": n["id"], "name": n["name"], "group": n["group"]} for n in nodes],
        "pairs": all_pairs,
    }, f, ensure_ascii=False, indent=0)

with open(os.path.join(HERE, "highschool-three-networks.json"), "w", encoding="utf-8") as f:
    json.dump(three_networks_data, f, ensure_ascii=False, indent=0)

# --- 22. summary la stdout
print(f"{len(nodes)} noduri, {len(edges)} muchii.")
print(f"grad: mean={mean_deg}  median={median_deg}  max={max_deg}")
print(f"paradoxul prieteniei: elev {mean_deg} vs prieteni {mean_friends}  pct sub: {pct_below}%")
print(f"clase (n, F, M, ?):")
for c, v in class_freq.items():
    print(f"  {c}: {v['n']} elevi ({v['nF']}F, {v['nM']}M, {v['nUnk']}?)  grad mediu {class_mean_degree[c]['mean']}")
print(f"contact intre clase: {inter_class_pct}%")
print(f"majority illusion: {majority_illusion['pctExposed']}% vad majoritatea prietenilor 'stiind' (seed {majority_illusion['seedNames']})")
print(f"small world: n={small_world['n']}  mean path={small_world['meanPathLen']}  diameter={small_world['diameter']}")
print(f"homofilie sex: observat {observed_same_sex_pct}%  asteptat {expected_same_sex_pct}%  (nF={nF}, nM={nM})")
print(f"spread max: {spread_ranking['max']} elevi. Campioni: {[c['name'] for c in spread_ranking['champions'][:3]]}")
print(f"muchii pe prag: {edge_count_by_threshold}")
print(f"snapshoturi orare: {len(hourly)}")
print(f"trei retele: senzor={three_networks['sensorPairs']}  jurnal={three_networks['diariesPairs']}  prietenie={three_networks['friendshipPairs']}  facebook={three_networks['facebookPairs']}")
print(f"  reciprocitate jurnal={three_networks['diariesReciprocityPct']}%  prietenie={three_networks['friendshipReciprocityPct']}%")
print(f"  suprapunere senzor∩jurnal={three_networks['overlaps']['sensorVsDiaries']}%  senzor∩facebook={three_networks['overlaps']['sensorVsFacebook']}%  jurnal∩facebook={three_networks['overlaps']['diariesVsFacebook']}%")
