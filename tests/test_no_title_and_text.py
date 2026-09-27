"""Decision points #9 and #10: answer a search that names no title, match
titles case-insensitively, send a User-Agent, and extract text without
mangling the spacing around inline tags."""
from test_bus_protocol import make_message, _sample_index

from conftest import CommonReadingExample, _module


def _search(skill, **data):
    skill.index = _sample_index()
    skill.bus.emit.reset_mock()
    skill.handle_search(make_message(data))
    return [c[0][0].data for c in skill.bus.emit.call_args_list]


def test_no_title_offers_the_latest_post_at_no_title_confidence(skill):
    sent = _search(skill, phrase=None)
    assert len(sent) == 1
    assert sent[0]["content_id"] == "https://x/b"  # the newer post
    assert sent[0]["confidence"] == _module.NO_TITLE_CONFIDENCE == 0.9


def test_no_title_with_the_collection_named_is_fully_confident(skill):
    sent = _search(skill, phrase=None, collection_hint="ovos blog")
    assert len(sent) == 1 and sent[0]["confidence"] == 1.0


def test_titles_match_regardless_of_case(skill):
    sent = _search(skill, phrase="BORING INSTALLS")
    assert sent[0]["content_id"] == "https://x/a"
    assert sent[0]["title"] == "Boring installs"
    assert sent[0]["confidence"] == 1.0


def test_requests_send_a_descriptive_user_agent():
    assert _module.HTTP_HEADERS["User-Agent"].startswith("ovos-skill-common-reading-example/")


def test_no_space_before_punctuation_and_no_glued_words():
    html = ("<p>Tighten <code>threshold</code>. If it returns <b>False</b>, stop.</p>"
            "<p>It ran on <em>geo-thermal</em> energy.<a href='#'>The roads</a> were empty.</p>")
    assert CommonReadingExample.extract_paragraphs(html) == [
        "Tighten threshold. If it returns False, stop.",
        "It ran on geo-thermal energy.The roads were empty.",  # the source's own missing space stays
    ]
