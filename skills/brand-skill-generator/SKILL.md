---
name: brand-skill-generator
description: >-
  Distil a company's real brand out of the artefacts it already has — a
  PowerPoint template, a logo file, the website, the LinkedIn page, a brand PDF
  — into an approved brand profile, then generate a named, installable agent
  skill for that company so every later deck, document, page or chart comes out
  in its colours, its typefaces, its logo rules and its voice. Use whenever
  someone wants their own or a client's branding applied to future output, says
  "make our output look like us", "use our brand", "here is our template and
  logo", "build a skill for my company", "keep everything on-brand", or hands
  over brand files and asks what can be done with them. Use it before producing
  branded work rather than after, because a brand guessed from one screenshot
  is wrong in ways nobody notices until a client sees it. The generated skill is
  always shown for approval before it is written, since a brand profile inferred
  from artefacts is a hypothesis until the person who owns the brand confirms it.
---

# Brand skill generator

You are turning scattered brand artefacts into one reusable thing: a skill,
named after the company, that any later session can load to produce work that
looks and sounds like it came from that company.

Two outputs, in this order, never merged:

1. **A brand profile** — what you extracted, what you inferred, and what you
   could not determine. Shown to the person for approval.
2. **The company skill** — a folder named after the company, generated only
   after that approval, plus the instructions to install it.

## The rule that does the work

**Extract, then ask. Never infer a brand and ship it in one move.**

Everything in the profile is either something you read out of a file, or
something you guessed. Those two things must be visibly different to the
person reviewing it, because they will accept the whole document at a glance
and only your labelling protects them from accepting your guesses too.

A logo's PNG has no "primary colour" field; you sampled it. A website's CSS
has forty greys; you picked one. The deck template and the site disagree; you
chose. Each of those is a question, not a finding — and the person whose brand
it is answers them in seconds, where you would spend the whole engagement
being subtly wrong.

## Workflow

### 1. Inventory what you were actually given

List the sources before touching them, and say what each one can and cannot
settle:

| Source | Settles | Cannot settle |
| --- | --- | --- |
| `.pptx` / `.potx` template | Theme colours, theme fonts, slide layouts | Which accent is "the" brand colour |
| Logo `.svg` | Exact mark colours, shapes | Clear space, minimum size, misuse rules |
| Logo `.png` / `.jpg` | Approximate colours | Exact hex, transparency behaviour |
| Website | Live palette, font stacks, real hierarchy | What is brand versus what is theme default |
| LinkedIn / About page | Voice, values, boilerplate, proof points | Any colour value |
| Brand PDF / guidelines | Stated rules, clear space, misuse | Whether anyone follows it |

Name the gaps now. "No brand guidelines document, so logo clear space is a
guess" is a line in the profile, not a silent omission.

### 2. Read the values out of the files

Guessing colours from a screenshot is the failure this skill exists to
prevent. `scripts/brand_profile.py` reads the real values, standard library
only:

```bash
python scripts/brand_profile.py --from-pptx template.potx   # theme colours, fonts, embedded media
python scripts/brand_profile.py --from-svg logo.svg         # every colour the mark paints with
python scripts/brand_profile.py --from-css site.css         # custom properties, palette, font stacks
python scripts/brand_profile.py --contrast "#1B1474" "#FFF" # WCAG ratio for one pairing
```

`references/extraction.md` has the per-source detail — where OOXML hides theme
colours, how to handle a raster-only logo, what to pull from a site when you
cannot download its CSS, and what to read off a LinkedIn page. Read it when a
source does not yield to the script.

If Python is unavailable, the same file formats are still readable by hand:
a `.pptx` is a zip, and `ppt/theme/theme1.xml` holds the palette. The
reference explains it.

### 3. Resolve the conflicts out loud

The deck, the site and the logo will disagree — usually because the deck is
four years old and the site was redesigned. Do not average them and do not
quietly prefer one.

Rank sources by how recently the company actually used them: **live website >
current logo file > deck template > brand PDF**. Then record each conflict as
a line the person can overrule:

> Primary blue is `#1B1474` on the website but `#241C7A` in the deck template.
> Used the website value. The template is the older of the two.

### 4. Build the brand profile

Fill the structure in `references/brand-profile-format.md`. Every colour gets
a role and a use, not just a hex. Every pairing of text on background gets a
contrast check — a brand skill that tells people to put a mid-grey caption on
white is worse than no brand skill, because it launders an accessibility
failure as a corporate standard.

```bash
python scripts/brand_profile.py --example > brand.json   # starter profile
python scripts/brand_profile.py --check brand.json       # validate + contrast-test every pairing
```

`--check` exits non-zero if a pairing fails WCAG AA. Fix it, or record it in
the profile as decorative-only with the accessible alternative named. Do not
pass a failing profile to the next step.

### 5. Align with the person — the approval gate

**Stop here. Do not generate the skill yet.**

Present three things:

- **The profile itself**, with extracted and inferred clearly marked.
- **A swatch preview** — a small HTML or Markdown block showing the palette,
  the type at heading and body size, and the logo on both light and dark, so
  they are approving something they can see rather than a table of hex codes.
