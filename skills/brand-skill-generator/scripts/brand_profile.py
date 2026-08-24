#!/usr/bin/env python3
"""Pull real brand values out of the files a client actually gave you.

Standard library only, like every script in this toolkit — no Pillow, no
python-pptx, no network. A .pptx is a zip of XML and an .svg is XML, so the
values are already reachable. The point is that you read the brand off the
artefacts instead of asking the client questions their own files answer.

    python brand_profile.py --from-pptx template.potx
    python brand_profile.py --extract-media template.potx --out assets/
    python brand_profile.py --from-html homepage.html
    python brand_profile.py --from-svg logo.svg
    python brand_profile.py --from-css site.css
    python brand_profile.py --contrast "#1B1474" "#FFFFFF"
    python brand_profile.py --example > brand.json
    python brand_profile.py --check brand.json
    python brand_profile.py --swatch brand.json --out swatches.html

Two commands carry most of the weight:

--extract-media writes the deck's images to disk and says which slide part
  each one appears on. A picture used by the slide master is a logo; a
  picture used by one slide is a photo. Never ask for a logo that is sitting
  inside the file you were handed.

--from-html ranks a saved page's logo candidates and reads the company name
  off it. A favicon is evidence of a logo, not a logo, so the header mark
  outranks it.

--swatch writes a page you can look at. Hex codes are unreadable to almost
  everyone, so an approval step built on them is not really an approval.
"""

import argparse
import base64
import colorsys
import html.parser
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

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

# Microsoft's own stock themes. A template carrying one of these has not been
# branded — nobody chose these colours, so do not present them as the client's.
OFFICE_DEFAULTS = {
    "Office 2013-2021 default": {
        "accents": ["4472C4", "ED7D31", "A5A5A5", "FFC000", "5B9BD5", "70AD47"],
        "fonts": ("Calibri Light", "Calibri"),
    },
    "Office 2024 / Microsoft 365 default": {
        "accents": ["156082", "E97132", "196B24", "0F9ED5", "A02B93", "4EA72E"],
        "fonts": ("Aptos Display", "Aptos"),
    },
}

HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
SCHEME_RE = re.compile(r'schemeClr\s+val="(\w+)"')
IMAGE_REL_RE = re.compile(r'Target="[^"]*?media/([^"]+)"')

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".bmp", ".tiff", ".emf", ".wmf")


# ── colour maths and naming ──────────────────────────────────────────────

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


# Hue bands, in degrees. Ordinary words, not paint-chart words — the person
# approving the profile should recognise the colour from the name.
HUE_NAMES = [
    (12, "red"), (24, "vermilion"), (38, "orange"), (48, "amber"),
    (62, "yellow"), (78, "lime"), (95, "yellow-green"), (140, "green"),
    (165, "emerald"), (180, "teal"), (196, "cyan"), (210, "sky blue"),
    (230, "blue"), (250, "indigo"), (270, "violet"), (290, "purple"),
    (320, "magenta"), (340, "pink"), (360, "red"),
]


def describe_color(value):
    """Plain-English name for a hex colour: 'deep indigo', 'pale grey'.

    A hex code tells a designer something and everyone else nothing. Every
    place this script prints a colour, it prints the name too.
    """
    r, g, b = parse_hex(value)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360

    if l >= 0.96:
        return "white" if s < 0.1 else "near-white"
    if l <= 0.06:
        return "black" if s < 0.1 else "near-black"

    if s < 0.10:
        if l < 0.25:
            return "charcoal grey"
        if l < 0.45:
            return "dark grey"
        if l < 0.65:
            return "mid grey"
        if l < 0.85:
            return "light grey"
        return "pale grey"

    name = next(n for bound, n in HUE_NAMES if hue < bound)

    if l < 0.22:
        tone = "very dark"
    elif l < 0.40:
        tone = "deep"
    elif l < 0.62:
        tone = ""
    elif l < 0.80:
        tone = "light"
    else:
        tone = "pale"

    if s < 0.25:
        sat = "muted"
    elif s > 0.80 and 0.3 < l < 0.7:
        sat = "vivid"
    else:
        sat = ""

    return " ".join(w for w in (tone, sat, name) if w)


def swatch_label(value):
    """'#1B1474 (deep indigo)' — used everywhere a colour is printed."""
    return "%s (%s)" % (value.upper(), describe_color(value))


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


