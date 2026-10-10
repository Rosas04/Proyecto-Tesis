import pytest

from services.screenshot_worker_impl import _get_display_name, _route_key


@pytest.mark.parametrize("url, expected", [
    ("https://quotes.toscrape.com/", "Home"),
    ("https://quotes.toscrape.com/tag/books/page/1/", "Books"),
    ("https://quotes.toscrape.com/tag/books/page/2/", "Books (pág. 2)"),
    ("http://quotes.toscrape.com/author/Jane-Austen/", "Jane Austen"),
    ("https://app.test/#/dashboard/settings", "Settings"),
    ("https://app.test/cursos/123", "Cursos 123"),
    ("https://app.test/index.html", "Home"),
    ("https://app.test/?view=perfil", "Perfil"),
])
def test_display_names_are_readable(url, expected):
    assert _get_display_name(url) == expected


def test_equivalent_routes_share_key():
    assert _route_key("https://www.a.com/tag/life/page/1/") == _route_key("http://a.com/tag/life")
    assert _route_key("https://a.com/index.html") == _route_key("https://a.com/")


def test_distinct_routes_keep_distinct_keys():
    assert _route_key("https://a.com/tag/life/page/2") != _route_key("https://a.com/tag/life")
    assert _route_key("https://a.com/#/a") != _route_key("https://a.com/#/b")
