import pandas as pd

from build_orders_analytics import (
    build_orders_analytics,
    save_orders_analytics,
)

from build_items_analytics import (
    build_items_analytics,
    save_items_analytics,
)


def validate_pipeline(
    orders: pd.DataFrame,
    items: pd.DataFrame,
) -> None:
    """
    Executa validações finais de integridade
    entre as tabelas analíticas.
    """

    print("\n" + "=" * 80)
    print("VALIDAÇÃO FINAL")
    print("=" * 80)

    # ------------------------------------------------------------
    # ORDERS
    # ------------------------------------------------------------

    if not orders["order_id"].is_unique:
        raise ValueError(
            "orders_analytics possui order_id duplicado."
        )

    print(
        f"[OK] orders_analytics: "
        f"{len(orders):,} pedidos únicos."
    )

    # ------------------------------------------------------------
    # ITEMS
    # ------------------------------------------------------------

    duplicated_items = (
        items.duplicated(
            subset=[
                "order_id",
                "order_item_id",
            ]
        )
        .sum()
    )

    if duplicated_items > 0:
        raise ValueError(
            f"items_analytics possui "
            f"{duplicated_items:,} itens duplicados."
        )

    print(
        f"[OK] items_analytics: "
        f"{len(items):,} itens únicos."
    )

    # ------------------------------------------------------------
    # INTEGRIDADE ITEM → ORDER
    # ------------------------------------------------------------

    item_orders = set(
        items["order_id"].unique()
    )

    order_ids = set(
        orders["order_id"].unique()
    )

    orphan_item_orders = (
        item_orders - order_ids
    )

    if orphan_item_orders:
        raise ValueError(
            f"Existem "
            f"{len(orphan_item_orders):,} "
            "pedidos em items_analytics "
            "sem correspondente em orders_analytics."
        )

    print(
        "[OK] Todos os itens possuem "
        "pedido correspondente."
    )

    # ------------------------------------------------------------
    # CONSISTÊNCIA DE VALOR DOS PRODUTOS
    # ------------------------------------------------------------

    items_by_order = (
        items.groupby("order_id")
        .agg(
            items_products_value=(
                "price",
                "sum",
            ),
            items_freight_value=(
                "freight_value",
                "sum",
            ),
        )
        .reset_index()
    )

    comparison = orders[
        [
            "order_id",
            "products_value",
            "freight_value",
        ]
    ].merge(
        items_by_order,
        on="order_id",
        how="inner",
        validate="one_to_one",
    )

    comparison[
        "products_difference"
    ] = (
        comparison["products_value"]
        - comparison["items_products_value"]
    ).abs()

    comparison[
        "freight_difference"
    ] = (
        comparison["freight_value"]
        - comparison["items_freight_value"]
    ).abs()

    product_mismatches = (
        comparison[
            "products_difference"
        ] > 0.01
    ).sum()

    freight_mismatches = (
        comparison[
            "freight_difference"
        ] > 0.01
    ).sum()

    if product_mismatches > 0:
        raise ValueError(
            f"Existem "
            f"{product_mismatches:,} "
            "divergências de valor de produtos."
        )

    if freight_mismatches > 0:
        raise ValueError(
            f"Existem "
            f"{freight_mismatches:,} "
            "divergências de frete."
        )

    print(
        "[OK] Valores de produtos conciliam "
        "entre orders e items."
    )

    print(
        "[OK] Valores de frete conciliam "
        "entre orders e items."
    )

    # ------------------------------------------------------------
    # RESUMO
    # ------------------------------------------------------------

    print("\n" + "-" * 80)

    print(
        f"Pedidos: "
        f"{len(orders):,}"
    )

    print(
        f"Itens: "
        f"{len(items):,}"
    )

    print(
        f"Clientes únicos: "
        f"{orders['customer_unique_id'].nunique():,}"
    )

    print(
        f"Produtos únicos: "
        f"{items['product_id'].nunique():,}"
    )

    print(
        f"Vendedores únicos: "
        f"{items['seller_id'].nunique():,}"
    )

    print(
        f"Pedidos com itens: "
        f"{orders['has_items'].sum():,}"
    )

    print(
        f"Pedidos com pagamento: "
        f"{orders['has_payment'].sum():,}"
    )

    print(
        f"Pedidos com review: "
        f"{orders['has_review'].sum():,}"
    )

    financial_mismatches = (
        orders[
            "has_financial_mismatch"
        ]
        .fillna(False)
        .sum()
    )

    print(
        f"Divergências financeiras: "
        f"{financial_mismatches:,}"
    )

    print("\nPIPELINE VALIDADO COM SUCESSO.")


def main() -> None:
    print("=" * 80)
    print("OLIST INTELLIGENCE")
    print("PIPELINE DE DADOS")
    print("=" * 80)

    # ============================================================
    # ORDERS
    # ============================================================

    print(
        "\n[1/4] Construindo orders_analytics..."
    )

    orders = build_orders_analytics()

    print(
        f"      {len(orders):,} registros processados."
    )

    # ============================================================
    # ITEMS
    # ============================================================

    print(
        "\n[2/4] Construindo items_analytics..."
    )

    items = build_items_analytics()

    print(
        f"      {len(items):,} registros processados."
    )

    # ============================================================
    # VALIDAÇÃO
    # ============================================================

    print(
        "\n[3/4] Validando integridade..."
    )

    validate_pipeline(
        orders,
        items,
    )

    # ============================================================
    # SALVAMENTO
    # ============================================================

    print(
        "\n[4/4] Salvando datasets..."
    )

    save_orders_analytics(
        orders
    )

    save_items_analytics(
        items
    )

    print("\n" + "=" * 80)
    print("PIPELINE CONCLUÍDO")
    print("=" * 80)

    print(
        "\nArquivos disponíveis em:"
    )

    print(
        "data/processed/orders_analytics.csv"
    )

    print(
        "data/processed/orders_analytics.parquet"
    )

    print(
        "data/processed/items_analytics.csv"
    )

    print(
        "data/processed/items_analytics.parquet"
    )


if __name__ == "__main__":
    main()
