"""Tests for handle_search / handle_fetch_content and the non-English
translation-gate behavior (match against translated titles; stay
silent without a translator)."""
from unittest.mock import MagicMock

from conftest import CommonReadingExample, COMMON_READING_SEARCH_RESPONSE, COMMON_READING_FETCH_CONTENT_RESPONSE, COMMON_READING_PONG


def make_message(data=None):
    m = MagicMock()
    m.data = data or {}
    m.reply = MagicMock(side_effect=lambda mtype, d: MagicMock(msg_type=mtype, data=d))
    return m


def _sample_index():
    return {
        "https://x/a": {"title": "Boring installs", "author": "Alice",
                         "html": "<p>A</p>", "pubdate": "Mon, 01 Jan 2024 00:00:00 GMT"},
        "https://x/b": {"title": "New release", "author": "Bob",
                         "html": "<p>B</p>", "pubdate": "Wed, 01 Jan 2025 00:00:00 GMT"},
    }


def test_handle_search_matches_by_phrase(skill):
    skill.index = _sample_index()
    skill.handle_search(make_message({"phrase": "boring installs"}))
    sent = skill.bus.emit.call_args[0][0]
    assert sent.msg_type == COMMON_READING_SEARCH_RESPONSE
    assert sent.data["content_id"] == "https://x/a"
    assert sent.data["machine_translated"] is False


def test_handle_search_stays_silent_for_unmatched_collection(skill):
    skill.index = _sample_index()
    skill.handle_search(make_message({"phrase": "boring installs", "collection_hint": "grimm"}))
    skill.bus.emit.assert_not_called()


def test_handle_fetch_content_unknown_id_returns_empty(skill):
    skill.index = {}
    skill.handle_fetch_content(make_message({"content_id": "nonexistent"}))
    sent = skill.bus.emit.call_args[0][0]
    assert sent.msg_type == COMMON_READING_FETCH_CONTENT_RESPONSE
    assert sent.data["paragraphs"] == []


def test_non_english_matches_against_translated_titles(skill, monkeypatch):
    monkeypatch.setattr(CommonReadingExample, "lang", "da-dk", raising=False)
    skill.index = _sample_index()
    fake_translator = MagicMock()
    translations = {"Boring installs": "Kedelige installationer", "New release": "Ny udgivelse"}
    fake_translator.translate.side_effect = lambda text, target, source: translations[text]
    skill._get_translator = MagicMock(return_value=fake_translator)

    skill.handle_search(make_message({"phrase": "kedelige installationer"}))

    sent = skill.bus.emit.call_args[0][0]
    assert sent.data["content_id"] == "https://x/a"
    assert sent.data["title"] == "Kedelige installationer"
    assert sent.data["machine_translated"] is True


def test_non_english_without_translator_stays_silent(skill, monkeypatch):
    monkeypatch.setattr(CommonReadingExample, "lang", "da-dk", raising=False)
    skill.index = _sample_index()
    skill._get_translator = MagicMock(return_value=None)

    skill.handle_search(make_message({"phrase": "kedelige installationer"}))

    skill.bus.emit.assert_not_called()


def test_handle_ping_replies_with_pong(skill):
    skill.handle_ping(make_message())

    sent = skill.bus.emit.call_args[0][0]
    assert sent.msg_type == COMMON_READING_PONG
    assert sent.data["skill_id"] == skill.skill_id
    assert sent.data["collection"] == "the OpenVoiceOS Blog"


def test_handle_ping_does_not_touch_the_index(skill):
    skill.index = None

    skill.handle_ping(make_message())

    skill.bus.emit.assert_called_once()
