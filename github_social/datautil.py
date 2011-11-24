
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

    repo_network = []
    issues = get_all_issues(repo, github)


    for issue in issues:
        if issue.comment > 0:
            interaction = [issue.user]
            comments = github.issues.comments(repo, issue.number)

            for comment in comments:
                interaction.append(comment.user)

            repo_network.append(interaction)
