from .. import datautil

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
            + 'per_pag=100&state=open>; rel="next", '\
            + '<https://api.github.com/repos/rails/rails/issues?page=22&'\
            + 'per_pag=100&state=open>; rel="last", '\
            + '<https://api.github.com/repos/rails/rails/issues?page=1&'\
            + 'per_pag=100&state=open>; rel="first", '\
            + '<https://api.github.com/repos/rails/rails/issues?page=20&'\
            + 'per_pag=100&state=open>; rel="prev"'
    link_last = '<https://api.github.com/repos/rails/rails/issues?page=1&'\
            + 'per_pag=100&state=open>; rel="first", '\
            + '<https://api.github.com/repos/rails/rails/issues?page=21&'\
            + 'per_pag=100&state=open>; rel="prev"'

    headers = {'link':link1, 'x-ratelimit-remaining':4000}

    expected_link = "https://api.github.com/repos/rails/rails/issues?"\
            + "page=22&per_pag=100&state=open" 

    assert expected_link == datautil.get_next_page_url(headers)

    headers['link'] = link_last
    
    assert datautil.get_next_page_url(headers) is None

