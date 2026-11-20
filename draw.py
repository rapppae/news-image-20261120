"""Poster painter for the 20 November 2026 world-news sheet.

All of the day's news lives in the EDITION table at the top: one lead
story, four card stories, a strip of shorter items and a footer line.
The painter below only knows geometry, so a different day means a
different table, not different drawing code.

Layout (1024 x 1024, all coordinates in pixels):
    masthead band, lead row (words left, chart right),
    a 2 x 2 grid of cards, an "also today" band, a footer line.
"""

from PIL import Image, ImageDraw, ImageFont

SHEET_W, SHEET_H = 1024, 1024
EDGE = 40
GAP = 24

PAPER = (247, 243, 232)
INK = (22, 28, 44)
BODY_INK = (52, 52, 50)
MUTED = (96, 96, 92)
NAVY = (23, 35, 61)
DEEP = (16, 26, 48)
BUILDING = (38, 54, 92)
CARD_BG = (255, 255, 255)
CARD_LINE = (203, 196, 178)
RULE_LINE = (201, 194, 176)
GOLD = (212, 175, 55)
GOLD_PALE = (226, 196, 110)
CRIMSON = (178, 34, 52)
TEAL = (15, 118, 110)
WHITE = (255, 255, 255)
SKY_BLUE = (140, 190, 220)

EDITION = {
    "kicker": "THE WORLD IN ONE DAY",
    "dateline": "FRIDAY, 20 NOVEMBER 2026",
    "lead": {
        "tag": "WALL STREET  \u00b7  THE BIGGEST IPO EVER",
        "headline": "Anthropic's $81bn debut tops the record books",
        "body": (
            "Claude's maker priced its shares at $83, opened at $111.50 "
            "\u2014 up 34% \u2014 and closed 17% higher at $97.17, worth "
            "about $1.75 trillion. The largest IPO ever."
        ),
    },
    "cards": [
        {
            "tag": "THE HAGUE  \u00b7  JUSTICE",
            "headline": "World court: Myanmar guilty of genocide",
            "body": (
                "The ICJ rules 9\u20136 that Myanmar committed genocide "
                "\u2014 a first in 80 years."
            ),
            "glyph": "scales",
        },
        {
            "tag": "GAMES  \u00b7  CULTURE",
            "headline": "GTA VI: a $2.36bn opening day",
            "body": (
                "About 24.5m copies sold on day one \u2014 the biggest "
                "entertainment launch ever."
            ),
            "glyph": "bars",
        },
        {
            "tag": "WEATHER  \u00b7  INDIA",
            "headline": "Cyclone Akvan makes landfall",
            "body": (
                "The storm hits India's east coast at midday; 300,000 "
                "people were moved to safety."
            ),
            "glyph": "swirl",
        },
        {
            "tag": "DIPLOMACY  \u00b7  SHENZHEN",
            "headline": "Three presidents sign a peace declaration",
            "body": (
                "Trump, Xi and Putin end a 90-minute trilateral summit "
                "with a joint declaration of peace."
            ),
            "glyph": "globe",
        },
    ],
    "also": [
        "Nasdaq falls 2.3% as the AI trade wobbles",
        "COP31 draft drops fossil fuels",
        "US loses measles-free status after 26 years",
        "Iran drones hit a US radar in Bahrain",
    ],
    "footer": (
        "All stories as reported on 20 November 2026  \u00b7  "
        "Sources: Reuters, WSJ, Barron's, BBC, CNN, IMD"
    ),
}


class Fonts:
    """The bundled DejaVu faces, loaded once and cached by size."""

    def __init__(self, folder):
        self.plain = folder + "/DejaVuSans.ttf"
        self.heavy = folder + "/DejaVuSans-Bold.ttf"
        self.seen = {}

    def get(self, size, bold=False):
        key = (size, bold)
        if key not in self.seen:
            self.seen[key] = ImageFont.truetype(
                self.heavy if bold else self.plain, size)
        return self.seen[key]


