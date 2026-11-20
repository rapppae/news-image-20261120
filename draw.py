"""Draw the 20 November 2026 world-news poster (1024x1024 PNG).

Everything on the poster is data in the tables below; the renderers are
generic (one card renderer, one chart renderer, one strip renderer), so the
layout is computed from a small grid instead of hard-coded per element.
Deterministic: no clock, no randomness, fixed fonts from assets/.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
ASSETS = "assets"

PALETTE = {
    "paper": (245, 240, 225),
    "navy": (26, 35, 64),
    "navy_deep": (18, 25, 48),
    "gold": (212, 175, 55),
    "gold_soft": (232, 200, 90),
    "red": (178, 34, 52),
    "teal": (0, 128, 128),
    "ink": (30, 30, 34),
    "grey": (110, 110, 105),
    "white": (255, 255, 255),
    "line": (200, 192, 172),
}

MARGIN = 40
GUTTER = 28
COL_W = (W - 2 * MARGIN - GUTTER) // 2

LEAD = {
    "eyebrow": "THE WORLD IN ONE DAY",
    "date": "FRIDAY, 20 NOVEMBER 2026",
    "kicker": "WALL STREET  \u00b7  THE BIGGEST IPO EVER",
    "headline": ["Anthropic's $81bn", "debut tops the record", "books"],
    "body": (
        "Claude's maker priced its shares at $83, opened at $111.50 \u2014 up 34% "
        "\u2014 and closed 17% higher at $97.17, worth about $1.75 trillion. "
        "The largest IPO ever."
    ),
}

CHART = {
    "ticker": "ANT",
    "move": "+34% AT THE OPEN",
    "prices": "$83 IPO  \u2192  $111.50 open  \u00b7  $97.17 close",
    # normalised (x, y) in panel coordinates, 0..1 across / 0..1 down
    "points": [
        (0.03, 0.88), (0.14, 0.80), (0.24, 0.84), (0.36, 0.68),
        (0.50, 0.54), (0.63, 0.42), (0.76, 0.30), (0.88, 0.18), (0.97, 0.05),
    ],
    # (x0, w, h) fractions of panel width/height, windows as (col, row) grid
    "towers": [
        (0.02, 0.11, 0.85), (0.15, 0.12, 0.65), (0.29, 0.13, 0.90),
        (0.44, 0.12, 0.70), (0.58, 0.11, 0.88), (0.71, 0.12, 0.62),
        (0.85, 0.12, 0.80),
    ],
}

STORIES = [
    {
        "icon": "scales",
        "kicker": "THE HAGUE  \u00b7  JUSTICE",
        "headline": ["World court: Myanmar", "guilty of genocide"],
        "body": "The ICJ rules 9\u20136 that Myanmar committed genocide \u2014 a first in 80 years.",
    },
    {
        "icon": "bars",
        "kicker": "GAMES  \u00b7  CULTURE",
        "headline": ["GTA VI: a $2.36bn", "opening day"],
        "body": "About 24.5m copies sold on day one \u2014 the biggest entertainment launch ever.",
    },
    {
        "icon": "cyclone",
        "kicker": "WEATHER  \u00b7  INDIA",
        "headline": ["Cyclone Akvan makes", "landfall"],
        "body": "The storm hits India's east coast at midday; 300,000 people were moved to safety.",
    },
    {
        "icon": "globe",
        "kicker": "DIPLOMACY  \u00b7  SHENZHEN",
        "headline": ["Three presidents sign a", "peace declaration"],
        "body": "Trump, Xi and Putin end a 90-minute trilateral summit with a joint declaration of peace.",
    },
]

ALSO = [
    "Nasdaq falls 2.3% as the AI trade wobbles",
    "US loses measles-free status after 26 years",
    "COP31 draft drops fossil fuels",
    "Iran drones hit a US radar in Bahrain",
]

FOOTER = "All stories as reported on 20 November 2026  \u00b7  Sources: Reuters, WSJ, Barron's, BBC, CNN, IMD"


def _fonts():
    def load(name, size):
        return ImageFont.truetype(f"{ASSETS}/{name}", size)

    bold = "LiberationSans-Bold.ttf"
    plain = "DejaVuSans.ttf"
    return {
        "eyebrow": load(bold, 27),
        "date": load(bold, 56),
        "kicker": load(bold, 21),
        "headline": load(bold, 48),
        "body": load(plain, 21),
        "ticker": load(bold, 62),
        "move": load(bold, 23),
        "prices": load(plain, 17),
        "card_kicker": load(bold, 18),
        "card_head": load(bold, 27),
        "card_body": load(plain, 20),
        "strip_title": load(bold, 21),
        "strip_item": load(plain, 19),
        "footer": load(plain, 17),
        "icon_label": load(bold, 22),
    }


def _wrap(draw, text, font, width):
    """Greedy word wrap returning a list of lines that fit `width`."""
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _spaced(draw, xy, text, font, fill, gap=6):
    """Draw text with extra tracking between characters; returns end x."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + gap
    return x


