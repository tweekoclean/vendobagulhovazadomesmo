#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demais secoes do cardapio no mesmo estilo card/fundo preto: Pizzas, Prato, Porcoes."""

from PIL import Image, ImageDraw, ImageFont

W, H = 1400, 1980
DIR = "/projects/sandbox/cardapio/"

BLACK  = (0, 0, 0)
ORANGE = (245, 102, 18)
RED    = (219, 22, 12)
GREEN  = (14, 140, 60)
WHITE  = (255, 255, 255)
GRAY   = (206, 206, 206)
CARD   = (24, 24, 27)
CARDLN = (52, 52, 56)

REG = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf"
ITA = "/usr/share/fonts/google-noto-vf/NotoSans-Italic[wght].ttf"

def font(path, size, weight=400):
    f = ImageFont.truetype(path, size)
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f

def tw(d,s,f):
    b=d.textbbox((0,0),s,font=f); return b[2]-b[0]
def th(d,s,f):
    b=d.textbbox((0,0),s,font=f); return b[3]-b[1]

def wrap(d,text,f,mw):
    words,lines,cur=text.split(),[],""
    for w in words:
        t=(cur+" "+w).strip()
        if tw(d,t,f)<=mw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

# ---------------- illustrations ----------------
def draw_pizza(d, cx, cy, s):
    d.ellipse([cx-s, cy-s, cx+s, cy+s], fill=(212,150,74))            # crust
    d.ellipse([cx-s*0.82, cy-s*0.82, cx+s*0.82, cy+s*0.82], fill=(206,66,42))  # sauce
    d.ellipse([cx-s*0.82, cy-s*0.82, cx+s*0.82, cy+s*0.82], outline=(230,200,120), width=6)
    for (dx,dy) in [(-0.4,-0.3),(0.2,-0.4),(0.45,0.1),(-0.1,0.35),(-0.45,0.15),(0.15,0.15),(0.35,-0.15)]:
        px,py=cx+dx*s,cy+dy*s
        d.ellipse([px-s*0.12,py-s*0.12,px+s*0.12,py+s*0.12], fill=(150,30,24))  # pepperoni
    for (dx,dy) in [(-0.2,-0.1),(0.3,-0.2),(0.0,0.3),(-0.3,0.3)]:
        px,py=cx+dx*s,cy+dy*s
        d.ellipse([px-s*0.06,py-s*0.06,px+s*0.06,py+s*0.06], fill=(240,235,210))  # cheese bits

def draw_plate(d, cx, cy, s):
    d.ellipse([cx-s, cy-s*0.5, cx+s, cy+s*0.5], fill=(70,72,78))       # plate
    d.ellipse([cx-s*0.78, cy-s*0.38, cx+s*0.78, cy+s*0.38], fill=(150,152,158))
    d.rounded_rectangle([cx-s*0.55, cy-s*0.2, cx-s*0.05, cy+s*0.12], radius=8, fill=(120,72,40))  # meat
    for i in range(4):  # fries
        d.rounded_rectangle([cx+s*0.1+i*s*0.14, cy-s*0.22, cx+s*0.18+i*s*0.14, cy+s*0.1], radius=4, fill=(226,178,60))
    d.ellipse([cx-s*0.1, cy+s*0.02, cx+s*0.25, cy+s*0.2], fill=(90,160,70))  # salad

def draw_fries(d, cx, cy, s):
    for i in range(5):
        x=cx-s*0.5+i*s*0.24
        d.rounded_rectangle([x, cy-s*1.1, x+s*0.16, cy+s*0.2], radius=4, fill=(230,182,60))
        d.rectangle([x, cy-s*1.1, x+s*0.16, cy-s*0.95], fill=(245,210,110))
    d.polygon([(cx-s*0.7,cy-s*0.1),(cx+s*0.7,cy-s*0.1),(cx+s*0.5,cy+s*0.9),(cx-s*0.5,cy+s*0.9)], fill=RED)
    d.rectangle([cx-s*0.66,cy-s*0.1,cx+s*0.66,cy+s*0.18], fill=(240,240,240))
    d.rectangle([cx-s*0.66,cy-s*0.1,cx+s*0.66,cy-s*0.02], fill=RED)

ILLUS = {"pizza": draw_pizza, "plate": draw_plate, "fries": draw_fries}

# ---------------- layout ----------------
MARGIN = 70
PAD = 22
Y0 = 470
FOOTER_TOP = H - 78

