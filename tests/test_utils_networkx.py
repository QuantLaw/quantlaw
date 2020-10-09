import unittest

import networkx as nx

import quantlaw
from quantlaw.utils.networkx import aggregate_attr_in_quotient_graph


class NetworkxTestCase(unittest.TestCase):
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

    def test_sequence_graph(self):
        G = nx.DiGraph(name="x")
        G.add_node("1_01", chars_n=30, chars_nowhites=24, tokens_n=8, tokens_unique=3)
        G.add_node("1_02", chars_n=30, chars_nowhites=24, tokens_n=6, tokens_unique=3)
        G.add_node("1_03", chars_n=20, chars_nowhites=16, tokens_n=4, tokens_unique=2)
        G.add_node("1_04", chars_n=10, chars_nowhites=8, tokens_n=2, tokens_unique=1)
        G.add_node("1_05", chars_n=10, chars_nowhites=8, tokens_n=2, tokens_unique=1)
        G.add_node("1_06", chars_n=10, chars_nowhites=8, tokens_n=2, tokens_unique=1)
        G.add_node("2_01", chars_n=10, chars_nowhites=8, tokens_n=2, tokens_unique=1)
        G.add_node("2_02", chars_n=10, chars_nowhites=8, tokens_n=2, tokens_unique=1)
        G.add_edges_from(
            [
                ["1_01", "1_02"],
                ["1_02", "1_03"],
                ["1_03", "1_04"],
                ["1_03", "1_05"],
                ["1_02", "1_06"],
                ["2_01", "2_02"],
            ],
            edge_type="containment",
        )
        G.add_edge("1_04", "2_02", edge_type="reference")

        H = quantlaw.utils.networkx.sequence_graph(G, seq_ref_ratio=23)
        self.assertEqual(["1_04", "1_05", "1_06", "2_02"], list(H.nodes))
        self.assertEqual(
            [
                ("1_04", "2_02", {"edge_type": "reference", "weight": 1 / 23}),
                (
                    "1_04",
                    "1_05",
                    {"backwards": False, "edge_type": "sequence", "weight": 1.0},
                ),
                (
                    "1_05",
                    "1_06",
                    {"backwards": False, "edge_type": "sequence", "weight": 0.5},
                ),
                (
                    "1_05",
                    "1_04",
                    {"backwards": True, "edge_type": "sequence", "weight": 1.0},
                ),
                (
                    "1_06",
                    "1_05",
                    {"backwards": True, "edge_type": "sequence", "weight": 0.5},
                ),
            ],
            list(H.edges(data=True)),
        )

        H = quantlaw.utils.networkx.sequence_graph(G, seq_ref_ratio=0)
        self.assertEqual(["1_04", "1_05", "1_06", "2_02"], list(H.nodes))
        self.assertEqual(
            [("1_04", "2_02", {"edge_type": "reference", "weight": 1})],
            list(H.edges(data=True)),
        )

    def test_quotient_graph(self):
        G = nx.DiGraph(name="x")
        G.add_nodes_from(
            [
                (
                    "root",
                    {
                        "level": -1,
                        "cluster": None,
                    },
                ),
                (
                    "1_04",
                    {
                        "chars_n": 10,
                        "chars_nowhites": 8,
                        "tokens_n": 2,
                        "tokens_unique": 1,
                        "cluster": 1,
                        "level": 3,
                    },
                ),
                (
                    "1_05",
                    {
                        "chars_n": 10,
                        "chars_nowhites": 8,
                        "tokens_n": 2,
                        "tokens_unique": 1,
                        "cluster": 2,
                        "level": 3,
                    },
                ),
                (
                    "1_06",
                    {
                        "chars_n": 10,
                        "chars_nowhites": 8,
                        "tokens_n": 2,
                        "tokens_unique": 1,
                        "cluster": 2,
                        "level": 2,
                    },
                ),
                (
                    "2_02",
                    {
                        "chars_n": 10,
                        "chars_nowhites": 8,
                        "tokens_n": 2,
                        "tokens_unique": 1,
                        "cluster": 1,
                        "level": 1,
                    },
                ),
            ]
        )
        G.add_edges_from(
            [
                ("1_05", "2_02", {"edge_type": "reference", "weight": 1 / 23}),
                (
                    "1_04",
                    "1_05",
                    {"backwards": False, "edge_type": "sequence", "weight": 1.0},
                ),
                (
                    "1_05",
                    "1_06",
                    {"backwards": False, "edge_type": "sequence", "weight": 0.5},
                ),
                (
                    "1_05",
                    "1_04",
                    {"backwards": True, "edge_type": "sequence", "weight": 1.0},
                ),
                (
                    "1_06",
                    "1_05",
                    {"backwards": True, "edge_type": "sequence", "weight": 0.5},
                ),
            ]
        )

        H = quantlaw.utils.networkx.quotient_graph(G, "cluster", aggregation_attrs=None)
        self.assertEqual(
            [
                (
                    1,
                    {},
                ),
                (
                    2,
                    {},
                ),
            ],
            list(H.nodes(data=True)),
        )

        H = quantlaw.utils.networkx.quotient_graph(G, "cluster")
        self.assertEqual(
            [
                (
                    1,
                    {
                        "chars_n": 20,
                        "chars_nowhites": 16,
                        "tokens_n": 4,
                        "tokens_unique": 2,
                    },
                ),
                (
                    2,
                    {
                        "chars_n": 20,
                        "chars_nowhites": 16,
                        "tokens_n": 4,
                        "tokens_unique": 2,
                    },
                ),
            ],
            list(H.nodes(data=True)),
        )
        self.assertEqual(
            [(2, 1, {"edge_type": "reference"})],
            list(H.edges(data=True)),
        )

        H = quantlaw.utils.networkx.quotient_graph(
            G,
            "cluster",
            edge_types=["sequence"],
        )
        self.assertEqual(
            [
                (
                    1,
                    {
                        "chars_n": 20,
                        "chars_nowhites": 16,
                        "tokens_n": 4,
                        "tokens_unique": 2,
                    },
                ),
                (
                    2,
                    {
                        "chars_n": 20,
                        "chars_nowhites": 16,
                        "tokens_n": 4,
                        "tokens_unique": 2,
                    },
                ),
            ],
            list(H.nodes(data=True)),
        )
        self.assertEqual(
            [
                (1, 2, {"edge_type": "sequence", "weight": 1.0}),
                (2, 1, {"edge_type": "sequence", "weight": 1.0}),
            ],
            list(H.edges(data=True)),
        )

    def test_quotient_graph_copy_node_attrs(self):
        G = nx.DiGraph(name="x")
        G.add_nodes_from(
            [
                (
                    "1_01",
                    {
                        "heading": "Bürgerliches Gesetzbuch",
                        "more_info": "test",
                        "chars_n": 10,
                        "chars_nowhites": 8,
                        "tokens_n": 2,
                        "tokens_unique": 1,
                        "law_name": "Bürgerliches Gesetzbuch",
                        "level": 3,
                    },
                ),
                (
                    "2_02",
                    {
                        "heading": "1. Buch",
                        "chars_n": 10,
                        "chars_nowhites": 8,
                        "tokens_n": 2,
                        "tokens_unique": 1,
                        "cluster": 2,
                        "law_name": "Zivilprozessordnung",
                        "level": 3,
                    },
                ),
                (
                    "2_15",
                    {
                        "heading": "2. Buch",
                        "chars_n": 10,
                        "chars_nowhites": 8,
                        "tokens_n": 2,
                        "tokens_unique": 1,
                        "cluster": 2,
                        "law_name": "Zivilprozessordnung",
                        "level": 3,
                    },
                ),
            ]
        )
        G.add_edges_from(
            [
                ("1_01", "2_02", {"edge_type": "reference", "weight": 1 / 23}),
                (
                    "2_02",
                    "2_15",
                    {"backwards": False, "edge_type": "sequence", "weight": 1.0},
                ),
                (
                    "2_02",
                    "2_15",
                    {"backwards": True, "edge_type": "sequence", "weight": 1.0},
                ),
            ]
        )

        H = quantlaw.utils.networkx.quotient_graph(G, "law_name", root_level=None)
        self.assertEqual(
            [
                (
                    "Bürgerliches Gesetzbuch",
                    {
                        "chars_n": 10,
                        "chars_nowhites": 8,
                        "heading": "Bürgerliches Gesetzbuch",
                        "law_name": "Bürgerliches Gesetzbuch",
                        "level": 3,
                        "more_info": "test",
                        "tokens_n": 2,
                        "tokens_unique": 1,
                    },
                ),
                (
                    "Zivilprozessordnung",
                    {
                        "chars_n": 20,
                        "chars_nowhites": 16,
                        "tokens_n": 4,
                        "tokens_unique": 2,
                    },
                ),
            ],
            list(H.nodes(data=True)),
        )
        self.assertEqual(
            [
                (
                    "Bürgerliches Gesetzbuch",
                    "Zivilprozessordnung",
                    {"edge_type": "reference"},
                )
            ],
            list(H.edges(data=True)),
        )

        # Test an if statement
        J = quantlaw.utils.networkx.quotient_graph(
            G,
            "law_name",
        )
        self.assertEqual(list(H.nodes(data=True)), list(J.nodes(data=True)))
        self.assertEqual(list(H.edges(data=True)), list(J.edges(data=True)))