def _skyline(draw, box, towers):
    """Night skyline along the bottom of `box`, with lit windows."""
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    for fx, fw, fh in towers:
        bx = x0 + fx * pw
        bw, bh = fw * pw, fh * ph
        by = y1 - bh
        draw.rectangle([bx, by, bx + bw, y1], fill=PALETTE["navy_deep"])
        cols, rows = max(1, int(bw // 22)), max(1, int(bh // 24))
        for c in range(cols):
            for r in range(rows):
                if (c * 2 + r) % 3 == 0:
                    wx = bx + 6 + c * 22
                    wy = by + 8 + r * 24
                    draw.rectangle([wx, wy, wx + 7, wy + 9], fill=PALETTE["gold_soft"])


def _chart_panel(draw, fonts, box):
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    draw.rectangle(box, fill=PALETTE["navy"])
    draw.text((x0 + 22, y0 + 8), CHART["ticker"], font=fonts["ticker"], fill=PALETTE["gold"])
    draw.text((x0 + 22, y0 + 82), CHART["move"], font=fonts["move"], fill=PALETTE["white"])
    draw.text((x0 + 22, y0 + 112), CHART["prices"], font=fonts["prices"], fill=PALETTE["white"])
    _skyline(draw, (x0, y1 - 90, x1, y1), CHART["towers"])
    pts = [(x0 + fx * pw, y0 + 40 + fy * (ph - 70)) for fx, fy in CHART["points"]]
    draw.line(pts, fill=PALETTE["gold"], width=4)
    for px, py in pts:
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=PALETTE["gold"])


def _icon(draw, fonts, kind, box):
    """Small white/gold glyph on a navy square."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=PALETTE["navy"])
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "scales":
        draw.line([(cx, y0 + 12), (cx, y1 - 14)], fill=PALETTE["gold"], width=3)
        draw.line([(x0 + 12, y0 + 22), (x1 - 12, y0 + 22)], fill=PALETTE["gold"], width=3)
        for sx in (x0 + 14, x1 - 34):
            draw.line([(sx + 8, y0 + 22), (sx, y0 + 44)], fill=PALETTE["gold"], width=2)
            draw.line([(sx + 8, y0 + 22), (sx + 16, y0 + 44)], fill=PALETTE["gold"], width=2)
            draw.line([(sx, y0 + 44), (sx + 16, y0 + 44)], fill=PALETTE["gold"], width=2)
        draw.line([(x0 + 16, y1 - 14), (x1 - 16, y1 - 14)], fill=PALETTE["gold"], width=3)
    elif kind == "bars":
        label = "VI"
        lw = draw.textlength(label, font=fonts["icon_label"])
        draw.text((cx - lw / 2, y0 + 6), label, font=fonts["icon_label"], fill=PALETTE["gold"])
        heights = [20, 30, 40]
        bw = 14
        total = len(heights) * bw + (len(heights) - 1) * 8
        bx = cx - total / 2
        for i, h in enumerate(heights):
            x = bx + i * (bw + 8)
            draw.rectangle([x, y1 - 10 - h, x + bw, y1 - 10], fill=PALETTE["gold"])
    elif kind == "cyclone":
        for r in (30, 21, 12):
            draw.arc([cx - r, cy - r, cx + r, cy + r], start=40, end=330, fill=PALETTE["white"], width=3)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=PALETTE["gold"])
    elif kind == "globe":
        draw.ellipse([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=PALETTE["white"], width=3)
        draw.ellipse([cx - 13, y0 + 12, cx + 13, y1 - 12], outline=PALETTE["white"], width=2)
        draw.line([(x0 + 12, cy), (x1 - 12, cy)], fill=PALETTE["white"], width=2)
        draw.arc([x0 + 12, y0 + 28, x1 - 12, y1 - 28], start=200, end=340, fill=PALETTE["white"], width=2)
        draw.ellipse([x1 - 26, y0 + 16, x1 - 14, y0 + 28], fill=PALETTE["gold"])


def _card(draw, fonts, box, story):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=PALETTE["white"], outline=PALETTE["line"], width=1)
    draw.rectangle([x0, y0, x1, y0 + 8], fill=PALETTE["teal"])
    icon_box = (x0 + 16, y0 + 16, x0 + 100, y0 + 100)
    _icon(draw, fonts, story["icon"], icon_box)
    tx = x0 + 112
    draw.text((tx, y0 + 20), story["kicker"], font=fonts["card_kicker"], fill=PALETTE["red"])
    y = y0 + 45
    for line in story["headline"]:
        draw.text((tx, y), line, font=fonts["card_head"], fill=PALETTE["ink"])
        y += 29
    body_lines = _wrap(draw, story["body"], fonts["card_body"], x1 - x0 - 28)
    y = y0 + 105
    for line in body_lines[:2]:
        draw.text((x0 + 14, y), line, font=fonts["card_body"], fill=PALETTE["ink"])
        y += 24


def _also_today(draw, fonts, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=PALETTE["navy"])
    draw.text((x0 + 16, y0 + 16), "ALSO TODAY", font=fonts["strip_title"], fill=PALETTE["gold"])
    col_w = (x1 - x0 - 32) // 2
    for i, item in enumerate(ALSO):
        col, row = divmod(i, 2)
        ix = x0 + 16 + col * col_w
        iy = y0 + 48 + row * 28
        draw.rectangle([ix, iy + 6, ix + 7, iy + 13], fill=PALETTE["gold"])
        draw.text((ix + 16, iy), item, font=fonts["strip_item"], fill=PALETTE["white"])


def build_poster(path):
    img = Image.new("RGB", (W, H), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    fonts = _fonts()

    # masthead
    draw.rectangle([0, 0, W, 138], fill=PALETTE["navy"])
    _spaced(draw, (MARGIN, 30), LEAD["eyebrow"], fonts["eyebrow"], PALETTE["gold"])
    draw.text((MARGIN, 66), LEAD["date"], font=fonts["date"], fill=PALETTE["white"])
    draw.rectangle([0, 138, W, 144], fill=PALETTE["gold"])

    # lead story, left column; chart panel, right column
    draw.text((MARGIN, 185), LEAD["kicker"], font=fonts["kicker"], fill=PALETTE["red"])
    y = 226
    for line in LEAD["headline"]:
        draw.text((MARGIN, y), line, font=fonts["headline"], fill=PALETTE["ink"])
        y += 48
    lead_w = MARGIN + 505
    y = 374
    for line in _wrap(draw, LEAD["body"], fonts["body"], lead_w - MARGIN):
        draw.text((MARGIN, y), line, font=fonts["body"], fill=PALETTE["ink"])
        y += 29
    _chart_panel(draw, fonts, (584, 140, 984, 420))

    # divider
    draw.line([(MARGIN, 486), (W - MARGIN, 486)], fill=PALETTE["line"], width=2)

    # story grid: 2 columns x 2 rows
    card_h, card_w = 166, COL_W
    for i, story in enumerate(STORIES):
        row, col = divmod(i, 2)
        bx = MARGIN + col * (COL_W + GUTTER)
        by = 500 + row * (card_h + 16)
        _card(draw, fonts, (bx, by, bx + card_w, by + card_h), story)

    # also-today strip + footer
    _also_today(draw, fonts, (MARGIN, 862, W - MARGIN, 958))
    draw.text((MARGIN, 974), FOOTER, font=fonts["footer"], fill=PALETTE["grey"])

    img.save(path, format="PNG")
    return path
