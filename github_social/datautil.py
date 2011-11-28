
"""
Miscellaneous data utility code.
"""

from BeautifulSoup import BeautifulSoup, SoupStrainer
import urllib

def parse_html_repo_list(data):
    """
    Parse html data to get most-watched repo list.

    It is assumed that each repo name has the css class "title".

    param
    ----
    data: raw html data.

    returns
    ----

    A list of repo name.
    """

    repos= []

    # The css class for the repo address.
    strainer = SoupStrainer(attrs={"class":"title"})

    repo_table = [tag for tag in BeautifulSoup(data, parseOnlyThese=strainer)]

    for repo in repo_table:
        # First get the tag <a>/<a>, then get the attribute href
        # and then, get rid of first '/'
        repos.append(repo.a["href"][1:])

    return repos

def get_most_watched_repos(language, count=1):
    """
    Scraps html page to retrieve most watched repos from github.

    param
    ----
    language: The language of the repos.
    count: Page count --- each page usually has 25 repos.

    returns
    ----

    A list of most watched repo names for that language.
    """

    repos = []

    base_url = "https://github.com/languages/" + language + \
        "/most_watched?page={0}"

    for page in range(0, count):
        url = base_url.format(page + 1)
        data = urllib.urlopen(url).read()
        repos.append(parse_html_repo_list(data))

    return repos

def get_all_issues(repo, github):
    """
    Returns all issues --- both closed and open.
    """

    issues = github.issues.list(repo, state="open")

    issues.extend(github.issues.list(repo, state ="closed"))

    return issues
    

def parse_interaction_from_issues(github, issues, repo):
    """Parses interaction from list of issues."""
    repo_network = []

    for issue in issues:
        if issue.comments > 0:
            interaction = [issue.user]
            comments = github.issues.comments(repo, issue.number)

            for comment in comments:
                interaction.append(comment.user)

            repo_network.append(interaction)

    return repo_network



def get_issues_interaction(repo, github):
    """
    Returns interaction between users resulting from issues.

    Interaction, here, is a chronological list of users commenting on a 
    particular issues

    params:
    ----
    repos: list of repository.
    github: Github client object.

    returns:
    ----
    A list containing list of interactions per issues.
    """

    issues = get_all_issues(repo, github)


    return parse_interaction_from_issues(github, issues, repo)


def get_next_page_url(header):
    """Returns next page url.
    From the header of the requests, it retrieves
    next page url. For more information,
    see: http://developer.github.com/v3/#pagination

    param
    ----
    header: Returned http headers.

    return
    ----
    The next page url if presented, or None.

    exception
    ----
    Throws ValueError if rate limit is exceeded, check
    http://developer.github.com/v3/#rate-limiting
    """

    if int(header['x-ratelimit-remaining']) <= 0:
        raise ValueError("Rate limit remaining:" +\
                header['x-ratelimit-remaining'])

    if 'link' not in header:
        return None

    links = [x.strip() for x in header['link'].split(",")]
    raw_next = None

    for link in links:
        if link.find('rel="next"') > 0:
            raw_next = [x.strip() for x in link.split(";")]
            break

    if raw_next is None:
        return None
    elif raw_next[0][0] == "<":
        # The link starts with < and ends with >
        return raw_next[0][1:-1]
    else:
        return raw_next[1][1:-1]

def ruby_repo_issues(repo, state):
    """Retrieves issues from ruby repos.

    Most of the ruby repos have too many issues which
    causes API V2 to throw 500 errors. To avoid that
    this method introduces API V3 for retrieving issues.

    param:
    ----
    repo: Name of the repo
    state: closed or open --- type of issues to be retrieved.
    """

    issues = []
    base_url = "https://api.github.com/repos/{0}/issues?" +\
    "per_page=100&page={1}&state="+state

    next_url = base_url.format(repo, "1")

    while next_url:
        f = urllib.urlopen(next_url)
        response = ""
        for line in f:
            response += line

        issues.append(response)

        next_url = get_next_page_url(f.headers)

    return issues

def ruby_issues_json_dump(repo, out):
    """Retrieves json issues from github.

    It gets json data and saves to disk which is later read by
    ruby_issues_json_load later.

    param
    ----
    repo: Name of the repo.
    out: Path of the file to write data
    """

    issues_open = ruby_repo_issues(repo, "open")
    issues_closed = ruby_repo_issues(repo, "closed")


    with open(out, "w") as f:
        pickle.dump([issues_open, issues_closed], f)

