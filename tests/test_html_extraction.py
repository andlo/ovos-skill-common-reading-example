"""Tests for extract_paragraphs() - includes the regression case for the
real bug found while building ovos-skill-ovosblog: stripping <code>
entirely broke sentence grammar."""
from conftest import CommonReadingExample

SAMPLE_HTML = """
<h1>A Title</h1>
<p><code>ovos-installer</code> exists to make things easier.</p>
<ul><li><strong>Method:</strong> <code>virtualenv</code> (only)</li></ul>
<pre><code class="hljs">xcode-select --install
</code></pre>
<p>Last paragraph.</p>
"""


def test_extract_paragraphs_keeps_inline_code_as_sentence_text():
    paragraphs = CommonReadingExample.extract_paragraphs(SAMPLE_HTML)
    assert "ovos-installer exists to make things easier." in paragraphs


def test_extract_paragraphs_keeps_list_items_with_inline_code():
    paragraphs = CommonReadingExample.extract_paragraphs(SAMPLE_HTML)
    assert "Method: virtualenv (only)" in paragraphs


def test_extract_paragraphs_drops_full_code_blocks():
    joined = " ".join(CommonReadingExample.extract_paragraphs(SAMPLE_HTML))
    assert "xcode-select" not in joined


def test_extract_paragraphs_empty_html_returns_empty_list():
    assert CommonReadingExample.extract_paragraphs("") == []