def _part_kind(name):
    """Which sort of slide part a path belongs to."""
    if "slideMaster" in name:
        return "master"
    if "slideLayout" in name:
        return "layout"
    if "/slides/" in name:
        return "slide"
    if "notesMaster" in name or "notesSlide" in name:
        return "notes"
    if "handoutMaster" in name:
        return "handout"
    return "other"


def _media_usage(z):
    """Map each embedded image to the slide parts that reference it.

    Relationship files name their targets, so this is exact rather than a
    guess from file size. An image on the master or on every layout is
    furniture — the logo. An image on one slide is content.
    """
    usage = {}
    for name in z.namelist():
        if not name.endswith(".rels"):
            continue
        owner = name.replace("/_rels/", "/").replace(".rels", "")
        kind = _part_kind(owner)
        if kind == "other":
            continue
        try:
            body = z.read(name).decode("utf-8", "replace")
        except KeyError:
            continue
        for target in IMAGE_REL_RE.findall(body):
            entry = usage.setdefault(target, {"kinds": {}, "parts": []})
            entry["kinds"][kind] = entry["kinds"].get(kind, 0) + 1
            if len(entry["parts"]) < 6:
                entry["parts"].append(os.path.basename(owner))
    return usage


def _logo_confidence(kinds):
    """How likely an image is the logo, from where it is used."""
    if kinds.get("master"):
        return "very likely the logo (used by the slide master)"
    if kinds.get("layout", 0) >= 2:
        return "likely the logo (used by several layouts)"
    if kinds.get("layout"):
        return "possibly the logo (used by one layout)"
    if kinds.get("slide", 0) >= 3:
        return "recurring slide image"
    return "slide content, not brand furniture"


def from_pptx(path):
    """Theme colours, theme fonts, real slot usage and media, from a deck."""
    if not zipfile.is_zipfile(path):
        raise SystemExit("%s is not a .pptx/.potx (not a zip archive)" % path)

    out = {"source": os.path.basename(path), "colors": {}, "fonts": {},
           "usage": {}, "media": [], "default_theme": None}
    with zipfile.ZipFile(path) as z:
        themes = sorted(n for n in z.namelist()
                        if n.startswith("ppt/theme/") and n.endswith(".xml"))
        if not themes:
            raise SystemExit("no ppt/theme/*.xml inside %s — is this a PowerPoint file?" % path)
        out["theme_part"] = themes[0]
        out["other_themes"] = themes[1:]
        root = ET.fromstring(z.read(themes[0]))

        scheme = root.find(".//" + A + "clrScheme")
        if scheme is not None:
            for slot, label in THEME_SLOTS:
                value = _solid_colour(scheme.find(A + slot))
                if value:
                    out["colors"][slot] = {
                        "hex": value, "role": label, "name": describe_color(value)}

        fonts = root.find(".//" + A + "fontScheme")
        if fonts is not None:
            for key, tag in (("heading", "majorFont"), ("body", "minorFont")):
                group = fonts.find(A + tag)
                if group is not None:
                    latin = group.find(A + "latin")
                    if latin is not None and latin.get("typeface"):
                        out["fonts"][key] = latin.get("typeface")

        # Is this actually Microsoft's stock theme wearing a company's filename?
        accents = [out["colors"].get("accent%d" % i, {}).get("hex", "").lstrip("#").upper()
                   for i in range(1, 7)]
        pair = (out["fonts"].get("heading"), out["fonts"].get("body"))
        for label, spec in OFFICE_DEFAULTS.items():
            if accents == spec["accents"] or pair == spec["fonts"]:
                out["default_theme"] = {
                    "matches": label,
                    "colors_match": accents == spec["accents"],
                    "fonts_match": pair == spec["fonts"],
                }
                break

        # Which theme slots the deck actually paints with. This answers
        # "which accents are real" instead of asking the client.
        for name in z.namelist():
            if not name.endswith(".xml"):
                continue
            kind = _part_kind(name)
            if kind not in ("master", "layout", "slide"):
                continue
            body = z.read(name).decode("utf-8", "replace")
            for slot in SCHEME_RE.findall(body):
                entry = out["usage"].setdefault(slot, {"master": 0, "layout": 0, "slide": 0})
                entry[kind] = entry.get(kind, 0) + 1

        usage = _media_usage(z)
        for info in z.infolist():
            if not info.filename.startswith("ppt/media/"):
                continue
            base = os.path.basename(info.filename)
            u = usage.get(base, {"kinds": {}, "parts": []})
            out["media"].append({
                "name": info.filename,
                "bytes": info.file_size,
                "used_on": u["parts"],
                "verdict": _logo_confidence(u["kinds"]),
                "is_logo_candidate": bool(u["kinds"].get("master") or u["kinds"].get("layout")),
            })
        out["media"].sort(key=lambda m: (not m["is_logo_candidate"], m["bytes"]))
    return out


