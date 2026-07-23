"""Filtreaza reteaua Thiers13 si scrie mai multe JSON-uri:
   highschool-network.json         noduri (cu nume) + muchii peste MIN_WEIGHT
   highschool-stats.json           statistici agregate (felia 3 clase + fullSchool 9 clase)
   highschool-hours.json           snapshoturi orare ale zilei
   highschool-pairs.json           toate perechile (weight >= 1) intre nodurile pastrate
   highschool-three-networks.json  sub-retele: senzor, jurnal, prietenie, facebook

   Ruleaza din data/:  py build_network.py"""
import json, collections, os, statistics, random
from collections import defaultdict, Counter, deque


# --- helper: label propagation communities (deterministic, weighted) --------
def label_propagation(node_ids, adj_map, weight_map, seed=42, max_iter=40):
    rnd = random.Random(seed)
    label = {n: n for n in node_ids}
    order = sorted(node_ids)
    for _ in range(max_iter):
        rnd.shuffle(order)
        changed = False
        for x in order:
            neighbors = adj_map.get(x, [])
            if not neighbors:
                continue
            tally = Counter()
            for y in neighbors:
                key = (x, y) if x < y else (y, x)
                w_xy = weight_map.get(key, 1)
                tally[label[y]] += w_xy
            best, best_w = None, -1
            for l, w_l in tally.items():
                if w_l > best_w or (w_l == best_w and (best is None or l < best)):
                    best_w = w_l
                    best = l
            if best is not None and label[x] != best:
                label[x] = best
                changed = True
        if not changed:
            break
    unique = sorted(set(label.values()))
    remap = {u: i for i, u in enumerate(unique)}
    return {n: remap[label[n]] for n in node_ids}


def bfs_reach(source, adj_map):
    seen = {source}
    q = deque([source])
    while q:
        x = q.popleft()
        for y in adj_map.get(x, ()):
            if y not in seen:
                seen.add(y)
                q.append(y)
    return seen


# --- Full multi-level Louvain with resolution parameter --------------------
def louvain_multilevel(node_ids, edges_with_weights, resolution=1.0, seed=42, max_levels=20, max_local_iter=50):
    """Louvain community detection. Weighted, undirected.
    edges_with_weights: iterable of (u, v, w).
    Returns dict node_id -> community_label (0-indexed by size, largest first).
    """
    rnd = random.Random(seed)

    def build_adj_dd(nodes, edges):
        adj = {n: {} for n in nodes}
        for u, v, w in edges:
            adj[u][v] = adj[u].get(v, 0) + w
            if u != v:
                adj[v][u] = adj[v].get(u, 0) + w
        return adj

    def local_move(adj):
        ki = {n: sum(adj[n].values()) for n in adj}
        m = sum(ki.values()) / 2.0
        if m == 0:
            return {n: n for n in adj}
        node2comm = {n: n for n in adj}
        sigma_tot = {n: ki[n] for n in adj}
        for _ in range(max_local_iter):
            order = list(adj.keys())
            rnd.shuffle(order)
            moved = 0
            for i in order:
                ci = node2comm[i]
                w_to = defaultdict(float)
                for j, w in adj[i].items():
                    if j == i:
                        continue
                    w_to[node2comm[j]] += w
                sigma_tot[ci] -= ki[i]
                best_c = ci
                best = w_to.get(ci, 0.0) - resolution * sigma_tot[ci] * ki[i] / (2 * m)
                for c, k_ic in w_to.items():
                    if c == ci:
                        continue
                    score = k_ic - resolution * sigma_tot[c] * ki[i] / (2 * m)
                    if score > best + 1e-12:
                        best = score
                        best_c = c
                sigma_tot[best_c] += ki[i]
                if best_c != ci:
                    node2comm[i] = best_c
                    moved += 1
            if moved == 0:
                break
        return node2comm

    def aggregate(adj, node2comm):
        new_adj = defaultdict(lambda: defaultdict(float))
        for u, nbrs in adj.items():
            cu = node2comm[u]
            for v, w in nbrs.items():
                new_adj[cu][node2comm[v]] += w
        return {c: dict(nbrs) for c, nbrs in new_adj.items()}

    edges_list = list(edges_with_weights)
    adj = build_adj_dd(list(node_ids), edges_list)
    orig_to_super = {n: n for n in node_ids}
    for _ in range(max_levels):
        n2c = local_move(adj)
        orig_to_super = {o: n2c[s] for o, s in orig_to_super.items()}
        if len(set(n2c.values())) == len(adj):
            break
        adj = aggregate(adj, n2c)

    # Re-label communities so that community 0 is the largest, 1 the next, etc.
    comm_sizes = Counter(orig_to_super.values())
    ordered = [c for c, _ in comm_sizes.most_common()]
    remap = {old: new for new, old in enumerate(ordered)}
    return {n: remap[orig_to_super[n]] for n in node_ids}


def _partition_metrics(labels, klass_map, node_ids):
    """Compute generous match rate, ARI, NMI vs class partition, size distribution."""
    import math as _math
    comms = defaultdict(list)
    for n in node_ids:
        comms[labels[n]].append(n)
    sizes = sorted((len(c) for c in comms.values()), reverse=True)
    # generous match
    maj = {c: Counter(klass_map[n] for n in ns).most_common(1)[0][0] for c, ns in comms.items()}
    matched = sum(1 for n in node_ids if klass_map[n] == maj[labels[n]])
    generous = round(100 * matched / len(node_ids), 1) if node_ids else 0.0
    # ARI
    a = [labels[n] for n in node_ids]
    b = [klass_map[n] for n in node_ids]
    n = len(node_ids)
    ca = Counter(a); cb = Counter(b)
    joint = Counter(zip(a, b))
    def C(k): return k * (k - 1) // 2
    sum_j = sum(C(v) for v in joint.values())
    sum_a = sum(C(v) for v in ca.values())
    sum_b = sum(C(v) for v in cb.values())
    total = C(n)
    if total == 0:
        ari = 0.0
    else:
        expected = sum_a * sum_b / total
        maxi = (sum_a + sum_b) / 2
        ari = 0.0 if maxi == expected else round((sum_j - expected) / (maxi - expected), 3)
    # NMI
    def H(counter):
        return -sum((c/n) * _math.log(c/n) for c in counter.values() if c > 0)
    hj = H(joint); ha = H(ca); hb = H(cb)
    mi = ha + hb - hj
    denom = (ha + hb) / 2 if (ha + hb) > 0 else 1
    nmi = round(mi / denom, 3) if denom else 0.0
    return {
        "n": len(comms),
        "sizes": sizes,
        "matchGenerous": generous,
        "ari": ari,
        "nmi": nmi,
    }


# --- new diffusion model: time-limited + strong-ties only --------------------
def build_top_adj(edges_list, k):
    """For each node, keep only its K strongest ties by weight.
       Ties broken by lower neighbor id (deterministic)."""
    ns = defaultdict(list)
    for a, b, w in edges_list:
        ns[a].append((w, b))
        ns[b].append((w, a))
    top = {}
    for n, items in ns.items():
        items.sort(key=lambda x: (-x[0], x[1]))
        top[n] = [x[1] for x in items[:k]]
    return top


def diffuse_limited(seeds, adj_top, pasi):
    """Multi-source deterministic BFS bounded to `pasi` rounds.
       Each carrier transmits ONLY to its top-K contacts (via adj_top)."""
    reached = set(seeds)
    frontier = list(seeds)
    for _ in range(pasi):
        nxt = []
        for x in frontier:
            for y in adj_top.get(x, []):
                if y not in reached:
                    reached.add(y)
                    nxt.append(y)
        frontier = nxt
    return reached


