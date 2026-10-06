from pathlib import Path
import pandas as pd, html

ROOT=Path(r"C:\Projetos\olist-intelligence")
REF=ROOT/"dashboard"/"reference"
OUT=REF/"executive_overview_compact.html"

k=pd.read_csv(REF/"kpi_reference.csv")
m=pd.read_csv(REF/"monthly_performance.csv")
c=pd.read_csv(REF/"category_performance.csv").head(6)
s=pd.read_csv(REF/"state_performance.csv").head(6)
kv={r.metric:r.value for r in k.itertuples()}

def brl(v):
    return ("R$ "+f"{v:,.2f}").replace(",","X").replace(".",",").replace("X",".")

def short(v):
    if v>=1_000_000:return f"{v/1_000_000:.1f}M".replace(".",",")
    if v>=1000:return f"{v/1000:.1f}K".replace(".",",")
    return str(int(v))

W,H=690,160
pl,pr,pt,pb=30,12,10,25
vals=m.gmv.tolist(); mn,mx=min(vals),max(vals); sp=max(mx-mn,1)
pts=[]
for i,v in enumerate(vals):
    x=pl+i*(W-pl-pr)/max(len(vals)-1,1)
    y=pt+(mx-v)*(H-pt-pb)/sp
    pts.append((x,y))
