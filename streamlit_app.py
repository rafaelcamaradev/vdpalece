from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "dados" / "processed" / "vdp_2025_dashboard.csv"
SOURCE_URL = "https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar"

DEPUTY_NAME_FIXES = {
    "DEP CARMELO BOLSONARO": "DEP CARMELO NETO",
}

HIDE_ORIGINAL_AS_ALIAS = {
    "DEP CARMELO BOLSONARO",
}

COLOR_SEQUENCE = [
    "#2563eb",
    "#16a34a",
    "#f59e0b",
    "#dc2626",
    "#7c3aed",
    "#0891b2",
    "#db2777",
    "#65a30d",
    "#ea580c",
    "#475569",
]


st.set_page_config(
    page_title="VDP ALECE 2025",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        background: #ffffff;
    }
    div[data-testid="stMetricLabel"] p {
        color: #475569;
        font-size: 0.84rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.45rem;
    }
    .source-line {
        color: #475569;
        font-size: 0.9rem;
        margin-top: -0.8rem;
        text-align: center;
    }
    .app-title {
        text-align: center;
        font-size: 2.35rem;
        font-weight: 700;
        line-height: 1.15;
        margin: 0 0 0.75rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def brl(value: float) -> str:
    formatted = f"R$ {value:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def file_version(path: Path) -> str:
    stat = path.stat()
    return f"{stat.st_mtime_ns}:{stat.st_size}"


def clean_deputy_name(value: object) -> str:
    name = str(value).strip().upper().replace("DEP.", "DEP")
    return " ".join(name.split())


def normalize_deputy_name(value: object) -> str:
    name = clean_deputy_name(value)
    return DEPUTY_NAME_FIXES.get(name, name)


def replace_hidden_aliases(value: object) -> str:
    text = str(value)
    for alias in HIDE_ORIGINAL_AS_ALIAS:
        replacement = DEPUTY_NAME_FIXES[alias]
        text = text.replace(alias, replacement)
        text = text.replace(alias.replace("DEP ", "DEP. "), replacement)
    return text


def is_valid_deputy_name(value: object) -> bool:
    return clean_deputy_name(value).startswith("DEP ")


@st.cache_data(show_spinner=False)
def load_data(path: str, data_version: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    df["DEPUTADO"] = df["DEPUTADO"].map(normalize_deputy_name)
    if "DEPUTADO_ORIGINAL" in df.columns:
        df["DEPUTADO_ORIGINAL"] = df["DEPUTADO_ORIGINAL"].map(
            lambda value: (
                normalize_deputy_name(value)
                if clean_deputy_name(value) in HIDE_ORIGINAL_AS_ALIAS
                else clean_deputy_name(value)
            )
        )
    for column in ["DESCRICAO", "CODIGO"]:
        if column in df.columns:
            df[column] = df[column].map(replace_hidden_aliases)
    df = df[df["DEPUTADO"].map(is_valid_deputy_name)].copy()
    df["VALOR_NUM"] = pd.to_numeric(df["VALOR_NUM"], errors="coerce").fillna(0)
    df["DATA_MES"] = pd.to_datetime(df["DATA_MES"], errors="coerce")
    df["VALOR_POSITIVO"] = df["VALOR_NUM"].clip(lower=0)
    df["VALOR_NEGATIVO"] = df["VALOR_NUM"].clip(upper=0)
    df["MES_LABEL"] = df["DATA_MES"].dt.strftime("%m/%Y")
    return df


def filtered_options(df: pd.DataFrame, column: str) -> list[str]:
    return sorted(item for item in df[column].dropna().unique() if str(item).strip())


def normalize_period_token(token: str) -> str | None:
    token = token.strip()
    if re.fullmatch(r"\d{2}/\d{4}", token):
        return token
    if re.fullmatch(r"\d{4}-\d{2}", token):
        year, month = token.split("-")
        return f"{month}/{year}"
    return None


def months_between(start: str, end: str, month_order: list[str]) -> list[str]:
    start_index = month_order.index(start)
    end_index = month_order.index(end)
    if start_index > end_index:
        start_index, end_index = end_index, start_index
    return month_order[start_index : end_index + 1]


def parse_period_text(period_text: str, month_order: list[str]) -> tuple[list[str], str | None]:
    tokens = re.findall(r"\d{2}/\d{4}|\d{4}-\d{2}", period_text)
    periods = [normalize_period_token(token) for token in tokens]
    periods = [period for period in periods if period]

    if not periods:
        return [], "Informe um periodo como 03/2025 ou 03/2025 a 08/2025."

    for period in periods[:2]:
        if period not in month_order:
            return [], f"O periodo {period} nao existe na base carregada."

    if len(periods) == 1:
        return [periods[0]], None
    return months_between(periods[0], periods[1], month_order), None


def apply_filters(
    df: pd.DataFrame,
    months: list[str],
    deputies: list[str],
    creditors: list[str],
) -> pd.DataFrame:
    filtered = df.copy()
    if months:
        filtered = filtered[filtered["PERIODO"].isin(months)]
    if deputies:
        filtered = filtered[filtered["DEPUTADO"].isin(deputies)]
    if creditors:
        filtered = filtered[filtered["CREDOR"].isin(creditors)]
    return filtered


def grouped_top(df: pd.DataFrame, by: str, value_col: str, limit: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[by, value_col])
    grouped = (
        df.groupby(by, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
        .head(limit)
    )
    return grouped[grouped[value_col] > 0]


def pie_chart(df: pd.DataFrame, names: str, values: str, title: str):
    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        hole=0.38,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        margin=dict(l=8, r=8, t=48, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0),
        title_font_size=18,
    )
    return fig


def line_chart(df: pd.DataFrame):
    monthly = (
        df.groupby(["DATA_MES", "PERIODO"], as_index=False)
        .agg(
            valor_liquido=("VALOR_NUM", "sum"),
            despesas_positivas=("VALOR_POSITIVO", "sum"),
        )
        .sort_values("DATA_MES")
    )
    long_df = monthly.melt(
        id_vars=["DATA_MES", "PERIODO"],
        value_vars=["valor_liquido", "despesas_positivas"],
        var_name="Serie",
        value_name="Valor",
    )
    labels = {
        "valor_liquido": "Valor liquido",
        "despesas_positivas": "Lancamentos positivos",
    }
    long_df["Serie"] = long_df["Serie"].map(labels)
    fig = px.line(
        long_df,
        x="PERIODO",
        y="Valor",
        color="Serie",
        markers=True,
        title="Evolucao mensal das despesas",
        color_discrete_sequence=["#2563eb", "#16a34a"],
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=48, b=8),
        xaxis_title=None,
        yaxis_title="Valor",
        title_font_size=18,
        legend_title_text=None,
    )
    fig.update_yaxes(tickprefix="R$ ", separatethousands=True)
    return fig


df = load_data(str(DATA_PATH), file_version(DATA_PATH))

month_order = (
    df[["PERIODO", "DATA_MES"]]
    .drop_duplicates()
    .sort_values("DATA_MES")["PERIODO"]
    .tolist()
)

st.markdown(
    f"""
    <h1 class="app-title">VDP ALECE 2025</h1>
    <div class="source-line">Fonte: <a href="{SOURCE_URL}" target="_blank">Portal da Transparencia da ALECE</a></div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filtros")
    period_mode = st.radio(
        "Mes/Ano",
        ["Selecionar intervalo", "Digitar periodo"],
        horizontal=False,
    )
    if period_mode == "Selecionar intervalo":
        selected_range = st.select_slider(
            "Periodo",
            options=month_order,
            value=(month_order[0], month_order[-1]),
        )
        selected_months = months_between(selected_range[0], selected_range[1], month_order)
    else:
        period_text = st.text_input(
            "Periodo",
            value=f"{month_order[0]} a {month_order[-1]}",
            placeholder="Ex.: 03/2025 a 08/2025",
        )
        selected_months, period_error = parse_period_text(period_text, month_order)
        st.caption("Aceita 03/2025, 03/2025 a 08/2025 ou 2025-03 a 2025-08.")
        if period_error:
            st.error(period_error)
    st.caption(f"{len(selected_months)} mes(es) selecionado(s).")

    selected_deputies = st.multiselect(
        "Deputado",
        filtered_options(df, "DEPUTADO"),
        default=[],
        placeholder="Todos",
    )
    selected_creditors = st.multiselect(
        "Credor",
        filtered_options(df, "CREDOR"),
        default=[],
        placeholder="Todos",
    )
    calculation = st.radio(
        "Calculo dos graficos",
        ["Valor liquido", "Somente lancamentos positivos"],
        horizontal=False,
    )

filtered = apply_filters(df, selected_months, selected_deputies, selected_creditors)
value_col = "VALOR_NUM" if calculation == "Valor liquido" else "VALOR_POSITIVO"

total_net = float(filtered["VALOR_NUM"].sum()) if not filtered.empty else 0.0
total_positive = float(filtered["VALOR_POSITIVO"].sum()) if not filtered.empty else 0.0
total_negative = float(filtered["VALOR_NEGATIVO"].sum()) if not filtered.empty else 0.0
record_count = int(len(filtered))
deputy_count = int(filtered["DEPUTADO"].nunique()) if not filtered.empty else 0

metric_cols = st.columns(5)
metric_cols[0].metric("Valor liquido", brl(total_net))
metric_cols[1].metric("Lancamentos positivos", brl(total_positive))
metric_cols[2].metric("Anulacoes/estornos", brl(total_negative))
metric_cols[3].metric("Registros", f"{record_count:,}".replace(",", "."))
metric_cols[4].metric("Deputados", str(deputy_count))

tab_overview, tab_rankings, tab_data = st.tabs(["Visao geral", "Rankings", "Dados"])

with tab_overview:
    st.plotly_chart(line_chart(filtered), width="stretch")

    left, right = st.columns(2)
    with left:
        monthly_table = (
            filtered.groupby(["DATA_MES", "PERIODO"], as_index=False)
            .agg(
                valor_liquido=("VALOR_NUM", "sum"),
                lancamentos_positivos=("VALOR_POSITIVO", "sum"),
                registros=("EMPENHO", "count"),
            )
            .sort_values("DATA_MES")
        )
        st.dataframe(
            monthly_table[["PERIODO", "valor_liquido", "lancamentos_positivos", "registros"]],
            width="stretch",
            hide_index=True,
            column_config={
                "PERIODO": "Mes/Ano",
                "valor_liquido": st.column_config.NumberColumn("Valor liquido", format="R$ %.2f"),
                "lancamentos_positivos": st.column_config.NumberColumn(
                    "Lancamentos positivos", format="R$ %.2f"
                ),
                "registros": "Registros",
            },
        )
    with right:
        creditor_share = grouped_top(filtered, "CREDOR", value_col, limit=8)
        if creditor_share.empty:
            st.info("Sem dados para a selecao atual.")
        else:
            fig = px.bar(
                creditor_share.sort_values(value_col),
                x=value_col,
                y="CREDOR",
                orientation="h",
                title="Principais credores",
                color_discrete_sequence=["#2563eb"],
            )
            fig.update_layout(
                margin=dict(l=8, r=8, t=48, b=8),
                xaxis_title="Valor",
                yaxis_title=None,
                title_font_size=18,
            )
            fig.update_xaxes(tickprefix="R$ ", separatethousands=True)
            st.plotly_chart(fig, width="stretch")

with tab_rankings:
    left, right = st.columns(2)
    top_deputies = grouped_top(filtered, "DEPUTADO", value_col)
    top_creditors = grouped_top(filtered, "CREDOR", value_col)

    with left:
        if top_deputies.empty:
            st.info("Sem dados para a selecao atual.")
        else:
            st.plotly_chart(
                pie_chart(top_deputies, "DEPUTADO", value_col, "Top 10 despesas por deputado"),
                width="stretch",
            )
            st.dataframe(
                top_deputies,
                width="stretch",
                hide_index=True,
                column_config={
                    "DEPUTADO": "Deputado",
                    value_col: st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                },
            )

    with right:
        if top_creditors.empty:
            st.info("Sem dados para a selecao atual.")
        else:
            st.plotly_chart(
                pie_chart(top_creditors, "CREDOR", value_col, "Top 10 despesas por credor"),
                width="stretch",
            )
            st.dataframe(
                top_creditors,
                width="stretch",
                hide_index=True,
                column_config={
                    "CREDOR": "Credor",
                    value_col: st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                },
            )

with tab_data:
    visible_columns = [
        "PERIODO",
        "DEPUTADO",
        "DEPUTADO_ORIGINAL",
        "EMPENHO",
        "CNPJ",
        "CREDOR",
        "VALOR",
        "VALOR_NUM",
        "DESCRICAO",
    ]
    st.dataframe(
        filtered[visible_columns].sort_values(["PERIODO", "DEPUTADO", "CREDOR"]),
        width="stretch",
        hide_index=True,
        column_config={
            "PERIODO": "Mes/Ano",
            "DEPUTADO": "Deputado",
            "DEPUTADO_ORIGINAL": "Nome original",
            "EMPENHO": "Empenho",
            "CNPJ": "CNPJ",
            "CREDOR": "Credor",
            "VALOR": "Valor original",
            "VALOR_NUM": st.column_config.NumberColumn("Valor numerico", format="R$ %.2f"),
            "DESCRICAO": "Descricao",
        },
    )

    csv_bytes = filtered[visible_columns].to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        "Baixar dados filtrados",
        data=csv_bytes,
        file_name="vdp_2025_dados_filtrados.csv",
        mime="text/csv",
    )
