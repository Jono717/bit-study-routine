# BIT Study Routine and Portfolio Skills

[Claude Code](https://docs.claude.com/en/docs/claude-code/overview) skills for Capable NZ Bachelor of
Information Technology learners building a Portfolio of Evidence.

| Skill | What it does |
|---|---|
| `/study` | A 15-minute daily session. Claude asks the next five questions from your question queue, you answer in your own words, and your answers are logged verbatim and filed as raw notes against the draft section they belong to. |
| `/bit-review LT3` | Reviews one learning task against your requirements, rubric, VESCAS prompter and writing rules, and writes a findings report with line references and questions only you can answer. |
| `/bit-prose LT2` | A line-by-line writing pass: scans for common problems, confirms each by reading, and returns findings with a question or direction for each. |
| `/bit-assess` | A mock assessment of the whole portfolio: evidence mapped to every GPO and rubric criterion, indicative grades, risks, ranked actions and likely oral questions. |
| `/bit-docx` | Renders the markdown portfolio to an APA 7 formatted Word document (contents, figure list, renumbered figures, references from Zotero) and audits the result. |
| `/bit-standards` | Answers "what does my guide say about X" from your own reference notes, with page citations. Also holds the reference files the other skills read. |

**None of these skills writes portfolio content.** They ask, check, point to the line and the standard,
and format. The writing is yours.

## No programme material is included

The review skills need the programme's requirements: the Learner Guide, the rubric, the VESCAS prompter and
any writing guidance from your facilitator. Those documents belong to the programme and are often supplied
for the recipient's use only, so **this repo does not contain any of their content.**

Instead, `.claude/skills/bit-standards/references/` holds **blank templates**: headings, tables and
instructions marked `FILL IN`. Each learner fills them from their own copies, with a page number for every
entry. The skills only ever judge against what you have filled in; if a template is still blank they say so
rather than guess.

Keep your filled-in reference files private. Do not commit them to a public repository or fork.

## Why /study exists

A portfolio rarely stalls for lack of reading. It stalls on questions only the learner can answer: what did
I actually do in that role, did I design that system or inherit it, which certificate can I still produce,
what would I do differently. Those questions pile up at the end of a draft and wait for a free weekend that
does not come.

`/study` pulls them out fifteen minutes at a time. A half-answered batch every day beats a full one every
three weeks.

## How the skills keep the work the learner's own

The programme requires the portfolio to be the learner's own experience, reflection and voice. The skills
are built around that:

1. **Claude asks; the learner answers.** No skill suggests an answer, offers examples to pick from, or fills
   a gap with a guess.
2. **Answers are logged verbatim and dated** in `ANSWER_LOG.md`, a provenance trail showing where each piece
   of content came from and when.
3. **Answers are filed raw, not written up.** They land in the draft as a marked block that says "write up
   in my own words, then delete this block".
4. **Reviews critique; they do not rewrite.** Each finding gives a line, the standard and a question. Only
   mechanical fixes (spelling, APA formatting, a term made consistent) are offered, as a list to accept or
   reject.
5. **Unowned text is an integrity finding.** bit-review flags any passage that originated in AI-written
   notes and has not been accepted by the learner.
6. **"I don't know" and "ask my facilitator" are valid answers.** They are logged as honest gaps or routed
   to the next facilitator meeting.
7. **Drafts only.** No skill writes to the folder the learner submits from.

## What is in this repo

```text
bit-study-routine/
├── .claude/skills/
│   ├── study/SKILL.md                  # /study
│   ├── bit-standards/
│   │   ├── SKILL.md                    # workspace layout and rules every bit-* skill follows
│   │   └── references/                 # BLANK TEMPLATES: fill from your own copies of the guides
│   │       ├── sources.md              #   which documents you have and which one wins
│   │       ├── rubric.md               #   rubric, rating levels, grade calculation
│   │       ├── vescas.md               #   VESCAS dimensions and prompter questions
│   │       ├── writing.md              #   writing, reflection and AI-use rules
│   │       └── lt1.md … lt8.md         #   per-task requirements
│   ├── bit-review/SKILL.md
│   ├── bit-prose/                      # SKILL.md + scripts/prose_scan.py
│   ├── bit-assess/SKILL.md
│   └── bit-docx/                       # SKILL.md, format spec, renderer, checker, Zotero sync
└── templates/DAILY/                    # blank STUDY_ROUTINE, QUESTION_QUEUE, ANSWER_LOG for /study
```

## Setting it up

You need [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) and
[uv](https://docs.astral.sh/uv/) installed, and a folder that holds your portfolio drafts (your
"workspace"). Replace `~/my-portfolio` below with the path to that folder.

1. Download this repo:

   ```bash
   git clone https://github.com/Jono717/bit-study-routine.git
   cd bit-study-routine
   ```

2. Copy the skills into your workspace:

   ```bash
   mkdir -p ~/my-portfolio/.claude/skills
   cp -R .claude/skills/* ~/my-portfolio/.claude/skills/
   ```

3. Copy the `/study` templates into your workspace:

   ```bash
   mkdir -p ~/my-portfolio/Workings
   cp -R templates/DAILY ~/my-portfolio/Workings/
   ```

4. Fill in the reference templates in `~/my-portfolio/.claude/skills/bit-standards/references/` from your own
   copies of the Learner Guide, rubric, VESCAS prompter and any writing guidance. Start with `lt1.md` to
   `lt8.md` and `rubric.md`; the skills tell you when they need a file you have not filled yet.

5. If your folders differ from the defaults (portfolio in `Workings/Portfolio_of_Evidence.md`, drafts in
   `Workings/`, figures in `Workings/Media/`), write your layout in `~/my-portfolio/CLAUDE.md`. The table in
   `bit-standards/SKILL.md` under "Your workspace" shows what to record.

6. Open Claude Code in your workspace and try `/study` or `/bit-review LT1`.

**For `/bit-docx` citations** you also need the Zotero desktop app and Node.js. The renderer uses Zotero's
own citation engine and APA 7 style from the installed app, so the output matches Zotero's Word plugin.
Without them, render with `--no-citations`.

## Filling the /study queue

The queue is the part that matters. Good sources of questions:

- **Your facilitator's feedback.** Every "can you say more about..." is a question.
- **The task requirements.** Each thing a task asks for that your draft does not yet show is a question.
- **Gaps you left in your own drafts.** Any `TODO`, `?` or "check this" note.
- **A review.** `/bit-review` ends with "Questions for you" and offers to add them to the queue.

Each batch names one destination file and section, holds five questions or fewer, and has a short "why"
line saying what answering it unblocks. `templates/DAILY/QUESTION_QUEUE.md` explains the format and has a
worked example.

## A /study session, start to finish

1. You type `/study`.
2. Claude says where things stand ("last session 3 days ago, Batch 4 is next") and asks Batch 4's
   questions, numbered.
3. You answer, as briefly or loosely as you like.
4. Claude appends your answers to `ANSWER_LOG.md`, files them as a raw block in the destination draft, and
   strikes the batch off the queue.
5. Claude closes with one line: what got closed and what is next.

## Reports

`/bit-review`, `/bit-prose` and `/bit-assess` write dated reports to `Workings/reviews/` (for example
`LT3_review_2026-10-12.md`), so you can compare one review with the next and show your facilitator how a
task developed.

## Adapting it

- `/study`: anything under "My own rules" in `STUDY_ROUTINE.md` overrides the skill's defaults (session
  length, folders, a workplace confidentiality register).
- The bit-* skills: record your layout and any confidentiality register in your workspace `CLAUDE.md`.
- Everything the skills judge against lives in the reference files you fill in, so updating your notes
  updates the reviews.

## Licence

MIT. See [LICENSE](LICENSE). The licence covers the skills and scripts in this repo only. It grants nothing
over programme documents, which are not included.
