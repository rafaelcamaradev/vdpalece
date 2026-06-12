from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar"
DETAIL_URL = f"{BASE_URL}/detalhes"
YEAR = "2025"
MONTHS = [f"{month:02d}" for month in range(1, 13)]


@dataclass(frozen=True)
class DeputyEntry:
    month: str
    code: str
    name: str

    @property
    def decoded_code(self) -> str:
        return base64.b64decode(self.code).decode("utf-8")


class ListingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.entries: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "button":
            return
        attrs_dict = dict(attrs)
        code = attrs_dict.get("data-bs-codigo")
        name = attrs_dict.get("data-bs-nome")
        if code and name:
            self.entries.append((code, name.strip()))


class DetailTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._in_cell = False
        self._cell_parts: list[str] = []
        self._current_row: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._in_cell = True
            self._cell_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._in_cell and self._current_row is not None:
            text = " ".join("".join(self._cell_parts).split())
            self._current_row.append(text)
            self._in_cell = False
            self._cell_parts = []
        elif tag == "tr" and self._current_row is not None:
            if any(cell for cell in self._current_row):
                self.rows.append(self._current_row)
            self._current_row = None


def fetch_bytes(url: str, sleep_seconds: float = 0.1) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; VDP dashboard data collector)",
            "Accept": "text/html,application/xhtml+xml,application/xml,text/csv,*/*",
        },
    )
    with urlopen(request, timeout=45) as response:
        data = response.read()
    if sleep_seconds:
        time.sleep(sleep_seconds)
    return data


def parse_listing(html: str, month: str) -> list[DeputyEntry]:
    parser = ListingParser()
    parser.feed(html)

    entries: list[DeputyEntry] = []
    seen: set[str] = set()
    for code, name in parser.entries:
        if code in seen:
            continue
        seen.add(code)
        entries.append(DeputyEntry(month=month, code=code, name=name))
    return entries


def parse_detail_rows(html: str) -> list[dict[str, str]]:
    parser = DetailTableParser()
    parser.feed(html)

    rows: list[dict[str, str]] = []
    for cells in parser.rows:
        if not cells:
            continue
        if cells[0].upper().startswith("EMPENHO"):
            continue
        if cells[0].upper().startswith("TOTAL GERAL"):
            continue
        if len(cells) < 5:
            continue
        rows.append(
            {
                "EMPENHO": cells[0],
                "DESCRICAO": cells[1],
                "CNPJ": cells[2],
                "CREDOR": cells[3],
                "VALOR": cells[4],
            }
        )
    return rows


def parse_brazilian_decimal(value: str) -> str:
    normalized = value.strip().replace(".", "").replace(",", ".")
    try:
        return str(Decimal(normalized))
    except InvalidOperation:
        return ""


def safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
    return value.strip("_") or "sem_nome"


def list_deputies_for_month(month: str, max_pages: int) -> list[DeputyEntry]:
    entries_by_code: dict[str, DeputyEntry] = {}
    for page in range(1, max_pages + 1):
        params = {"ano": YEAR, "mes": month}
        if page > 1:
            params["page"] = str(page)
        url = f"{BASE_URL}?{urlencode(params)}"
        html = fetch_bytes(url).decode("utf-8", errors="replace")
        page_entries = parse_listing(html, month)
        new_entries = [entry for entry in page_entries if entry.code not in entries_by_code]
        for entry in new_entries:
            entries_by_code[entry.code] = entry
        if not page_entries or not new_entries:
            break
    return list(entries_by_code.values())


def detail_url(code: str) -> str:
    return f"{DETAIL_URL}?{urlencode({'codigo': code})}"


def download_detail(entry: DeputyEntry, raw_dir: Path, refresh: bool) -> tuple[Path, list[dict[str, str]]]:
    month_dir = raw_dir / f"{YEAR}_{entry.month}"
    month_dir.mkdir(parents=True, exist_ok=True)
    html_path = month_dir / f"{safe_filename(entry.name)}.html"
    url = detail_url(entry.code)

    if refresh or not html_path.exists() or html_path.stat().st_size == 0:
        html_path.write_bytes(fetch_bytes(url))

    html = html_path.read_text(encoding="utf-8", errors="replace")
    rows = parse_detail_rows(html)
    for row in rows:
        row["ANO"] = YEAR
        row["MES"] = entry.month
        row["PERIODO"] = f"{entry.month}/{YEAR}"
        row["DEPUTADO"] = entry.name
        row["CODIGO"] = entry.decoded_code
        row["VALOR_NUM"] = parse_brazilian_decimal(row["VALOR"])
        row["URL_DETALHE"] = url
    return html_path, rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ANO",
        "MES",
        "PERIODO",
        "DEPUTADO",
        "EMPENHO",
        "DESCRICAO",
        "CNPJ",
        "CREDOR",
        "VALOR",
        "VALOR_NUM",
        "CODIGO",
        "URL_DETALHE",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="dados/raw/detalhes")
    parser.add_argument("--out-csv", default="dados/processed/vdp_2025_por_deputado.csv")
    parser.add_argument("--manifest", default="dados/processed/vdp_2025_manifest.json")
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    out_csv = Path(args.out_csv)
    manifest_path = Path(args.manifest)

    all_rows: list[dict[str, str]] = []
    manifest: dict[str, object] = {
        "source": BASE_URL,
        "year": YEAR,
        "months": {},
    }

    for month in MONTHS:
        entries = list_deputies_for_month(month, args.max_pages)
        month_rows = 0
        detail_pages = 0
        print(f"{YEAR}-{month}: {len(entries)} deputados encontrados")
        for index, entry in enumerate(entries, start=1):
            _, rows = download_detail(entry, raw_dir, refresh=args.refresh)
            detail_pages += 1
            month_rows += len(rows)
            all_rows.extend(rows)
            print(f"  {index:02d}/{len(entries):02d} {entry.name}: {len(rows)} linhas")
        manifest["months"][month] = {
            "deputies": len(entries),
            "detail_pages": detail_pages,
            "rows": month_rows,
        }

    write_csv(out_csv, all_rows)
    manifest["total_rows"] = len(all_rows)
    manifest["output_csv"] = str(out_csv)
    manifest["raw_detail_dir"] = str(raw_dir)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"CSV consolidado: {out_csv} ({len(all_rows)} linhas)")
    print(f"Manifesto: {manifest_path}")


if __name__ == "__main__":
    main()
