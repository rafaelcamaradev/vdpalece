from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "dados" / "processed" / "vdp_2025_manifest.json"
DASHBOARD_CSV = ROOT / "dados" / "processed" / "vdp_2025_dashboard.csv"
PDF_PATH = ROOT / "docs" / "relatorio_dashboard_vdp_2025.pdf"
MD_PATH = ROOT / "docs" / "relatorio_dashboard_vdp_2025.md"


PROMPTS = [
    "analise as instrucoes para construcao de um dashboard no PDF deste diretorio. nao faca nada por agora",
    "extraia as informacoes desse link e baixe o que e preciso. Considere utilizar para construcao do dashboard flask ou Streamlit, o que for mais otimizado para esse fim.",
    "considere baixar os 12 meses pra cada deputado",
    "prossiga com o streamlit e ao final informe o endpoint do servico. Consolide todas as etapas que vc realizou (bem como dificuldades enfrentadas e erros, prompts inseridos e erros de dados nos arquivos CSV), pode ser em um documento PDF.",
]

NAME_FIXES = [
    ("DEP ALCIDERS FERNANDES", "DEP ALCIDES FERNANDES"),
    ("DEP ALMIIR BIE", "DEP ALMIR BIE"),
    ("DEP ALMIR B", "DEP ALMIR BIE"),
    ("DEP ALYSSON AGUYIAR", "DEP ALYSSON AGUIAR"),
    ("Variacao indevida do nome de Carmelo Neto", "DEP CARMELO NETO"),
    ("DEP EMIILA PESSOA", "DEP EMILIA PESSOA"),
    ("DEP EMILA PESSOA", "DEP EMILIA PESSOA"),
    ("DEP FIRMO CAMUCA", "DEP FIRMO CAMURCA"),
    ("DEP GUILHERME BISMARK", "DEP GUILHERME BISMARCK"),
    ("DEP MISSISAS DIAS", "DEP MISSIAS DIAS"),
    ("DEP SERGIO AHUIAR", "DEP SERGIO AGUIAR"),
]


def read_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def read_dashboard_rows() -> list[dict[str, str]]:
    with DASHBOARD_CSV.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def raw_monthly_counts() -> list[tuple[str, int, int, int]]:
    processed = Counter()
    for row in read_dashboard_rows():
        processed[row["MES"]] += 1

    counts = []
    for path in sorted((ROOT / "dados" / "raw").glob("vdp_2025_*.csv")):
        month = path.stem[-2:]
        with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
            raw_rows = list(csv.reader(handle, delimiter=";"))
        header_idx = next(i for i, row in enumerate(raw_rows) if row and row[0] == "DEPUTADO")
        data = [row for row in raw_rows[header_idx + 1 :] if len(row) >= 7 and any(cell.strip() for cell in row)]
        filled = sum(1 for row in data if row[0].strip())
        counts.append((month, len(data), filled, processed[month]))
    return counts


