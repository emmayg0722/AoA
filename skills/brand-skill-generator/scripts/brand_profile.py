#!/usr/bin/env python3
"""Pull real brand values out of the files a client actually gave you.

Standard library only, like every script in this toolkit — no Pillow, no
python-pptx, no network. A .pptx is a zip of XML and an .svg is XML, so the
values are already reachable; the point of this script is that you read the
brand off the artefacts instead of eyeballing a screenshot and guessing.

    python brand_profile.py --from-pptx template.potx
    python brand_profile.py --from-svg logo.svg
    python brand_profile.py --from-css site.css
    python brand_profile.py --contrast "#1B1474" "#FFFFFF"
    python brand_profile.py --example > brand.json
    python brand_profile.py --check brand.json

--check is the one that matters before you hand a profile to anyone: it
validates the shape and runs WCAG contrast on every pairing the profile
claims is usable, so a brand skill cannot ship telling people to put grey
text on a white background.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

# OOXML's own names for the theme slots, in the order PowerPoint shows them.
# dk/lt are text and background pairs; accent1-6 are the chart and shape colours.
THEME_SLOTS = [
    ("dk1", "Text / dark 1"),
    ("lt1", "Background / light 1"),
    ("dk2", "Text / dark 2"),
    ("lt2", "Background / light 2"),
    ("accent1", "Accent 1"),
    ("accent2", "Accent 2"),
    ("accent3", "Accent 3"),
    ("accent4", "Accent 4"),
    ("accent5", "Accent 5"),
    ("accent6", "Accent 6"),
    ("hlink", "Hyperlink"),
    ("folHlink", "Followed hyperlink"),
]

HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")


# ── colour maths ─────────────────────────────────────────────────────────

def parse_hex(value):
    """'#1b1474', '1b1474' or '#abc' -> (r, g, b) as 0-255 ints."""
    v = str(value).strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", v):
        raise ValueError("not a hex colour: %r" % value)
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    """WCAG 2.x relative luminance."""
    channels = []
    for c in rgb:
        c = c / 255.0
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    """WCAG contrast ratio between two hex colours, 1.0 to 21.0."""
    l1 = relative_luminance(parse_hex(fg))
    l2 = relative_luminance(parse_hex(bg))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def contrast_verdict(ratio, large_text=False):
    """What the ratio is good for. Large text is 18pt+, or 14pt+ bold."""
    if large_text:
        if ratio >= 4.5:
            return "AAA (large text)"
        return "AA (large text)" if ratio >= 3.0 else "fails"
    if ratio >= 7.0:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    if ratio >= 3.0:
        return "AA large text only"
    return "fails"


# ── extraction ───────────────────────────────────────────────────────────

def _solid_colour(slot_el):
    """A theme slot holds either an explicit sRGB value or a system colour."""
    if slot_el is None:
        return None
    srgb = slot_el.find(A + "srgbClr")
    if srgb is not None and srgb.get("val"):
        return "#" + srgb.get("val").upper()
    sysclr = slot_el.find(A + "sysClr")
    if sysclr is not None and sysclr.get("lastClr"):
        return "#" + sysclr.get("lastClr").upper()
    return None


def from_pptx(path):
    """Theme colours, theme fonts and embedded media from a .pptx/.potx.

    The deck's theme is the most authoritative colour source a client has:
    it is what their own template actually applies, not what a brand PDF
    says it should apply.
    """
    if not zipfile.is_zipfile(path):
        raise SystemExit("%s is not a .pptx/.potx (not a zip archive)" % path)

    out = {"source": os.path.basename(path), "colors": {}, "fonts": {}, "media": []}
    with zipfile.ZipFile(path) as z:
        themes = sorted(n for n in z.namelist()
                        if n.startswith("ppt/theme/") and n.endswith(".xml"))
        if not themes:
            raise SystemExit("no ppt/theme/*.xml inside %s — is this a PowerPoint file?" % path)
        out["theme_part"] = themes[0]
        root = ET.fromstring(z.read(themes[0]))

        scheme = root.find(".//" + A + "clrScheme")
        if scheme is not None:
            for slot, label in THEME_SLOTS:
                value = _solid_colour(scheme.find(A + slot))
                if value:
                    out["colors"][slot] = {"hex": value, "role": label}

        fonts = root.find(".//" + A + "fontScheme")
        if fonts is not None:
            for key, tag in (("heading", "majorFont"), ("body", "minorFont")):
                group = fonts.find(A + tag)
                if group is not None:
                    latin = group.find(A + "latin")
                    if latin is not None and latin.get("typeface"):
                        out["fonts"][key] = latin.get("typeface")

        # Candidate logo files. Ordered by size: the logo is rarely the
        # biggest image in a deck, so show sizes and let a human pick.
        for info in z.infolist():
            if info.filename.startswith("ppt/media/"):
                out["media"].append({
                    "name": info.filename,
                    "bytes": info.file_size,
                })
        out["media"].sort(key=lambda m: m["bytes"])
    return out


def from_svg(path):
    """Every colour an SVG logo actually paints with.

    Covers presentation attributes (fill=, stroke=, stop-color=) and the
    same properties inside a style="" attribute, which is where exported
    logos usually hide them.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    counts = {}

    def add(value):
        value = value.strip()
        if not value or value.lower() in ("none", "transparent", "currentcolor", "inherit"):
            return
        m = HEX_RE.fullmatch(value) or HEX_RE.match(value)
        if not m:
            return
        key = "#" + m.group(1).upper()
        if len(key) == 4:  # expand #abc so counts do not split across notations
            key = "#" + "".join(c * 2 for c in key[1:])
        counts[key] = counts.get(key, 0) + 1

    for attr in ("fill", "stroke", "stop-color", "flood-color", "lighting-color"):
        for m in re.finditer(r'%s\s*=\s*"([^"]*)"' % attr, text):
            add(m.group(1))
        for m in re.finditer(r'%s\s*:\s*([^;"\'}]+)' % attr, text):
            add(m.group(1))

    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "source": os.path.basename(path),
        "colors": [{"hex": h, "occurrences": n} for h, n in ordered],
        "note": "Occurrence count is a hint, not a ranking — a one-use hex can "
                "still be the primary mark colour.",
    }


