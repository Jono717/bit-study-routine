# Portfolio .docx format spec

What the rendered Portfolio of Evidence looks like, and who is responsible for each part: the renderer
(`scripts/render_portfolio.py`) or the learner (in the markdown). `scripts/check_docx.py` tests every row
marked "checked".

Basis: APA 7 student-paper conventions. Where your Learner Guide or facilitator asks for something
different (paper size, front matter, appendix order), their requirement wins; record it in
`bit-standards/references/lt8.md` and adjust the render options.

## Page and type

| Requirement | Value | Who | Checked |
|---|---|---|---|
| Paper | A4. `--letter` for US Letter | renderer | yes |
| Margins | 2.54 cm (1 inch) all sides | renderer | yes |
| Font | Times New Roman 12 everywhere, including headings; no theme fonts | renderer | yes |
| Spacing | double, no extra space before or after paragraphs | renderer | yes |
| Body paragraphs | 0.5 inch first-line indent, left aligned (ragged right) | renderer | yes |
| Language | en-NZ (spell-check NZ spelling) | renderer | no |
| Page number | top right, every page (APA student paper) | renderer | yes |
| Footer | "Back to Contents" link (`--no-footer-link` to remove) | renderer | no |

## Headings (APA 7)

| Level | Format | Markdown |
|---|---|---|
| 1 | centred, bold, title case; new page | `#` |
| 2 | flush left, bold, title case | `##` |
| 3 | flush left, bold italic, title case | `###` |
| 4 | indented 0.5 inch, bold | `####` |
| 5 | indented 0.5 inch, bold italic | `#####` |

All black, same size as body text. One level-1 heading per task; the checker warns if a task carries a
second one.

## Front matter

| Item | Requirement | Who |
|---|---|---|
| Cover page | the fields your guide asks for (typically full name, student ID, programme, institution, facilitator, date or version). Centred, own page | learner writes the lines under the first `#` title; renderer lays out the page |
| Declaration of authorship and use of tools | as your guide requires; name each tool and what it was used for | learner |
| Table of contents | auto-updating Word field built from heading styles | renderer replaces the "Table of Contents" section with a TOC field (levels `--toc-levels`, default 1-2) |
| Table of figures | built from captions; a separate list of tables when tables are captioned | renderer replaces the "Table of Figures (and Tables)" section with a field over each caption style |
| Glossary | when the work carries many acronyms or workplace terms | learner (bit-prose lists candidates) |

Word asks to update fields when the file opens; answer Yes, or right-click a table and choose Update Field.

## Figures (APA 7)

Markdown pattern the renderer recognises:

```markdown
**Figure 2**

*Career Timeline*

![Career timeline diagram](Media/LT2_Fig1_Career_Timeline.png)

*Note.* Own work, created in draw.io.
```

| Requirement | Who | Checked |
|---|---|---|
| Number bold above the image, title in italic title case on the next line, kept with the image | renderer | yes |
| Numbered consecutively across the whole portfolio, in order of first mention | renderer renumbers at render time (per-task numbers stay in the markdown) and rewrites callouts; unresolved references are logged | yes |
| Every figure called out in the text ("see Figure 2") | learner | no |
| `*Note.*` line: explanation and source; own work, adapted, workplace-supplied or AI-generated, said plainly | learner | no |
| Alt text | renderer uses the markdown alt text; learner writes meaningful alt text | yes |
| Size | fits the text width, at most 4.6 inches tall | renderer | no |

## Tables (APA 7)

| Requirement | Who | Checked |
|---|---|---|
| Rules above and below the table and under the header row; no vertical lines | renderer | yes |
| Hairline grey rule between body rows when rows wrap | renderer | no |
| Cell text single-spaced, 10 pt, header row bold and repeated on each page | renderer | yes |
| No column narrower than its longest word; short code and number columns centred | renderer (measures with the font file) | yes |
| Grid, table width and cell widths agree; table within the margins | renderer | yes |
| Tables with the same header share column widths | renderer | no |
| Short rows not split across pages | renderer (`cantSplit` under 2 inches) | no |
| `**Table N**` number and italic title above, `*Note.*` below | renderer styles them and builds the List of Tables | yes |
| Wide matrix tables on landscape pages | renderer moves any table with a row over 2.5 inches tall on portrait to landscape; learner can force it with `<!-- landscape -->` … `<!-- /landscape -->` | yes |

## References and appendices

| Requirement | Who | Checked |
|---|---|---|
| Every source held in Zotero, cited by key | learner adds sources; `zotero_sync.py push` can add them | no |
| Hanging indent 0.5 inch on every reference entry | renderer (any section headed "References") | yes |
| One consolidated APA reference list for the final portfolio | renderer generates it under the level-1 "References" heading; `--submission` drops the per-task lists | no |
| Every in-text citation in the list and every entry cited | renderer: lists are generated from the citations, so this holds by construction | yes (unformatted `[@key]` FAILs) |
| Appendices in the order your guide asks for | learner | no |

## Draft hygiene

| Requirement | Who | Checked |
|---|---|---|
| No raw markdown (`](`, `{#`, `**`, `<!--`, YAML) | renderer | yes |
| No placeholders or TODOs in a submission | learner; `--submission` refuses to render while any remain, and the checker FAILs them with `--submission` | yes |
| No single-sentence paragraphs except deliberate bridges | learner | yes (warn) |
| No em dashes (optional style rule) | learner | yes (warn) |
| Running-header lines from per-task assembly removed | renderer drops `*Portfolio of Evidence …*` lines | no |
