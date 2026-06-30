from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "ranking_casos_ia_setor_publico.md"
PDF_PATH = ROOT / "docs" / "ranking_casos_ia_setor_publico.pdf"


REQUIREMENTS = [
    "Contexto e dor: narrativa humana e escala do problema.",
    "Intervencao: solucao, tecnologia de IA e atores envolvidos.",
    "Impacto: metricas quantitativas, valor publico e efeitos sociais/operacionais.",
    "Aplicabilidade ao Brasil: dono institucional, matriz tecnica/legal/orcamentaria-cultural e veredito.",
    "Fontes: priorizar repositorios oficiais, governamentais e OCDE/OPSI.",
]


CASES = [
    {
        "rank": 1,
        "name": "Boti, the City's WhatsApp",
        "country": "Argentina - Buenos Aires",
        "oecd": "Sim. Caso publicado na biblioteca da OCDE/OPSI e listado na area de IA no setor publico.",
        "why": "Melhor caso geral para a apresentacao: combina IA/NLP, atendimento ao cidadao, escala massiva, metricas claras e alta replicabilidade municipal no Brasil.",
        "technology": "Chatbot omnicanal no WhatsApp e web, com IA e processamento de linguagem natural para interpretar mensagens, sugerir respostas e integrar servicos publicos.",
        "actors": "Governo da Cidade de Buenos Aires, equipes de inovacao/digital, designers, desenvolvedores, comunicadores, especialistas em dados e fornecedores como Amazon, Google e Botmaker.",
        "metrics": [
            "Recorde de 11 milhoes de conversas em janeiro de 2022.",
            "Media mensal aproximada de 5 milhoes de conversas.",
            "Mais de 450 topicos, 70 integracoes e 15 filas de atendimento humano.",
            "Cerca de 1,3 milhao de usuarios por mes e mais de 250 operadores humanos.",
            "Mais de 11 milhoes de agendamentos de vacinacao oferecidos via WhatsApp.",
            "Satisfacao media mensal de 90% e mais de 80% das conversas compreendidas.",
        ],
        "brazil": "Pode ser adaptado por prefeituras, estados ou Gov.br como canal unico de atendimento para saude, transporte, assistencia social, tributos, protocolos e servicos urbanos.",
        "feasibility": "Viavel no medio prazo, com piloto em 6 a 12 meses em uma prefeitura ou secretaria estadual. Requer base de conhecimento atualizada, integracao com sistemas legados, governanca de dados e plano LGPD.",
        "requirements_fit": "Cumpre todos os requisitos com folga: tem dor clara, tecnologia de IA identificavel, atores publicos/privados, metricas concretas e comparacao brasileira direta.",
        "sources": [
            "https://oecd-opsi.org/innovations/boti-the-citys-whatsapp/",
            "https://oecd-opsi.org/work-areas/ai/",
        ],
    },
    {
        "rank": 2,
        "name": "Electronic Quoter",
        "country": "Peru",
        "oecd": "Sim. Caso publicado na biblioteca da OCDE/OPSI, com tags de IA, blockchain e compras publicas.",
        "why": "Melhor caso para discutir compras publicas e Lei 14.133 no Brasil. Tem impacto operacional e financeiro muito forte.",
        "technology": "Ferramenta de cotacao eletronica para estimar precos em catalogos de acordos-marco, usando algoritmos estatisticos, componentes de IA e blockchain para transparencia/imutabilidade.",
        "actors": "PERU COMPRAS, operadores logisticos de entidades publicas, area de tecnologia da informacao, comunicacao institucional e lideranca da central de compras.",
        "metrics": [
            "Reducao dos atos preparatorios de compras de 68,1 dias corridos para 1 dia.",
            "Beneficio para 1.969 entidades publicas, aproximadamente 2 mil entidades.",
            "Simplificacao de aproximadamente 155.822 compras anuais.",
            "Volume estimado associado de US$ 400 milhoes.",
            "80,5% de satisfacao dos usuarios.",
            "88,6% confirmaram reducao de tempo na pesquisa de mercado.",
        ],
        "brazil": "Encaixe natural no Compras.gov.br, Ministerio da Gestao/SEGES, centrais estaduais de compras, TCU e controladorias. Pode apoiar pesquisa de preco, planejamento da contratacao e controle.",
        "feasibility": "Viavel no medio prazo. A maior barreira e qualidade/integracao dos dados historicos de compras e desenho juridico conforme Lei 14.133, pesquisa de precos, transparencia e governanca.",
        "requirements_fit": "Cumpre muito bem os requisitos de escala, impacto e aplicabilidade. A unica ressalva e explicar a IA com cuidado, pois parte do valor vem de estatistica, automacao e dados estruturados.",
        "sources": [
            "https://oecd-opsi.org/innovations/electronic-quoter-peru/",
        ],
    },
    {
        "rank": 3,
        "name": "Chatico Virtual Agent",
        "country": "Colombia - Bogota",
        "oecd": "Sim. Caso publicado na biblioteca da OCDE/OPSI com tag de Artificial Intelligence (AI).",
        "why": "Caso forte para governo aberto, participacao social e atendimento digital. Menor que Boti em escala, mas muito bom para storytelling.",
        "technology": "Agente virtual em web e WhatsApp, com IA, interoperabilidade entre fontes distritais e linguagem acessivel, para servicos, informacao e participacao cidada.",
        "actors": "Secretaria Geral da Prefeitura de Bogota, Alta Conselheira TIC, area de planejamento, entidades distritais, cidadaos e industria de TI contratada.",
        "metrics": [
            "45 mil interacoes/conversas registradas no periodo informado pela OCDE/OPSI.",
            "5.400 interacoes na versao web em 2021.",
            "91% de satisfacao em pesquisa.",
            "Tempo medio de resposta de 0,38 segundo.",
            "5.145 votos em Causas Ciudadanas em 2021 e mais de 32 mil votos em 2022.",
        ],
        "brazil": "Aplicavel a prefeituras e governos estaduais para consultas, beneficios, participacao popular, orcamento participativo, triagem de servicos e alertas personalizados.",
        "feasibility": "Viavel no medio prazo, especialmente em capitais e estados com canais digitais existentes. Exige desenho conversacional, integracao com bases oficiais, atendimento humano de retaguarda e regras LGPD.",
        "requirements_fit": "Cumpre todos os requisitos, especialmente narrativa, atores e impacto social. Fica abaixo de Boti apenas por escala menor e menos integracoes documentadas.",
        "sources": [
            "https://oecd-opsi.org/innovations/chatico-virtual-agent/",
        ],
    },
    {
        "rank": 4,
        "name": "Forecasting GDP with Explainable AI",
        "country": "Suecia",
        "oecd": "Sim. Caso publicado na biblioteca da OCDE/OPSI com tag de Artificial Intelligence (AI).",
        "why": "Tecnicamente muito forte, pois usa machine learning explicavel. E adequado para uma equipe que queira discutir IA de decisao economica, mas e menos intuitivo em uma apresentacao curta.",
        "technology": "Modelo hibrido de machine learning explicavel para previsao de PIB, com visualizacao da influencia das variaveis nas predicoes.",
        "actors": "Agencia Nacional de Gestao Financeira da Suecia (ESV), Data Lab da ESV, pesquisadores de machine learning do KTH Royal Institute of Technology, consultores de TI e estudantes.",
        "metrics": [
            "A aplicacao confirma que algoritmos de ML podem superar previsoes humanas/tradicionais no curto e medio prazo.",
            "Codigo e aplicacao foram compartilhados para testes e evolucao.",
            "A propria OCDE/OPSI registra que ainda ha trabalho em andamento para mensurar impacto numerico direto.",
        ],
        "brazil": "Poderia ser estudado por Ipea, Ministerio da Fazenda, Banco Central, Tesouro Nacional ou secretarias de planejamento para previsoes economicas explicaveis.",
        "feasibility": "Viavel no longo prazo para uso institucional pleno. Requer maturidade tecnica, dados economicos consistentes, governanca de modelos, explicabilidade e definicao de responsabilidade por previsoes.",
        "requirements_fit": "Cumpre bem tecnologia e atores, mas e mais fraco em storytelling simples e metricas operacionais ja comprovadas. Por isso fica fora do top 3.",
        "sources": [
            "https://oecd-opsi.org/innovations/forecasting-gdp/",
        ],
    },
]


