"""Zotero citations for the portfolio renderer.

The markdown cites by key, in the pandoc form:

    [@schon1983]                    (Schön, 1983)
    [@apa2020, p. 25]               (American Psychological Association, 2020, p. 25)
    [see @kolb1984; @gibbs1988]     (see Kolb, 1984; Gibbs, 1988)
    Schön's [-@schon1983]           Schön's (1983)
    @becker2015                     Becker et al. (2015)
    @schon1983 [p. 54]              Schön (1983, p. 54)

Keys come from the Zotero library: a CSL JSON export at ``Workings/references/zotero_library.json``
(each item's Extra field carries ``Citation Key: schon1983``). Until that export exists, the newest
``zotero_seed_*.json`` import file stands in, and the renderer says so.

Formatting is done by Zotero's own citeproc-js, APA 7 style and en-US locale, extracted from the
installed Zotero app and run under Node (``cite.js``), so the output matches Zotero's Word plugin.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import subprocess
import zipfile

OMNI = pathlib.Path("/Applications/Zotero.app/Contents/Resources/app/omni.ja")
CACHE = pathlib.Path.home() / "Library/Caches/bit-docx/zotero"
USER_STYLE = pathlib.Path.home() / "Zotero/styles/apa.csl"
CITE_JS = pathlib.Path(__file__).with_name("cite.js")
ENGINE_FILES = (("chrome/content/zotero/xpcom/citeproc.js", "citeproc.js"),
                ("chrome/content/zotero/locale/csl/locales-en-US.xml", "locales-en-US.xml"),
                ("styles/apa.csl", "apa.csl"))

KEY = r"\w(?:[\w-]*\w)?"
CITATION = re.compile(rf"(?P<cluster>\[(?P<body>[^\[\]]*?-?@{KEY}[^\[\]]*)\](?!\())"
                      rf"|(?P<narrative>(?<![\w@\[\]-])@(?P<nkey>{KEY})(?:\s\[(?P<nloc>[^\[\]]+)\])?)")
LOCATOR = re.compile(r"(pp?|paras?|chap|sec|fig|vol)\.\s*(\S.*)$")
LABELS = {"p": "page", "pp": "page", "para": "paragraph", "paras": "paragraph", "chap": "chapter",
          "sec": "section", "fig": "figure", "vol": "volume"}
SKIP_HEADINGS = {"table of contents", "contents", "table of figures", "list of figures",
                 "table of figures and tables", "list of figures and tables", "list of tables"}
EXTRA_VARIABLES = {"version", "number", "publisher", "publisher-place", "original-date", "event-title", "event-place",
                   "collection-title", "genre", "medium", "status", "edition", "available-date"}
DATE_VARIABLES = {"original-date", "available-date"}


def find_library(workings):
    """The Zotero export if present, else the newest seed file. Returns (path, is_seed)."""
    refs = pathlib.Path(workings) / "references"
    export = refs / "zotero_library.json"
    if export.exists():
        return export, False
    seeds = sorted(refs.glob("zotero_seed_*.json"))
    return (seeds[-1], True) if seeds else (None, False)


def load_library(path):
    """CSL JSON items keyed by citation key (``citation-key``, else "Citation Key:" in Extra).

    Extra lines of the form ``variable: value`` (``version: 2.0``, ``number: 57``) become CSL variables when
    the item lacks them, as Zotero desktop does on export; the Web API's CSL export leaves them in ``note``.
    """
    library = {}
    for item in json.loads(pathlib.Path(path).read_text(encoding="utf-8")):
        note = item.get("note", "")
        m = re.search(r"^Citation Key:\s*(\S+)", note, re.M)
        key = item.get("citation-key") or (m.group(1) if m else None) or str(item.get("id"))
        item = {**item, "id": key}
        for var, value in re.findall(r"^([a-z][a-z-]*):\s*(.+?)\s*$", note, re.M):
            if var in EXTRA_VARIABLES and var not in item:
                item[var] = ({"date-parts": [[int(p) for p in value.split("-")]]} if var in DATE_VARIABLES
                             else value)
        library[key] = item
    return library


def engine_files():
    """Paths to Zotero's citeproc-js, en-US locale and APA style, refreshed when Zotero updates."""
    if not OMNI.exists():
        return None
    CACHE.mkdir(parents=True, exist_ok=True)
    stamp = CACHE / ".omni_mtime"
    if not stamp.exists() or stamp.read_text() != str(OMNI.stat().st_mtime):
        with zipfile.ZipFile(OMNI) as z:
            for src, dst in ENGINE_FILES:
                (CACHE / dst).write_bytes(z.read(src))
        stamp.write_text(str(OMNI.stat().st_mtime))
    style = USER_STYLE if USER_STYLE.exists() else CACHE / "apa.csl"
    return {"citeproc": str(CACHE / "citeproc.js"), "locale": str(CACHE / "locales-en-US.xml"), "style": str(style)}


