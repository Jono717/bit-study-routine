# BIT 15-Minute Study Routine

A small [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) skill for Capable NZ
Bachelor of Information Technology learners building a Portfolio of Evidence. Type `/study` and
Claude asks you the next five questions from your own question queue. You answer in your own
words. Your answers are logged verbatim with a date and filed, as raw notes, against the portfolio
section they belong to. You then write the portfolio prose yourself.

## Why it exists

A portfolio rarely stalls for lack of reading. It stalls on questions only the learner can answer:
what did I actually do in that role, did I design that system or inherit it, which certificate can I
still produce, what would I do differently. Those questions pile up at the end of a draft and wait
for a free weekend that does not come.

This routine pulls them out fifteen minutes at a time. A half-answered batch every day beats a full
one every three weeks.

## How it keeps the work the learner's own

The programme requires the portfolio to be the learner's own experience, reflection and voice. The
skill is built around that:

1. **Claude asks; the learner answers.** It never suggests an answer, offers examples to pick from,
   or fills a silence with a guess.
2. **Answers are logged verbatim and dated** in `ANSWER_LOG.md`. That log is a provenance trail
   showing where each piece of content came from and when.
3. **Answers are filed raw, not written up.** They land in the draft as a marked block that says
   "write up in my own words, then delete this block". Claude does not turn them into portfolio
   prose.
4. **"I don't know" and "ask my facilitator" are valid answers.** They are logged as honest gaps or
   routed to the next facilitator meeting, rather than papered over.
5. **Drafts only.** The skill never writes to the folder the learner submits from or shares with
   their facilitator.

## What is in this repo

```text
bit-study-routine/
├── .claude/skills/study/SKILL.md   # the /study skill: what Claude does in a session
└── templates/DAILY/
    ├── STUDY_ROUTINE.md            # the protocol, plus space for your own rules
    ├── QUESTION_QUEUE.md           # batches of questions, with one worked example
    └── ANSWER_LOG.md               # dated answers and a streak table
```

## Setting it up

You need Claude Code installed and a folder that holds your portfolio drafts (your "workspace").
Replace `~/my-portfolio` below with the path to that folder.

1. Download this repo:

   ```bash
   git clone https://github.com/Jono717/bit-study-routine.git
   cd bit-study-routine
   ```

2. Copy the skill into your workspace:

   ```bash
   mkdir -p ~/my-portfolio/.claude/skills
   cp -R .claude/skills/study ~/my-portfolio/.claude/skills/
   ```

   To use it from any folder instead, copy it to `~/.claude/skills/` rather than into the workspace.

3. Copy the three templates into your workspace:

   ```bash
   mkdir -p ~/my-portfolio/Workings
   cp -R templates/DAILY ~/my-portfolio/Workings/
   ```

   The skill looks in `Workings/DAILY/` first. If you keep them somewhere else, pass the folder when
   you start: `/study notes/daily`.

4. Fill in `STUDY_ROUTINE.md` (why you are doing this, plus any rules of your own) and replace the
   example batch in `QUESTION_QUEUE.md` with your first real questions. See the next section.

5. Open Claude Code in your workspace and type `/study`.

## Filling the queue

The queue is the part that matters. Good sources of questions:

- **Your facilitator's feedback.** Every "can you say more about..." is a question.
- **The Learner Guide's task description.** Each thing a task asks for that your draft does not yet
  show is a question.
- **Gaps you left in your own drafts.** Any `TODO`, `?` or "check this" note.
- **A review of a draft.** You can ask Claude to read a draft and list the questions only you could
  answer, as long as it writes questions and never answers. For example:

  > Read `Workings/LT2_draft.md`. List the questions only I can answer about my own experience that
  > would fill its gaps. Group them into batches of five with the destination section for each.
  > Write questions only. Do not draft any answers or portfolio text.

Each batch names one destination file and section, holds five questions or fewer, and has a short
"why" line saying what answering it unblocks. `QUESTION_QUEUE.md` explains the format and has a
worked example.

## A session, start to finish

1. You type `/study`.
2. Claude says where things stand ("last session 3 days ago, Batch 4 is next") and asks Batch 4's
   questions, numbered.
3. You answer, as briefly or loosely as you like.
4. Claude appends your answers to `ANSWER_LOG.md`, files them as a raw block in the destination
   draft, and strikes the batch off the queue.
5. Claude closes with one line: what got closed and what is next.

## Adapting it

Everything in `STUDY_ROUTINE.md` under "My own rules" overrides the skill's defaults. Common changes:
a different session length, a different folder for your drafts, or a confidentiality register for
your workplace (which internal names to replace with neutral labels when answers move into a draft).

## Licence

MIT. See [LICENSE](LICENSE).
