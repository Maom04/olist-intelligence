# Dados

Os arquivos de dados não são versionados neste repositório.

## Dataset de origem

Use o **Brazilian E-Commerce Public Dataset by Olist**, disponível publicamente no Kaggle:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Baixe e coloque os 9 CSVs em:

```text
data/raw/
├── olist_customers_dataset.csv
├── olist_geolocation_dataset.csv
├── olist_order_items_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_orders_dataset.csv
├── olist_products_dataset.csv
├── olist_sellers_dataset.csv
└── product_category_name_translation.csv
```

As pastas `data/processed/` e `data/ai/` são geradas localmente pelo pipeline e também não são enviadas ao GitHub.

Essa decisão mantém o repositório leve e evita versionar datasets e artefatos derivados desnecessariamente.
