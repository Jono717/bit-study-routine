---
name: study
description: Run a 15-minute portfolio study session. Claude asks the next batch of questions from the learner's question queue, the learner answers in their own words, and the answers are logged verbatim with a date and filed against the portfolio section they belong to. Claude never writes the portfolio prose. Use when the learner types /study, says "study session", "15 minutes", "ask me the next questions", or wants to work through their question queue.
argument-hint: "optional: the folder holding QUESTION_QUEUE.md, or a topic to talk through instead of the queue"
allowed-tools: Read, Edit, Write, Glob, Bash(date:*)
---

# 15-minute study session

One short session that turns questions only the learner can answer into dated, logged answers.
Claude asks. The learner supplies every fact, judgement and reflection.

## Files

Find the folder that holds the three study files, in this order:

1. The folder named in the argument, if one was given.
2. `Workings/DAILY/` in the current workspace.
3. Anywhere in the workspace that contains `QUESTION_QUEUE.md`.

If none exists, say so, point the learner at `templates/DAILY/` in the bit-study-routine repo, and stop.

| File | Role |
|---|---|
| `STUDY_ROUTINE.md` | The protocol and the learner's own rules. Its rules override the defaults below. |
| `QUESTION_QUEUE.md` | Ordered batches of questions. Each batch names a destination file and section. |
| `ANSWER_LOG.md` | Dated, verbatim answers plus a streak table. The provenance trail. |

## Steps

1. Read `STUDY_ROUTINE.md`, `QUESTION_QUEUE.md` and the last 80 or so lines of `ANSWER_LOG.md`.
   Get today's date with `date +%F`.
2. Say in one line where things stand: last session date, days since, which batch is next.
3. Ask every open question in the next unstruck batch at once, numbered, in plain language, with no
   preamble. Do not explain why each question matters unless asked.
4. Wait for answers. Accept fragments, "I don't know" and "ask my facilitator": all three close a
   question. Ask a follow-up only when an answer is too ambiguous to file. Never suggest an answer,
   offer example answers, or fill a silence with a guess.
5. When the batch is answered, or the learner calls time:
   - **`ANSWER_LOG.md`:** append a `### YYYY-MM-DD: Batch N` section with each answer as close to
     verbatim as possible (spelling fixes only), then add a row to the streak table.
   - **Destination file:** under the section named in the batch header, add the answers as a clearly
     marked raw block for the learner to write up later:

     ```markdown
     > **Raw answers, YYYY-MM-DD (Batch N). Write up in my own words, then delete this block.**
     > 1. <answer, verbatim>
     > 2. I don't know yet. (gap)
     > 3. Ask my facilitator. (facilitator question)
     ```

     Do not turn the answers into portfolio prose. That writing is the learner's.
   - **`QUESTION_QUEUE.md`:** strike each answered question with `~~` and the date. Strike the batch
     heading once every question in it is closed. Unanswered questions stay open.
6. Close with one line: what got closed, what is next. No summary essay.

## Rules

- **Fifteen minutes of the learner's effort, hard stop.** Unfinished questions stay queued. A
  half-answered batch every day beats a full one every three weeks.
- **Nothing is invented.** If the learner did not say it, it is not written anywhere. A logged gap
  is honest evidence; a fluent guess is not.
- **No ghostwriting.** This skill captures and files. The learner writes the portfolio. Spelling
  and formatting fixes are fine; new sentences, reflections or claims are not.
- **Drafts only.** Write only to the three study files and to destination files in the learner's
  drafts area. Never write to the folder the learner submits from or shares with their facilitator.
- **Workplace confidentiality.** The answer log is private and may be specific. When filing a raw
  block into a draft, replace identifying details (internal system names, colleagues' names, budget
  figures) with neutral labels such as "System A" or "a colleague in the security team", and say
  in the block that you did.
- **The learner's topic wins.** If they arrive with something else to talk through, drop the queue,
  follow them, and log it as an unbatched session.
- **Skipping a day is not failure.** Do not comment on gaps in the streak.

$ARGUMENTS
