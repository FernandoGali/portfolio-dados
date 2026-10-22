# Esmagadora Modelo: base de dados fictícia de esmagamento de soja

Base usada em todo o roadmap de Analista de Dados. Simula uma unidade de esmagamento de soja de 01/01/2022 a 30/09/2026: recebimento de soja, armazenagem em silo, esmagamento, produção de farelo e óleo degomado, paradas, consumo de utilidades, laboratório e expedição.

**Todos os dados são fictícios.** Nomes de fornecedores, clientes, números e eventos foram gerados por script. A estrutura foi inspirada em um boletim diário de produção típico do setor, que não faz parte deste repositório.

## Estrutura

```
esmagadora/
├── dados_limpos/            CSV padrão (UTF-8, separador vírgula, decimal ponto)
├── esmagadora_modelo.xlsx   As mesmas tabelas limpas, uma por aba (Excel e Power BI)
├── dados_sujos/             CSV padrão Brasil (separador ;, decimal vírgula, Windows-1252), com problemas reais
│   └── apontamentos_mensais/  12 arquivos de 2025 para consolidar no Power Query
├── _gabarito/               Não abra antes da hora (ver abaixo)
├── gerar_dados.py           Gera a base limpa (seed fixa: sempre o mesmo resultado)
├── sujar_dados.py           Gera a versão suja a partir da limpa
└── validar.py               Confere balanço de massa, estoques e faixas dos KPIs
```

**Qual usar em cada fase**

| Fase | Base |
|---|---|
| 2. Excel e Power Query | `esmagadora_modelo.xlsx` + `apontamentos_mensais/` |
| 3. SQL | `dados_limpos/` carregado no PostgreSQL (banco `fabrica_modelo`) |
| 4. Power BI | PostgreSQL (views do CP2) |
| 5 e 6. Python e coleta | `dados_limpos/` e depois `dados_sujos/` |
| 7. Limpeza | `dados_sujos/`, conferindo o resultado contra `dados_limpos/` |
| 8 em diante | base limpa resultante da Fase 7 |

**Gabarito:** a pasta `_gabarito/` é gerada pelo `sujar_dados.py` e fica fora do repositório (está no `.gitignore`).

## Modelo de dados

Esquema estrela: tabelas fato (eventos e medições) ligadas a tabelas dimensão (cadastros).

| Tabela | Grão | Linhas (aprox.) | Liga com |
|---|---|---|---|
| `fato_producao` | 1 dia | 1.700 | `dim_calendario` (data) |
| `fato_paradas` | 1 evento de parada | 1.300 | `dim_calendario`, `dim_motivo_parada`, `dim_equipamento` |
| `fato_lab_farelo` | 1 análise por turno | 4.300 | `dim_calendario` |
| `fato_lab_soja_industrializada` | 1 dia | 1.600 | `dim_calendario` |
| `fato_recebimento` | 1 carga (ticket da balança) | 51.000 | `dim_calendario`, `dim_fornecedor` |
| `fato_expedicao` | 1 carregamento | 51.000 | `dim_calendario`, `dim_cliente` |
| `dim_calendario` | 1 dia | 1.734 | |
| `dim_motivo_parada` | 1 motivo | 11 | |
| `dim_equipamento` | 1 equipamento | 17 | |
| `dim_fornecedor` | 1 fornecedor | 160 | |
| `dim_cliente` | 1 cliente | 15 | |

## Dicionário de dados

### fato_producao
| Coluna | Tipo | Unidade | Descrição |
|---|---|---|---|
| data | data | | Dia de produção |
| soja_esmagada_t | decimal | t | Soja processada no dia |
| horas_trabalhadas | decimal | h | Horas com a fábrica rodando (24 menos as paradas) |
| farelo_produzido_t | decimal | t | Farelo produzido |
| oleo_degomado_t | decimal | t | Óleo degomado produzido |
| hexano_l | inteiro | L | Hexano consumido (perdido) no processo |
| vapor_kg | inteiro | kg | Vapor consumido |
| energia_kwh | inteiro | kWh | Energia elétrica consumida |
| estoque_soja_t_fechamento | decimal | t | Estoque de soja no silo no fim do dia (já descontada a classificação) |
| estoque_farelo_t_fechamento | decimal | t | Estoque de farelo no fim do dia (capacidade: 28.000 t) |
| estoque_oleo_t_fechamento | decimal | t | Estoque de óleo no fim do dia (capacidade: 6.000 t) |