def build_markdown(manifest: dict, rows: list[dict[str, str]]) -> str:
    months = manifest["months"]
    total_rows = len(rows)
    unique_deputies = len({row["DEPUTADO"] for row in rows})
    original_deputies = len({row["DEPUTADO_ORIGINAL"] for row in rows})
    negative_rows = sum(1 for row in rows if row["VALOR_NUM"].startswith("-"))
    html_count = len(list((ROOT / "dados" / "raw" / "detalhes").rglob("*.html")))

    lines = [
        "# Relatorio de construcao do dashboard VDP ALECE 2025",
        "",
        "## Objetivo",
        "Construir um painel de visualizacao para a Verba de Desempenho Parlamentar (VDP) da Assembleia Legislativa do Estado do Ceara, cobrindo janeiro a dezembro de 2025, com filtros por deputado, mes/ano e credor, graficos de top 10 despesas por deputado e por credor, e evolucao mensal das despesas.",
        "",
        "## Prompts/solicitacoes recebidas",
    ]
    for index, prompt in enumerate(PROMPTS, start=1):
        lines.append(f"{index}. {prompt}")

    lines.extend(
        [
            "",
            "## Etapas realizadas",
            "1. Analisei o PDF do trabalho no diretorio e extraí os requisitos minimos do dashboard.",
            "2. Acessei o portal da ALECE e identifiquei o endpoint mensal de CSV.",
            "3. Baixei os 12 CSVs mensais de 2025 para dados/raw.",
            "4. Inspecionei o HTML do portal e descobri que o detalhe por deputado e mes e carregado por iframe/modal.",
            "5. Identifiquei a rota de detalhe: /despesas/verba-desempenho-parlamentar/detalhes?codigo=...",
            "6. Criei scripts de coleta e preparacao dos dados com biblioteca padrao do Python.",
            "7. Baixei as paginas de detalhe para cada deputado em cada mes de 2025.",
            "8. Consolidei os detalhes em CSV, adicionando ANO, MES, PERIODO, DEPUTADO e URL_DETALHE.",
            "9. Gereei a base tratada do dashboard com nomes de deputados normalizados.",
            "10. Instalei Streamlit, pandas, plotly e reportlab em ambiente virtual local.",
            "11. Implementei o dashboard Streamlit com filtros, indicadores, graficos e tabela exportavel.",
            "",
            "## Rotas e comandos principais",
            "- CSV mensal: https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar/csv?ano=2025&mes=MM",
            "- Listagem paginada: https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar?ano=2025&mes=MM&page=N",
            "- Detalhe por deputado/mes: https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar/detalhes?codigo=CODIGO",
            "- O codigo de detalhe decodifica para o padrao 2025_MM_DEP NOME.",
            "",
            "## Dificuldades e erros enfrentados",
            "- Nao havia extratores de PDF instalados, como pdftotext, pypdf, PyPDF2 ou pdfplumber.",
            "- A primeira tentativa de abrir o PDF por nome literal falhou por perda do acento no shell; a solucao foi localizar o arquivo por glob *.pdf.",
            "- O PDF usava fluxos FlateDecode e mapas ToUnicode; foi necessario decodificar os fluxos internos para recuperar o texto.",
            "- A primeira tentativa de download pelo sandbox falhou com 'Impossivel conectar-se ao servidor remoto'; foi necessario executar a coleta com permissao de rede.",
            "- O portal nao expunha links diretos para CSV por deputado; os detalhes eram carregados por modal/iframe via JavaScript.",
            "- O endpoint mensal agregado continha linhas sem deputado, insuficientes para o filtro obrigatorio por parlamentar.",
            "- Nenhuma biblioteca de dashboard estava instalada inicialmente; foi criado um ambiente virtual .venv.",
            "",
            "## Erros e ajustes encontrados nos arquivos CSV/dados",
            "- A primeira linha dos CSVs mensais agregados e vazia no formato ;;; antes do cabecalho real.",
            "- O separador dos CSVs e ponto e virgula.",
            "- Os valores monetarios usam formato brasileiro, por exemplo 6.516,55, exigindo conversao para numero.",
            "- Existem valores negativos, preservados na base por representarem anulacoes ou estornos.",
            "- Os CSVs mensais agregados possuem linhas sem DEPUTADO preenchido.",
            "- O portal contem erros evidentes de digitacao em nomes de deputados, normalizados apenas na base final do dashboard.",
            "",
            "## Normalizacoes de nomes aplicadas",
        ]
    )
    for source, target in NAME_FIXES:
        lines.append(f"- {source} -> {target}")

    lines.extend(
        [
            "",
            "## Resumo quantitativo",
            f"- Registros na base final: {total_rows}",
            f"- Deputados unicos na base final normalizada: {unique_deputies}",
            f"- Nomes originais distintos antes da normalizacao: {original_deputies}",
            f"- Paginas HTML de detalhe salvas: {html_count}",
            f"- Registros com valor negativo: {negative_rows}",
            "",
            "### Coleta por mes",
            "| Mes | Deputados encontrados | Paginas de detalhe | Registros consolidados |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for month, info in months.items():
        lines.append(f"| {month}/2025 | {info['deputies']} | {info['detail_pages']} | {info['rows']} |")

    lines.extend(
        [
            "",
            "### Comparacao entre CSV mensal e detalhe por deputado",
            "| Mes | Linhas no CSV mensal | Linhas com deputado preenchido | Linhas no detalhe por deputado |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for month, total, filled, detail in raw_monthly_counts():
        lines.append(f"| {month}/2025 | {total} | {filled} | {detail} |")

    lines.extend(
        [
            "",
            "## Arquivos entregues",
            "- streamlit_app.py: dashboard Streamlit.",
            "- requirements.txt: dependencias do projeto.",
            "- scripts/download_vdp_2025.py: coleta reproduzivel.",
            "- scripts/prepare_vdp_dashboard_data.py: tratamento da base.",
            "- dados/processed/vdp_2025_dashboard.csv: base final para visualizacao.",
            "- dados/processed/vdp_2025_por_deputado.csv: consolidado extraido dos detalhes.",
            "- dados/processed/vdp_2025_manifest.json: manifesto de coleta.",
            "- docs/ajustes_dados.md: documentacao resumida de ajustes.",
            "- docs/relatorio_dashboard_vdp_2025.pdf: este relatorio.",
            "",
            "## Decisao tecnica",
            "Streamlit foi escolhido em vez de Flask por ser mais direto para paineis exploratorios: filtros, tabelas, download e graficos interativos exigem menos infraestrutura e menos codigo. Para o volume atual de 4.219 registros, carregar a base em memoria e suficiente.",
        ]
    )
    return "\n".join(lines) + "\n"


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    safe = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    return Paragraph(safe, style)


def add_heading(story: list, text: str, styles, level: int = 1) -> None:
    style = styles["Heading1"] if level == 1 else styles["Heading2"]
    story.append(Paragraph(text, style))
    story.append(Spacer(1, 0.18 * cm))


def add_bullets(story: list, items: list[str], style: ParagraphStyle) -> None:
    for item in items:
        story.append(Paragraph(f"- {item}", style))
        story.append(Spacer(1, 0.05 * cm))


def build_pdf(manifest: dict, rows: list[dict[str, str]]) -> None:
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
    )

    styles = getSampleStyleSheet()
    styles["Title"].fontName = "Helvetica-Bold"
    styles["Heading1"].fontName = "Helvetica-Bold"
    styles["Heading2"].fontName = "Helvetica-Bold"
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        spaceAfter=5,
    )
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=7.6,
        leading=9.3,
    )

    total_rows = len(rows)
    unique_deputies = len({row["DEPUTADO"] for row in rows})
    original_deputies = len({row["DEPUTADO_ORIGINAL"] for row in rows})
    negative_rows = sum(1 for row in rows if row["VALOR_NUM"].startswith("-"))
    html_count = len(list((ROOT / "dados" / "raw" / "detalhes").rglob("*.html")))

    story = [Paragraph("Relatorio de construcao do dashboard VDP ALECE 2025", styles["Title"])]
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        paragraph(
            "Fonte principal: https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar",
            body,
        )
    )

    add_heading(story, "Objetivo", styles, 2)
    story.append(
        paragraph(
            "Construir um painel de visualizacao para a Verba de Desempenho Parlamentar da ALECE, cobrindo janeiro a dezembro de 2025, com filtros por deputado, mes/ano e credor, graficos top 10 por deputado e credor, e evolucao mensal.",
            body,
        )
    )

    add_heading(story, "Prompts/solicitacoes recebidas", styles, 2)
    for index, prompt in enumerate(PROMPTS, start=1):
        story.append(paragraph(f"{index}. {prompt}", body))

    add_heading(story, "Etapas realizadas", styles, 2)
    add_bullets(
        story,
        [
            "Analise do PDF da disciplina e extracao dos requisitos minimos.",
            "Identificacao do endpoint CSV mensal e download dos 12 CSVs de 2025.",
            "Inspecao do HTML/JavaScript do portal para descobrir a rota oculta de detalhe por deputado/mes.",
            "Coleta de 617 paginas HTML de detalhe e consolidacao em CSV.",
            "Tratamento da base com conversao monetaria, preservacao de negativos e normalizacao de nomes.",
            "Implementacao do dashboard Streamlit com filtros, indicadores, graficos, rankings e exportacao.",
            "Geracao deste relatorio em PDF.",
        ],
        body,
    )

    add_heading(story, "Dificuldades e erros enfrentados", styles, 2)
    add_bullets(
        story,
        [
            "Nao havia pdftotext, pypdf, PyPDF2 ou pdfplumber instalados.",
            "A leitura inicial do PDF por nome literal falhou por perda do acento no shell; foi usado glob *.pdf.",
            "O PDF exigiu decodificacao de fluxos FlateDecode e mapas ToUnicode.",
            "O primeiro download falhou no sandbox com 'Impossivel conectar-se ao servidor remoto'; a rede foi autorizada em seguida.",
            "A rota por deputado nao estava em links diretos; ela era montada em modal/iframe.",
            "Nenhuma biblioteca de dashboard estava instalada; foi criado um ambiente virtual .venv.",
        ],
        body,
    )

    add_heading(story, "Erros e ajustes nos CSVs/dados", styles, 2)
    add_bullets(
        story,
        [
            "Primeira linha vazia nos CSVs mensais agregados: ;;;.",
            "Separador de campos: ponto e virgula.",
            "Valores monetarios em formato brasileiro, convertidos para numero decimal.",
            "Valores negativos preservados como anulacoes ou estornos.",
            "Linhas sem DEPUTADO nos CSVs mensais agregados; os detalhes por deputado foram usados para o dashboard.",
            "Erros de digitacao em nomes de deputados, corrigidos no campo DEPUTADO da base final e preservados em DEPUTADO_ORIGINAL.",
        ],
        body,
    )

    story.append(PageBreak())
    add_heading(story, "Normalizacoes aplicadas", styles, 2)
    name_table = [["Nome no portal", "Nome usado no dashboard"], *NAME_FIXES]
    table = Table(name_table, colWidths=[7.2 * cm, 7.2 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.25 * cm))

    add_heading(story, "Resumo quantitativo", styles, 2)
    summary_table = Table(
        [
            ["Metrica", "Valor"],
            ["Registros na base final", str(total_rows)],
            ["Deputados unicos normalizados", str(unique_deputies)],
            ["Nomes originais distintos", str(original_deputies)],
            ["Paginas HTML de detalhe", str(html_count)],
            ["Registros com valor negativo", str(negative_rows)],
        ],
        colWidths=[8.5 * cm, 5.5 * cm],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.25 * cm))

    add_heading(story, "Coleta por mes", styles, 2)
    month_table = [["Mes", "Deputados", "Paginas", "Registros"]]
    for month, info in manifest["months"].items():
        month_table.append([f"{month}/2025", info["deputies"], info["detail_pages"], info["rows"]])
    table = Table(month_table, colWidths=[3.0 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(table)

    story.append(PageBreak())
    add_heading(story, "Comparacao: CSV mensal x detalhe por deputado", styles, 2)
    comparison = [["Mes", "CSV mensal", "Com deputado", "Detalhe"]]
    for month, total, filled, detail in raw_monthly_counts():
        comparison.append([f"{month}/2025", total, filled, detail])
    table = Table(comparison, colWidths=[3.0 * cm, 3.8 * cm, 3.8 * cm, 3.8 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.25 * cm))

    add_heading(story, "Arquivos entregues", styles, 2)
    add_bullets(
        story,
        [
            "streamlit_app.py",
            "requirements.txt",
            "scripts/download_vdp_2025.py",
            "scripts/prepare_vdp_dashboard_data.py",
            "dados/processed/vdp_2025_dashboard.csv",
            "dados/processed/vdp_2025_por_deputado.csv",
            "dados/processed/vdp_2025_manifest.json",
            "docs/ajustes_dados.md",
            "docs/relatorio_dashboard_vdp_2025.pdf",
        ],
        small,
    )

    add_heading(story, "Decisao tecnica", styles, 2)
    story.append(
        paragraph(
            "Streamlit foi escolhido em vez de Flask porque entrega filtros, tabelas, download e graficos interativos com menos infraestrutura. Para 4.219 registros, a carga em memoria e adequada.",
            body,
        )
    )

    doc.build(story)


def main() -> None:
    manifest = read_manifest()
    rows = read_dashboard_rows()
    markdown = build_markdown(manifest, rows)
    MD_PATH.write_text(markdown, encoding="utf-8")
    build_pdf(manifest, rows)
    print(f"Markdown: {MD_PATH}")
    print(f"PDF: {PDF_PATH}")


if __name__ == "__main__":
    main()
