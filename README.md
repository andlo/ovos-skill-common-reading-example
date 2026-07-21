# <img src='story-512.png' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> Common Reading - Example Provider

A **template**, not a product. Copy this repo and adapt it to build your
own provider skill for
[ovos-skill-common-reading](https://github.com/andlo/ovos-skill-common-reading).

[![Tests](https://github.com/andlo/ovos-skill-common-reading-example/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-common-reading-example/actions/workflows/test.yml)

> This skill is fully functional (it really does read the OpenVoiceOS
> blog aloud if you install it) so that every pattern shown here is
> genuinely tested and working, not pseudocode - but it exists to be
> **copied and adapted**, not installed for its own sake. If you just
> want to read the OVOS blog, install
> [ovos-skill-ovosblog](https://github.com/andlo/ovos-skill-ovosblog)
> instead.

## Why this exists

Building a provider means re-solving the same handful of problems every
time: fetching content, deciding what's worth reading aloud, wiring up
the `ovos.common_reading.*` bus protocol, caching, and - the part that
actually needs a human, not a template - deciding **whether** to
translate and **what** a person would call your source out loud.

This repo shows the mechanical parts done once, correctly, so you can
focus on the parts that need your judgment.

## The two patterns

### Pattern A - RSS feed (`CommonReadingExample` class, fully wired)

Use this when your source publishes RSS/Atom. You get structured items
(title, author, date, often full HTML) for free. This class is wired
into the bus handlers and actually works - it's the same approach as
[ovos-skill-ovosblog](https://github.com/andlo/ovos-skill-ovosblog).

### Pattern B - static page scraping (`StaticPageScraper` class, reference only)

Use this when your source is a plain website with no feed: fetch an
index page, then fetch and parse each item's own page. **Not wired into
this skill's bus handlers** (that would duplicate
[ovos-skill-andersen-tales](https://github.com/andlo/ovos-skill-andersen-tales)
as a real content source) - copy the methods into your own provider
class instead. The exact selectors here (`itemprop="name"`,
`itemprop="text"`) are specific to andersenstories.com; your source will
need its own, found by inspecting its actual HTML.

## Three decisions that are on you, not the template

1. **Should this content be machine-translated?** Blog posts: usually
   fine, with disclosure via `machine_translated` in the search
   response. Poetry, legal text, safety information: maybe not - bad
   translation can be actively wrong in ways that matter. This is a
   judgment call about *your* content.
2. **What does a human call this source out loud?** Your
   `COLLECTION_ALIASES` should be what a person would actually say, not
   your skill_id or package name.
3. **What's worth reading aloud?** Not every HTML tag is useful spoken
   content. `extract_paragraphs()` has one real example of this: full
   `<pre>` code blocks are dropped, but inline `<code>` is kept as part
   of its sentence (dropping it entirely broke sentence grammar - a real
   bug found while building `ovos-skill-ovosblog`).

See the module docstring in `__init__.py` for the full walkthrough.

## How to use this as a template

1. Fork or copy this repo
2. Rename the class, package, `skill_id`
3. Decide: RSS (Pattern A) or static scraping (Pattern B)? Keep one, delete the other
4. Point `FEED_URL` / `STATIC_INDEX_URL` at your source, adjust parsing to match its actual structure
5. Make the three decisions above deliberately
6. Copy the caching pattern as-is - it's the same across every provider
7. Write tests before you trust any of it (see `tests/` here for the shape)

See existing real providers for full worked examples:
[ovos-skill-andersen-tales](https://github.com/andlo/ovos-skill-andersen-tales)
(Pattern B), [ovos-skill-ovosblog](https://github.com/andlo/ovos-skill-ovosblog)
(Pattern A, with translation).

## Category
**Entertainment**

## Tags
#template #example #provider #orchestrator