def from_css(path):
    """Hex colours and font stacks declared in a stylesheet.

    Custom properties are reported separately because a name like
    --brand-primary is worth more than the tenth-most-used hex value.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    variables = {}
    for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;{}]+)", text):
        value = m.group(2).strip()
        if HEX_RE.match(value):
            variables[m.group(1)] = value

    counts = {}
    for m in HEX_RE.finditer(text):
        key = "#" + m.group(1).upper()
        if len(key) == 4:
            key = "#" + "".join(c * 2 for c in key[1:])
        counts[key] = counts.get(key, 0) + 1

    families = []
    for m in re.finditer(r"font-family\s*:\s*([^;{}]+)", text):
        stack = " ".join(m.group(1).split())
        if stack not in families:
            families.append(stack)

    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "source": os.path.basename(path),
        "custom_properties": variables,
        "colors": [{"hex": h, "occurrences": n} for h, n in ordered[:24]],
        "font_families": families[:12],
    }


# ── the profile itself ───────────────────────────────────────────────────

EXAMPLE = {
    "company": "Columbus",
    "slug": "columbus",
    "sources": [
        "corporate-template.potx (theme colours and fonts)",
        "logo-primary.svg (mark colours)",
        "https://example.com (site CSS)",
    ],
    "colors": {
        "primary": {"hex": "#1B1474", "use": "Headings, primary buttons, the mark"},
        "primary_dark": {"hex": "#120D52", "use": "Hover and pressed states"},
        "accent": {"hex": "#DCDDF6", "use": "Fills, chips, quiet emphasis"},
        "surface": {"hex": "#FFFFFF", "use": "Page and slide background"},
        "ink": {"hex": "#1C1C28", "use": "Body text"},
        "muted": {"hex": "#5B5B6B", "use": "Secondary text, captions"},
    },
    "pairings": [
        {"name": "Body text on page", "fg": "#1C1C28", "bg": "#FFFFFF"},
        {"name": "Heading on page", "fg": "#1B1474", "bg": "#FFFFFF", "large_text": True},
        {"name": "Button label on primary", "fg": "#FFFFFF", "bg": "#1B1474"},
        {"name": "Caption on page", "fg": "#5B5B6B", "bg": "#FFFFFF"},
    ],
    "typography": {
        "heading": {"family": "Fraunces", "fallback": "Georgia, serif"},
        "body": {"family": "Inter", "fallback": "system-ui, Arial, sans-serif"},
    },
    "logo": {
        "files": ["assets/logo-primary.svg", "assets/logo-reverse.svg"],
        "clear_space": "Half the mark's height on every side",
        "min_width_px": 120,
        "on_dark": "Use logo-reverse.svg — never recolour the primary mark",
        "never": ["Recolour", "Stretch or skew", "Add effects", "Place on a busy photo"],
    },
    "voice": {
        "traits": ["Direct", "Evidence-led", "Plain about trade-offs"],
        "avoid": ["Hype adjectives", "Vague futurism", "Exclamation marks"],
    },
    "values": [
        {"value": "Placeholder value", "means_in_output": "What this changes about the writing"},
    ],
}

REQUIRED = ("company", "slug", "colors", "typography", "logo")


def check(path):
    """Validate a brand profile and contrast-test every pairing it claims."""
    with open(path, "r", encoding="utf-8") as fh:
        try:
            profile = json.load(fh)
        except json.JSONDecodeError as exc:
            raise SystemExit("%s is not valid JSON: %s" % (path, exc))

    problems, lines = [], []

    for key in REQUIRED:
        if key not in profile:
            problems.append("missing required key: %s" % key)

    slug = profile.get("slug", "")
    if slug and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        problems.append("slug %r must be lowercase letters, digits and single hyphens "
                        "— it becomes the skill's folder and frontmatter name" % slug)

    for name, entry in (profile.get("colors") or {}).items():
        value = entry.get("hex") if isinstance(entry, dict) else entry
        try:
            parse_hex(value)
        except ValueError as exc:
            problems.append("colors.%s: %s" % (name, exc))

    pairings = profile.get("pairings") or []
    if not pairings:
        problems.append("no pairings declared — a palette without tested "
                        "text/background pairs cannot be applied safely")

    lines.append("Contrast")
    lines.append("--------")
    for pair in pairings:
        try:
            ratio = contrast_ratio(pair["fg"], pair["bg"])
        except (KeyError, ValueError) as exc:
            problems.append("pairing %r: %s" % (pair.get("name", "?"), exc))
            continue
        large = bool(pair.get("large_text"))
        verdict = contrast_verdict(ratio, large)
        lines.append("  %-28s %s on %s  %5.2f:1  %s"
                     % (pair.get("name", "?"), pair["fg"], pair["bg"], ratio, verdict))
        if verdict == "fails":
            problems.append("pairing %r fails WCAG AA at %.2f:1 — either darken the "
                            "foreground, lighten the background, or record it as "
                            "decorative-only in the generated skill"
                            % (pair.get("name", "?"), ratio))

    print("\n".join(lines))
    print()
    if problems:
        print("Problems (%d)" % len(problems))
        print("------------")
        for p in problems:
            print("  - %s" % p)
        return 1
    print("Profile is valid, and every declared pairing passes WCAG AA.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Extract and validate brand values from real artefacts.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--from-pptx", metavar="FILE", help="theme colours and fonts from a .pptx/.potx")
    g.add_argument("--from-svg", metavar="FILE", help="colours painted by an .svg logo")
    g.add_argument("--from-css", metavar="FILE", help="colours and font stacks from a stylesheet")
    g.add_argument("--contrast", nargs=2, metavar=("FG", "BG"), help="WCAG ratio for two hex colours")
    g.add_argument("--check", metavar="FILE", help="validate a brand profile and test its pairings")
    g.add_argument("--example", action="store_true", help="print a starter brand profile")
    ap.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = ap.parse_args(argv)

    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return 0

    if args.check:
        return check(args.check)

    if args.contrast:
        fg, bg = args.contrast
        try:
            ratio = contrast_ratio(fg, bg)
        except ValueError as exc:
            raise SystemExit(str(exc))
        if args.format == "json":
            print(json.dumps({"fg": fg, "bg": bg, "ratio": round(ratio, 2),
                              "normal_text": contrast_verdict(ratio),
                              "large_text": contrast_verdict(ratio, True)}, indent=2))
        else:
            print("%s on %s" % (fg, bg))
            print("  ratio       %.2f:1" % ratio)
            print("  normal text %s" % contrast_verdict(ratio))
            print("  large text  %s" % contrast_verdict(ratio, True))
        return 0

    if args.from_pptx:
        data = from_pptx(args.from_pptx)
        if args.format == "json":
            print(json.dumps(data, indent=2))
            return 0
        print("Theme colours (%s, from %s)" % (data["source"], data["theme_part"]))
        for slot, label in THEME_SLOTS:
            entry = data["colors"].get(slot)
            if entry:
                print("  %-10s %-24s %s" % (slot, entry["role"], entry["hex"]))
        print()
        print("Theme fonts")
        for key in ("heading", "body"):
            print("  %-10s %s" % (key, data["fonts"].get(key, "(not set)")))
        if data["media"]:
            print()
            print("Embedded media — the logo is usually one of the smaller files")
            for m in data["media"][:12]:
                print("  %8d bytes  %s" % (m["bytes"], m["name"]))
        return 0

    reader = from_svg if args.from_svg else from_css
    data = reader(args.from_svg or args.from_css)
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 0
    print("%s" % data["source"])
    if data.get("custom_properties"):
        print()
        print("Custom properties (named colours beat frequent ones)")
        for name, value in data["custom_properties"].items():
            print("  %-28s %s" % (name, value))
    print()
    print("Colours")
    for c in data["colors"]:
        print("  %-9s %d occurrence%s" % (c["hex"], c["occurrences"],
                                          "" if c["occurrences"] == 1 else "s"))
    if data.get("font_families"):
        print()
        print("Font stacks")
        for f in data["font_families"]:
            print("  %s" % f)
    if data.get("note"):
        print()
        print(data["note"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
