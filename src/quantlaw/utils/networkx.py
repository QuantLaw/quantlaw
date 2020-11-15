import networkx as nx


def induced_subgraph(
    G, filter_type, filter_attribute, filter_values, ignore_attrs=False
):
    """
    Create custom induced subgraph.

    Args:
        filter_type: 'node' or 'edge'
        filter_attribute: attribute to filter on
        filter_values: attribute values to evaluate to `True`

    """
    G = nx.MultiDiGraph(G)
    if filter_type == "node":
        nodes = [
            n for n in G.nodes() if G.nodes[n].get(filter_attribute) in filter_values
        ]
        sG = nx.induced_subgraph(G, nodes)
    elif filter_type == "edge":
        sG = nx.MultiDiGraph()
        sG.add_nodes_from(G.nodes(data=not ignore_attrs))
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


def hierarchy_graph(G: nx.DiGraph, ignore_attrs=False):
    """
    Remove reference edges from G.
    Wrapper around induced_subgraph.
    """
    hG = induced_subgraph(G, "edge", "edge_type", ["containment"], ignore_attrs)
    return hG


def multi_to_weighted(G: nx.MultiDiGraph):
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


def get_leaves(G: nx.DiGraph):
    """
    Args:
        G: A tree as directed graph with edges from root to leaves

    Returns: Set of leaves of the tree G
    """
    H = hierarchy_graph(G, ignore_attrs=True)
    return set([node for node in H.nodes if H.out_degree(node) == 0])


def decay_function(key: int):
    """
    Returns a decay function to create a weighted sequence graph.
    """
    return lambda x: (x - 1) ** (-key)


def sequence_graph(
    G: nx.MultiDiGraph, seq_decay_func=decay_function(1), seq_ref_ratio=1
):
    """
    Creates sequence graph for G, consisting of seqitems and their cross-references
    only,
    where neighboring seqitems are connected via edges in both directions.

    Args:
        seq_decay_func: function to calculate sequence edge weight based on distance
            between neighboring nodes
        seq_ref_ratio: ratio between a sequence edge weight when nodes in the
            sequence are at minimum distance from each other and a reference edge weight

    """

    hG = hierarchy_graph(G, ignore_attrs=True)
    # make sure we get _all_ seqitems as leaves, not only the ones without outgoing
    # references
    leaves = [n for n in hG.nodes() if hG.out_degree(n) == 0]

    sG = nx.MultiDiGraph(nx.induced_subgraph(G, leaves))

    if seq_ref_ratio:
        nx.set_edge_attributes(sG, 1 / seq_ref_ratio, name="weight")
        node_headings = dict(sG.nodes(data="heading"))
        ordered_seqitems = sorted(list(node_headings.keys()))

        # connect neighboring seqitems sequentially
        new_edges = get_new_edges(G, ordered_seqitems, seq_decay_func)
        sG.add_edges_from(new_edges)
    else:
        nx.set_edge_attributes(sG, 1, name="weight")

    sG.graph["name"] = f'{G.graph["name"]}_sequence_graph_seq_ref_ratio_{seq_ref_ratio}'

    return sG


def get_new_edges(G, ordered_seqitems, seq_decay_func):
    """
    Convenience function to avoid list comprehension over four lines.
    """
    there = []
    back = []
    hG = hierarchy_graph(G).to_undirected()
    for idx, n in enumerate(ordered_seqitems[:-1]):
        next_item = ordered_seqitems[idx + 1]
        if (
            n.split("_")[0] == next_item.split("_")[0]
        ):  # n and next_item are in the same law
            distance = nx.shortest_path_length(hG, source=n, target=next_item)
            weight = seq_decay_func(distance)
            there.append(
                (
                    n,
                    next_item,
                    {"edge_type": "sequence", "weight": weight, "backwards": False},
                )
            )
            back.append(
                (
                    next_item,
                    n,
                    {"edge_type": "sequence", "weight": weight, "backwards": True},
                )
            )
    return there + back


def quotient_graph(
    G,
    node_attribute,
    edge_types=["reference", "cooccurrence"],
    self_loops=False,
    root_level=-1,
    aggregation_attrs=("chars_n", "chars_nowhites", "tokens_n", "tokens_unique"),
):
    """
    Generate the quotient graph with all nodes sharing the same node_attribute condensed
    into a single node. Simplest use case is aggregation by law_name.
    """

    # node_key:attribute_value map
    attribute_data = dict(G.nodes(data=node_attribute))
    # set cluster -1 if they were not part of the clustering
    # (guess: those are empty laws)
    attribute_data = {
        k: (v if v is not None else -1) for k, v in attribute_data.items()
    }

    # remove the root if root_level is given
    root = None
    if root_level is not None:
        roots = [x for x in G.nodes() if G.nodes[x]["level"] == root_level]
        if roots:
            root = roots[0]

    # unique values in that map with root node
    unique_values = sorted({v for k, v in attribute_data.items() if k != root})

    # build a new MultiDiGraph
    nG = nx.MultiDiGraph()

    # add nodes
    new_nodes = {x: [] for x in unique_values}
    nG.add_nodes_from(unique_values)

    # sort nodes into buckets
    for n in attribute_data.keys():
        if n != root:
            mapped_to = attribute_data[n]
            new_nodes[mapped_to].append(n)
            if G.nodes[n].get("heading") == mapped_to:
                for x in G.nodes[n].keys():
                    nG.nodes[mapped_to][x] = G.nodes[n][x]

    # add edges
    for e in G.edges(data=True):
        if e[-1]["edge_type"] not in edge_types:
            continue
        if (True if self_loops else attribute_data[e[0]] != attribute_data[e[1]]) and (
            True if root_level is None else G.nodes[e[0]]["level"] != root_level
        ):  # special treatment for root
            k = nG.add_edge(
                attribute_data[e[0]], attribute_data[e[1]], edge_type=e[-1]["edge_type"]
            )
            if e[-1]["edge_type"] == "sequence":
                nG.edges[attribute_data[e[0]], attribute_data[e[1]], k]["weight"] = e[
                    -1
                ]["weight"]

    nG.graph["name"] = f'{G.graph["name"]}_quotient_graph_{node_attribute}'

    if aggregation_attrs:
        aggregate_attr_in_quotient_graph(nG, G, new_nodes, aggregation_attrs)

    return nG


def aggregate_attr_in_quotient_graph(nG, G, new_nodes, aggregation_attrs):
    """
    Sums attributes of nodes in an original graph per community and adds the sum to the
    nodes in a quotient graph.

    Args:
        nG: Quotient graph
        G: Original graph
            new_nodes: Mapping of nodes in the quotient graph to an iterable of nodes in
            the original graph that are represented by the node in the quotient graph.
        aggregation_attrs: attributes to aggregate
    """
    for attr in aggregation_attrs:
        attr_data = nx.get_node_attributes(G, attr)
        for community_id, nodes in new_nodes.items():
            aggregated_value = sum(attr_data.get(n) for n in nodes)
            nG.nodes[community_id][attr] = aggregated_value
