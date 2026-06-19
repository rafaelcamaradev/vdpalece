# Ajustes identificados nos dados da VDP 2025

Fonte: https://transparencia.al.ce.gov.br/despesas/verba-desempenho-parlamentar

## Coleta

- Os CSVs mensais agregados foram baixados de `csv?ano=2025&mes=MM`, para os meses `01` a `12`.
- Para garantir a associacao correta de cada despesa ao parlamentar, tambem foram baixadas as paginas de detalhe por deputado e mes, usando a rota `detalhes?codigo=...`.
- O codigo de detalhe do portal codifica a combinacao `ANO_MES_DEPUTADO`.

## Ajustes necessarios

- Remover a primeira linha vazia dos CSVs mensais agregados (`;;;`) antes de ler o cabecalho real.
- Ler os arquivos com separador `;`.
- Converter valores monetarios do formato brasileiro para numero: exemplo `1.234,56` para `1234.56`.
- Preservar valores negativos, pois representam anulacoes ou estornos publicados pelo portal.
- Preferir os detalhes por deputado para o dashboard, porque os CSVs mensais agregados possuem linhas sem `DEPUTADO` preenchido.
- Normalizar erros evidentes de digitacao nos nomes dos deputados para evitar filtros duplicados.

## Normalizacoes aplicadas

| Nome no portal | Nome usado no dashboard |
| --- | --- |
| DEP ALCIDERS FERNANDES | DEP ALCIDES FERNANDES |
| DEP ALMIIR BIE | DEP ALMIR BIE |
| DEP ALMIR B | DEP ALMIR BIE |
| DEP ALYSSON AGUYIAR | DEP ALYSSON AGUIAR |
| Variacao indevida do nome de Carmelo Neto | DEP CARMELO NETO |
| DEP EMIILA PESSOA | DEP EMILIA PESSOA |
| DEP EMILA PESSOA | DEP EMILIA PESSOA |
| DEP FIRMO CAMUCA | DEP FIRMO CAMURCA |
| DEP GUILHERME BISMARK | DEP GUILHERME BISMARCK |
| DEP MISSISAS DIAS | DEP MISSIAS DIAS |
| DEP SERGIO AHUIAR | DEP SERGIO AGUIAR |

## Arquivos gerados

- `dados/raw/vdp_2025_MM.csv`: CSV mensal agregado original do portal.
- `dados/raw/detalhes/YYYY_MM/*.html`: HTML bruto de detalhe por deputado e mes.
- `dados/processed/vdp_2025_por_deputado.csv`: consolidado extraido das paginas de detalhe.
- `dados/processed/vdp_2025_dashboard.csv`: base tratada para visualizacao.
- `dados/processed/vdp_2025_manifest.json`: resumo da coleta.
