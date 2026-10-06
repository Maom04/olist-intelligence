import html
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
AI = ROOT / "data" / "ai"
REF = ROOT / "dashboard" / "reference"
OUT = REF / "customer_ai_intelligence.html"


def main() -> None:
    REF.mkdir(parents=True, exist_ok=True)
    metrics = json.loads((AI / "ai_model_metrics.json").read_text(encoding="utf-8"))
    sent = pd.read_csv(AI / "sentiment_summary.csv")
    topics = pd.read_csv(AI / "topic_summary.csv")

    orders = pd.read_csv(
        ROOT / "data" / "processed" / "orders_analytics.csv", low_memory=False
    )
    orders = orders.loc[orders["order_status"].eq("delivered")]
    flag = orders["is_delayed"].astype("string")
    rating_late = orders.loc[flag.eq("True"), "latest_review_score"].dropna().mean()
    rating_ontime = orders.loc[flag.eq("False"), "latest_review_score"].dropna().mean()
    ontime_label = f"{rating_ontime:.2f}".replace(".", ",")
    late_label = f"{rating_late:.2f}".replace(".", ",")
    difference_label = f"{rating_ontime - rating_late:.2f}".replace(".", ",")

    sent_map = {r.ai_sentiment: r for r in sent.itertuples()}
    pos = sent_map["Positivo"]
    neg = sent_map["Negativo"]
    neu = sent_map["Neutro"]

    problem_topics = topics[topics["ai_topic"] != "Experiência positiva"].copy()
    max_reviews = problem_topics["reviews"].max()

    bars = ""
    for r in problem_topics.itertuples():
        width = 100 * r.reviews / max_reviews
        bars += f"""
        <div class="barrow">
          <div class="blabel">{html.escape(str(r.ai_topic))}</div>
          <div class="track"><div class="fill" style="width:{width:.1f}%"></div></div>
          <div class="bvalue">{int(r.reviews):,}</div>
        </div>"""

    sentbars = ""
    for label, obj, cls in [
        ("Positivo", pos, "pos"),
        ("Negativo", neg, "neg"),
        ("Neutro", neu, "neu"),
    ]:
        sentbars += f"""
        <div class="sent-row">
          <div class="sent-head"><span>{label}</span><b>{obj.share * 100:.1f}%</b></div>
          <div class="sent-track"><div class="sent-fill {cls}" style="width:{obj.share * 100:.1f}%"></div></div>
        </div>"""

    doc = f"""<!doctype html>
    <html lang="pt-br"><head><meta charset="utf-8"><title>Customer & AI Intelligence</title>
    <style>
    *{{box-sizing:border-box}} html,body{{margin:0;background:#070B14;color:#E5E7EB;font-family:Segoe UI,Arial,sans-serif;overflow:hidden}}
    .page{{width:1440px;height:810px;padding:28px 34px 22px;background:radial-gradient(circle at 80% -8%,rgba(34,211,238,.13),transparent 32%),#080D18}}
    .header{{height:66px;display:flex;justify-content:space-between;align-items:flex-start}}
    h1{{margin:0;font-size:28px;letter-spacing:.2px;color:#fff}} .sub{{font-size:12px;color:#8391A6;margin-top:5px}}
    .badge{{font-size:11px;border:1px solid #293246;border-radius:18px;padding:8px 12px;background:#101827;color:#B9C3D2}}
    .cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:11px;height:96px;margin-bottom:12px}}
    .card,.panel{{background:#101827;border:1px solid #222E41;border-radius:14px}}
    .card{{padding:13px 16px}} .label{{font-size:9px;color:#8A98AC;text-transform:uppercase;letter-spacing:.65px}}
    .val{{font-size:24px;font-weight:700;color:#fff;margin-top:7px;white-space:nowrap}} .hint{{font-size:9px;color:#65758A;margin-top:2px}}
    .grid{{display:grid;grid-template-columns:1.12fr .88fr;gap:12px;height:292px;margin-bottom:12px}}
    .bottom{{display:grid;grid-template-columns:1.2fr .8fr;gap:12px;height:248px}}
    .panel{{padding:16px 18px;overflow:hidden}} h3{{margin:0;font-size:14px;color:#fff}} .p{{font-size:9px;color:#64748B;margin:4px 0 13px}}
    .sent-row{{margin:15px 0}} .sent-head{{display:flex;justify-content:space-between;font-size:11px;color:#CBD5E1;margin-bottom:6px}}
    .sent-track,.track{{height:9px;background:#1B2636;border-radius:9px;overflow:hidden}} .sent-fill,.fill{{height:100%;border-radius:9px}}
    .pos{{background:linear-gradient(90deg,#10B981,#34D399)}} .neg{{background:linear-gradient(90deg,#EF4444,#FB7185)}} .neu{{background:linear-gradient(90deg,#F59E0B,#FBBF24)}}
    .barrow{{display:grid;grid-template-columns:190px 1fr 54px;gap:10px;align-items:center;margin:14px 0}}
    .blabel{{font-size:10px;color:#CBD5E1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}} .fill{{background:linear-gradient(90deg,#7C3AED,#A78BFA)}} .bvalue{{font-size:10px;color:#94A3B8;text-align:right}}
    .compare{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}}
    .ratebox{{border:1px solid #273247;border-radius:12px;background:#0D1524;padding:15px}} .ratebox small{{font-size:9px;color:#64748B}} .ratebox b{{display:block;font-size:31px;margin-top:7px;color:#fff}}
    .delta{{font-size:38px;font-weight:750;margin-top:18px;color:#22D3EE}} .desc{{font-size:11px;color:#94A3B8;line-height:1.45;margin-top:6px}}
    .modelbox{{margin-top:15px;border:1px solid #273247;border-radius:12px;padding:14px;background:#0D1524}}
    .modelbox div{{font-size:10px;color:#AAB5C4;margin:7px 0}} .modelbox span{{color:#64748B}}
    .foot{{position:absolute;left:34px;right:34px;bottom:7px;display:flex;justify-content:space-between;color:#3F4C60;font-size:8px}}
    </style></head><body><div class="page">
    <div class="header"><div><h1>CUSTOMER & AI INTELLIGENCE</h1><div class="sub">NLP aplicado a avaliações reais de clientes da Olist</div></div><div class="badge">TF-IDF • Classificação • Topic Modeling</div></div>

    <div class="cards">
    <div class="card"><div class="label">Comentários analisados</div><div class="val">{metrics["comments_used"]:,}</div><div class="hint">reviews com texto válido</div></div>
    <div class="card"><div class="label">Acurácia do modelo</div><div class="val">{metrics["accuracy"] * 100:.1f}%</div><div class="hint">holdout de {metrics["test_rows"]:,} comentários</div></div>
    <div class="card"><div class="label">Sentimento positivo</div><div class="val">{pos.share * 100:.1f}%</div><div class="hint">{int(pos.reviews):,} comentários</div></div>
    <div class="card"><div class="label">Sentimento negativo</div><div class="val">{neg.share * 100:.1f}%</div><div class="hint">{int(neg.reviews):,} comentários</div></div>
    <div class="card"><div class="label">Macro F1</div><div class="val">{metrics["macro_f1"]:.2f}</div><div class="hint">3 classes de sentimento</div></div>
    </div>

    <div class="grid">
    <div class="panel"><h3>Distribuição de sentimento prevista pela IA</h3><div class="p">Classificador treinado a partir das notas 1–5 dos próprios reviews</div>{sentbars}</div>
    <div class="panel"><h3>Principais temas em experiências problemáticas</h3><div class="p">Tópicos descobertos por NMF em comentários negativos/neutros</div>{bars}</div>
    </div>

    <div class="bottom">
    <div class="panel"><h3>Impacto do atraso na satisfação</h3><div class="p">Nota média do review conforme o desempenho logístico</div>
    <div class="compare">
    <div class="ratebox"><small>ENTREGUE NO PRAZO</small><b>{ontime_label}</b></div>
    <div class="ratebox"><small>ENTREGUE ATRASADO</small><b>{late_label}</b></div>
    </div>
    <div class="delta">−{difference_label} pts</div><div class="desc">Pedidos atrasados apresentam queda expressiva na avaliação média, indicando forte relação entre logística e experiência do cliente.</div></div>

    <div class="panel"><h3>Como a camada de IA foi construída</h3><div class="p">Pipeline reproduzível, sem uso de labels inventados</div>
    <div class="modelbox">
    <div><span>Sentimento:</span> {metrics["model"]}</div>
    <div><span>Treino/Teste:</span> {metrics["train_rows"]:,} / {metrics["test_rows"]:,}</div>
    <div><span>Tópicos:</span> {metrics["topic_model"]}</div>
    <div><span>Classes:</span> Positivo • Neutro • Negativo</div>
    <div><span>Entrada:</span> comentários reais dos clientes</div>
    </div></div>
    </div>

    <div class="foot"><span>OLIST INTELLIGENCE • Python/Pandas → Machine Learning → Power BI</span><span>Customer & AI Intelligence</span></div>
    </div></body></html>"""
    OUT.write_text(doc, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
