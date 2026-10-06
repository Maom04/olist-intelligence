from pathlib import Path
import pandas as pd

root=Path(r"C:\Projetos\olist-intelligence")
ai=pd.read_csv(root/"data"/"ai"/"review_ai_analytics.csv", low_memory=False)
sent=pd.read_csv(root/"data"/"ai"/"sentiment_summary.csv")
topics=pd.read_csv(root/"data"/"ai"/"topic_summary.csv")
out=root/"dashboard"/"ai_source.xlsx"

with pd.ExcelWriter(out, engine="openpyxl") as writer:
    ai.to_excel(writer, sheet_name="review_ai", index=False)
    sent.to_excel(writer, sheet_name="sentiment_summary", index=False)
    topics.to_excel(writer, sheet_name="topic_summary", index=False)

print(out)
print(len(ai))