def wrap_lines(draw, text, font, width):
    """Break text into lines that fit `width`, one word at a time."""
    out, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def spaced_text(draw, xy, text, font, fill, gap):
    """Draw text with extra space between letters (masthead kicker)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + gap
    return x


def draw_masthead(draw, fonts):
    draw.rectangle([0, 0, SHEET_W, 148], fill=NAVY)
    spaced_text(draw, (EDGE, 26), EDITION["kicker"],
                fonts.get(26, bold=True), GOLD, 7)
    draw.text((EDGE, 58), EDITION["dateline"],
              font=fonts.get(52, bold=True), fill=WHITE)
    draw.rectangle([0, 148, SHEET_W, 154], fill=GOLD)


def draw_lead_chart(draw, box, fonts):
    """Rising ANT chart over a night skyline inside the lead panel."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=DEEP)
    for sx, sy in ((36, 30), (120, 58), (200, 24), (290, 66),
                   (350, 34), (80, 96), (240, 108), (330, 118)):
        draw.ellipse([x0 + sx - 2, y0 + sy - 2, x0 + sx + 2, y0 + sy + 2],
                     fill=GOLD_PALE)
    for bx, bw, top in ((10, 56, 400), (80, 52, 384), (146, 60, 404),
                        (220, 54, 378), (288, 52, 398), (344, 44, 388)):
        draw.rectangle([x0 + bx, top, x0 + bx + bw, y1],
                       fill=BUILDING)
        for wy in range(top + 12, 436, 24):
            for wx in (bx + 11, bx + bw - 19):
                draw.rectangle(
                    [x0 + wx, wy, x0 + wx + 7, wy + 9],
                    fill=GOLD_PALE)
    pts = [(606, 392), (656, 372), (706, 382), (756, 336),
           (806, 296), (856, 248), (906, 224), (956, 208)]
    draw.line(pts, fill=GOLD, width=4)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=GOLD)
    draw.text((x0 + 20, y0 + 14), "ANT",
              font=fonts.get(44, bold=True), fill=GOLD)
    draw.text((x0 + 20, y0 + 66), "+34% AT THE OPEN",
              font=fonts.get(20, bold=True), fill=WHITE)
    draw.rectangle([x0 + 12, y0 + 94, x1 - 12, y0 + 126], fill=DEEP)
    draw.text((x0 + 20, y0 + 100), "$83 IPO  \u2192  $111.50 open  \u00b7  $97.17 close",
              font=fonts.get(18), fill=WHITE)


def draw_lead(draw, fonts):
    top = 182
    panel = (584, top, SHEET_W - EDGE, top + 268)
    draw_lead_chart(draw, panel, fonts)
    text_w = 584 - EDGE - 28
    draw.text((EDGE, top), EDITION["lead"]["tag"],
              font=fonts.get(21, bold=True), fill=CRIMSON)
    y = top + 38
    for line in wrap_lines(draw, EDITION["lead"]["headline"],
                           fonts.get(40, bold=True), text_w):
        draw.text((EDGE, y), line, font=fonts.get(40, bold=True), fill=INK)
        y += 48
    y += 8
    for line in wrap_lines(draw, EDITION["lead"]["body"],
                           fonts.get(21), text_w):
        draw.text((EDGE, y), line, font=fonts.get(21), fill=BODY_INK)
        y += 29
    draw.line([EDGE, 486, SHEET_W - EDGE, 486], fill=RULE_LINE, width=2)


