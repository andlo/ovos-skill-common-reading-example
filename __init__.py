"""
skill OVOS Common Reading Example
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

TEMPLATE / EXAMPLE SKILL - not meant to be installed for its own content
value. Copy this repo, rename the class, and adapt the parts you need
for your own ovos-skill-common-reading provider.

It demonstrates TWO real, working, tested content-fetching patterns:

  PATTERN A - RSS FEED (see RssExampleMixin below)
      Source: blog.openvoiceos.org's feed. Same approach as
      ovos-skill-ovosblog. Use this pattern when your source publishes
      an RSS/Atom feed - you get structured items (title, author, date,
      often full HTML content) for free, no need to guess at page
      structure.

  PATTERN B - STATIC PAGE SCRAPING (see StaticPageScraper below)
      Source: andersenstories.com. Same approach as
      ovos-skill-andersen-tales. Use this pattern when your source is a
      plain website with no feed - you fetch an index page, then fetch
      each item's own page and parse whatever HTML structure it uses
      (here: schema.org itemprop attributes). This is INCLUDED FOR
      REFERENCE ONLY here - it is not wired into this skill's bus
      handlers (only Pattern A is live), to avoid this example
      duplicating ovos-skill-andersen-tales as a real content source.

THINGS THAT ARE DELIBERATELY *NOT* AUTOMATIC - YOU MUST DECIDE THESE
PER PROVIDER, THIS TEMPLATE ONLY SHOWS *HOW*, NOT WHETHER:

  1. SHOULD THIS CONTENT BE MACHINE-TRANSLATED?
     Blog posts/articles: usually fine, with disclosure (see
     ovos-skill-ovosblog). Poetry, legal text, medical/safety
     information, anything where exact wording matters: probably NOT -
     a bad translation could be actively harmful or just wrong in a way
     that matters. This is a judgment call about YOUR content, not
     something to default to blindly. If you do translate, always
     disclose it via 'machine_translated' in the search response (see
     ovos-skill-common-reading's README).

  2. WHAT DOES A HUMAN ACTUALLY CALL THIS SOURCE?
     Your collection_hint aliases should be what a person would say out
     loud, not your skill_id or package name. 'the openvoiceos blog' and
     'ovos blog', not 'ovos-skill-ovosblog'. Think about this from the
     user's side, not the code's side.

  3. WHAT'S ACTUALLY WORTH READING ALOUD?
     Not every HTML element on a page is useful spoken content - code
     blocks, navigation, ads, footers. Look at your specific source's
     HTML and decide what to keep (see extract_paragraphs below for one
     real example of this kind of decision - inline <code> is kept as
     part of its sentence, but full <pre> code blocks are dropped). How to
     get that text out without mangling it is decision point #10.

  4. IF YOU DON'T TRANSLATE, REFUSE TO LOAD UNLESS A CONFIGURED LANGUAGE
     IS ONE YOU SUPPORT - DON'T JUST DECLINE SEARCHES AT RUNTIME.
     This example (Pattern A) translates, so it loads whatever the
     language - see decision point #1 (and #8 for which languages it
     answers in). But most sources DON'T have a good reason to translate
     (see ovos-skill-andersen-tales/ovos-skill-grimm-tales/
     ovos-skill-andrew-lang-tales: real per-language sources or none at
     all, no translation attempted). For those, check at the TOP of
     initialize(), before building any index or registering any bus
     events, whether any language this installation is configured for
     is one you support. "Configured for" is the device's own 'lang'
     PLUS 'secondary_langs' in mycroft.conf - self.native_langs in
     ovos-workshop - not the device language alone: a HiveMind hub runs
     one ovos-core for users in several languages and lists them in
     secondary_langs.

         SUPPORTED_LANGUAGES = {"en", "da", "de"}  # whatever your source covers

         def initialize(self):
             self.served = configured_languages(self.native_langs) & SUPPORTED_LANGUAGES
             if not self.served:
                 self.log.info(
                     f"{self.skill_id}: none of the configured languages "
                     f"{sorted(self.native_langs)} is supported and this "
                     f"provider does not translate - skill will stay inert."
                 )
                 return
             # ... normal setup for each language in self.served:
             # build its index, load its locale meta, self.add_event(...)

     This is meaningfully better than gating inside handle_search(): the
     skill never wastes work building an index it can't use, never even
     listens for ovos.common_reading.search where nobody speaks its
     languages, and the log clearly explains why at load time instead of
     the provider just mysteriously never answering. See
     ovos-skill-andersen-tales's __init__.py for the real version of
     this pattern, including one index per served language.

  5. NAME YOUR REPO/PACKAGE ovos-skill-<NAME>-<CONTENT TYPE>.
     Not a strict requirement, but every provider in this family follows
     it, and it's a genuinely useful convention: ovos-skill-andersen-
     tales, ovos-skill-grimm-tales, ovos-skill-arxiv-papers, ovos-skill-
     365tomorrows-stories. <NAME> is whatever identifies the source
     (an author, a site, a collection), <CONTENT TYPE> is a short plural
     noun for what it delivers (tales, papers, stories, articles). This
     makes a skill's purpose legible at a glance in a list of a dozen
     providers, and keeps it distinct from same-named skills that do
     something other than read content aloud (e.g. an existing
     'fairytales' skill with a different architecture - see
     ovos-skill-fairytales vs. this family's ovos-skill-andersen-tales/
     ovos-skill-grimm-tales, which deliberately don't reuse that name).

  6. IF YOU SUPPORT MULTIPLE LANGUAGES WITHOUT TRANSLATING, LOCALIZE
     YOUR COLLECTION_ALIASES/AUTHOR_NAME/COLLECTION_NAME TOO - DON'T
     HARDCODE THEM IN ENGLISH.
     This example (Pattern A) translates, so it only ever needs one
     English collection name - see decision point #1. But a provider
     using the SUPPORTED_LANGUAGES gate (decision point #4) genuinely
     serves several languages without translating, and 'the Brothers
     Grimm'/'Grimm's Fairy Tales' hardcoded in English breaks two
     things: a German user saying 'die Gebrüder Grimm' as a
     collection_hint only matches by luck (if it happens to share a
     substring with the English alias), and the pipeline's pre-reading
     announcement ends up mixing languages - a correctly-localized
     German title glued to an English author/collection name.

     Fix: load these from locale/<lang>/ instead of Python constants,
     using OVOS's own resource file resolution (self.resources) rather
     than reinventing language fallback:

         def initialize(self):
             ...
             self._load_collection_meta()  # after the language gate passes
             ...

         def _load_collection_meta(self):
             aliases_raw = self.resources.load_vocabulary_file("collection")
             self._collection_aliases = [phrase for line in aliases_raw for phrase in line]
             meta = self.resources.load_json_file("collection_meta.json")
             self._author_name = meta["author"]
             self._collection_name = meta["collection"]

     ...with locale/<lang>/collection.voc (one alias phrase per line -
     the idiomatic OVOS mechanism for "list of phrases meaning the same
     thing") and locale/<lang>/collection_meta.json
     (`{"author": "...", "collection": "..."}`) for every language in
     your SUPPORTED_LANGUAGES set. You only need ONE folder per
     canonical language (e.g. locale/en-us/, not separate en-gb/en-au/
     folders) - self.resources already does distance-based language
     fallback (langcodes.tag_distance) when resolving these files, so a
     device on 'en-gb' automatically finds locale/en-us/.

     This also means every language needs its own locale/<lang>/
     skill.json, not just en-us - per the OVOS technical manual, that's
     how the Skills Store is meant to discover which languages a skill
     actually supports. See ovos-skill-andersen-tales/
     ovos-skill-grimm-tales's __init__.py and locale/ for the real
     version of this pattern, and
     ovos-common-reading-pipeline-plugin#26 for the full reasoning.

  7. IF YOU DO TRANSLATE, STILL LOCALIZE YOUR COLLECTION_ALIASES - WITH
     AN ENGLISH FALLBACK INSTEAD OF A FIXED LANGUAGE SET.
     A translating provider (this example's Pattern A) works in any
     configured language, so there's no bounded list of locale/<lang>/
     folders you can guarantee exist. _load_collection_aliases() loads
     locale/<lang>/collection.voc where one exists and falls back to
     FALLBACK_COLLECTION_ALIASES (English) otherwise, so collection_hint
     matching never breaks completely. COLLECTION_NAME usually stays
     untranslated: brand names ("arXiv", "365tomorrows") don't need it.

  8. ANSWER EACH REQUEST IN ITS OWN LANGUAGE.
     Once loaded, decide per request - not from the device language -
     whether and in which language to answer. The request's language is
     the pipeline plugin's 'lang' field, else the language of the
     session it was forwarded from (a HiveMind client's, on a hub), else
     the device's own (an older plugin sends neither) - see
     _request_lang() below. Answer search and ping only when that
     language is one you serve (self.served for a non-translating
     provider; configured_languages(self.native_langs) for a translating
     one like this example). Answer fetch_content always: it is
     addressed to you by skill_id and the plugin is waiting for it.

     For a translating provider this matters twice over: a search in a
     language nobody here speaks would otherwise load a translation
     model and translate your whole title catalogue - on a test box, one
     French search loaded NLLB once per translating provider (~7 GB).

  9. ANSWER A SEARCH THAT NAMES NO TITLE.
     "Tell me a story" (the pipeline plugin's ReadAnyStory intent, from
     0.2.0) and "read me an article" search with phrase=None. A provider
     that stays silent then is never picked. Offer something that fits the
     content_type: a random story for a story provider, the latest post for
     a feed like this one. Answer at NO_TITLE_CONFIDENCE (0.9), or 1.0 when
     the collection itself was named ("a story from Grimm"). See
     handle_search() below. Also match titles case-insensitively: titles
     keep their case, spoken requests never do.

  10. FETCH POLITELY, AND EXTRACT TEXT THAT READS WELL.
     Fetching:
     - Send a descriptive User-Agent (HTTP_HEADERS below). Some sites answer
       python-requests' default with 403 - 365tomorrows.com, behind
       Cloudflare, does.
     - Fetch a source as rarely as it changes. For a book or anything else
       that never changes, cache the extracted text on disk (the skill's XDG
       cache directory), ask again with If-Modified-Since after a long
       while, back off for a few minutes after a failure, and read the stale
       copy meanwhile. Drop parse trees as soon as the text is out - a
       Gutenberg book is 5-10 MB of BeautifulSoup. See
       ovos-skill-bechstein-tales (StoryCache, extract_book()) for the
       reference version.
     - Never let an empty fetch (a feed with nothing today, e.g. arXiv on
       weekends) overwrite a good cached index: raise instead, and let
       refresh_index() fall back to the cache, as fetch_feed_index() does.
     Extracting:
     - get_text() with no separator, then collapse the whitespace - see
       extract_paragraphs() for what both other forms get wrong.
     - Keep the source's own paragraphs (a <div> per paragraph on
       andersenstories.com/grimmstories.com, not one .text for the whole
       story): the reading plugin pauses between them, and its SSML
       narration marks them.
     - A <br> inside a paragraph is a line break (verse); a newline in the
       HTML source is just whitespace.
     - Drop what isn't the text: page numbers (<span class="pagenum">),
       footnote markers ([1]) and their notes, editorial source notes,
       licence boilerplate. Read verse (<pre>, <div class="verse">), which
       only-<p> extraction skips.
"""

