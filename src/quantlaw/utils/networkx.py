import networkx as nx


def induced_subgraph(G, filter_type, filter_attribute, filter_values):
    """
    Create custom induced subgraph.
    :param filter_type: node|edge
    :param filter_attribute: attribute to filter on
    :param filter_values: attribute values to evaluate to True
    """
    G = nx.MultiDiGraph(G)
    if filter_type == "node":
        nodes = [
            n for n in G.nodes() if G.nodes[n].get(filter_attribute) in filter_values
        ]
        sG = nx.induced_subgraph(G, nodes)
    elif filter_type == "edge":
        sG = nx.MultiDiGraph()
        sG.add_nodes_from(G.nodes(data=True))
        sG.add_edges_from(
            [
                (e[0], e[1], e[-1])
                for e in G.edges(data=True)
                if e[-1][filter_attribute] in filter_values
            ]
        )
    else:
        raise
    sG.graph["name"] = "_".join(
        [G.graph["name"], filter_type, filter_attribute, str(*filter_values)]
    )
    return sG


def hierarchy_graph(G):
    """
    Remove reference edges from G.
    Wrapper around induced_subgraph.
    """
    hG = induced_subgraph(G, "edge", "edge_type", ["containment"])
    return hG


def multi_to_weighted(G):
    """
    Converts a multidigraph into a weighted digraph.
    """
    nG = nx.DiGraph(G)
    # nG.add_nodes_from(G.nodes)
    nG.name = G.name + "_weighted_nomulti"
    edge_weights = {(u, v): 0 for u, v, k in G.edges}
    for u, v, key in G.edges:
        edge_weights[(u, v)] += 1
    # nG.add_edges_from(edge_weights.keys())
    nx.set_edge_attributes(nG, edge_weights, "weight")
    return nG


def get_leaves(G):
    H = hierarchy_graph(G)
    return set([node for node in H.nodes if H.out_degree(node) == 0])
