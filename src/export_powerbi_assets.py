from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "dashboard" / "reference"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    orders = pd.read_csv(
        PROCESSED / "orders_analytics.csv",
        parse_dates=["order_purchase_timestamp", "purchase_date"],
        low_memory=False,
    )

    items = pd.read_csv(
        PROCESSED / "items_analytics.csv",
        parse_dates=["order_purchase_timestamp", "purchase_date"],
        low_memory=False,
    )

    delivered_orders = orders[orders["order_status"].eq("delivered")].copy()
    delivered_items = items[items["order_status"].eq("delivered")].copy()

    gmv = delivered_orders["products_value"].sum()
    delivered_count = delivered_orders["order_id"].nunique()
    customers = delivered_orders["customer_unique_id"].nunique()
    ticket = gmv / delivered_count
    review_avg = delivered_orders["latest_review_score"].mean()

    delay_base = delivered_orders["is_delayed"].notna().sum()
    delayed_count = delivered_orders["is_delayed"].astype("string").eq("True").sum()
    delay_rate = delayed_count / delay_base if delay_base else 0

    repeat_customers = delivered_orders.loc[
        delivered_orders["is_repeat_customer"].astype("string").eq("True"),
        "customer_unique_id",
    ].nunique()
    repeat_rate = repeat_customers / customers if customers else 0

    freight_total = delivered_orders["freight_value"].sum()

    kpis = pd.DataFrame(
        [
            ["GMV", gmv, "BRL"],
            ["Pedidos entregues", delivered_count, "count"],
            ["Clientes únicos", customers, "count"],
            ["Ticket médio", ticket, "BRL"],
            ["Avaliação média", review_avg, "score"],
            ["Taxa de atraso", delay_rate, "percent"],
            ["Clientes recorrentes", repeat_customers, "count"],
            ["Taxa clientes recorrentes", repeat_rate, "percent"],
            ["Frete total", freight_total, "BRL"],
        ],
        columns=["metric", "value", "format"],
    )
    kpis.to_csv(OUT / "kpi_reference.csv", index=False)

    monthly = (
        delivered_orders.assign(
            month=delivered_orders["order_purchase_timestamp"]
            .dt.to_period("M")
            .astype(str)
        )
        .groupby("month", as_index=False)
        .agg(
            gmv=("products_value", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_unique_id", "nunique"),
        )
    )
    monthly["ticket_avg"] = monthly["gmv"] / monthly["orders"]
    monthly.to_csv(OUT / "monthly_performance.csv", index=False)

    categories = (
        delivered_items.groupby("product_category_name_english", as_index=False)
        .agg(
            gmv=("price", "sum"),
            items=("order_item_id", "count"),
            orders=("order_id", "nunique"),
            avg_freight=("freight_value", "mean"),
            avg_review=("latest_review_score", "mean"),
        )
        .sort_values("gmv", ascending=False)
    )
    categories.to_csv(OUT / "category_performance.csv", index=False)

    states = (
        delivered_orders.groupby("customer_state", as_index=False)
        .agg(
            gmv=("products_value", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_unique_id", "nunique"),
            avg_review=("latest_review_score", "mean"),
        )
        .sort_values("gmv", ascending=False)
    )
    states["ticket_avg"] = states["gmv"] / states["orders"]
    states.to_csv(OUT / "state_performance.csv", index=False)

    payments = (
        delivered_orders.groupby("primary_payment_type", dropna=False, as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            total_paid=("total_paid", "sum"),
        )
        .sort_values("orders", ascending=False)
    )
    payments.to_csv(OUT / "payment_mix.csv", index=False)

    quality = pd.DataFrame(
        {
            "metric": [
                "Pedidos totais",
                "Pedidos entregues",
                "Pedidos com itens",
                "Pedidos com pagamento",
                "Pedidos com review",
                "Divergências financeiras",
            ],
            "value": [
                len(orders),
                delivered_count,
                int(orders["has_items"].fillna(False).astype(bool).sum()),
                int(orders["has_payment"].fillna(False).astype(bool).sum()),
                int(orders["has_review"].fillna(False).astype(bool).sum()),
                int(orders["has_financial_mismatch"].fillna(False).astype(bool).sum()),
            ],
        }
    )
    quality.to_csv(OUT / "data_quality_reference.csv", index=False)

    print("Power BI reference assets created.")
    print(kpis.to_string(index=False))


if __name__ == "__main__":
    main()
