# The brand profile

The profile is the thing the person approves. It is also the input the
generated skill is written from, so anything missing here is missing from
every document the company produces afterwards.

`scripts/brand_profile.py --example` prints a starter file;
`--check` validates it and contrast-tests every declared pairing.

## Fields

```json
{
  "company": "Columbus",
  "slug": "columbus",
  "sources": ["what you read, and what each settled"],
  "colors": {
    "primary":   {"hex": "#1B1474", "use": "Headings, primary buttons, the mark"},
    "surface":   {"hex": "#FFFFFF", "use": "Page and slide background"},
    "ink":       {"hex": "#1C1C28", "use": "Body text"},
    "muted":     {"hex": "#5B5B6B", "use": "Secondary text, captions"},
    "accent":    {"hex": "#DCDDF6", "use": "Fills, chips, quiet emphasis"}
  },
  "pairings": [
    {"name": "Body text on page", "fg": "#1C1C28", "bg": "#FFFFFF"},
    {"name": "Heading on page",   "fg": "#1B1474", "bg": "#FFFFFF", "large_text": true}
  ],
  "typography": {
    "heading": {"family": "Fraunces", "fallback": "Georgia, serif"},
    "body":    {"family": "Inter",    "fallback": "system-ui, Arial, sans-serif"}
  },
  "logo": {
    "files": ["assets/logo-primary.svg", "assets/logo-reverse.svg"],
    "clear_space": "Half the mark's height on every side",
    "min_width_px": 120,
    "on_dark": "Use logo-reverse.svg — never recolour the primary mark",
    "never": ["Recolour", "Stretch or skew", "Add effects", "Place on a busy photo"]
  },
  "voice": {
    "traits": ["Direct", "Evidence-led", "Plain about trade-offs"],
    "avoid": ["Hype adjectives", "Vague futurism", "Exclamation marks"],
    "samples": ["A real sentence taken verbatim from their own material"]
  },
  "values": [
    {"value": "Transparency", "means_in_output": "State the cost and the caveat in the same paragraph as the benefit"}
  ]
}
```

`company`, `slug`, `colors`, `typography` and `logo` are required. `slug`
becomes the generated skill's folder name and frontmatter `name`, so it must
be lowercase letters, digits and single hyphens.

## Colour roles

Five roles carry almost every document. Add more only when the company
genuinely uses them.

| Role | What it is for |
| --- | --- |
| `primary` | The colour someone would name if asked for the brand colour |
| `surface` | What the page or slide sits on |
| `ink` | Body text on `surface` |
| `muted` | Captions, secondary text, axis labels |
| `accent` | Quiet fills — chips, highlights, table headers |

Optional, when real: `primary_dark` (hover and pressed states), `success` /
`warning` / `danger` (status), `chart_1`–`chart_n` (a derived categorical
scale — see below).

A hex without a role gets applied at random by whoever loads the skill later.

## Pairings

Every combination of text on background that the generated skill will tell
someone to use, checked with `--check`. At minimum:

- body text on surface
- heading on surface
- text on primary (button labels, filled table headers)
- caption or muted text on surface
- text on accent, if accent is ever used as a fill behind text

WCAG AA is 4.5:1 for normal text and 3:1 for large text (18pt+, or 14pt+
bold). Mark large-text pairings with `"large_text": true` so they are judged
against the right threshold.

If a pairing the company actually uses fails, do not quietly fix it and do
not quietly ship it. Record it, name the accessible alternative, and raise it
at the approval gate — it is their brand and their decision, but they should
make it knowingly.

## Charts

Brand palettes make poor categorical scales. They are picked to contrast with
a background, not with each other, and two brand colours of similar lightness
are indistinguishable in a pie chart and identical in greyscale.

If the company has no data-viz palette, derive one and label it derived:
start from `primary`, then pick colours that differ in **hue and lightness**,
checking each against the others rather than against the background. Five or
six is the practical ceiling; past that, the chart needs a different form, not
more colours.

## Voice

Three traits maximum, each with a prohibition, and at least one verbatim
sample from the company's own material. A trait without a sample is an
adjective, and adjectives do not survive into generated text.

The strongest voice records are the negative ones: "never opens with a
rhetorical question", "no exclamation marks", "does not use 'leverage' as a
verb". They are checkable, where "professional yet approachable" is not.

## Values

Each value needs a `means_in_output` that constrains something concrete. Test
it: could two different writers apply this and produce visibly different
work? If yes, it is not specific enough yet.

| Value | Weak | Usable |
| --- | --- | --- |
| Transparency | "We are transparent" | "State the cost and the caveat in the same paragraph as the benefit" |
| Craft | "We care about quality" | "No placeholder text or lorem ipsum in anything shown to a client" |
| Partnership | "We work with our clients" | "Write in second person about their situation, not third person about ours" |

A value that cannot be made usable belongs in the profile as context, not in
the generated skill as an instruction.

## Marking extracted versus inferred

Every value carries one of three provenances, and the profile shows which:

- **Extracted** — read out of a file. `#1B1474` from `theme1.xml`.
- **Inferred** — derived, sampled, or chosen between conflicting sources.
- **Proposed** — a sensible default for something no source covered, such as
  logo clear space.

The person approving reads quickly. Provenance is what stops them
accepting your guesses at the same speed as your findings.
