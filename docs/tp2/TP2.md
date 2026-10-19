**PASSAGEM PARA O GRUPO  \|  18/10/2026**

# Case Cassotis - Onde estamos e como concluir o TP2

> **Atualização local:** prazo confirmado às **23:59 de 18/10/2026 (Brasília)**.
> Setup CPython 3.13.5. O usuário confirmou LaTeX em outro computador como
> ambiente de compilação final. A campanha oficial terminou e foi auditada:
> 160 buscas, 1.600.000 avaliações. Resultados, figuras e discussão foram
> desenvolvidos; compilação/revisão do PDF e envio ainda estão pendentes.
> Consulte o [registro atual](EXECUCAO_13_EM_ANDAMENTO.md) e o
> [checklist de fechamento](CHECKLIST_ENTREGA_TP2.md). O restante deste arquivo
> preserva a passagem original: estados de tarefas, caminhos do Henry e PRs
> abaixo são históricos, não o estado atual.

> **O código dos dois métodos e a infraestrutura de experimentos estão prontos e testados.** Ainda faltam a campanha oficial completa, as figuras, a análise comparativa e a atualização final do relatório. A Entrega 2 ainda não está pronta para envio.

### 1. Qual é o problema?

Devemos definir as receitas de **10 pilhas de minério**, movimentando caminhões de 2 kt. Uma solução informa quais minérios entram em cada pilha. É obrigatório respeitar massa, compatibilidade dos minérios, disponibilidade global e faixas de SiO₂ e Al₂O₃ por pilha.

Há três objetivos a **minimizar**: **f1**, custo total em R$; **f2**, soma dos desvios quadráticos de SiO₂ em relação aos alvos; **f3**, o mesmo para Al₂O₃. Os desvios têm unidade p.p.². Reduzir custo e melhorar ambas as qualidades pode exigir escolhas conflitantes.

O TP1 resolveu cada objetivo isoladamente. O **TP2 busca alternativas de compromisso** com soma ponderada e ε-restrito, reutilizando o GVNS do TP1. O resultado esperado é um conjunto de alternativas não dominadas, acompanhado de gráficos e análise; a escolha multicritério de uma ação fica para o TP3.

### 2. O que já temos como evidência?

**TP1 corrigido:** 15 execuções finais viáveis, composições recuperáveis, referências empíricas e seis figuras. **TP2:** tarefas internas TP2-07 a TP2-12B concluídas; 162 testes passaram, inclusive em checkout limpo. Uma campanha reduzida real confirmou busca, salvamento, auditoria e retomada.

| Termo | Significado neste projeto |
| --- | --- |
| Configuração / run | Um conjunto de pesos ou um par ε. Uma run é uma busca com essa configuração e uma semente. |
| Varredura / repetição | Percorre todas as 16 configurações de um método. São cinco varreduras por método: 2 × 5 × 16 = 160 runs oficiais. |
| Semente / Pareto | A semente reproduz os sorteios. Uma solução é não dominada quando nenhuma outra encontrada é tão boa em tudo e melhor em pelo menos um objetivo. |

Como ler: exigências e feedback; método implementado; acesso e arquivos; próximos passos executáveis; relatório e checklist de envio. A ordem das seções acompanha a versão em PDF.

## O que foi pedido e o que está atendido

As referências de página abaixo são as páginas físicas do enunciado oficial. Os IDs TP2-xx organizam o backlog do grupo; não são itens numerados pela professora.

| Exigência do enunciado | Situação e ação restante |
| --- | --- |
| Duas formulações com três objetivos e normalização baseada no TP1<br>**p. 4, iv(a)** | **Código pronto.** Normalização, soma ponderada e ε-restrito implementados. Falta escrever formulações e justificativas no relatório cumulativo (TP2-15). |
| Reutilizar o algoritmo do TP1 nas duas abordagens<br>**p. 4, iv(b)** | **Pronto e testado.** O núcleo comum usa construtiva, SHAKE, VND e N1/N2/N3 existentes. Falta descrever fielmente seu fluxo no relatório. |
| Cinco execuções por abordagem e reunião das não dominadas<br>**p. 4, iv(c)** | **Infraestrutura pronta; coleta oficial pendente.** Agenda de 160 runs e Pareto por repetição/método implementados. Executar e auditar TP2-13. |
| Três projeções por abordagem, identificando repetições<br>**p. 4, iv(c)** | **Pendente (TP2-14).** Gerar seis painéis: f1×f2, f1×f3 e f2×f3 para cada método, com cores/símbolos das cinco varreduras. |
| Código atualizado, tabelas/figuras e relatório cumulativo com comparação<br>**pp. 4-5, entregáveis** | **Parcial.** Código-base disponível; faltam gerador de figuras, análise dos resultados finais e relatório TP2 completo (TP2-14 a 17). |

