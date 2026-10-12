---
name: bit-review
description: Review one BIT Learning Task (LT1 to LT8) of the learner's Portfolio of Evidence against the requirements, rubric, VESCAS prompter and writing rules the learner has recorded in the bit-standards reference files, then write a findings report with line references, indicative rubric bands, VESCAS gaps, unsupported claims, integrity flags and questions only the learner can answer. Also does a readiness review for a task that has no draft yet. Use when the user says "review LT3", "check my LT5", "is my capstone section ready", "what is missing from task 4", "review my portfolio task", or asks for feedback on a BIT learning task. For a line-by-line writing pass use bit-prose; for a whole-portfolio mock assessment use bit-assess.
argument-hint: "LT number (1-8), optionally a file path; e.g. 'LT3' or 'LT6 readiness'"
---

# BIT task review

Produces an evidence-based review of one learning task. The review critiques and asks; it never writes the
learner's portfolio for them.

## Hard rules

1. **No ghostwriting.** Do not draft replacement paragraphs, sentences, reflections, experiences, feelings,
   evidence, quotes or figures. Point to the line, name the standard, say what is missing, and ask the
   question that would let the learner write it. Allowed: spelling, grammar, APA formatting and
   term-consistency fixes, offered as a list for the learner to accept.
2. **Every finding cites a location.** Draft mode: a line number in the reviewed file. Readiness mode:
   `file:line` in the source material. Quote at most 15 words.
3. **Check the whole portfolio before calling something absent.** If the evidence is in another task, say
   where and whether to cross-reference it (Major at most, not Blocker). If it exists only in files outside
   the portfolio, report it as "exists but not in the portfolio" and say where it belongs.
4. **Bands are indicative.** The panel judges holistically across the whole body of work. Estimate bands per
   rubric criterion as evidenced in this task; leave GPO grades to bit-assess.
5. **Do not reward length or topic coverage.** Reward the band qualities `rubric.md` marks as discriminators.
6. **Standards come from the reference files only.** If a file this review needs is still a template
   (contains `FILL IN`), say which one at the top of the report and review only against what is filled in.
   Never substitute general knowledge of the programme for the learner's sources.
7. Follow the workspace rules in the bit-standards skill (drafts folder only, confidentiality).

## Severity and finding types

- **Blocker**: a required item absent from the whole portfolio; a rubric criterion with no evidence anywhere
  in the portfolio; a confidentiality problem; or an integrity issue (below).
- **Major**: a requirement only partly met, or met only in another task without a cross-reference; a
  criterion held at the pass band when the next band is within reach.
- **Minor**: polish.
- **Integrity** (always its own section, always a Blocker for submission): text the learner has not yet
  owned (for example reflection that originated in AI-written notes with no sign the learner accepted it);
  a source cited but not read; a figure or metric that cannot be traced to evidence; an internal note left
  in submission text. If the learner uses `/study`, `ANSWER_LOG.md` is the verbatim record of their own
  words; anything assembled from it by AI is not their words until they say so.

## Workflow

### 1. Resolve the target

- Argument is an LT number, "LTn readiness", or a path. No argument: list the tasks present with their word
  counts and ask which to review.
