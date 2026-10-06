from pathlib import Path
import json
import re
import unicodedata

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.decomposition import NMF
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "ai"

STOPWORDS_PT = {
    "a",
    "ao",
    "aos",
    "aquela",
    "aquele",
    "aqueles",
    "as",
    "até",
    "com",
    "como",
    "da",
    "das",
    "de",
    "dela",
    "dele",
    "deles",
    "depois",
    "do",
    "dos",
    "e",
    "ela",
    "elas",
    "ele",
    "eles",
    "em",
    "entre",
    "era",
    "essa",
    "esse",
    "esta",
    "este",
    "eu",
    "foi",
    "foram",
    "isso",
    "isto",
    "já",
    "mais",
    "mas",
    "me",
    "mesmo",
    "meu",
    "minha",
    "muito",
    "na",
    "nas",
    "não",
    "no",
    "nos",
    "nossa",
    "nosso",
    "num",
    "numa",
    "o",
    "os",
    "ou",
    "para",
    "pela",
    "pelas",
    "pelo",
    "pelos",
    "por",
    "porque",
    "pra",
    "que",
    "se",
    "sem",
    "seu",
    "sua",
    "são",
    "também",
    "tem",
    "tenho",
    "tinha",
    "um",
    "uma",
    "você",
    "vocês",
    "produto",
    "pedido",
}


def normalize_text(text: str) -> str:
    text = str(text).lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sentiment_from_score(score: int) -> str:
    if score <= 2:
        return "Negativo"
    if score == 3:
        return "Neutro"
    return "Positivo"


