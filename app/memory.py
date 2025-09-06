from collections import defaultdict

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
