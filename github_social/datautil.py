
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
    

def parse_interaction_from_issues(issues):
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


    return parse_interaction_from_issues(issues)


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
    base_url = "https://api.github.com/repos/rails/rails/issues?" +\
    "per_pag=100&page={0}&state="+state

    next_url = base_url.format(1)

    while next_url:
        f = urllib.urlopen(next_url)
        response = ""
        for line in f:
            response += line

        issues.append(response)

        next_url = get_next_page_url(f.headers)

    return issues

