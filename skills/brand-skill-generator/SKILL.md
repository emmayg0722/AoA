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

## Three rules

**1. A question the artefacts can answer is a bug, not diligence.**

If someone hands you a deck and you ask them for their logo, you have wasted
their time — the logo is inside the file, on the slide master. Same for the
company name, the fonts, and which accent colours are real. Work the derive-first
list below to exhaustion before you write a single question.

| Do not ask | Derive it from |
| --- | --- |
| The logo | `--extract-media` from a deck, `--from-html` from a site — both rank candidates |
| Company name | `--from-html` reads `og:site_name` / `<title>`; a deck's title slide has it too |
| Which accents are real | `--from-pptx` counts how often each theme slot is actually painted |
| Heading and body fonts | The theme's `majorFont` / `minorFont` |
| Whether fonts are a brand choice | If the theme matches a stock Office default, they are not |
| Voice and values | The site's About page and the LinkedIn boilerplate |

**2. Never ask permission to do the work.**

Being handed a `.pptx` *is* the instruction to read it. "Shall I proceed with
extraction from the .pptx now?" is not a courtesy — it is a turn spent asking
whether to do the thing you were invoked for, and the only possible answer is
yes. Run the commands, then report what came out.

The same goes for "shall I look at the website you gave me", "would you like
me to check the logo colours", and every other variant. If the answer to your
question is obviously yes, it was not a question.

Ask before doing only when an action is destructive, costs the person money,
or sends their data somewhere. Reading files they handed you is none of those.

**3. Extract, then ask. Never infer a brand and ship it in one move.**

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

### 2. Run the extraction now

Not "offer to". Run it, in this turn, for every input that arrived. Guessing
colours from a screenshot is the failure this skill exists to prevent, and
`scripts/brand_profile.py` reads the real values with nothing but the standard
library — there is no cost to running it and no reason to ask first.

Map inputs to commands and work the list:

| They gave you | Run |
| --- | --- |
| `.pptx` / `.potx` | `--from-pptx`, then `--extract-media` |
| `.docx` / `.dotx` | Same ZIP structure — see `references/extraction.md` |
| A website URL | Save the page, then `--from-html`, then `--from-css` on its stylesheet |
| `.svg` logo | `--from-svg` |
| `.png` / `.jpg` logo | Check the deck and site for a vector first |
| A LinkedIn URL | Read the About text — voice and values, no colours |

```bash
python scripts/brand_profile.py --from-pptx template.potx        # colours, fonts, real slot usage, media
python scripts/brand_profile.py --extract-media template.potx --out assets/   # write the logo out
python scripts/brand_profile.py --from-svg logo.svg              # every colour the mark paints with
python scripts/brand_profile.py --from-html homepage.html        # logo candidates, company name, theme colour
python scripts/brand_profile.py --from-css site.css              # custom properties, palette, font stacks
python scripts/brand_profile.py --contrast "#1B1474" "#FFF"      # WCAG ratio for one pairing
```

Three things `--from-pptx` reports that decide how much of the deck is real:

- **Slot usage.** `accent1 used 8×` versus `accent3 never used — template
  leftover` answers which accents are the brand's, without asking.
- **Stock-theme detection.** If the palette and fonts match an Office default,
  it says so. A template using Aptos and Microsoft's stock accents has not
  been branded at all, and treating those values as the company's colours is
  the single easiest way to produce a confidently wrong skill.
- **Where each image is used.** An image on the slide master is the logo; an
  image on one slide is a photo. `--extract-media` writes them out, candidates
  first.

`references/extraction.md` has the per-source detail — where OOXML hides theme
colours, how to handle a raster-only logo, what to pull from a site when you
cannot download its CSS, and what to read off a LinkedIn page. Read it when a
source does not yield to the script.

If Python is unavailable, the same file formats are still readable by hand:
a `.pptx` is a zip, and `ppt/theme/theme1.xml` holds the palette. The
reference explains it.

### 2b. If a website was provided, it is the reference

A live site outranks everything else, because it is what the company ships
today rather than what someone approved four years ago. When you are given a
URL, work it properly rather than treating it as one source among several:

- **Palette and type** from the stylesheet — custom properties first.
- **Company name and descriptor** from the `<title>` and the header.
- **Voice** from the About page: take two or three sentences verbatim.
- **Values** from wherever they state them, then push each one until it
  constrains a sentence.