def label_topic(top_terms: list[str]) -> str:
    joined = " ".join(top_terms)
    rules = [
        (
            "Atraso / entrega",
            [
                "entrega",
                "atraso",
                "prazo",
                "chegou",
                "chegar",
                "correio",
                "transportadora",
                "receber",
            ],
        ),
        (
            "Produto com problema",
            [
                "defeito",
                "quebrado",
                "danificado",
                "qualidade",
                "funciona",
                "estragado",
                "diferente",
            ],
        ),
        (
            "Item faltante / pedido incompleto",
            ["faltou", "faltando", "recebi", "veio", "apenas", "parte", "incompleto"],
        ),
        (
            "Atendimento / vendedor",
            ["atendimento", "vendedor", "loja", "resposta", "contato", "cliente"],
        ),
        (
            "Embalagem / avaria",
            ["embalagem", "caixa", "embalado", "amassado", "avariado"],
        ),
        (
            "Cancelamento / reembolso",
            ["cancelado", "cancelar", "reembolso", "estorno", "devolucao", "devolver"],
        ),
    ]
    scores = []
    for label, kws in rules:
        scores.append((sum(kw in joined for kw in kws), label))
    scores.sort(reverse=True)
    return scores[0][1] if scores[0][0] > 0 else "Outros problemas"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reviews = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")
    comments = reviews[reviews["review_comment_message"].fillna("").str.strip().ne("")][
        ["review_id", "order_id", "review_score", "review_comment_message"]
    ].copy()

    comments["comment_clean"] = comments["review_comment_message"].map(normalize_text)
    comments = comments[comments["comment_clean"].str.len() >= 3].copy()
    comments["sentiment_label"] = (
        comments["review_score"].astype(int).map(sentiment_from_score)
    )

    print(f"Comentários utilizados: {len(comments):,}")
    print("\nDistribuição original:")
    print(comments["sentiment_label"].value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        comments["comment_clean"],
        comments["sentiment_label"],
        test_size=0.20,
        random_state=42,
        stratify=comments["sentiment_label"],
    )

    sentiment_vectorizer = TfidfVectorizer(
        max_features=30000,
        min_df=2,
        max_df=0.98,
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words=list(STOPWORDS_PT),
    )

    Xtr = sentiment_vectorizer.fit_transform(X_train)
    Xte = sentiment_vectorizer.transform(X_test)

    clf = SGDClassifier(
        loss="log_loss",
        class_weight="balanced",
        max_iter=1500,
        tol=1e-4,
        random_state=42,
    )
    clf.fit(Xtr, y_train)

    pred = clf.predict(Xte)
    accuracy = float(accuracy_score(y_test, pred))
    macro_f1 = float(f1_score(y_test, pred, average="macro"))

    print(f"\nAcurácia: {accuracy:.3f}")
    print(f"Macro F1: {macro_f1:.3f}")
    print("\nRelatório:")
    print(classification_report(y_test, pred))

    Xall = sentiment_vectorizer.transform(comments["comment_clean"])
    comments["ai_sentiment"] = clf.predict(Xall)
    proba = clf.predict_proba(Xall)
    comments["ai_sentiment_confidence"] = proba.max(axis=1).round(4)

    # Topic modeling focado em experiências negativas/neutras.
    problem_mask = comments["sentiment_label"].isin(["Negativo", "Neutro"])
    problem_docs = comments.loc[problem_mask, "comment_clean"]

    topic_vectorizer = TfidfVectorizer(
        max_features=7000,
        min_df=4,
        max_df=0.95,
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words=list(STOPWORDS_PT),
    )
    Xtopic = topic_vectorizer.fit_transform(problem_docs)

    n_topics = 6
    nmf = NMF(
        n_components=n_topics,
        init="nndsvda",
        random_state=42,
        max_iter=400,
    )
    W = nmf.fit_transform(Xtopic)
    feature_names = np.array(topic_vectorizer.get_feature_names_out())

    topic_rows = []
    topic_labels = {}
    for topic_id, component in enumerate(nmf.components_):
        top_idx = component.argsort()[-12:][::-1]
        terms = feature_names[top_idx].tolist()
        label = label_topic(terms)
        topic_labels[topic_id] = label
        topic_rows.append(
            {
                "topic_id": topic_id,
                "topic_label": label,
                "top_terms": ", ".join(terms),
            }
        )

    comments["ai_topic_id"] = pd.Series(pd.NA, index=comments.index, dtype="Int64")
    comments["ai_topic"] = "Experiência positiva"
    comments.loc[problem_mask, "ai_topic_id"] = W.argmax(axis=1)
    comments.loc[problem_mask, "ai_topic"] = (
        comments.loc[problem_mask, "ai_topic_id"].astype(int).map(topic_labels)
    )

    # Mantém uma linha por review; depois o Power BI pode relacionar por order_id.
    export_cols = [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_message",
        "sentiment_label",
        "ai_sentiment",
        "ai_sentiment_confidence",
        "ai_topic_id",
        "ai_topic",
    ]
    comments[export_cols].to_csv(
        OUT / "review_ai_analytics.csv",
        index=False,
        encoding="utf-8-sig",
    )

    sentiment_summary = (
        comments.groupby("ai_sentiment", as_index=False)
        .agg(
            reviews=("review_id", "count"),
            avg_score=("review_score", "mean"),
            avg_confidence=("ai_sentiment_confidence", "mean"),
        )
        .sort_values("reviews", ascending=False)
    )
    sentiment_summary["share"] = (
        sentiment_summary["reviews"] / sentiment_summary["reviews"].sum()
    )
    sentiment_summary.to_csv(OUT / "sentiment_summary.csv", index=False)

    topic_summary = (
        comments.groupby("ai_topic", as_index=False)
        .agg(
            reviews=("review_id", "count"),
            avg_score=("review_score", "mean"),
            avg_confidence=("ai_sentiment_confidence", "mean"),
        )
        .sort_values("reviews", ascending=False)
    )
    topic_summary["share"] = topic_summary["reviews"] / topic_summary["reviews"].sum()
    topic_summary.to_csv(OUT / "topic_summary.csv", index=False)

    pd.DataFrame(topic_rows).to_csv(OUT / "topic_terms.csv", index=False)

    metrics = {
        "comments_used": int(len(comments)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "classes": list(clf.classes_),
        "model": "TF-IDF + SGDClassifier(log_loss)",
        "topic_model": f"TF-IDF + NMF ({n_topics} topics)",
    }
    (OUT / "ai_model_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nTópicos descobertos:")
    print(pd.DataFrame(topic_rows).to_string(index=False))

    print("\nResumo IA - sentimento:")
    print(sentiment_summary.to_string(index=False))

    print("\nResumo IA - tópicos:")
    print(topic_summary.to_string(index=False))

    print(f"\nArquivos salvos em: {OUT}")


if __name__ == "__main__":
    main()
