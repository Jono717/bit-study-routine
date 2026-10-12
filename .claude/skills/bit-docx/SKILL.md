---
name: bit-docx
description: Render the BIT Portfolio of Evidence (a markdown draft such as Workings/Portfolio_of_Evidence.md) to a properly formatted Word .docx and audit the result: A4, Times New Roman 12, double spacing, first-line indents, APA 7 headings, page numbers, real Word table-of-contents and table-of-figures fields, APA figure captions renumbered across the whole portfolio, APA tables, hanging-indent references generated from Zotero, alt text, no leaked markdown. Use when the user asks to render, build, export, regenerate or format the portfolio as Word or docx, says the portfolio docx "looks bad", asks to fix formatting, prepare a submission copy, or check the docx against APA 7. For editing an existing Word document by hand or with tracked changes, use a docx editing skill instead.
argument-hint: "optional: 'review' for a reading copy, 'submission' for a final copy, or 'check FILE.docx'"
---

# BIT portfolio to Word

The learner writes in markdown; this skill turns it into the document the facilitator and assessors read.
It owns formatting only. It never edits the markdown's prose.

## Requirements

- `uv` (runs Python with `python-docx` and `pillow` on demand).
- For citations: the Zotero desktop app installed at `/Applications/Zotero.app` (macOS) and Node.js. The
  renderer extracts Zotero's own citeproc-js engine, APA 7 style and locale from the app, so the output
  matches Zotero's Word plugin.
