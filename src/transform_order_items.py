from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw")


def load_order_items() -> pd.DataFrame:
    return pd.read_csv(
        RAW_PATH / "olist_order_items_dataset.csv"
    )


def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Converte a data limite de envio
    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    # Valor total de cada item
    df["item_total_value"] = (
        df["price"]
        + df["freight_value"]
    )

    return df


def aggregate_order_items(df: pd.DataFrame) -> pd.DataFrame:
    order_items_agg = (
        df.groupby("order_id")
        .agg(
            items_count=("order_item_id", "count"),
            products_count=("product_id", "nunique"),
            sellers_count=("seller_id", "nunique"),
            products_value=("price", "sum"),
            freight_value=("freight_value", "sum"),
            order_items_total=("item_total_value", "sum"),
        )
        .reset_index()
    )

    return order_items_agg


def main() -> None:
    items = load_order_items()

    print("ANTES DA TRANSFORMAÇÃO:")
    print(f"Linhas: {len(items):,}")
    print(f"Pedidos: {items['order_id'].nunique():,}")

    items = transform_order_items(items)

    order_items_agg = aggregate_order_items(items)

    print("\nAPÓS AGREGAÇÃO:")
    print(f"Linhas: {len(order_items_agg):,}")
    print(f"Pedidos: {order_items_agg['order_id'].nunique():,}")

    print("\nTIPOS:")
    print(order_items_agg.dtypes)

    print("\nEXEMPLO:")
    print(order_items_agg.head())

    print("\nRESUMO:")
    print(
        order_items_agg[
            [
                "items_count",
                "products_count",
                "sellers_count",
                "products_value",
                "freight_value",
                "order_items_total",
            ]
        ].describe()
    )


if __name__ == "__main__":
    main()