def extract_media(path, out_dir):
    """Write the deck's images to disk, logo candidates first."""
    data = from_pptx(path)
    os.makedirs(out_dir, exist_ok=True)
    written = []
    with zipfile.ZipFile(path) as z:
        for item in data["media"]:
            if not item["name"].lower().endswith(IMAGE_EXT):
                continue
            target = os.path.join(out_dir, os.path.basename(item["name"]))
            with open(target, "wb") as fh:
                fh.write(z.read(item["name"]))
            written.append(dict(item, path=target))
    return written


def from_svg(path):
    """Every colour an SVG logo actually paints with."""
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
        if len(key) == 4:
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
        "colors": [{"hex": h, "name": describe_color(h), "occurrences": n}
                   for h, n in ordered],
        "note": "Occurrence count is a hint, not a ranking — a one-use hex can "
                "still be the primary mark colour.",
    }


def from_css(path):
    """Hex colours and font stacks declared in a stylesheet."""
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
        "colors": [{"hex": h, "name": describe_color(h), "occurrences": n}
                   for h, n in ordered[:24]],
        "font_families": families[:12],
    }


# ── website: logo, name and colours, without asking for any of them ──────

LOGO_HINT = re.compile(r"logo|brand|wordmark|masthead|site-?title", re.I)

# Ranked by how likely the asset is the actual logo rather than a favicon.
# The favicon libraries on GitHub stop at <link rel="icon">, which is why they
# return a 32px square when what you wanted was the wordmark in the header.
ICON_RELS = {
    "mask-icon": ("mask icon (always vector, usually the mark)", 55),
    "apple-touch-icon": ("apple touch icon (largest square, often the mark)", 50),
    "apple-touch-icon-precomposed": ("apple touch icon", 48),
    "icon": ("favicon", 30),
    "shortcut icon": ("favicon", 30),
}