### fato_paradas
| Coluna | Tipo | Descrição |
|---|---|---|
| id_parada | texto | Identificador do evento |
| data | data | Dia da parada |
| hora_inicio | texto (hh:mm) | Início da parada |
| turno | texto | I (07-15h), II (15-23h), III (23-07h) |
| id_motivo | inteiro | Chave para `dim_motivo_parada` |
| id_equipamento | inteiro | Chave para `dim_equipamento` (vazio quando a parada não é de um equipamento) |
| duracao_min | inteiro | Duração em minutos |
| descricao | texto | Descrição livre, como escrita no boletim |

### fato_lab_farelo
| Coluna | Unidade | Descrição |
|---|---|---|
| id_analise, data, turno | | Identificação da amostra |
| residual_farelo_branco_pct | % | Óleo residual no farelo após a extração (quanto menor, melhor; meta 0,60%) |
| residual_pellets_pct | % | Óleo residual nos pellets de casca |
| umidade_pct | % | Umidade do farelo |
| proteina_pct | % | Proteína do farelo (especificação comercial: cerca de 46%) |
| fibra_pct | % | Fibra |
| silica_pct | % | Sílica (indicador de terra e impureza) |
| oleo_casca_pct | % | Óleo na casca (analisado nos turnos I e II) |
| atividade_ureatica | ΔpH | Indica se o farelo foi bem tostado (alta = cru; baixa demais = queimado) |
| proteina_soluvel_pct | % | Proteína solúvel em KOH (analisada só no turno II) |

### fato_lab_soja_industrializada
Qualidade média da soja que entrou no processo no dia: `proteina_pct`, `oleo_pct`, `umidade_pct`, `impureza_pct`, `avariados_pct`, `esverdeados_pct`.

### fato_recebimento
| Coluna | Unidade | Descrição |
|---|---|---|
| id_ticket | | Número do ticket da balança |
| data, hora_entrada | | Chegada do caminhão |
| id_fornecedor | | Chave para `dim_fornecedor` |
| peso_bruto_t, peso_liquido_t | t | Peso com e sem o caminhão |
| umidade_pct, impureza_pct, avariados_pct, esverdeados_pct | % | Classificação na entrada |
| proteina_pct, oleo_pct | % | Análise de composição |
| desconto_t | t | Desconto por classificação (umidade acima de 14%, impureza acima de 1%, avariados acima de 8%) |

### fato_expedicao
`id_expedicao`, `data`, `produto` (Farelo ou Óleo), `id_cliente`, `quantidade_t`.

### Dimensões
- `dim_calendario`: data, ano, mês, nome do mês, trimestre, semana ISO, dia da semana, período (Safra de fevereiro a julho, Entressafra no resto)
- `dim_motivo_parada`: motivo, tipo (Planejada ou Não planejada), área responsável
- `dim_equipamento`: tag, nome, setor (Recebimento, Preparação, Extração, Óleo, Farelo, Utilidades)
- `dim_fornecedor`: código, nome, tipo (Produtor, Cooperativa, Grupo), região
- `dim_cliente`: nome, segmento, produto que compra

## Fórmulas dos principais KPIs

| KPI | Fórmula | Faixa típica nesta base |
|---|---|---|
| Rendimento de óleo | óleo degomado / soja esmagada | 19,9% a 20,2% |
| Rendimento de farelo | farelo produzido / soja esmagada | cerca de 72,5% |
| Índice de hexano | hexano (L) / soja esmagada (t) | 1,5 a 2,1 L/t |
| Consumo de vapor | vapor (kg) / soja esmagada (t) | cerca de 270 kg/t |
| Consumo de energia | energia (kWh) / soja esmagada (t) | cerca de 45 kWh/t |
| Produtividade | soja esmagada / horas trabalhadas | cerca de 61 t/h |
| Disponibilidade | horas trabalhadas / 24 h | depende do mês |

Para recriar a base: `python gerar_dados.py` e depois `python sujar_dados.py`.