from ovos_workshop.skills import OVOSSkill
from ovos_bus_client.session import SessionManager
from ovos_utils.parse import match_one
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import json


def _user_agent():
    """Say who is asking. Some sites answer python-requests' default
    User-Agent with 403 (365tomorrows.com behind Cloudflare does), and a
    descriptive one is what sites ask automated clients to send."""
    try:
        from importlib.metadata import version
        ver = version("ovos-skill-common-reading-example")
    except Exception:
        ver = "unknown"
    return f"ovos-skill-common-reading-example/{ver} (+https://github.com/andlo/ovos-skill-common-reading-example)"


HTTP_HEADERS = {"User-Agent": _user_agent()}

# --- PATTERN A: RSS FEED config ---
FEED_URL = "https://blog.openvoiceos.org/feed.xml"
DC_CREATOR_TAG = "{http://purl.org/dc/elements/1.1/}creator"

# --- PATTERN B: STATIC PAGE config (reference only, see StaticPageScraper) ---
STATIC_INDEX_URL = "https://www.andersenstories.com/en/andersen_fairy-tales/list"


class ContentFetchError(Exception):
    """Raised when content could not be fetched or parsed."""


def language_is_supported(lang, supported_languages):
    """True when a language tag ('en-us') is in a set of primary
    subtags ({'en', 'da'}). Kept for providers built from an older copy
    of this template - new ones gate on configured_languages() instead
    (see decision points #4 and #8)."""
    return primary_subtag(lang) in supported_languages


