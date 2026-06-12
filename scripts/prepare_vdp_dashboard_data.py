from __future__ import annotations

import argparse
import csv
from pathlib import Path


MONTH_NAMES = {
    "01": "Janeiro",
    "02": "Fevereiro",
    "03": "Marco",
    "04": "Abril",
    "05": "Maio",
    "06": "Junho",
    "07": "Julho",
    "08": "Agosto",
    "09": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro",
}

DEPUTY_NAME_FIXES = {
    "DEP ALCIDERS FERNANDES": "DEP ALCIDES FERNANDES",
    "DEP ALMIIR BIE": "DEP ALMIR BIE",
    "DEP ALMIR B": "DEP ALMIR BIE",
    "DEP ALYSSON AGUYIAR": "DEP ALYSSON AGUIAR",
    "DEP EMIILA PESSOA": "DEP EMILIA PESSOA",
    "DEP EMILA PESSOA": "DEP EMILIA PESSOA",
    "DEP FIRMO CAMUCA": "DEP FIRMO CAMURCA",
    "DEP GUILHERME BISMARK": "DEP GUILHERME BISMARCK",
    "DEP MISSISAS DIAS": "DEP MISSIAS DIAS",
    "DEP SERGIO AHUIAR": "DEP SERGIO AGUIAR",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ANO",
        "MES",
        "MES_NOME",
        "DATA_MES",
        "PERIODO",
        "DEPUTADO",
        "DEPUTADO_ORIGINAL",
        "EMPENHO",
        "DESCRICAO",
        "CNPJ",
        "CREDOR",
        "VALOR",
        "VALOR_NUM",
        "CODIGO",
        "URL_DETALHE",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="dados/processed/vdp_2025_por_deputado.csv")
    parser.add_argument("--output", default="dados/processed/vdp_2025_dashboard.csv")
    args = parser.parse_args()

    rows = []
    for row in read_rows(Path(args.input)):
        month = row["MES"].zfill(2)
        original_deputy = row["DEPUTADO"].strip()
        row["DEPUTADO_ORIGINAL"] = original_deputy
        row["DEPUTADO"] = DEPUTY_NAME_FIXES.get(original_deputy, original_deputy)
        row["MES"] = month
        row["MES_NOME"] = MONTH_NAMES.get(month, month)
        row["DATA_MES"] = f'{row["ANO"]}-{month}-01'
        rows.append(row)

    rows.sort(key=lambda item: (item["ANO"], item["MES"], item["DEPUTADO"], item["CREDOR"], item["EMPENHO"]))
    write_rows(Path(args.output), rows)
    print(f"Base de dashboard: {args.output} ({len(rows)} linhas)")
    print(f"Nomes corrigidos: {len(DEPUTY_NAME_FIXES)}")


if __name__ == "__main__":
    main()
