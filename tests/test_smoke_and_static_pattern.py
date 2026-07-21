"""Smoke tests + Pattern B (StaticPageScraper) tests + decision point #4
(language_is_supported, the load-time language gate helper)."""
from unittest.mock import MagicMock

import pytest
import requests
from conftest import CommonReadingExample, StaticPageScraper, ContentFetchError, language_is_supported


def test_imports_cleanly():
    assert CommonReadingExample is not None
    assert issubclass(ContentFetchError, Exception)


def test_is_an_ovos_skill():
    from ovos_workshop.skills import OVOSSkill
    assert issubclass(CommonReadingExample, OVOSSkill)


@pytest.mark.parametrize("lang", ["en-us", "en-gb", "da-dk"])
def test_language_is_supported_true_for_matching_base_code(lang):
    assert language_is_supported(lang, {"en", "da"}) is True


@pytest.mark.parametrize("lang", ["de-de", "fr-fr", "pt-pt"])
def test_language_is_supported_false_for_non_matching(lang):
    assert language_is_supported(lang, {"en", "da"}) is False


STATIC_INDEX_HTML = """
<html><body>
<ul class="list_link">
<li><a href="/story-a">The First Story</a></li>
<li><a href="/story-b">The Second Story</a></li>
</ul>
</body></html>
"""

STATIC_ITEM_HTML = """
<html><body>
<h2 itemprop="name">The First Story</h2>
<div itemprop="text">Once upon a time, there was a story.</div>
</body></html>
"""


def test_static_scraper_get_index(monkeypatch):
    fake_response = MagicMock(text=STATIC_INDEX_HTML)
    fake_response.raise_for_status = MagicMock()
    fake_response.apparent_encoding = "utf-8"
    monkeypatch.setattr(requests, "get", lambda *a, **kw: fake_response)

    index = StaticPageScraper.get_index("http://example.test/list")

    assert index == {"The First Story": "/story-a", "The Second Story": "/story-b"}


def test_static_scraper_get_title_and_text(monkeypatch):
    fake_response = MagicMock(text=STATIC_ITEM_HTML)
    fake_response.raise_for_status = MagicMock()
    fake_response.apparent_encoding = "utf-8"
    monkeypatch.setattr(requests, "get", lambda *a, **kw: fake_response)

    assert StaticPageScraper.get_title("http://example.test/story-a") == "The First Story"
    assert StaticPageScraper.get_text("http://example.test/story-a") == "Once upon a time, there was a story."


def test_static_scraper_missing_structure_raises(monkeypatch):
    fake_response = MagicMock(text="<html><body>nothing here</body></html>")
    fake_response.raise_for_status = MagicMock()
    fake_response.apparent_encoding = "utf-8"
    monkeypatch.setattr(requests, "get", lambda *a, **kw: fake_response)

    with pytest.raises(ContentFetchError):
        StaticPageScraper.get_index("http://example.test/list")


def test_static_scraper_network_error_raises(monkeypatch):
    def fail(*a, **kw):
        raise requests.ConnectionError("boom")
    monkeypatch.setattr(requests, "get", fail)

    with pytest.raises(ContentFetchError):
        StaticPageScraper.get_index("http://example.test/list")
