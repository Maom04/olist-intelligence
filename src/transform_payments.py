from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw")


def load_payments() -> pd.DataFrame:
    return pd.read_csv(
        RAW_PATH / "olist_order_payments_dataset.csv"
    )


def transform_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Padronização textual
    df["payment_type"] = (
        df["payment_type"]
        .str.strip()
        .str.lower()
    )

    # Flag de pagamento com valor zero
    df["is_zero_value_payment"] = (
        df["payment_value"] == 0
    )

    # Parcelamento igual a zero não faz sentido
    # para cartão de crédito.
    df["has_invalid_installments"] = (
        (df["payment_type"] == "credit_card")
        & (df["payment_installments"] == 0)
    )

    # Criamos uma versão analítica sem alterar
    # a coluna original.
    df["installments_clean"] = (
        df["payment_installments"]
        .astype("Int64")
    )

    df.loc[
        df["has_invalid_installments"],
        "installments_clean",
    ] = pd.NA

    return df


def aggregate_payments(df: pd.DataFrame) -> pd.DataFrame:

    payments_agg = (
        df.groupby("order_id")
        .agg(
            payment_records=(
                "payment_sequential",
                "count",
            ),
            payment_types_count=(
                "payment_type",
                "nunique",
            ),
            max_installments=(
                "installments_clean",
                "max",
            ),
            total_paid=(
                "payment_value",
                "sum",
            ),
            has_zero_value_payment=(
                "is_zero_value_payment",
                "any",
            ),
            has_invalid_installments=(
                "has_invalid_installments",
                "any",
            ),
        )
        .reset_index()
    )

    # Principal forma de pagamento:
    # registro de maior valor dentro do pedido.
    primary_payment = (
        df.sort_values(
            by=[
                "order_id",
                "payment_value",
                "payment_sequential",
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )
        .drop_duplicates(
            subset="order_id",
            keep="first",
        )
        [
            [
                "order_id",
                "payment_type",
            ]
        ]
        .rename(
            columns={
                "payment_type":
                "primary_payment_type"
            }
        )
    )

    payments_agg = payments_agg.merge(
        primary_payment,
        on="order_id",
        how="left",
        validate="one_to_one",
    )

    # Identifica utilização de voucher
    voucher_usage = (
        df.assign(
            has_voucher=(
                df["payment_type"] == "voucher"
            )
        )
        .groupby("order_id")["has_voucher"]
        .any()
        .reset_index()
    )

    payments_agg = payments_agg.merge(
        voucher_usage,
        on="order_id",
        how="left",
        validate="one_to_one",
    )

    return payments_agg


def main() -> None:

    payments = load_payments()

    payments = transform_payments(
        payments
    )

    payments_agg = aggregate_payments(
        payments
    )

    print("RESULTADO:")
    print(
        f"Registros originais: "
        f"{len(payments):,}"
    )

    print(
        f"Pedidos agregados: "
        f"{len(payments_agg):,}"
    )

    print("\nTIPOS:")
    print(payments_agg.dtypes)

    print("\nEXEMPLO:")
    print(payments_agg.head())

    print(
        "\nPEDIDOS COM VALOR ZERO "
        "EM ALGUM PAGAMENTO:"
    )

    print(
        payments_agg[
            "has_zero_value_payment"
        ].sum()
    )

    print(
        "\nPEDIDOS COM PROBLEMA "
        "DE PARCELAMENTO:"
    )

    print(
        payments_agg[
            "has_invalid_installments"
        ].sum()
    )

    print(
        "\nFORMAS PRINCIPAIS "
        "DE PAGAMENTO:"
    )

    print(
        payments_agg[
            "primary_payment_type"
        ].value_counts()
    )


if __name__ == "__main__":
    main()
