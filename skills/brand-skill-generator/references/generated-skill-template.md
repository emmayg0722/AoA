# What the generated company skill looks like

The artefact this whole workflow produces. Fill it from the approved brand
profile, substituting the company's real values everywhere `[Company]` and
`[slug]` appear.

## Layout

```
[slug]/
├── SKILL.md
├── assets/
│   ├── logo-primary.svg
│   ├── logo-reverse.svg
│   └── template.potx          # if they have one
└── references/
    ├── palette.md
    └── voice.md
```

Copy the real files into `assets/`. A skill that points at a path on the
machine where it was generated breaks the moment somebody installs it
elsewhere, and it breaks silently — the output just comes out logo-less.

Keep `SKILL.md` short. Colour tables and voice examples belong in
`references/`, which loads only when needed.

## SKILL.md

````markdown
---
name: [slug]
description: >-
  Apply [Company]'s brand to anything being produced — decks, documents,
  HTML pages, reports, charts, emails. Use whenever output is for [Company]
  or its clients, whenever someone asks to make something "on-brand", and
  whenever a deck, document, page or chart is being created without another
  brand having been specified. Covers the colour palette and where each
  colour goes, heading and body typefaces with fallbacks, logo placement and
  the rules for using it, the writing voice, and the values that change how
  copy reads.
---

# [Company] brand

Apply this whenever you are producing something that carries [Company]'s
name. If another brand has been specified for a piece of work, that one wins.

## Colours

| Role | Hex | Use |
| --- | --- | --- |
| Primary | `#______` | Headings, primary buttons, the mark |
| Surface | `#______` | Page and slide background |
| Ink | `#______` | Body text |
| Muted | `#______` | Captions, secondary text |
| Accent | `#______` | Fills, chips, quiet emphasis |

Tested pairings — these are safe for text:

| Pairing | Ratio |
| --- | --- |
| Ink on Surface | __:1 |
| White on Primary | __:1 |

Never put [any pairing that failed] together; use [the alternative] instead.

Full palette, including the derived chart scale: `references/palette.md`.

## Typography

- Headings: **[Family]**, falling back to `[fallback stack]`
- Body: **[Family]**, falling back to `[fallback stack]`

[If the typeface is licensed but not embeddable, say so here, and say which
fallback to use rather than letting it resolve at random.]

## Logo

- Light backgrounds: `assets/logo-primary.svg`
- Dark backgrounds: `assets/logo-reverse.svg`
- Clear space: [rule]. Minimum width: [n]px.
- Never: recolour it, stretch it, add effects, or place it on a busy
  photograph.

Place it [where the company actually places it — bottom-right of slides,
top-left of documents].

## Voice

[Three traits.] Avoid [the prohibitions].

How it sounds:

> [A verbatim sentence from their own material.]

Not:

> [The same point written the way they would not write it.]

More, with worked rewrites: `references/voice.md`.

## What the values change

- **[Value]** → [the concrete effect on the writing]
- **[Value]** → [the concrete effect on the writing]

## Applying it

**Slides** — start from `assets/template.potx` if present rather than
restyling a blank deck. Headings in the heading face at the template's size,
body in the body face, logo [where], accent fills for shapes rather than
default Office colours.

**Documents** — heading face for headings only, body face throughout,
[Company] primary for headings and rules, ink for body.

**HTML** — declare the palette as custom properties at `:root` so the whole
page inherits it, and give every face a real fallback stack.

**Charts** — use the derived chart scale in `references/palette.md`, not the
brand palette. Brand colours are chosen to contrast with a background, not
with each other.
````

## references/palette.md

Every colour with role, hex, and where it goes. The full contrast table for
all tested pairings. The derived chart scale, labelled as derived. Any colour
the company uses that fails contrast, with the accessible alternative next to
it.

## references/voice.md

The traits and prohibitions, three or more verbatim samples, and two or three
before/after rewrites showing a generic sentence turned into one that sounds
like the company. Rewrites teach more than adjectives.

## The slug is a command

On Claude Code the skill's folder and frontmatter `name` become a slash
command: a skill installed at `~/.claude/skills/columbus/` is invoked by
typing `/columbus`. Pick the slug accordingly — short, lowercase, the word the
person would actually type. `columbus` is a good command; `columbus-brand-v2`
is one nobody will type twice.

The skill still triggers on its own from the description; the slash command is
for when someone wants it deliberately. Both matter, so do not trade a good
description for a good slug.

Hand over the command with the path, in the same message:

> Copy the folder to `~/.claude/skills/columbus/`, then type `/columbus` in
> Claude Code — or just ask for a deck and it will apply itself.

Codex and Cursor have no slash commands for skills. There the wiring file
(`AGENTS.md` or a rule file) is what makes the skill load, so say that instead
of promising a command that does not exist.

## Description quality

The description is the only part always in context, so it is the only part
that decides whether the skill fires at all. A skill that triggers on
"use the [Company] brand" and nothing else will be ignored exactly when it
matters — someone asks for a deck, gets a generic deck, and never learns the
skill existed.

List the artefact types by name: decks, slides, documents, reports, HTML
pages, landing pages, emails, charts, proposals. Include the implicit case:
output for this company where no brand was named.

## Before handing it over

- Every asset path resolves inside the skill folder.
- Every hex in `SKILL.md` matches the approved profile.
- No pairing recommended for text failed `--check`.
- The description names the artefact types, not just the brand.
- One smoke test run, and its output looked at.
