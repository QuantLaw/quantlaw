import unittest

import networkx as nx

import quantlaw
from quantlaw.utils.networkx import aggregate_attr_in_quotient_graph


class NetworkxTextCase(unittest.TestCase):
    def test_aggregate_attr_in_quotient_graph(self):
        G = nx.Graph()
        G.add_node("a", attr1=30, attr2=2.0)
        G.add_node("b", attr1=300, attr2=2.1)
        G.add_node("c", attr1=3000, attr2=2.01)

        nG = nx.Graph()
        nG.add_nodes_from(["x", "y"])

        new_nodes = {"x": {"a", "b"}, "y": {"c"}}

        aggregation_attrs = ["attr1", "attr2"]

        aggregate_attr_in_quotient_graph(nG, G, new_nodes, aggregation_attrs)

        self.assertEqual(nG.nodes["x"]["attr1"], 330)
        self.assertEqual(nG.nodes["x"]["attr2"], 4.1)
        self.assertEqual(nG.nodes["y"]["attr1"], 3000)
        self.assertEqual(nG.nodes["y"]["attr2"], 2.01)

    def test_induces_subgraph_node(self):
        G = nx.MultiDiGraph(name="test_name")
        G.add_nodes_from(["a", "b", "c"], test_attr="x")
        G.add_nodes_from(["d", "e", "f"], test_attr="y")
        G.add_edge("a", "b")
        G.add_edge("b", "d")
        H = quantlaw.utils.networkx.induced_subgraph(G, "node", "test_attr", ["x"])
        self.assertEqual(["a", "b", "c"], list(H.nodes))
        self.assertEqual([("a", "b", 0)], list(H.edges))

    def test_induces_subgraph_edges(self):
        G = nx.MultiDiGraph(name="test_name")
        G.add_nodes_from(["a", "b", "c"])
        G.add_nodes_from(["d", "e", "f"])
        G.add_edge("a", "b", test_attr="x")
        G.add_edge("a", "b", test_attr="x")
        G.add_edge("b", "d", test_attr="y")
        H = quantlaw.utils.networkx.induced_subgraph(G, "edge", "test_attr", ["x"])
        self.assertEqual(["a", "b", "c", "d", "e", "f"], list(H.nodes))
        self.assertEqual([("a", "b", 0), ("a", "b", 1)], list(H.edges))

    def test_induces_subgraph_fail(self):
        with self.assertRaises(Exception):
            quantlaw.utils.networkx.induced_subgraph(
                nx.Graph(), "xx", "test_attr", ["x"]
            )

    def test_hierarchy_graph(self):
        G = nx.DiGraph(name="asd")
        G.add_edges_from([[1, 2], [1, 3], [1, 4], [2, 5]], edge_type="containment")
        G.add_edges_from([[4, 5]], edge_type="reference")
        H = quantlaw.utils.networkx.hierarchy_graph(G)
        self.assertEqual([1, 2, 3, 4, 5], list(H.nodes))
        self.assertEqual([(1, 2, 0), (1, 3, 0), (1, 4, 0), (2, 5, 0)], list(H.edges))

    def test_multi_to_weighted(self):
        G = nx.MultiDiGraph(name="test_name")
        G.add_nodes_from(["a", "b", "c"])
        G.add_nodes_from(["d", "e", "f"])
        G.add_edge("a", "b")
        G.add_edge("a", "b")
        G.add_edge("b", "d")
        H = quantlaw.utils.networkx.multi_to_weighted(G)
        self.assertEqual(["a", "b", "c", "d", "e", "f"], list(H.nodes))
        self.assertEqual(
            [("a", "b", {"weight": 2}), ("b", "d", {"weight": 1})],
            list(H.edges(data=True)),
        )

    def test_get_leaves(self):
        G = nx.DiGraph(name="asd")
        G.add_edges_from([[1, 2], [1, 3], [1, 4], [2, 5]], edge_type="containment")
        G.add_edges_from([[4, 5]], edge_type="reference")
        leaves = quantlaw.utils.networkx.get_leaves(G)
        self.assertEqual({3, 4, 5}, leaves)
