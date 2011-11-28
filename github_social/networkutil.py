
"""
Miscellaneous network utility code.
"""

import datautil
import networkx as nx

def create_interaction_network(interactions, **kargs):
    """
    Creates an interaction network from issues.

    The definition of interaction network is similar to Crowston and Howison,
    2004 --- there exists an edge between user x to y, if x replied after
    y in the issue thread.

    params
    ----
    interactions: a chronological list of users commenting on a 
        particular issues (see datautil.get_issues_interaction)


    returns
    ----
    The graph
    """

    G = nx.DiGraph(**kargs)

    for interaction in interactions:
        # We need to reverse the list
        G.add_path(interaction[-1::-1])

    return G


def remove_self_loop(graph):
    """Removes self-loops in-place."""
    for node in graph.nodes_iter():
        if graph.has_edge(node, node):
            graph.remove_edge(node, node)

def get_network_property(graph):
    """Returns various property of the graph.

    It calculates the richness coefficient, triangles and transitivity
    coefficient. To do so, it removes self-loops *in-place*. So, there
    is a possibility that the graph passed as parameter has been
    changed.
    """

    remove_self_loop(graph)

    # If number of nodes is less than three
    # no point in calculating these property.
    if len(graph.nodes()) < 3:
        return ({0: 0.0}, 0, 0)

    try:
        richness = nx.rich_club_coefficient(graph)
    except nx.NetworkXAlgorithmError:
        # NetworkXAlgorithmError is raised when
        # it fails achieve desired swaps after
        # maximum number of attempts. It happened
        # for a really small graph. But, just to
        # guard against those cases.
        richness = nx.rich_club_coefficient(graph, False)

    triangle = nx.triangles(graph)
    transitivity = nx.transitivity(graph)

    return (richness, triangle, transitivity)


