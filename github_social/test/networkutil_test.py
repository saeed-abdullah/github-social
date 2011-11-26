from .. import networkutil

import networkx as nx

def test_create_issues_interaction_network():
    interactions = [[x for x in range(0, y)] for y in range(2, 5)]

    G = networkutil.create_issues_interaction_network(interactions)

    for interaction in interactions:
        for x in range(len(interaction) - 1, 0, -1):
            assert G.has_edge(interaction[x], interaction[x - 1])


def test_remove_self_loop():
    graph = nx.DiGraph()
    li = [1, 2, 3]

    for x in li:
        graph.add_edge(x, x)

    graph.add_edge(1, 3)

    networkutil.remove_self_loop(graph)

    assert graph.edges() == [(1, 3)]
