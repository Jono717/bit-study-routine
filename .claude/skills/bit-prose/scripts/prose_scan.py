#!/usr/bin/env python3
"""Mechanical writing scan for BIT portfolio Markdown.

Flags common writing patterns that cost a reader (vague openers, agentless passives, empty importance
claims, single-sentence paragraphs and more), with line numbers, so a reviewer can confirm each one by
reading the line. It does not judge quality; it finds candidates.

Usage (from the workspace root):
    uv run python .claude/skills/bit-prose/scripts/prose_scan.py FILE [--start N] [--end N] [--json]
        [--figures-dir Workings/Media]

Lines are 1-based and inclusive. Without --start/--end the whole file is scanned. Acronym first use and
expansion are judged across the whole file; everything else within the range.

What counts where:
- Words and page estimate: prose, lists and table text in the range, excluding headings, HTML comments,
  placeholders ([NEEDS YOUR INPUT ...], [TODO ...], "to insert"), the References section and appendices.
- Style checks: every line in the range except HTML comments and placeholders, including appendices,
  blockquotes and table cells.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import OrderedDict

WORDS_PER_PAGE = 275  # APA 7, 12 pt, double spaced, approximate
PAGES_PER_FIGURE = 0.5

UPPER = "A-ZÀ-ÖØ-ÞĀĂĄĆĈĊČĎĐĒĔĖĘĚĜĞĠĢĤĦĨĪĬĮİĴĶĹĻĽĿŁŃŅŇŌŎŐŒŔŖŘŚŜŞŠŢŤŦŨŪŬŮŰŲŴŶŸŹŻŽ"
NAME = rf"[{UPPER}][\w'’-]+"

EMPTY_IMPORTANCE = [
    r"\bthis matters\b",
    r"\bthis is (very |really |extremely )?important\b",
    r"\bit is important to (note|remember|recognise|recognize)\b",
    r"\bit is worth noting\b",
    r"\bplays? a (crucial|vital|key|pivotal) role\b",
    r"\bcommunication improved\b",
    r"\bchanges were made\b",
    r"\b(the )?feedback was (useful|helpful|valuable)\b",
    r"\bvaluable lessons were\b",
    r"\blessons were learn(ed|t)\b",
    r"\bneedless to say\b",
    r"\bthe outcome was better\b",
]

AGENTLESS_PASSIVE = re.compile(
    r"\b(was|were|has been|have been|had been)\s+(\w+ly\s+)?"
    r"(raised|made|decided|agreed|identified|implemented|completed|taken|given|reported|noted|"
    r"chosen|selected|approved|introduced|established|deployed|discussed|addressed|resolved|"
    r"highlighted|recognised|recognized|considered|reviewed|found|felt)\b"
    r"(?![^.]{0,60}\bby\b)",
    re.IGNORECASE,
)

VOICE_MARKERS = [
    r"\bdelve[sd]?\b",
    r"\btapestry\b",
    r"\b(a |is a )?testament to\b",
    r"\bmultifaceted\b",
    r"\bever-evolving\b",
    r"\bin today's\b",
    r"\bnavigat(e|ing) the complexit",
    r"\ba myriad of\b",
    r"\bunderscores?\b",
    r"\bnot (just|only|simply)\b[^.]{1,80}?[,;:—–]\s*(but|it|they|this)\b",
    r"\b(is|was|are|were|does|did)n['’]?t (just|only|simply)\b[^.]{1,80}?[,;:—–]\s*(it|they|this|but)\b",
    r"\bat the end of the day\b",
]

# Bare "This" followed by a verb or auxiliary (name the referent instead). "This task", "This decision"
# already name it and are not flagged.
THIS_BARE = re.compile(
    r"^[\"“(]?This\s+(is|was|are|were|has|had|have|will|would|can|could|should|may|might|must|meant|means|"
    r"made|makes|led|leads|gave|gives|shows|showed|shaped|matters|mattered|became|becomes|felt|feels|"
    r"seemed|seems|helped|helps|allowed|allows|required|requires|left|took|takes|set|sets|put|puts|"
    r"[a-z]+ed)\b|^[\"“(]?This[,.;:]"
)

ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]{1,6}s?\b")
ACRONYM_IGNORE = {
    "I", "A", "LT", "GPO", "GPOS", "BIT", "IT", "APA", "NZ", "US", "UK", "OK", "VESCAS", "SFIA", "PDF", "AI",
    "II", "III", "IV", "TP", "PE", "TODO", "STRONG", "PARTIAL", "MEDIUM", "HIGH", "LOW", "NOTE", "NB",
    "NEEDS", "INPUT", "YOUR", "WEAK", "GAP", "DRAFT", "NA", "TBD", "CEO", "CTO", "CIO",
}

CITATION_PAREN = re.compile(rf"\([^()]*?{NAME}[^()]*?,\s*((19|20)\d{{2}}[a-z]?|n\.d\.)[^()]*\)")
CITATION_NARR = re.compile(
    rf"\b{NAME}( et al\.| and {NAME}| & {NAME})?\s\(((19|20)\d{{2}}[a-z]?|n\.d\.)(, p+\. ?\d+[-–]?\d*)?\)"
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])[\"”’)]*\s+(?=[\"“(]?[A-Z0-9])")
EXCLUDE_SECTION = re.compile(r"^#+\s*(appendix|appendices|document information)", re.IGNORECASE)
REFERENCE_SECTION = re.compile(r"^#+\s*references?\b", re.IGNORECASE)
PLACEHOLDER = re.compile(
    r"\[[^\]]*(NEEDS YOUR INPUT|TODO|to insert|placeholder|TBD)[^\]]*\]|NEEDS YOUR INPUT|^\s*TODO\b.*$",
    re.IGNORECASE,
)
LABEL_LINE = re.compile(r"^\s*\*\*[^*]{1,60}[:.]\*\*")

SPELLING_PAIRS = [
    ("organisation", "organization"), ("recognise", "recognize"), ("prioritise", "prioritize"),
    ("optimise", "optimize"), ("standardise", "standardize"), ("minimise", "minimize"),
    ("analyse", "analyze"), ("behaviour", "behavior"), ("colour", "color"), ("centre", "center"),
    ("judgement", "judgment"), ("modelling", "modeling"), ("labour", "labor"),
    ("licence", "license"), ("defence", "defense"), ("favour", "favor"),
    ("learnt", "learned"), ("travelled", "traveled"),
]


def strip_md(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\{#[^}]*\}", " ", text)
    text = re.sub(r"[*_`>#|]", " ", text)
    return text


def word_count(text: str) -> int:
    return len(re.findall(r"[^\W_][\w'’-]*", strip_md(text)))


def heading_level(line: str) -> int:
    m = re.match(r"^(#+)\s", line)
    return len(m.group(1)) if m else 0


def is_caption_or_header(line: str) -> bool:
    s = line.strip().strip("*_ ")
    if re.match(r"^(Figure|Table)\s+\d+", s) or s.lower().startswith("note."):
        return True
    t = line.strip()
    return t.startswith(("*", "_")) and t.endswith(("*", "_")) and len(s.split()) < 16 and not LABEL_LINE.match(t)


def remove_comments(lines: list[str]) -> list[str]:
    """Blank out HTML comments, including multi-line ones, keeping line numbering."""
    out, in_comment = [], False
    for line in lines:
        buf, i = "", 0
        while i < len(line):
            if in_comment:
                j = line.find("-->", i)
                if j < 0:
                    i = len(line)
                else:
                    in_comment, i = False, j + 3
            else:
                j = line.find("<!--", i)
                if j < 0:
                    buf += line[i:]
                    i = len(line)
                else:
                    buf += line[i:j]
                    in_comment, i = True, j + 4
        out.append(buf)
    return out


def text_units(line: str) -> list[str]:
    """Prose-bearing text in a line: table cells, list item text, blockquote text, or the line."""
    s = line.strip()
    if s.startswith("|"):
        if re.match(r"^\|[\s:|-]+\|?$", s):
            return []
        return [c.strip() for c in s.strip("|").split("|") if c.strip()]
    s = re.sub(r"^>+\s?", "", s)
    s = re.sub(r"^([-*+]|\d+[.)])\s+", "", s)
    return [s] if s else []


def acronym_index(lines: list[str]) -> dict:
    index: dict = {}
    full = "\n".join(lines)
    for idx, line in enumerate(lines, 1):
        if heading_level(line):
            continue
        plain = strip_md(PLACEHOLDER.sub(" ", line))
        caps_runs = {m.group(0) for m in re.finditer(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})+\b", plain)}
        run_words = {w for run in caps_runs for w in run.split()}
        for tok in ACRONYM.findall(plain):
            base = tok[:-1] if tok.endswith("s") and tok[:-1].isupper() else tok
            if base in ACRONYM_IGNORE or base in run_words or re.fullmatch(r"LT\d|[A-Z]\d+", base) or base.isdigit():
                continue
            if base not in index:
                expanded = bool(
                    re.search(r"\(" + re.escape(base) + r"s?\)", full)
                    or re.search(r"\b" + re.escape(base) + r"s?\s*\((?!\d)[A-Za-z][a-z]", full)
                )
                index[base] = {"first_line": idx, "expanded_in_document": expanded, "lines": []}
            index[base]["lines"].append(idx)
    return index


def scan(raw_lines: list[str], start: int, end: int, figures_dir: str | None = None) -> dict:
    lines = remove_comments(raw_lines)
    flags: "OrderedDict[str, list]" = OrderedDict(
        (k, [])
        for k in [
            "this_opener_bare",
            "empty_importance",
            "agentless_passive",
            "single_sentence_paragraph",
            "long_sentence",
            "em_dash",
            "spaced_en_dash_pause",
            "vestas_naming",
            "voice_marker",
            "placeholder",
        ]
    )
    body_words = reference_words = appendix_words = table_words = 0
    em_dash_chars = 0
    figures_body, figures_appendix, images = set(), set(), 0
    citations = 0
    spelling = {uk: [0, 0] for uk, _ in SPELLING_PAIRS}

    excluded_level = reference_level = 0
    in_code = False
    para: list[tuple[int, str]] = []

    def flush_para():
        if not para:
            return
        text = " ".join(t.strip() for _, t in para)
        first = para[0][1]
        sentences = [s for s in SENTENCE_SPLIT.split(strip_md(text)) if word_count(s) > 0]
        if (
            len(sentences) == 1
            and word_count(text) >= 4
            and not is_caption_or_header(first)
            and not LABEL_LINE.match(first)
            and not text.rstrip().endswith(":")
            and not re.match(r"^\s*\*\*[^*]+\*\*\s*[^.]{0,80}$", text)  # bylines, bold one-liners
        ):
            flags["single_sentence_paragraph"].append({"line": para[0][0], "text": text[:120]})
        para.clear()

    for idx in range(start, end + 1):
        raw = raw_lines[idx - 1]
        line = lines[idx - 1]
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            flush_para()
            continue
        if in_code:
            continue

        for m in PLACEHOLDER.finditer(line):
            flags["placeholder"].append({"line": idx, "text": m.group(0)[:100]})
        line = PLACEHOLDER.sub(" ", line)
        stripped = line.strip()

        level = heading_level(line)
        if level:
            flush_para()
            if excluded_level and level <= excluded_level:
                excluded_level = 0
            if reference_level and level <= reference_level:
                reference_level = 0
            if EXCLUDE_SECTION.match(line):
                excluded_level = level
            elif REFERENCE_SECTION.match(line):
                reference_level = level

        # Checks that apply to every line, appendices and headings included.
        n_em = raw.count("—") if "<!--" not in raw else line.count("—")
        if n_em:
            em_dash_chars += n_em
            kind = "heading" if level else ("header/caption" if is_caption_or_header(line) else "prose")
            flags["em_dash"].append({"line": idx, "count": n_em, "kind": kind, "text": stripped[:110]})
        for m in re.finditer(r"[A-Za-z)\"”’] – [A-Za-z(\"“]", line):
            flags["spaced_en_dash_pause"].append({"line": idx, "text": stripped[max(0, m.start() - 40): m.end() + 40]})
        if re.search(r"\bVESTAS\b", line):
            flags["vestas_naming"].append({"line": idx, "text": stripped[:110]})
        for m in re.finditer(r"\b(Figure)\s+(\d+)\b", line):
            if is_caption_or_header(line):
                (figures_appendix if excluded_level else figures_body).add(m.group(2))
        if "![" in line and not excluded_level:
            images += 1

        if level:
            continue

        wc = sum(word_count(u) for u in text_units(line))
        if stripped.startswith("|") and not excluded_level and not reference_level:
            table_words += wc
        if excluded_level:
            appendix_words += wc
        elif reference_level:
            reference_words += wc
            continue
        else:
            body_words += wc
            citations += len(CITATION_PAREN.findall(line)) + len(CITATION_NARR.findall(line))

        low = line.lower()
        for uk, us in SPELLING_PAIRS:
            spelling[uk][0] += len(re.findall(rf"\b{uk}\w*", low))
            spelling[uk][1] += len(re.findall(rf"\b{us}\w*", low))

        is_prose_para = stripped and not (
            stripped.startswith(("|", "![", "<", "---", ">")) or re.match(r"^([-*+]|\d+[.)])\s", stripped)
        )
        if is_prose_para:
            para.append((idx, line))
        else:
            flush_para()

        if is_caption_or_header(line):
            continue
        for unit in text_units(line):
            plain = strip_md(unit)
            for sent in SENTENCE_SPLIT.split(plain):
                s = sent.strip()
                if THIS_BARE.match(s):
                    flags["this_opener_bare"].append({"line": idx, "text": s[:90]})
                if word_count(s) > 40:
                    flags["long_sentence"].append({"line": idx, "words": word_count(s), "text": s[:90]})
            for pat in EMPTY_IMPORTANCE:
                for m in re.finditer(pat, plain, re.IGNORECASE):
                    flags["empty_importance"].append({"line": idx, "match": m.group(0)})
            for m in AGENTLESS_PASSIVE.finditer(plain):
                flags["agentless_passive"].append({"line": idx, "match": m.group(0)})
            for pat in VOICE_MARKERS:
                for m in re.finditer(pat, plain, re.IGNORECASE):
                    flags["voice_marker"].append({"line": idx, "match": m.group(0)[:80]})
    flush_para()

    acr = acronym_index(lines)
    candidates = [
        {"acronym": k, "first_line_in_document": v["first_line"], "uses_in_range": sum(start <= l <= end for l in v["lines"])}
        for k, v in acr.items()
        if not v["expanded_in_document"] and any(start <= l <= end for l in v["lines"])
    ]

    figure_svgs = []
    if figures_dir and os.path.isdir(figures_dir):
        for path in sorted(glob.glob(os.path.join(figures_dir, "*.svg"))):
            with open(path, encoding="utf-8", errors="ignore") as fh:
                n = fh.read().count("—")
            if n:
                figure_svgs.append({"file": os.path.basename(path), "em_dashes": n})

    figure_count = max(len(figures_body), images)
    mixed = {f"{uk}/{us}": c for (uk, us), c in zip(SPELLING_PAIRS, spelling.values()) if c[0] and c[1]}
    return {
        "range": [start, end],
        "words_body": body_words,
        "words_body_in_tables": table_words,
        "words_references": reference_words,
        "words_appendices": appendix_words,
        "figures_body": figure_count,
        "figures_appendices": len(figures_appendix),
        "citations_in_body": citations,
        "est_pages_body": round(body_words / WORDS_PER_PAGE + figure_count * PAGES_PER_FIGURE, 1),
        "est_pages_incl_references": round((body_words + reference_words) / WORDS_PER_PAGE + figure_count * PAGES_PER_FIGURE, 1),
        "page_assumption": (
            f"{WORDS_PER_PAGE} words per APA double-spaced page + {PAGES_PER_FIGURE} page per body figure; "
            "headings, comments, placeholders and appendices excluded; table text counted as prose"
        ),
        "em_dash_characters": em_dash_chars,
        "counts": {k: len(v) for k, v in flags.items()},
        "flags": flags,
        "spelling_mixed_uk_us": mixed,
        "acronyms_never_expanded_in_document": candidates,
        "figure_sources_with_em_dashes": figure_svgs,
    }


def print_text(r: dict) -> None:
    print(f"Lines {r['range'][0]}-{r['range'][1]}")
    print(f"Words: body {r['words_body']} (of which tables {r['words_body_in_tables']}), references {r['words_references']}, appendices {r['words_appendices']}")
    print(
        f"Figures: body {r['figures_body']}, appendices {r['figures_appendices']}  Citations in body: "
        f"{r['citations_in_body']}  Est. pages: {r['est_pages_body']} body, {r['est_pages_incl_references']} incl. refs"
    )
    print(f"({r['page_assumption']})")
    print(f"Em dash characters: {r['em_dash_characters']} on {r['counts']['em_dash']} lines\n")
    for key, items in r["flags"].items():
        print(f"## {key} ({len(items)})")
        for it in items[:60]:
            detail = it.get("text") or it.get("match") or ""
            extra = f" [{it['words']} words]" if "words" in it else ""
            extra += f" [{it['kind']}, {it['count']}]" if "kind" in it else ""
            print(f"  L{it['line']}{extra}: {detail}")
        if len(items) > 60:
            print(f"  ... {len(items) - 60} more")
        print()
    if r["spelling_mixed_uk_us"]:
        print("## spelling mixed UK/US (uk count, us count)")
        for k, v in r["spelling_mixed_uk_us"].items():
            print(f"  {k}: {v[0]} / {v[1]}")
        print()
    acr = r["acronyms_never_expanded_in_document"]
    print(f"## acronyms never expanded anywhere in the document ({len(acr)}): glossary candidates")
    for a in acr[:80]:
        print(f"  {a['acronym']}: first use L{a['first_line_in_document']}, {a['uses_in_range']} uses in range")
    if r["figure_sources_with_em_dashes"]:
        print("\n## figure SVG sources containing em dashes")
        for f in r["figure_sources_with_em_dashes"]:
            print(f"  {f['file']}: {f['em_dashes']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--figures-dir", help="also count em dashes in *.svg figure sources in this folder")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    end = args.end or len(lines)
    if not (1 <= args.start <= end <= len(lines)):
        print(f"invalid range {args.start}-{end} for {len(lines)} lines", file=sys.stderr)
        return 2
    result = scan(lines, args.start, end, args.figures_dir)
    if args.json:
        json.dump(result, sys.stdout, indent=1, ensure_ascii=False)
        print()
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
