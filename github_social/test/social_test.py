from .. import social

def repo_property_test():
    repo = ['facebook_tornado']
    in_pattern = "../data/network/issues/python/{0}.txt"

    p = social.repo_property(repo, in_pattern)

    assert len(p) == 1
    assert len(p[0][1])/3. == 90
    assert p[0][2] ==  0.007530208394139279

def read_repos_from_file_test():
    path = "../data/most_watched/python_3.txt"
    repos = ["playframework/play", "django-extensions/django-extensions",
            "simplegeo/python-oauth2"]

    assert repos == social.read_repos_from_file(path)


def get_language_property_test():
    repo_dir = "../data/most_watched/{0}.txt"

    graph_dir = "../data/network/issues/{0}/"
    out_dir = "/tmp/{0}.txt"

    langs = ['python']

    social.get_language_property(repo_dir, graph_dir, out_dir, langs)

