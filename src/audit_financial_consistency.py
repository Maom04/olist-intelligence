import pandas as pd

from build_orders_analytics import build_orders_analytics


def main() -> None:
    df = build_orders_analytics()

    print("1. PEDIDOS SEM PAGAMENTO")

    no_payment = df[~df["has_payment"]]

    print(
        no_payment[
            [
                "order_id",
                "order_status",
                "products_value",
                "freight_value",
                "order_items_total",
                "total_paid",
            ]
        ].to_string(index=False)
    )

    print("2. MAIORES DIFERENÇAS FINANCEIRAS")

    differences = (
        df[df["payment_items_difference"].notna()]
        .assign(absolute_difference=lambda x: x["payment_items_difference"].abs())
        .sort_values(
            "absolute_difference",
            ascending=False,
        )
    )

    print(
        differences[
            [
                "order_id",
                "order_status",
                "products_value",
                "freight_value",
                "order_items_total",
                "total_paid",
                "payment_items_difference",
                "primary_payment_type",
                "has_voucher",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    print("3. QUANTIDADE DE PEDIDOS COM DIFERENÇA")

    tolerance = 0.01

    inconsistent = df[df["payment_items_difference"].abs() > tolerance]

    print(f"Pedidos com diferença > R$ {tolerance:.2f}: {len(inconsistent):,}")

    print("\nPOR STATUS:")

    print(inconsistent["order_status"].value_counts())

    print("4. DIFERENÇAS EM PEDIDOS ENTREGUES")

    delivered_inconsistent = inconsistent[inconsistent["order_status"] == "delivered"]

    print(f"Pedidos entregues com diferença: {len(delivered_inconsistent):,}")

    print("5. DIFERENÇAS E VOUCHERS")

    print(
        pd.crosstab(
            inconsistent["has_voucher"],
            inconsistent["order_status"],
        )
    )


if __name__ == "__main__":
    main()