- **Your open questions**, as a short numbered list. Ask only what you
  genuinely could not determine, and make each one answerable in a word:

  > 1. Accent 1 in your template is a warm orange, but it appears nowhere on
  >    the site. Still in use, or legacy?
  > 2. Is Poppins licensed for the client's use, or should the generated skill
  >    specify the fallback as primary?
  > 3. Three values on your About page. Which one should actually change how
  >    a document reads?

Then wait. Explicit approval, not silence, and not "looks good" to a message
that contained five questions. If they answer some questions and ignore
others, ask the rest — an unanswered question becomes a wrong default baked
into every document the company produces from here.

### 6. Generate the company skill

Only now. Create a folder named with the company slug, laid out to the Agent
Skills convention so it installs anywhere:

```
columbus/
├── SKILL.md                  # frontmatter + how to apply the brand
├── assets/                   # the real files: logo variants, template
│   ├── logo-primary.svg
│   ├── logo-reverse.svg
│   └── template.potx
└── references/
    ├── palette.md            # colours, roles, tested pairings
    └── voice.md              # voice, values, worked examples
```

`references/generated-skill-template.md` carries the full skeleton to fill in,
including the frontmatter description — which matters more than the body,
since it is what makes the skill trigger at all. Write it so it fires on
"make a deck", "write the client email", "build the landing page", not only on
"use the Columbus brand".

Copy the real asset files in. A generated skill that references
`/Users/someone/Downloads/logo.svg` is broken the moment it is installed
anywhere else.

### 7. Install it, then prove it works

Give the exact path for the agent they use:

| Agent | Where the folder goes |
| --- | --- |
| Claude (personal) | `~/.claude/skills/columbus/` |
| Claude (one project) | `<project>/.claude/skills/columbus/` |
| Codex | `~/.codex/skills/columbus/`, then point `AGENTS.md` at it |
| Cursor | `~/.cursor/skills/columbus/`, then a rule file that names it |

Then run one smoke test and look at the result together: *"Make a one-slide
title deck for Columbus"* or *"Build a one-page HTML overview."* Check the
things that actually break — logo on the right background, heading typeface
resolving rather than silently falling back, the primary colour matching the
site rather than the old template.

A generated skill nobody has run once is not finished.

## Output template

Use this for the profile at step 5.

## Brand profile — [Company]

**Sources used**
[Each file or URL, and what it settled]

**What I could not determine**
[The gaps, and what each one would take to close]

## Colours
| Role | Hex | Use | Source | Extracted or inferred |

## Tested pairings
| Pairing | Ratio | Verdict |

## Typography
[Heading and body, with fallbacks, and the licensing position]

## Logo
[Variants, clear space, minimum size, what must never happen to it]

## Voice
[Traits, things to avoid, one rewritten sentence showing the difference]

## Values, and what each one changes about the output
[Value → the concrete effect on writing or design. A value that changes
nothing is decoration; drop it.]

## Conflicts I resolved
[Each disagreement between sources, and which won]

## Questions before I generate the skill
[Numbered, each answerable in a word]

## What separates a real brand skill from a colour list

**Values must cash out into behaviour.** "Innovation" in a values list changes
nothing. "We say what a thing costs before we say what it does" changes every
paragraph. Push each stated value until it constrains an actual sentence, or
leave it out — a generated skill full of nouns produces output that ignores
them.

**The logo needs rules, not just a file.** Most brand damage is a stretched
mark, a recoloured mark, or a mark on a background it was never meant for. The
generated skill says what must never happen to it, and ships the reverse
variant so nobody improvises one.

**Colour needs roles.** A palette of six hexes with no roles gets applied at
random. `primary`, `surface`, `ink`, `muted`, `accent` tell a later session
where each one goes — and which two may sit on top of each other.

**Charts are where brands break.** Brand colours make poor categorical scales:
they are chosen for contrast against a background, not against each other. If
the company has no data-viz palette, say so in the generated skill and give a
derived one rather than letting six brand colours become six series colours.

## Traps

- **Sampling a JPEG.** Compression shifts colour. A hex sampled from a JPEG
  logo is close, not correct — mark it inferred and ask for the source file.
- **The template's accent 1 is not the brand colour.** PowerPoint's default
  theme ships accents that nobody chose. If an accent appears nowhere else,
  it is probably a leftover.
- **Fonts nobody licensed.** A generated skill that specifies a commercial
  typeface the client cannot embed produces documents that silently fall back.
  Record the fallback as a first-class choice.
- **Copying the brand PDF instead of the brand.** Guidelines documents
  describe an intent. The website is what the company actually ships.
- **Generating before approval.** The whole point of the gate. A skill built
  on unconfirmed inference gets installed, and then every later output is
  confidently wrong in the same way.
- **One skill per company, not per artefact.** If they hand you a second deck
  later, update the existing skill; do not generate `columbus-2`.

## Working with someone else's brand

Only generate a skill for a brand the person is entitled to use — their own
company, or a client they are working for. Extracting a brand from artefacts
you were given is ordinary consulting work; building a skill that reproduces a
third party's identity so output can pass as theirs is not. If the request
looks like the second, say so plainly and stop.

## Where this fits

This is a foundation skill rather than a phase skill: run it once at the start
of an engagement, and every deliverable afterwards — discovery readouts,
architecture blueprints, business cases, board decks — comes out in the
client's identity instead of a generic template. It pairs with any skill that
produces an artefact, and it replaces none of them: they decide what the
document says, this decides what it looks and sounds like.