# ovos.common_reading.* bus protocol - see ovos-skill-common-reading/README.md
COMMON_READING_SEARCH = "ovos.common_reading.search"
COMMON_READING_SEARCH_RESPONSE = "ovos.common_reading.search.response"
COMMON_READING_FETCH_CONTENT = "ovos.common_reading.fetch_content"  # + ".{this_skill_id}"
COMMON_READING_FETCH_CONTENT_RESPONSE = "ovos.common_reading.fetch_content.response"
# ping/pong: a lightweight 'is anyone there?' check, broadcast by the
# pipeline plugin only on its rare 0-candidates path (never on every
# search). Answering this is REQUIRED, not optional - a provider that
# never pongs is indistinguishable from one that isn't installed at
# all, from the pipeline's perspective. See
# ovos-common-reading-pipeline-plugin's README, section 3.
COMMON_READING_PING = "ovos.common_reading.ping"
COMMON_READING_PONG = "ovos.common_reading.pong"

# the confidence of an answer to a search that named no title (decision
# point #8): the pipeline plugin reads anything from 0.8 up without asking
# "is it that one?", and a named title's own match should still win
NO_TITLE_CONFIDENCE = 0.9

# DECISION POINT #2 (see module docstring): pick names a human would
# actually say, not your skill_id. DECISION POINT #7: since this
# provider translates (works on ANY device language, no fixed
# SUPPORTED_LANGUAGES set), COLLECTION_ALIASES below is a FALLBACK, not
# the only source of truth - see _load_collection_aliases() and
# locale/<lang>/collection.voc.
FALLBACK_COLLECTION_ALIASES = ["openvoiceos blog", "ovos blog", "open voice os blog", "the openvoiceos blog"]
CONTENT_TYPES = ["article", "blog", "news", "post"]
COLLECTION_HINT_THRESHOLD = 0.85  # see ovos-skill-common-reading's README - don't go lower than this
COLLECTION_NAME = "the OpenVoiceOS Blog"
SOURCE_NAME = "blog.openvoiceos.org"



