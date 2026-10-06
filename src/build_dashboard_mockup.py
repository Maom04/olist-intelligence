from pathlib import Path
import pandas as pd
import html

ROOT = Path(r"C:\Projetos\olist-intelligence")
REF = ROOT / "dashboard" / "reference"
OUT = ROOT / "dashboard" / "reference" / "executive_overview.html"

kpis = pd.read_csv(REF / "kpi_reference.csv")
monthly = pd.read_csv(REF / "monthly_performance.csv")
cats = pd.read_csv(REF / "category_performance.csv").head(8)
states = pd.read_csv(REF / "state_performance.csv").head(8)

kv = {r.metric: r.value for r in kpis.itertuples()}

def brl(v):
    return ("R$ " + f"{v:,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")

def compact(v):
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M".replace(".", ",")
    if v >= 1_000:
        return f"{v/1_000:.1f}K".replace(".", ",")
    return f"{v:.0f}"

# line chart coordinates
w, h = 760, 220
pad_l, pad_r, pad_t, pad_b = 42, 18, 18, 34
vals = monthly["gmv"].tolist()
minv, maxv = min(vals), max(vals)
span = max(maxv-minv, 1)
pts = []
for i, v in enumerate(vals):
    x = pad_l + i * (w-pad_l-pad_r) / max(len(vals)-1,1)
    y = pad_t + (maxv-v) * (h-pad_t-pad_b) / span
    pts.append((x,y))
poly = " ".join(f"{x:.1f},{y:.1f}" for x,y in pts)