def parse_cluster(body):
    cites = []
    for part in body.split(";"):
        m = re.match(rf"\s*(.*?)(-?)@({KEY})(.*)$", part.strip(), re.S)
        if not m:
            return None
        prefix, suppress, key, rest = m.groups()
        cite = {"id": key}
        if prefix.strip():
            cite["prefix"] = prefix.strip() + " "
        if suppress:
            cite["suppress-author"] = True
        rest = rest.strip().lstrip(",").strip()
        if rest:
            if loc := LOCATOR.match(rest):
                cite["label"], cite["locator"] = LABELS[loc.group(1)], loc.group(2)
            else:
                cite["suffix"] = ", " + rest
        cites.append(cite)
    return cites


def to_markdown(fragment):
    """citeproc HTML to the renderer's inline markdown: italics, bold, live URLs."""
    text = re.sub(r"</?div[^>]*>", "", fragment)
    text = re.sub(r"<i>(.*?)</i>", r"*\1*", text, flags=re.S)
    text = re.sub(r"<b>(.*?)</b>", r"**\1**", text, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
    return re.sub(r"(?<!\()(https?://[^\s<>]+?)(?=[.,;]?(?:\s|$))", r"[\1](\1)", text)


def _walk(items, visit):
    """Apply visit(text, section_anchor) to every rendered text in document order."""
    out, skip, section = [], None, None
    for kind, payload in items:
        if kind == "heading":
            if skip is not None and payload[0] <= skip:
                skip = None
            if payload[1].lower().strip() in SKIP_HEADINGS:
                skip = payload[0]
            if payload[0] == 1:
                section = payload[2]
        if skip is None:
            if kind in ("para", "bullet", "numbered", "quote"):
                payload = visit(payload, section)
            elif kind == "heading":
                payload = (payload[0], visit(payload[1], section), payload[2])
            elif kind == "table":
                payload = [visit(row, section) for row in payload]
        out.append((kind, payload))
    return out


def apply(items, library, log):
    """Format every citation; returns (items, bibliography, cited_by_section) or None if unavailable.

    bibliography: [(ids, markdown)] in APA order; cited_by_section: H1 anchor -> set of keys.
    """
    files = engine_files()
    if files is None:
        log("citations left as keys: Zotero.app not found (its citation engine is used for formatting)")
        return None
    clusters, cited_by_section = [], {}

    def collect(text, section):
        for m in CITATION.finditer(text):
            if m.group("cluster"):
                cites = parse_cluster(m.group("body"))
                if cites is None:
                    continue
                clusters.append(cites)
            else:
                cite = {"id": m.group("nkey")}
                if m.group("nloc") and (loc := LOCATOR.match(m.group("nloc").strip())):
                    cite["label"], cite["locator"] = LABELS[loc.group(1)], loc.group(2)
                clusters.append([{"id": cite["id"], "author-only": True}])
                clusters.append([{**cite, "suppress-author": True}])
            for c in clusters[-1]:
                cited_by_section.setdefault(section, set()).add(c["id"])
        return text

    _walk(items, collect)
    if not clusters:
        return None
    result = subprocess.run(["node", str(CITE_JS)], capture_output=True, text=True,
                            input=json.dumps({**files, "items": list(library.values()), "clusters": clusters}))
    if result.returncode:
        log("citations left as keys: citation engine failed: " + result.stderr.strip()[-300:])
        return None
    out = json.loads(result.stdout)
    for err in dict.fromkeys(out["errors"]):
        log(err)
    formatted = iter(out["clusters"])

    def substitute(text, section):
        def repl(m):
            if m.group("cluster"):
                if parse_cluster(m.group("body")) is None:
                    return m.group(0)
                html_ = next(formatted)
                return to_markdown(html_) if html_ else m.group(0)
            author, year = next(formatted), next(formatted)
            return f"{to_markdown(author)} {to_markdown(year)}" if author and year else m.group(0)
        return CITATION.sub(repl, text)

    items = _walk(items, substitute)
    bibliography = [(entry["ids"], to_markdown(entry["html"])) for entry in out["bibliography"]]
    log(f"citations: {len(clusters)} formatted, {len(bibliography)} sources cited")
    return items, bibliography, cited_by_section
