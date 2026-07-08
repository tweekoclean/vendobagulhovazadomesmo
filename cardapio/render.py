#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the 'Parada Obrigatoria Lanches' menu into high-res PNG pages (offline)."""

from PIL import Image, ImageDraw, ImageFont
import os

# ---------------- config ----------------
W, H = 1240, 1754          # A4 @150dpi portrait
MARGIN = 96
OUT = "/projects/sandbox/cardapio"

BLACK   = (0, 0, 0)
YELLOW  = (255, 204, 0)
WHITE   = (255, 255, 255)
GRAY    = (200, 200, 200)
RED     = (225, 6, 0)
GREEN   = (10, 138, 58)
LINE    = (70, 70, 70)

FONT_PATH = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf"

def font(size, weight=400):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f

# ---------------- helpers ----------------
def text_w(draw, s, f):
    return draw.textbbox((0, 0), s, font=f)[2]

def wrap(draw, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(draw, t, f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def rounded_price(draw, cx_right, cy, label, f, box_w=None, pad_x=22, h=52):
    """Draw a white rounded price box whose RIGHT edge is at cx_right, vertically centered at cy."""
    tw = text_w(draw, label, f)
    w = box_w if box_w else tw + pad_x * 2
    x1 = cx_right - w
    y1 = cy - h // 2
    draw.rounded_rectangle([x1, y1, cx_right, y1 + h], radius=10, fill=WHITE)
    tb = draw.textbbox((0, 0), label, font=f)
    th = tb[3] - tb[1]
    draw.text((x1 + (w - tw) / 2, cy - th / 2 - tb[1]), label, font=f, fill=BLACK)
    return x1  # left edge

def dotted_leader(draw, x1, x2, y, color=LINE, gap=14, r=2):
    x = x1
    while x < x2:
        draw.ellipse([x, y - r, x + r, y + r], fill=color)
        x += gap

def base_page():
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 12], fill=RED)          # top bar
    d.rectangle([0, H - 12, W, H], fill=RED)      # bottom bar
    return img, d

def fit_font(d, text, size, weight, max_w, min_size=24):
    """Return a font whose rendered text width fits max_w, shrinking if needed."""
    s = size
    while s > min_size:
        f = font(s, weight)
        if text_w(d, text, f) <= max_w:
            return f
        s -= 2
    return font(min_size, weight)

