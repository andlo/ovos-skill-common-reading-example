"""Shared pytest fixtures."""
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("example_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

CommonReadingExample = _module.CommonReadingExample
StaticPageScraper = _module.StaticPageScraper
ContentFetchError = _module.ContentFetchError
language_is_supported = _module.language_is_supported
COMMON_READING_SEARCH_RESPONSE = _module.COMMON_READING_SEARCH_RESPONSE
COMMON_READING_FETCH_CONTENT_RESPONSE = _module.COMMON_READING_FETCH_CONTENT_RESPONSE


class FakeFileSystem:
    def __init__(self, base):
        self.base = base
        self.path = str(base)

    def exists(self, name):
        return (self.base / name).exists()

    def open(self, name, mode="r"):
        return open(self.base / name, mode)


@pytest.fixture
def skill(tmp_path, monkeypatch):
    s = CommonReadingExample.__new__(CommonReadingExample)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-common-reading-example.test"
    s.status = MagicMock()
    s._bus = MagicMock()
    s._settings = {}
    monkeypatch.setattr(CommonReadingExample, "lang", "en-us", raising=False)
    s.file_system = FakeFileSystem(tmp_path)
    s.index = {}
    s._translator = None
    s._translator_failed = False
    s._translated_titles_cache = {}
    return s
