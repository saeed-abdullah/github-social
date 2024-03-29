import datautil
import networkutil
import networkx as nx
from github2.client import Github
import pickle

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

    graph = networkutil.create_interaction_network(interactions,
            repo_name=repo)

    nx.write_adjlist(graph, out)


def get_commits_from_repo(repo, github):
    """Fetches commit from repo.

    To build commit interaction network, the current snapshot
    is fetched from the repo then all the blobs (files) are
    fetched from that tree.

    It then fetches all the commits done on the blobs.

    """

    branch = datautil.get_repo_default_branch(repo, github)
    files = datautil.get_file_list(repo, branch, github)

    commits = datautil.get_all_commits(files, repo, branch, github)

    return commits

def commit_interactions_from_repo(commits):
    """Gets interaction from history.

    It returns a list whose each element is a list
    of commit for a particular file.

    param
    ----
    commits: A list of containing tuples of
        (filename, commit_history_of_file).
        See datautil.get_all_commits for more information
    """

    commit_interactions = []
    for commit in commits:
        commit_interactions.append(datautil.parse_commit_interactions(
            commit[1]))

    return commit_interactions


def commit_networks(in_pattern, out_dir, languages):
    """ Builds commit network.

    It retrieves commits from the top most-watched
    repos of the given language. Then, for each repo,
    it builds interaction network from the commit history
    of each blob.

    param:
    in_pattern: The path pattern of file containing top
        most watched repos.
    out_dir: The pattern of the output dir for both
        raw data and graph data.
    lang: List of language.

    Here is the example of each param:
    in_pattern = "../data/most_watched/{0}.txt"
    out_dir = "../data/network/commit/{0}"
    lang = ['python', 'java']

    It should be noted that in out_dir, it is expected
    that there will be sub-dir graph/ and raw/.

    """

    graph_out = out_dir + "/graph/{1}.txt"
    raw_out = out_dir + "/raw/{1}.pickle"

    github = Github(requests_per_second=1)

    for lang in languages:
        with open(in_pattern.format(lang), "r") as f:
            for line in f:
                repo = line.strip()
                f_name = repo.replace('/', '_')

                print "Starting {0} at {1}".format(repo, raw_out.format(
                    lang, f_name))

                commits = get_commits_from_repo(repo, github)

                with open(raw_out.format(lang, f_name), "w") as pickle_f:
                        pickle.dump(commits, pickle_f)

                print "Starting {0} at {1}".format(repo, graph_out.format(
                    lang, f_name))

                commit_interactions = commit_interactions_from_repo(commits)
                g = networkutil.create_interaction_network(
                        commit_interactions, repo_name=repo)

                nx.write_adjlist(g, graph_out.format(lang, f_name))


def read_repos_from_file(filename):
    """Retrieves repos from the file."""
    repos = []
    with open(filename, "r") as f:
        for line in f:
            repos.append(line.strip())

    return repos


def repo_property(repo_file_names, in_pattern):
    """Calculates network property of repos.

    param
    ----
    repo_file_names: List of file names of repo (/ replaced to _).
    in_pattern: Location of adjacency list formatted graph.

    return
    ----
    List of tuples (richness, triangles, transitivity).

    Example of in_pattern:
    graph_dir = "../data/network/issues/python/{0}.txt"
    """

    property_list = []

    for repo in repo_file_names:
        print repo
        graph = nx.read_adjlist(in_pattern.format(repo))
        p = networkutil.get_network_property(graph)

        property_list.append(p)

    return property_list


def get_language_property(repo_dir, graph_dir, out_dir, langs):
    """Retrieves network property for repos for given languages.

    It writes all the property to the disk.

    param
    ----
    repo_dir: Pattern of most-watched repo list file.
    graph_dir: Pattern of graph files for repos.
    out_dir: Patter of output directory.
    langs: List of languages.

    For Example:
    repo_dir = "../data/most_watched/{0}.txt"
    graph_dir = "../data/network/issues/{0}/"
    out_dir = "../data/network/issues/{0}/network_property.pickle"

    lang = ['ruby', 'javascript']

    """

    for lang in langs:
        repos = read_repos_from_file(repo_dir.format(lang))
        repo_file_names = [x.replace("/", "_") for x in repos]

        p = repo_property(repo_file_names, graph_dir.format(lang) + "{0}.txt")

        with open(out_dir.format(lang), "w") as f:
            pickle.dump(p, f)


