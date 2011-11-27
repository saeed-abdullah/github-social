from .. import datautil
from github2.client import Github

github = None

def get_github_client():
    global github

    if github is None:
        github = Github(requests_per_second = 1)

    return github

def test_parse_repo_from_html():
    data = """
    <table class="repo" cellpadding=".3em" cellspacing="0">
        <tr>
        <td class="title">
            <a href="/facebook/tornado">tornado</a>
        </td>
        </tr>

        <tr>
        <td class="title">
            <a href="/django/django">django</a>
        </td>
        </tr>

        <tr>
        <td class="title">
            <a href="/mitsuhiko/flask">flask</a>
        </td>
        </tr>

    </table>
    """    

    expected_list = ["facebook/tornado", "django/django", "mitsuhiko/flask"]

    actual_list = datautil.parse_html_repo_list(data)

    assert actual_list == expected_list

#def test_create_issues_network():

def test_get_next_page_url():
    link1 = '<https://api.github.com/repos/rails/rails/issues?page=22&'\
            + 'per_page=100&state=open>; rel="next", '\
            + '<https://api.github.com/repos/rails/rails/issues?page=22&'\
            + 'per_page=100&state=open>; rel="last", '\
            + '<https://api.github.com/repos/rails/rails/issues?page=1&'\
            + 'per_page=100&state=open>; rel="first", '\
            + '<https://api.github.com/repos/rails/rails/issues?page=20&'\
            + 'per_page=100&state=open>; rel="prev"'
    link_last = '<https://api.github.com/repos/rails/rails/issues?page=1&'\
            + 'per_page=100&state=open>; rel="first", '\
            + '<https://api.github.com/repos/rails/rails/issues?page=21&'\
            + 'per_page=100&state=open>; rel="prev"'

    headers = {'link':link1, 'x-ratelimit-remaining':4000}

    expected_link = "https://api.github.com/repos/rails/rails/issues?"\
            + "page=22&per_page=100&state=open" 

    assert expected_link == datautil.get_next_page_url(headers)

    headers['link'] = link_last
    
    assert datautil.get_next_page_url(headers) is None

def test_ruby_repo_issues():
    repo = "rails/rails"
    state = "closed"


    import json
    from github2.issues import Issue

    li = datautil.ruby_repo_issues(repo, state)
    json_issues = json.loads(li[-1])
    issues = [Issue(**dict((str(k), v) for (k, v) in value.iteritems()))
                    for value in json_issues]


    assert issues[-1].id == 132

    #json_issues = json.loads(li[0])
    #issues = [Issue(**dict((str(k), v) for (k, v) in value.iteritems()))
                    #for value in json_issues]


    #assert issues[0].id == 2351068

    repo = "ask/python-github2"
    li = datautil.ruby_repo_issues(repo, state)
    json_issues = json.loads(li[-1])
    issues = [Issue(**dict((str(k), v) for (k, v) in value.iteritems()))
                    for value in json_issues]

    assert issues[-1].id == 3081


def get_repo_default_branch_test():
    github = get_github_client()

    repo = "schacon/grit"
    assert "master" == datautil.get_repo_default_branch(repo, github)

def get_file_list_test():
    github = get_github_client()
    repo = "octocat/Spoon-Knife"
    expected = ["README", "forkit.gif", "index.html"]
    actual = datautil.get_file_list(repo, "master", github)
    assert set(expected) == set(actual)

def get_all_commits_and_parse_test():
    github = get_github_client()
    repo = "octocat/Spoon-Knife"
    files = ["README", "forkit.gif", "index.html"]

    expected = [['zhuowei', 'invalid-email-address', 'invalid-email-address',
                'dave1010', 'invalid-email-address'],
            ['invalid-email-address','invalid-email-address',
                'invalid-email-address'],
            ['invalid-email-address']]

    actual = datautil.get_all_commits(files, repo, "master", github)


    for x in actual:
        actual_interaction = datautil.parse_commit_interactions(x[1])

        if x[0] == files[0]:
            assert len(x[1]) == 3
            assert actual_interaction == expected[1]

        elif x[0] == files[1]:
            assert len(x[1]) == 1
            assert actual_interaction == expected[2]
        else:
            assert len(x[1]) == 5
            assert actual_interaction == expected[0]

