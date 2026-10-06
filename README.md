# Olist Intelligence

Análise do Brazilian E-Commerce Public Dataset by Olist com Pandas, scikit-learn e Power BI. O projeto produz duas tabelas analíticas, resultados de análise de reviews e imagens de referência dos dashboards.

![Painel executivo](assets/executive_overview.png)
![Análise de reviews](assets/customer_ai_intelligence.png)

## Dados e saídas

Baixe os nove CSVs do [dataset da Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) e coloque-os em `data/raw/` conforme [data/README.md](data/README.md).

O pipeline produz:

- `data/processed/orders_analytics.csv` e `.parquet`: uma linha por pedido;
- `data/processed/items_analytics.csv` e `.parquet`: uma linha por item;
- `data/ai/review_ai_analytics.csv`, resumos e métricas do modelo de reviews.

As tabelas de pedidos e itens preservam os identificadores originais e são validadas quanto a chaves, granularidade e conciliação de produtos e frete. A diferença entre pagamentos e itens é sinalizada, sem alterar os valores da fonte.

## Execução

Crie um ambiente virtual e instale as dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Execute a camada analítica e a análise de reviews:

```powershell
python src\full_pipeline.py
```

Para executar as etapas separadamente:

```powershell
python src\main.py
python src\ai_review_intelligence.py
```

Os scripts resolvem os dados a partir da pasta do projeto, mesmo quando o arquivo Python é chamado de outro diretório.

## Auditorias opcionais

As auditorias abaixo são ferramentas de diagnóstico e **não** são executadas por `full_pipeline.py`:

```powershell
python src\data_audit.py
python src\relational_audit.py
python src\audit_payments.py
python src\audit_financial_consistency.py
```

Elas inspecionam CSVs brutos, relações entre tabelas e casos financeiros específicos. As validações necessárias para construir as tabelas analíticas continuam no pipeline principal.

## Dashboards e Power BI

O [guia de construção do Power BI](dashboard/POWERBI_BUILD_GUIDE.md) usa os CSVs processados e a análise de reviews. O tema e as medidas ficam em `dashboard/`. O arquivo `.pbix` e as planilhas Excel geradas localmente não são versionados.

Scripts auxiliares, executados quando necessário:

```powershell
python src\export_powerbi_assets.py
python src\build_dashboard_compact.py
python src\build_dashboard_mockup.py
python src\build_ai_dashboard.py
python src\build_powerbi_source.py
python src\build_ai_powerbi_source.py
python src\build_linkedin_carousel.py
```

`export_powerbi_assets.py` gera os CSVs de referência consumidos pelos dois dashboards executivos. Os scripts `build_*_powerbi_source.py` criam planilhas Excel opcionais. O carrossel usa as tabelas processadas, as métricas de IA e as imagens finais em `assets/`.

## Leitura das métricas

Na base atual há 99.441 pedidos, 112.650 itens e 303 divergências financeiras entre pedidos comparáveis. Para pedidos entregues, o GMV dos produtos é R$ 13,22 milhões; ele não representa receita contábil da Olist.

A análise de sentimento usa as notas dos próprios reviews como rótulos aproximados: 1–2 negativo, 3 neutro, 4–5 positivo. A acurácia de 83,7% e o macro F1 de 0,67 medem concordância com esse critério, não com uma anotação humana independente.

A comparação entre satisfação e atraso considera somente pedidos com `order_status == "delivered"` e datas válidas. A nota média é cerca de 4,29 no prazo e 2,27 em atraso. É uma associação observada, não uma estimativa causal.
