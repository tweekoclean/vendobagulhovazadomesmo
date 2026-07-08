#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MENU de Lanches - layout em 2 colunas, fundo preto, caixas de preco em branco."""

from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1400, 1980
OUT = "/projects/sandbox/cardapio/menu-lanches.png"

BLACK  = (0, 0, 0)
ORANGE = (245, 102, 18)
RED    = (219, 22, 12)
WHITE  = (255, 255, 255)
GRAY   = (208, 208, 208)

REG = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf"
ITA = "/usr/share/fonts/google-noto-vf/NotoSans-Italic[wght].ttf"

def font(path, size, weight=400):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]

def th(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[3] - b[1]

def wrap(d, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ---------------- background ----------------
img = Image.new("RGB", (W, H), BLACK)
d = ImageDraw.Draw(img)

# subtle diagonal checker texture (very dark) to echo the reference, still "black"
tile = 46
for gy in range(-1, H // tile + 2):
    for gx in range(-1, W // tile + 2):
        if (gx + gy) % 2 == 0:
            x = gx * tile
            y = gy * tile
            d.polygon([(x + tile/2, y), (x + tile, y + tile/2),
                       (x + tile/2, y + tile), (x, y + tile/2)], fill=(15, 15, 15))

# ---------------- burger illustration ----------------
def draw_burger(d, cx, cy, s):
    # s = scale (half width)
    # bottom bun
    d.rounded_rectangle([cx-s, cy+s*0.55, cx+s, cy+s*0.95], radius=int(s*0.35), fill=(196,120,52))
    # patty
    d.rounded_rectangle([cx-s*1.02, cy+s*0.32, cx+s*1.02, cy+s*0.62], radius=int(s*0.2), fill=(74,44,26))
    # cheese (two triangles hanging)
    d.polygon([(cx-s, cy+s*0.28),(cx+s, cy+s*0.28),(cx+s*0.5, cy+s*0.6)], fill=(240,176,40))
    d.polygon([(cx-s, cy+s*0.28),(cx+s, cy+s*0.28),(cx-s*0.4, cy+s*0.58)], fill=(240,176,40))
    d.rectangle([cx-s, cy+s*0.2, cx+s, cy+s*0.3], fill=(240,176,40))
    # lettuce (wavy green)
    pts=[]
    n=10
    for i in range(n+1):
        x = cx - s*1.05 + (2*s*1.05)*i/n
        y = cy+s*0.12 + (s*0.10 if i%2 else 0)
        pts.append((x,y))
    pts += [(cx+s*1.05, cy+s*0.28),(cx-s*1.05, cy+s*0.28)]
    d.polygon(pts, fill=(96,168,74))
    # tomato
    d.ellipse([cx-s*0.55, cy+s*0.02, cx+s*0.55, cy+s*0.22], fill=(206,54,40))
    # top bun (dome)
    d.pieslice([cx-s, cy-s*0.75, cx+s, cy+s*0.35], 180, 360, fill=(214,138,66))
    # sesame seeds
    for (dx,dy) in [(-0.45,-0.15),(-0.15,-0.3),(0.2,-0.28),(0.5,-0.1),(0.0,-0.05),(-0.3,0.05),(0.35,0.05)]:
        sx, sy = cx+dx*s, cy+dy*s
        d.ellipse([sx-4, sy-2, sx+4, sy+2], fill=(245,232,200))

def draw_soda(d, cx, cy, s):
    # cup trapezoid
    d.polygon([(cx-s*0.7, cy-s), (cx+s*0.7, cy-s), (cx+s*0.5, cy+s), (cx-s*0.5, cy+s)], fill=(38,38,42))
    # lid
    d.rectangle([cx-s*0.8, cy-s*1.18, cx+s*0.8, cy-s*0.95], fill=(70,70,74))
    d.ellipse([cx-s*0.8, cy-s*1.28, cx+s*0.8, cy-s*1.08], fill=(90,90,94))
    # straw
    d.line([(cx+s*0.15, cy-s*1.9),(cx+s*0.3, cy-s*1.1)], fill=(230,60,60), width=int(s*0.14))
    # cola highlight
    d.polygon([(cx-s*0.55, cy-s*0.7),(cx-s*0.35, cy-s*0.7),(cx-s*0.3, cy+s*0.7),(cx-s*0.45, cy+s*0.7)], fill=(60,60,66))

draw_burger(d, W-360, 210, 150)
draw_soda(d, W-150, 210, 92)

# ---------------- title ----------------
f_menu = font(ITA, 190, 900)
d.text((60, 40), "MENU", font=f_menu, fill=WHITE)
menu_w = tw(d, "MENU", f_menu)
f_de = font(ITA, 70, 800)
d.text((70, 245), "de", font=f_de, fill=ORANGE)
de_w = tw(d, "de", f_de)
f_lan = font(ITA, 150, 900)
d.text((70 + de_w + 24, 210), "Lanches", font=f_lan, fill=ORANGE)

# ---------------- columns setup ----------------
MARGIN = 56
col_gap = 48
col_w = (W - MARGIN*2 - col_gap) // 2
col_x = [MARGIN, MARGIN + col_w + col_gap]

box_w = 100
box_gap = 12
price_area = box_w*2 + box_gap          # width of the two price boxes
box_h = 48

HEADER_Y = 430

def draw_col_headers(cx):
    """Two red header tags above the price boxes of a column."""
    right = cx + col_w
    fh = font(REG, 18, 800)
    labels = ["Pão de\nHamburguer", "Pão\nFrancês"]
    xs = [right - price_area, right - box_w]
    for x, lab in zip(xs, labels):
        d.rounded_rectangle([x, HEADER_Y, x + box_w, HEADER_Y + 52], radius=7, fill=RED)
        parts = lab.split("\n")
        ty = HEADER_Y + 26 - (len(parts)*20)//2
        for p in parts:
            d.text((x + (box_w - tw(d, p, fh))/2, ty), p, font=fh, fill=WHITE)
            ty += 20

def draw_items(cx, items):
    right = cx + col_w
    text_max = col_w - price_area - 16
    name_f = font(ITA, 33, 900)
    desc_f = font(REG, 16, 600)
    y = HEADER_Y + 78
    for name, desc in items:
        nb_h = th(d, name, name_f)
        d.text((cx, y), name, font=name_f, fill=ORANGE)
        # two empty white price boxes aligned to headers, centered on name row
        row_cy = y + nb_h/2
        xs = [right - price_area, right - box_w]
        for bx in xs:
            d.rounded_rectangle([bx, row_cy - box_h/2, bx + box_w, row_cy + box_h/2],
                                radius=7, fill=WHITE)
        y += nb_h + 8
        for ln in wrap(d, desc, desc_f, text_max):
            d.text((cx, y), ln, font=desc_f, fill=GRAY)
            y += th(d, ln, desc_f) + 6
        y += 20

# ---------------- data ----------------
left = [
    ("HAMBÚRGUER", "CARNE, ALFACE, TOMATE, CEBOLA, KETCHUP, MOSTARDA, MAIONESE E BATATA PALHA"),
    ("HAMBÚRGUER CATUPIRY", "CARNE, ALFACE, TOMATE, CATUPIRY, CEBOLA, KETCHUP, MOSTARDA, MAIONESE E BATATA PALHA"),
    ("X-BÚRGUER", "CARNE, KETCHUP, QUEIJO, MOSTARDA, MAIONESE E BATATA PALHA"),
    ("HOT-DOG", "2 SALSICHAS, ALFACE, TOMATE, CEBOLA, MAIONESE, KETCHUP, MOSTARDA E BATATA PALHA"),
    ("X-SALADA", "CARNE, ALFACE, TOMATE, PRESUNTO, QUEIJO, CEBOLA, KETCHUP, MOSTARDA, MAIONESE E BATATA PALHA"),
    ("X-BACON", "CARNE, QUEIJO, PRESUNTO, ALFACE, TOMATE, CEBOLA, MAIONESE, KETCHUP, MOSTARDA, BATATA PALHA E BACON"),
    ("X-EGG", "CARNE, ALFACE, TOMATE, CEBOLA, KETCHUP, MOSTARDA, MAIONESE, BATATA PALHA, PRESUNTO, OVO E QUEIJO"),
    ("X-EGG BACON", "CARNE, ALFACE, TOMATE, CEBOLA, KETCHUP, MOSTARDA, MAIONESE, BATATA PALHA, PRESUNTO, OVO, QUEIJO E BACON"),
    ("BIG CHEDDAR", "2 CARNES, ALFACE, TOMATE, CEBOLA, CHEDDAR, MAIONESE, MOSTARDA, KETCHUP E BATATA PALHA"),
    ("FRANGO ESPECIAL", "FRANGO DESFIADO, CATUPIRY, MILHO, TOMATE, CEBOLA, BATATA PALHA, ALFACE, KETCHUP, MAIONESE E MOSTARDA"),
]
right = [
    ("X-TUDO", "CARNE, QUEIJO, PRESUNTO, ALFACE, TOMATE, CEBOLA, MAIONESE, KETCHUP, MOSTARDA, BATATA PALHA, OVO, BACON E SALSICHA"),
    ("X-HOT DOG", "4 SALSICHAS, ALFACE, TOMATE, CEBOLA, MAIONESE, KETCHUP, MOSTARDA, BATATA PALHA, QUEIJO E MILHO"),
    ("HAMBURGÃO", "2 CARNES, ALFACE, TOMATE, CEBOLA, MILHO, QUEIJO, MAIONESE, MOSTARDA, KETCHUP E BATATA PALHA"),
    ("MISTO QUENTE", "PRESUNTO, QUEIJO, TOMATE, CEBOLA, MAIONESE, MOSTARDA, KETCHUP E BATATA PALHA"),
    ("X-CAIPIRA", "FILÉ DE FRANGO, ALFACE, TOMATE, CEBOLA, QUEIJO, BACON, MAIONESE, MOSTARDA, KETCHUP E BATATA PALHA"),
    ("LOMBO", "LOMBO, BACON, QUEIJO, ALFACE, TOMATE, CEBOLA, MAIONESE, MOSTARDA, KETCHUP E BATATA PALHA"),
    ("AZEITONADO", "2 CARNES, AZEITONA, ALFACE, TOMATE, CEBOLA, KETCHUP, MAIONESE, MOSTARDA E BATATA PALHA"),
    ("CHURRASCO", "CONTRA FILÉ, QUEIJO E TOMATE"),
    ("BAURU", "CONTRA FILÉ, QUEIJO, BACON, ALFACE, TOMATE, CEBOLA, KETCHUP, MAIONESE, MOSTARDA E BATATA PALHA"),
    ("X-CALABRESA", "CALABRESA, ALFACE, TOMATE, CEBOLA, KETCHUP, MOSTARDA, MAIONESE, QUEIJO E BATATA PALHA"),
]

# ---------------- draw ----------------
for cx in col_x:
    draw_col_headers(cx)
draw_items(col_x[0], left)
draw_items(col_x[1], right)

# footer accent + phones
d.rectangle([0, H-70, W, H], fill=ORANGE)
fph = font(REG, 30, 800)
phones = "Tel / WhatsApp:  (14) 98214-4789   •   (14) 98155-7309"
d.text(((W - tw(d, phones, fph))//2, H-56), phones, font=fph, fill=BLACK)

img.save(OUT)
print("saved", OUT)