def primary_subtag(lang):
    """'en-US', 'en_gb', 'EN' -> 'en'."""
    return (lang or "").replace("_", "-").split("-")[0].lower()


def configured_languages(langs):
    """Primary subtags of the languages an installation is configured
    for (core lang + secondary_langs): ['en-US', 'da-DK'] -> {'en', 'da'}."""
    return {primary_subtag(lang) for lang in langs or [] if lang}

class CommonReadingExample(OVOSSkill):
    """PATTERN A provider - fully wired to the bus. Reads
    blog.openvoiceos.org, exactly like ovos-skill-ovosblog, so it's a
    genuinely runnable/testable example rather than pseudocode."""

    INDEX_CACHE_TTL = 60 * 60  # 1 hour - match your source's own freshness signal if it has one

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=True,
            network_before_load=True,
            requires_internet=True,
            requires_network=True,
            no_internet_fallback=True,
            no_network_fallback=True,
        )

    def initialize(self):
        self.index = {}  # link -> {title, author, html, pubdate}
        self._translator = None
        self._translator_failed = False
        self._translated_titles_cache = {}  # lang_code -> {content_id: translated_title}
        self._load_collection_aliases()
        self.refresh_index()
        self.add_event(COMMON_READING_SEARCH, self.handle_search)
        self.add_event(f"{COMMON_READING_FETCH_CONTENT}.{self.skill_id}", self.handle_fetch_content)
        self.add_event(COMMON_READING_PING, self.handle_ping)

    def _load_collection_aliases(self):
        """DECISION POINT #7 (see module docstring): since this provider
        translates and works on ANY device language, there's no fixed
        SUPPORTED_LANGUAGES set of locale/ folders to guarantee - so
        unlike decision point #6's SUPPORTED_LANGUAGES-gated pattern,
        this loads per-language aliases from
        locale/<lang>/collection.voc where we've bothered to translate
        them, and FALLS BACK to FALLBACK_COLLECTION_ALIASES (English)
        for any language we haven't. Always loading successfully (never
        leaving collection_hint matching completely broken) matters
        more here than it does for a SUPPORTED_LANGUAGES-gated provider,
        since THIS provider claims to serve every language, not just a
        known set."""
        aliases_raw = self.resources.load_vocabulary_file("collection")
        aliases = [phrase for line in aliases_raw for phrase in line]
        self._collection_aliases = aliases or FALLBACK_COLLECTION_ALIASES

    def _index_cache_filename(self):
        return "feed_index.json"

    def _read_index_cache(self):
        cache_file = self._index_cache_filename()
        if not self.file_system.exists(cache_file):
            return None
        try:
            with self.file_system.open(cache_file, "r") as f:
                return json.load(f)
        except (OSError, ValueError) as e:
            self.log.warning(f"could not read index cache: {e}")
            return None

    def _write_index_cache(self):
        cache_file = self._index_cache_filename()
        try:
            with self.file_system.open(cache_file, "w") as f:
                json.dump({"timestamp": time.time(), "index": self.index}, f)
        except OSError as e:
            self.log.warning(f"could not write index cache: {e}")

    def refresh_index(self, force=False):
        """This caching shape (disk cache with a TTL, fall back to a
        stale cache on fetch failure rather than ending up empty) is the
        same across every provider in this family - copy it as-is."""
        cached = self._read_index_cache()
        if not force and cached and (time.time() - cached.get("timestamp", 0)) < self.INDEX_CACHE_TTL:
            self.index = cached.get("index", {})
            self._translated_titles_cache.clear()
            return
        try:
            self.index = self.fetch_feed_index()
            self._write_index_cache()
            self._translated_titles_cache.clear()
        except ContentFetchError as e:
            self.log.error(f"Could not refresh index: {e}")
            if cached:
                self.log.warning("Falling back to previously cached (possibly stale) index")
                self.index = cached.get("index", {})
                self._translated_titles_cache.clear()

    def fetch_feed_index(self):
        """PATTERN A core: fetch + parse an RSS feed with stdlib
        xml.etree (no extra dependency needed for this part)."""
        try:
            r = requests.get(FEED_URL, timeout=10, headers=HTTP_HEADERS)
            r.raise_for_status()
        except requests.RequestException as e:
            raise ContentFetchError(f"failed to fetch {FEED_URL}: {e}") from e
        try:
            root = ET.fromstring(r.content)
        except ET.ParseError as e:
            raise ContentFetchError(f"failed to parse feed XML: {e}") from e

        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else []
        index = {}
        for item in items:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if not title or not link:
                continue
            index[link] = {
                "title": title,
                "author": (item.findtext(DC_CREATOR_TAG) or "").strip(),
                "html": item.findtext("description") or "",
                "pubdate": (item.findtext("pubDate") or "").strip(),
            }
        if not index:
            raise ContentFetchError("feed parsed but contained no usable items")
        return index

    @staticmethod
    def extract_paragraphs(html):
        """DECISION POINT #3 (see module docstring): not every HTML tag
        is worth reading aloud. This is a REAL example of that judgment
        call, found while building ovos-skill-ovosblog: stripping <code>
        entirely broke sentence grammar ('ovos-installer exists to...'
        lost its subject, which was wrapped in <code>). Full <pre> blocks
        (multi-line shell commands) genuinely aren't useful read aloud
        and are dropped; inline <code> is unwrapped and kept as text.

        Take the text with get_text() and no separator, then collapse the
        whitespace. get_text(" ", strip=True) puts a space at every tag
        boundary ("threshold ." after a <code>, "False ," after a <b> -
        451 of them in the OVOS blog's feed), and get_text(strip=True)
        glues the words on either side of a tag together ("energy.The
        roads") - see decision point #10."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("pre"):
            tag.decompose()
        for tag in soup.find_all("code"):
            tag.unwrap()
        paragraphs = []
        for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            text = " ".join(tag.get_text().split())
            if text:
                paragraphs.append(text)
        return paragraphs

    def _latest_link(self):
        from email.utils import parsedate_to_datetime
        best_link, best_date = None, None
        for link, entry in self.index.items():
            try:
                d = parsedate_to_datetime(entry["pubdate"])
            except (TypeError, ValueError):
                continue
            if best_date is None or d > best_date:
                best_date, best_link = d, link
        return best_link or (next(iter(self.index), None))

    # --- Translation: DECISION POINT #1 (see module docstring). ---
    # This provider's content (technical blog posts) is a reasonable
    # candidate for machine translation, WITH disclosure. If your source
    # is poetry, legal text, or anything where precise wording matters,
    # you may want to skip this whole section and just decline to
    # respond (return None / stay silent) for non-English devices instead.

    def _get_translator(self):
        if self._translator is None and not self._translator_failed:
            try:
                from ovos_plugin_manager.language import OVOSLangTranslationFactory
                self._translator = OVOSLangTranslationFactory.create()
            except Exception as e:
                self.log.warning(f"no language translation plugin available: {e}")
                self._translator_failed = True
        return self._translator

    def _get_translated_titles(self, lang):
        """Match against *translated* titles, not English ones - a
        non-English user speaks a phrase in their own language. Returns
        None (not English text!) if translation isn't possible - callers
        must treat that as 'we can't help in this language right now'."""
        target = lang.split("-")[0]
        if target == "en":
            return {link: entry["title"] for link, entry in self.index.items()}
        cached = self._translated_titles_cache.get(target)
        if cached is not None:
            return cached
        translator = self._get_translator()
        if translator is None:
            return None
        translated = {}
        try:
            for link, entry in self.index.items():
                translated[link] = translator.translate(entry["title"], target=target, source="en")
        except Exception as e:
            self.log.warning(f"failed to translate titles to '{target}': {e}")
            return None
        self._translated_titles_cache[target] = translated
        return translated

    def _maybe_translate_paragraphs(self, paragraphs, lang):
        target = lang.split("-")[0]
        if target == "en":
            return paragraphs, False
        translator = self._get_translator()
        if translator is None:
            return paragraphs, False
        try:
            translated = [translator.translate(p, target=target, source="en") for p in paragraphs]
            return translated, True
        except Exception as e:
            self.log.warning(f"translation failed, falling back to English: {e}")
            return paragraphs, False

    def _matches_collection_hint(self, hint):
        if not hint:
            return True
        _, score = match_one(hint.lower(), self._collection_aliases)
        return score >= COLLECTION_HINT_THRESHOLD

    def _matches_content_type(self, content_type):
        if not content_type:
            return True
        return content_type.lower() in CONTENT_TYPES


    @staticmethod
    def _request_lang(message):
        """The language a request was made in, or None when it does not
        say: the pipeline plugin's own 'lang' field first, then the
        language of the session the request was forwarded from (a
        HiveMind client's, on a hub). An older plugin sends neither."""
        lang = message.data.get("lang") or message.context.get("lang")
        if not lang and message.context.get("session"):
            lang = SessionManager.get(message).lang
        return lang or None

    def _serves(self, lang):
        """This provider translates, so it could answer in any language -
        but it only does for the languages this installation is
        configured for (the device's lang plus secondary_langs in
        mycroft.conf). A request in any other language would otherwise
        load a translation model and translate the whole catalogue of
        titles for a language nobody here speaks."""
        return primary_subtag(lang) in configured_languages(self.native_langs)

    def handle_search(self, message):
        if not self._serves(self._request_lang(message) or self.lang):
            return  # not a language this installation is configured for
        if not self.index:
            return
        collection_hint = message.data.get("collection_hint")
        if not self._matches_collection_hint(collection_hint):
            return
        content_type = message.data.get("content_type")
        if not self._matches_content_type(content_type):
            return

        titles = self._get_translated_titles(self.lang)
        if titles is None:
            return  # can't offer this language - see _get_translated_titles docstring

        phrase = (message.data.get("phrase") or "").strip()
        if phrase:
            # titles keep their case, spoken requests don't - compare both
            # lower case, or "boring installs" only scores ~0.9 against
            # "Boring Installs"
            by_lower = {t.lower(): l for l, t in titles.items()}
            match, confidence = match_one(phrase.lower(), list(by_lower))
            link = by_lower[match]
            title = titles[link]
        else:
            # DECISION POINT #9: no title asked for - "read me an article",
            # or (for a story provider) the pipeline's "tell me a story",
            # which searches with phrase=None. Offer something rather than
            # stay silent: here the latest post; a story provider offers a
            # random story. Fully confident only when the collection itself
            # was named; otherwise NO_TITLE_CONFIDENCE, which is read
            # without an "is it that one?" question but loses to a title
            # somebody actually named.
            link = self._latest_link()
            title = titles[link]
            confidence = 1.0 if collection_hint else NO_TITLE_CONFIDENCE

        self.bus.emit(message.reply(COMMON_READING_SEARCH_RESPONSE, {
            "skill_id": self.skill_id,
            "content_id": link,
            "title": title,
            "author": self.index[link].get("author") or "",
            "collection": COLLECTION_NAME,
            "source": SOURCE_NAME,
            "confidence": confidence,
            "machine_translated": self.lang.split("-")[0] != "en",
        }))

    def handle_fetch_content(self, message):
        content_id = message.data.get("content_id")
        entry = self.index.get(content_id)
        if not entry:
            self.bus.emit(message.reply(COMMON_READING_FETCH_CONTENT_RESPONSE, {"paragraphs": []}))
            return
        paragraphs = self.extract_paragraphs(entry["html"])
        paragraphs, _ = self._maybe_translate_paragraphs(paragraphs, self.lang)
        self.bus.emit(message.reply(COMMON_READING_FETCH_CONTENT_RESPONSE, {"paragraphs": paragraphs}))

    def handle_ping(self, message):
        """Cheap 'is anyone there?' reply - no index lookup, no
        translation. Only ever called by the pipeline plugin on its
        rare 0-candidates path, never on every search. REQUIRED for
        every real provider - copy this as-is; there's rarely a reason
        to customize it. If your provider uses the SUPPORTED_LANGUAGES
        load-time gate (decision point #4), register this handler only
        inside the 'language is supported' branch of initialize(),
        exactly like COMMON_READING_SEARCH - a provider that refused to
        load for the device's language should stay silent here too,
        not falsely claim to be present."""
        lang = self._request_lang(message)
        if lang and not self._serves(lang):
            return
        self.bus.emit(message.reply(COMMON_READING_PONG, {
            "skill_id": self.skill_id,
            "collection": COLLECTION_NAME,
        }))


