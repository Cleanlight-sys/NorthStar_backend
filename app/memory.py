from collections import defaultdict
import random

# === Graph Utilities ===

def extract_facet_graph(memory_rows):
    graph = defaultdict(set)
    for row in memory_rows:
        if "facets" in row and row["facets"]:
            for a in row["facets"]:
                for b in row["facets"]:
                    if a != b:
                        graph[a].add(b)
    return graph

def get_related_facets(facet_graph, facets, depth=1):
    related = set(facets)
    for _ in range(depth):
        for f in list(related):
            related.update(facet_graph.get(f, []))
    return list(related)

# === Curriculum Engine ===

def pick_next_challenge(facet_graph, weights_out, all_challenges, past_runs):
    """
    Pick the next challenge by:
    - Avoiding recently run IDs
    - Prioritizing undertrained facets
    """
    recent_ids = {r["challenge_id"] for r in past_runs[-20:]}
    candidates = [c for c in all_challenges if c["id"] not in recent_ids and c.get("facets")]

    # Count facet frequency
    facet_counts = defaultdict(int)
    for c in candidates:
        for f in c["facets"]:
            facet_counts[f] += 1

    def challenge_score(ch):
        score = 0
        for f in ch["facets"]:
            if f in weights_out["weights"]:
                score -= facet_counts.get(f, 1)
        return score + random.random()

    return sorted(candidates, key=challenge_score)
