
"""
Miscellaneous network utility code.
"""

import datautil
import networkx as nx

def create_issues_interaction_network(interactions):
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

    G = nx.DiGraph()

    for interaction in interactions:
        # We need to reverse the list
        G.add_path(interaction[-1::-1])

    return G

