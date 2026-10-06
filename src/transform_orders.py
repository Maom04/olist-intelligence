from pathlib import Path

import pandas as pd


RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw"

DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def load_orders() -> pd.DataFrame:
    return pd.read_csv(RAW_PATH / "olist_orders_dataset.csv")


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for column in DATE_COLUMNS:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days

    df["estimated_delivery_days"] = (
        df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]
    ).dt.days

    # Atraso é medido em dias de calendário, sem considerar o horário.
    delivered_date = df["order_delivered_customer_date"].dt.normalize()

    estimated_date = df["order_estimated_delivery_date"].dt.normalize()

    df["delay_days"] = (delivered_date - estimated_date).dt.days

    # Pedidos sem as duas datas permanecem sem classificação de atraso.
    df["is_delayed"] = pd.Series(pd.NA, index=df.index, dtype="boolean")

    delivered_mask = delivered_date.notna() & estimated_date.notna()

    df.loc[delivered_mask, "is_delayed"] = (
        delivered_date[delivered_mask] > estimated_date[delivered_mask]
    )

    return df


def add_purchase_fields(df: pd.DataFrame) -> None:
    purchase = df["order_purchase_timestamp"]
    df["purchase_date"] = purchase.dt.normalize()
    df["purchase_year"] = purchase.dt.year
    df["purchase_month"] = purchase.dt.month
    df["purchase_year_month"] = purchase.dt.to_period("M").astype(str)


def main() -> None:
    orders = load_orders()
    orders = transform_orders(orders)

    print("TIPOS:")
    print(orders.dtypes)

    print("\nEXEMPLO:")
    print(
        orders[
            [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
                "delivery_days",
                "estimated_delivery_days",
                "delay_days",
                "is_delayed",
            ]
        ].head()
    )

    print("\nRESUMO DE ATRASOS:")
    print(orders["is_delayed"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
