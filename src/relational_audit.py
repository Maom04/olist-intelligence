from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw")


def load_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(RAW_PATH / filename)


def main() -> None:
    customers = load_csv("olist_customers_dataset.csv")
    orders = load_csv("olist_orders_dataset.csv")
    items = load_csv("olist_order_items_dataset.csv")
    payments = load_csv("olist_order_payments_dataset.csv")
    reviews = load_csv("olist_order_reviews_dataset.csv")
    products = load_csv("olist_products_dataset.csv")
    sellers = load_csv("olist_sellers_dataset.csv")
    geolocation = load_csv("olist_geolocation_dataset.csv")
    translation = load_csv("product_category_name_translation.csv")

    print("=" * 80)
    print("1. UNICIDADE DAS PRINCIPAIS CHAVES")
    print("=" * 80)

    print(
        f"customers.customer_id: "
        f"{customers['customer_id'].nunique():,} únicos "
        f"/ {len(customers):,} linhas"
    )

    print(
        f"customers.customer_unique_id: "
        f"{customers['customer_unique_id'].nunique():,} únicos "
        f"/ {len(customers):,} linhas"
    )

    print(
        f"orders.order_id: "
        f"{orders['order_id'].nunique():,} únicos "
        f"/ {len(orders):,} linhas"
    )

    print(
        f"products.product_id: "
        f"{products['product_id'].nunique():,} únicos "
        f"/ {len(products):,} linhas"
    )

    print(
        f"sellers.seller_id: "
        f"{sellers['seller_id'].nunique():,} únicos "
        f"/ {len(sellers):,} linhas"
    )

    print("\n" + "=" * 80)
    print("2. CARDINALIDADE DAS TABELAS")
    print("=" * 80)

    print(
        f"Pedidos presentes em order_items: "
        f"{items['order_id'].nunique():,}"
    )

    print(
        f"Pedidos presentes em payments: "
        f"{payments['order_id'].nunique():,}"
    )

    print(
        f"Pedidos presentes em reviews: "
        f"{reviews['order_id'].nunique():,}"
    )

    print(
        f"Pedidos com mais de 1 item: "
        f"{(items.groupby('order_id').size() > 1).sum():,}"
    )

    print(
        f"Pedidos com mais de 1 pagamento: "
        f"{(payments.groupby('order_id').size() > 1).sum():,}"
    )

    print(
        f"Pedidos com mais de 1 review: "
        f"{(reviews.groupby('order_id').size() > 1).sum():,}"
    )

    print("\n" + "=" * 80)
    print("3. CHAVES ÓRFÃS")
    print("=" * 80)

    customer_orphans = (
        set(orders["customer_id"])
        - set(customers["customer_id"])
    )

    item_order_orphans = (
        set(items["order_id"])
        - set(orders["order_id"])
    )

    product_orphans = (
        set(items["product_id"])
        - set(products["product_id"])
    )

    seller_orphans = (
        set(items["seller_id"])
        - set(sellers["seller_id"])
    )

    print(f"orders → customers: {len(customer_orphans):,}")
    print(f"items → orders: {len(item_order_orphans):,}")
    print(f"items → products: {len(product_orphans):,}")
    print(f"items → sellers: {len(seller_orphans):,}")

    print("\n" + "=" * 80)
    print("4. STATUS DOS PEDIDOS")
    print("=" * 80)

    print(orders["order_status"].value_counts())

    print("\n" + "=" * 80)
    print("5. DATAS AUSENTES POR STATUS")
    print("=" * 80)

    date_columns = [
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
    ]

    for column in date_columns:
        print(f"\n{column}")
        print(
            orders.loc[
                orders[column].isna(),
                "order_status",
            ].value_counts()
        )

    print("\n" + "=" * 80)
    print("6. GEOLOCALIZAÇÃO")
    print("=" * 80)

    print(
        f"Linhas: {len(geolocation):,}"
    )

    print(
        f"CEPs únicos: "
        f"{geolocation['geolocation_zip_code_prefix'].nunique():,}"
    )

    print(
        f"Duplicatas exatas: "
        f"{geolocation.duplicated().sum():,}"
    )

    print("\n" + "=" * 80)
    print("7. CATEGORIAS DE PRODUTOS")
    print("=" * 80)

    categories = set(
        products["product_category_name"]
        .dropna()
        .unique()
    )

    translated_categories = set(
        translation["product_category_name"]
        .dropna()
        .unique()
    )

    missing_translation = categories - translated_categories

    print(
        f"Categorias nos produtos: "
        f"{len(categories):,}"
    )

    print(
        f"Categorias traduzidas: "
        f"{len(translated_categories):,}"
    )

    print(
        f"Categorias sem tradução: "
        f"{len(missing_translation):,}"
    )

    if missing_translation:
        print(sorted(missing_translation))


if __name__ == "__main__":
    main()
