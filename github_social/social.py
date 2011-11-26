import datautil
import networkutil
import networkx as nx


def most_watched_repos(out, lang, page=3):
    """Retrieves most watched repos"""

    li = datautil.get_most_watched_repos(lang, page)

    with open(out, "w") as f:
        for repos in li:
            for repo in repos:
                f.write(repo)
                f.write("\n")


def issues_network(out, repo, github):
    """Builds issues netowrk"""

    interactions = datautil.get_issues_interaction(repo, github)

    graph = networkutil.create_issues_interaction_network(interactions)

    nx.write_adjlist(graph, out)




