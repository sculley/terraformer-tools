"""README artwork: docs/images/banner.png, items.png, recipes.png and sizes.png.

Run from the repo root:  python3 tools/render_docs.py
Needs Pillow and the DejaVu fonts. Every picture is original pixel art drawn here
(the tool icons are the add-on's own textures).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(ROOT, "docs", "images")
ITEMS = os.path.join(ROOT, "Terraformer_Tools_RP", "textures", "items")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

BG_TOP, BG_BOTTOM = (18, 54, 38), (6, 18, 12)
MINT, MUTED = (196, 255, 220), (150, 196, 170)
EMERALD, EMERALD_DARK = (31, 201, 101), (6, 64, 30)


# ---------- helpers ----------

def h(*v):
    """Deterministic 0..1 noise from integers."""
    n = 0
    for i, x in enumerate(v):
        n = (n * 31 + int(x) * (i + 7) * 2654435761) & 0xFFFFFFFF
    n ^= n >> 13
    n = (n * 1274126177) & 0xFFFFFFFF
    return (n & 0xFFFF) / 0xFFFF


def noisy(base, x, y, seed, amt=0.12):
    f = 1 + (h(x, y, seed) - 0.5) * 2 * amt
    return tuple(max(0, min(255, int(c * f))) for c in base)


def background(w, h_, sparkles=70):
    img = Image.new("RGB", (w, h_))
    d = ImageDraw.Draw(img)
    for y in range(h_):
        t = y / h_
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)))
    rnd = random.Random(5)
    for _ in range(sparkles):
        x, y, s = rnd.randrange(w), rnd.randrange(h_), rnd.choice([2, 2, 2, 4])
        d.rectangle([x, y, x + s - 1, y + s - 1], fill=rnd.choice([(120, 240, 170), (60, 170, 110), (230, 255, 240)]))
    return img


def pixel_text(text, size, colour, scale):
    """Crisp blocky text: render small without antialiasing, then scale up."""
    font = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", size)
    l, t, r, b = font.getbbox(text)
    small = Image.new("RGBA", (r - l + 2, b - t + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(small)
    d.fontmode = "1"
    d.text((1 - l, 1 - t), text, font=font, fill=colour)
    return small.resize((small.width * scale, small.height * scale), Image.NEAREST)


def paste_text(img, text, size, colour, scale, centre_x, top, shadow=(4, 24, 12)):
    sh = pixel_text(text, size, shadow + (255,), scale)
    fg = pixel_text(text, size, colour + (255,), scale)
    x = int(centre_x - fg.width / 2)
    img.paste(sh, (x + scale, top + scale), sh)
    img.paste(fg, (x, top), fg)


def item(name):
    return Image.open(os.path.join(ITEMS, name)).convert("RGBA")


def blank():
    return Image.new("RGBA", (16, 16), (0, 0, 0, 0))


def from_rows(rows, palette):
    img = blank()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in palette:
                img.putpixel((x, y), palette[ch] + (255,))
    return img


# ---------- 16x16 block textures ----------

def grass_block():
    img = blank()
    for y in range(16):
        for x in range(16):
            edge = 3 + int(h(x, 9) * 3)
            if y < edge:
                c = noisy((92, 170, 60), x, y, 1, 0.14)
            else:
                c = noisy((134, 96, 62), x, y, 2, 0.16)
            img.putpixel((x, y), c + (255,))
    return img


def dirt_block():
    img = blank()
    for y in range(16):
        for x in range(16):
            img.putpixel((x, y), noisy((134, 96, 62), x, y, 3, 0.18) + (255,))
    return img


def stone_block():
    img = blank()
    for y in range(16):
        for x in range(16):
            c = noisy((126, 126, 130), x, y, 4, 0.12)
            if h(x // 2, y, 8) > 0.9:
                c = (98, 98, 104)
            img.putpixel((x, y), c + (255,))
    return img


def emerald_ore():
    img = stone_block()
    for (x, y) in [(4, 4), (5, 4), (4, 5), (10, 9), (11, 9), (11, 10), (6, 11), (7, 11)]:
        img.putpixel((x, y), (40, 220, 120, 255))
    for (x, y) in [(5, 5), (10, 10), (6, 12)]:
        img.putpixel((x, y), (8, 110, 50, 255))
    return img


# ---------- 16x16 ingredient icons ----------

def emerald():
    return from_rows([
        "................",
        "................",
        "......kkkk......",
        ".....kHLLLk.....",
        "....kHLLEEDk....",
        "...kLLLEEEEDk...",
        "...kLEEEEEEDk...",
        "..kLEEEEEEEEDk..",
        "..kEEEEEEEEDDk..",
        "...kEEEEEEDDk...",
        "...kEEEEEDDDk...",
        "....kDEEDDDk....",
        ".....kDDDDk.....",
        "......kkkk......",
        "................",
        "................",
    ], {"k": EMERALD_DARK, "H": (217, 255, 233), "L": (92, 243, 154), "E": EMERALD, "D": (14, 140, 63)})


def iron_ingot():
    return from_rows([
        "................",
        "................",
        "................",
        "................",
        ".......kkkkkk...",
        ".....kkWWWWLLk..",
        "...kkWWLLLLLMk..",
        "..kWWLLLLLLMMk..",
        "..kLLLLLLLMMDk..",
        "..kMMLLLLMMDDk..",
        "..kDMMMMMMDDk...",
        "...kkDDDDDkk....",
        ".....kkkkk......",
        "................",
        "................",
        "................",
    ], {"k": (40, 40, 44), "W": (246, 246, 246), "L": (214, 214, 214), "M": (170, 170, 170), "D": (118, 118, 122)})


def book():
    img = blank()
    d = ImageDraw.Draw(img)
    d.rectangle([3, 2, 12, 13], fill=(120, 66, 36, 255))
    d.rectangle([11, 3, 13, 14], fill=(236, 228, 206, 255))
    d.line([(11, 14), (13, 14)], fill=(190, 180, 160, 255))
    d.rectangle([3, 2, 4, 13], fill=(84, 44, 22, 255))
    d.rectangle([6, 5, 9, 6], fill=(160, 100, 60, 255))
    return img


ICONS = {}


def icon(name, size):
    if not ICONS:
        ICONS.update({
            "emerald": emerald(), "iron": iron_ingot(), "book": book(),
            "pickaxe": item("terraformer_pickaxe.png"), "spade": item("terraformer_spade.png"),
            "guide": item("terraformer_guide.png"),
        })
    return ICONS[name].resize((size, size), Image.NEAREST)


# ---------- banner ----------

def glow(img, box, colour, radius):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle(box, outline=colour + (200,), width=radius)
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    img.paste(layer, (0, 0), layer)


def banner():
    W, H = 1280, 490
    img = background(W, H).convert("RGBA")
    B = 64                       # one block on screen
    top = H - 3 * B              # three rows of terrain at the bottom
    textures = [grass_block(), dirt_block(), stone_block()]
    cols = W // B + 1
    hole = range(cols // 2 - 1, cols // 2 + 2)   # a 3-wide gap dug out of the middle

    for row in range(3):
        for col in range(cols):
            x, y = col * B - 8, top + row * B
            tex = textures[row]
            if row == 2 and h(col, 77) > 0.82:
                tex = emerald_ore()
            if col in hole:
                # dug out: show the darker back wall, like looking into a cut
                back = tex.resize((B, B), Image.NEAREST)
                back = Image.blend(back, Image.new("RGBA", back.size, (10, 20, 14, 255)), 0.62)
                img.paste(back, (x, y))
            else:
                img.paste(tex.resize((B, B), Image.NEAREST), (x, y))

    x0 = hole[0] * B - 8
    glow(img, [x0, top, x0 + 3 * B - 1, top + 3 * B - 1], (60, 255, 150), 6)
    d = ImageDraw.Draw(img)
    for i in range(0, 3 * B, 12):  # dashed outline of the mined 3x3
        for (a, b) in [((x0 + i, top), (x0 + i + 6, top)), ((x0 + i, top + 3 * B - 2), (x0 + i + 6, top + 3 * B - 2)),
                       ((x0, top + i), (x0, top + i + 6)), ((x0 + 3 * B - 2, top + i), (x0 + 3 * B - 2, top + i + 6))]:
            d.line([a, b], fill=MINT, width=3)

    # block bits flying out of the hole
    rnd = random.Random(11)
    for _ in range(26):
        cx = x0 + 3 * B / 2 + rnd.uniform(-130, 130)
        cy = top - rnd.uniform(6, 34)
        s = rnd.choice([6, 8, 10])
        colour = rnd.choice([(92, 170, 60), (134, 96, 62), (126, 126, 130), (40, 220, 120)])
        d.rectangle([cx, cy, cx + s, cy + s], fill=colour, outline=(20, 30, 24))

    # the two tools, big, either side of the title
    pick = icon("pickaxe", 192)
    spade = icon("spade", 192).transpose(Image.FLIP_LEFT_RIGHT)
    for im, pos in [(pick, (36, 56)), (spade, (W - 36 - 192, 56))]:
        shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
        shadow.paste((0, 0, 0, 110), (0, 0), im)
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)), (pos[0] + 8, pos[1] + 10))
        img.alpha_composite(im, pos)

    paste_text(img, "TERRAFORMER", 22, MINT, 4, W / 2, 34)
    paste_text(img, "TOOLS", 22, (92, 243, 154), 4, W / 2, 130)
    paste_text(img, "Instant  ·  Unbreakable  ·  1×1  2×2  3×3", 11, MUTED, 2, W / 2, 226)
    img.convert("RGB").save(os.path.join(IMAGES, "banner.png"))


# ---------- item cards ----------

CARD, CARD_EDGE = (16, 44, 30), (40, 120, 76)


def items():
    W, H = 1200, 400
    img = background(W, H, sparkles=36).convert("RGBA")
    d = ImageDraw.Draw(img)
    cards = [("pickaxe", "Terraformer Pickaxe", "Stone, ores, deepslate"),
             ("spade", "Terraformer Spade", "Dirt, sand, gravel, snow"),
             ("guide", "Terraformer Tools Guide", "Every player gets one")]
    cw = W // 3
    for i, (key, name, note) in enumerate(cards):
        cx = i * cw + cw // 2
        d.rounded_rectangle([i * cw + 16, 16, (i + 1) * cw - 16, H - 16], 18, fill=CARD, outline=CARD_EDGE, width=2)
        ic = icon(key, 176)
        img.alpha_composite(ic, (cx - 88, 64))
        paste_text(img, name, 13, MINT, 2, cx, 282)
        paste_text(img, note, 10, MUTED, 2, cx, 336)
    img.convert("RGB").save(os.path.join(IMAGES, "items.png"))


# ---------- recipes ----------

SLOT_IN, SLOT_DARK, SLOT_LIGHT = (28, 66, 46), (8, 26, 16), (58, 120, 86)


def slot(size, border=4):
    s = Image.new("RGBA", (size, size), SLOT_IN + (255,))
    d = ImageDraw.Draw(s)
    d.rectangle([0, 0, size - 1, border - 1], fill=SLOT_DARK)
    d.rectangle([0, 0, border - 1, size - 1], fill=SLOT_DARK)
    d.rectangle([0, size - border, size - 1, size - 1], fill=SLOT_LIGHT)
    d.rectangle([size - border, 0, size - 1, size - 1], fill=SLOT_LIGHT)
    return s


def arrow(size):
    a = from_rows([
        "................", "................", "................", "................",
        "........LL......", "........LLL.....", "..LLLLLLLLLL....", "..LLLLLLLLLLL...",
        "..LLLLLLLLLLL...", "..LLLLLLLLLL....", "........LLL.....", "........LL......",
        "................", "................", "................", "................",
    ], {"L": MINT})
    return a.resize((size, size), Image.NEAREST)


def recipe_panel(grid, result, title, note):
    S, G = 76, 6
    W, H = 3 * S + 2 * G + 130 + S + 40, 3 * S + 2 * G + 120
    p = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle([0, 0, W - 1, H - 1], 16, fill=CARD, outline=CARD_EDGE, width=2)
    gx, gy = 20, 64
    for r in range(3):
        for c in range(3):
            s = slot(S)
            name = grid[r][c]
            if name:
                s.alpha_composite(icon(name, 56), (10, 10))
            p.alpha_composite(s, (gx + c * (S + G), gy + r * (S + G)))
    ax = gx + 3 * S + 2 * G + 22
    p.alpha_composite(arrow(80), (ax, gy + S + G - 2))
    out = slot(S + 16)
    out.alpha_composite(icon(result, 68), (12, 12))
    p.alpha_composite(out, (ax + 96, gy + S + G - 8))
    paste_text(p, title, 11, MINT, 2, W / 2, 18)
    paste_text(p, note, 9, MUTED, 2, W / 2, H - 40)
    return p


def recipes():
    E, I, B = "emerald", "iron", "book"
    panels = [
        recipe_panel([[E, E, E], [None, I, None], [None, I, None]], "pickaxe", "Terraformer Pickaxe", "3 Emeralds + 2 Iron Ingots"),
        recipe_panel([[None, E, None], [None, I, None], [None, I, None]], "spade", "Terraformer Spade", "1 Emerald + 2 Iron Ingots"),
        recipe_panel([[B, E, None], [None, None, None], [None, None, None]], "guide", "Terraformer Tools Guide", "Book + Emerald, any slots"),
    ]
    pw, ph = panels[0].size
    W = 3 * pw + 4 * 24
    img = background(W, ph + 48, sparkles=30).convert("RGBA")
    for i, p in enumerate(panels):
        img.alpha_composite(p, (24 + i * (pw + 24), 24))
    img.convert("RGB").save(os.path.join(IMAGES, "recipes.png"))


# ---------- mining sizes ----------

def sizes():
    B, N = 44, 5                      # a 5x5 stone wall per panel
    pw = N * B + 48
    W, H = 3 * pw + 4 * 24, N * B + 150
    img = background(W, H, sparkles=24).convert("RGBA")
    d = ImageDraw.Draw(img)
    stone = stone_block().resize((B, B), Image.NEAREST)
    dug = Image.blend(stone, Image.new("RGBA", stone.size, (10, 20, 14, 255)), 0.65)
    areas = {
        1: {(2, 2)},
        2: {(2, 2), (3, 2), (2, 1), (3, 1)},          # hit block, plus up and to the right
        3: {(c, r) for c in (1, 2, 3) for r in (1, 2, 3)},
    }
    notes = {1: "Just the block you hit", 2: "Hit block, up and right", 3: "Centred on that block"}
    for i, n in enumerate((1, 2, 3)):
        px0 = 24 + i * (pw + 24)
        d.rounded_rectangle([px0, 16, px0 + pw, H - 16], 16, fill=CARD, outline=CARD_EDGE, width=2)
        gx, gy = px0 + 24, 70
        for r in range(N):
            for c in range(N):
                img.alpha_composite(dug if (c, r) in areas[n] else stone, (gx + c * B, gy + r * B))
        # mark the block you hit
        hx_, hy_ = gx + 2 * B, gy + 2 * B
        d.rectangle([hx_ + 2, hy_ + 2, hx_ + B - 3, hy_ + B - 3], outline=MINT, width=3)
        cells = areas[n]
        xs = [c for c, _ in cells]
        ys = [r for _, r in cells]
        glow(img, [gx + min(xs) * B, gy + min(ys) * B, gx + (max(xs) + 1) * B - 1, gy + (max(ys) + 1) * B - 1], (60, 255, 150), 4)
        paste_text(img, f"{n} × {n}", 14, MINT, 3, px0 + pw / 2, 24)
        paste_text(img, notes[n], 9, MUTED, 2, px0 + pw / 2, H - 64)
    img.convert("RGB").save(os.path.join(IMAGES, "sizes.png"))


if __name__ == "__main__":
    os.makedirs(IMAGES, exist_ok=True)
    banner()
    items()
    recipes()
    sizes()
    print("rendered banner.png, items.png, recipes.png and sizes.png")