class _SiteParser(html.parser.HTMLParser):
    """Find the brand assets a page is already showing.

    A logo is normally an <img> or an inline <svg> inside the header, named
    something with 'logo' in it. Icons and og:image are the fallback, in that
    order, because a 32px favicon is evidence of a logo, not a logo.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.candidates = []
        self.meta = {}
        self.title = None
        self._in_title = False
        self._chrome_depth = 0      # inside <header>/<nav>
        self._svg_depth = 0
        self._svg_hinted = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        blob = " ".join([a.get("class", ""), a.get("id", ""), a.get("alt", ""),
                         a.get("src", ""), a.get("href", ""), a.get("aria-label", "")])
        hinted = bool(LOGO_HINT.search(blob))

        if tag in ("header", "nav"):
            self._chrome_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "svg":
            if self._svg_depth == 0:
                self._svg_hinted = hinted or self._chrome_depth > 0
            self._svg_depth += 1
            if self._svg_depth == 1 and self._svg_hinted:
                self._add("inline <svg>", "inline SVG in the page chrome — "
                          "copy it straight out of the page source", 90 if hinted else 70)
        elif tag == "img" and (hinted or self._chrome_depth > 0):
            src = a.get("src") or a.get("data-src") or ""
            if src:
                vector = src.lower().split("?")[0].endswith(".svg")
                self._add(src, "logo image in the %s%s" % (
                    "header" if self._chrome_depth else "page",
                    ", vector" if vector else ""),
                    (95 if vector else 80) if hinted else (70 if vector else 60))
        elif tag == "link":
            rels = a.get("rel", "").lower().strip()
            entry = ICON_RELS.get(rels)
            if entry and a.get("href"):
                label, score = entry
                sizes = a.get("sizes", "")
                if sizes:
                    label += " (%s)" % sizes
                    try:
                        score += min(int(sizes.split("x")[0]) // 32, 8)
                    except ValueError:
                        pass
                if a["href"].lower().split("?")[0].endswith(".svg"):
                    score += 10
                self._add(a["href"], label, score)
        elif tag == "meta":
            key = (a.get("property") or a.get("name") or "").lower()
            content = a.get("content", "")
            if key and content:
                self.meta[key] = content
            if key == "og:image":
                self._add(content, "og:image (social card — may be the logo or a photo)", 35)
            elif key == "msapplication-tileimage":
                self._add(content, "Windows tile image", 40)

    def handle_endtag(self, tag):
        if tag in ("header", "nav") and self._chrome_depth:
            self._chrome_depth -= 1
        elif tag == "svg" and self._svg_depth:
            self._svg_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and not self.title:
            self.title = data.strip()

    def _add(self, ref, why, score):
        if any(c["ref"] == ref for c in self.candidates):
            return
        self.candidates.append({"ref": ref, "why": why, "score": score})


def from_html(path):
    """Logo candidates, company name and theme colour from a saved page.

    Fetch the page with whatever tool you have, save it, and run this. The
    script itself never touches the network, same as everything else here.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    parser = _SiteParser()
    parser.feed(text)

    candidates = sorted(parser.candidates, key=lambda c: -c["score"])
    if not any("favicon.ico" in c["ref"] for c in candidates):
        candidates.append({"ref": "/favicon.ico", "score": 10,
                           "why": "root fallback — try it if nothing above resolves"})

    meta = parser.meta
    name = meta.get("og:site_name") or parser.title or ""
    if name and " | " in name:
        name = name.split(" | ")[0].strip()
    elif name and " - " in name:
        name = name.split(" - ")[0].strip()

    theme = meta.get("theme-color", "")
    return {
        "source": os.path.basename(path),
        "company_name": name,
        "descriptor": meta.get("og:description") or meta.get("description", ""),
        "theme_color": theme if HEX_RE.match(theme or "") else "",
        "logo_candidates": candidates,
    }


# ── the profile itself ───────────────────────────────────────────────────

EXAMPLE = {
    "company": "Columbus",
    "slug": "columbus",
    "sources": [
        "corporate-template.potx (theme colours and fonts)",
        "logo-primary.svg (mark colours)",
        "https://example.com (site CSS, About page voice)",
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
        "samples": ["A real sentence taken verbatim from their own material"],
    },
    "values": [
        {"value": "Placeholder value", "means_in_output": "What this changes about the writing"},
    ],
}

REQUIRED = ("company", "slug", "colors", "typography", "logo")


def _color_hex(entry):
    return entry.get("hex") if isinstance(entry, dict) else entry


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

    lines.append("Palette")
    lines.append("-------")
    for name, entry in (profile.get("colors") or {}).items():
        value = _color_hex(entry)
        try:
            parse_hex(value)
        except ValueError as exc:
            problems.append("colors.%s: %s" % (name, exc))
            continue
        use = entry.get("use", "") if isinstance(entry, dict) else ""
        lines.append("  %-14s %-28s %s" % (name, swatch_label(value), use))

    pairings = profile.get("pairings") or []
    if not pairings:
        problems.append("no pairings declared — a palette without tested "
                        "text/background pairs cannot be applied safely")

    lines.append("")
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
        lines.append("  %-28s %-26s on %-26s %5.2f:1  %s"
                     % (pair.get("name", "?"), swatch_label(pair["fg"]),
                        swatch_label(pair["bg"]), ratio, verdict))
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


# ── the swatch sheet ─────────────────────────────────────────────────────

def _embed_logo(path):
    """Inline an SVG, or base64 a raster, so the sheet is self-contained."""
    if not os.path.isfile(path):
        return '<p class="miss">missing: %s</p>' % path
    ext = os.path.splitext(path)[1].lower()
    if ext == ".svg":
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif"}.get(ext)
    if not mime:
        return '<p class="miss">cannot preview %s</p>' % os.path.basename(path)
    with open(path, "rb") as fh:
        return '<img alt="%s" src="data:%s;base64,%s">' % (
            os.path.basename(path), mime, base64.b64encode(fh.read()).decode("ascii"))