- Find the task in the portfolio (bit-standards "Your workspace"). Record start and end line numbers.
- If the section is a placeholder (under about 300 words of the learner's prose), switch to **readiness
  mode** (step 6).

### 2. Load the standards

From `.claude/skills/bit-standards/references/` read: `ltN.md` (always), `rubric.md` (the criteria `ltN.md`
lists as fed, plus §1 and §2), `vescas.md` (when `ltN.md` expects VESCAS depth; skim otherwise),
`writing.md` §1, §3, §4, §8 and §9. For LT8 read `lt8.md` in full and treat the whole portfolio as the
target.

### 3. Read the task and its context

- Read the whole section with line numbers, including any in-section appendices.
- Search the whole portfolio for passages in other tasks that cite this task; contradictions usually
  surface there.
- Read what `ltN.md` lists under "Links to other tasks", and any earlier review in the reviews folder.

### 4. Run the mechanical scan (draft mode)

From the workspace root:

```bash
uv run python .claude/skills/bit-prose/scripts/prose_scan.py Workings/Portfolio_of_Evidence.md --start START --end END --figures-dir Workings/Media --json
```

It returns word counts, estimated pages, figures, citations, placeholders, UK/US spelling mixes, glossary
candidates and flagged lines. Use it as input, not as the review: confirm each flag by reading the line.

### 5. Evaluate (draft mode)

Work through these in order; each produces findings with a severity:

a. **Requirements.** Every item under "What the Learner Guide asks" in `ltN.md`: Met / Partial / Missing,
   with lines. Length against the target (the estimate assumes about 275 words per APA double-spaced page
   plus half a page per figure; say so).
b. **Rubric criteria fed.** For each criterion `ltN.md` lists: the band the evidence supports, the
   discriminator it does or does not show, line references, and **what would lift it one band**, phrased as
   a direction or question, not as text. If the task feeds no criteria, report what it sets up for later
   tasks and whether that is there.
c. **VESCAS.** Per dimension in `vescas.md`: present, woven in or bolted on, and the most important
   unanswered prompter question. Where `vescas.md` records recursive questions: are they answerable from
   the text?
d. **Evidence chain.** Against `writing.md` §1: the strongest unsupported claims, evidence that is never
   explained, and explanation that never reaches reflection or a change in practice. Separate observed
   from inferred.
e. **Critical thinking and reflection.** Against `writing.md` §4: an assumption named, an alternative
   considered and rejected with reasons, the limits of the evidence stated, the learner's own role
   examined. Name where each is present or absent.
f. **Writing**, top five issues only. Point to bit-prose for the full pass.
g. **Integrity, voice and confidentiality.** The integrity checks above; passages that read generic or
   could describe anyone; claims the learner would struggle to defend in the oral; workplace detail that
   should not be there; whether the declaration of tools will need to mention AI assistance.
h. **Cross-task consistency.** Dates, job titles, locations, numbers, levels claimed, elective names,
   project descriptions, figure numbers, key terms.
i. **Decisions only the facilitator can make** (scope, electives, depth), listed separately.
j. **Remaining review-focus items** in `ltN.md` not already covered.

### 6. Readiness mode (no draft yet)

Do not draft the task. Instead:
- Inventory what exists (plans, artefacts, notes, learning logs, earlier tasks' bridges), noting for each
  whether it is the learner's own words or AI-assembled and not yet owned.
- If `writing.md` §5 has a planning tool, fill it **only from the learner's own words**, citing `file:line`
  for each entry; mark every gap `NEEDS YOUR INPUT`.
- If `ltN.md` records a task one-pager or checklist, mark each item Have / Partial / Missing.
- Risks to the rubric criteria the task feeds, and the decisions the facilitator must confirm.

### 7. Questions for the learner

Up to ten, each tied to a finding, each answerable only by the learner (a fact, a decision, a recollection,
a judgement). Plain language. Do not repeat questions already open in `QUESTION_QUEUE.md`.

### 8. Write the report

Path: `Workings/reviews/LTN_review_YYYY-MM-DD.md` (draft mode) or `Workings/reviews/LTN_readiness_YYYY-MM-DD.md`
(readiness mode). Create the folder if needed; add `-2`, `-3` if the file exists.

Draft mode structure:

```markdown
# LTN review: <task title>

Reviewed: <file> lines A–B, <date>. Standards: <the sources and versions listed in sources.md>.
Reference files still templates: <list, or "none">.
Indicative only: the panel judges holistically across the whole portfolio.

## Verdict

<two or three sentences: where the task stands against its purpose, the single biggest lever>
Length: ~N words, ~P pages est. (target X–Y, or "no page target"). Figures: F. Citations: C.

## Top actions (ranked by effect on the rubric)

1. [Blocker|Major|Minor] <action> (Lnnn): why, which criterion

## Requirements checklist

| Requirement (source) | Status | Where / note |

## Rubric criteria this task feeds

| Criterion | Band supported here | Evidence (lines) | To lift one band |

## VESCAS

| Dimension | Present? | Woven or bolted on | Unanswered prompter question(s) |

## Evidence chain

## Critical thinking and reflection

## Writing (top 5; run bit-prose for the full pass)

## Integrity, voice and confidentiality

## Cross-task consistency

## Decisions for the facilitator

## Questions for you
```

Readiness mode structure: Verdict; Inventory (source, owned or not); Planning sheet (cited, with
`NEEDS YOUR INPUT`); Checklist status; Rubric and VESCAS risks; Decisions for the facilitator; Questions
for you.

### 9. Reply

In chat: the verdict, the top actions, the report path. Then offer, as a question, to append the
"Questions for you" as the next batch in `Workings/DAILY/QUESTION_QUEUE.md` so `/study` picks them up. Only
append after the learner agrees. When running as a subagent, skip the offer and return the questions to the
caller instead. Queue format:

```markdown
## Batch N: LTN review <date>, <short theme>

*Destination: `Workings/Portfolio_of_Evidence.md` LTN (lines A–B). Why it matters: <one line tied to the rubric>.*

1. ...
```

Keep a batch to at most five questions; split into two batches if needed.