def draw_emblem(draw, box, kind, fonts):
    """Small square emblem drawn from primitives, one per card."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=NAVY)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "scales":
        draw.line([cx, y0 + 10, cx, y1 - 14], fill=WHITE, width=3)
        draw.line([cx - 26, y0 + 16, cx + 26, y0 + 16], fill=WHITE, width=3)
        for sx in (cx - 26, cx + 26):
            draw.line([sx, y0 + 16, sx, y0 + 34], fill=GOLD, width=2)
            draw.polygon([(sx - 12, y0 + 34), (sx + 12, y0 + 34),
                          (sx, y0 + 48)], outline=GOLD, width=2)
        draw.line([cx - 14, y1 - 12, cx + 14, y1 - 12], fill=GOLD, width=3)
    elif kind == "bars":
        draw.text((cx, y0 + 6), "VI", font=fonts.get(22, bold=True),
                  fill=WHITE, anchor="ma")
        tops = (20, 26, 30, 34)
        for i, top in enumerate(tops):
            bx = x0 + 10 + i * 15
            draw.rectangle([bx, y1 - 10 - top, bx + 11, y1 - 10], fill=GOLD)
    elif kind == "swirl":
        for r in (30, 22, 14):
            draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
                     fill=WHITE, width=3)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)
        for rx in (18, 40, 62):
            draw.line([x0 + rx, y1 - 16, x0 + rx - 5, y1 - 6],
                      fill=SKY_BLUE, width=2)
    elif kind == "globe":
        draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30],
                     outline=WHITE, width=3)
        draw.ellipse([cx - 12, cy - 30, cx + 12, cy + 30],
                     outline=WHITE, width=2)
        draw.line([cx - 30, cy, cx + 30, cy], fill=WHITE, width=2)
        draw.line([cx - 26, cy - 18, cx + 26, cy - 18], fill=WHITE, width=2)
        draw.ellipse([cx + 12, cy - 26, cx + 22, cy - 16], fill=GOLD)


def draw_card(draw, fonts, item, box):
    """Icon + tag + headline up top, body text full-width underneath."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=CARD_BG, outline=CARD_LINE, width=2)
    draw.rectangle([x0, y0, x1, y0 + 7], fill=TEAL)
    emblem = (x0 + 16, y0 + 16, x0 + 92, y0 + 92)
    draw_emblem(draw, emblem, item["glyph"], fonts)
    tx = x0 + 108
    tw = x1 - tx - 16
    draw.text((tx, y0 + 18), item["tag"], font=fonts.get(17, bold=True),
              fill=CRIMSON)
    y = y0 + 42
    for line in wrap_lines(draw, item["headline"],
                           fonts.get(24, bold=True), tw):
        draw.text((tx, y), line, font=fonts.get(24, bold=True), fill=INK)
        y += 29
    by = y0 + 104
    for line in wrap_lines(draw, item["body"], fonts.get(18),
                           x1 - x0 - 32):
        draw.text((x0 + 16, by), line, font=fonts.get(18), fill=BODY_INK)
        by += 24


def draw_grid(draw, fonts):
    cw = (SHEET_W - 2 * EDGE - GAP) // 2
    ch = 168
    top = 500
    for i, item in enumerate(EDITION["cards"]):
        col, row = i % 2, i // 2
        x0 = EDGE + col * (cw + GAP)
        y0 = top + row * (ch + 14)
        draw_card(draw, fonts, item, (x0, y0, x0 + cw, y0 + ch))


def draw_also(draw, fonts):
    y0, y1 = 862, 960
    draw.rectangle([EDGE, y0, SHEET_W - EDGE, y1], fill=NAVY)
    draw.text((EDGE + 18, y0 + 12), "ALSO TODAY",
              font=fonts.get(22, bold=True), fill=GOLD)
    col_w = (SHEET_W - 2 * EDGE - 36 - GAP) // 2
    for i, entry in enumerate(EDITION["also"]):
        col, row = i % 2, i // 2
        x = EDGE + 18 + col * (col_w + GAP)
        y = y0 + 46 + row * 28
        draw.text((x, y), "\u00b7", font=fonts.get(19, bold=True),
                  fill=GOLD_PALE)
        draw.text((x + 16, y), entry, font=fonts.get(18), fill=WHITE)


def draw_footer(draw, fonts):
    draw.text((EDGE, 974), EDITION["footer"], font=fonts.get(17),
              fill=MUTED)


def compose(assets_dir):
    """Build the whole poster and hand back a PIL image."""
    fonts = Fonts(assets_dir)
    sheet = Image.new("RGB", (SHEET_W, SHEET_H), PAPER)
    draw = ImageDraw.Draw(sheet)
    draw_masthead(draw, fonts)
    draw_lead(draw, fonts)
    draw_grid(draw, fonts)
    draw_also(draw, fonts)
    draw_footer(draw, fonts)
    return sheet
