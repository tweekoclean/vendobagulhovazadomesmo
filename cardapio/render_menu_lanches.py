#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MENU de Lanches - 2 paginas (10 itens cada), coluna unica, fundo preto, estilo card."""

from PIL import Image, ImageDraw, ImageFont

W, H = 1400, 1980

BLACK  = (0, 0, 0)
ORANGE = (245, 102, 18)
RED    = (219, 22, 12)
WHITE  = (255, 255, 255)
GRAY   = (206, 206, 206)
CARD   = (24, 24, 27)
CARDLN = (52, 52, 56)

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
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]
def th(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[3] - b[1]

def wrap(d, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= max_w: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ---------------- illustrations ----------------
def draw_burger(d, cx, cy, s):
    d.rounded_rectangle([cx-s, cy+s*0.55, cx+s, cy+s*0.95], radius=int(s*0.35), fill=(196,120,52))
    d.rounded_rectangle([cx-s*1.02, cy+s*0.32, cx+s*1.02, cy+s*0.62], radius=int(s*0.2), fill=(74,44,26))
    d.polygon([(cx-s, cy+s*0.28),(cx+s, cy+s*0.28),(cx+s*0.5, cy+s*0.6)], fill=(240,176,40))
    d.polygon([(cx-s, cy+s*0.28),(cx+s, cy+s*0.28),(cx-s*0.4, cy+s*0.58)], fill=(240,176,40))
    d.rectangle([cx-s, cy+s*0.2, cx+s, cy+s*0.3], fill=(240,176,40))
    pts=[]; n=10
    for i in range(n+1):
        x = cx - s*1.05 + (2*s*1.05)*i/n
        y = cy+s*0.12 + (s*0.10 if i%2 else 0); pts.append((x,y))
    pts += [(cx+s*1.05, cy+s*0.28),(cx-s*1.05, cy+s*0.28)]
    d.polygon(pts, fill=(96,168,74))
    d.ellipse([cx-s*0.55, cy+s*0.02, cx+s*0.55, cy+s*0.22], fill=(206,54,40))
    d.pieslice([cx-s, cy-s*0.75, cx+s, cy+s*0.35], 180, 360, fill=(214,138,66))
    for (dx,dy) in [(-0.45,-0.15),(-0.15,-0.3),(0.2,-0.28),(0.5,-0.1),(0.0,-0.05),(-0.3,0.05),(0.35,0.05)]:
        sx, sy = cx+dx*s, cy+dy*s
        d.ellipse([sx-4, sy-2, sx+4, sy+2], fill=(245,232,200))

def draw_soda(d, cx, cy, s):
    d.polygon([(cx-s*0.7, cy-s),(cx+s*0.7, cy-s),(cx+s*0.5, cy+s),(cx-s*0.5, cy+s)], fill=(38,38,42))
    d.rectangle([cx-s*0.8, cy-s*1.18, cx+s*0.8, cy-s*0.95], fill=(70,70,74))
    d.ellipse([cx-s*0.8, cy-s*1.28, cx+s*0.8, cy-s*1.08], fill=(90,90,94))
    d.line([(cx+s*0.15, cy-s*1.9),(cx+s*0.3, cy-s*1.1)], fill=(230,60,60), width=int(s*0.14))
    d.polygon([(cx-s*0.55, cy-s*0.7),(cx-s*0.35, cy-s*0.7),(cx-s*0.3, cy+s*0.7),(cx-s*0.45, cy+s*0.7)], fill=(60,60,66))

# ---------------- layout ----------------
MARGIN = 70
box_w, box_gap, box_h = 122, 14, 60
price_area = box_w*2 + box_gap
PAD = 22
Y0 = 470
FOOTER_TOP = H - 78

def new_page():
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    tile = 48
    for gy in range(-1, H//tile+2):
        for gx in range(-1, W//tile+2):
            if (gx+gy) % 2 == 0:
                x, y = gx*tile, gy*tile
                d.polygon([(x+tile/2,y),(x+tile,y+tile/2),(x+tile/2,y+tile),(x,y+tile/2)], fill=(15,15,15))
    return img, d

def draw_header(d, page_no):
    # title
    f_menu = font(ITA, 150, 900)
    d.text((60, 44), "MENU", font=f_menu, fill=WHITE)
    f_de = font(ITA, 58, 800)
    d.text((72, 210), "de", font=f_de, fill=ORANGE)
    de_w = tw(d, "de", f_de)
    f_lan = font(ITA, 118, 900)
    d.text((72 + de_w + 22, 182), "Lanches", font=f_lan, fill=ORANGE)
    # illustration
    draw_burger(d, W-330, 175, 132)
    draw_soda(d, W-135, 175, 80)
    # divider
    d.rectangle([MARGIN, 330, W-MARGIN, 336], fill=ORANGE)
    # page pill (left side, below title)
    fp = font(REG, 26, 800)
    txt = f"PÁGINA {page_no}/2"
    pw = tw(d, txt, fp) + 44
    d.rounded_rectangle([MARGIN, 356, MARGIN+pw, 356+44], radius=22, fill=ORANGE)
    d.text((MARGIN + 22, 364), txt, font=fp, fill=BLACK)
    # price column headers
    right = W - MARGIN - 24
    fh = font(REG, 19, 800)
    labels = ["Pão de\nHamburguer", "Pão\nFrancês"]
    xs = [right - price_area, right - box_w]
    for x, lab in zip(xs, labels):
        d.rounded_rectangle([x, 352, x+box_w, 352+56], radius=8, fill=RED)
        parts = lab.split("\n")
        ty = 352 + 28 - (len(parts)*21)//2
        for p in parts:
            d.text((x + (box_w - tw(d, p, fh))/2, ty), p, font=fh, fill=WHITE)
            ty += 21

def draw_footer(d):
    d.rectangle([0, FOOTER_TOP, W, H], fill=ORANGE)
    fph = font(REG, 30, 800)
    phones = "PARADA OBRIGATÓRIA LANCHES   •   (14) 98214-4789   •   (14) 98155-7309"
    d.text(((W - tw(d, phones, fph))//2, FOOTER_TOP + 22), phones, font=fph, fill=BLACK)

def render_page(filename, items, page_no):
    img, d = new_page()
    draw_header(d, page_no)

    name_f = font(ITA, 38, 900)
    desc_f = font(REG, 19, 600)
    num_f  = font(ITA, 34, 900)
    right = W - MARGIN - 24
    text_x = MARGIN + 84
    text_max = (right - price_area - 40) - text_x

    # compute card heights to distribute evenly
    blocks = []
    for name, desc in items:
        lines = wrap(d, desc, desc_f, text_max)
        blk_h = th(d, name, name_f) + 8 + len(lines)*(th(d, "Ag", desc_f)+7)
        ch = max(blk_h + PAD*2, box_h + PAD*2)
        blocks.append((name, lines, ch))

    total = sum(b[2] for b in blocks)
    avail = FOOTER_TOP - 24 - Y0
    gap = max(10, (avail - total) // (len(blocks)))
    gap = min(gap, 26)

    y = Y0
    for i, (name, lines, ch) in enumerate(blocks, 1):
        # card
        d.rounded_rectangle([MARGIN, y, W-MARGIN, y+ch], radius=16, fill=CARD, outline=CARDLN, width=1)
        # orange accent bar
        d.rounded_rectangle([MARGIN+14, y+14, MARGIN+22, y+ch-14], radius=4, fill=ORANGE)
        # number
        d.text((MARGIN+34, y+PAD-2), f"{i:02d}", font=num_f, fill=(90,90,96))
        # name + desc
        d.text((text_x, y+PAD-4), name, font=name_f, fill=ORANGE)
        ty = y + PAD - 4 + th(d, name, name_f) + 10
        for ln in lines:
            d.text((text_x, ty), ln, font=desc_f, fill=GRAY)
            ty += th(d, "Ag", desc_f) + 7
        # price boxes centered vertically
        row_cy = y + ch/2
        for bx in [right - price_area, right - box_w]:
            d.rectangle([bx+3, row_cy - box_h/2 + 3, bx+box_w+3, row_cy + box_h/2 + 3], fill=(0,0,0))  # shadow
            d.rounded_rectangle([bx, row_cy - box_h/2, bx+box_w, row_cy + box_h/2], radius=8, fill=WHITE)
        y += ch + gap

    draw_footer(d)
    img.save("/projects/sandbox/cardapio/" + filename)
    print("saved", filename)

# ---------------- data ----------------
page1 = [
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
page2 = [
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

render_page("menu-lanches-1.png", page1, 1)
render_page("menu-lanches-2.png", page2, 2)

# combined PDF
imgs = [Image.open("/projects/sandbox/cardapio/menu-lanches-1.png").convert("RGB"),
        Image.open("/projects/sandbox/cardapio/menu-lanches-2.png").convert("RGB")]
imgs[0].save("/projects/sandbox/cardapio/Menu-Lanches.pdf", save_all=True, append_images=imgs[1:], resolution=150.0)
print("PDF ok")
