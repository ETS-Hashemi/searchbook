# Textbook factory — a reusable kit for writing a textbook with Claude

This folder packages the process that produced *Multi-Agent Path Planning and Drone
Collision Avoidance* (737 pages, 25 chapters, 179 figures, 26 code files, two review rounds
per chapter) as a **skill** for Claude Code plus five **agent** definitions, so that the same
pipeline can write a book on another subject.

```
book-kit/
├── README.md                      this file
└── textbook-factory/              the skill (install this folder)
    ├── SKILL.md                   what Claude does, phase by phase, and the loop rules
    ├── references/                playbook, review rubric, spec format, book-level passes, lessons, agents
    ├── scripts/                   new_book.py (scaffolder), chapter-loop.js (Workflow), qa.sh, check_book.py,
    │                              american.py, joinindex.py, autosave.sh
    └── assets/                    LaTeX templates (style file, root document, build/package scripts, front
                                   matter, chapter template, tools), STYLE_GUIDE/brief/TODO templates,
                                   the five agent files, book.example.json, KICKOFF.md
```

## Install

**Claude Code (recommended; this is where parallel agents exist).** Copy the skill into the
new book's repository or into your user profile:

```bash
mkdir -p <repo>/.claude/skills && cp -r book-kit/textbook-factory <repo>/.claude/skills/
# or, for every project:  cp -r book-kit/textbook-factory ~/.claude/skills/
```

The agents are installed by the scaffolder (`.claude/agents/` of the new repository), so a
fresh session there sees both the skill and the agents.

**claude.ai.** Upload `textbook-factory.skill` (the packaged version of the same folder) in
Settings → Skills. The skill then runs without subagents, one chapter at a time, as described
at the end of `SKILL.md`.

## Start a new book (five steps)

1. Write `book.json` from `textbook-factory/assets/book.example.json`: title, author, parts
   and chapters (id, file stem, title, one-line scope, essential or not), appendices,
   spelling, code language, canonical sources.
2. Scaffold: `python3 .claude/skills/textbook-factory/scripts/new_book.py book.json .`
   (in an empty repository), then `git add -A && git commit -m "Scaffold"`.
3. Put the source brief in the repository (the Word file, syllabus or outline) and paste
   the prompt from `textbook-factory/assets/KICKOFF.md` into a Claude Code session opened in
   that repository, with the bracketed parts filled in.
4. Watch `TODO.md` and the loop log; use the follow-ups listed in `KICKOFF.md`
   ("continue", "check that the agents are not stalled", "how long is left").
5. When Claude delivers the PDF and the zip: read the book yourself, get a human expert
   review, decide the license, and add your own front-matter pages.

## What the agents are

| Agent | Does | Model |
|---|---|---|
| `chapter-author` | writes or completes one chapter from its spec, with code, figures, exercises | strongest you have |
| `chapter-reviewer` | reviews one chapter against the rubric, verifying by building and running | strong (cheaper is acceptable) |
| `chapter-reviser` | applies the review, rebuilds, responds | same as reviewer |
| `book-copyeditor` | book-wide judgment items on a precise file list | strong |
| `accuracy-checker` | read-only check of every theorem and comparison table | strongest you have |

Change an agent's model in the `model:` line of its file. The loop script's
`writeModel` / `reviewModel` arguments override it per run.

## Costs and time, from the drone book

Twenty-five chapters took about five working days of wall-clock time, interrupted by
rate limits; roughly 40 % of the tokens went to authors, 45 % to the review/revision
loop, 15 % to the book-level passes. Expect one chapter per author agent per hour, two
review rounds per chapter, and a full pdfLaTeX build of 8–12 minutes for a 700-page book
(2 minutes with the figure cache).
