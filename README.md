# VDP ALECE 2025

Dashboard em Streamlit para analise da Verba de Desempenho Parlamentar da Assembleia Legislativa do Estado do Ceara em 2025.

## Como executar

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Endpoint local padrao:

```text
http://127.0.0.1:8501
```

## Dados

A base tratada esta em `dados/processed/vdp_2025_dashboard.csv`.

Fonte:

```text
https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar
```

## Documentacao

O relatorio do processo de coleta, tratamento e construcao do dashboard esta em:

```text
docs/relatorio_dashboard_vdp_2025.pdf
```