def swatch(path, out_path):
    """Write a page showing the palette as colour, not as hex codes.

    Nobody can approve '#1B1474'. They can approve a block of deep indigo
    with white text sitting on it, next to the logo on that same colour.
    """
    with open(path, "r", encoding="utf-8") as fh:
        profile = json.load(fh)

    company = profile.get("company", "This company")
    colors = profile.get("colors") or {}
    typography = profile.get("typography") or {}
    logo = profile.get("logo") or {}

    blocks = []
    for name, entry in colors.items():
        value = _color_hex(entry)
        try:
            rgb = parse_hex(value)
        except ValueError:
            continue
        on_white = contrast_ratio(value, "#FFFFFF")
        on_black = contrast_ratio(value, "#000000")
        text_on = "#FFFFFF" if on_white > on_black else "#000000"
        use = entry.get("use", "") if isinstance(entry, dict) else ""
        blocks.append(
            '<figure class="sw">'
            '<div class="chip" style="background:%s;color:%s">Aa</div>'
            '<figcaption><b>%s</b><span class="nm">%s</span>'
            '<code>%s</code><span class="rgb">rgb(%d, %d, %d)</span>'
            '<span class="use">%s</span></figcaption></figure>'
            % (value, text_on, name, describe_color(value), value.upper(),
               rgb[0], rgb[1], rgb[2], use))

    rows = []
    for pair in profile.get("pairings") or []:
        try:
            ratio = contrast_ratio(pair["fg"], pair["bg"])
        except (KeyError, ValueError):
            continue
        verdict = contrast_verdict(ratio, bool(pair.get("large_text")))
        cls = "bad" if verdict == "fails" else "ok"
        rows.append(
            '<tr><td>%s</td>'
            '<td class="demo" style="background:%s;color:%s">The quick brown fox</td>'
            '<td>%s on %s</td><td class="%s">%.2f:1 &middot; %s</td></tr>'
            % (pair.get("name", ""), pair["bg"], pair["fg"],
               describe_color(pair["fg"]), describe_color(pair["bg"]),
               cls, ratio, verdict))

    heading = typography.get("heading") or {}
    body = typography.get("body") or {}
    hfam = "%s, %s" % (heading.get("family", "Georgia"), heading.get("fallback", "serif"))
    bfam = "%s, %s" % (body.get("family", "system-ui"), body.get("fallback", "sans-serif"))

    primary = _color_hex(colors.get("primary")) or "#333333"
    logo_light = "".join(_embed_logo(f) for f in logo.get("files", [])[:1])
    logo_dark = "".join(_embed_logo(f) for f in logo.get("files", [])[:2][-1:])

    html = """<!doctype html>
<meta charset="utf-8">
<title>%(company)s brand — for approval</title>
<style>
  body { font: 16px/1.55 system-ui, -apple-system, Arial, sans-serif; margin: 0 auto;
         max-width: 980px; padding: 40px 24px 80px; color: #1c1c28; }
  h1 { font-size: 28px; margin: 0 0 4px; }
  .lede { color: #5b5b6b; margin: 0 0 32px; }
  h2 { font-size: 18px; margin: 40px 0 12px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 16px; }
  .sw { margin: 0; border: 1px solid #e4e4f0; border-radius: 10px; overflow: hidden; }
  .chip { height: 92px; display: flex; align-items: center; justify-content: center;
          font-size: 26px; font-weight: 700; }
  figcaption { padding: 10px 12px 12px; display: grid; gap: 1px; }
  figcaption b { font-size: 14px; }
  .nm { font-size: 14px; color: #1c1c28; }
  figcaption code { font-size: 12.5px; color: #5b5b6b; }
  .rgb { font-size: 12px; color: #8a8a99; }
  .use { font-size: 12.5px; color: #5b5b6b; margin-top: 5px; }
  table { border-collapse: collapse; width: 100%%; font-size: 14px; }
  td, th { border-bottom: 1px solid #e4e4f0; padding: 9px 10px; text-align: left; }
  .demo { font-weight: 600; }
  .ok { color: #1a7f4b; } .bad { color: #b3261e; font-weight: 700; }
  .logos { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .logo-box { border: 1px solid #e4e4f0; border-radius: 10px; padding: 28px;
              display: flex; align-items: center; justify-content: center; min-height: 130px; }
  .logo-box svg, .logo-box img { max-width: 200px; max-height: 80px; height: auto; }
  .on-dark { background: %(primary)s; }
  .miss { color: #b3261e; font-size: 13px; margin: 0; }
  .spec-h { font-family: %(hfam)s; font-size: 34px; margin: 0 0 6px; color: %(primary)s; }
  .spec-b { font-family: %(bfam)s; font-size: 16px; margin: 0; max-width: 60ch; }
  .ask { background: #fbf7ec; border: 1px solid #e8dcc0; border-radius: 10px;
         padding: 16px 18px; margin-top: 36px; }
  .ask h2 { margin-top: 0; }
</style>
<h1>%(company)s — brand profile for approval</h1>
<p class="lede">Look at the colours rather than the codes. If a block below is not
your colour, say which one is wrong; nothing is generated until you approve this.</p>

<h2>Palette</h2>
<div class="grid">%(blocks)s</div>

<h2>Text on background, as it will actually look</h2>
<table>
  <tr><th>Pairing</th><th>Rendered</th><th>Colours</th><th>Contrast</th></tr>
  %(rows)s
</table>

<h2>Logo</h2>
<div class="logos">
  <div class="logo-box">%(logo_light)s</div>
  <div class="logo-box on-dark">%(logo_dark)s</div>
</div>

<h2>Type</h2>
<p class="spec-h">Headings look like this</p>
<p class="spec-b">Body text looks like this. %(company)s uses it for everything that
is not a heading, at the size and measure shown here.</p>

<div class="ask">
  <h2>What to check</h2>
  <ul>
    <li>Is the primary colour the one you would call your brand colour?</li>
    <li>Any colour here that is not really yours?</li>
    <li>Does the logo sit correctly on both backgrounds?</li>
    <li>Anything in red under Contrast is unreadable and needs a decision.</li>
  </ul>
</div>
""" % {"company": company, "blocks": "".join(blocks), "rows": "".join(rows),
       "primary": primary, "hfam": hfam, "bfam": bfam,
       "logo_light": logo_light or '<p class="miss">no logo file in profile</p>',
       "logo_dark": logo_dark or '<p class="miss">no reverse logo in profile</p>'}

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


