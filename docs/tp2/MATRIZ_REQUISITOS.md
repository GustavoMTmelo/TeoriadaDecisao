# Matriz de requisitos — Entrega 2

Fontes E/A5/A6/F/R definidas em [AUDITORIA.md](AUDITORIA.md). Situação em 15/10/2026, antes da implementação. `P` = pronto para reutilização no escopo indicado; `R` = parcialmente reutilizável; `A` = ausente. Uma linha pronta não certifica a entrega inteira. IDs de issues são locais, definidos em [BACKLOG.md](BACKLOG.md).

**Atualização 18/10/2026:** os estados da tabela abaixo são o diagnóstico
histórico. TP2-01 a TP2-12B foram implementadas; o estado atual por tarefa e
suas evidências estão no [backlog](BACKLOG.md) e no
[registro 07–12](EXECUCAO_07_12.md). E08–E11, D02–D06 e D08 têm infraestrutura
implementada/testada; E12/E13 ainda exigem executar a campanha oficial TP2-13.
Figuras, análise e relatório cumulativo TP2-14 a TP2-17 seguem pendentes.

## Exigências explícitas do enunciado e correções recebidas

| ID | Requisito | Origem | Artefato/arquivos | Estado | Validação | Issues |
|---|---|---|---|---|---|---|
| E01 | Incorporar e corrigir etapas anteriores; relatório único cumulativo | E p. 2, Formato; p. 5, Relatório | `relatorio.tex/pdf`, código TP1 atualizado | R | Revisão das seções antigas e novas no mesmo PDF | TP2-03, TP2-04, TP2-05, TP2-15, TP2-17 |
| E02 | Instruções, dependências, parâmetros e organização suficientes para reproduzir | E p. 2, Formato | README, requirements, configurações e manifesto | R | Executar instruções em ambiente limpo | TP2-01, TP2-11, TP2-17 |
| E03 | Manter parâmetros, variáveis, três objetivos e restrições originais | E pp. 1–3, i(a–f); anexo pp. 6–8; cumulatividade | `sol_inicial.py`, relatório §1, avaliador | R | Dados do anexo; custo/massa/teores; nenhuma pilha faltante | TP2-02, TP2-06, TP2-15 |
| E04 | Usar VNS/GVNS do item ii para ambas as abordagens | E p. 4, iv(b) | `vns.py`, `busca.py`, dois escalares | R | Integração exercita SHAKE, VND e N1/N2/N3 nos dois métodos | TP2-04, TP2-08, TP2-09, TP2-10, TP2-12 |
| E05 | Preservar representação, construtiva, ≥3 vizinhanças e política de inviabilidade justificada | E pp. 2–3, ii(a–d) | `sol_inicial.py`, `vizinhancas.py`, `busca.py`, relatório | R | Operadores reais sem mutação, compatibilidade; N3 altera ambas e não permuta | TP2-02, TP2-04, TP2-08, TP2-15 |
| E06 | Resultados TP1: 5 rodadas por objetivo, valores finais, min/std/max | E p. 3, iii(a–b), cumulatividade p. 2 | Registros TP1 e tabela cumulativa | R | 15 registros individuais; estatísticas só de finais válidos, falhas visíveis | TP2-03, TP2-05, TP2-06, TP2-15 |
| E07 | Preservar 5 curvas sobrepostas por objetivo e figura da melhor solução | E p. 3, iii(c–d), cumulatividade | 6 figuras TP1 e dados geradores | R | Figuras regeneradas das novas composições/históricos | TP2-05, TP2-06, TP2-15 |
| E08 | Formular soma ponderada com os três objetivos | E p. 4, iv(a) | `escalarizacoes.py`, relatório | A | Fórmula corresponde à implementação e pesos válidos | TP2-09, TP2-15 |
| E09 | Formular ε-restrito com os três objetivos | E p. 4, iv(a) | `escalarizacoes.py`, relatório | A | Objetivo principal e dois tetos; restrições originais preservadas | TP2-10, TP2-15 |
| E10 | Normalizar antes da combinação ou definição de ε usando TP1 | E p. 4, iv(a) | `normalizacao.py`, referências, tabela cruzada | A | Referências rastreáveis a soluções TP1 viáveis, escalas congeladas | TP2-06, TP2-07, TP2-15 |
| E11 | Diferentes configurações e justificativa dos pesos e ε | E pp. 4–5, códigos e relatório | `configs/tp2.json`, relatório | A | Listas completas, não só diagonal ε; justificativa da resolução | TP2-09, TP2-10, TP2-11, TP2-15 |
| E12 | Cinco execuções de cada abordagem escalar | E p. 4, iv(c); A6 p. 35 esclarece varreduras | `experimentos.py`, manifesto, resultados | A | 5 varreduras × todas as configurações de cada método | TP2-11, TP2-13 |
| E13 | Reunir não dominadas obtidas nas cinco execuções | E p. 4, iv(c) | `pareto.py`, arquivos por repetição e método | A | Filtrar 3 objetivos antes de projetar; revalidar e preservar origem | TP2-08, TP2-12, TP2-13 |
| E14 | Projeções f1×f2, f1×f3, f2×f3 separadas por abordagem | E p. 4, iv(c) | `figuras_tp2.py`, seis painéis | A | 2 métodos × 3 pares, eixos/unidades/legendas corretos | TP2-14 |
| E15 | Cores/símbolos identificam repetições; discutir regiões similares | E p. 4, iv(c) | Figuras e análise | A | Mesma identidade visual das 5 repetições; dados sustentam texto | TP2-14, TP2-16 |
| E16 | Entregar código atualizado, normalização, varreduras, Pareto, tabelas e figuras | E pp. 4–5, Códigos | Pacote executável e fontes de resultados | R | Checklist de arquivos e execução sem editar resultados manualmente | TP2-11, TP2-13, TP2-14, TP2-17 |
| E17 | Explicar método, pseudocódigo, inviabilidade, aceitação, parada, parâmetros e experimentos | E p. 4, relatório TP1; p. 5, relatório TP2 | `relatorio.tex` e dados de configuração | R | Traçar pseudocódigo contra código e contratos | TP2-04, TP2-08, TP2-11, TP2-15 |
| E18 | Comparar abordagens, compromissos e variabilidade | E p. 5, Relatório | Tabelas, análises, métricas descritivas | A | Comparação no mesmo espaço e com orçamento documentado | TP2-13, TP2-14, TP2-16 |
| F01 | Penalização não equivale a normalização/garantia de viabilidade | F, primeiro ponto | Busca, normalização, texto | R | Teste separa valor escalar, violações e validação final | TP2-02, TP2-03, TP2-07, TP2-08, TP2-15 |
| F02 | Verificar e registrar solução final de cada execução | F, segundo ponto | Logs estruturados e resumo | A | Rodada inválida não passa por válida nem desaparece da tabela | TP2-05, TP2-11, TP2-12 |
| F03 | Manter melhor viável separadamente e retorná-la quando existir | F, terceiro ponto; A6 p. 34 | Incumbente viável e arquivo | A | Viável observada mesmo quando não aceita pela trajetória é preservada | TP2-03, TP2-08, TP2-12 |
| F04 | Alinhar VND real e descrição após cinco reinícios | F, quarto ponto; R §6.4 | `vns.py`, `busca.py`, relatório | R | Sequência controlada: melhoria em N2 após limite mantém N2 | TP2-04, TP2-15 |

