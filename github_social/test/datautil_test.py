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


