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
| [`context-architecture-designer`](context-architecture-designer/) | Designs how information actually reaches the model — retrieved vs prompt vs fine-tuned, chunking, reranking, permissions, caching, and the token/cost budget per request | Design | Phase 3 · Architecture |
| [`roi-scenario-model`](roi-scenario-model/) | Conservative / base / optimistic ROI for one solution, with NPV, payback, sensitivity, and the breakeven the case hinges on | Quantify | Phase 10 · ROI |
| [`brand-skill-generator`](brand-skill-generator/) | Distils a company's real brand out of its template, logo, site and LinkedIn into an approved profile, then generates a named, installable skill so later output carries that identity | Distil | Any phase · every deliverable |

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

**Scripts are stdlib-only and optional.** `roi_model.py`, `eval_report.py`,
`context_budget.py` and `brand_profile.py` need nothing but Python 3, and each skill says
what to do if Python is unavailable. A skill that
silently requires a package manager is not portable.
`brand_profile.py` reads `.pptx` and `.svg` without a library at all — both are
XML, and a `.pptx` is a zip of it.

**One verb each.** The set is deliberately spread across interrogate / design /
decide / critique / quantify / distil. Skills whose descriptions overlap compete for the same
request and mis-trigger, so each one owns a distinct kind of question.

**Prose explains why, not just what.** These are read by models with good
judgement working on messy real cases. Rules without reasons get misapplied at
the edges; a stated reason lets the agent adapt sensibly.

**No client data leaves the machine.** Same rule as every tool here. The skills
work from what the architect types; nothing uploads anything.

## Installing

### The one command

Clone the repo, then run the installer. It is standard-library Python, so it
works the same on macOS, Linux and Windows with nothing to install first.

```bash
git clone https://github.com/emmayg0722/AoA.git
cd AoA/skills

python3 install.py --list                      # see what is available
python3 install.py --agent claude              # all of them, just for you
python3 install.py --agent codex  --project .  # copies + wires AGENTS.md
python3 install.py --agent cursor --project .  # copies + writes a rule file
```

On Windows use `py install.py …` or `python install.py …` if `python3` is not
on your PATH. Nothing else differs — `~` resolves to `%USERPROFILE%`, so the
Claude path becomes `%USERPROFILE%\.claude\skills` automatically.

Useful flags:

| Flag | Effect |
|---|---|
| `--skill NAME` | Install one skill instead of all of them. Repeatable. |
| `--project DIR` | For Claude, install into `DIR/.claude/skills` so the team shares it. Required for Codex and Cursor. |
| `--force` | Overwrite skills already installed. Without it they are skipped and reported. |
| `--dry-run` | Print what would happen and change nothing. |

For Codex and Cursor the installer also writes the wiring file that points the
agent at the skills. It inserts a marked block, so re-running updates that block
and leaves the rest of your `AGENTS.md` untouched.

### Or do it by hand

Nothing here is magic — a skill is a folder, and installing it is a copy.

| Agent | Where the folder goes |
|---|---|
| **Claude** (you, everywhere) | macOS/Linux `~/.claude/skills/` · Windows `%USERPROFILE%\.claude\skills\` |
| **Claude** (one project) | `<project>/.claude/skills/` |
| **claude.ai** | Upload the folder as a skill in settings |
| **Codex** | Anywhere in the project; point at it from `AGENTS.md` |
| **Cursor / Windsurf** | Anywhere in the project; point at it from `.cursor/rules/` |

```bash
# macOS / Linux
cp -r business-problem-sharpener ~/.claude/skills/
```

```powershell
# Windows PowerShell
Copy-Item -Recurse business-problem-sharpener $env:USERPROFILE\.claude\skills\
```

For Codex, the block the installer generates looks like this — paste it into
`AGENTS.md` yourself if you prefer:

```markdown
## AI-architect skills

Each file states when it applies. Before starting one of these tasks, read
the matching file and follow it.

- Sharpening a vague or solution-shaped business problem →
  `skills/business-problem-sharpener/SKILL.md`
- Designing evaluation — test sets, metrics, accuracy targets →
  `skills/eval-harness-designer/SKILL.md`
- Choosing between technical approaches →
  `skills/architecture-tradeoff-analyst/SKILL.md`
- Reviewing or stress-testing a proposed design →
  `skills/architecture-red-team/SKILL.md`
- Building an ROI or business case →
  `skills/roi-scenario-model/SKILL.md`
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