- **Logo** — save the page and run `--from-html`. It ranks candidates, and
  the ranking matters: a favicon is *evidence* of a logo, not a logo. The
  header `<img>` or inline `<svg>`, then `mask-icon` (always vector), then the
  apple-touch-icon, then `og:image`, then the 32px favicon last. The
  favicon-extractor libraries on GitHub stop at `<link rel="icon">`, which is
  why they hand back a 32px square when you wanted the wordmark.

Anything the site settles is settled. Do not then ask the person for it, and
do not let a deck template overrule it — say which one you followed instead.

If you cannot fetch the site, say so explicitly rather than silently falling
back to the deck. That is a gap the person can close in one paste.

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

Before you write a single question, every one of these must already be true.
If one is not, you are not at this step yet — go back and run it.

- [ ] Every input that arrived has been run through its command: a deck
      through `--from-pptx` **and** `--extract-media`, a site through
      `--from-html` and `--from-css`, a logo through `--from-svg`.
- [ ] You have the extracted logo files on disk, and you know which one is
      the primary mark and why.
- [ ] You know which theme slots are actually used, and whether the template
      is an unmodified Office default.
- [ ] `--check` passes on the profile.
- [ ] `--swatch` has been written.

A question written before this checklist is complete is a question the files
were about to answer.

Present three things:

- **A swatch sheet they can look at.** Not optional, and not a table of hex
  codes — `#1B1474` is meaningless to almost everyone, so an approval built on
  it is not really an approval.

  ```bash
  python scripts/brand_profile.py --swatch brand.json --out swatches.html
  ```

  It renders each colour as a block with its plain-English name ("deep
  indigo"), the logo on both light and dark, the type at heading and body
  size, and every text pairing rendered as real text on its real background
  with failures in red. Give them the file and tell them to open it.

- **The profile itself**, with extracted, inferred and proposed marked.

- **Your open questions** — only the ones the artefacts genuinely could not
  settle. Before writing any question, check it against the derive-first table
  in the rules above. These are legitimate:

  > 1. Accent 1 in your template is a warm orange, used on two slides but
  >    nowhere on your site. Still in use, or legacy?
  > 2. Aptos is Microsoft's default font, so your template was never branded.
  >    Do you have a real typeface, or shall the skill use the site's stack?
  > 3. Your About page lists three values. Which one should actually change
  >    how a document reads?

  These are bugs:

  - *"Can you send me your logo?"* — you were handed a deck; it is on the
    slide master. Extract it, show it, and only then ask for what is missing.
  - *"Shall I proceed with extraction from the .pptx?"* — see rule 2.
  - *"Is this the company name?"* — it is on the title slide and in the site's
    `<title>`.
  - *"Do you have a website?"* — they gave you the URL.

  A logo question becomes legitimate once you have shown what you already
  found, and it names the specific gap rather than asking for everything:

  > I pulled your logo off the slide master — it is a 3 KB PNG, so it will
  > blur above about 300px wide. Do you have the SVG? And I found no
  > light-on-dark variant anywhere; is there one, or shall the skill say to
  > keep the logo on light backgrounds only?

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

On Claude Code the folder name becomes a slash command, so once
`~/.claude/skills/columbus/` exists the person types **`/columbus`** to invoke
it deliberately — and it also triggers on its own from the description. Keep
the slug short and typeable for exactly this reason; `columbus` is a good
command, `columbus-brand-guidelines-2026` is not. Codex and Cursor have no
slash commands for skills, so there the wiring file is what makes it load.

Tell the person the command in the same message as the install path. A skill
nobody knows how to call is a skill nobody calls.

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
[The files you extracted and where each came from — "logo-primary.png, pulled
from the slide master" — then clear space, minimum size, and what must never
happen to it. If you are showing a logo here, you cannot also be asking for
one below.]

## Voice
[Traits, things to avoid, one rewritten sentence showing the difference]

## Values, and what each one changes about the output
[Value → the concrete effect on writing or design. A value that changes
nothing is decoration; drop it.]

## Conflicts I resolved
[Each disagreement between sources, and which won]

## Questions before I generate the skill
[Numbered, each answerable in a word. Every one has survived this test: the
files I was given cannot answer it, and the answer is not obviously yes.
Three or four is normal. If you have written more than five, you skipped
step 2.]

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