## Decisões de implementação, não novas exigências da professora

| ID | Decisão proposta | Motivação/origem | Artefato | Estado | Validação | Issues |
|---|---|---|---|---|---|---|
| D01 | Preservar dicionário de listas e dados atuais | Reuso de E03–E05 | Contratos e avaliador | P | Adaptadores mantêm resultados da construtiva | TP2-01, TP2-02 |
| D02 | Min–max empírico sobre 15 finais TP1 viáveis; matriz cruzada | E10; A5 p. 9; escolha de referências é do grupo | Referências versionadas | A | Cada extremo aponta a run_id e composição; sem clipping | TP2-06, TP2-07 |
| D03 | 16 pesos (malha H=4 e centro), 16 pares ε (4×4) | E11, A6 p. 31 apenas exemplifica níveis | Configuração | A | 16 únicos por método; contagem 160 buscas TP2 | TP2-09, TP2-10, TP2-11 |
| D04 | Priorizar viabilidade no TP2; conservar penalidade histórica no TP1 corrigido | F01/F03; A6 p. 34 permite políticas | Comparador e avaliador | A | Regras transitivas e viabilidade ε individual | TP2-08, TP2-12 |
| D05 | Mesmo teto de avaliações por subproblema; sementes derivadas estáveis | Comparação justa e E02/E18 | Manifesto | A | Teto respeitado em laços internos e agenda independente da ordem | TP2-08, TP2-11, TP2-13 |
| D06 | Arquivar candidatos viáveis observados, não só finais | F03/E13 | Pareto por repetição/método | A | Rejeição escalar não apaga candidato não dominado | TP2-08, TP2-12 |
| D07 | Testes unitários, integração e revalidação independente | Forma de comprovar requisitos; enunciado não impõe framework | `tests/` | R | Casos sintéticos e arquivos completos passam | TP2-02 a TP2-12, TP2-17 |
| D08 | CSV+JSON, hashes de entrada e versão de software | Reprodutibilidade E02 | `results/`, manifesto | A | Releitura não altera números ou composição | TP2-05, TP2-11, TP2-13 |

## Itens fora da obrigação desta etapa

| Item | Classificação e origem | Tratamento |
|---|---|---|
| Apresentação oral TP2 | **Dispensada explicitamente**, E p. 5 | Nenhuma issue obrigatória de slides; revisar slides antigos apenas se reutilizados |
| Streamlit e decisão AHP/ELECTRE/PROMETHEE, ≥4 critérios | Entrega 3, E pp. 5–6 | Fora do backlog TP2; guardar composições prepara reaproveitamento |
| NSGA-II/MOEA, população evolutiva | Não exigidos; não substituem E04/E08/E09 | Fora do escopo |
| Hipervolume, IGD, testes estatísticos inferenciais | Métricas específicas não exigidas | Opcionais, após concluir E18; IGD precisaria de referência apropriada |
| Busca adaptativa de pesos/ε, warm start, cálculo incremental | Melhorias opcionais | Adiar; podem enviesar comparação e ampliar risco antes de 18/10 |
| Prova de Pareto global/ótimo exato | Não exigida nem demonstrada pelo GVNS | Usar “aproximação não dominada entre soluções encontradas” |
| Testes existentes das vizinhanças | Parcialmente reutilizáveis; não provam GVNS completo | Mantê-los e cobrir variantes rápidas |

## Revisão de cobertura

Todos os 18 requisitos E e os 4 pontos F têm issue responsável. A apresentação foi tratada explicitamente como não aplicável. O conjunto completo de obrigações está mapeado; **o atendimento só ocorrerá após implementar, executar e validar**. Dúvidas remanescentes do grupo estão no [plano](PLANEJAMENTO.md), sem transformar opções em obrigações.
