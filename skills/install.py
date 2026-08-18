#!/usr/bin/env python3
"""Install the AI-architect agent skills for Claude, Codex or Cursor.

Works the same on macOS, Linux and Windows. Standard library only — the same
rule the skills themselves follow, so nothing needs installing to install.

    python3 install.py --list                      # what is available
    python3 install.py --agent claude              # all skills, just for you
    python3 install.py --agent claude --project .  # committed to a project
    python3 install.py --agent codex --project .   # copies + wires AGENTS.md
    python3 install.py --agent cursor --project .  # copies + writes a rule file
    python3 install.py --agent claude --skill roi-scenario-model
    python3 install.py --agent codex --project . --dry-run

Where things go:

    claude, no --project   ~/.claude/skills/<skill>/
    claude, --project DIR  DIR/.claude/skills/<skill>/
    codex,  --project DIR  DIR/skills/<skill>/  + a block in DIR/AGENTS.md
    cursor, --project DIR  DIR/skills/<skill>/  + DIR/.cursor/rules/

On Windows ~ resolves to %USERPROFILE%, so the Claude path is
%USERPROFILE%\\.claude\\skills — no separate command needed.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Markers let the AGENTS.md / rule-file block be rewritten on re-install
# without touching anything else the file already contains.
START = "<!-- ai-architect-skills:start -->"
END = "<!-- ai-architect-skills:end -->"

# One line per skill for the generated wiring. Kept here rather than parsed
# out of each SKILL.md so the phrasing stays short and task-shaped — the
# frontmatter description is written for matching, not for a menu.
WHEN = {
    "business-problem-sharpener":
        "Sharpening a vague or solution-shaped business problem, or "
        "classifying an AI use case",
    "eval-harness-designer":
        "Designing evaluation — test sets, metrics, accuracy targets, or "
        "diagnosing why quality dropped",
    "architecture-tradeoff-analyst":
        "Choosing between technical approaches — RAG vs fine-tune, managed "
        "vs self-hosted, agent vs pipeline, build vs buy",
    "architecture-red-team":
        "Reviewing or stress-testing a proposed design before it ships",
    "roi-scenario-model":
        "Building an ROI case, business case, payback or TCO for an AI "
        "initiative",
}


def discover():
    """Every folder next to this script holding a SKILL.md."""
    return sorted(p.name for p in HERE.iterdir()
                  if p.is_dir() and (p / "SKILL.md").is_file())


def describe(name):
    """First line of the skill's description, for --list."""
    text = (HERE / name / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^description:\s*>-?\s*\n((?:\s{2,}.*\n)+)", text, re.M)
    if not m:
        m = re.search(r"^description:\s*(.+)$", text, re.M)
        return m.group(1).strip() if m else ""
    body = " ".join(line.strip() for line in m.group(1).splitlines())
    return body.split(". ")[0].strip().rstrip(".") + "."


def target_dir(agent, project):
    if agent == "claude":
        base = (project / ".claude" / "skills") if project else (
            Path.home() / ".claude" / "skills")
    else:
        # Codex and Cursor read files by path, so the skills live in the
        # project and the wiring file points at them.
        base = project / "skills"
    return base


def copy_skills(names, dest, force, dry):
    installed, skipped = [], []
    for name in names:
        src, dst = HERE / name, dest / name
        if dst.exists() and not force:
            skipped.append(name)
            continue
        if not dry:
            if dst.exists():
                shutil.rmtree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            # Skip caches so a local run does not ship __pycache__.
            shutil.copytree(src, dst,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        installed.append(name)
    return installed, skipped


def wiring_block(names, skills_rel):
    lines = [START,
             "## AI-architect skills",
             "",
             "Each file states when it applies. Before starting one of these "
             "tasks, read the matching file and follow it.",
             ""]
    for name in names:
        lines.append("- %s →" % WHEN.get(name, "Working with `%s`" % name))
        lines.append("  `%s/%s/SKILL.md`" % (skills_rel, name))
    lines.append(END)
    return "\n".join(lines)


def write_block(path, block, dry):
    """Insert or replace the marked block, leaving the rest of the file
    alone. Re-running the installer must not duplicate or clobber."""
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if START in existing and END in existing:
        updated = re.sub(re.escape(START) + r".*?" + re.escape(END),
                         block, existing, flags=re.S)
        action = "updated"
    elif existing.strip():
        updated = existing.rstrip() + "\n\n" + block + "\n"
        action = "appended to"
    else:
        updated = block + "\n"
        action = "created"
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(updated, encoding="utf-8")
    return action


def main():
    ap = argparse.ArgumentParser(
        description="Install the AI-architect agent skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Where things go:")[1])
    ap.add_argument("--agent", choices=("claude", "codex", "cursor"),
                    help="which agent to install for")
    ap.add_argument("--project", type=Path,
                    help="project directory; required for codex and cursor")
    ap.add_argument("--skill", action="append", dest="skills",
                    help="install just this skill; repeatable")
    ap.add_argument("--force", action="store_true",
                    help="overwrite skills that are already installed")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would happen, change nothing")
    ap.add_argument("--list", action="store_true",
                    help="list the available skills and exit")
    args = ap.parse_args()

    available = discover()
    if not available:
        raise SystemExit("No skills found next to %s" % HERE)

    if args.list or not args.agent:
        print("Available skills (%d):\n" % len(available))
        for name in available:
            print("  %s" % name)
            print("      %s\n" % describe(name))
        if not args.agent:
            print("Pick a target, e.g.:")
            print("  python3 install.py --agent claude")
            print("  python3 install.py --agent codex --project .")
        return 0

    names = args.skills or available
    unknown = [n for n in names if n not in available]
    if unknown:
        raise SystemExit("Unknown skill(s): %s\nAvailable: %s"
                         % (", ".join(unknown), ", ".join(available)))

    if args.agent in ("codex", "cursor") and not args.project:
        raise SystemExit(
            "--project is required for %s: it reads files by path, so the "
            "skills have to live inside the project.\n"
            "  python3 install.py --agent %s --project ."
            % (args.agent, args.agent))

    project = args.project.resolve() if args.project else None
    if project and not project.is_dir():
        raise SystemExit("Not a directory: %s" % project)

    dest = target_dir(args.agent, project)
    dry = args.dry_run
    tag = "[dry run] " if dry else ""

    installed, skipped = copy_skills(names, dest, args.force, dry)
    print("%s%d skill(s) → %s" % (tag, len(installed), dest))
    for n in installed:
        print("    + %s" % n)
    if skipped:
        print("  %d already installed (use --force to overwrite):" % len(skipped))
        for n in skipped:
            print("    · %s" % n)

    if args.agent in ("codex", "cursor"):
        try:
            skills_rel = dest.relative_to(project).as_posix()
        except ValueError:
            skills_rel = dest.as_posix()
        # List everything actually present in the destination, not just what
        # this run touched — installing one skill at a time must not drop the
        # others from the wiring file.
        present = sorted(d.name for d in dest.iterdir()
                         if d.is_dir() and (d / "SKILL.md").is_file()) \
            if dest.is_dir() else sorted(set(installed + skipped))
        block = wiring_block(present, skills_rel)
        if args.agent == "codex":
            path = project / "AGENTS.md"
        else:
            path = project / ".cursor" / "rules" / "ai-architect.md"
        action = write_block(path, block, dry)
        print("%s%s %s" % (tag, action, path))

    if not dry:
        print("\nDone.", end=" ")
        if args.agent == "claude":
            print("Start a new session; Claude picks the skills up "
                  "when a request matches one.")
        else:
            print("The wiring file points at the skills — no other setup.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
