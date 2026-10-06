from pathlib import Path

import pandas as pd


RAW_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw"


def audit_csv(file_path: Path) -> None:
    df = pd.read_csv(file_path)

    print(f"ARQUIVO: {file_path.name}")
    print(f"Linhas: {df.shape[0]:,}")
    print(f"Colunas: {df.shape[1]}")
    print(f"Duplicatas: {df.duplicated().sum():,}")
    print(f"Memória: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    print("\nCOLUNAS E TIPOS:")
    print(df.dtypes)

    print("\nVALORES NULOS:")
    nulls = df.isna().sum()
    print(nulls[nulls > 0])

    print()


def main() -> None:
    csv_files = sorted(RAW_DATA_PATH.glob("*.csv"))

    if not csv_files:
        print("Nenhum arquivo CSV encontrado em data/raw.")
        return

    print(f"{len(csv_files)} arquivos encontrados.\n")

    for file_path in csv_files:
        audit_csv(file_path)


if __name__ == "__main__":
    main()
