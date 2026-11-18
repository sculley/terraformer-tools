"""Draws every texture for Terraformer Tools.

Run from the repo root:  python3 tools/render_textures.py
Needs Pillow. Writes into Terraformer_Tools_RP/ and both pack icons.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RP = ROOT / "Terraformer_Tools_RP"
BP = ROOT / "Terraformer_Tools_BP"


def hx(c, a=255):
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


# Emerald and iron palettes (light comes from the top right, like vanilla tools)
EM = {"H": hx("D9FFE9"), "L": hx("5CF39A"), "E": hx("1FC965"), "D": hx("0E8C3F"), "k": hx("06401E")}
FE = {"i": hx("E4E4E4"), "I": hx("B4B4B4"), "j": hx("767676"), "k": hx("262626")}
CLEAR = (0, 0, 0, 0)


def shade(fill, x, y):
    """Light on the top/right edges, dark on the bottom/left, mid inside."""
    up = (x, y - 1) in fill
    right = (x + 1, y) in fill
    down = (x, y + 1) in fill
    left = (x - 1, y) in fill
    if not up or not right:
        return "L" if (down and left) else "E"
    if not down or not left:
        return "D"
    return "E"


def outline(img, owners):
    """Add a 1 px outline around filled pixels; colour follows the part it touches."""
    px = img.load()
    w, h = img.size
    add = {}
    for (x, y), part in owners.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in owners:
                # head outline wins over handle outline
                if add.get((nx, ny)) != "head":
                    add[(nx, ny)] = part
    for (x, y), part in add.items():
        px[x, y] = EM["k"] if part == "head" else FE["k"]


def draw_handle(img, owners, x_from, x_to):
    """Two-pixel-wide iron rod along the x + y = 15 diagonal, with a wrapped grip."""
    px = img.load()
    for x in range(x_from, x_to + 1):
        y = 15 - x
        grip = x <= 3
        top = FE["I"] if grip and x % 2 else FE["i"]
        px[x, y] = top
        owners[(x, y)] = "handle"
        if x + 1 <= 15:
            px[x + 1, y] = FE["j"] if not grip else FE["I"] if x % 2 == 0 else FE["j"]
            owners[(x + 1, y)] = "handle"


def mirror(points):
    """Reflect across the x + y = 15 diagonal (the handle's line)."""
    return {(15 - y, 15 - x) for (x, y) in points}


def pickaxe():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    owners = {}
    draw_handle(img, owners, 1, 10)

    arm = set()
    rows = {1: [(6, 11)], 2: [(4, 12)], 3: [(2, 5), (10, 12)], 4: [(1, 2), (11, 11)]}
    for y, spans in rows.items():
        for a, b in spans:
            for x in range(a, b + 1):
                arm.add((x, y))
    head = arm | mirror(arm)
    for (x, y) in head:
        px[x, y] = EM[shade(head, x, y)]
        owners[(x, y)] = "head"
    # sparkle on the top face of the head
    for p in [(8, 1), (9, 1), (14, 7), (14, 6), (12, 2)]:
        px[p] = EM["H"]
    # iron collar where the head meets the handle
    px[10, 5] = FE["i"]
    px[11, 5] = FE["j"]
    outline(img, owners)
    return img


def spade():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    owners = {}
    draw_handle(img, owners, 1, 8)

    # Blade: a square set on its corner, like vanilla shovels, tip at the top right
    blade = {(x, y) for x in range(9, 15) for y in range(1, 7)}
    blade -= {(14, 1), (9, 6), (13, 1), (14, 2)}   # round the tip, leave room for the socket
    for (x, y) in blade:
        px[x, y] = EM[shade(blade, x, y)]
        owners[(x, y)] = "head"
    # a bright ridge down the middle of the blade
    for (x, y) in blade:
        if x + y == 15 and 10 <= x <= 12:
            px[x, y] = EM["H"]
        elif x + y == 16 and 11 <= x <= 13:
            px[x, y] = EM["D"]
    # iron socket where the blade meets the handle
    for p, c in [((8, 7), "i"), ((9, 7), "j"), ((9, 6), "i")]:
        px[p] = FE[c]
        owners[p] = "handle"
    outline(img, owners)
    return img


GUIDE = [
    "................",
    "...kkkkkkkkkk...",
    "..kSGGGGGGGGck..",
    "..kSgGGGGGGGPk..",
    "..kSgGGkkGGGPk..",
    "..kSgGkHLkGGPk..",
    "..kSgkHLEDkGPk..",
    "..kSgkLEEDkGPk..",
    "..kSgGkEDkGGPk..",
    "..kSgGGkkGGGPk..",
    "..kSgGGGGGGGPk..",
    "..kSgGGGGGGGPk..",
    "..kSddddddddPk..",
    "..kSppppppppPk..",
    "...kkkkkkkkkk...",
    "................",
]
GUIDE_PAL = {
    "k": hx("10301D"), "S": hx("0B4A27"), "G": hx("1F7A45"), "g": hx("2E9A5A"),
    "d": hx("145C33"), "P": hx("EFE4C4"), "p": hx("D9CBA3"), "c": hx("C8C8C8"),
    "H": EM["H"], "L": EM["L"], "E": EM["E"], "D": EM["D"],
}


def guide():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    for y, row in enumerate(GUIDE):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = GUIDE_PAL[ch]
    return img


def size_icon(n):
    """32x32 menu icon: a 3x3 grid with the mined area lit up."""
    img = Image.new("RGBA", (32, 32), CLEAR)
    px = img.load()
    lit = {(c, r) for r in range(3) for c in range(3)}
    if n == 1:
        lit = {(1, 1)}
    elif n == 2:
        lit = {(1, 0), (2, 0), (1, 1), (2, 1)}
    for r in range(3):
        for c in range(3):
            x0, y0 = 2 + c * 10, 2 + r * 10
            on = (c, r) in lit
            for y in range(y0, y0 + 8):
                for x in range(x0, x0 + 8):
                    edge = x in (x0, x0 + 7) or y in (y0, y0 + 7)
                    if on:
                        col = EM["k"] if edge else EM["L"] if (x - x0 < 3 and y - y0 < 3) else EM["E"]
                    else:
                        col = hx("2A2A2A", 200) if edge else hx("5A5A5A", 160)
                    px[x, y] = col
    return img


def pack_icon(pick, spd):
    """128x128: layered terrain with the two tools crossed over it."""
    s = 128
    img = Image.new("RGBA", (s, s))
    px = img.load()
    for y in range(s):
        for x in range(s):
            n = ((x * 7 + y * 13) ^ (x * y)) % 9  # cheap texture noise
            if y < 22:
                col = (110 + n * 3, 190 + n * 2, 230, 255)            # sky
            elif y < 34:
                col = (70 + n * 4, 160 + n * 4, 60 + n * 2, 255)      # grass
            elif y < 78:
                col = (120 + n * 4, 85 + n * 3, 55 + n * 2, 255)      # dirt
            else:
                col = (110 + n * 4, 110 + n * 4, 112 + n * 4, 255)    # stone
            px[x, y] = col
    big_p = pick.resize((80, 80), Image.NEAREST)
    big_s = spd.transpose(Image.FLIP_LEFT_RIGHT).resize((80, 80), Image.NEAREST)
    img.alpha_composite(big_s, (6, 26))
    img.alpha_composite(big_p, (42, 26))
    return img


def main():
    items = RP / "textures" / "items"
    ui = RP / "textures" / "ui"
    items.mkdir(parents=True, exist_ok=True)
    ui.mkdir(parents=True, exist_ok=True)
    p, s, g = pickaxe(), spade(), guide()
    p.save(items / "terraformer_pickaxe.png")
    s.save(items / "terraformer_spade.png")
    g.save(items / "terraformer_guide.png")
    for n in (1, 2, 3):
        size_icon(n).save(ui / f"terraformer_size_{n}.png")
    icon = pack_icon(p, s)
    icon.save(RP / "pack_icon.png")
    BP.mkdir(exist_ok=True)
    icon.save(BP / "pack_icon.png")


if __name__ == "__main__":
    main()
