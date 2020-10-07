import unittest
import networkx as nx

from quantlaw.utils.networkx import aggregate_attr_in_quotient_graph


class TestNetworkx(unittest.TestCase):
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