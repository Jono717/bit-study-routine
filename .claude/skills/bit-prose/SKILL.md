---
name: bit-prose
description: Line-by-line writing pass on a section of the BIT Portfolio of Evidence. Runs a mechanical scanner (vague "This" openers, agentless passives, empty importance claims, single-sentence paragraphs, long sentences, placeholders, UK/US spelling mixes, unexplained acronyms, em dashes), confirms each hit by reading, checks the writing rules the learner has recorded in the bit-standards writing reference, and returns a table of line-referenced findings with the rule and a question or direction, never a rewrite. Use when the user asks to check, tighten, proofread, polish or line-edit portfolio writing, asks "does this read well", "check my paragraphs", "prose pass on LT2", or before a task goes to the facilitator.
argument-hint: "LT number, heading text, or line range; e.g. 'LT2', 'Ethics section of LT5', '880-1040'"
---

# BIT prose pass

Finds writing problems at sentence and paragraph level, with line numbers. It explains each problem and
asks the question that lets the learner fix it. It does not rewrite.

## Hard rules

1. **No rewrites of substance.** For each finding give: line, short quote (max 15 words), the rule, why it
   costs the reader, and a direction or question ("Who raised this? Name them." / "Which proposal does
   'This' refer to?"). Do not supply the replacement sentence.
2. **Mechanical fixes may be proposed** as a separate accept-or-reject list: spelling, grammar,
   punctuation, APA citation formatting, a term made consistent, an acronym expanded on first use.
3. **Confirm every scanner hit by reading the line.** Drop false positives silently; do not pad.
4. Follow the workspace rules in the bit-standards skill (drafts folder only, confidentiality).

## Workflow

### 1. Resolve the range

LT number: that task's section of the portfolio (bit-standards "Your workspace"). Heading text: that
heading to the next heading of the same or higher level. Line range: as given. Whole document only if
asked; then process task by task.

### 2. Load the rules

`.claude/skills/bit-standards/references/writing.md` §1 to §4 and §8, and the "Writing rules for VESCAS"
in `vescas.md` when the task expects VESCAS depth. If `writing.md` is still a template, say so and run
only the scanner and the general checks below.

### 3. Scan

From the workspace root:

```bash
uv run python .claude/skills/bit-prose/scripts/prose_scan.py Workings/Portfolio_of_Evidence.md --start A --end B --figures-dir Workings/Media
```

Flags: `this_opener_bare` (bare "This" followed by a verb; "This task" already names its referent and is
not flagged), `empty_importance`, `agentless_passive`, `single_sentence_paragraph` (bylines, list lead-ins
and `**Label:**` lines excluded), `long_sentence` (over 40 words), `em_dash`, `spaced_en_dash_pause`,
`vestas_naming` (the framework's older name), `voice_marker` (phrases common in machine-written text),
`placeholder`. Also: UK/US spelling mixes, acronyms never expanded anywhere in the document, figure SVG
sources containing em dashes, word counts, estimated pages, figures and citations. Add `--json` when
another skill consumes the output.

### 4. Read for what a scanner cannot see

Read the range paragraph by paragraph. Check every rule recorded in `writing.md` §3 and §4. Then these
general checks:

| Check | What to look for |
|---|---|
| Paragraph point | Is the point near the start, developed with explanation and evidence? |
| Bridges | Does each paragraph connect to the next, or does the focus jump? |
| People visible | Who did what? "I" for the learner's own contribution, "we" for shared work. |
| Connectors | "because" means reason, "however" contrast, "afterwards" sequence. Flag causal claims built only on sequence. |
| Observed vs inferred | Is it clear which statements are observation and which are inference? |
| Evidence pointers | Does a claim point to a figure, table or appendix where one exists? |
| Term consistency | The same term for the same thing throughout, including role titles and product names. |
| Voice | Passages that sound generic, templated or unlike the learner's surrounding prose. Flag gently; the learner decides. |
| Over-claiming | Superlatives and evaluative adjectives without evidence ("seamless", "significant" with no figure). |

### 5. Report

Write `Workings/reviews/LTN_prose_YYYY-MM-DD.md` (or `<slug>_prose_YYYY-MM-DD.md` for a non-task range):

```markdown
# Prose pass: <range description>
Lines A–B of <file>, <date>. Rules: writing.md (sources as recorded there) and general checks.

## Summary
<counts by rule; the two habits that cost the reader most; est. pages vs target>

## Findings
| Line | Quote | Rule | Why it costs the reader | Direction or question |

## Mechanical fixes (accept or reject)
| Line | Current | Proposed | Type |

## Glossary candidates
<acronyms and specialist terms not explained on first use>
```

Order findings by line. Group repeated mechanical issues into one row with the line list.

### 6. Reply

Chat: the summary, the two habits to work on first, the report path. Offer to apply only the accepted
mechanical fixes, and only in the drafts folder.
