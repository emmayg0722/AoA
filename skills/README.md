# Agent Skills

Portable skills that give a coding or chat agent the reasoning an AI architect
applies — installable on Claude, Codex, Cursor, or anything else that can read a
markdown file before it starts work.

These are the one part of this toolkit that does **not** run in a browser. The
rest of the repo is HTML tools an architect operates by hand; these are
instructions an *agent* loads and follows. Same methodology, different operator.

## What's here

| Skill | What it does | Verb | Maps to |
|---|---|---|---|
| [`business-problem-sharpener`](business-problem-sharpener/) | Turns a vague, solution-shaped request into a sharp, measurable, solution-free problem statement — then classifies it, starting with whether it is an AI problem at all | Interrogate | Phase 1 · Discovery |
| [`eval-harness-designer`](eval-harness-designer/) | Designs how you will know the system works — stratified test set, metrics by archetype, baselines, per-slice thresholds, regression plan | Interrogate | Phase 4 · PoC & Pilot |
| [`architecture-tradeoff-analyst`](architecture-tradeoff-analyst/) | Weights the criteria before the options are visible, so a comparison is evidence rather than advocacy — then argues the runner-up's case | Decide | Phase 3 · Architecture |
| [`architecture-red-team`](architecture-red-team/) | Attacks a proposed design along eight axes, ranked by likelihood and recoverability, each with its cheapest mitigation | Critique | Phase 3/5 · Design & Delivery |
| [`roi-scenario-model`](roi-scenario-model/) | Conservative / base / optimistic ROI for one solution, with NPV, payback, sensitivity, and the breakeven the case hinges on | Quantify | Phase 10 · ROI |

Each skill is a self-contained folder:

```
skill-name/
├── SKILL.md            # frontmatter (name, description) + the instructions
├── references/         # detail loaded only when needed
└── scripts/            # executable helpers, where arithmetic beats prose
```

## Design rules

These follow from wanting one skill to work on several agents, and from the
same privacy stance as the rest of the toolkit.

**Self-contained.** A skill never reads another file in this repo. The toolkit's
HTML tools are cross-referenced by name where useful, but nothing breaks if the
skill is copied out on its own — which is the normal way it gets used.

**No agent-specific assumptions.** No named tools, no vendor APIs, no
`.claude/`-only conventions inside the skill body. Frontmatter stays at `name`
and `description`, the two fields every implementation understands.

**Scripts are stdlib-only and optional.** `roi_model.py` and `eval_report.py`
need nothing but Python 3, and each skill says what to do if Python is
unavailable. A skill that
silently requires a package manager is not portable.

**One verb each.** The set is deliberately spread across interrogate / decide /
critique / quantify. Skills whose descriptions overlap compete for the same
request and mis-trigger, so each one owns a distinct kind of question.

**Prose explains why, not just what.** These are read by models with good
judgement working on messy real cases. Rules without reasons get misapplied at
the edges; a stated reason lets the agent adapt sensibly.

**No client data leaves the machine.** Same rule as every tool here. The skills
work from what the architect types; nothing uploads anything.

## Installing

The `SKILL.md` format — YAML frontmatter plus markdown — is readable by any
agent. What changes per agent is where the file goes.

### Claude Code / claude.ai

Copy the folder into a skills directory. Claude discovers it and loads the body
when the description matches what you are doing.

```bash
# just you, everywhere
cp -r skills/business-problem-sharpener ~/.claude/skills/

# or committed to a project, shared with the team
mkdir -p .claude/skills && cp -r skills/business-problem-sharpener .claude/skills/
```

On claude.ai, upload the folder as a skill in settings instead.

### Codex

Codex reads `AGENTS.md` from the repo root. Point it at the skill rather than
pasting the contents, so there is one copy to maintain:

```markdown
## Skills

Each file below states when it applies. Read the matching one and follow it.

- Sharpening or classifying a business problem →
  `skills/business-problem-sharpener/SKILL.md`
- Designing evaluation, test sets or accuracy targets →
  `skills/eval-harness-designer/SKILL.md`
- Choosing between technical approaches →
  `skills/architecture-tradeoff-analyst/SKILL.md`
- Reviewing or stress-testing a design →
  `skills/architecture-red-team/SKILL.md`
- Building an ROI or business case →
  `skills/roi-scenario-model/SKILL.md`
```

### Cursor, Windsurf, and similar

Same idea, different filename — a rule file that points at the skill:

```
# .cursor/rules/ai-architect.mdc
Before starting AI-architecture work — framing a problem, designing an
evaluation, choosing between approaches, reviewing a design, or building an
ROI case — list skills/*/SKILL.md, read the frontmatter description of each,
and follow the one whose description matches the task.
```

### Any other agent

Paste the contents of `SKILL.md` into the system prompt or project
instructions. The reference files under `references/` can be pasted on demand
when the skill points to them — that layering is deliberate, so the main
instructions stay short and the detail loads only when it is needed.

## Writing another one

Worth adding a skill when the work is **judgement-heavy, repeatable, and
currently inconsistent** — where the difference between a good and a poor answer
is knowing which question to ask next. Problem framing, trade-off analysis, and
review rubrics fit well.

Not worth it when the work is a lookup, a single calculation, or something the
model already does reliably. A skill that restates default behaviour costs
context and earns nothing.

If you add one:

1. Follow the folder shape above; keep `SKILL.md` under roughly 500 lines and
   push detail into `references/`.
2. Make the `description` specific about **when to trigger**, and lean toward
   over-describing the triggers — agents under-trigger skills more often than
   they over-trigger them.
3. Explain the reasoning behind each instruction, not just the instruction.
4. Add a row to the table above, and a card on the root `index.html`.