### O feedback da professora foi tratado assim

| Ponto do feedback¹ | Correção feita / cuidado para o relatório |
| --- | --- |
| Pesos de penalidade não normalizam e não garantem viabilidade. | Normalização separada e viabilidade explícita. TP1 mantém penalidade histórica; TP2 prioriza viabilidade. Explicar a diferença. |
| Verificar a solução de cada execução. | Cada run guarda composição, três objetivos e validações; a leitura recalcula esses dados. Falhas aparecem explicitamente no resumo. |
| Guardar e devolver a melhor viável encontrada. | Observação anterior à aceitação, inclusive dentro da busca. A melhor viável é separada da trajetória e preservada mesmo ao acabar o orçamento. |
| Descrição do VND deve coincidir com o código. | Regra preservada e testada: após cinco reinícios, melhoria mantém a vizinhança atual; ausência de melhoria avança. Revisar o pseudocódigo. |

¹ Síntese do feedback registrado em AUDITORIA.md, não citação literal. A N3 recebeu avaliação positiva e foi preservada: altera duas posições e rejeita mera permutação interna.

> **Limites do escopo:** o enunciado dispensa apresentação oral no TP2 (p. 5). AHP/ELECTRE/PROMETHEE, quarto critério e seleção final pertencem ao TP3. Não são pendências desta entrega.

## Como a solução implementada funciona

### 1. Mesma escala para objetivos de magnitudes diferentes

Para cada objetivo j, usamos **g\<sub\>j\</sub\>(x) = \[f\<sub\>j\</sub\>(x) - a\<sub\>j\</sub\>\] / \[b\<sub\>j\</sub\> - a\<sub\>j\</sub\>\]**. Os extremos a e b vêm dos três objetivos recalculados nas 15 soluções finais viáveis do TP1, incluindo valores cruzados de buscas por outros objetivos.

| Objetivo | Mínimo empírico a | Máximo empírico b |
| --- | --- | --- |
| f1 (R$) | 60.300.000 | 65.840.000 |
| f2 (p.p.²) | 2,3727567955 | 6,7057453980 |
| f3 (p.p.²) | 1,4361688772 | 5,9951294968 |

Valores resumidos para leitura; usar a precisão completa de results/referencias\_tp1.json. São extremos observados, não ideal/nadir exatos. Novas soluções podem ter g\<0 ou g\>1: o código não trunca. Intervalos degenerados ou não finitos são rejeitados.

### 2. Dois métodos sobre o mesmo conjunto físico viável

**Soma ponderada:** minimiza w1·g1 + w2·g2 + w3·g3, com pesos não negativos e soma 1. A malha contém 15 triplas em passos de 0,25 cuja soma é 1, mais o centro (1/3,1/3,1/3): **16 configurações**.

**ε-restrito:** minimiza g1 (custo), impondo g2≤ε2 e g3≤ε3. Cada limite assume 0, 1/3, 2/3 ou 1: **16 pares cartesianos**, inclusive fora da diagonal. As faixas químicas de cada pilha continuam obrigatórias; limitar o desvio total não as substitui.

### 3. Busca, observação e não dominância

**Fluxo:** construtiva → SHAKE → VND → comparação e atualização → parada. A estrutura inválida é rejeitada. No TP2, uma viável é preferida a uma inviável; entre inviáveis, reduz-se a violação; entre viáveis, o escalar e seu desempate decidem. Empate completo mantém a incumbente.

Cada candidato avaliado é observado **antes de ser aceito ou rejeitado**. A melhor viável e o arquivo Pareto são separados da trajetória. O orçamento vale nos laços internos e conta a avaliação inicial e as repetidas. Qualidade e ε usam tolerância 10\<super\>-9\</super\>; pesos, 10\<super\>-12\</super\> na soma.

A dominância é calculada nos **três objetivos brutos**. Duplicatas físicas agregam suas origens; soluções fisicamente diferentes com o mesmo vetor podem permanecer. Há arquivos por varredura e uma união não dominada por método.

> **Decisões do grupo, não exigências numéricas do enunciado:** malhas com 16 configurações, extremos empíricos cruzados, prioridade à viabilidade e teto proposto de avaliações. Preservar e justificar essas escolhas; a professora exige os métodos e resultados, não esses números específicos.

## Por onde continuar: código certo e arquivos

