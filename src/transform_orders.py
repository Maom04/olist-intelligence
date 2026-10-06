from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw")

DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def load_orders() -> pd.DataFrame:
    return pd.read_csv(
        RAW_PATH / "olist_orders_dataset.csv"
    )


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Converte colunas de data
    for column in DATE_COLUMNS:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Tempo total entre compra e entrega
    df["delivery_days"] = (
        df["order_delivered_customer_date"]
        - df["order_purchase_timestamp"]
    ).dt.days

    # Prazo originalmente estimado
    df["estimated_delivery_days"] = (
        df["order_estimated_delivery_date"]
        - df["order_purchase_timestamp"]
    ).dt.days

    # Normaliza as datas para ignorar horário
    delivered_date = (
        df["order_delivered_customer_date"]
        .dt.normalize()
    )

    estimated_date = (
        df["order_estimated_delivery_date"]
        .dt.normalize()
    )

    # Diferença entre entrega real e prevista
    # negativo = entregue antes
    # zero = entregue no dia
    # positivo = atraso
    df["delay_days"] = (
        delivered_date
        - estimated_date
    ).dt.days

    # Booleano anulável:
    # True  = atrasado
    # False = no prazo ou antecipado
    # <NA>  = pedido sem data de entrega
    df["is_delayed"] = pd.Series(
        pd.NA,
        index=df.index,
        dtype="boolean"
    )

    delivered_mask = (
        delivered_date.notna()
        & estimated_date.notna()
    )

    df.loc[delivered_mask, "is_delayed"] = (
        delivered_date[delivered_mask]
        > estimated_date[delivered_mask]
    )

    return df


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
