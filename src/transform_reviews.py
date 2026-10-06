from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw")


DATE_COLUMNS = [
    "review_creation_date",
    "review_answer_timestamp",
]


def load_reviews() -> pd.DataFrame:
    return pd.read_csv(
        RAW_PATH / "olist_order_reviews_dataset.csv"
    )


def transform_reviews(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Datas
    for column in DATE_COLUMNS:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    # Presença de título
    df["has_review_title"] = (
        df["review_comment_title"]
        .fillna("")
        .str.strip()
        .ne("")
    )

    # Presença de comentário
    df["has_review_comment"] = (
        df["review_comment_message"]
        .fillna("")
        .str.strip()
        .ne("")
    )

    # Texto limpo para futura análise com IA.
    # Mantemos a coluna original intacta.
    df["review_comment_clean"] = (
        df["review_comment_message"]
        .fillna("")
        .str.strip()
    )

    # Tempo que levou para o cliente/responsável
    # responder à avaliação
    df["review_response_hours"] = (
        df["review_answer_timestamp"]
        - df["review_creation_date"]
    ).dt.total_seconds() / 3600

    return df


def aggregate_reviews(df: pd.DataFrame) -> pd.DataFrame:
    # Métricas gerais por pedido
    reviews_agg = (
        df.groupby("order_id")
        .agg(
            reviews_count=(
                "review_id",
                "count",
            ),
            review_score_mean=(
                "review_score",
                "mean",
            ),
            review_score_min=(
                "review_score",
                "min",
            ),
            review_score_max=(
                "review_score",
                "max",
            ),
            has_review_comment=(
                "has_review_comment",
                "any",
            ),
            comments_count=(
                "has_review_comment",
                "sum",
            ),
        )
        .reset_index()
    )

    # Review mais recente do pedido.
    # Em caso de múltiplas avaliações, usamos
    # review_answer_timestamp como referência.
    latest_review = (
        df.sort_values(
            by=[
                "order_id",
                "review_answer_timestamp",
                "review_creation_date",
            ],
            ascending=[
                True,
                False,
                False,
            ],
            na_position="last",
        )
        .drop_duplicates(
            subset="order_id",
            keep="first",
        )
        [
            [
                "order_id",
                "review_score",
                "review_creation_date",
                "review_answer_timestamp",
                "review_comment_clean",
            ]
        ]
        .rename(
            columns={
                "review_score":
                    "latest_review_score",
                "review_creation_date":
                    "latest_review_creation_date",
                "review_answer_timestamp":
                    "latest_review_answer_timestamp",
                "review_comment_clean":
                    "latest_review_comment",
            }
        )
    )

    reviews_agg = reviews_agg.merge(
        latest_review,
        on="order_id",
        how="left",
        validate="one_to_one",
    )

    return reviews_agg


def main() -> None:
    reviews = load_reviews()

    print("ANTES DA TRANSFORMAÇÃO:")
    print(f"Linhas: {len(reviews):,}")
    print(
        f"Pedidos: "
        f"{reviews['order_id'].nunique():,}"
    )

    reviews = transform_reviews(reviews)

    reviews_agg = aggregate_reviews(reviews)

    print("\nAPÓS AGREGAÇÃO:")
    print(
        f"Linhas: "
        f"{len(reviews_agg):,}"
    )

    print(
        f"Pedidos: "
        f"{reviews_agg['order_id'].nunique():,}"
    )

    print("\nTIPOS:")
    print(reviews_agg.dtypes)

    print("\nEXEMPLO:")
    print(reviews_agg.head())

    print("\nDISTRIBUIÇÃO DA ÚLTIMA NOTA:")
    print(
        reviews_agg[
            "latest_review_score"
        ]
        .value_counts()
        .sort_index()
    )

    print("\nPEDIDOS COM MAIS DE UMA AVALIAÇÃO:")
    print(
        (
            reviews_agg["reviews_count"] > 1
        ).sum()
    )

    print("\nPEDIDOS COM COMENTÁRIO:")
    print(
        reviews_agg[
            "has_review_comment"
        ].sum()
    )

    print("\nTOTAL DE COMENTÁRIOS:")
    print(
        reviews[
            "has_review_comment"
        ].sum()
    )

    print("\nRESUMO DAS NOTAS:")
    print(
        reviews["review_score"]
        .describe()
    )


if __name__ == "__main__":
    main()
