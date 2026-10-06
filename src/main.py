import pandas as pd

from build_items_analytics import build_items_analytics, save_items_analytics
from build_orders_analytics import build_orders_analytics, save_orders_analytics


def validate_pipeline(orders: pd.DataFrame, items: pd.DataFrame) -> None:
    if not orders["order_id"].is_unique:
        raise ValueError("orders_analytics possui order_id duplicado.")

    duplicate_items = items.duplicated(["order_id", "order_item_id"]).sum()
    if duplicate_items:
        raise ValueError(
            f"items_analytics possui {duplicate_items:,} itens duplicados."
        )

    orphan_orders = set(items["order_id"]) - set(orders["order_id"])
    if orphan_orders:
        raise ValueError(
            f"Existem {len(orphan_orders):,} pedidos em items_analytics "
            "sem correspondente em orders_analytics."
        )

    totals = (
        items.groupby("order_id")
        .agg(
            items_products_value=("price", "sum"),
            items_freight_value=("freight_value", "sum"),
        )
        .reset_index()
    )
    comparison = orders[["order_id", "products_value", "freight_value"]].merge(
        totals, on="order_id", how="inner", validate="one_to_one"
    )

    product_mismatches = (
        (comparison["products_value"] - comparison["items_products_value"]).abs() > 0.01
    ).sum()
    freight_mismatches = (
        (comparison["freight_value"] - comparison["items_freight_value"]).abs() > 0.01
    ).sum()

    if product_mismatches:
        raise ValueError(f"Existem {product_mismatches:,} divergências de produtos.")
    if freight_mismatches:
        raise ValueError(f"Existem {freight_mismatches:,} divergências de frete.")

    print(
        f"Validação concluída: {len(orders):,} pedidos, {len(items):,} itens, "
        "sem chaves órfãs ou divergências entre produtos e frete."
    )


def main() -> None:
    print("Construindo tabelas analíticas...")
    orders = build_orders_analytics()
    items = build_items_analytics()
    validate_pipeline(orders, items)

    save_orders_analytics(orders)
    save_items_analytics(items)

    print(
        f"Concluído: {orders['customer_unique_id'].nunique():,} clientes, "
        f"{items['product_id'].nunique():,} produtos e "
        f"{items['seller_id'].nunique():,} vendedores."
    )
    print(
        "Pedidos com itens, pagamento e review:",
        f"{orders['has_items'].sum():,},",
        f"{orders['has_payment'].sum():,},",
        f"{orders['has_review'].sum():,}.",
    )
    mismatches = orders["has_financial_mismatch"].fillna(False).sum()
    print(f"Divergências financeiras: {mismatches:,}.")


if __name__ == "__main__":
    main()
