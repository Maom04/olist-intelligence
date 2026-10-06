from pathlib import Path

import pandas as pd

from transform_order_items import (
    load_order_items,
    transform_order_items,
)

from transform_orders import (
    load_orders,
    transform_orders,
    add_purchase_fields,
)

from transform_reviews import (
    load_reviews,
    transform_reviews,
    aggregate_reviews,
)


ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw"
PROCESSED_PATH = ROOT / "data" / "processed"


def load_products() -> pd.DataFrame:
    return pd.read_csv(RAW_PATH / "olist_products_dataset.csv")


def load_translation() -> pd.DataFrame:
    return pd.read_csv(RAW_PATH / "product_category_name_translation.csv")


def load_sellers() -> pd.DataFrame:
    return pd.read_csv(RAW_PATH / "olist_sellers_dataset.csv")


def load_customers() -> pd.DataFrame:
    return pd.read_csv(RAW_PATH / "olist_customers_dataset.csv")


def prepare_products() -> pd.DataFrame:
    products = load_products()
    translation = load_translation()

    products = products.merge(
        translation,
        on="product_category_name",
        how="left",
        validate="many_to_one",
    )

    # Existem duas categorias no dataset que não
    # aparecem na tabela oficial de tradução.
    manual_translation = {
        "pc_gamer": "pc_gamer",
        "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_and_food_preparation",
    }

    missing_translation_mask = (
        products["product_category_name_english"].isna()
        & products["product_category_name"].notna()
    )

    products.loc[
        missing_translation_mask,
        "product_category_name_english",
    ] = products.loc[
        missing_translation_mask,
        "product_category_name",
    ].map(manual_translation)

    products["product_category_name_english"] = products[
        "product_category_name_english"
    ].fillna("unknown")

    products["product_volume_cm3"] = (
        products["product_length_cm"]
        * products["product_height_cm"]
        * products["product_width_cm"]
    )

    return products


def build_items_analytics() -> pd.DataFrame:
    """Uma linha por item de pedido."""

    items = load_order_items()
    items = transform_order_items(items)

    original_item_count = len(items)

    products = prepare_products()

    sellers = load_sellers()

    orders = load_orders()
    orders = transform_orders(orders)

    customers = load_customers()

    reviews = load_reviews()
    reviews = transform_reviews(reviews)
    reviews_agg = aggregate_reviews(reviews)

    df = items.merge(
        products,
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    df = df.merge(
        sellers,
        on="seller_id",
        how="left",
        validate="many_to_one",
    )

    order_context = orders[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "delivery_days",
            "estimated_delivery_days",
            "delay_days",
            "is_delayed",
        ]
    ]

    df = df.merge(
        order_context,
        on="order_id",
        how="left",
        validate="many_to_one",
    )

    customer_context = customers[
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state",
        ]
    ]

    df = df.merge(
        customer_context,
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    review_context = reviews_agg[
        [
            "order_id",
            "latest_review_score",
            "review_score_mean",
            "has_review_comment",
        ]
    ]

    df = df.merge(
        review_context,
        on="order_id",
        how="left",
        validate="many_to_one",
    )

    if len(df) != original_item_count:
        raise ValueError(
            "Erro de granularidade: "
            f"a tabela original tinha {original_item_count:,} itens "
            f"e o resultado possui {len(df):,}."
        )

    duplicated_item_keys = df.duplicated(
        subset=[
            "order_id",
            "order_item_id",
        ]
    ).sum()

    if duplicated_item_keys > 0:
        raise ValueError(
            f"Foram encontradas {duplicated_item_keys:,} chaves duplicadas de item."
        )

    add_purchase_fields(df)

    df["freight_share"] = df["freight_value"] / df["item_total_value"]

    # Sem um dos estados, não há como classificar a entrega interestadual.
    df["is_interstate"] = pd.Series(
        pd.NA,
        index=df.index,
        dtype="boolean",
    )

    location_mask = df["customer_state"].notna() & df["seller_state"].notna()

    df.loc[
        location_mask,
        "is_interstate",
    ] = (
        df.loc[
            location_mask,
            "customer_state",
        ]
        != df.loc[
            location_mask,
            "seller_state",
        ]
    )

    integer_columns = [
        "order_item_id",
        "purchase_year",
        "purchase_month",
        "latest_review_score",
    ]

    for column in integer_columns:
        df[column] = df[column].astype("Int64")

    df = df.sort_values(
        by=[
            "order_purchase_timestamp",
            "order_id",
            "order_item_id",
        ]
    ).reset_index(drop=True)

    return df


def save_items_analytics(
    df: pd.DataFrame,
) -> None:
    PROCESSED_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = PROCESSED_PATH / "items_analytics.csv"

    parquet_path = PROCESSED_PATH / "items_analytics.parquet"

    df.to_csv(
        csv_path,
        index=False,
    )

    df.to_parquet(
        parquet_path,
        index=False,
    )

    print(f"\nCSV salvo em: {csv_path}")

    print(f"Parquet salvo em: {parquet_path}")


def main() -> None:
    df = build_items_analytics()

    print("=" * 80)
    print("ITEMS ANALYTICS")
    print("=" * 80)

    print(f"Linhas: {len(df):,}")

    print(f"Pedidos únicos: {df['order_id'].nunique():,}")

    print(f"Produtos únicos: {df['product_id'].nunique():,}")

    print(f"Vendedores únicos: {df['seller_id'].nunique():,}")

    print(f"Colunas: {df.shape[1]}")

    print("\nTOP 10 CATEGORIAS POR GMV:")

    category_gmv = (
        df.groupby(
            "product_category_name_english",
            dropna=False,
        )["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    print(category_gmv)

    print("\nITENS INTERESTADUAIS:")

    print(df["is_interstate"].value_counts(dropna=False))

    print("\nPRODUTOS CLASSIFICADOS COMO UNKNOWN:")

    unknown_products = df.loc[
        df["product_category_name_english"] == "unknown",
        "product_id",
    ].nunique()

    print(f"{unknown_products:,}")

    print("\nPARTICIPAÇÃO DO FRETE:")

    print(df["freight_share"].describe())

    print("\nEXEMPLO:")

    example_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "product_category_name_english",
        "seller_state",
        "customer_state",
        "price",
        "freight_value",
        "item_total_value",
        "latest_review_score",
        "is_delayed",
        "is_interstate",
    ]

    print(df[example_columns].head())

    save_items_analytics(df)


if __name__ == "__main__":
    main()
