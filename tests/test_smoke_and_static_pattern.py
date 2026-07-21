"""Smoke tests + Pattern B (StaticPageScraper) tests."""
from unittest.mock import MagicMock

import pytest
import requests
from conftest import CommonReadingExample, StaticPageScraper, ContentFetchError


def test_imports_cleanly():
    assert CommonReadingExample is not None
    assert issubclass(ContentFetchError, Exception)


def test_is_an_ovos_skill():
    from ovos_workshop.skills import OVOSSkill
    assert issubclass(CommonReadingExample, OVOSSkill)


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
