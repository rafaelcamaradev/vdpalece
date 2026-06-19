# Relatorio de construcao do dashboard VDP ALECE 2025

## Equipe
- Giovanna Munhoz
- Gleydson Silva
- Jandro Medeiros
- Francisco Queiroz

## Objetivo
Construir um painel de visualizacao para a Verba de Desempenho Parlamentar (VDP) da Assembleia Legislativa do Estado do Ceara, cobrindo janeiro a dezembro de 2025, com filtros por deputado, mes/ano e credor, graficos de top 10 despesas por deputado e por credor, e evolucao mensal das despesas.

## Prompts/solicitacoes recebidas
1. analise as instrucoes para construcao de um dashboard no PDF deste diretorio. nao faca nada por agora
2. extraia as informacoes desse link e baixe o que e preciso. Considere utilizar para construcao do dashboard flask ou Streamlit, o que for mais otimizado para esse fim.
3. considere baixar os 12 meses pra cada deputado
4. prossiga com o streamlit e ao final informe o endpoint do servico. Consolide todas as etapas que vc realizou (bem como dificuldades enfrentadas e erros, prompts inseridos e erros de dados nos arquivos CSV), pode ser em um documento PDF.
5. no relatorio PDF ja gerado, incluir a lista com os nomes dos integrantes da equipe deste trabalho.

## Etapas realizadas
1. Analisei o PDF do trabalho no diretorio e extraí os requisitos minimos do dashboard.
2. Acessei o portal da ALECE e identifiquei o endpoint mensal de CSV.
3. Baixei os 12 CSVs mensais de 2025 para dados/raw.
4. Inspecionei o HTML do portal e descobri que o detalhe por deputado e mes e carregado por iframe/modal.
5. Identifiquei a rota de detalhe: /despesas/verba-desempenho-parlamentar/detalhes?codigo=...
6. Criei scripts de coleta e preparacao dos dados com biblioteca padrao do Python.
7. Baixei as paginas de detalhe para cada deputado em cada mes de 2025.
8. Consolidei os detalhes em CSV, adicionando ANO, MES, PERIODO, DEPUTADO e URL_DETALHE.
9. Gereei a base tratada do dashboard com nomes de deputados normalizados.
10. Instalei Streamlit, pandas, plotly e reportlab em ambiente virtual local.
11. Implementei o dashboard Streamlit com filtros, indicadores, graficos e tabela exportavel.

## Rotas e comandos principais
- CSV mensal: https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar/csv?ano=2025&mes=MM
- Listagem paginada: https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar?ano=2025&mes=MM&page=N
- Detalhe por deputado/mes: https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar/detalhes?codigo=CODIGO
- O codigo de detalhe decodifica para o padrao 2025_MM_DEP NOME.

## Dificuldades e erros enfrentados
- Nao havia extratores de PDF instalados, como pdftotext, pypdf, PyPDF2 ou pdfplumber.
- A primeira tentativa de abrir o PDF por nome literal falhou por perda do acento no shell; a solucao foi localizar o arquivo por glob *.pdf.
- O PDF usava fluxos FlateDecode e mapas ToUnicode; foi necessario decodificar os fluxos internos para recuperar o texto.
- A primeira tentativa de download pelo sandbox falhou com 'Impossivel conectar-se ao servidor remoto'; foi necessario executar a coleta com permissao de rede.
- O portal nao expunha links diretos para CSV por deputado; os detalhes eram carregados por modal/iframe via JavaScript.
- O endpoint mensal agregado continha linhas sem deputado, insuficientes para o filtro obrigatorio por parlamentar.
- Nenhuma biblioteca de dashboard estava instalada inicialmente; foi criado um ambiente virtual .venv.

## Erros e ajustes encontrados nos arquivos CSV/dados
- A primeira linha dos CSVs mensais agregados e vazia no formato ;;; antes do cabecalho real.
- O separador dos CSVs e ponto e virgula.
- Os valores monetarios usam formato brasileiro, por exemplo 6.516,55, exigindo conversao para numero.
- Existem valores negativos, preservados na base por representarem anulacoes ou estornos.
- Os CSVs mensais agregados possuem linhas sem DEPUTADO preenchido.
- O portal contem erros evidentes de digitacao em nomes de deputados, normalizados apenas na base final do dashboard.

