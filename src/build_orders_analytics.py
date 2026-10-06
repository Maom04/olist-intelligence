from pathlib import Path

import pandas as pd

from transform_orders import (
    load_orders,
    transform_orders,
)

from transform_order_items import (
    load_order_items,
    transform_order_items,
    aggregate_order_items,
)

from transform_payments import (
    load_payments,
    transform_payments,
    aggregate_payments,
)

from transform_reviews import (
    load_reviews,
    transform_reviews,
    aggregate_reviews,
)


RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")


def load_customers() -> pd.DataFrame:
    """
    Carrega a tabela original de clientes.
    """
    return pd.read_csv(
        RAW_PATH / "olist_customers_dataset.csv"
    )


def build_orders_analytics() -> pd.DataFrame:
    """
    Constrói a tabela analítica principal.

    Granularidade:
        1 linha = 1 pedido
    """

    # ============================================================
    # ORDERS
    # ============================================================

    orders = load_orders()
    orders = transform_orders(orders)

    original_order_count = len(orders)

    # ============================================================
    # CUSTOMERS
    # ============================================================

    customers = load_customers()

    # ============================================================
    # ORDER ITEMS
    # ============================================================

    items = load_order_items()
    items = transform_order_items(items)

    items_agg = aggregate_order_items(items)

    # ============================================================
    # PAYMENTS
    # ============================================================

    payments = load_payments()
    payments = transform_payments(payments)

    payments_agg = aggregate_payments(payments)

    # ============================================================
    # REVIEWS
    # ============================================================

    reviews = load_reviews()
    reviews = transform_reviews(reviews)

    reviews_agg = aggregate_reviews(reviews)

    # ============================================================
    # ORDERS + CUSTOMERS
    # ============================================================

    df = orders.merge(
        customers,
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    # ============================================================
    # + ORDER ITEMS
    # ============================================================

    df = df.merge(
        items_agg,
        on="order_id",
        how="left",
        validate="one_to_one",
    )

    # ============================================================
    # + PAYMENTS
    # ============================================================

    df = df.merge(
        payments_agg,
        on="order_id",
        how="left",
        validate="one_to_one",
    )

    # ============================================================
    # + REVIEWS
    # ============================================================

    df = df.merge(
        reviews_agg,
        on="order_id",
        how="left",
        validate="one_to_one",
    )

    # ============================================================
    # VALIDAÇÃO DA GRANULARIDADE
    # ============================================================

    if len(df) != original_order_count:
        raise ValueError(
            "Erro de granularidade: "
            f"orders tinha {original_order_count:,} linhas "
            f"e o resultado possui {len(df):,}."
        )

    if not df["order_id"].is_unique:
        raise ValueError(
            "Erro: order_id deixou de ser único "
            "após os merges."
        )

    # ============================================================
    # FLAGS DE DISPONIBILIDADE
    # ============================================================

    df["has_items"] = df["items_count"].notna()

    df["has_payment"] = df["total_paid"].notna()

    df["has_review"] = (
        df["latest_review_score"].notna()
    )

    # ============================================================
    # CAMPOS TEMPORAIS
    # ============================================================

    df["purchase_date"] = (
        df["order_purchase_timestamp"]
        .dt.normalize()
    )

    df["purchase_year"] = (
        df["order_purchase_timestamp"]
        .dt.year
    )

    df["purchase_month"] = (
        df["order_purchase_timestamp"]
        .dt.month
    )

    df["purchase_year_month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    # ============================================================
    # COMPORTAMENTO DO CLIENTE
    # ============================================================

    df = df.sort_values(
        by=[
            "customer_unique_id",
            "order_purchase_timestamp",
            "order_id",
        ]
    )

    # Número do pedido daquele cliente
    # em ordem cronológica
    df["customer_order_number"] = (
        df.groupby("customer_unique_id")
        .cumcount()
        + 1
    )

    # Quantidade total de pedidos
    # associados ao mesmo cliente único
    df["customer_total_orders"] = (
        df.groupby("customer_unique_id")[
            "order_id"
        ]
        .transform("count")
    )

    # Cliente fez mais de um pedido
    df["is_repeat_customer"] = (
        df["customer_total_orders"] > 1
    )

    # Esta linha representa uma compra
    # posterior à primeira
    df["is_repeat_purchase"] = (
        df["customer_order_number"] > 1
    )

    # ============================================================
    # CONSISTÊNCIA FINANCEIRA
    # ============================================================

    # Comparação:
    #
    # total_paid
    #     vs.
    # products_value + freight_value
    #
    # Não usamos isso para alterar os dados.
    # Apenas identificamos possíveis divergências.

    df["payment_items_difference"] = (
        df["total_paid"]
        - df["order_items_total"]
    ).round(2)

    # Booleano anulável:
    #
    # True  = existe divergência > R$ 0,01
    # False = valores conciliam
    # <NA>  = comparação não pode ser realizada
    df["has_financial_mismatch"] = pd.Series(
        pd.NA,
        index=df.index,
        dtype="boolean",
    )

    financial_mask = (
        df["total_paid"].notna()
        & df["order_items_total"].notna()
    )

    df.loc[
        financial_mask,
        "has_financial_mismatch",
    ] = (
        df.loc[
            financial_mask,
            "payment_items_difference",
        ].abs()
        > 0.01
    )

    # ============================================================
    # AJUSTE DE TIPOS
    # ============================================================

    integer_columns = [
        "items_count",
        "products_count",
        "sellers_count",
        "payment_records",
        "payment_types_count",
        "max_installments",
        "reviews_count",
        "comments_count",
        "latest_review_score",
        "customer_order_number",
        "customer_total_orders",
        "purchase_year",
        "purchase_month",
    ]

    for column in integer_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("Int64")
            )

    boolean_columns = [
        "has_items",
        "has_payment",
        "has_review",
        "is_repeat_customer",
        "is_repeat_purchase",
    ]

    for column in boolean_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("boolean")
            )

    # ============================================================
    # ORDENAÇÃO FINAL
    # ============================================================

    df = (
        df.sort_values(
            "order_purchase_timestamp"
        )
        .reset_index(drop=True)
    )

    return df