def new_page():
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    tile=48
    for gy in range(-1,H//tile+2):
        for gx in range(-1,W//tile+2):
            if (gx+gy)%2==0:
                x,y=gx*tile,gy*tile
                d.polygon([(x+tile/2,y),(x+tile,y+tile/2),(x+tile/2,y+tile),(x,y+tile/2)], fill=(15,15,15))
    return img,d

def draw_title(d, connector, word2, illus):
    f_menu=font(ITA,150,900); d.text((60,44),"MENU",font=f_menu,fill=WHITE)
    f_c=font(ITA,58,800); d.text((72,210),connector,font=f_c,fill=ORANGE)
    cw=tw(d,connector,f_c)
    f_w=font(ITA,118,900); d.text((72+cw+22,182),word2,font=f_w,fill=ORANGE)
    ILLUS[illus](d, W-300, 185, 120)
    d.rectangle([MARGIN,330,W-MARGIN,336],fill=ORANGE)

def draw_footer(d):
    d.rectangle([0,FOOTER_TOP,W,H],fill=ORANGE)
    fph=font(REG,30,800)
    phones="PARADA OBRIGATÓRIA LANCHES   •   (14) 98214-4789   •   (14) 98155-7309"
    d.text(((W-tw(d,phones,fph))//2,FOOTER_TOP+22),phones,font=fph,fill=BLACK)

def render(filename, connector, word2, illus, columns, items, box_w=140):
    """columns: list of (label, color).  items: (name, desc, [price strings])."""
    img,d=new_page()
    draw_title(d, connector, word2, illus)

    ncols=len(columns)
    box_gap=14; box_h=60
    price_area=box_w*ncols+box_gap*(ncols-1)
    right=W-MARGIN-24
    xs=[right-price_area+k*(box_w+box_gap) for k in range(ncols)]

    # headers
    fh=font(REG,19,800)
    for (label,color),x in zip(columns,xs):
        d.rounded_rectangle([x,352,x+box_w,352+56],radius=8,fill=color)
        parts=label.split("\n")
        ty=352+28-(len(parts)*21)//2
        for p in parts:
            d.text((x+(box_w-tw(d,p,fh))/2,ty),p,font=fh,fill=WHITE)
            ty+=21

    name_f=font(ITA,38,900); desc_f=font(REG,19,600); num_f=font(ITA,34,900); price_f=font(REG,30,900)
    text_x=MARGIN+84
    text_max=(right-price_area-40)-text_x

    blocks=[]
    for name,desc,prices in items:
        lines=wrap(d,desc,desc_f,text_max) if desc else []
        blk_h=th(d,name,name_f)+ (10+len(lines)*(th(d,"Ag",desc_f)+7) if lines else 0)
        ch=max(blk_h+PAD*2, box_h+PAD*2)
        blocks.append((name,lines,prices,ch))

    total=sum(b[3] for b in blocks)
    avail=FOOTER_TOP-24-Y0
    # spread cards; allow bigger gaps for short lists, then vertically center the block
    gap=min(max(10,(avail-total)//len(blocks)),90)
    used=total+gap*(len(blocks)-1)
    y=Y0+max(0,(avail-used)//2)
    for i,(name,lines,prices,ch) in enumerate(blocks,1):
        d.rounded_rectangle([MARGIN,y,W-MARGIN,y+ch],radius=16,fill=CARD,outline=CARDLN,width=1)
        d.rounded_rectangle([MARGIN+14,y+14,MARGIN+22,y+ch-14],radius=4,fill=ORANGE)
        d.text((MARGIN+34,y+PAD-2),f"{i:02d}",font=num_f,fill=(90,90,96))
        d.text((text_x,y+PAD-4),name,font=name_f,fill=ORANGE)
        ty=y+PAD-4+th(d,name,name_f)+10
        for ln in lines:
            d.text((text_x,ty),ln,font=desc_f,fill=GRAY); ty+=th(d,"Ag",desc_f)+7
        row_cy=y+ch/2
        for x,pr in zip(xs,prices):
            d.rectangle([x+3,row_cy-box_h/2+3,x+box_w+3,row_cy+box_h/2+3],fill=(0,0,0))
            d.rounded_rectangle([x,row_cy-box_h/2,x+box_w,row_cy+box_h/2],radius=8,fill=WHITE)
            col = (150,150,150) if pr=="—" else BLACK
            d.text((x+(box_w-tw(d,pr,price_f))/2, row_cy-th(d,pr,price_f)/2-4), pr, font=price_f, fill=col)
        y+=ch+gap

    draw_footer(d)
    img.save(DIR+filename); print("saved",filename)

# ---------------- data ----------------
pizzas=[
    ("MUSSARELA","MUSSARELA, ORÉGANO, TOMATE E AZEITONA",["R$ 65,00"]),
    ("CALABRESA","CALABRESA, MUSSARELA, ORÉGANO, TOMATE E AZEITONA",["R$ 65,00"]),
    ("AMERICANA","MUSSARELA, PRESUNTO, PALMITO, BACON, ERVILHA, ORÉGANO E AZEITONA",["R$ 70,00"]),
    ("PORTUGUESA","MUSSARELA, PRESUNTO, PALMITO, OVOS, CEBOLA, TOMATE, ORÉGANO E AZEITONA",["R$ 70,00"]),
    ("PRIMAVERA","MUSSARELA, CATUPIRY, PALMITO, MILHO, CEBOLA, TOMATE, ORÉGANO E AZEITONA",["R$ 65,00"]),
    ("MAMMA-MIA","MUSSARELA, PRESUNTO, CALABRESA, BACON, CATUPIRY, MILHO, CEBOLA, TOMATE, ERVILHA, ORÉGANO E AZEITONA",["R$ 70,00"]),
    ("LOMBINHO CANADENSE","MUSSARELA, LOMBINHO, CATUPIRY, TOMATE, CEBOLA, ORÉGANO E AZEITONA",["R$ 65,00"]),
    ("CAIPIRA","MUSSARELA, FRANGO, CATUPIRY, MILHO, TOMATE, CEBOLA, ORÉGANO E AZEITONA",["R$ 70,00"]),
]
prato=[
    ("AMERICANO","CONTRA FILÉ, 02 OVOS, QUEIJO, CATUPIRY, SALADA E BATATA FRITA",["R$ 50,00"]),
    ("BAURU NO PRATO","CONTRA FILÉ, BACON, QUEIJO, SALADA E BATATA FRITA",["R$ 48,00"]),
    ("FILÉ DE FRANGO","FILÉ DE FRANGO, BACON, QUEIJO, SALADA E BATATA FRITA",["R$ 45,00"]),
    ("LOMBO","LOMBO, BACON, QUEIJO, SALADA E BATATA FRITA",["R$ 45,00"]),
]
porcoes=[
    ("BATATA MEGA","01 KG DE BATATA, CALABRESA, BACON, QUEIJO, CHEDDAR E CATUPIRY",["—","R$ 60,00"]),
    ("BATATA FRITA","",["R$ 25,00","R$ 28,00"]),
    ("BATATA FRITA C/ QUEIJO E BACON","",["R$ 30,00","R$ 45,00"]),
    ("TILÁPIA","",["—","R$ 50,00"]),
    ("CONTRA FILÉ","COM TOMATE, CEBOLA, QUEIJO E PÃO",["R$ 50,00","R$ 65,00"]),
    ("FILÉ FRANGO","",["—","R$ 40,00"]),
    ("CALABRESA","COM TOMATE, CEBOLA E PÃO",["R$ 30,00","R$ 45,00"]),
    ("LOMBO","COM TOMATE, CEBOLA, QUEIJO E PÃO",["R$ 40,00","R$ 55,00"]),
    ("FRANGO À PASSARINHO","COM FRITAS",["—","R$ 40,00"]),
    ("POLENTA","",["R$ 20,00","R$ 28,00"]),
    ("MINI SALGADOS","PORÇÃO COM 10 UNIDADES",["—","R$ 25,00"]),
]

render("menu-pizzas.png","de","Pizzas","pizza",[("VALOR",RED)],pizzas,box_w=150)
render("menu-no-prato.png","no","Prato","plate",[("VALOR",RED)],prato,box_w=150)
render("menu-porcoes.png","","Porções","fries",[("MEIA\nPORÇÃO",GREEN),("PORÇÃO\nINTEIRA",RED)],porcoes,box_w=132)

# full combined PDF (lanches 1-2 + pizzas + prato + porcoes)
order=["menu-lanches-1.png","menu-lanches-2.png","menu-pizzas.png","menu-no-prato.png","menu-porcoes.png"]
imgs=[Image.open(DIR+f).convert("RGB") for f in order]
imgs[0].save(DIR+"Cardapio-Completo.pdf", save_all=True, append_images=imgs[1:], resolution=150.0)
print("PDF completo ok")
