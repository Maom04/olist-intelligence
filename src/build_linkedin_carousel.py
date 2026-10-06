from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"C:\Projetos\olist-intelligence")
ASSETS = ROOT / "assets"
OUT = ASSETS / "linkedin"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350

BG = "#080D18"
PANEL = "#101827"
BORDER = "#223047"
TEXT = "#F8FAFC"
MUTED = "#8FA0B7"
PURPLE = "#8B5CF6"
PURPLE2 = "#A78BFA"
CYAN = "#22D3EE"
GREEN = "#34D399"
RED = "#FB7185"

font_regular = r"C:\Windows\Fonts\segoeui.ttf"
font_semibold = r"C:\Windows\Fonts\seguisb.ttf"
font_bold = r"C:\Windows\Fonts\segoeuib.ttf"

def f(path, size):
    return ImageFont.truetype(path, size)

def draw_gradient_bg(img):
    px = img.load()
    # vertical dark gradient
    for y in range(H):
        t = y / max(H-1,1)
        r = int(8*(1-t) + 5*t)
        g = int(13*(1-t) + 8*t)
        b = int(24*(1-t) + 18*t)
        for x in range(W):
            px[x,y] = (r,g,b)
    # subtle glows
    glow = Image.new("RGBA", (W,H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((650,-180,1180,350), fill=(124,58,237,50))
    gd.ellipse((-180,800,380,1390), fill=(34,211,238,28))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img.alpha_composite(glow)

def page():
    img = Image.new("RGBA",(W,H),(0,0,0,255))
    draw_gradient_bg(img)
    return img

def round_rect(draw, box, radius=28, fill=PANEL, outline=BORDER, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def fit_text(draw, text, box_w, font_path, max_size, min_size=20):
    for size in range(max_size, min_size-1, -1):
        font = f(font_path,size)
        bbox = draw.textbbox((0,0), text, font=font)
        if bbox[2]-bbox[0] <= box_w:
            return font
    return f(font_path,min_size)

def paste_rounded(base, src, box, radius=24):
    x1,y1,x2,y2 = box
    width,height = x2-x1,y2-y1
    src = src.copy().convert("RGB")
    src.thumbnail((width,height), Image.LANCZOS)
    canvas = Image.new("RGB",(width,height), PANEL)
    sw,sh = src.size
    ox=(width-sw)//2; oy=(height-sh)//2
    canvas.paste(src,(ox,oy))
    mask = Image.new("L",(width,height),0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,width,height),radius=radius,fill=255)
    base.paste(canvas,(x1,y1),mask)

def footer(draw, page_no, label):
    draw.text((54,1305), "OLIST INTELLIGENCE • Portfolio Project", font=f(font_regular,18), fill="#536175")
    right = f"{page_no}/4  •  {label}"
    bb=draw.textbbox((0,0),right,font=f(font_regular,18))
    draw.text((W-54-(bb[2]-bb[0]),1305),right,font=f(font_regular,18),fill="#536175")

# 1 COVER
img=page(); d=ImageDraw.Draw(img)
d.text((54,70),"PROJETO DE PORTFÓLIO",font=f(font_semibold,22),fill=CYAN)
d.text((54,135),"OLIST",font=f(font_bold,86),fill=TEXT)
d.text((54,220),"INTELLIGENCE",font=f(font_bold,86),fill=TEXT)
d.text((54,342),"Do dado bruto ao insight com",font=f(font_regular,34),fill=MUTED)
d.text((54,390),"Python, Power BI e Machine Learning",font=f(font_semibold,38),fill=PURPLE2)

round_rect(d,(54,510,1026,760),radius=26,fill="#0D1524")
stats=[
    ("99.441","pedidos"),
    ("112.650","itens"),
    ("96.096","clientes únicos"),
    ("40.604","comentários analisados"),
]
x=82
for i,(v,lbl) in enumerate(stats):
    if i==2: x=82
    y=545 if i<2 else 655
    if i%2==1: x=565
    d.text((x,y),v,font=f(font_bold,42),fill=TEXT)
    d.text((x,y+54),lbl,font=f(font_regular,19),fill=MUTED)
    if i%2==0: x=565

d.text((54,850),"PIPELINE",font=f(font_semibold,20),fill=CYAN)
steps=["9 CSVs reais","Pandas + validação","Modelo analítico","NLP / ML","Power BI"]
sx=54; y=905
for i,s in enumerate(steps):
    w=184 if i<4 else 170
    round_rect(d,(sx,y,sx+w,y+72),radius=18,fill="#101827")
    sf=fit_text(d,s,w-24,font_semibold,18,14)
    bb=d.textbbox((0,0),s,font=sf)
    d.text((sx+(w-(bb[2]-bb[0]))/2,y+24),s,font=sf,fill=TEXT)
    sx += w+20
    if i<4:
        d.text((sx-15,y+25),"→",font=f(font_bold,20),fill=PURPLE2)
footer(d,1,"Capa")
img.convert("RGB").save(OUT/"01_capa.png",quality=95)

# 2 EXECUTIVE
img=page(); d=ImageDraw.Draw(img)
d.text((54,58),"01  EXECUTIVE OVERVIEW",font=f(font_bold,40),fill=TEXT)
d.text((54,112),"Performance comercial, logística e clientes em uma visão executiva.",font=f(font_regular,24),fill=MUTED)
round_rect(d,(40,180,1040,770),radius=30,fill="#0D1524")
dash=Image.open(ASSETS/"executive_overview.png")
paste_rounded(img,dash,(58,198,1022,740),radius=20)

d.text((54,825),"KPIs EM DESTAQUE",font=f(font_semibold,20),fill=CYAN)
cards=[
    ("R$ 13,22M","GMV entregue",PURPLE2),
    ("96,5 mil","pedidos entregues",TEXT),
    ("4,16","avaliação média",CYAN),
    ("6,8%","taxa de atraso",RED),
]
cx=54
for v,lbl,color in cards:
    round_rect(d,(cx,870,cx+225,1015),radius=22,fill="#101827")
    d.text((cx+18,895),v,font=f(font_bold,31),fill=color)
    d.text((cx+18,947),lbl,font=f(font_regular,17),fill=MUTED)
    cx+=245
d.text((54,1085),"O dashboard foi construído sobre duas granularidades analíticas:",font=f(font_regular,23),fill=MUTED)
d.text((54,1130),"orders_analytics  •  1 linha por pedido",font=f(font_semibold,23),fill=TEXT)
d.text((54,1170),"items_analytics   •  1 linha por item vendido",font=f(font_semibold,23),fill=TEXT)
footer(d,2,"Executive Overview")
img.convert("RGB").save(OUT/"02_executive_overview.png",quality=95)

# 3 AI
img=page(); d=ImageDraw.Draw(img)
d.text((54,58),"02  CUSTOMER & AI INTELLIGENCE",font=f(font_bold,38),fill=TEXT)
d.text((54,112),"NLP aplicado a comentários reais de clientes.",font=f(font_regular,24),fill=MUTED)
round_rect(d,(40,180,1040,770),radius=30,fill="#0D1524")
dash=Image.open(ASSETS/"customer_ai_intelligence.png")
paste_rounded(img,dash,(58,198,1022,740),radius=20)

d.text((54,825),"MODELO DE SENTIMENTO",font=f(font_semibold,20),fill=CYAN)
round_rect(d,(54,865,1026,1035),radius=24,fill="#101827")
d.text((82,895),"TF-IDF",font=f(font_bold,26),fill=PURPLE2)
d.text((242,895),"→",font=f(font_bold,28),fill=MUTED)
d.text((300,895),"SGDClassifier",font=f(font_bold,26),fill=TEXT)
d.text((580,895),"→",font=f(font_bold,28),fill=MUTED)
d.text((635,895),"Positivo • Neutro • Negativo",font=f(font_semibold,22),fill=CYAN)
d.text((82,955),"83,7% de acurácia",font=f(font_bold,31),fill=TEXT)
d.text((410,960),"Macro F1  0,67",font=f(font_semibold,24),fill=MUTED)
d.text((700,960),"8.121 reviews no holdout",font=f(font_regular,19),fill=MUTED)

d.text((54,1090),"40.604 comentários com texto foram analisados.",font=f(font_semibold,26),fill=TEXT)
d.text((54,1135),"Para comentários negativos/neutros, usei TF-IDF + NMF para descobrir tópicos.",font=f(font_regular,21),fill=MUTED)
footer(d,3,"Customer & AI")
img.convert("RGB").save(OUT/"03_customer_ai.png",quality=95)

# 4 INSIGHT
img=page(); d=ImageDraw.Draw(img)
d.text((54,58),"03  INSIGHT DE NEGÓCIO",font=f(font_bold,40),fill=TEXT)
d.text((54,112),"O atraso logístico aparece fortemente associado à satisfação do cliente.",font=f(font_regular,23),fill=MUTED)

round_rect(d,(54,200,1026,560),radius=30,fill="#101827")
d.text((90,245),"ENTREGUE NO PRAZO",font=f(font_semibold,20),fill=GREEN)
d.text((90,290),"4,29",font=f(font_bold,78),fill=TEXT)
d.text((90,390),"nota média",font=f(font_regular,21),fill=MUTED)

d.text((705,245),"ENTREGUE ATRASADO",font=f(font_semibold,20),fill=RED)
d.text((705,290),"2,27",font=f(font_bold,78),fill=TEXT)
d.text((705,390),"nota média",font=f(font_regular,21),fill=MUTED)

d.text((445,285),"−2,02",font=f(font_bold,52),fill=CYAN)
d.text((458,350),"pontos",font=f(font_regular,21),fill=MUTED)

d.text((54,625),"ARQUITETURA DO PROJETO",font=f(font_semibold,20),fill=CYAN)
labels=["Dados brutos","Pandas","Analytics","Machine Learning","Power BI"]
subs=["9 CSVs","auditoria + ETL","orders + items","sentimento + tópicos","dashboard executivo"]
x=54
for i,(lab,sub) in enumerate(zip(labels,subs)):
    w=184 if i<4 else 170
    round_rect(d,(x,680,x+w,810),radius=22,fill="#101827")
    lf=fit_text(d,lab,w-24,font_semibold,20,15)
    bb=d.textbbox((0,0),lab,font=lf)
    d.text((x+(w-(bb[2]-bb[0]))/2,708),lab,font=lf,fill=TEXT)
    sf=fit_text(d,sub,w-18,font_regular,15,11)
    bb=d.textbbox((0,0),sub,font=sf)
    d.text((x+(w-(bb[2]-bb[0]))/2,758),sub,font=sf,fill=MUTED)
    x += w+20
    if i<4:
        d.text((x-15,730),"→",font=f(font_bold,20),fill=PURPLE2)

round_rect(d,(54,890,1026,1175),radius=26,fill="#0D1524")
d.text((82,925),"O objetivo não foi apenas criar um dashboard bonito.",font=f(font_bold,27),fill=TEXT)
lines=[
    "O projeto foi construído para ser reproduzível, auditável e explicável",
    "de ponta a ponta: do dado bruto à validação, modelagem, BI e NLP.",
]
yy=985
for line in lines:
    d.text((82,yy),line,font=f(font_regular,22),fill=MUTED)
    yy+=40
d.text((82,1090),"Python  •  Pandas  •  Scikit-learn  •  Power BI  •  DAX",font=f(font_semibold,23),fill=CYAN)
footer(d,4,"Insight & Arquitetura")
img.convert("RGB").save(OUT/"04_insight_arquitetura.png",quality=95)

print(f"Created: {OUT}")
for p in sorted(OUT.glob("*.png")):
    print(p.name, Image.open(p).size)
