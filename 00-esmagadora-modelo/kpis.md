# Ficha de KPIs da Esmagadora Modelo

Os 15 indicadores usados nas análises do portfólio, com definição, fórmula, fonte do dado e a armadilha de interpretação mais comum de cada um. Indicador sem definição escrita vira discussão: cada área calcula de um jeito e a reunião gasta tempo descobrindo por que os números não batem.

As faixas misturam a referência do setor e a minha experiência em fábrica com os valores da base fictícia; onde as duas diferem, as duas aparecem.

## Resumo

| Área | KPI | Fórmula | Unidade | Sentido | Faixa típica |
|---|---|---|---|---|---|
| Produção | [Soja esmagada](#soja-esmagada) | leitura da balança de fluxo; conferência: estoque inicial + recebido − estoque final | t | ↑ | 1.200 a 1.600 t/dia |
| Produção | [Produtividade](#produtividade) | soja esmagada (t) ÷ hora trabalhada (h) | t/h | ↑ | 54 a 63 t/h (1.300 a 1.500 t/dia rodando 24 h); base: cerca de 61 t/h |
| Produção | [Rendimento de óleo](#rendimento-de-óleo) | Produção de óleo (t) ÷ soja esmagada (t) | % | ↑ | 20% a 21% |
| Produção | [Rendimento de farelo](#rendimento-de-farelo) | Produção de farelo (t) ÷ soja esmagada (t) | % | faixa ideal | 72% a 76% |
| Qualidade | [Óleo residual no farelo branco (LEX)](#óleo-residual-no-farelo-branco-lex) | % de óleo no farelo na saída do extrator | % | ↓ | meta 0,6% |
| Qualidade | [Proteína do farelo](#proteína-do-farelo) | % de proteína na análise | % | faixa ideal | meta 46% |
| Qualidade | [Umidade do farelo](#umidade-do-farelo) | % de umidade na análise | % | faixa ideal | 12% a 14% |
| Utilidades | [Índice de hexano](#índice-de-hexano) | hexano consumido (L) ÷ soja esmagada (t) | L/t | ↓ | Referência do setor cerca de 1,0 L/t; até 0,8 é excelente; acima de 1,5 é alto |
| Utilidades | [Consumo de vapor](#consumo-de-vapor) | vapor (kg) ÷ soja esmagada (t) | kg/t | ↓ | cerca de 270 kg/t |
| Utilidades | [Consumo de energia](#consumo-de-energia) | energia (kWh) ÷ soja esmagada (t) | kWh/t | ↓ | cerca de 45 kWh/t |
| Manutenção | [Disponibilidade](#disponibilidade) | horas trabalhadas ÷ (24 h − parada programada) | % | ↑ | meta ≥ 95% |
| Manutenção | [Horas paradas por categoria](#horas-paradas-por-categoria) | soma de duracao_min ÷ 60, por motivo | horas | ↓ | depende do mês |
| Recebimento | [Desconto de classificação](#desconto-de-classificação) | desconto (t) ÷ peso líquido (t) | % | ↓ | cerca de 1% do peso líquido (out/2022: 33,59 t de 3.118 t = 1,1%); limites de classificação: umidade 14%, impureza 1%, avariados 8% |
| Estoque | [Cobertura de estoque de soja](#cobertura-de-estoque-de-soja) | (estoque − mínimo) ÷ esmagamento médio diário | dias | faixa ideal | mínimo de 5 dias para retomar a operação (regra da base); acima de cerca de 15 dias é capital parado e risco de qualidade |
| Expedição | [OTIF da expedição](#otif-da-expedição) | entregas no prazo e completas ÷ total de entregas | % | ↑ | ≥ 95% |

Sentido: ↑ quanto maior, melhor; ↓ quanto menor, melhor; faixa ideal quando passar do ponto também custa dinheiro.

## Produção

### Soja esmagada

- **Definição:** Quanto de soja a fábrica processou no período.
- **Fórmula:** leitura da balança de fluxo; conferência: estoque inicial + recebido − estoque final (t)
- **Fonte na fábrica:** Balança de fluxo
- **Na base:** fato_producao (soja_esmagada_t)
- **Faixa típica:** 1.200 a 1.600 t/dia
- **Armadilha:** O total do mês não diz se a fábrica rodou cheia ou parou muito. Duas fábricas com o mesmo total podem ter disponibilidades bem diferentes. Olhar sempre junto com a disponibilidade e a produtividade.

### Produtividade

- **Definição:** Quanto a fábrica esmaga por hora de operação.
- **Fórmula:** soja esmagada (t) ÷ hora trabalhada (h) (t/h)
- **Fonte na fábrica:** balança de fluxo e controle de paradas
- **Na base:** fato_producao (soja_esmagada_t, horas_trabalhadas)
- **Faixa típica:** 54 a 63 t/h (1.300 a 1.500 t/dia rodando 24 h); base: cerca de 61 t/h
- **Armadilha:** Dia de partida derruba o t/h, porque a fábrica volta devagar; parada lançada com horas erradas muda o denominador e distorce o resultado; e t/h alto não quer dizer dia bom: se a fábrica ficou muito tempo parada, a produção total pode ter sido baixa. Olhar sempre junto com a disponibilidade.

### Rendimento de óleo

- **Definição:** Quanto óleo degomado é produzido para cada tonelada de soja esmagada.
- **Fórmula:** Produção de óleo (t) ÷ soja esmagada (t) (%)
- **Fonte na fábrica:** medidor de vazão na saída da degomagem
- **Na base:** fato_producao (oleo_degomado_t, soja_esmagada_t)
- **Faixa típica:** 20% a 21%
- **Armadilha:** Depende do óleo que a soja traz. Soja com menos óleo derruba o rendimento sem ser culpa da fábrica. Comparar com o teor de óleo da soja industrializada antes de cobrar a operação

### Rendimento de farelo

- **Definição:** Quanto farelo é produzido para cada tonelada de soja esmagada.
- **Fórmula:** Produção de farelo (t) ÷ soja esmagada (t) (%)
- **Fonte na fábrica:** farelo produzido pela balança de fluxo
- **Na base:** fato_producao (farelo_produzido_t, soja_esmagada_t)
- **Faixa típica:** 72% a 76%
- **Armadilha:** Subir pode ser ruim. Mais óleo ficando no farelo ou mais umidade aumentam o peso do farelo e “melhoram” o rendimento enquanto a fábrica perde dinheiro

## Qualidade

### Óleo residual no farelo branco (LEX)

- **Definição:** Quanto óleo fica no farelo depois da lavagem no extrator (óleo perdido).
- **Fórmula:** % de óleo no farelo na saída do extrator (%)
- **Fonte na fábrica:** análise laboratorial
- **Na base:** fato_lab_farelo (residual_farelo_branco_pct)
- **Faixa típica:** meta 0,6%
- **Armadilha:** É análise por amostra, então um resultado fora não é tendência. Amostra mal coletada gera falso alarme. A média do dia esconde o turno ruim

### Proteína do farelo

- **Definição:** Teor de proteína do farelo, comparado à especificação comercial.
- **Fórmula:** % de proteína na análise (%)
- **Fonte na fábrica:** análise laboratorial
- **Na base:** fato_lab_farelo (proteina_pct)
- **Faixa típica:** meta 46%
- **Armadilha:** A média esconde as análises fora da especificação. Acima da especificação é proteína dada de graça ao cliente; abaixo é reclamação. Olhar o % de análises fora, não só a média

### Umidade do farelo

- **Definição:** Teor de umidade do farelo final.
- **Fórmula:** % de umidade na análise (%)
- **Fonte na fábrica:** análise laboratorial
- **Na base:** fato_lab_farelo (umidade_pct)
- **Faixa típica:** 12% a 14%
- **Armadilha:** Umidade alta “rende” peso no farelo vendido, mas dilui a proteína e põe a conservação em risco. Umidade baixa demais é energia gasta à toa na secagem

## Utilidades

### Índice de hexano

- **Definição:** Quanto solvente é perdido no processo para cada tonelada de soja esmagada.
- **Fórmula:** hexano consumido (L) ÷ soja esmagada (t) (L/t)
- **Fonte na fábrica:** Medição manual do nível do tanque de hexano; soja esmagada pela balança de fluxo
- **Na base:** fato_producao (hexano_l, soja_esmagada_t)
- **Faixa típica:** Referência do setor cerca de 1,0 L/t; até 0,8 é excelente; acima de 1,5 é alto
- **Armadilha:** Dia de partida infla o índice; medição manual do tanque mistura períodos (comparar o mês, não o dia isolado)

### Consumo de vapor

- **Definição:** Quantos kg de vapor são consumidos por tonelada de soja esmagada.
- **Fórmula:** vapor (kg) ÷ soja esmagada (t) (kg/t)
- **Fonte na fábrica:** medidor de vazão de vapor na saída da caldeira
- **Na base:** fato_producao (vapor_kg, soja_esmagada_t)
- **Faixa típica:** cerca de 270 kg/t
- **Armadilha:** Parte do consumo é fixa. Em dia de pouca operação, o kg/t sobe sem ninguém ter piorado. Separar os dias de partida antes de comparar

### Consumo de energia

- **Definição:** Quantos kWh de energia são consumidos por tonelada de soja esmagada.
- **Fórmula:** energia (kWh) ÷ soja esmagada (t) (kWh/t)
- **Fonte na fábrica:** Medição na unidade distribuidora (subestação) da fábrica
- **Na base:** fato_producao (energia_kwh, soja_esmagada_t)
- **Faixa típica:** cerca de 45 kWh/t
- **Armadilha:** Mesma armadilha do vapor. Comparar sempre por tonelada, nunca o total, porque o total cai junto com a produção e parece melhora

## Manutenção

### Disponibilidade

- **Definição:** % do tempo em que a fábrica deveria rodar e de fato rodou (paradas programadas fora da conta).
- **Fórmula:** horas trabalhadas ÷ (24 h − parada programada) (%)
- **Fonte na fábrica:** Controle de operação
- **Na base:** fato_producao (horas_trabalhadas), fato_paradas, dim_motivo_parada (tipo)
- **Faixa típica:** meta ≥ 95%
- **Armadilha:** Classificar falta de soja ou falta de espaço como parada programada esconde a maior perda do mês e infla o indicador. Só entra como programada o que foi planejado para a fábrica parar de propósito

### Horas paradas por categoria

- **Definição:** Tempo de fábrica parada em cada motivo de parada.
- **Fórmula:** soma de duracao_min ÷ 60, por motivo (horas)
- **Fonte na fábrica:** Controle de paradas
- **Na base:** fato_paradas + dim_motivo_parada
- **Faixa típica:** depende do mês
- **Armadilha:** Motivo genérico (“outras paradas”) deixa o indicador sem uso. Se a maior barra do gráfico for “outros”, a classificação falhou, não a fábrica

## Recebimento

### Desconto de classificação

- **Definição:** % do peso recebido descontado por qualidade fora do padrão (umidade, impureza, avariados).
- **Fórmula:** desconto (t) ÷ peso líquido (t) (%)
- **Fonte na fábrica:** Boletim recebimento
- **Na base:** fato_recebimento (desconto_t, peso_liquido_t)
- **Faixa típica:** cerca de 1% do peso líquido (out/2022: 33,59 t de 3.118 t = 1,1%); limites de classificação: umidade 14%, impureza 1%, avariados 8%
- **Armadilha:** A média de todos os fornecedores esconde o fornecedor ruim. Safra ruim sobe o desconto de todo mundo junto, e isso não é culpa de um fornecedor. Comparar cada fornecedor com a média do mesmo período

## Estoque

### Cobertura de estoque de soja

- **Definição:** Quantos dias a fábrica consegue rodar só com a soja que está no silo.
- **Fórmula:** (estoque − mínimo) ÷ esmagamento médio diário (dias)
- **Fonte na fábrica:** Estoque de fechamento (balança e medição do silo) e esmagamento programado
- **Na base:** fato_producao (estoque_soja_t_fechamento, soja_esmagada_t)
- **Faixa típica:** mínimo de 5 dias para retomar a operação (regra da base); acima de cerca de 15 dias é capital parado e risco de qualidade
- **Armadilha:** O resultado muda conforme a média de esmagamento usada (últimos dias ou programada). Esquecer o estoque mínimo, que não dá para usar, superestima a cobertura. Ignorar a soja que ainda vai chegar subestima

## Expedição

### OTIF da expedição

- **Definição:** % das entregas feitas no prazo combinado e na quantidade pedida.
- **Fórmula:** entregas no prazo e completas ÷ total de entregas (%)
- **Fonte na fábrica:** a programação de carregamentos ou os pedidos de venda (no SAP, módulo SD)
- **Na base:** Não é possível calcular: a base não tem data prometida nem quantidade pedida. Com fato_expedicao, só se mede o volume expedido.
- **Faixa típica:** ≥ 95%
- **Armadilha:** Sem a regra escrita do que é “no prazo” (dia exato ou janela) e “completo”, cada área calcula de um jeito. Atraso causado pelo cliente ou pela transportadora derruba o indicador da fábrica sem culpa dela

## Regra de parada programada (usada na disponibilidade)

Entra como parada programada só o que foi planejado para a fábrica parar de propósito: manutenção preventiva ou programada e a parada de entressafra prevista no plano anual. Não entram falta de matéria-prima, falta de espaço no armazém, queda de energia externa e falha da geração própria. Classificar falta de soja como programada esconde a maior perda do mês.