months = monthly["month"].tolist()
ticks_idx = sorted(set([0, len(months)//4, len(months)//2, 3*len(months)//4, len(months)-1]))
tick_svg = "".join(
    f'<text x="{pts[i][0]:.1f}" y="{h-7}" text-anchor="middle" class="axis">{html.escape(months[i])}</text>'
    for i in ticks_idx
)

# bar charts
catmax = cats["gmv"].max()
cat_rows = ""
for r in cats.itertuples():
    pct = 100*r.gmv/catmax
    label = str(r.product_category_name_english).replace("_"," ").title()
    cat_rows += f"""<div class="bar-row"><div class="bar-label">{html.escape(label)}</div><div class="bar-track"><div class="bar-fill" style="width:{pct:.1f}%"></div></div><div class="bar-value">{brl(r.gmv)}</div></div>"""

statemax = states["gmv"].max()
state_rows = ""
for r in states.itertuples():
    pct = 100*r.gmv/statemax
    state_rows += f"""<div class="bar-row state"><div class="bar-label">{html.escape(r.customer_state)}</div><div class="bar-track"><div class="bar-fill alt" style="width:{pct:.1f}%"></div></div><div class="bar-value">{brl(r.gmv)}</div></div>"""

html_text = f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Olist Intelligence</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#070B14;color:#E5E7EB;font-family:Segoe UI,Arial,sans-serif}}
.page{{width:1600px;height:900px;padding:46px 52px;background:
radial-gradient(circle at 84% 0%,rgba(124,58,237,.18),transparent 33%),
linear-gradient(180deg,#0B1020,#070B14)}}
.header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:26px}}
.title h1{{font-size:35px;margin:0;letter-spacing:.3px;color:#F8FAFC}}
.title p{{margin:8px 0 0;color:#94A3B8;font-size:15px}}
.badge{{border:1px solid #293246;background:#111827;border-radius:22px;padding:10px 16px;color:#CBD5E1;font-size:13px}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:18px}}
.card,.panel{{background:rgba(17,24,39,.9);border:1px solid #202A3B;border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,.16)}}
.card{{padding:18px 20px;height:112px}}
.card .label{{font-size:12px;text-transform:uppercase;letter-spacing:.8px;color:#8B98AA}}
.card .value{{font-size:30px;font-weight:650;margin-top:11px;color:#F8FAFC}}
.card .sub{{font-size:11px;color:#64748B;margin-top:3px}}
.grid{{display:grid;grid-template-columns:1.55fr .95fr;gap:18px}}
.panel{{padding:20px 22px}}
.panel h3{{margin:0 0 6px;font-size:15px;color:#F8FAFC}}
.panel p{{margin:0 0 14px;color:#64748B;font-size:11px}}
.line-panel{{height:320px}}
.lower{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin-top:18px}}
.small-panel{{height:255px}}
svg{{width:100%;height:230px;overflow:visible}}
.axis{{fill:#64748B;font-size:10px}}
.gridline{{stroke:#202A3B;stroke-width:1}}
.line{{fill:none;stroke:#8B5CF6;stroke-width:4;stroke-linejoin:round;stroke-linecap:round}}
.area{{fill:url(#grad)}}
.dot{{fill:#22D3EE;stroke:#0B1020;stroke-width:2}}
.bar-row{{display:grid;grid-template-columns:160px 1fr 90px;gap:10px;align-items:center;margin:13px 0}}
.bar-row.state{{grid-template-columns:35px 1fr 90px}}
.bar-label{{font-size:11px;color:#CBD5E1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.bar-track{{height:8px;background:#1F2937;border-radius:12px;overflow:hidden}}
.bar-fill{{height:100%;background:linear-gradient(90deg,#7C3AED,#A78BFA);border-radius:12px}}
.bar-fill.alt{{background:linear-gradient(90deg,#0891B2,#22D3EE)}}
.bar-value{{font-size:10px;text-align:right;color:#94A3B8}}
.metric-big{{font-size:42px;font-weight:700;margin-top:18px}}
.metric-caption{{color:#94A3B8;font-size:12px;margin-top:5px}}
.compare{{display:flex;gap:12px;margin-top:18px}}
.pill{{flex:1;padding:12px;border:1px solid #273247;border-radius:13px;background:#0F172A}}
.pill span{{display:block;color:#64748B;font-size:10px;margin-bottom:5px}}
.pill b{{font-size:17px;color:#F8FAFC}}
.foot{{position:absolute;left:52px;right:52px;bottom:22px;display:flex;justify-content:space-between;color:#475569;font-size:10px}}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="title"><h1>OLIST INTELLIGENCE</h1><p>E-commerce performance, logistics & customer experience</p></div>
    <div class="badge">Brazilian E-commerce • 2016–2018</div>
  </div>
  <div class="cards">
    <div class="card"><div class="label">GMV entregue</div><div class="value">{brl(kv["GMV"])}</div><div class="sub">valor dos produtos vendidos</div></div>
    <div class="card"><div class="label">Pedidos entregues</div><div class="value">{compact(kv["Pedidos entregues"])}</div><div class="sub">pedidos concluídos</div></div>
    <div class="card"><div class="label">Clientes únicos</div><div class="value">{compact(kv["Clientes únicos"])}</div><div class="sub">em pedidos entregues</div></div>
    <div class="card"><div class="label">Ticket médio</div><div class="value">{brl(kv["Ticket médio"])}</div><div class="sub">GMV por pedido entregue</div></div>
    <div class="card"><div class="label">Avaliação média</div><div class="value">{kv["Avaliação média"]:.2f}</div><div class="sub">escala de 1 a 5</div></div>
  </div>

  <div class="grid">
    <div class="panel line-panel">
      <h3>Evolução mensal do GMV</h3><p>Pedidos com status delivered</p>
      <svg viewBox="0 0 {w} {h}">
        <defs><linearGradient id="grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#7C3AED" stop-opacity=".34"/><stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/></linearGradient></defs>
        <line x1="{pad_l}" y1="55" x2="{w-pad_r}" y2="55" class="gridline"/>
        <line x1="{pad_l}" y1="105" x2="{w-pad_r}" y2="105" class="gridline"/>
        <line x1="{pad_l}" y1="155" x2="{w-pad_r}" y2="155" class="gridline"/>
        <polygon points="{pad_l},{h-pad_b} {poly} {w-pad_r},{h-pad_b}" class="area"/>
        <polyline points="{poly}" class="line"/>
        {tick_svg}
      </svg>
    </div>
    <div class="panel line-panel">
      <h3>Top categorias por GMV</h3><p>Ranking de produtos em pedidos entregues</p>
      {cat_rows}
    </div>
  </div>

  <div class="lower">
    <div class="panel small-panel"><h3>Performance por estado</h3><p>Estados com maior GMV entregue</p>{state_rows}</div>
    <div class="panel small-panel"><h3>Eficiência logística</h3><p>Entregas comparadas ao prazo estimado</p>
      <div class="metric-big">{kv["Taxa de atraso"]*100:.1f}%</div>
      <div class="metric-caption">dos pedidos entregues com data válida chegaram após a previsão</div>
      <div class="compare">
        <div class="pill"><span>Frete total</span><b>{brl(kv["Frete total"])}</b></div>
        <div class="pill"><span>Clientes recorrentes</span><b>{int(kv["Clientes recorrentes"]):,}</b></div>
      </div>
    </div>
    <div class="panel small-panel"><h3>Retenção de clientes</h3><p>Recorrência observada no período</p>
      <div class="metric-big">{kv["Taxa clientes recorrentes"]*100:.1f}%</div>
      <div class="metric-caption">dos clientes de pedidos entregues possuem mais de um pedido na base</div>
      <div class="compare">
        <div class="pill"><span>Base de clientes</span><b>{compact(kv["Clientes únicos"])}</b></div>
        <div class="pill"><span>Recorrentes</span><b>{compact(kv["Clientes recorrentes"])}</b></div>
      </div>
    </div>
  </div>
  <div class="foot"><span>OLIST INTELLIGENCE • Python/Pandas → Power BI → AI Insights</span><span>Portfolio dashboard concept</span></div>
</div>
</body>
</html>"""

OUT.write_text(html_text, encoding="utf-8")
print(OUT)