def draw_logo(d, cy):
    # simple brand badge centered
    f1 = font(34, 900); f2 = font(20, 800); f3 = font(40, 900)
    lines = [("PARADA", f1, WHITE), ("OBRIGAT\u00d3RIA", f2, YELLOW), ("LANCHES", f3, WHITE)]
    heights = [d.textbbox((0,0),t,font=f)[3] for t,f,_ in lines]
    total_h = sum(heights) + 8*2
    box_w = 360
    x1 = (W - box_w)//2
    y1 = cy - total_h//2 - 16
    d.rounded_rectangle([x1, y1, x1+box_w, y1+total_h+32], radius=16, fill=RED, outline=YELLOW, width=4)
    y = y1 + 16
    for (t,f,c),hh in zip(lines, heights):
        tw = text_w(d, t, f)
        d.text(((W-tw)//2, y), t, font=f, fill=c)
        y += hh + 8

def draw_title(d, y, title):
    f = font(74, 900)
    tw = text_w(d, title, f)
    d.text(((W - tw)//2, y), title, font=f, fill=YELLOW)
    return y + 96

def draw_contact(d):
    f = font(30, 800)
    y = H - 120
    d.line([MARGIN, y, W-MARGIN, y], fill=LINE, width=2)
    phones = ["(14) 98214-4789", "(14) 98155-7309"]
    fy = y + 26
    # center both phones on one row
    labels = ["Tel/Zap:  " + phones[0], "|", phones[1]]
    gap = 26
    widths = [text_w(d, l, f) for l in labels]
    total = sum(widths) + gap*(len(labels)-1)
    x = (W - total)//2
    for l, wl in zip(labels, widths):
        d.text((x, fy), l, font=f, fill=WHITE if l != "|" else GRAY)
        x += wl + gap

def draw_price_headers(d, right_edge, y, box_w, headers):
    """Two colored header boxes above the price columns."""
    f = font(20, 800)
    colors = [GREEN, RED]
    gap = 16
    # rightmost box right edge = right_edge; second box to its left
    x_right2 = right_edge
    x_right1 = right_edge - box_w - gap
    boxes = [x_right1, x_right2]
    for (hx_right, txt, col) in zip(boxes, headers, colors):
        x1 = hx_right - box_w
        d.rounded_rectangle([x1, y, hx_right, y+56], radius=8, fill=col)
        parts = txt.split("\n")
        fh = 24
        ty = y + 28 - (len(parts)*fh)//2
        for p in parts:
            tw = text_w(d, p, f)
            d.text((x1 + (box_w-tw)/2, ty), p, font=f, fill=WHITE)
            ty += fh
    return box_w, gap

# ---------------- page renderers ----------------
def render_single(filename, title, items, with_logo=False, note="Imagens ilustrativas"):
    """items: list of (name, desc, price_str)"""
    img, d = base_page()
    y = 70
    if with_logo:
        draw_logo(d, y+70); y += 170
    y = draw_title(d, y, title)
    y += 10

    name_f = font(40, 800)
    desc_f = font(27, 400)
    price_f = font(38, 900)
    right = W - MARGIN
    left = MARGIN
    text_max = W - MARGIN*2 - 260  # leave room for price

    name_max = right - 260 - left - 30
    for name, desc, price in items:
        name_u = name.upper()
        name_f = fit_font(d, name_u, 40, 800, name_max)
        d.text((left, y), name_u, font=name_f, fill=YELLOW)
        nb = d.textbbox((0,0), name_u, font=name_f)
        name_h = nb[3]-nb[1]
        name_end = left + text_w(d, name_u, name_f)
        # price box aligned to name row center
        row_cy = y + name_h//2
        px_left = rounded_price(d, right, row_cy, price, price_f)
        # dotted leader
        dotted_leader(d, name_end + 18, px_left - 18, y + name_h + 4)
        y += name_h + 10
        if desc:
            for ln in wrap(d, desc, desc_f, text_max):
                d.text((left, y), ln, font=desc_f, fill=GRAY)
                lb = d.textbbox((0,0), ln, font=desc_f)
                y += (lb[3]-lb[1]) + 8
        y += 26

    draw_contact(d)
    if note:
        nf = font(18, 400)
        d.text((W-MARGIN-text_w(d, note, nf), H-150), note, font=nf, fill=(90,90,90))
    path = os.path.join(OUT, filename)
    img.save(path)
    print("saved", path)

def render_dual(filename, title, items, headers, note="Imagens ilustrativas"):
    """items: (name, desc, price_left, price_right).  price '-' shows dash."""
    img, d = base_page()
    y = 70
    y = draw_title(d, y, title)

    price_f = font(34, 900)
    box_w = 168
    gap = 16
    right = W - MARGIN
    # headers
    draw_price_headers(d, right, y, box_w, headers)
    y += 76

    name_f = font(40, 800)
    desc_f = font(27, 400)
    left = MARGIN
    text_max = right - box_w*2 - gap - left - 30

    name_max = right - box_w*2 - gap - left - 30
    for name, desc, p1, p2 in items:
        name_u = name.upper()
        name_f = fit_font(d, name_u, 40, 800, name_max)
        d.text((left, y), name_u, font=name_f, fill=YELLOW)
        nb = d.textbbox((0,0), name_u, font=name_f)
        name_h = nb[3]-nb[1]
        row_cy = y + name_h//2
        # right box
        rounded_price(d, right, row_cy, p2, price_f, box_w=box_w)
        # left box
        rounded_price(d, right - box_w - gap, row_cy, p1, price_f, box_w=box_w)
        y += name_h + 10
        if desc:
            for ln in wrap(d, desc, desc_f, text_max):
                d.text((left, y), ln, font=desc_f, fill=GRAY)
                lb = d.textbbox((0,0), ln, font=desc_f)
                y += (lb[3]-lb[1]) + 8
        y += 26

    draw_contact(d)
    if note:
        nf = font(18, 400)
        d.text((W-MARGIN-text_w(d, note, nf), H-150), note, font=nf, fill=(90,90,90))
    path = os.path.join(OUT, filename)
    img.save(path)
    print("saved", path)

# ---------------- data ----------------
pizzas = [
    ("Mussarela", "Mussarela, or\u00e9gano, tomate e azeitona", "R$ 65,00"),
    ("Calabresa", "Calabresa, mussarela, or\u00e9gano, tomate e azeitona", "R$ 65,00"),
    ("Americana", "Mussarela, presunto, palmito, bacon, ervilha, or\u00e9gano e azeitona", "R$ 70,00"),
    ("Portuguesa", "Mussarela, presunto, palmito, ovos, cebola, tomate, or\u00e9gano e azeitona", "R$ 70,00"),
    ("Primavera", "Mussarela, catupiry, palmito, milho, cebola, tomate, or\u00e9gano e azeitona", "R$ 65,00"),
    ("Mamma-Mia", "Mussarela, presunto, calabresa, bacon, catupiry, milho, cebola, tomate, ervilha, or\u00e9gano e azeitona", "R$ 70,00"),
    ("Lombinho Canadense", "Mussarela, lombinho, catupiry, tomate, cebola, or\u00e9gano e azeitona", "R$ 65,00"),
    ("Caipira", "Mussarela, frango, catupiry, milho, tomate, cebola, or\u00e9gano e azeitona", "R$ 70,00"),
]

lanches = [
    ("Hamburguer", "Carne, alface, cebola, tomate, catchup, mostarda, maionese e batata palha", "R$ 12,00", "R$ 14,00"),
    ("Hamburguer com Catupiry", "Carne, alface, cebola, tomate, catupiry, catchup, mostarda, maionese e batata palha", "R$ 18,00", "R$ 20,00"),
    ("X-Burguer", "Carne, queijo, catchup, maionese, mostarda e batata palha", "R$ 15,00", "R$ 18,00"),
    ("Hot Dog", "02 salsichas, alface, tomate, cebola, maionese, catchup, mostarda e batata palha", "R$ 12,00", "R$ 14,00"),
    ("X-Salada", "Carne, alface, tomate, cebola, queijo, presunto, maionese, catchup, mostarda e batata palha", "R$ 25,00", "R$ 28,00"),
    ("X-Bacon", "Carne, alface, tomate, cebola, queijo, bacon, maionese, mostarda, catchup e batata palha", "R$ 30,00", "R$ 34,00"),
    ("X-Egg", "Carne, alface, tomate, cebola, ovo, presunto, maionese, mostarda, catchup e batata palha", "R$ 26,00", "R$ 28,00"),
    ("X-Egg Bacon", "Carne, alface, tomate, cebola, ovo, presunto, queijo, bacon, maionese, mostarda, catchup e batata palha", "R$ 32,00", "R$ 34,00"),
    ("Big Cheddar", "02 carnes, alface, tomate, cebola, cheddar, maionese, mostarda, catchup e batata palha", "R$ 28,00", "R$ 30,00"),
]

no_prato = [
    ("Americano", "Contra fil\u00e9, 02 ovos, queijo, catupiry, salada e batata frita", "R$ 50,00"),
    ("Bauru no Prato", "Contra fil\u00e9, bacon, queijo, salada e batata frita", "R$ 48,00"),
    ("Fil\u00e9 de Frango", "Fil\u00e9 de frango, bacon, queijo, salada e batata frita", "R$ 45,00"),
    ("Lombo", "Lombo, bacon, queijo, salada e batata frita", "R$ 45,00"),
]

porcoes = [
    ("Batata Mega", "01 kg de batata, calabresa, bacon, queijo, cheddar e catupiry", "\u2014", "R$ 60,00"),
    ("Batata Frita", "", "R$ 25,00", "R$ 28,00"),
    ("Batata Frita c/ Queijo e Bacon", "", "R$ 30,00", "R$ 45,00"),
    ("Til\u00e1pia", "", "\u2014", "R$ 50,00"),
    ("Contra Fil\u00e9", "Com tomate, cebola, queijo e p\u00e3o", "R$ 50,00", "R$ 65,00"),
    ("Fil\u00e9 Frango", "", "\u2014", "R$ 40,00"),
    ("Calabresa", "Com tomate, cebola e p\u00e3o", "R$ 30,00", "R$ 45,00"),
    ("Lombo", "Com tomate, cebola, queijo e p\u00e3o", "R$ 40,00", "R$ 55,00"),
    ("Frango \u00e0 Passarinho", "Com fritas", "\u2014", "R$ 40,00"),
    ("Polenta", "", "R$ 20,00", "R$ 28,00"),
    ("Mini Salgados", "Por\u00e7\u00e3o com 10 unidades", "\u2014", "R$ 25,00"),
]

# ---------------- build ----------------
render_single("1-pizzas.png", "PIZZAS", pizzas, with_logo=True)
render_dual("2-lanches.png", "LANCHES", lanches, ["P\u00e3o de\nHamburguer", "P\u00e3o\nFranc\u00eas"])
render_single("3-lanches-no-prato.png", "LANCHES NO PRATO", no_prato)
render_dual("4-porcoes-quentes.png", "POR\u00c7\u00d5ES QUENTES", porcoes, ["Meia\nPor\u00e7\u00e3o", "Por\u00e7\u00e3o\nInteira"])
print("ALL DONE")