def ruby_issues_json_load(in_file):
    """Reads Issues from json data.

    It reads the json data written by ruby_issues_json_dump
    and convert to a list of Issue from github2.issues

    The json data is written to disk in the following format:
    [list_of_open_issues, list_of_closed_issues], where each
    element of the inside list is a string representing a page.

    param
    ----
    in_file: Location of the file containing json data.

    """
    repo_issues = []
    from github2.issues import Issue

    with open(in_file) as f:
        pickle_list = pickle.load(f)

    for state in pickle_list:
        for page in state:
            json_issues = json.loads(page)
            issues = [Issue(**dict((str(k), v) for (k, v) in value.iteritems()))
                for value in json_issues]
            repo_issues.extend(issues)

    return repo_issues

def parse_interaction_from_ruby_issues(github, issues, repo):
    """Parses interaction from list of issues."""
    repo_network = []

    for issue in issues:
        if issue.comments > 0:
            interaction = [issue.user["login"]]
            comments = github.issues.comments(repo, issue.number)

            for comment in comments:
                interaction.append(comment.user)

            repo_network.append(interaction)

    return repo_network



def ruby_issue_json_fetch(in_file, json_file):
    """Fetches issues from ruby repo.
    It fetches raw json data from github repo
    by using API V3 then writes it to the disk.

    param
    ----
    in_file: Template of filename containing repo names.
    json_file: Template of filename containing raw json list of issues.
    Here is the example of each filename:

    in_file = "../data/most_watched/{0}.txt"
    json_file = "../data/network/issues/{0}/json/{1}.json"
    """

    languages = ['ruby']

    for lang in languages:
        with open(in_file.format(lang), "r") as f:

            for line in f:
                repo = line.strip()
                f_name = repo.replace('/', '_')
                print "Starting {0} at {1}".format(repo, json_file.format(lang, f_name))
                ruby_issues_json_dump(repo, json_file.format(lang, f_name))

     
def ruby_issue_json_read(in_file, json_file, out_file, github):
    """Creates issues network for ruby repo.
    
    It reads raw json file listing issues for a particular repo and then
    fetches comments to build a social network.

    param
    ----
    in_file: Template of filename containing repo names.
    json_file: Template of filename containing raw json list of issues.
    out_file: Template of filename to which the resultant graph will be
        written.

    Here is the example of each filename:

    in_file = "../data/most_watched/{0}.txt"
    out_file = "../data/network/issues/{0}/{1}.txt"
    json_file = "../data/network/issues/{0}/json/{1}.json"
    """

    languages = ['ruby']


    for lang in languages:
        with open(in_file.format(lang), "r") as f:

            for line in f:
                repo = line.strip()
                f_name = repo.replace('/', '_')
                print "Starting {0} at {1}".format(repo, out_file.format(lang, f_name))
                issues = ruby_issues_json_load(json_file.format(lang, f_name))
                interactions = parse_interaction_from_ruby_issues(github,
                        issues, repo)


                graph = networkutil.create_interaction_network(
                        interactions)

                nx.write_adjlist(graph, out_file.format(lang, f_name))


def get_repo_default_branch(repo, github):
    """Returns default branch of the repo."""

    branch = github.repos.show(repo).master_branch
    return branch if branch else "master"

def get_file_list(repo, branch, github):
    """Returns all the blobs from the HEAD commit."""

    commits = github.commits.list(repo, branch)
    tree = commits[0].tree

    return github.get_all_blobs(repo, tree).keys()

def get_all_commits(files, repo, branch, github):
    """Returns commits done on the given files.

    param
    ----
    files: List of files (blobs).
    repo: Name of the repo.
    branch: Branch of the repo.
    github: Github client.

    returns
    ----
    List of tuples whose first element is the name of the
        blob and second element is a list containing all the
        commits done on it.
    """
    
    li = []
    for f in files:
        try:
            li.append((f, github.commits.list(repo, branch, file=f)))
        except UnicodeDecodeError:
            print "Unicode Error for file {0} in repo {1} branch {2}".format(f,
                    repo, branch)

    return li

def parse_commit_interactions(commits):
    """Parses interaction from commits.
    Interactions are returned as a chronological list of commit
    author (most recent being the first one).
    """

    li = []
    for commit in commits:
        li.append(commit.author['login'])

    return li

