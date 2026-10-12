---
name: bit-standards
description: Answers questions about the Capable NZ / Otago Polytechnic Bachelor of Information Technology (BIT) portfolio requirements from the learner's own reference notes, with citations to the source document and page, and holds the shared reference files that bit-review, bit-prose and bit-assess load. The reference files ship as blank templates; the learner fills them from their own copies of the programme guides. Use whenever the user asks what a Learning Task (LT1 to LT8) requires, how the portfolio is graded, what a rubric band or GPO means, page counts, timelines, VESCAS questions, electives, peer review, the oral presentation, or "what does my guide or facilitator say about X".
---

# BIT standards

Answers questions about BIT portfolio requirements from the learner's reference notes, with citations, and
holds the reference files that the review skills load.

## Before first use: fill the reference files

The files in `references/` are **templates**. They contain structure and instructions, not programme
content. The learner fills them from their own copies of the programme documents (Learner Guide, rubric or
assessor guidance, the VESCAS prompter, any writing guidance from their facilitator), with a page number
for every entry.

If a file the question needs is still a template (it contains `FILL IN`), say so, name the file, and answer
only from what is filled in or from the source PDF itself. Never fill a gap from general knowledge of the
programme and never guess at rubric wording.

**Keep filled reference files private.** Programme documents are often supplied for the recipient's use
only. Do not commit filled files to a public repository.

## Reference files

Load only what the question needs.

| File | Contents (once filled) |
|---|---|
| `references/sources.md` | Source register: each document, version, where it is kept, and which one wins when they disagree |
| `references/rubric.md` | Pass rule, rating levels, the rubric criteria per Graduate Profile Outcome, what assessors look for, the final-grade calculation, outcomes on the day |
| `references/vescas.md` | The VESCAS dimensions, the prompter questions, how the facilitator wants VESCAS used, the learner's elective prompters |
| `references/writing.md` | Writing, reflection and critical-thinking rules, planning tools, AI-use rules, the pre-submission self-check |
| `references/lt1.md` … `references/lt8.md` | Per task: length, effort, rubric criteria fed, what the guide asks for, suggested headings, evidence, review focus |

## Answering a question

1. Find the answer in the reference files. Cite the source document and page recorded there (for example
   "Learner Guide p. 31"), not the reference file.
2. If sources disagree, apply the authority order in `references/sources.md` and say which source wins.
3. If the reference files do not cover it, read the source PDF from the guides folder named below
   (`pdftotext -layout` extracts text; image-only pages need a render). Say that you went to the PDF, and
   suggest the learner adds the answer to the right reference file.
4. Never present suggestions or guidance as requirements. Guidance shapes how to meet the Learner Guide;
   it does not add to what the Learner Guide requires, unless the facilitator says otherwise.

## Your workspace

Defaults below. If the learner's layout differs, they record it in their workspace `CLAUDE.md` and every
BIT skill follows that instead.

| Item | Default |
|---|---|
| Portfolio | `Workings/Portfolio_of_Evidence.md`, one document. A task runs from its `# Learning Task N` heading to the next `# Learning Task` or `# References` heading. If the learner keeps one file per task, use those files. |
| Drafts folder | `Workings/` |
| Reviews | `Workings/reviews/` |
| Figures | `Workings/Media/` |
| Study files | `Workings/DAILY/` (`QUESTION_QUEUE.md`, `ANSWER_LOG.md`, used by `/study`) |
| Guides (PDFs) | `Reference_Materials/`. Private; never in a public repository. |
| Submission folder | `BIT_Data/` or wherever the learner keeps the copy they share with their facilitator |

If the layout has changed, find the newest portfolio or task draft by modification time before assuming.

## Rules every BIT skill inherits

- **Write only in the drafts folder.** Never write to the submission folder unless the learner explicitly
  asks for that specific copy.
- **The substance, judgement and voice must be the learner's.** Reviews critique, question and point to the
  standard. They do not write replacement prose or invent experiences, evidence, quotes or figures.
- **Workplace confidentiality.** Do not reproduce internal system names, colleagues' names or commercial
  figures in anything produced. If the learner keeps a confidentiality register in their `CLAUDE.md`, apply
  it.
- **Tools.** Run Python through `uv run python`. Some environments block `grep`, `sed` or `awk` through
  hooks; search with the Read tool or Python one-liners instead.