poly=" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
ticks=[0,len(vals)//2,len(vals)-1]
ticksvg="".join(f'<text x="{pts[i][0]:.1f}" y="{H-4}" text-anchor="middle" class="axis">{m.month.iloc[i]}</text>' for i in ticks)

cmx=c.gmv.max()
cat="".join(f'<div class="bar"><span>{html.escape(str(r.product_category_name_english).replace("_"," ").title())}</span><i><b style="width:{100*r.gmv/cmx:.1f}%"></b></i><em>{brl(r.gmv)}</em></div>' for r in c.itertuples())
smx=s.gmv.max()
states="".join(f'<div class="bar state"><span>{r.customer_state}</span><i><b style="width:{100*r.gmv/smx:.1f}%"></b></i><em>{brl(r.gmv)}</em></div>' for r in s.itertuples())

doc=f"""<!doctype html><html><head><meta charset="utf-8"><title>Olist Intelligence Compact</title>
<style>
*{{box-sizing:border-box}} html,body{{margin:0;background:#070B14;color:#E5E7EB;font-family:Segoe UI,Arial,sans-serif;overflow:hidden}}
.page{{width:100vw;height:100vh;min-width:1100px;padding:24px 28px 20px;background:radial-gradient(circle at 78% -10%,rgba(124,58,237,.17),transparent 31%),#080D18}}
.header{{height:58px;display:flex;justify-content:space-between;align-items:flex-start}}
h1{{margin:0;font-size:27px;color:#fff;letter-spacing:.2px}} .sub{{font-size:12px;color:#8391A6;margin-top:5px}} .badge{{font-size:11px;border:1px solid #293246;border-radius:18px;padding:7px 12px;background:#101827;color:#B9C3D2}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;height:88px;margin-bottom:10px}}
.card,.panel{{background:#101827;border:1px solid #222E41;border-radius:13px}}
.card{{padding:12px 15px}} .label{{font-size:9px;color:#8A98AC;text-transform:uppercase;letter-spacing:.65px}} .val{{font-size:23px;font-weight:700;color:#fff;margin-top:7px;white-space:nowrap}} .hint{{font-size:9px;color:#65758A;margin-top:2px}}
.mid{{display:grid;grid-template-columns:1.55fr .9fr;gap:10px;height:255px;margin-bottom:10px}}
.bottom{{display:grid;grid-template-columns:1.15fr .925fr .925fr;gap:10px;height:215px}}
.panel{{padding:14px 16px;overflow:hidden}} h3{{margin:0;font-size:13px;color:#fff}} .p{{font-size:9px;color:#64748B;margin:3px 0 8px}}
svg{{width:100%;height:178px}} .grid{{stroke:#202A3B;stroke-width:1}} .line{{fill:none;stroke:#8B5CF6;stroke-width:3}} .area{{fill:url(#g)}} .axis{{fill:#64748B;font-size:8px}}
.bar{{display:grid;grid-template-columns:135px 1fr 78px;gap:8px;align-items:center;margin:9px 0}} .bar.state{{grid-template-columns:26px 1fr 78px}}
.bar span{{font-size:9px;color:#D6DCE6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}} .bar i{{height:6px;background:#1C2737;border-radius:8px;overflow:hidden}} .bar b{{display:block;height:100%;background:linear-gradient(90deg,#7C3AED,#A78BFA)}} .state b{{background:linear-gradient(90deg,#0891B2,#22D3EE)}} .bar em{{font-style:normal;font-size:8px;text-align:right;color:#91A0B5}}
.big{{font-size:34px;font-weight:750;color:#fff;margin-top:18px}} .desc{{font-size:10px;color:#8391A6;line-height:1.35;margin-top:3px}}
.mini{{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:14px}} .pill{{border:1px solid #29364A;border-radius:10px;padding:8px 9px;background:#0D1524}} .pill small{{display:block;font-size:8px;color:#65758A;margin-bottom:3px}} .pill b{{font-size:13px;color:#fff}}
.foot{{position:absolute;left:28px;right:28px;bottom:7px;display:flex;justify-content:space-between;color:#3F4C60;font-size:8px}}
</style></head><body><div class="page">
<div class="header"><div><h1>OLIST INTELLIGENCE</h1><div class="sub">E-commerce Performance, Logistics & Customer Experience</div></div><div class="badge">Brazilian E-commerce • 2016–2018</div></div>
<div class="cards">
<div class="card"><div class="label">GMV entregue</div><div class="val">{brl(kv["GMV"])}</div><div class="hint">valor dos produtos vendidos</div></div>
<div class="card"><div class="label">Pedidos entregues</div><div class="val">{short(kv["Pedidos entregues"])}</div><div class="hint">pedidos concluídos</div></div>
<div class="card"><div class="label">Clientes únicos</div><div class="val">{short(kv["Clientes únicos"])}</div><div class="hint">pedidos entregues</div></div>
<div class="card"><div class="label">Ticket médio</div><div class="val">{brl(kv["Ticket médio"])}</div><div class="hint">GMV por pedido</div></div>
<div class="card"><div class="label">Avaliação média</div><div class="val">{kv["Avaliação média"]:.2f}</div><div class="hint">escala de 1 a 5</div></div>
</div>
<div class="mid">
<div class="panel"><h3>Evolução mensal do GMV</h3><div class="p">Pedidos entregues ao longo do período</div><svg viewBox="0 0 {W} {H}"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#7C3AED" stop-opacity=".33"/><stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/></linearGradient></defs><line x1="{pl}" y1="52" x2="{W-pr}" y2="52" class="grid"/><line x1="{pl}" y1="95" x2="{W-pr}" y2="95" class="grid"/><polygon points="{pl},{H-pb} {poly} {W-pr},{H-pb}" class="area"/><polyline points="{poly}" class="line"/>{ticksvg}</svg></div>
<div class="panel"><h3>Top categorias por GMV</h3><div class="p">Pedidos entregues</div>{cat}</div>
</div>
<div class="bottom">
<div class="panel"><h3>Performance por estado</h3><div class="p">Maiores mercados por GMV</div>{states}</div>
<div class="panel"><h3>Eficiência logística</h3><div class="p">Entrega comparada ao prazo previsto</div><div class="big">{kv["Taxa de atraso"]*100:.1f}%</div><div class="desc">dos pedidos entregues com data válida chegaram após a previsão.</div><div class="mini"><div class="pill"><small>Frete total</small><b>{short(kv["Frete total"])}</b></div><div class="pill"><small>Recorrentes</small><b>{short(kv["Clientes recorrentes"])}</b></div></div></div>
<div class="panel"><h3>Retenção de clientes</h3><div class="p">Recorrência observada no período</div><div class="big">{kv["Taxa clientes recorrentes"]*100:.1f}%</div><div class="desc">dos clientes de pedidos entregues aparecem em mais de um pedido na base.</div><div class="mini"><div class="pill"><small>Base</small><b>{short(kv["Clientes únicos"])}</b></div><div class="pill"><small>Recorrentes</small><b>{short(kv["Clientes recorrentes"])}</b></div></div></div>
</div>
<div class="foot"><span>OLIST INTELLIGENCE • Python/Pandas → Power BI → AI Insights</span><span>Executive Overview</span></div>
</div></body></html>"""
OUT.write_text(doc,encoding="utf-8")
print(OUT)
