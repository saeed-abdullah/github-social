from .. import networkutil

def test_create_issues_interaction_network():
    interactions = [[x for x in range(0, y)] for y in range(2, 5)]

    G = networkutil.create_issues_interaction_network(interactions)

    for interaction in interactions:
        for x in range(len(interaction) - 1, 0, -1):
            assert G.has_edge(interaction[x], interaction[x - 1])