# ── output ───────────────────────────────────────────────────────────────

def print_pptx(data):
    print("Theme colours (%s, from %s)" % (data["source"], data["theme_part"]))
    for slot, label in THEME_SLOTS:
        entry = data["colors"].get(slot)
        if not entry:
            continue
        u = data["usage"].get(slot)
        if u:
            total = sum(u.values())
            where = "used %d× (master %d, layouts %d, slides %d)" % (
                total, u.get("master", 0), u.get("layout", 0), u.get("slide", 0))
        else:
            where = "never used — template leftover"
        print("  %-10s %-24s %-28s %s" % (slot, label, swatch_label(entry["hex"]), where))

    print()
    print("Theme fonts")
    for key in ("heading", "body"):
        print("  %-10s %s" % (key, data["fonts"].get(key, "(not set)")))

    if data.get("default_theme"):
        d = data["default_theme"]
        print()
        print("WARNING: this looks like %s, not a brand." % d["matches"])
        print("  colours match the stock theme: %s" % ("yes" if d["colors_match"] else "no"))
        print("  fonts match the stock theme:   %s" % ("yes" if d["fonts_match"] else "no"))
        print("  Nobody chose these values. Treat them as a starting point at best,")
        print("  and look for the brand in the logo and on the website instead.")

    if data.get("other_themes"):
        print()
        print("Other themes in this file (check if the colours look wrong):")
        for t in data["other_themes"]:
            print("  %s" % t)

    if data["media"]:
        print()
        print("Embedded images — where each one is used decides what it is")
        for m in data["media"][:14]:
            print("  %-26s %8d bytes  %s" % (os.path.basename(m["name"]), m["bytes"], m["verdict"]))
            if m["used_on"]:
                print("  %-26s %8s  on: %s" % ("", "", ", ".join(m["used_on"])))
        print()
        print("Write them out with:  --extract-media <file> --out assets/")