- Optional: a Zotero Web API key for `zotero_sync.py` (see that script's header).

## Files

| File | Purpose |
|---|---|
| `scripts/render_portfolio.py` | markdown to .docx (submission layout by default; `--review` for a reading copy) |
| `scripts/check_docx.py` | audits any .docx against the spec; PASS / WARN / FAIL per check |
| `scripts/citations.py`, `scripts/cite.js` | formats `[@key]` citations and the reference lists with Zotero's citeproc-js and APA 7 style |
| `scripts/zotero_sync.py` | Zotero Web API: `push` sources into a collection (default `BIT`), `pull` it to `Workings/references/zotero_library.json` |
| `references/format-spec.md` | the spec: what the document must look like and who owns each part |

## Rules

1. **Never overwrite a .docx Word last saved.** The learner may have edited it in Word. Two signals: a
   `~$` lock file beside it means it is open in Word now, and `check_docx.py` prints a Provenance row
   (Word adds `w14:paraId` to every paragraph and replaces `lastModifiedBy` on save; renders carry
   `lastModifiedBy = bit-docx render_portfolio.py`). `Application` in `docProps/app.xml` proves nothing:
   python-docx's template says "Microsoft Macintosh Word". Default output is a new dated file such as
   `Workings/Portfolio_of_Evidence_APA_YYYY-MM-DD.docx` (add `_v2` if that one exists). Overwrite only on
   explicit instruction.
2. **Follow the workspace rules in the bit-standards skill.** Write only in the drafts folder; never into
   the submission folder unless the learner asks for that specific copy.
3. **Prose is the learner's; assembly leftovers are not.** Prose problems the checker reports
   (single-sentence paragraphs, placeholders, missing callouts, length) go back to the learner, or to
   bit-review and bit-prose. Mechanical leftovers may be cleaned, only if the learner agrees:
   - running headers, a duplicate level-1 heading per task, and per-task bylines;
   - drafting notes, TODOs and "[verify …]" tags, moved into `<!-- -->` comments, never deleted;
   - cross-references whose target the text names;
   - "Table N" captions whose titles come from the heading above the table.

   Back up the markdown first (for example `Workings/archive/Portfolio_of_Evidence_YYYY-MM-DD_pre-cleanup.md`)
   and list every change in the reply. Cover facts (student ID, signature), the declaration's tool list and
   `[NEEDS YOUR INPUT]` gaps stay with the learner.
4. **References live in Zotero.** Do not type reference entries into the markdown: add the source to the
   Zotero collection (`zotero_sync.py push`, or Zotero's File > Import) with `Citation Key: <key>` in Extra,
   and cite it as `[@key]`. Every "References" section is generated from what is cited.
5. Always run Python through `uv run`. Do not automate Microsoft Word through AppleScript: Word's sandbox
   blocks `/tmp`, raises file-access dialogs and times out. For a visual check, the learner opens the file.

## Workflow

### 1. Render

From `Workings/` (image paths in the markdown are relative to it):

```bash
uv run --with python-docx --with pillow python ../.claude/skills/bit-docx/scripts/render_portfolio.py \
  Portfolio_of_Evidence.md Portfolio_of_Evidence_APA_$(date +%F).docx
```

Options: `--review` (Calibri, 1.15, landscape reading copy), `--submission` (refuses while any
placeholder remains), `--letter` (US Letter instead of A4), `--toc-levels 1-3`, `--no-renumber`,
`--no-footer-link`, `--no-auto-landscape`, `--no-citations`.

The renderer reports on stderr what it did structurally: running-header lines dropped, the figure
renumbering map per task (for example `LT3: 1->3, 2->4, 3->5`), any unresolved figure references, tables
moved to landscape pages, and the placeholders it highlighted. Pass the renumbering map to the learner:
the rendered document's figure numbers differ from the markdown's per-task numbers by design (one sequence
across the portfolio, in order of first mention).

### 1a. References come from Zotero

Before rendering, refresh the library export when the Zotero collection has changed:

```bash
uv run python ../.claude/skills/bit-docx/scripts/zotero_sync.py pull     # writes references/zotero_library.json
```

The renderer reads `references/zotero_library.json`; until it exists it uses the newest
`references/zotero_seed_*.json` and says so on stderr. Without the Web API, the learner exports the
collection from Zotero as CSL JSON to the same path. The renderer logs `unknown citation key: …` for any
key the library lacks; the checker FAILs any `[@key]` left unformatted. The Web API's CSL export leaves
Extra lines such as `version: 2.0` or `number: 57` in `note`; the renderer applies them as CSL variables,
as Zotero desktop would.

New source: add it in Zotero with `Citation Key: key` in Extra, or write it as CSL JSON with
`"note": "Citation Key: key"` and `push` it.

### 2. Check

```bash
uv run --with python-docx --with pillow python ../.claude/skills/bit-docx/scripts/check_docx.py Portfolio_of_Evidence_APA_YYYY-MM-DD.docx [--submission]
```

Expect 0 FAIL. WARN rows are usually content: name each and who fixes it. Pillow lets the table checks
measure text with the real font; without it they estimate.

### 3. Report

Tell the learner: the output path, the check summary (pass, warn, fail), the renumbering map, the content
warnings to fix in the markdown, and that Word will ask to update fields on first open (answer Yes; this
fills the contents, table of figures and page numbers). For a submission copy, rerun with `--submission`
once placeholders are gone.

## Markdown conventions the renderer understands

- YAML front matter: `title`, `author` become document properties; it is not printed.
- The first `#` heading is the cover title; the lines under it, up to the next heading, become centred cover
  lines, one per source line. Put name, student ID, programme, institution, facilitator and date there.
- A section headed "Table of Contents" or "Contents" is replaced by a Word TOC field; one headed "Table of
  Figures" or "List of Figures" by a figure-list field. Whatever is written under them is ignored.
- `{#anchor}` after a heading sets its bookmark; `[text](#anchor)` becomes an internal link (a "Back to
  Contents" line works); external links become hyperlinks.
- Figure block: `**Figure N**`, then an italic title line, then the image, then `*Note.* …`.
- Figure references are rewritten to the portfolio-wide numbers. Inside a task, "Figure 2" means that
  task's Figure 2. From another task, write "LT3 Figure 2", or name the task earlier in the same sentence
  or table cell; ranges such as "Figures 1 to 3" work too. A reference the renderer cannot place is logged
  as "unresolved reference": relay it to the learner, because it may now point at the wrong figure.
- Tables: `|` pipe tables. Two-column `| Column | Content |` tables are flattened into headed paragraphs.
  Column widths come from the text, measured in the real font: no column narrower than its longest word,
  single-line columns sized to fit and centred, wrapping columns sharing the rest by text volume. Tables
  with the same header row share one set of widths. Rows that wrap get hairline grey rules between them;
  short rows never split across a page.
- Landscape pages: `<!-- landscape -->` … `<!-- /landscape -->`. Without markers, any table with a row
  taller than 2.5 inches on a portrait page moves to landscape automatically, with the headings that lead
  into it, and back-to-back tall tables share one landscape run.
- Placeholders `[NEEDS YOUR INPUT …]`, `[TODO …]`, `[to confirm]`, `[To be completed …]` are highlighted.
- Citations (pandoc form): `[@schon1983]`, `[@apa2020, p. 25]`, `[see @kolb1984; @gibbs1988]`,
  `@becker2015` (narrative), and the learner's own author wording plus `[-@key]` for the year
  ("Schön's [-@schon1983]" gives "Schön's (1983)"). In-text forms, "et al.", `2025a`/`2025b` and `n.d.-a`
  suffixes follow APA 7 automatically.
- References: the level-1 "References" heading gets the consolidated list of everything cited; a task's
  level-2 "References" heading gets that task's list (left out with `--submission`). Anything typed under
  them is skipped, except a line holding a `[NEEDS YOUR INPUT …]` gap. Entries get a 0.5 inch hanging indent
  and live links. With `--no-citations`, typed entries render as written.

## Known limits

- Captions under an `Appendix X` heading are numbered X1, X2 (APA 7: Figure A1) outside the main
  sequence, so the figure list reads in page order.
- APA level 4 and 5 headings are rendered as their own paragraphs, not run into the text.
- Table numbering and captions follow the figure pattern (`**Table N**`, italic title line, then the
  table). Captioned tables get their own style and a List of Tables field under a "Table of Figures and
  Tables" heading; uncaptioned tables are not listed.
- Page count is only known after Word lays the document out; `docProps/app.xml` page counts are stale.
