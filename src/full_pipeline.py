import os
from pathlib import Path

from main import main as run_data_pipeline
from ai_review_intelligence import main as run_ai_pipeline


ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    os.chdir(ROOT)

    print("=" * 80)
    print("OLIST INTELLIGENCE - FULL PIPELINE")
    print("=" * 80)

    print("\n[1/2] Pipeline analítico")
    run_data_pipeline()

    print("\n[2/2] Camada de IA / NLP")
    run_ai_pipeline()

    print("\n" + "=" * 80)
    print("PROJETO PROCESSADO COM SUCESSO")
    print("=" * 80)


if __name__ == "__main__":
    main()
