# Getting real values out of brand artefacts

Per-source recipes. Read the section for whichever source you are holding;
you rarely need all of them.

- [PowerPoint templates](#powerpoint-templates-pptx-potx)
- [Logos](#logos)
- [Websites](#websites)
- [LinkedIn and About pages](#linkedin-and-about-pages)
- [Word templates](#word-templates-docx-dotx)
- [Brand guideline PDFs](#brand-guideline-pdfs)
- [When you cannot extract anything](#when-you-cannot-extract-anything)

---

## PowerPoint templates (.pptx, .potx)

The single best colour source most companies have, because it is what their
own template actually applies. A `.pptx` is a ZIP of XML — no library needed.

```bash
python scripts/brand_profile.py --from-pptx template.potx
```

By hand, if Python is unavailable:

```bash
unzip -o template.potx -d unpacked
cat unpacked/ppt/theme/theme1.xml     # the palette and the fonts live here
ls -la unpacked/ppt/media/            # embedded images, logo usually among the smallest
```

### What the theme slots mean

Inside `<a:clrScheme>`, each slot holds either `<a:srgbClr val="1B1474"/>` or
`<a:sysClr lastClr="FFFFFF"/>`:

| Slot | Means |
| --- | --- |
| `dk1` / `lt1` | Primary text and background pair |
| `dk2` / `lt2` | Secondary text and background pair — the brand's dark tone often lives in `dk2` |
| `accent1`–`accent6` | Shape and chart colours, in the order the UI offers them |
| `hlink` / `folHlink` | Link colours |

`<a:fontScheme>` holds `<a:majorFont>` (headings) and `<a:minorFont>` (body),
each with a `<a:latin typeface="…"/>`.

### Cautions

- **Multiple themes.** A deck can carry `theme1.xml`, `theme2.xml` and more,
  one per slide master. The script reads the first; check the others if the
  colours look wrong for the slides you were shown.
- **Defaults masquerading as brand.** If accents 4–6 are Office's stock
  values and appear nowhere in the company's real material, they are
  leftovers. Say so rather than shipping them.
- **Overrides beat the theme.** A designer who typed a hex directly onto a
  shape produces a slide that does not match the theme. If the deck looks
  different from what the theme says, search the slide XML for `srgbClr`.

---

## Logos

### SVG — the good case

```bash
python scripts/brand_profile.py --from-svg logo.svg
```

Exact values, no sampling. Also read the file for structure: a mark built
from one path with one fill is easy to place on any background; a mark with
embedded raster images or filters is not, and the generated skill should say
so.

Check for `currentColor` — a logo using it inherits the surrounding text
colour, which is a feature worth documenting rather than replacing.

### PNG or JPEG — the common case

There is no reliable stdlib way to quantise a raster image, and guessing is
what this skill exists to avoid. Options, best first:

1. **Ask for the vector.** Most companies have one. One question beats an
   afternoon of sampling.
2. **Cross-reference.** If the site CSS or the deck theme already contains a
   colour that visibly matches the logo, use that value and note the
   cross-reference as the evidence.
3. **Sample and mark it inferred.** If Pillow or an image editor is available,
   sample the flat interior of each region — never an edge or a gradient, both
   of which are blended pixels. Record every sampled value as inferred.

Never sample a JPEG and present the result as exact: compression shifts
colour, especially at edges.

### Rules the file cannot tell you

Clear space, minimum size, and permitted backgrounds come from a guidelines
document or from asking. Sensible defaults to propose, clearly marked as
proposals:

- Clear space: half the mark's height on all sides
- Minimum width: 120px on screen, 25mm in print
- Reverse variant required on any background darker than roughly 50% luminance

---

## Websites

The most current source, because it is what the company ships today.

### If you can fetch the page

Look for, in this order:

1. **CSS custom properties.** `--brand-primary`, `--color-accent` and friends
   are the company naming its own palette. A named colour outranks a frequent
   one.
2. **`font-family` stacks.** Take the whole stack, not just the first entry —
   the fallbacks are part of the design decision.
3. **Favicon and `og:image`.** Often the cleanest logo assets on the site.
4. **Header and footer.** Where the primary colour and the logo lockup are
   used most deliberately.

```bash
python scripts/brand_profile.py --from-css site.css
```

### If you cannot fetch it

Ask for a screenshot of the homepage plus the "About" page, and treat every
colour you take from them as inferred. Say in the profile that the site was
not machine-readable.

### Caution

A site built on Tailwind, Bootstrap or a template ships a full framework
palette. Most of those greys are the framework's, not the brand's. The brand
colours are the ones that also appear in the logo or the deck.

---

## LinkedIn and About pages

These settle voice and values, never colour.

Read for:

- **The boilerplate.** The "About" paragraph a company repeats everywhere is
  its own summary of what it does. It is the single most useful sentence.
- **Sentence length and register.** Short and declarative, or long and
  qualified? First person plural, or third person?
- **What they claim as proof.** Client names, numbers, certifications,
  years — the evidence they reach for is part of the voice.
- **Stated values.** Usually three to five nouns. Nouns are not yet usable;
  the SKILL.md workflow covers pushing each one until it constrains a
  sentence.
- **What they never say.** A firm whose posts contain no exclamation marks
  and no hype adjectives has a voice rule worth recording as a prohibition.

Take two or three real sentences verbatim into the profile as voice samples.
A generated skill with worked examples produces better output than one with
adjectives.

---

## Word templates (.docx, .dotx)

Same ZIP trick as PowerPoint, different paths:

```bash
unzip -o template.dotx -d unpacked
cat unpacked/word/theme/theme1.xml    # same clrScheme/fontScheme structure
cat unpacked/word/styles.xml          # named styles: Heading 1, Body, Quote
ls unpacked/word/media/               # letterhead logo
```

`styles.xml` is worth reading even when the theme is uninformative: it shows
the real heading sizes and spacing the company uses in documents.

---

## Brand guideline PDFs

Useful for the rules a file cannot carry — clear space, misuse, tone of
voice, co-branding. Less reliable for colour, for two reasons: PDFs often
quote CMYK or Pantone rather than hex, and the document may predate the
current website by years.

If it quotes CMYK only, say so and ask for hex rather than converting: CMYK
to RGB conversion is profile-dependent and the answer you compute will not be
the one their designer uses.

---

## When you cannot extract anything

Sometimes all you get is "our colour is blue" and a JPEG business card. That
is still workable, as long as the profile is honest about it: mark everything
inferred, keep the palette small, propose values, and put the open questions
at the top rather than the bottom. The approval gate then does the work that
extraction could not.

What you must not do is produce a confident-looking profile from thin
evidence. The person reading it cannot tell the difference between a hex you
read out of their template and one you invented, unless you tell them.