def print_html(data):
    print("%s" % data["source"])
    print()
    print("Company")
    print("  name        %s" % (data["company_name"] or "(no title or og:site_name)"))
    if data["descriptor"]:
        print("  describes   %s" % data["descriptor"][:150])
    if data["theme_color"]:
        print("  theme-color %s" % swatch_label(data["theme_color"]))
    print()
    print("Logo candidates, best first — fetch the top one before asking for a logo")
    for c in data["logo_candidates"]:
        print("  %-52s %s" % (c["ref"][:52], c["why"]))
    print()
    print("A favicon is evidence of a logo, not a logo. Prefer the header mark or")
    print("the mask-icon; fall back to an icon only when nothing else resolves.")


def print_colors(data):
    print("%s" % data["source"])
    if data.get("custom_properties"):
        print()
        print("Custom properties (a named colour beats a frequent one)")
        for name, value in data["custom_properties"].items():
            print("  %-28s %s" % (name, swatch_label(value)))
    print()
    print("Colours")
    for c in data["colors"]:
        print("  %-30s %d occurrence%s" % (swatch_label(c["hex"]), c["occurrences"],
                                           "" if c["occurrences"] == 1 else "s"))
    if data.get("font_families"):
        print()
        print("Font stacks")
        for f in data["font_families"]:
            print("  %s" % f)
    if data.get("note"):
        print()
        print(data["note"])


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Extract and validate brand values from real artefacts.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--from-pptx", metavar="FILE", help="theme colours, fonts, slot usage and media")
    g.add_argument("--extract-media", metavar="FILE", help="write a deck's images to --out")
    g.add_argument("--from-svg", metavar="FILE", help="colours painted by an .svg logo")
    g.add_argument("--from-css", metavar="FILE", help="colours and font stacks from a stylesheet")
    g.add_argument("--from-html", metavar="FILE", help="logo candidates, company name and theme colour from a saved page")
    g.add_argument("--contrast", nargs=2, metavar=("FG", "BG"), help="WCAG ratio for two hex colours")
    g.add_argument("--check", metavar="FILE", help="validate a brand profile and test its pairings")
    g.add_argument("--swatch", metavar="FILE", help="write a visual approval sheet from a profile")
    g.add_argument("--example", action="store_true", help="print a starter brand profile")
    ap.add_argument("--out", metavar="PATH", help="output directory (--extract-media) or file (--swatch)")
    ap.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = ap.parse_args(argv)

    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return 0

    if args.check:
        return check(args.check)

    if args.swatch:
        out = args.out or "swatches.html"
        swatch(args.swatch, out)
        print("Wrote %s — open it and look at the colours before approving." % out)
        return 0

    if args.extract_media:
        out_dir = args.out or "assets"
        written = extract_media(args.extract_media, out_dir)
        if not written:
            print("No images found in %s." % args.extract_media)
            return 0
        print("Wrote %d image(s) to %s/" % (len(written), out_dir.rstrip("/")))
        for item in written:
            print("  %-26s %s" % (os.path.basename(item["path"]), item["verdict"]))
        print()
        print("Logo candidates are listed first. Do not ask for a logo that is in here.")
        return 0

    if args.contrast:
        fg, bg = args.contrast
        try:
            ratio = contrast_ratio(fg, bg)
        except ValueError as exc:
            raise SystemExit(str(exc))
        if args.format == "json":
            print(json.dumps({"fg": fg, "fg_name": describe_color(fg),
                              "bg": bg, "bg_name": describe_color(bg),
                              "ratio": round(ratio, 2),
                              "normal_text": contrast_verdict(ratio),
                              "large_text": contrast_verdict(ratio, True)}, indent=2))
        else:
            print("%s on %s" % (swatch_label(fg), swatch_label(bg)))
            print("  ratio       %.2f:1" % ratio)
            print("  normal text %s" % contrast_verdict(ratio))
            print("  large text  %s" % contrast_verdict(ratio, True))
        return 0

    if args.from_html:
        data = from_html(args.from_html)
        if args.format == "json":
            print(json.dumps(data, indent=2))
        else:
            print_html(data)
        return 0

    if args.from_pptx:
        data = from_pptx(args.from_pptx)
        if args.format == "json":
            print(json.dumps(data, indent=2))
        else:
            print_pptx(data)
        return 0

    reader = from_svg if args.from_svg else from_css
    data = reader(args.from_svg or args.from_css)
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print_colors(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