**Versão de referência:** branch `tp2/07-12-multiobjetivo`, commit `2787ceb`. [PR #5: métodos e infraestrutura](https://github.com/GustavoMTmelo/TeoriadaDecisao/pull/5) depende do [PR #4: base TP1 corrigida](https://github.com/GustavoMTmelo/TeoriadaDecisao/pull/4). Ambos estavam abertos nesta conferência. O #5 já contém a base do #4; não é necessário copiar arquivos manualmente.

**No computador do Henry:** a cópia de desenvolvimento está em `C:\Users\henry\Desktop\UFMG\TD\tp2-multiobjetivo`. A cópia antiga em `tp1/TeoriadaDecisao/TeoriadaDecisao` continua na branch anterior e tem cinco PDFs de aula excluídos localmente. Não usar essa cópia como se já contivesse o TP2 nem incluir essas exclusões nos commits.

### Em outro computador: começar numa pasta nova

```
git clone https://github.com/GustavoMTmelo/TeoriadaDecisao.git
cd TeoriadaDecisao
git switch tp2/07-12-multiobjetivo
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest -q
```

Python 3.12+; a etapa atual foi testada com 3.14.4 (162 testes). O lock antigo registra o ambiente TP2-01 em Python 3.12; as versões efetivas da campanha estão no manifesto. Nos comandos seguintes, “python” significa o executável do ambiente configurado. Executar na raiz Git, onde ficam os arquivos .py.

| Arquivo ou diretório | Para que serve |
| --- | --- |
| sol\_inicial.py / vizinhancas.py | Dados oficiais, composição, objetivos, validações físicas e movimentos. |
| avaliacao.py / normalizacao.py / escalarizacoes.py | Restrições, escalar, intervalos congelados, pesos e pares ε. |
| busca.py / vns.py | Núcleo TP2: busca.resolver. vns.resolver é adaptador; vns.gvns mantém o TP1 histórico corrigido. |
| experimentos.py / registros.py / pareto.py | Agenda, execução, salvamento/retomada e arquivo não dominado. |
| verificar\_tp2.py / tests/ | Auditoria somente leitura e testes de regressão/integração. |
| configs/tp2.json / tp2\_agenda.json | Parâmetros oficiais propostos e as 160 identidades/sementes. |
| results/tp1\_corrigido/ / referencias\_tp1.json | Resultados corrigidos e referência canônica; conservar. |
| results/integracao\_tp2\_final/ | Evidência reduzida auditada, sem representar a campanha oficial. |
| docs/tp2/ / relatorio.tex | Backlog, planejamento, matriz e registros; fonte do relatório cumulativo. |

Leitura prioritária: README → EXECUCAO\_07\_12.md → BACKLOG (TP2-13 a 17) → PLANEJAMENTO e MATRIZ\_REQUISITOS. AUDITORIA.md contém o diagnóstico antigo; não confundir achados históricos com defeitos ainda abertos.

## Executar a campanha oficial

> **Não reimplementar os métodos.** Primeiro confirmar o ambiente e auditar a evidência salva. Depois fazer piloto, congelar o protocolo e executar a campanha completa (TP2-13).

### 1. Conferir o ponto de partida

```
python verificar_tp2.py --output results/integracao_tp2_final
python reproduzir_tp1.py --output results/tp1_corrigido --verificar
```

A integração salva tem **8 runs e 4.000 avaliações**: 5 finais viáveis e 3 sem viável encontrada; 260 candidatos viáveis observados. A união Pareto tem 49 composições ponderadas e 37 ε-restritas. Auditoria e retomada 8/8 foram testadas. Esses números comprovam a infraestrutura; **não sustentam uma comparação final entre métodos**. No verificador TP1, codigo\_atual\_confere=false é esperado após a evolução dos módulos; conferir também as composições e os produtos.

### 2. Fazer o piloto e registrar a escolha do orçamento

Criar uma configuração de piloto a partir de configs/tp2.json, com sementes externas às cinco oficiais e saída própria. O plano propõe teto de 10.000 avaliações; **ainda é proposta, não orçamento final validado**. Avaliar tempo, fração de runs com viável e comportamento de ε apertado. Registrar a decisão e suas razões em docs/tp2/PROTOCOLO\_EXPERIMENTAL.md (a criar). As sementes 90001/90002 já foram usadas na integração, não na coleta oficial.

Antes da campanha final, fixar código, dados, referência, configurações, sementes e orçamento. Usar o mesmo teto por subproblema nos dois métodos e registrar também o esforço efetivamente gasto. Se alterar módulos ou entradas depois de iniciar, usar uma nova campanha versionada; a retomada rejeita hashes incompatíveis.

### 3. Executar e auditar as 160 runs

```
python experimentos.py --config configs/tp2.json --output results/tp2
python verificar_tp2.py --output results/tp2
```

A agenda tem cinco varreduras de 16 configurações por método, identificadas pelas sementes-base **42, 123, 456, 789 e 1011**. Cada combinação recebe sua própria semente SHA-256. Rodar sequencialmente; o código atual não fornece orquestração distribuída. Não iniciar dois processos gravando na mesma saída.

### 4. Se a execução parar

Repetir o mesmo comando, com os mesmos arquivos de entrada e diretório. As runs completas são revalidadas e reaproveitadas; a run interrompida recomeça. Temporários não contam como conclusão. Não apagar falhas nem trocar sementes por terem dado resultados ruins. Se houver corrupção ou mudança de hash, investigar e preservar a campanha anterior.

**Encerrar TP2-13 somente com:** 160 runs contabilizadas, auditor aprovado, arquivos Pareto por varredura e união por método, protocolo registrado e revisão de outro integrante.

## Fechar gráficos, relatório e entrega

| Etapa restante | Ação concreta e critério para encerrar |
| --- | --- |
| **TP2-14**<br>Figuras e tabelas | Criar figuras\_tp2.py (ainda ausente). Ler os arquivos Pareto já filtrados em 3D e gerar seis projeções: três pares de objetivos por método. Identificar as cinco varreduras; preservar todas as origens quando uma composição aparece em mais de uma. Usar eixos originais, unidades e escalas comparáveis. |
| **TP2-15**<br>Método no relatório | Evoluir relatorio.tex, preservando o conteúdo relevante do TP1 corrigido. Incluir duas formulações, normalização, referências empíricas, justificativa das malhas, restrições físicas/ε, política de inviabilidade, desempates, orçamento e pseudocódigo completo coerente com o VND real. Pode avançar enquanto a campanha roda. |
| **TP2-16**<br>Análise | Inserir resultados oficiais; discutir custo versus qualidades, regiões atingidas por cada repetição, semelhanças/diferenças entre métodos, esforço e falhas. Cada afirmação numérica deve apontar à tabela ou figura correspondente. Comparar só com dados finais congelados. |
| **TP2-17**<br>Reprodução e pacote | Atualizar instruções e matriz de requisitos; testar ambiente/checkout limpo, auditar dados, regenerar tabelas/figuras, compilar o relatório cumulativo e ler todas as páginas. Montar pacote com código, configs, referências, resultados, figuras e PDF final. Envio à plataforma continua com o grupo. |

### Divisão prática entre os colegas

**Uma pessoa:** piloto, campanha e auditoria. **Outra:** gerador de figuras e tabelas, que pode ser desenvolvido com a integração salva como exemplo. **Um editor do LaTeX:** método e integração dos resultados; outro colega revisa números e conformidade. A análise final espera a coleta oficial. Combinar responsáveis e um único editor por arquivo compartilhado.

### Checklist para declarar a Entrega 2 concluída

1. Cinco varreduras completas de cada método, com todas as configurações e falhas contabilizadas.
2. Seis projeções oficiais, com identificação das repetições e Pareto filtrado em 3D.
3. Relatório cumulativo revisado, fórmulas/decisões justificadas e comparação das regiões atingidas.
4. Dados recarregados e auditados; figuras e tabelas geradas do mesmo conjunto congelado.
5. Testes, compilação e revisão visual aprovados; pacote e instruções coerentes com a versão entregue.

> **Evitar conclusões indevidas:** “sem\_viavel\_encontrada” não prova que o subproblema é inviável; arquivo não dominado encontrado não é a fronteira global; mais pontos não provam método melhor. Os 160 subproblemas não são 160 repetições independentes. Não apresentar o PDF atual do TP1 nem a integração reduzida como a Entrega 2 final.

### Fontes e rastreabilidade

Enunciado: Case-UFMG-Teoria\_da\_Decisão.pdf, pp. 4-5 (TP2) e 6-8 (dados). Aulas 5, pp. 8-9 (normalização), e 6, trechos sobre ε-restrito e varreduras. Feedback: síntese em docs/tp2/AUDITORIA.md e NOTAS\_REVISAO\_TP1.md; evidência atual em EXECUCAO\_01\_06.md e EXECUCAO\_07\_12.md. Links de acesso: [repositório na branch de continuidade](https://github.com/GustavoMTmelo/TeoriadaDecisao/tree/tp2/07-12-multiobjetivo) e [backlog completo](https://github.com/GustavoMTmelo/TeoriadaDecisao/blob/tp2/07-12-multiobjetivo/docs/tp2/BACKLOG.md).

Estado conferido em 18/10/2026, commit 2787ceb. Prazo informado pelo grupo: 18/10/2026; horário de envio não registrado. Confirmar diretamente no canal da disciplina. Este é um guia de continuidade, não o relatório acadêmico da entrega.
