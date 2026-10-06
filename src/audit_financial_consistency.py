from pathlib import Path

import pandas as pd

from build_orders_analytics import build_orders_analytics


def main() -> None:
    df = build_orders_analytics()

    print("=" * 80)
    print("1. PEDIDOS SEM PAGAMENTO")
    print("=" * 80)

    no_payment = df[
        df["has_payment"] == False
    ]

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

    print("\n" + "=" * 80)
    print("2. MAIORES DIFERENÇAS FINANCEIRAS")
    print("=" * 80)

    differences = (
        df[
            df["payment_items_difference"].notna()
        ]
        .assign(
            absolute_difference=lambda x:
                x["payment_items_difference"].abs()
        )
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

    print("\n" + "=" * 80)
    print("3. QUANTIDADE DE PEDIDOS COM DIFERENÇA")
    print("=" * 80)

    tolerance = 0.01

    inconsistent = df[
        df["payment_items_difference"].abs()
        > tolerance
    ]

    print(
        f"Pedidos com diferença > R$ {tolerance:.2f}: "
        f"{len(inconsistent):,}"
    )

    print("\nPOR STATUS:")

    print(
        inconsistent[
            "order_status"
        ].value_counts()
    )

    print("\n" + "=" * 80)
    print("4. DIFERENÇAS EM PEDIDOS ENTREGUES")
    print("=" * 80)

    delivered_inconsistent = inconsistent[
        inconsistent["order_status"]
        == "delivered"
    ]

    print(
        f"Pedidos entregues com diferença: "
        f"{len(delivered_inconsistent):,}"
    )

    print("\n" + "=" * 80)
    print("5. DIFERENÇAS E VOUCHERS")
    print("=" * 80)

    print(
        pd.crosstab(
            inconsistent["has_voucher"],
            inconsistent["order_status"],
        )
    )


if __name__ == "__main__":
    main()
