# The five agents

The scaffolder installs these into `<project>/.claude/agents/` (sources in
`assets/agents/`). Each is a Claude Code subagent: `name`, `description`, `tools`, `model`
in the frontmatter, the role's standing instructions in the body. Launch them with the
Agent tool (`subagent_type: <name>`) or let `scripts/chapter-loop.js` do it. The prompt you
pass is the *task* (which chapter, which files, which budget); the agent file is the *role*.

| Agent | Role | Model to use | Typical budget |
|---|---|---|---|
| `chapter-author` | writes or completes one chapter from its spec: text, code with self-test, figures, data, solutions, glossary terms | strongest available (`inherit`) | 60 tool calls |
| `chapter-reviewer` | reviews one chapter against rubric A–H; verifies by building, running, recomputing; writes `reviews/<id>-round<k>.md`; never edits the chapter | strong; a cheaper model is acceptable | 40 |
| `chapter-reviser` | applies every required change of a review, rebuilds, re-runs code, appends the response | same as reviewer | 50 |
| `book-copyeditor` | book-wide judgment items from the audits on a precise file list; minimal edits; single-chapter builds to verify | strong | 150–200 |
| `accuracy-checker` | read-only check of every theorem/proof/table; writes `docs/accuracy-spot-check.md` | strongest available | 110 |

Prompts that worked are embedded in `scripts/chapter-loop.js` (`writePrompt`,
`reviewPrompt`, `revisePrompt`, `applyReviewPrompt`); for the copyeditor and the accuracy
checker see `references/book-level-passes.md` §4–6. Always include in a task prompt: the
repository root, the exact files the agent owns, the files it must not touch, the budget,
the verification it must run before reporting, and the shape of its final report.

To change the model of an agent, edit the `model:` line in its file (`inherit`, `opus`,
`sonnet`, `haiku`); the loop script's `--reviewModel` / `--writeModel` arguments override
it for one run.