PARLAMENTO_2030 = {
    "name": "Parlamento2030",
    "summary": "O caso sugerido pela equipe e bom para transparencia legislativa e monitoramento de ODS, mas nao e a melhor escolha para este trabalho de IA.",
    "evidence": [
        "O site oficial descreve scraping de PDFs, estruturacao de base e etiquetagem automatica por dicionarios de ODS/metas.",
        "A API publica mostra mais de 100 mil iniciativas no acervo e cerca de 45 mil iniciativas classificadas com ODS.",
        "A imagem enviada mostra o caso em pagina da OPSI/OCDE, mas a pagina principal verificavel do projeto nao apresenta metricas fortes de economia, satisfacao, reducao de filas ou horas poupadas.",
        "A IA e menos defensavel: parece mais automacao por regras/NLP e dicionarios do que machine learning claramente documentado.",
    ],
    "verdict": "Pode ser citado como alternativa, mas eu nao o escolheria para defender todos os requisitos. Ele e inferior a Boti, Electronic Quoter e Chatico para a rubrica do professor.",
    "sources": [
        "https://www.parlamento2030.es/",
        "https://api.quehacenlosdiputados.es/stats/overall?knowledgebase=ods",
        "https://github.com/politicalwatch/parlamento2030.es",
    ],
}