def save_orders_analytics(
    df: pd.DataFrame,
) -> None:
    """
    Salva a tabela analítica em CSV e Parquet.
    """

    PROCESSED_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        PROCESSED_PATH
        / "orders_analytics.csv"
    )

    parquet_path = (
        PROCESSED_PATH
        / "orders_analytics.parquet"
    )

    df.to_csv(
        csv_path,
        index=False,
    )

    df.to_parquet(
        parquet_path,
        index=False,
    )

    print(
        f"\nCSV salvo em: {csv_path}"
    )

    print(
        f"Parquet salvo em: {parquet_path}"
    )


def main() -> None:
    df = build_orders_analytics()

    print("=" * 80)
    print("ORDERS ANALYTICS")
    print("=" * 80)

    print(
        f"Linhas: {len(df):,}"
    )

    print(
        f"Pedidos únicos: "
        f"{df['order_id'].nunique():,}"
    )

    print(
        f"Colunas: {df.shape[1]}"
    )

    print(
        f"Clientes únicos: "
        f"{df['customer_unique_id'].nunique():,}"
    )

    # ============================================================
    # STATUS
    # ============================================================

    print("\nSTATUS DOS PEDIDOS:")

    print(
        df["order_status"]
        .value_counts()
    )

    # ============================================================
    # DISPONIBILIDADE
    # ============================================================

    print("\nDISPONIBILIDADE DOS DADOS:")

    print(
        "Com itens:",
        int(df["has_items"].sum()),
    )

    print(
        "Com pagamento:",
        int(df["has_payment"].sum()),
    )

    print(
        "Com review:",
        int(df["has_review"].sum()),
    )

    # ============================================================
    # CLIENTES RECORRENTES
    # ============================================================

    recurring_customers = (
        df.loc[
            df["is_repeat_customer"],
            "customer_unique_id",
        ]
        .nunique()
    )

    print("\nCLIENTES RECORRENTES:")

    print(
        f"{recurring_customers:,}"
    )

    # ============================================================
    # CONSISTÊNCIA FINANCEIRA
    # ============================================================

    print(
        "\nDIFERENÇA PAGAMENTO VS ITENS:"
    )

    print(
        df["payment_items_difference"]
        .describe()
    )

    financial_mismatch_count = (
        df["has_financial_mismatch"]
        .fillna(False)
        .sum()
    )

    financial_comparable_count = (
        df["has_financial_mismatch"]
        .notna()
        .sum()
    )

    print(
        "\nPEDIDOS COM DIVERGÊNCIA FINANCEIRA:"
    )

    print(
        f"{financial_mismatch_count:,}"
    )

    print(
        "\nPEDIDOS COMPARÁVEIS FINANCEIRAMENTE:"
    )

    print(
        f"{financial_comparable_count:,}"
    )

    if financial_comparable_count > 0:
        mismatch_rate = (
            financial_mismatch_count
            / financial_comparable_count
            * 100
        )

        print(
            "\nTAXA DE DIVERGÊNCIA:"
        )

        print(
            f"{mismatch_rate:.2f}%"
        )

    # ============================================================
    # EXEMPLO
    # ============================================================

    print("\nEXEMPLO:")

    example_columns = [
        "order_id",
        "customer_unique_id",
        "order_status",
        "products_value",
        "freight_value",
        "order_items_total",
        "total_paid",
        "payment_items_difference",
        "has_financial_mismatch",
        "latest_review_score",
        "delivery_days",
        "is_delayed",
    ]

    print(
        df[
            example_columns
        ].head()
    )

    # ============================================================
    # SALVAMENTO
    # ============================================================

    save_orders_analytics(df)


if __name__ == "__main__":
    main()