## Normalizacoes de nomes aplicadas
- DEP ALCIDERS FERNANDES -> DEP ALCIDES FERNANDES
- DEP ALMIIR BIE -> DEP ALMIR BIE
- DEP ALMIR B -> DEP ALMIR BIE
- DEP ALYSSON AGUYIAR -> DEP ALYSSON AGUIAR
- Variacao indevida do nome de Carmelo Neto -> DEP CARMELO NETO
- DEP EMIILA PESSOA -> DEP EMILIA PESSOA
- DEP EMILA PESSOA -> DEP EMILIA PESSOA
- DEP FIRMO CAMUCA -> DEP FIRMO CAMURCA
- DEP GUILHERME BISMARK -> DEP GUILHERME BISMARCK
- DEP MISSISAS DIAS -> DEP MISSIAS DIAS
- DEP SERGIO AHUIAR -> DEP SERGIO AGUIAR

## Resumo quantitativo
- Registros na base final: 4219
- Deputados unicos na base final normalizada: 58
- Nomes originais distintos antes da normalizacao: 68
- Paginas HTML de detalhe salvas: 617
- Registros com valor negativo: 196

### Coleta por mes
| Mes | Deputados encontrados | Paginas de detalhe | Registros consolidados |
| --- | ---: | ---: | ---: |
| 01/2025 | 47 | 47 | 208 |
| 02/2025 | 51 | 51 | 411 |
| 03/2025 | 50 | 50 | 372 |
| 04/2025 | 49 | 49 | 328 |
| 05/2025 | 46 | 46 | 272 |
| 06/2025 | 51 | 51 | 335 |
| 07/2025 | 48 | 48 | 303 |
| 08/2025 | 55 | 55 | 474 |
| 09/2025 | 53 | 53 | 321 |
| 10/2025 | 58 | 58 | 405 |
| 11/2025 | 56 | 56 | 406 |
| 12/2025 | 53 | 53 | 384 |

### Comparacao entre CSV mensal e detalhe por deputado
| Mes | Linhas no CSV mensal | Linhas com deputado preenchido | Linhas no detalhe por deputado |
| --- | ---: | ---: | ---: |
| 01/2025 | 565 | 208 | 208 |
| 02/2025 | 1234 | 411 | 411 |
| 03/2025 | 874 | 372 | 372 |
| 04/2025 | 686 | 328 | 328 |
| 05/2025 | 284 | 272 | 272 |
| 06/2025 | 340 | 335 | 335 |
| 07/2025 | 308 | 303 | 303 |
| 08/2025 | 478 | 474 | 474 |
| 09/2025 | 322 | 321 | 321 |
| 10/2025 | 408 | 405 | 405 |
| 11/2025 | 412 | 406 | 406 |
| 12/2025 | 388 | 384 | 384 |

## Arquivos entregues
- streamlit_app.py: dashboard Streamlit.
- requirements.txt: dependencias do projeto.
- scripts/download_vdp_2025.py: coleta reproduzivel.
- scripts/prepare_vdp_dashboard_data.py: tratamento da base.
- dados/processed/vdp_2025_dashboard.csv: base final para visualizacao.
- dados/processed/vdp_2025_por_deputado.csv: consolidado extraido dos detalhes.
- dados/processed/vdp_2025_manifest.json: manifesto de coleta.
- docs/ajustes_dados.md: documentacao resumida de ajustes.
- docs/relatorio_dashboard_vdp_2025.pdf: este relatorio.

## Decisao tecnica
Streamlit foi escolhido em vez de Flask por ser mais direto para paineis exploratorios: filtros, tabelas, download e graficos interativos exigem menos infraestrutura e menos codigo. Para o volume atual de 4.219 registros, carregar a base em memoria e suficiente.