def markdown_report() -> str:
    lines = [
        "# Ranking de estudos de caso de IA aplicada ao setor publico",
        "",
        "## Objetivo",
        "Avaliar casos internacionais para o trabalho de Inteligencia Artificial Aplicada ao Setor Publico, com foco em aderencia aos requisitos do professor e facilidade de defesa em apresentacao de 5 a 10 minutos.",
        "",
        "## Requisitos do trabalho",
    ]
    lines.extend(f"- {item}" for item in REQUIREMENTS)
    lines.extend(
        [
            "",
            "## Ranking recomendado",
            "| Posicao | Caso | Pais | Esta na OCDE/OPSI? | Veredito |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for case in CASES:
        lines.append(
            f"| {case['rank']} | {case['name']} | {case['country']} | {case['oecd']} | {case['why']} |"
        )

    for case in CASES:
        lines.extend(
            [
                "",
                f"## {case['rank']}. {case['name']} ({case['country']})",
                f"**OCDE/OPSI:** {case['oecd']}",
                "",
                f"**Por que entra no ranking:** {case['why']}",
                "",
                f"**Tecnologia:** {case['technology']}",
                "",
                f"**Atores:** {case['actors']}",
                "",
                "**Metricas de impacto:**",
            ]
        )
        lines.extend(f"- {metric}" for metric in case["metrics"])
        lines.extend(
            [
                "",
                f"**Aplicabilidade ao Brasil:** {case['brazil']}",
                "",
                f"**Viabilidade:** {case['feasibility']}",
                "",
                f"**Defesa frente aos requisitos:** {case['requirements_fit']}",
                "",
                "**Fontes:**",
            ]
        )
        lines.extend(f"- {source}" for source in case["sources"])

    lines.extend(
        [
            "",
            "## Observacao sobre o caso sugerido: Parlamento2030",
            PARLAMENTO_2030["summary"],
            "",
            "**Evidencias verificadas:**",
        ]
    )
    lines.extend(f"- {item}" for item in PARLAMENTO_2030["evidence"])
    lines.extend(
        [
            "",
            f"**Veredito:** {PARLAMENTO_2030['verdict']}",
            "",
            "**Fontes:**",
        ]
    )
    lines.extend(f"- {source}" for source in PARLAMENTO_2030["sources"])

    lines.extend(
        [
            "",
            "## Recomendacao final",
            "Escolha Boti se a equipe quiser a opcao mais segura para nota: e simples de explicar, tem IA/NLP clara, impacto quantitativo forte e encaixe direto no Brasil. Escolha Electronic Quoter se quiser conectar o trabalho a compras publicas e Lei 14.133. Escolha Chatico se quiser uma narrativa de participacao cidada e governo aberto.",
            "",
        ]
    )
    return "\n".join(lines)


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(text), style)


def bullet_list(items: list[str], style: ParagraphStyle, bullet: str = "-") -> list:
    flowables = []
    for item in items:
        flowables.append(para(f"{bullet} {item}", style))
    return flowables


def source_text(sources: list[str]) -> str:
    return "Fontes: " + "; ".join(sources)


def build_pdf() -> None:
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
        pageCompression=0,
    )
    styles = getSampleStyleSheet()
    styles["Title"].fontName = "Helvetica-Bold"
    styles["Heading1"].fontName = "Helvetica-Bold"
    styles["Heading2"].fontName = "Helvetica-Bold"
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        spaceAfter=6,
        splitLongWords=True,
    )
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=8.2,
        leading=10,
        spaceAfter=4,
        splitLongWords=True,
        wordWrap="CJK",
    )
    rank_style = ParagraphStyle(
        "Rank",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        spaceBefore=2,
        spaceAfter=3,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        spaceAfter=3,
    )

    story = [
        Paragraph("Ranking de estudos de caso de IA aplicada ao setor publico", styles["Title"]),
        Spacer(1, 0.2 * cm),
        para(
            "Objetivo: avaliar casos internacionais para o trabalho de Inteligencia Artificial Aplicada ao Setor Publico, com foco em aderencia aos requisitos do professor e facilidade de defesa em apresentacao.",
            body,
        ),
        Spacer(1, 0.15 * cm),
        Paragraph("Requisitos do trabalho", styles["Heading2"]),
    ]
    story.extend(bullet_list(REQUIREMENTS, body))

    story.append(Paragraph("Ranking recomendado", styles["Heading2"]))
    for case in CASES:
        story.append(para(f"{case['rank']}. {case['name']} ({case['country']})", rank_style))
        story.append(para(f"OCDE/OPSI: {case['oecd']}", body))
        story.append(para(f"Forca principal: {case['why']}", body))
    story.append(Spacer(1, 0.1 * cm))

    for case in CASES:
        story.append(Paragraph(f"{case['rank']}. {case['name']} - {case['country']}", styles["Heading2"]))
        story.append(para(f"OCDE/OPSI: {case['oecd']}", body))
        story.append(para(f"Por que entra no ranking: {case['why']}", body))
        story.append(para(f"Tecnologia: {case['technology']}", body))
        story.append(para(f"Atores: {case['actors']}", body))
        story.append(para("Metricas de impacto:", label_style))
        story.extend(bullet_list(case["metrics"], small))
        story.append(para(f"Aplicabilidade ao Brasil: {case['brazil']}", body))
        story.append(para(f"Viabilidade: {case['feasibility']}", body))
        story.append(para(f"Defesa frente aos requisitos: {case['requirements_fit']}", body))
        story.append(para(source_text(case["sources"]), small))
        story.append(Spacer(1, 0.12 * cm))

    story.append(Paragraph("Observacao sobre o caso sugerido: Parlamento2030", styles["Heading2"]))
    story.append(para(PARLAMENTO_2030["summary"], body))
    story.append(para("Evidencias verificadas:", label_style))
    story.extend(bullet_list(PARLAMENTO_2030["evidence"], small))
    story.append(para(f"Veredito: {PARLAMENTO_2030['verdict']}", body))
    story.append(para(source_text(PARLAMENTO_2030["sources"]), small))

    story.append(Paragraph("Recomendacao final", styles["Heading2"]))
    story.append(
        para(
            "Escolha Boti se a equipe quiser a opcao mais segura para nota: e simples de explicar, tem IA/NLP clara, impacto quantitativo forte e encaixe direto no Brasil. Electronic Quoter e a melhor opcao para compras publicas e Lei 14.133. Chatico e muito bom para participacao cidada e governo aberto.",
            body,
        )
    )

    doc.build(story)


def main() -> None:
    MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text(markdown_report(), encoding="utf-8")
    build_pdf()
    print(f"Markdown: {MD_PATH}")
    print(f"PDF: {PDF_PATH}")


if __name__ == "__main__":
    main()