class StaticPageScraper:
    """PATTERN B - reference only, NOT wired into this skill's bus
    handlers (that would duplicate ovos-skill-andersen-tales as a real
    content source). Copy these methods into your own provider class if
    your source is a plain website with no feed, not this file's
    RSS-based CommonReadingExample.

    This is the exact approach ovos-skill-andersen-tales uses against
    andersenstories.com: fetch an index page listing all items, then
    fetch each item's own page and parse it - here via schema.org
    'itemprop' attributes, which is what THIS particular site happens to
    use. Your source will have its own structure; inspect its HTML and
    adjust the selectors accordingly - there's no way to make this part
    fully generic across arbitrary websites (see module docstring,
    decision point #3)."""

    @staticmethod
    def get_soup(url):
        try:
            r = requests.get(url, timeout=10, headers=HTTP_HEADERS)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return BeautifulSoup(r.text, "html.parser")
        except requests.RequestException as e:
            raise ContentFetchError(f"failed to fetch {url}: {e}") from e

    @classmethod
    def get_index(cls, index_url=STATIC_INDEX_URL):
        """Fetch the list of all available items -> {title: item_url}.
        Here: a <ul class="list_link"> full of <a> tags. Your source's
        index page will look completely different - open it in a
        browser's dev tools and find its actual structure."""
        soup = cls.get_soup(index_url)
        lists = soup.find_all("ul", {"class": ["list_link"]})
        if not lists:
            raise ContentFetchError(f"index structure not found at {index_url}")
        return {link.text: link.get("href") for link in lists[0].find_all("a")}

    @classmethod
    def get_title(cls, item_url):
        """Here: a <h2 itemprop="name"> tag (schema.org markup this site
        happens to use). Find your source's equivalent."""
        soup = cls.get_soup(item_url)
        elements = soup.find_all("h2", {"itemprop": ["name"]})
        if not elements:
            raise ContentFetchError(f"title not found at {item_url}")
        return elements[0].text.strip()

    @classmethod
    def get_text(cls, item_url):
        """Here: a <div itemprop="text"> tag. Find your source's
        equivalent - it could be a <article>, a specific class name,
        anything."""
        soup = cls.get_soup(item_url)
        elements = soup.find_all("div", {"itemprop": ["text"]})
        if not elements:
            raise ContentFetchError(f"body text not found at {item_url}")
        return elements[0].text.strip()
