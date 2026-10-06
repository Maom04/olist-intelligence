from main import main as run_data_pipeline
from ai_review_intelligence import main as run_ai_pipeline


def main() -> None:
    print("Pipeline analítico")
    run_data_pipeline()

    print("\nAnálise de reviews")
    run_ai_pipeline()


if __name__ == "__main__":
    main()
