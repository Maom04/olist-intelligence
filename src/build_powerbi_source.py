from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
OUT = ROOT / "dashboard" / "powerbi_source.xlsx"


def main() -> None:
    orders_cols = [
        "order_id",
        "customer_unique_id",
        "purchase_date",
        "order_status",
        "products_value",
        "freight_value",
        "latest_review_score",
        "is_delayed",
        "is_repeat_customer",
        "customer_state",
        "primary_payment_type",
    ]
    items_cols = [
        "order_id",
        "product_category_name_english",
        "price",
        "freight_value",
        "seller_state",
        "customer_state",
        "latest_review_score",
        "is_delayed",
    ]

    orders = pd.read_csv(
        PROC / "orders_analytics.csv", usecols=orders_cols, low_memory=False
    )
    items = pd.read_csv(
        PROC / "items_analytics.csv", usecols=items_cols, low_memory=False
    )

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        orders.to_excel(writer, sheet_name="orders", index=False)
        items.to_excel(writer, sheet_name="items", index=False)

    print(OUT)
    print(len(orders), len(items))


if __name__ == "__main__":
    main()