def compute_slice_metrics(nodes_list, edges_list, klass_map, sex_map, name_map, tag, seed=42, pasi=4, max_t=4):
    """Given a slice (nodes + edges), compute all metrics for TRANSA 0.
       nodes_list: list of int ids.
       edges_list: list of tuples (a, b, weight) with a < b."""
    node_ids = sorted(nodes_list)
    n = len(node_ids)

    adj = defaultdict(set)
    weight_map = {}
    for a, b, ww in edges_list:
        adj[a].add(b)
        adj[b].add(a)
        weight_map[(a, b)] = ww

    degrees = Counter()
    weighted = Counter()
    for a, b, ww in edges_list:
        degrees[a] += 1
        degrees[b] += 1
        weighted[a] += ww
        weighted[b] += ww
    for x in node_ids:
        degrees.setdefault(x, 0)
        weighted.setdefault(x, 0)

    # --- components
    seen = set()
    comps = []
    for start in node_ids:
        if start in seen:
            continue
        comp = []
        stack = [start]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            for y in adj.get(x, ()):
                if y not in seen:
                    stack.append(y)
        comps.append(sorted(comp))
    comps.sort(key=len, reverse=True)

    def id_name(x):
        return {"id": x, "name": name_map.get(x, str(x))}

    n_isolated = sum(1 for c in comps if len(c) == 1)
    components = {
        "n":                len(comps),
        "sizes":            [len(c) for c in comps],
        "largest":          len(comps[0]) if comps else 0,
        "isolated":         n_isolated,
        "smallCompNodes":   [[id_name(x) for x in c] for c in comps if len(c) <= 4],
    }

    # --- communities via label propagation (LEGACY, kept for backward-compat)
    community = label_propagation(node_ids, adj, weight_map, seed=seed)
    n_communities = len(set(community.values()))

    # contingency: community x class
    contingency = defaultdict(Counter)
    for x in node_ids:
        contingency[community[x]][klass_map[x]] += 1

    comm_majority = {}
    for c_id, ct in contingency.items():
        cls, _ = ct.most_common(1)[0]
        comm_majority[c_id] = cls

    match_count = sum(1 for x in node_ids if klass_map[x] == comm_majority.get(community[x]))
    pct_match = round(100 * match_count / n, 1) if n else 0.0

    mismatched = []
    for x in node_ids:
        cls = klass_map[x]
        maj = comm_majority.get(community[x])
        if cls != maj:
            mismatched.append({
                "id":                     x,
                "name":                   name_map.get(x, str(x)),
                "class":                  cls,
                "community":              community[x],
                "communityMajorityClass": maj,
            })

    # --- LOUVAIN multi-level at three resolutions.  Fragmentation-robust
    # detection; label propagation left as a legacy artifact.
    louvain_edges = [(a, b, w) for a, b, w in edges_list]
    louvain_results = {}
    for res_key, res_value in (("res05", 0.5), ("res10", 1.0), ("res20", 2.0)):
        lv_labels = louvain_multilevel(node_ids, louvain_edges, resolution=res_value, seed=seed)
        metrics = _partition_metrics(lv_labels, klass_map, node_ids)
        # contingency: community x class
        lv_contingency = defaultdict(Counter)
        for x in node_ids:
            lv_contingency[lv_labels[x]][klass_map[x]] += 1
        lv_majority = {c_id: ct.most_common(1)[0][0] for c_id, ct in lv_contingency.items()}
        # per-community summary
        comm_summary = []
        for c_id, ct in sorted(lv_contingency.items(), key=lambda kv: -sum(kv[1].values())):
            members_here = [x for x in node_ids if lv_labels[x] == c_id]
            dominant = lv_majority[c_id]
            dom_count = ct.get(dominant, 0)
            comm_summary.append({
                "id":            c_id,
                "size":          len(members_here),
                "dominant":      dominant,
                "dominantFriendly": CLASS_NAMES.get(dominant, dominant),
                "dominantPct":   round(100 * dom_count / len(members_here), 1),
                "composition":   [
                    {"class": cls, "classFriendly": CLASS_NAMES.get(cls, cls), "count": cnt}
                    for cls, cnt in ct.most_common()
                ],
                "memberIds":     members_here,
                "memberNames":   [name_map.get(x, str(x)) for x in members_here],
            })
        louvain_results[res_key] = {
            "resolution":     res_value,
            "byId":           {str(x): lv_labels[x] for x in node_ids},
            "n":              metrics["n"],
            "sizes":          metrics["sizes"],
            "ari":            metrics["ari"],
            "nmi":            metrics["nmi"],
            "matchGenerous":  metrics["matchGenerous"],
            "communities":    comm_summary,
        }

    # --- openness: number of contacts OUTSIDE the person's own class.
    # This is the pedagogical definition used across the lesson: a student's
    # "deschidere" is how many of their contacts live in a different class,
    # counted raw (not a fraction, not a set of distinct classes, not the
    # count of Louvain communities they touch). It reads at a glance and
    # produces the character contrasts the story relies on:
    #   - Antoine (popular) has 19 contacts but only 1 outside Bio C
    #   - Léa is #1 at 10 out-of-class contacts
    #   - Chloé has 0 out-of-class contacts
    openness = {}
    for x in node_ids:
        own = klass_map.get(x)
        openness[x] = sum(1 for y in adj.get(x, ()) if klass_map.get(y) != own)

    # --- reach: NEW MODEL. Diffusion bounded to `pasi` rounds, each carrier
    # transmits only to its `max_t` strongest contacts (by edge weight).
    adj_top = build_top_adj(edges_list, max_t)
    reach = {x: diffuse_limited([x], adj_top, pasi) for x in node_ids}
    reach_size = {x: len(reach[x]) for x in node_ids}

    # For izolat: which nodes are never reached FROM SOMEONE ELSE
    in_reach = Counter()
    for source in node_ids:
        for y in reach[source]:
            in_reach[y] += 1
    unreachable_ids = [x for x in node_ids if in_reach[x] == 1]  # only self reaches self

    # --- characters
    star_id = max(node_ids, key=lambda x: (degrees[x], -x))
    bridge_id = max(node_ids, key=lambda x: (openness[x], -degrees[x], -x))
    med_deg = statistics.median([degrees[x] for x in node_ids])
    # Discretul: popularitate SUB mediana, dar ACOPERIRE (noul model) in top 10% din scoala.
    reach_sorted = sorted(reach_size.values(), reverse=True)
    top10_reach = reach_sorted[max(0, int(len(reach_sorted) * 0.10) - 1)] if reach_sorted else 0
    discreet_cands = sorted(
        [x for x in node_ids if degrees[x] < med_deg and reach_size[x] >= top10_reach and x != star_id and x != bridge_id],
        key=lambda x: (-reach_size[x], degrees[x], x),
    )
    if not discreet_cands:
        # Fallback: relax to top 20% reach
        top20_reach = reach_sorted[max(0, int(len(reach_sorted) * 0.20) - 1)] if reach_sorted else 0
        discreet_cands = sorted(
            [x for x in node_ids if degrees[x] < med_deg and reach_size[x] >= top20_reach and x != star_id and x != bridge_id],
            key=lambda x: (-reach_size[x], degrees[x], x),
        )
    discreet_id = discreet_cands[0] if discreet_cands else min(
        (x for x in node_ids if x != star_id and x != bridge_id),
        key=lambda x: (degrees[x], -reach_size[x], x),
    )

    # Izolatul: prefera un nod ne-atins de nimeni CU GRAD 1 (cel mai izolat posibil).
    # Al doilea criteriu: aceeasi clasa cu puntea (Luca), pentru rezonanta narativa.
    small_comp_set = {x for c in comps if len(c) < 3 for x in c}
    used_char_ids = {star_id, bridge_id, discreet_id}
    # Pastreaza doar cei neatinsi cu grad 1
    unr_deg1 = [x for x in unreachable_ids if degrees[x] == 1 and x not in used_char_ids]
    # Prioritizeaza cei din clasa PSI* (Inginerie) daca exista, pentru legatura narativa cu Luca
    unr_deg1_ing = [x for x in unr_deg1 if klass_map.get(x) == "PSI*"]
    if unr_deg1_ing:
        isolated_cands = sorted(unr_deg1_ing, key=lambda x: x)
    elif unr_deg1:
        isolated_cands = sorted(unr_deg1, key=lambda x: x)
    else:
        # fallback: orice neatins
        isolated_cands = sorted([x for x in unreachable_ids if x not in used_char_ids], key=lambda x: (degrees[x], x))
    if not isolated_cands:
        isolated_cands = sorted([x for x in small_comp_set if x not in used_char_ids], key=lambda x: (degrees[x], x))
    if not isolated_cands:
        min_deg_ = min(degrees[x] for x in node_ids if x not in used_char_ids)
        isolated_cands = sorted(
            [x for x in node_ids if degrees[x] == min_deg_ and x not in used_char_ids],
            key=lambda x: (reach_size[x], openness[x], x),
        )
    isolated_id = isolated_cands[0] if isolated_cands else min(node_ids, key=lambda x: (degrees[x], x))

    def char_dict(nid):
        return {
            "id":         nid,
            "name":       name_map.get(nid, str(nid)),
            "class":      klass_map[nid],
            "popularity": degrees[nid],
            "openness":   openness[nid],
            "reach":      reach_size[nid],
        }

    # --- Role IDs pinned from Phase 1 analysis on the full 299-node network.
    # These override the older heuristic characters below.
    ROLE_IDS = {
        "vedeta":    117,
        "campion":   778,
        "surpriza":  1218,
        "puntea":    1332,
        "dependent": 276,
        "izolat":    1519,
    }

    # Precompute ranks so characters expose them for text placeholders.
    _rank_by_reach     = {nid: r + 1 for r, nid in enumerate(sorted(node_ids, key=lambda x: (-reach_size[x], x)))}
    _rank_by_pop       = {nid: r + 1 for r, nid in enumerate(sorted(node_ids, key=lambda x: (-degrees[x], x)))}
    _rank_by_openness  = {nid: r + 1 for r, nid in enumerate(sorted(node_ids, key=lambda x: (-openness[x], x)))}
    _reach2 = {x: len(diffuse_limited([x], adj_top, 2)) for x in node_ids}
    _rank_by_reach2    = {nid: r + 1 for r, nid in enumerate(sorted(node_ids, key=lambda x: (-_reach2[x], x)))}

    def role_dict(nid):
        if nid not in node_ids:
            return None
        d = char_dict(nid)
        own = klass_map.get(nid, "?")
        neighbor_classes = {klass_map.get(y, "?") for y in adj.get(nid, ())}
        neighbor_classes.discard(own)
        d["groups"] = len(neighbor_classes) + 1
        d["groupsOut"] = len(neighbor_classes)
        d["outClassContacts"] = sum(1 for y in adj.get(nid, ()) if klass_map.get(y) != own)
        d["classFriendly"] = CLASS_NAMES.get(own, own)
        d["sex"] = sex_map.get(nid, "Unknown")
        d["rankReach"]     = _rank_by_reach.get(nid)
        d["rankPop"]       = _rank_by_pop.get(nid)
        d["rankOpenness"]  = _rank_by_openness.get(nid)
        d["rankReach2"]    = _rank_by_reach2.get(nid)
        # Split reach by inside/outside the character's own class, and by
        # class dominance. reachInClass is what {{sliceMetrics.characters.
        # vedeta.reachInClass}} resolves to in the story text.
        r_set = reach[nid]
        d["reachInClass"]  = sum(1 for x in r_set if klass_map.get(x) == own)
        d["reachOutClass"] = len(r_set) - d["reachInClass"]
        d["reachClassDist"] = [
            {"class": k, "classFriendly": CLASS_NAMES.get(k, k), "count": v}
            for k, v in sorted(Counter(klass_map.get(x, "?") for x in r_set).items(), key=lambda kv: -kv[1])
        ]
        return d

    roles = {k: role_dict(v) for k, v in ROLE_IDS.items()}

    characters = {
        # legacy heuristic picks (kept so older cards keep resolving)
        "star":     char_dict(star_id),
        "bridge":   char_dict(bridge_id),
        "discreet": char_dict(discreet_id),
        "isolated": char_dict(isolated_id),
        # canonical role picks used by the lesson
        "vedeta":    roles["vedeta"],
        "campion":   roles["campion"],
        "surpriza":  roles["surpriza"],
        "puntea":    roles["puntea"],
        "dependent": roles["dependent"],
        "izolat":    roles["izolat"],
    }

    # --- strategies + coverage (using NEW LIMITED DIFFUSION MODEL)
    # Coverage of a set of seeds = |diffuse_limited(seeds, adj_top, pasi)|
    def coverage(seeds):
        s = diffuse_limited(list(seeds), adj_top, pasi)
        return len(s), s

    top3_pop = sorted(node_ids, key=lambda x: (-degrees[x], x))[:3]
    top3_open = sorted(node_ids, key=lambda x: (-openness[x], -degrees[x], x))[:3]

    comm_sizes = Counter(community[x] for x in node_ids)
    top_comms = [c_id for c_id, _ in comm_sizes.most_common(3)]
    one_each_comm = []
    for c_id in top_comms:
        cands = [x for x in node_ids if community[x] == c_id]
        best = max(cands, key=lambda x: degrees[x])
        one_each_comm.append(best)

    # Greedy: pick seed that maximally EXTENDS current joint coverage under the limited model.
    greedy = []
    covered = set()
    for _ in range(3):
        best_id, best_add = None, -1
        for x in node_ids:
            if x in greedy:
                continue
            new_covered = diffuse_limited(greedy + [x], adj_top, pasi)
            add = len(new_covered) - len(covered)
            if add > best_add or (add == best_add and (best_id is None or x < best_id)):
                best_add = add
                best_id = x
        if best_id is not None:
            greedy.append(best_id)
            covered = diffuse_limited(greedy, adj_top, pasi)

    rnd2 = random.Random(seed + 1)
    random_covs = []
    for _ in range(30):
        seeds3 = rnd2.sample(node_ids, min(3, len(node_ids)))
        cov3, _ = coverage(seeds3)
        random_covs.append(cov3)

    def strat_dict(seeds):
        cov, _ = coverage(seeds)
        return {
            "seeds":    [id_name(s) for s in seeds],
            "coverage": cov,
        }

    strategies = {
        "topPopular":    strat_dict(top3_pop),
        "topOpen":       strat_dict(top3_open),
        "oneEachComm":   strat_dict(one_each_comm),
        "greedy":        strat_dict(greedy),
        "randomMean":    round(sum(random_covs) / len(random_covs), 1) if random_covs else 0.0,
        "randomMin":     min(random_covs) if random_covs else 0,
        "randomMax":     max(random_covs) if random_covs else 0,
        "pasi":          pasi,
        "maxTransmiteri": max_t,
    }
    # topSingle: cine ia cel mai bun scor cu 1 seminta singura
    best_solo = max(node_ids, key=lambda x: (reach_size[x], -x))
    top_by_reach = sorted(node_ids, key=lambda x: (-reach_size[x], x))[:5]
    strategies["topSingle"] = {
        "seeds":    [id_name(best_solo)],
        "coverage": reach_size[best_solo],
    }
    strategies["singleReachChampions"] = [
        {"id": x, "name": name_map.get(x, str(x)), "class": klass_map.get(x, "?"),
         "popularity": degrees[x], "openness": openness[x], "reach": reach_size[x]}
        for x in top_by_reach
    ]

    # --- overlap analysis for topPopular + greedy
    def overlap_analysis(seeds):
        ind = [{"id": s, "name": name_map.get(s, str(s)), "coverage": len(reach[s])} for s in seeds]
        joint = coverage(seeds)[0]
        sum_ind = sum(x["coverage"] for x in ind)
        pairs = []
        for i in range(len(seeds)):
            for j in range(i + 1, len(seeds)):
                a, b = seeds[i], seeds[j]
                shared = adj.get(a, set()) & adj.get(b, set())
                pairs.append({
                    "a":              id_name(a),
                    "b":              id_name(b),
                    "sharedContacts": len(shared),
                    "sharedNames":    [name_map.get(x, str(x)) for x in sorted(shared)],
                })
        return {
            "individual":     ind,
            "joint":          joint,
            "sumIndividual":  sum_ind,
            "overlapCount":   sum_ind - joint,
            "pairs":          pairs,
        }

    overlap = {
        "topPopular": overlap_analysis(top3_pop),
        "greedy":     overlap_analysis(greedy),
    }

    # --- distributions
    class_sizes = Counter(klass_map[x] for x in node_ids)
    distributions = {
        "degrees":     sorted(degrees[x] for x in node_ids),
        "weighted":    sorted(weighted[x] for x in node_ids),
        "classSizes":  sorted(class_sizes.values(), reverse=True),
    }

    # --- class stats: freq + sex + mean degree + internal vs external
    classes_here = sorted(set(klass_map[x] for x in node_ids))
    class_stats = {}
    total_wt = sum(w for _, _, w in edges_list)
    for c in classes_here:
        cn = [x for x in node_ids if klass_map[x] == c]
        cd = [degrees[x] for x in cn]
        internal, external = 0, 0
        for (a, b, ww) in edges_list:
            if klass_map[a] == c and klass_map[b] == c:
                internal += ww
            elif klass_map[a] == c or klass_map[b] == c:
                external += ww
        tot = internal + external
        class_stats[c] = {
            "n":          len(cn),
            "nF":         sum(1 for x in cn if sex_map.get(x) == "F"),
            "nM":         sum(1 for x in cn if sex_map.get(x) == "M"),
            "nUnk":       sum(1 for x in cn if sex_map.get(x) not in ("F", "M")),
            "meanDegree": round(sum(cd) / len(cd), 1) if cd else 0.0,
            "internalPct": round(100 * internal / tot, 1) if tot else 0.0,
            "externalPct": round(100 * external / tot, 1) if tot else 0.0,
        }
    inter_class_weight = sum(w for (a, b, w) in edges_list if klass_map[a] != klass_map[b])
    inter_class_pct = round(100 * inter_class_weight / total_wt, 1) if total_wt else 0.0
    class_stats["_globalBetweenPct"] = inter_class_pct

    # --- friendship paradox on this slice + pick a 6-node subnet
    friends_mean = {}
    below_flag = {}
    for x in node_ids:
        fs = adj[x]
        if fs:
            fm = sum(degrees[y] for y in fs) / len(fs)
            friends_mean[x] = fm
            below_flag[x] = degrees[x] < fm

    n_with_friends = sum(1 for x in node_ids if x in friends_mean)
    n_below_fm = sum(1 for x, b in below_flag.items() if b)
    mean_friend_deg = round(sum(friends_mean.values()) / len(friends_mean), 1) if friends_mean else 0.0
    pct_below = round(100 * n_below_fm / n_with_friends) if n_with_friends else 0

    # Subnet of 6 for the manual counting card.
    # Strategy: take the star + its 4 lowest-degree neighbors + 1 mid-degree neighbor.
    star_neighbors = sorted(adj[star_id], key=lambda x: (degrees[x], x))
    subnet_ids = [star_id]
    for cand in star_neighbors:
        if len(subnet_ids) >= 5:
            break
        subnet_ids.append(cand)
    for cand in reversed(star_neighbors):
        if len(subnet_ids) >= 6:
            break
        if cand not in subnet_ids:
            subnet_ids.append(cand)
    subnet_ids = subnet_ids[:6]

    def node_row(x):
        friend_ids = sorted(adj[x])
        friend_degs = [degrees[y] for y in friend_ids]
        fm = round(sum(friend_degs) / len(friend_degs), 1) if friend_degs else 0.0
        return {
            "id":            x,
            "name":          name_map.get(x, str(x)),
            "class":         klass_map[x],
            "degree":        degrees[x],
            "friendDegrees": friend_degs,
            "friendMean":    fm,
            "belowMean":     degrees[x] < fm,
        }
    subnet_rows = [node_row(x) for x in subnet_ids]

    subnet_edges = []
    for i, a in enumerate(subnet_ids):
        for b in subnet_ids[i + 1:]:
            if b in adj[a]:
                subnet_edges.append({
                    "source": a,
                    "target": b,
                    "weight": weight_map.get((a, b) if a < b else (b, a), 1),
                })

    n_subnet_below = sum(1 for r in subnet_rows if r["belowMean"])

    friendship_paradox = {
        "meanDegree":       round(sum(degrees[x] for x in node_ids) / n, 1) if n else 0.0,
        "meanFriendDegree": mean_friend_deg,
        "pctBelow":         pct_below,
        "subnet": {
            "nodes":    subnet_rows,
            "edges":    subnet_edges,
            "nBelow":   n_subnet_below,
            "n":        len(subnet_rows),
        },
    }

    # --- cutVertices: nodurile a caror indepartare mareste numarul de componente
    baseline_n = len(comps)
    def components_excluding(exclude):
        seen = {exclude}
        n_comp = 0
        sizes = []
        for start in node_ids:
            if start in seen: continue
            comp = 0
            stack = [start]
            while stack:
                x = stack.pop()
                if x in seen: continue
                seen.add(x); comp += 1
                for y in adj.get(x, ()):
                    if y != exclude and y not in seen:
                        stack.append(y)
            n_comp += 1
            sizes.append(comp)
        return n_comp, sorted(sizes, reverse=True)

    cut_vertices = []
    for x in node_ids:
        n_comp, sizes = components_excluding(x)
        if n_comp > baseline_n:
            # Care noduri sunt in componentele mici (nu in cea principala)
            seen = {x}
            small_nodes = []
            largest_start = None
            for start in node_ids:
                if start in seen: continue
                comp = []
                stack = [start]
                while stack:
                    y = stack.pop()
                    if y in seen: continue
                    seen.add(y); comp.append(y)
                    for z in adj.get(y, ()):
                        if z != x and z not in seen:
                            stack.append(z)
                if len(comp) < sizes[0]:
                    small_nodes.extend(comp)
            cut_vertices.append({
                "id":            x,
                "name":          name_map.get(x, str(x)),
                "class":         klass_map.get(x, "?"),
                "componentsAfter": n_comp,
                "largestAfter":  sizes[0],
                "detachedCount": len(small_nodes),
                "detached":      [id_name(y) for y in sorted(small_nodes)],
            })
    cut_vertices.sort(key=lambda cv: (-cv["detachedCount"], cv["id"]))

    # --- bridgeEdges: muchii a caror indepartare mareste numarul de componente (Tarjan)
    def find_bridges(adj_map):
        # iterative Tarjan (adapted for undirected)
        disc = {}
        low = {}
        parent = {}
        bridges = []
        timer = [0]
        def dfs_iter(start):
            stack_ = [(start, iter(adj_map.get(start, ())))]
            disc[start] = low[start] = timer[0]; timer[0] += 1
            parent[start] = None
            while stack_:
                u, it = stack_[-1]
                found_next = False
                for v in it:
                    if v not in disc:
                        parent[v] = u
                        disc[v] = low[v] = timer[0]; timer[0] += 1
                        stack_.append((v, iter(adj_map.get(v, ()))))
                        found_next = True
                        break
                    elif v != parent[u]:
                        low[u] = min(low[u], disc[v])
                if not found_next:
                    stack_.pop()
                    if stack_:
                        p = stack_[-1][0]
                        low[p] = min(low[p], low[u])
                        if low[u] > disc[p]:
                            bridges.append((min(p, u), max(p, u)))
        for x in node_ids:
            if x not in disc:
                dfs_iter(x)
        return bridges

    bridge_edges_raw = find_bridges(adj)
    bridge_edges = []
    for (a, b) in bridge_edges_raw:
        w_edge = weight_map.get((min(a, b), max(a, b)), 1)
        # Care este componenta mica dupa taiere?
        seen_a = {a}
        stack_ = [a]
        while stack_:
            y = stack_.pop()
            for z in adj.get(y, ()):
                if y == a and z == b: continue
                if y == b and z == a: continue
                if z in seen_a: continue
                # Verificam ca nu folosim muchia (a,b)
                edge_key = (min(y, z), max(y, z))
                if edge_key == (min(a, b), max(a, b)): continue
                seen_a.add(z)
                stack_.append(z)
        detached_from_a = len(node_ids) - len(seen_a)
        cls_a = klass_map.get(a, "?")
        cls_b = klass_map.get(b, "?")
        bridge_edges.append({
            "a":              id_name(a),
            "b":              id_name(b),
            "aClass":         cls_a,
            "bClass":         cls_b,
            "weight":         w_edge,
            "sameClass":      cls_a == cls_b,
            "detachedCount":  detached_from_a,
        })
    bridge_edges.sort(key=lambda b: (-b["detachedCount"], b["a"]["id"]))

    # --- classPairMatrix: pentru fiecare pereche de clase, numarul de muchii + mediatori
    class_pair_edges = defaultdict(list)  # (cls_a, cls_b) -> list of (nid_a, nid_b, w)
    for a, b, w in edges_list:
        ca = klass_map.get(a, "?")
        cb = klass_map.get(b, "?")
        if ca == cb: continue
        pair = tuple(sorted([ca, cb]))
        class_pair_edges[pair].append((a, b, w))
    class_pair_matrix = []
    for pair, es in sorted(class_pair_edges.items(), key=lambda x: len(x[1])):
        mediators = Counter()
        for a, b, w in es:
            mediators[a] += 1
            mediators[b] += 1
        class_pair_matrix.append({
            "classA":     pair[0],
            "classB":     pair[1],
            "edgeCount":  len(es),
            "edges":      [{"a": id_name(a), "b": id_name(b), "weight": w} for a, b, w in es],
            "topMediators": [{"id": mid, "name": name_map.get(mid, str(mid)), "class": klass_map.get(mid, "?"), "contactsOnBridge": ct} for mid, ct in mediators.most_common(3)],
        })

    # --- top5 popular removal effect
    top5_ids = sorted(node_ids, key=lambda x: (-degrees[x], x))[:5]
    seen = set(top5_ids)
    n_comp_top5 = 0
    sizes_top5 = []
    for start in node_ids:
        if start in seen: continue
        comp = 0
        stack_ = [start]
        while stack_:
            x_ = stack_.pop()
            if x_ in seen: continue
            seen.add(x_); comp += 1
            for y in adj.get(x_, ()):
                if y not in seen and y not in top5_ids:
                    stack_.append(y)
        n_comp_top5 += 1
        sizes_top5.append(comp)
    sizes_top5.sort(reverse=True)
    top5_removal = {
        "top5":            [id_name(x) for x in top5_ids],
        "componentsAfter": n_comp_top5,
        "largestAfter":    sizes_top5[0] if sizes_top5 else 0,
        "sizes":           sizes_top5,
    }

    # --- try-break scenarios (precomputed for the c10-try-break card).
    # For each candidate removal set, compute connected components on the
    # remaining nodes; report component sizes (desc), which nodes end up
    # detached from the biggest surviving piece, and totals. The browser
    # just reads this and animates; no live BFS on the client.
    def scenario(key, label, removed_ids, description=""):
        removed = set(removed_ids)
        seen_s = set(removed)
        components = []  # list of member-id lists, one per component
        for start in node_ids:
            if start in seen_s: continue
            members = []
            stack_ = [start]
            while stack_:
                x_ = stack_.pop()
                if x_ in seen_s: continue
                seen_s.add(x_); members.append(x_)
                for y in adj.get(x_, ()):
                    if y not in seen_s and y not in removed:
                        stack_.append(y)
            components.append(members)
        components.sort(key=lambda c: -len(c))
        biggest = components[0] if components else []
        detached_ids = [x for comp in components[1:] for x in comp]
        sizes = [len(c) for c in components]
        return {
            "key":                key,
            "label":               label,
            "description":         description,
            "removedIds":          [x for x in removed_ids],
            "removedNames":        [name_map.get(x, str(x)) for x in removed_ids],
            "componentSizesAfter": sizes,
            "biggestSize":         len(biggest),
            "detachedIds":         detached_ids,
            "detachedCount":       len(detached_ids),
            "totalGroups":         len(components),
            "totalRemaining":      len(node_ids) - len(removed_ids),
        }

    cut_vertex_ids = [cv["id"] for cv in cut_vertices]
    try_break_scenarios = [
        scenario(
            "vedeta",
            "Scoate-l pe {}".format(name_map.get(ROLE_IDS["vedeta"], "?")),
            [ROLE_IDS["vedeta"]],
            "Cel mai popular elev al școlii dispare."
        ),
        scenario(
            "top5",
            "Scoate primii cinci după grad",
            top5_ids,
            "Elimină simultan cei mai populari cinci elevi."
        ),
        scenario(
            "dependent",
            "Scoate-l pe {}".format(name_map.get(ROLE_IDS["dependent"], "?")),
            [ROLE_IDS["dependent"]],
            "Un elev cu popularitate modestă, dar cu un rol structural aparte."
        ),
        scenario(
            "allCutVertices",
            "Scoate toți cei {} elevi de care atârnă cineva".format(len(cut_vertex_ids)),
            cut_vertex_ids,
            "Fiecare dintre acești elevi e singurul drum al cel puțin unei persoane. Ce se rupe când dispar toți simultan?"
        ),
    ]
    try_break = {
        "scenarios": try_break_scenarios,
    }

    # === MISSION DATA: trioMission (Sandu, Emil, Doina), correlations, plafon, scatterData

    def person_by_name(target_name):
        # Names can repeat across classes; pick the one with the largest reach so the
        # mission narrative uses the version the story is actually about.
        candidates = [nid for nid in node_ids if name_map.get(nid) == target_name]
        if not candidates:
            return None
        return max(candidates, key=lambda x: (reach_size[x], degrees[x], -x))

    def profile_person(nid):
        if nid is None: return None
        r_set = reach[nid]
        own_class = klass_map.get(nid, "?")
        in_class = sum(1 for x in r_set if klass_map.get(x) == own_class)
        out_class = len(r_set) - in_class
        cls_dist = Counter(klass_map.get(x, "?") for x in r_set)
        # neighbor-class span for the mission (class-based grupuri, small integer)
        neighbor_classes = {klass_map.get(y, "?") for y in adj.get(nid, ())}
        neighbor_classes.discard(own_class)
        groups_out = len(neighbor_classes)  # classes OTHER than own where the person has ties
        groups_total = groups_out + 1  # including own class
        return {
            "id":            nid,
            "name":          name_map.get(nid, str(nid)),
            "class":         own_class,
            "classFriendly": CLASS_NAMES.get(own_class, own_class),
            "sex":           sex_map.get(nid, "Unknown"),
            "popularity":    degrees[nid],
            "openness":      openness[nid],
            "groups":        groups_total,
            "groupsOut":     groups_out,
            "reach":         reach_size[nid],
            "reachInClass":  in_class,
            "reachOutClass": out_class,
            "classDist":     [{"class": k, "classFriendly": CLASS_NAMES.get(k, k), "count": v}
                              for k, v in sorted(cls_dist.items(), key=lambda kv: -kv[1])],
        }

    # Trio for the mission duel: vedeta (max popularity), campion (max reach),
    # surpriza (small pop, top-10% reach). Pinned by ID from Phase 1.
    trio_mission = {
        "vedeta":   profile_person(ROLE_IDS["vedeta"])   if ROLE_IDS["vedeta"]   in node_ids else None,
        "campion":  profile_person(ROLE_IDS["campion"])  if ROLE_IDS["campion"]  in node_ids else None,
        "surpriza": profile_person(ROLE_IDS["surpriza"]) if ROLE_IDS["surpriza"] in node_ids else None,
    }

    # Pearson correlations
    def pearson(xs, ys):
        n = len(xs)
        if n == 0: return 0.0
        mx = sum(xs) / n; my = sum(ys) / n
        num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
        import math
        dx = math.sqrt(sum((xs[i] - mx) ** 2 for i in range(n)))
        dy = math.sqrt(sum((ys[i] - my) ** 2 for i in range(n)))
        return round(num / (dx * dy), 3) if dx and dy else 0.0

    pop_arr   = [degrees[x] for x in node_ids]
    open_arr  = [openness[x] for x in node_ids]
    reach_arr = [reach_size[x] for x in node_ids]

    correlations = {
        "popularityReach": pearson(pop_arr, reach_arr),
        "opennessReach":   pearson(open_arr, reach_arr),
    }

    plafon = len(node_ids) - len(unreachable_ids)

    def groups_of(x):
        nc = {klass_map.get(y, "?") for y in adj.get(x, ())}
        nc.discard(klass_map.get(x, "?"))
        return len(nc) + 1

    # Bounded reach at 2 and 3 rounds (as opposed to the full-mission reach at `pasi`).
    def reach_at_k(source, k):
        known = {source}
        frontier = [source]
        for _ in range(k):
            nxt = []
            for u in frontier:
                for v in adj_top.get(u, ()):
                    if v not in known:
                        known.add(v); nxt.append(v)
            frontier = nxt
            if not frontier: break
        return len(known)

    reach2 = {x: reach_at_k(x, 2) for x in node_ids}
    reach3 = {x: reach_at_k(x, 3) for x in node_ids}

    scatter_data = [
        {
            "id":         x,
            "name":       name_map.get(x, str(x)),
            "class":      klass_map.get(x, "?"),
            "popularity": degrees[x],
            "openness":   openness[x],
            "groups":     groups_of(x),
            "reach2":     reach2[x],
            "reach3":     reach3[x],
            "reach":      reach_size[x],
        }
        for x in node_ids
    ]

    groups_arr = [groups_of(x) for x in node_ids]
    reach2_arr = [reach2[x] for x in node_ids]
    reach3_arr = [reach3[x] for x in node_ids]
    correlations["groupsReach"] = pearson(groups_arr, reach_arr)
    correlations["reach2Reach"] = pearson(reach2_arr, reach_arr)
    correlations["reach3Reach"] = pearson(reach3_arr, reach_arr)

    top3_pop_names   = [name_map.get(x, str(x)) for x in top3_pop]
    top3_open_names  = [name_map.get(x, str(x)) for x in top3_open]
    greedy_names     = [name_map.get(x, str(x)) for x in greedy]

    # Coverage of the three characters the story has introduced by name
    # (vedeta + campion + puntea = Antoine + Chloé + Léa). Distinct from the
    # top-3-popular strategy, which is the automatic degree-only pick.
    known_team_ids = [ROLE_IDS["vedeta"], ROLE_IDS["campion"], ROLE_IDS["puntea"]]
    known_team_coverage = len(diffuse_limited(known_team_ids, adj_top, pasi))
    known_team_names = [name_map.get(x, str(x)) for x in known_team_ids]

    # === Coverage maps: precomputed reach set per strategy + a shared radial
    # layout, so the client can render four alăturate mini-maps without any
    # simulation or layout work.
    def _cov_set(seed_ids):
        return sorted(int(x) for x in diffuse_limited(list(seed_ids), adj_top, pasi))

    def _seed_ids(strat_key):
        seeds = strategies[strat_key]["seeds"]
        return [int(s["id"]) if isinstance(s, dict) else int(s) for s in seeds]

    top3_pop_ids = _seed_ids("topPopular")
    top3_open_ids = _seed_ids("topOpen")
    greedy_ids = _seed_ids("greedy")
    known_ids = [int(x) for x in known_team_ids]
    # Top 3 by reach — surprising killer: Chloé + Gabin + Estée. Chloé and
    # Gabin are both in Bio C, so they overlap heavily on the same crowd.
    top3_reach_ids = [int(x) for x in sorted(node_ids, key=lambda x: (-reach_size[x], x))[:3]]
    top3_reach_names = [name_map.get(x, str(x)) for x in top3_reach_ids]
    top3_reach_coverage = len(diffuse_limited(top3_reach_ids, adj_top, pasi))

    # Top 3 by betweenness — needs Brandes' algorithm on the full network.
    def _betweenness():
        Cb = {v: 0.0 for v in node_ids}
        for s in node_ids:
            S = []
            P = {v: [] for v in node_ids}
            sigma = {v: 0 for v in node_ids}; sigma[s] = 1
            d = {v: -1 for v in node_ids}; d[s] = 0
            Q = deque([s])
            while Q:
                v = Q.popleft(); S.append(v)
                for w in adj.get(v, ()):
                    if d[w] < 0: d[w] = d[v] + 1; Q.append(w)
                    if d[w] == d[v] + 1: sigma[w] += sigma[v]; P[w].append(v)
            delta = {v: 0.0 for v in node_ids}
            while S:
                w = S.pop()
                for v in P[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                if w != s: Cb[w] += delta[w]
        for v in Cb: Cb[v] /= 2.0
        return Cb
    betweenness = _betweenness()
    top3_betw_ids = sorted(node_ids, key=lambda x: (-betweenness[x], x))[:3]
    top3_betw_names = [name_map.get(x, str(x)) for x in top3_betw_ids]
    top3_betw_coverage = len(diffuse_limited(top3_betw_ids, adj_top, pasi))
    # For the terminology mention: top 10 by betweenness (name + class + value)
    betw_top10 = []
    for nid in sorted(node_ids, key=lambda x: (-betweenness[x], x))[:10]:
        betw_top10.append({
            "id": nid,
            "name": name_map.get(nid, str(nid)),
            "classFriendly": CLASS_NAMES.get(klass_map.get(nid, "?"), "?"),
            "value": round(betweenness[nid], 1),
        })

    coverage_maps = {
        "top3pop":   {"seedIds": top3_pop_ids,   "seedNames": top3_pop_names,   "coveredIds": _cov_set(top3_pop_ids)},
        "top3open":  {"seedIds": top3_open_ids,  "seedNames": top3_open_names,  "coveredIds": _cov_set(top3_open_ids)},
        "top3reach": {"seedIds": top3_reach_ids, "seedNames": top3_reach_names, "coveredIds": _cov_set(top3_reach_ids)},
        "top3betw":  {"seedIds": top3_betw_ids,  "seedNames": top3_betw_names,  "coveredIds": _cov_set(top3_betw_ids)},
        "greedy":    {"seedIds": greedy_ids,     "seedNames": greedy_names,     "coveredIds": _cov_set(greedy_ids)},
        "knownTeam": {"seedIds": known_ids,      "seedNames": known_team_names, "coveredIds": _cov_set(known_ids)},
    }

    # Shared layout: place each class as a small radial cluster on a nine-slot
    # ring. Deterministic, so the four minis in the browser all match visually.
    # Coordinates are normalized to [-1, 1] with the school centered at origin.
    _class_order = sorted({klass_map[x] for x in node_ids})
    _by_class = defaultdict(list)
    for x in node_ids:
        _by_class[klass_map[x]].append(x)
    import math as _math
    _step = 2 * _math.pi / max(1, len(_class_order))
    _outer_r = 0.72
    coverage_positions = {}
    for i, cls in enumerate(_class_order):
        cx = _math.cos(i * _step - _math.pi / 2) * _outer_r
        cy = _math.sin(i * _step - _math.pi / 2) * _outer_r
        members = sorted(_by_class[cls])
        n = len(members)
        cluster_r = max(0.12, min(0.20, 0.02 + 0.008 * n))
        for j, nid in enumerate(members):
            ang = (j / max(1, n)) * 2 * _math.pi
            coverage_positions[str(nid)] = {
                "x": round(cx + _math.cos(ang) * cluster_r, 4),
                "y": round(cy + _math.sin(ang) * cluster_r, 4),
                "class": cls,
                "classFriendly": CLASS_NAMES.get(cls, cls),
            }
    coverage_maps["_positions"] = coverage_positions
    coverage_maps["_total"] = len(node_ids)

    # Organic layout via a small Fruchterman-Reingold pass. This is what the
    # measure-tabs "Pe hartă" view uses, so the network looks like a general
    # spring-embedder result, not a per-class ring. Deterministic thanks to
    # the fixed seed.
    def _fr_layout(nodes_iter, edges_iter, iters=140, seed_int=42):
        import math as _m
        r = random.Random(seed_int)
        nlist = list(nodes_iter)
        n = len(nlist)
        idx = {nid: i for i, nid in enumerate(nlist)}
        # Init random positions in [-1, 1]
        pos = [(r.uniform(-1.0, 1.0), r.uniform(-1.0, 1.0)) for _ in range(n)]
        # Optimal edge length
        area = 4.0  # unit square scaled up
        k = _m.sqrt(area / max(1, n))
        elist = [(idx[a], idx[b]) for a, b in edges_iter if a in idx and b in idx]
        for it in range(iters):
            # Temperature: linear cool
            t = 0.10 * (1.0 - it / iters)
            # Displacement per node
            disp = [(0.0, 0.0)] * n
            # Repulsive between all pairs (O(n^2), fine at n=299)
            for i in range(n):
                dxi, dyi = 0.0, 0.0
                xi, yi = pos[i]
                for j in range(n):
                    if i == j: continue
                    xj, yj = pos[j]
                    dx = xi - xj; dy = yi - yj
                    d2 = dx * dx + dy * dy
                    if d2 < 1e-6:
                        # Nudge to avoid singularity
                        dx = (r.random() - 0.5) * 0.001
                        dy = (r.random() - 0.5) * 0.001
                        d2 = dx * dx + dy * dy
                    d = _m.sqrt(d2)
                    # Repulsive force ~ k^2 / d
                    f = (k * k) / d
                    dxi += (dx / d) * f
                    dyi += (dy / d) * f
                disp[i] = (dxi, dyi)
            # Attractive along edges
            for ia, ib in elist:
                xa, ya = pos[ia]; xb, yb = pos[ib]
                dx = xa - xb; dy = ya - yb
                d = _m.sqrt(dx * dx + dy * dy) or 1e-6
                f = (d * d) / k
                fx = (dx / d) * f; fy = (dy / d) * f
                dax, day = disp[ia]; dbx, dby = disp[ib]
                disp[ia] = (dax - fx, day - fy)
                disp[ib] = (dbx + fx, dby + fy)
            # Update positions, cap step by t
            new_pos = []
            for i in range(n):
                x, y = pos[i]; dx, dy = disp[i]
                dmag = _m.sqrt(dx * dx + dy * dy) or 1e-6
                step = min(dmag, t)
                x += (dx / dmag) * step
                y += (dy / dmag) * step
                # Clamp to a reasonable box
                x = max(-1.05, min(1.05, x))
                y = max(-1.05, min(1.05, y))
                new_pos.append((x, y))
            pos = new_pos
        # Normalize to [-1, 1]
        xs = [p[0] for p in pos]; ys = [p[1] for p in pos]
        mnx, mxx = min(xs), max(xs); mny, mxy = min(ys), max(ys)
        rx = (mxx - mnx) or 1.0; ry = (mxy - mny) or 1.0
        norm = []
        for x, y in pos:
            nx = ((x - mnx) / rx) * 2 - 1
            ny = ((y - mny) / ry) * 2 - 1
            norm.append((round(nx * 0.95, 4), round(ny * 0.95, 4)))
        return {nlist[i]: {"x": norm[i][0], "y": norm[i][1]} for i in range(n)}

    # Organic FR layout is ARCHIVED: it was used only by the measure-tabs
    # "Pe hartă" view, which now uses the class-clustered radial layout so the
    # champion's contact pattern reads at a glance. FR was also visibly broken
    # (nodes pushed against the clamp boundary in straight lines). Flip
    # ENABLE_ORGANIC = True to precompute it again on other data.
    ENABLE_ORGANIC = False
    if ENABLE_ORGANIC:
        _fr_positions = _fr_layout(node_ids, [(a, b) for a, b, _w in edges_list], iters=50, seed_int=42)
        coverage_positions_organic = {}
        for nid in node_ids:
            p = _fr_positions.get(nid, {"x": 0.0, "y": 0.0})
            coverage_positions_organic[str(nid)] = {
                "x": p["x"],
                "y": p["y"],
                "class": klass_map.get(nid, "?"),
                "classFriendly": CLASS_NAMES.get(klass_map.get(nid, "?"), "?"),
            }
        coverage_maps["_positionsOrganic"] = coverage_positions_organic

    # === Robustness curves for the "Ce se rupe" card — ARCHIVED.
    # Result about targeted-attack fragility is only clean for networks with
    # large hubs. Our slice caps degree at 19 with no scale-free concentration,
    # so the two curves separate only after ~50 removals — not sharp enough
    # to demonstrate the phenomenon in class. The card is disabled in the
    # lesson (enabled: false). Set ENABLE_ROBUSTNESS = True to re-enable on
    # other data.
    ENABLE_ROBUSTNESS = False
    def _largest_component(remaining, adj_map):
        seen = set()
        largest = 0
        for start in remaining:
            if start in seen: continue
            stack = [start]; sz = 0
            while stack:
                x = stack.pop()
                if x in seen: continue
                seen.add(x); sz += 1
                for y in adj_map.get(x, ()):
                    if y not in seen and y in remaining: stack.append(y)
            if sz > largest: largest = sz
        return largest

    if ENABLE_ROBUSTNESS:
        _rob_max = 100
        _rob_trials = 30
        _sum_random = [0] * (_rob_max + 1)
        for _seed in range(_rob_trials):
            rnd = random.Random(1000 + _seed)
            order = list(node_ids)
            rnd.shuffle(order)
            remaining_r = set(node_ids)
            for k in range(_rob_max + 1):
                if k > 0: remaining_r.discard(order[k - 1])
                _sum_random[k] += _largest_component(remaining_r, adj)
        random_curve = [round(v / _rob_trials, 1) for v in _sum_random]

        targeted_curve = []
        remaining_t = set(node_ids)
        for k in range(_rob_max + 1):
            targeted_curve.append(_largest_component(remaining_t, adj))
            if k >= _rob_max: break
            best = None; best_deg = -1
            for x in remaining_t:
                d = sum(1 for y in adj.get(x, ()) if y in remaining_t)
                if d > best_deg: best_deg = d; best = x
            if best is not None: remaining_t.discard(best)

        coverage_maps["_robustness"] = {
            "randomCurve":   random_curve,
            "targetedCurve": targeted_curve,
            "maxRemoved":    _rob_max,
            "trials":        _rob_trials,
            "total":         len(node_ids),
        }

    # === Precomputes for the measure-tabs cards.
    # For each measure champion, we save:
    #  - their id + name + friendly class
    #  - their contact ids
    #  - class distribution of contacts (list of {class, classFriendly, count})
    # For deschidere we also save Antoine (the swap-target for the contrast).
    # For intermediere we sample 5 shortest paths that pass THROUGH the champion,
    # so the browser can animate them without recomputing BFS on the client.
    def _map_data_for(nid, extra_class_dist=True):
        contacts = list(adj.get(nid, ()))
        cls_dist = Counter(klass_map.get(c, "?") for c in contacts)
        return {
            "id":            nid,
            "name":          name_map.get(nid, str(nid)),
            "class":         klass_map.get(nid, "?"),
            "classFriendly": CLASS_NAMES.get(klass_map.get(nid, "?"), "?"),
            "degree":        degrees[nid],
            "openness":      openness[nid],
            "contactIds":    contacts,
            "classDistribution": [
                {"class": k, "classFriendly": CLASS_NAMES.get(k, k), "count": v}
                for k, v in sorted(cls_dist.items(), key=lambda kv: -kv[1])
            ] if extra_class_dist else None,
        }

    # Sample paths through Charlotte for the betweenness map. Pick pairs of
    # unrelated students at reasonable distance from opposite corners.
    def _paths_through(nid, target_count=5):
        # Do a BFS from nid to get distance labels.
        # Then, for candidate pairs (s, t) with s, t on OPPOSITE sides
        # (t on the far shell, s on another far shell), check if the shortest
        # s-t path passes through nid.
        # Simple heuristic: pick pairs from among the neighbors' subtrees.
        def bfs_all_pairs_shortest(source):
            dist = {source: 0}; parent = {source: None}
            q = deque([source])
            while q:
                x = q.popleft()
                for y in adj.get(x, ()):
                    if y not in dist:
                        dist[y] = dist[x] + 1
                        parent[y] = x
                        q.append(y)
            return dist, parent

        # Fix nid on the path. For every pair (s, t) with nid on the s-t path,
        # the shortest s-t distance = dist(s, nid) + dist(nid, t). To confirm
        # nid is on THE shortest path we need to actually compute BFS from s
        # and check that dist(s, t) equals dist(s, nid) + dist(nid, t).
        # Sample: from source nid, pick 20 nodes at distance 2-4 (far shell),
        # then for each pair of them check the condition.
        dist_from_c, _ = bfs_all_pairs_shortest(nid)
        far_shell = [x for x, d in dist_from_c.items() if 2 <= d <= 4]
        # Group far-shell by class so we can pick pairs from DIFFERENT classes.
        by_class = defaultdict(list)
        for x in far_shell:
            by_class[klass_map.get(x, "?")].append(x)
        # Sort within each class to keep output deterministic.
        for cls in by_class:
            by_class[cls].sort(key=lambda x: name_map.get(x, str(x)))
        classes_in_order = sorted(by_class.keys())

        collected = []
        seen_pairs = set()
        used_sources = set()
        used_targets = set()
        # Try all cross-class combinations; prefer a fresh source and target
        # in each accepted path so the visual sample is diverse.
        # Iterate class pairs; take at most ONE path per unordered class pair,
        # so the 5 sampled paths cover different corners of the school.
        class_pairs_used = set()
        # Multi-round: keep looping while more paths are needed.
        for _round in range(3):
            if len(collected) >= target_count: break
            for ci in range(len(classes_in_order)):
                if len(collected) >= target_count: break
                for cj in range(ci + 1, len(classes_in_order)):
                    if len(collected) >= target_count: break
                    ca, cb = classes_in_order[ci], classes_in_order[cj]
                    pair_key = tuple(sorted([ca, cb]))
                    if pair_key in class_pairs_used and _round == 0: continue
                    for s in by_class[ca]:
                        if s in used_sources or s in used_targets: continue
                        dist_from_s, parent_from_s = bfs_all_pairs_shortest(s)
                        found = False
                        for t in by_class[cb]:
                            if t in used_sources or t in used_targets: continue
                            if (s, t) in seen_pairs or (t, s) in seen_pairs: continue
                            if t not in dist_from_s: continue
                            if dist_from_s[t] < 3: continue
                            if dist_from_s.get(nid, 10**9) + dist_from_c.get(t, 10**9) != dist_from_s[t]: continue
                            path = []
                            cur = t
                            while cur is not None:
                                path.append(cur); cur = parent_from_s.get(cur)
                            path.reverse()
                            if nid not in path: continue
                            collected.append({
                                "sourceId":    s,
                                "sourceName":  name_map.get(s, str(s)),
                                "sourceClass": CLASS_NAMES.get(klass_map.get(s, "?"), "?"),
                                "targetId":    t,
                                "targetName":  name_map.get(t, str(t)),
                                "targetClass": CLASS_NAMES.get(klass_map.get(t, "?"), "?"),
                                "pathIds":     path,
                                "length":      dist_from_s[t],
                            })
                            seen_pairs.add((s, t))
                            used_sources.add(s); used_targets.add(t)
                            class_pairs_used.add(pair_key)
                            found = True
                            break
                        if found: break
        return collected

    # Betweenness top 3 champion IDs (integer form)
    top1_betw_id = int(top3_betw_ids[0]) if top3_betw_ids else None

    measure_maps = {
        "positions": coverage_positions,  # shared layout
        "total":     len(node_ids),
        # Degree champion: vedeta (Antoine, id 117)
        "degree":    {
            "champion": _map_data_for(ROLE_IDS["vedeta"]),
        },
        # Openness champion: puntea (Léa, id 1332). We also store the vedeta
        # so the map can flip between the two and show the contrast (Léa's
        # contacts span multiple classes, Antoine's are all Bio C).
        "openness":  {
            "champion":  _map_data_for(ROLE_IDS["puntea"]),
            "contrast":  _map_data_for(ROLE_IDS["vedeta"]),
        },
        # Betweenness champion: Charlotte. Sample 5 shortest paths through her.
        "betweenness": {
            "champion":  _map_data_for(top1_betw_id) if top1_betw_id is not None else None,
            "paths":     _paths_through(top1_betw_id, target_count=5) if top1_betw_id is not None else [],
        },
    }
    coverage_maps["_measureMaps"] = measure_maps

    # === Greedy step-by-step trace: at each step, top 5 candidates by
    # marginal gain (coverage added over currently-chosen), plus who was
    # picked. Used by the new "cine sunt ei" story-telling in the greedy
    # card so students see the algorithm's actual reasoning.
    greedy_trace = []
    chosen = []
    for _step in range(3):
        step_scores = []
        prev_cov = diffuse_limited(chosen, adj_top, pasi) if chosen else set()
        for cand in node_ids:
            if cand in chosen: continue
            new_cov = diffuse_limited(chosen + [cand], adj_top, pasi)
            step_scores.append({"id": cand, "name": name_map.get(cand, str(cand)), "gain": len(new_cov) - len(prev_cov)})
        step_scores.sort(key=lambda x: (-x["gain"], x["id"]))
        picked = step_scores[0]
        greedy_trace.append({
            "step": _step + 1,
            "pickedId": picked["id"],
            "pickedName": picked["name"],
            "pickedGain": picked["gain"],
            "top5": step_scores[:5],
        })
        chosen.append(picked["id"])
    # Also: compare picked-at-step2 with "runner-up-from-step-1 evaluated
    # AT step 2". That is the key pedagogical number for the greedy card.
    if greedy_trace and len(greedy_trace) >= 2 and greedy_trace[0]["top5"]:
        step1_runnerup_id = greedy_trace[0]["top5"][1]["id"]
        step1_runnerup_name = greedy_trace[0]["top5"][1]["name"]
        cov_after_step1 = diffuse_limited([greedy_trace[0]["pickedId"]], adj_top, pasi)
        cov_with_runnerup = diffuse_limited([greedy_trace[0]["pickedId"], step1_runnerup_id], adj_top, pasi)
        greedy_trace[1]["step1RunnerUpName"] = step1_runnerup_name
        greedy_trace[1]["step1RunnerUpSoloReach"] = greedy_trace[0]["top5"][1]["gain"]
        greedy_trace[1]["step1RunnerUpMarginalAtStep2"] = len(cov_with_runnerup) - len(cov_after_step1)

    mission_summary = {
        "plafon":        plafon,
        "trioMission":   trio_mission,
        "correlations":  correlations,
        "top3PopularNames":     top3_pop_names,
        "top3PopularCoverage":  strategies["topPopular"]["coverage"],
        "top3OpenNames":        top3_open_names,
        "top3OpenCoverage":     strategies["topOpen"]["coverage"],
        "top3ReachNames":       top3_reach_names,
        "top3ReachCoverage":    top3_reach_coverage,
        "top3BetweennessNames":    top3_betw_names,
        "top3BetweennessCoverage": top3_betw_coverage,
        "greedyNames":          greedy_names,
        "greedyCoverage":       strategies["greedy"]["coverage"],
        "knownTeamNames":       known_team_names,
        "knownTeamCoverage":    known_team_coverage,
        "randomMean":           strategies["randomMean"],
        "randomMax":            strategies["randomMax"],
        "randomMin":            strategies["randomMin"],
        "coverageMaps":         coverage_maps,
        "betweennessTop10":     betw_top10,
        "greedyTrace":          greedy_trace,
    }

    return {
        "components":         components,
        "communities": {
            "n":                       n_communities,
            "byId":                    {str(x): community[x] for x in node_ids},
            "contingency":             {str(c_id): dict(ct) for c_id, ct in contingency.items()},
            "majorityClass":           {str(c_id): c for c_id, c in comm_majority.items()},
            "pctMatchClass":           pct_match,
            "mismatched":              mismatched,
            "nMismatched":             len(mismatched),
        },
        "openness":           {str(x): openness[x] for x in node_ids},
        "reach":              {str(x): reach_size[x] for x in node_ids},
        "unreachableCount":   len(unreachable_ids),
        "unreachableIds":     unreachable_ids,
        "characters":         characters,
        "strategies":         strategies,
        "overlap":            overlap,
        "distributions":      distributions,
        "classStats":         class_stats,
        "friendshipParadox":  friendship_paradox,
        "diffusionModel": {
            "pasi":            pasi,
            "maxTransmiteri":  max_t,
            "description":     "Deterministic BFS bounded to `pasi` rounds; each carrier transmits only to top `maxTransmiteri` contacts by edge weight."
        },
        "cutVertices":         cut_vertices,
        "nCutVertices":        len(cut_vertices),
        "bridgeEdges":         bridge_edges,
        "nBridgeEdges":        len(bridge_edges),
        "classPairMatrix":     class_pair_matrix,
        "top5Removal":         top5_removal,
        "tryBreak":            try_break,
        "trioMission":         trio_mission,
        "correlations":        correlations,
        "plafon":              plafon,
        "scatterData":         scatter_data,
        "mission":             mission_summary,
        "louvain":             louvain_results,
        "brokenPair": {
            "classA":            "MP*1",
            "classB":            "PSI*",
            "classAFriendly":    "Mate B",
            "classBFriendly":    "Inginerie",
            "personA":           {"name": "Luca", "class": "PSI*"},
            "personB":           {"name": "Kira", "class": "MP*1"},
            "edgeWeight":        53,
            "distanceBefore":    4.94,
            "distanceAfter":     5.16,
            "distanceIncrease":  0.22,
            "distanceIncreasePct": 5,
        }
    }


CLASSES    = ["2BIO1", "2BIO2", "2BIO3", "MP", "MP*1", "MP*2", "PC", "PC*", "PSI*"]
DAY        = 1
MIN_WEIGHT = 4

CLASS_NAMES = {
    "2BIO1": "Bio A",
    "2BIO2": "Bio B",
    "2BIO3": "Bio C",
    "MP":    "Mate A",
    "MP*1":  "Mate B",
    "MP*2":  "Mate C",
    "PC":    "Chimie A",
    "PC*":   "Chimie B",
    "PSI*":  "Inginerie",
}

FRENCH_F = [
    "Camille", "Léa", "Manon", "Chloé", "Sarah", "Emma", "Inès", "Clara", "Jade", "Louise",
    "Anaïs", "Zoé", "Alice", "Margaux", "Élise", "Noémie", "Charlotte", "Solène", "Amandine", "Juliette",
    "Océane", "Marion", "Aurélie", "Justine", "Pauline", "Adèle", "Lucie", "Maëlle", "Romane", "Éloïse",
    "Aurore", "Cécile", "Delphine", "Élodie", "Fanny", "Gabrielle", "Hélène", "Isabelle", "Jeanne", "Karine",
    "Laurence", "Mélanie", "Nadège", "Odile", "Pénélope", "Roxane", "Sylvie", "Thérèse", "Valentine", "Yasmine",
    "Zélie", "Adélaïde", "Béatrice", "Cléa", "Diane", "Estelle", "Flavie", "Iris", "Louane", "Mathilde",
    "Naïs", "Olympe", "Perrine", "Sabine", "Tiphaine", "Vanessa", "Angèle", "Blandine", "Coralie", "Domitille",
    "Eugénie", "Fabienne", "Gwendoline", "Honorine", "Josiane", "Malorie", "Nadine", "Rosalie", "Sophie", "Tessa",
    "Virginie", "Ysée", "Amélie", "Bérénice", "Célestine", "Dorothée", "Émilie", "Florence", "Ghislaine", "Hortense",
    "Ingrid", "Julie", "Katia", "Lorraine", "Mireille", "Noëlle", "Ondine", "Pascaline", "Quiterie", "Simone",
    "Ténéré", "Ursule", "Violette", "Zoraïde", "Adeline", "Brigitte", "Christiane", "Danielle", "Estée", "Françoise",
    "Georgette", "Henriette", "Irène", "Joëlle", "Katarina", "Laëtitia", "Marguerite", "Nicoline", "Ombeline", "Prudence",
    "Rébecca", "Sandrine", "Tatiana", "Ulysse", "Véronique", "Wilhelmine", "Xénia", "Yveline", "Adrienne", "Beatrix",
    "Corinne", "Désirée", "Eulalie", "Félicie", "Guenièvre", "Héloïse", "Ismérie", "Jacqueline", "Kim", "Ludivine",
    "Micheline", "Nathalie", "Odette", "Patricia", "Reine", "Séverine", "Tiphany", "Ulrike", "Valérie", "Wanda"
]

FRENCH_M = [
    "Julien", "Thomas", "Antoine", "Maxime", "Lucas", "Hugo", "Nathan", "Théo", "Enzo", "Baptiste",
    "Rémi", "Mathis", "Quentin", "Corentin", "Damien", "Adrien", "Gaspard", "Victor", "Florian", "Benoît",
    "Kévin", "Sébastien", "Clément", "Romain", "Guillaume", "Étienne", "Loïc", "Bastien", "Yann", "Grégoire",
    "Alexandre", "Bernard", "Christophe", "David", "Édouard", "Fabien", "Gérard", "Henri", "Ismaël", "Jérôme",
    "Karl", "Laurent", "Marc", "Nicolas", "Olivier", "Pierre", "Régis", "Sylvain", "Tristan", "Vincent",
    "Xavier", "Yohan", "Zacharie", "Aymeric", "Basile", "Cyril", "Denis", "Emmanuel", "Franck", "Gilles",
    "Hervé", "Ivan", "Joachim", "Ludovic", "Michel", "Norbert", "Ovide", "Philippe", "Renaud", "Sylvestre",
    "Timothée", "Ulysse", "Valentin", "Wilfrid", "Yves", "Alain", "Boris", "Cédric", "Didier", "Fabrice",
    "Gaël", "Hadrien", "Ismaïl", "Joris", "Karim", "Léopold", "Mathéo", "Naël", "Owen", "Paul",
    "Rayan", "Samuel", "Timéo", "Vadim", "Wassim", "Yassin", "Zayd", "Amaury", "Bruno", "Christian",
    "Damir", "Ernest", "Frédéric", "Gustave", "Hubert", "Ignace", "Jacques", "Kilian", "Léon", "Martin",
    "Nolan", "Octave", "Pascal", "Quinton", "Robin", "Stéphane", "Thibault", "Ugo", "Valère", "William",
    "Yanis", "Ayoub", "Blaise", "Célestin", "Diego", "Ethan", "Gabin", "Iban", "Jules", "Killian",
    "Léonard", "Malo", "Noé", "Oscar", "Pierrick", "Raphaël", "Simon", "Théophile", "Vasco", "Yaël",
    "Adam", "Bilal", "Cyrus", "Djibril", "Erwan", "Fadi", "Gustavo", "Hicham", "Isaac", "Jean",
    "Karam", "Lorenzo", "Milan", "Nour-Eddine", "Omar", "Paolo", "Rachid", "Selim", "Tarek", "Yohann"
]

FRENCH_N = ["Sacha", "Charlie", "Alix", "Cyprien", "Éden", "Andrea", "Ellie", "Léon-Marie"]

# Explicit name assignments for the six protagonists, chosen by role.
# Same class as identified in Phase 1 analysis; sex-matched.
ROLE_NAMES = {
    117:  "Antoine",  # vedeta       (Bio C, M)
    778:  "Chloé",    # campionul    (Bio C, F)
    1218: "Rémi",     # surpriza     (Mate C, M)
    1332: "Léa",      # puntea       (Mate C, F)
    276:  "Damien",   # dependentul  (Chimie B, M)
    1519: "Yann",     # izolatul     (Mate C, M)
}

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

# --- 5. nodes (sorted by id, French names assigned deterministically by sex)
nodes = [{"id": n, "group": klass[n], "sex": sex.get(n, "Unknown")} for n in sorted(used)]

def assign_french_names(node_list):
    """Assign unique French names to nodes. Sex-matched. Six protagonists get fixed names."""
    used_names = set(ROLE_NAMES.values())
    f_iter = iter(nm for nm in FRENCH_F if nm not in used_names)
    m_iter = iter(nm for nm in FRENCH_M if nm not in used_names)
    n_iter = iter(nm for nm in FRENCH_N if nm not in used_names)
    assigned = {}
    for n in node_list:
        if n["id"] in ROLE_NAMES:
            n["name"] = ROLE_NAMES[n["id"]]
            assigned[n["name"]] = n["id"]
            continue
        pool_iter = f_iter if n["sex"] == "F" else m_iter if n["sex"] == "M" else n_iter
        try:
            nm = next(pool_iter)
            while nm in assigned:
                nm = next(pool_iter)
            n["name"] = nm
            assigned[nm] = n["id"]
        except StopIteration:
            raise RuntimeError(f"Pool epuizat pentru sex={n['sex']} la id {n['id']}. Extinde lista franceza.")
    # Verify uniqueness across the whole node set
    seen = {}
    for n in node_list:
        if n["name"] in seen:
            raise RuntimeError(f"Nume duplicat: {n['name']} pentru id {n['id']} si id {seen[n['name']]}.")
        seen[n["name"]] = n["id"]
    return node_list

assign_french_names(nodes)

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

# --- 11b. FULL SCHOOL: 9 classes, day 1, prag 3. Only descriptive stats,
#          not the interactive network (which stays on 3 classes for readability).
full_classes = sorted({c for c in klass.values()})
full_keep = set(klass.keys())
full_w = Counter()
for t, i, j in rows:
    if day_start <= t <= day_end and i in full_keep and j in full_keep:
        a, b = (i, j) if i < j else (j, i)
        full_w[(a, b)] += 1
full_edges_pairs = [(a, b, c) for (a, b), c in full_w.items() if c >= MIN_WEIGHT]
full_used = set()
for a, b, _ in full_edges_pairs:
    full_used.add(a); full_used.add(b)
full_group_by = {n: klass[n] for n in full_used}
full_sex_by   = {n: sex.get(n, "Unknown") for n in full_used}
full_deg = Counter()
for a, b, _ in full_edges_pairs:
    full_deg[a] += 1
    full_deg[b] += 1
for n in full_used:
    full_deg.setdefault(n, 0)

full_class_freq = {}
full_class_mean_degree = {}
full_class_contact_split = {}
full_class_sex_composition = {}
full_total_weight = sum(c for _, _, c in full_edges_pairs)

for c in full_classes:
    class_nodes = [n for n in full_used if full_group_by[n] == c]
    n_class = len(class_nodes)
    nF = sum(1 for n in class_nodes if full_sex_by[n] == "F")
    nM = sum(1 for n in class_nodes if full_sex_by[n] == "M")
    nUnk = sum(1 for n in class_nodes if full_sex_by[n] not in ("F", "M"))
    full_class_freq[c] = {"n": n_class, "nF": nF, "nM": nM, "nUnk": nUnk}
    cd = [full_deg[n] for n in class_nodes]
    full_class_mean_degree[c] = {
        "mean":    round(sum(cd) / len(cd), 1) if cd else 0.0,
        "degrees": cd,
    }
    denom = max(1, nF + nM)
    full_class_sex_composition[c] = {
        "pctF": round(100 * nF / denom, 1),
        "pctM": round(100 * nM / denom, 1),
        "n":    n_class,
        "nF":   nF,
        "nM":   nM,
    }
    internal, external = 0, 0
    for (a, b, weight) in full_edges_pairs:
        gs, gt = full_group_by[a], full_group_by[b]
        if gs == c and gt == c:
            internal += weight
        elif gs == c or gt == c:
            external += weight
    tot = internal + external
    full_class_contact_split[c] = {
        "internalPct": round(100 * internal / tot, 1) if tot else 0.0,
        "externalPct": round(100 * external / tot, 1) if tot else 0.0,
    }
full_inter_class_weight = sum(c for (a, b, c) in full_edges_pairs if full_group_by[a] != full_group_by[b])
full_inter_class_pct    = round(100 * full_inter_class_weight / full_total_weight, 1) if full_total_weight else 0.0
full_class_contact_split["globalBetweenPct"] = full_inter_class_pct

full_school = {
    "classes":            full_classes,
    "totalStudents":      len(full_used),
    "edges":              len(full_edges_pairs),
    "classFreq":          full_class_freq,
    "classMeanDegree":    full_class_mean_degree,
    "classContactSplit":  full_class_contact_split,
    "classSexComposition": full_class_sex_composition,
    "interClassPct":      full_inter_class_pct,
}

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

# --- 16. edgeCountByThreshold (asupra celor N elevi)
edge_count_by_threshold = {}
for t in range(1, 11):
    edge_count_by_threshold[str(t)] = sum(
        1 for (a, b), c in w.items() if c >= t and a in used and b in used
    )
print()
print(f"CALIBRARE MIN_WEIGHT (pentru {len(CLASSES)} clase = {sum(1 for x in klass.values() if x in CLASSES)} elevi in metadata):")
for t in [3, 4, 5, 6]:
    n_edges = sum(1 for (a, b), c in w.items() if c >= t)
    used_at = set()
    for (a, b), c in w.items():
        if c >= t: used_at.add(a); used_at.add(b)
    print(f"  prag {t}: {n_edges} muchii, {len(used_at)} noduri")
print(f"Pragul ales pentru rețeaua principală: MIN_WEIGHT = {MIN_WEIGHT}")

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

# --- 21. TRANSA 0: compute slice metrics for both felia and fullSchool

# Sliced 3-class: use the network we already built.
slice3_name_map = {n["id"]: n["name"] for n in nodes}
slice3_edges_list = [(e["source"], e["target"], e["weight"]) for e in edges]
slice3_metrics = compute_slice_metrics(
    nodes_list=[n["id"] for n in nodes],
    edges_list=slice3_edges_list,
    klass_map=group_by,
    sex_map=sex_by,
    name_map=slice3_name_map,
    tag="slice3",
    seed=42,
)

# Full school: assign French names to any students not covered by the 299-node core.
full_sorted_ids = sorted(full_used)
full_name_map = dict(slice3_name_map)  # start from the 299 already named
used_names = set(full_name_map.values())
f_iter = iter(nm for nm in FRENCH_F if nm not in used_names)
m_iter = iter(nm for nm in FRENCH_M if nm not in used_names)
n_iter = iter(nm for nm in FRENCH_N if nm not in used_names)
for nid in full_sorted_ids:
    if nid in full_name_map: continue
    s = sex.get(nid, "Unknown")
    pool_iter = f_iter if s == "F" else m_iter if s == "M" else n_iter
    try:
        nm = next(pool_iter)
        while nm in used_names: nm = next(pool_iter)
        full_name_map[nid] = nm
        used_names.add(nm)
    except StopIteration:
        raise RuntimeError(f"Pool epuizat pentru elev {nid} sex={s}")

full_edges_list = [(a, b, c) for (a, b, c) in full_edges_pairs]
full_metrics = compute_slice_metrics(
    nodes_list=full_sorted_ids,
    edges_list=full_edges_list,
    klass_map=full_group_by,
    sex_map=full_sex_by,
    name_map=full_name_map,
    tag="full9",
    seed=42,
)

# Attach the new metrics under a "transA0" key inside each slice bucket for clarity.
full_school["metrics"] = full_metrics

# --- 22. stats
stats = {
    "total":         len(nodes),
    "edges":         len(edges),
    "degrees":       deg_list,
    "meanDegree":    mean_deg,
    "medianDegree":  median_deg,
    "maxDegree":     max_deg,
    "exempluGrad":   median_deg,
    "pasi":          4,
    "maxTransmiteri": 4,
    "classNames":    CLASS_NAMES,
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
    "fullSchool":           full_school,
    "sliceMetrics":         slice3_metrics,
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
print()
print(f"FULL SCHOOL: {full_school['classes']}  ({full_school['totalStudents']} elevi, {full_school['edges']} legaturi, {full_inter_class_pct}% intre clase)")
for c in full_school['classes']:
    cf = full_school['classFreq'][c]
    csx = full_school['classSexComposition'][c]
    cmd = full_school['classMeanDegree'][c]
    print(f"  {c:>6}: {cf['n']:>2} elevi ({cf['nF']}F/{cf['nM']}M/{cf['nUnk']}?)  {csx['pctF']}%F  grad med {cmd['mean']}")

def calibrate_new_diffusion(nodes_list, edges_list, klass_map, sex_map, name_map):
    """Test all combinations of (pasi, max_t) and report the coverage table."""
    print()
    print("=== CALIBRARE MODEL NOU DE DIFUZIE ===")
    print(f"N = {len(nodes_list)} noduri, {len(edges_list)} muchii")
    print(f"{'PASI':>4} {'MAX_T':>5} | {'top3pop':>8} {'top3op':>7} {'oneComm':>7} {'greedy':>7} {'randMean':>9} {'randMax':>7} {'gap':>6} | {'pop':>4} {'grd':>4} {'max':>4}")
    print("-" * 100)
    results = []
    for pasi_t in [2, 3, 4]:
        for max_t_t in [2, 3, 4]:
            m = compute_slice_metrics(nodes_list, edges_list, klass_map, sex_map, name_map, tag=f"cal-{pasi_t}-{max_t_t}", seed=42, pasi=pasi_t, max_t=max_t_t)
            s = m["strategies"]
            pop = s["topPopular"]["coverage"]
            openn = s["topOpen"]["coverage"]
            pcomm = s["oneEachComm"]["coverage"]
            greedy = s["greedy"]["coverage"]
            randmean = s["randomMean"]
            randmax = s["randomMax"]
            n = len(nodes_list)
            pct = lambda x: 100 * x / n
            gap = pct(greedy) - pct(pop)
            print(f"{pasi_t:>4} {max_t_t:>5} | {pct(pop):>7.1f}% {pct(openn):>6.1f}% {pct(pcomm):>6.1f}% {pct(greedy):>6.1f}% {pct(randmean):>8.1f}% {pct(randmax):>6.1f}% {gap:>+5.1f}% | {pop:>4} {greedy:>4} {randmax:>4}")
            results.append({"pasi": pasi_t, "max_t": max_t_t, "pop": pop, "greedy": greedy, "randmax": randmax, "gap_pct": gap, "top_single": m["strategies"]["topSingle"]["coverage"], "top_single_pct": pct(m["strategies"]["topSingle"]["coverage"])})
    print("-" * 100)
    print("CRITERII: greedy - top3pop >= 15pp, iar acoperirea max < 80% din scoala.")
    ok = [r for r in results if r["gap_pct"] >= 15 and (100 * r["randmax"] / len(nodes_list)) < 80]
    if ok:
        best = max(ok, key=lambda r: (r["gap_pct"], -abs(80 - 100 * r["randmax"] / len(nodes_list))))
        print(f"COMBINATII VALIDE: {len(ok)}. Aleasa: PASI={best['pasi']}, MAX_T={best['max_t']} (gap {best['gap_pct']:+.1f}pp)")
    else:
        print("NICIO COMBINATIE nu satisface criteriile. Cel mai bun gap:")
        best = max(results, key=lambda r: r["gap_pct"])
        print(f"  PASI={best['pasi']}, MAX_T={best['max_t']}, gap {best['gap_pct']:+.1f}pp, randmax {100 * best['randmax'] / len(nodes_list):.1f}%")
    print()
    print("=== SINGLE-SEED RANKING (cine castiga la 1 seminta) ===")
    for r in results:
        print(f"  PASI={r['pasi']} MAX_T={r['max_t']}: cel mai bun solo atinge {r['top_single']} elevi ({r['top_single_pct']:.1f}%)")
    return best


def report_slice(tag, m):
    print()
    print(f"=== TRANSA 0 metrics · {tag} ===")
    comps = m["components"]
    print(f"componente: {comps['n']} (marimile: {comps['sizes'][:6]}{'...' if len(comps['sizes'])>6 else ''}), izolati: {comps['isolated']}")
    c = m["communities"]
    print(f"comunitati (label prop, seed 42): {c['n']}  potrivire cu clasele: {c['pctMatchClass']}%  nepotriviti: {c['nMismatched']}")
    for cid, ct in c["contingency"].items():
        print(f"  comm {cid} (maj={c['majorityClass'][cid]}): {dict(ct)}")
    ch = m["characters"]
    print(f"caractere:")
    for role in ("star", "bridge", "discreet", "isolated"):
        v = ch[role]
        print(f"  {role:>8}: {v['name']} (id {v['id']}, {v['class']})  pop={v['popularity']}  desc={v['openness']}  reach={v['reach']}")
    s = m["strategies"]
    print(f"strategii (acoperire din 3 seed-uri):")
    for st in ("topPopular", "topOpen", "oneEachComm", "greedy"):
        seeds = [n["name"] for n in s[st]["seeds"]]
        print(f"  {st:>12}: {seeds} -> {s[st]['coverage']}")
    print(f"  random 30x: mean={s['randomMean']}, min={s['randomMin']}, max={s['randomMax']}")
    o = m["overlap"]
    op = o["topPopular"]
    print(f"overlap topPopular: individual={[i['coverage'] for i in op['individual']]}  sum={op['sumIndividual']}  joint={op['joint']}  suprapun={op['overlapCount']}")
    for p in op["pairs"]:
        print(f"  {p['a']['name']} ∩ {p['b']['name']}: {p['sharedContacts']} contacte comune ({p['sharedNames']})")
    fp = m["friendshipParadox"]
    print(f"paradox: elev {fp['meanDegree']} vs prieteni {fp['meanFriendDegree']}  {fp['pctBelow']}% sub")
    sn = fp["subnet"]
    print(f"  subnet 6 noduri: {[r['name'] for r in sn['nodes']]}  {sn['nBelow']}/6 sub media prietenilor")

report_slice("felia 3 clase", slice3_metrics)
report_slice("full school 9 clase", full_metrics)

# Run calibration and print full table
try:
    best_combo = calibrate_new_diffusion(
        [n["id"] for n in nodes],
        slice3_edges_list,
        group_by, sex_by, slice3_name_map,
    )
except Exception as _e:
    print(f"Calibrare esuata: {_e}")
