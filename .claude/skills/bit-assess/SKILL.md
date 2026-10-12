---
name: bit-assess
description: Mock assessment panel for the whole BIT Portfolio of Evidence, using the rubric and grading model the learner has recorded in the bit-standards reference files. Maps evidence for every Graduate Profile Outcome and rubric criterion across LT1 to LT7 and the appendices, estimates a band and grade per GPO, flags any GPO at risk of not reaching the pass band, applies the final-grade calculation exactly as recorded, runs the final-assembly checklist, ranks actions by grade impact, and lists the probe questions an assessor might ask in the oral. Use when the user asks "how would my portfolio be graded", "am I on track to pass", "assess my whole portfolio", "which GPO is weakest", "mock assessment", "peer review my portfolio", or is preparing for peer review or the oral.
argument-hint: "optional: path to the portfolio file; 'oral' to focus on oral probe questions"
---

# BIT mock assessment panel

A self-check, not a grade prediction: the real panel triangulates the portfolio, the presentation and a
professional conversation, and judges holistically. Say this once at the top of the report.

## Hard rules

1. **Evidence first, grade second.** Every band or grade cites portfolio line numbers. No evidence, no
   band.
2. **Holistic, across the whole body of work.** A criterion can be met anywhere in the portfolio. Do not
   mark a GPO down because the evidence sits in a different task than the rubric's indicative tasks
   suggest; do mark it down if the evidence is only asserted.
3. **Be conservative and say why.** When torn between two bands, give the lower and state what evidence
   would justify the higher. An inflated mock grade is worse than none before an oral.
4. **Incomplete portfolio.** If tasks are not yet written, grade on current evidence **and** state the
   projected band if those tasks deliver specific named evidence. Never project without naming the
   evidence.
5. **Apply the recorded model only.** Bands, the pass rule and the final-grade calculation come from
   `rubric.md` exactly as written. If `rubric.md` is still a template, map evidence to criteria only, say
   that no grade can be given until it is filled, and stop before step 5.
6. **No ghostwriting.** Actions say what evidence or reasoning is missing and where; they never supply the
   prose. Follow the workspace rules in the bit-standards skill.

## Workflow

### 1. Load the standards

From `.claude/skills/bit-standards/references/`: `rubric.md` (all), `lt8.md` (all), `vescas.md` (general
prompter and evidence requirement), `writing.md` §1 and §4, `sources.md`.

### 2. Inventory the portfolio

List every top-level part with line ranges. For each task run the scanner for words, estimated pages,
figures and citations:

```bash
uv run python .claude/skills/bit-prose/scripts/prose_scan.py Workings/Portfolio_of_Evidence.md --start A --end B --json
```

Mark placeholders. Note the appendices present and the references section.

### 3. Reuse recent task reviews

If `LTN_review_*.md` or `LTN_readiness_*.md` files in the reviews folder are newer than the portfolio,
use their findings as input (and say so); spot-check two or three of their key claims before relying on
them. Otherwise read the portfolio in full. Carry every **Integrity** finding into the assessment as a
risk: integrity problems surface in the oral.

### 4. Structural check

Run the assembly checklist in `lt8.md`: Present / Partial / Missing, with lines.

### 5. GPO evidence map and grades

For each GPO and each criterion in `rubric.md` §3:
- Where the evidence is (task, lines), strongest first.
- The band it supports, using the discriminators in `rubric.md` §3 and what assessors look for in §4.
- What evidence would move it up one band.

Then a holistic grade per GPO on the scale in `rubric.md` §2, with a two-to-four sentence justification.
Flag **pass risk** for any GPO below the pass band, and **floor risk** for any GPO at the pass band whose
evidence is thin or mostly asserted.

### 6. Calculate

Apply `rubric.md` §6 step by step in a table, showing every intermediate value. Do not convert to a letter
grade or apply any rule the section does not state. When tasks are missing, add a second, **projected**
column using the projected grades from step 5, and name the single cheapest change that moves the result.
Text the portfolio marks as not yet owned by the learner counts as evidence at risk: grade with it, flag
the GPO, and say what the grade becomes without it.

### 7. Peer-review criteria

If `lt8.md` records peer-review criteria, rate each with one line of evidence.

### 8. The central question

Answer the panel's central question from `rubric.md` §1 in three to five sentences from the evidence,
naming what an assessor would still need to be convinced of.

### 9. Actions ranked by grade impact

Up to ten. Each: the GPO and criterion, the task and lines, what is missing (evidence, reasoning,
reflection, structure), and the expected effect. Pass and floor risks first, then the largest band gains
for the least work.

### 10. Oral probe questions

Two or three per GPO that a panel could plausibly ask, aimed at the weakest or most ambitious claims. The
learner should be able to answer each without notes. With the argument `oral`, expand this section and add
the presentation notes from `lt8.md`.

### 11. Report and reply

Write `Workings/reviews/Portfolio_assessment_YYYY-MM-DD.md` with sections in the order above, opened by a
one-paragraph verdict and the indicative-only caveat. In chat: the GPO grade table, the calculation, any
pass or floor risks, the top five actions, the report path. Offer to queue the learner-only questions into
`Workings/DAILY/QUESTION_QUEUE.md` (format in bit-review step 9), only on agreement.
