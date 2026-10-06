# Olist Intelligence — Power BI Build Guide

## Data sources

Execute o pipeline primeiro e importe:

- `data/processed/orders_analytics.csv`
- `data/processed/items_analytics.csv`
- `data/ai/review_ai_analytics.csv` (camada de NLP)

## Model

Crie os relacionamentos:

- `orders_analytics[order_id]` 1 → * `items_analytics[order_id]`
- `orders_analytics[order_id]` 1 → * `review_ai[order_id]`
- Cross-filter direction: **Single**

## Theme

Importe:

- `dashboard/olist_intelligence_theme.json`

## Measures

Use as medidas de:

- `dashboard/measures.dax`

## Executive Overview

Canvas: **16:9**

Título: **OLIST INTELLIGENCE**

Subtítulo: **E-commerce Performance, Logistics & Customer Experience**

### Top cards

1. GMV
2. Pedidos Entregues
3. Clientes Únicos
4. Ticket Médio
5. Avaliação Média

### Main visuals

- Line chart: `AnoMes → GMV`
- Horizontal bar: `product_category_name_english → GMV por Item`
- Horizontal bar: `customer_state → GMV`
- KPI/Card: Taxa de Atraso
- KPI/Card: Taxa de Clientes Recorrentes

## Valores de referência

Com a versão atual do dataset:

- GMV entregue: **R$ 13.221.498,11**
- Pedidos entregues: **96.478**
- Clientes únicos em pedidos entregues: **93.358**
- Ticket médio: **R$ 137,04**
- Avaliação média: **4,16**
- Taxa de atraso: **6,8%**
- Frete total: **R$ 2.198.275,64**
- Clientes recorrentes: **2.979**
- Taxa de clientes recorrentes: **3,2%**

## Portfolio reference

As imagens finais do dashboard estão em:

- `assets/executive_overview.png`
- `assets/customer_ai_intelligence.png`

O arquivo `.pbix` e as fontes Excel usadas localmente não são versionados porque incorporam dados derivados e aumentam o tamanho do repositório.
