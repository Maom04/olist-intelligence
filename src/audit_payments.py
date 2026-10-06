from pathlib import Path

import pandas as pd


RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw"


def main() -> None:
    payments = pd.read_csv(RAW_PATH / "olist_order_payments_dataset.csv")

    orders = pd.read_csv(RAW_PATH / "olist_orders_dataset.csv")

    print("1. PAGAMENTOS NOT_DEFINED")

    not_defined = payments[payments["payment_type"] == "not_defined"]

    print(not_defined)

    print("\nSTATUS DOS PEDIDOS:")
    print(
        not_defined.merge(
            orders[
                [
                    "order_id",
                    "order_status",
                ]
            ],
            on="order_id",
            how="left",
        )
    )

    print("2. PAGAMENTOS COM VALOR ZERO")

    zero_value = payments[payments["payment_value"] == 0]

    print(zero_value)

    print("3. PAGAMENTOS COM 0 PARCELAS")

    zero_installments = payments[payments["payment_installments"] == 0]

    print(zero_installments)

    print("4. PEDIDOS COM MAIS REGISTROS DE PAGAMENTO")

    payment_counts = (
        payments.groupby("order_id").size().sort_values(ascending=False).head(10)
    )

    print(payment_counts)

    print("\nDETALHES DO PEDIDO COM MAIS PAGAMENTOS:")

    top_order_id = payment_counts.index[0]

    print(
        payments[payments["order_id"] == top_order_id].sort_values("payment_sequential")
    )


if __name__ == "__main__":
    main()
