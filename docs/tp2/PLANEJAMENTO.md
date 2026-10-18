# Plano de implementação — Entrega 2 do Case Cassotis

**Atualização de execução:** TP2-01 a TP2-06 concluídas, com evidências em
[EXECUCAO_01_06.md](EXECUCAO_01_06.md). Em 18/10 o usuário autorizou também
TP2-07,08,09,10,11,12A,12B; implementação e validação registradas em
[EXECUCAO_07_12.md](EXECUCAO_07_12.md). TP2-13 a TP2-17 continuam posteriores.

> Para execução por agentes: depois da aprovação do usuário, usar `superpowers:executing-plans` para implementar as tarefas em sequência; delegação somente se escolhida/autorizada. Este documento e o backlog são propostas para revisão, não autorização para iniciar o algoritmo.

**Objetivo:** concluir a otimização multiobjetivo por soma ponderada e ε-restrito, corrigindo o TP1 e entregando código reproduzível e relatório cumulativo conforme o enunciado.

**Arquitetura:** conservar a representação e as vizinhanças; parametrizar o núcleo GVNS por avaliação, comparação e orçamento. Normalização, duas escalarizações, arquivo não dominado, experimentos e figuras ficam em módulos separados.

**Tecnologias:** Python 3.12+ declarado pelo README, biblioteca padrão, matplotlib e pytest; relatório LaTeX existente. Fixar versões efetivamente testadas no manifesto. Não exigir nova biblioteca de otimização.

**Especificação:** [matriz de requisitos](MATRIZ_REQUISITOS.md), derivada do enunciado E; [auditoria](AUDITORIA.md); [backlog executável](BACKLOG.md). Data da elaboração: 15/10/2026. Prazo informado pelo usuário: **18/10/2026**, horário ainda não informado.

## 1. Resumo executivo

Os entregáveis são código atualizado e relatório cumulativo, com duas abordagens escalares, cinco varreduras independentes de cada uma, filtragem de não dominância nos três objetivos e seis projeções identificando as repetições. **Não há apresentação oral no TP2** (E p. 5).

O caminho crítico é: contratos/ambiente → validador e retorno viável → registros TP1 → reexecução TP1 e referências → integração dos dois métodos → experimento completo → figuras/análise → relatório e pacote. Pareto, escalares e texto metodológico podem avançar em paralelo após estabilizar contratos; não dependem dos números finais para seus testes sintéticos.

Primeiras issues: TP2-01 (contratos e ambiente), TP2-02 (validação), TP2-03 (melhor viável), TP2-04 (VND e operadores reais). Distribuir Pareto, normalização, escalares e relatório assim que os contratos estiverem definidos. Evitar trocar N3, adicionar população evolutiva ou iniciar Streamlit nesta etapa.

## 2. Restrições gerais

- Preservar exclusões locais preexistentes de cinco PDFs e não executar reset/clean.
- Nenhuma normalização baseada em fitness penalizado, solução inicial inviável ou números arredondados do relatório.
- Toda alternativa publicada deve ter composição recuperável e passar pelas restrições originais; no ε-restrito deve passar também pelos dois limites da configuração de origem.
- Separar incumbente da trajetória, melhor viável do subproblema e conjunto não dominado; nenhum dos três substitui os outros.
- Não alegar garantia de encontrar viável, ótimo global ou fronteira completa. Retornar a melhor viável **se foi encontrada**; caso contrário, registrar falha de busca.
- Congelar configurações e referências antes da campanha final; preservar dados antigos como históricos.
- Relatório único, estendendo `relatorio.tex`; não produzir um segundo relatório independente.

## 3. Pontos que exigem testes de revisão

1. Pilha ausente, chave desconhecida ou minério inválido: rejeitar de forma diagnosticável antes do cálculo de objetivos (TP2-02).
2. Candidato viável não aceito pelo fitness, ou orçamento encerrado imediatamente depois: ainda preservar a melhor viável observada (TP2-03/08).
3. Referência de amplitude zero, objetivo melhor que a referência ou acima do máximo observado: não dividir por zero nem truncar para [0,1] (TP2-07).
4. Qualidade física válida mas ε violado; nenhuma solução encontrada; empate no custo: não confundir situações nem publicar ponto dominado por erro de desempate (TP2-10/12).
5. Solução repetida em várias sementes, arquivo parcial ou retomada em ordem diferente: preservar proveniência e não repetir/omitir configurações (TP2-11/12).

## 4. Reuso e módulos

Todos os caminhos de implementação abaixo são relativos à raiz Git identificada na auditoria; são **arquivos propostos**, salvo os que já existem.

| Arquivo | Responsabilidade | Reuso/novo | Responsável funcional |
|---|---|---|---|
| `sol_inicial.py` | Dados, composição, funções f1/f2/f3, validações | Reutilizar e endurecer validação | A |
| `vizinhancas.py` | Operadores enumerados atuais | Preservar | B |
| `vns.py` | Interface mono-objetivo e reprodução TP1 | Corrigir retorno/registro; depois adaptar ao núcleo | B |
| `contratos.py` | Tipos e configuração compartilhados | Novo, pequeno | A |
| `avaliacao.py` | Avaliação conjunta, viabilidade física/ε, violações | Novo sobre funções atuais | A |
| `busca.py` | SHAKE/VND/GVNS genéricos, orçamento e observador | Extrair de `vns.py` sem redesenhar operadores | B |
| `normalizacao.py` | Construir/carregar referências e normalizar | Novo | C |
| `escalarizacoes.py` | Soma ponderada, ε-restrito e configurações | Novo | C |
| `pareto.py` | Dominância, chave física e proveniência | Novo | D |
| `registros.py` | Serialização e manifesto compartilhados | Novo | E |
| `experimentos.py` | Repetições, agenda de sementes, retomada | Novo | E |
| `figuras_tp2.py` | Tabelas e seis projeções | Novo | F |
| `tests/test_*.py` | Testes por módulo e integração | Novo, conservar testes existentes | Cada autor + revisor |
| `configs/tp2.json` | Pesos, ε, orçamento, sementes, tolerâncias | Novo | E com C |
| `results/tp1_corrigido/`, `results/tp2/` | Composições, objetivos, históricos, manifesto | Novo | E |
| `relatorio.tex` e `relatorio.pdf` | Documento cumulativo e figuras geradas | Atualizar | F, editor único |

Não mover todos os arquivos antigos para outra árvore: isso ampliaria conflitos sem atender a uma exigência. Usar importações simples compatíveis com a raiz atual. A futura extração para `src/` é opcional.

## 5. Formulação e normalização

Seja X o conjunto original de soluções: 10 pilhas completas, massa exata, minérios compatíveis, disponibilidades globais e faixas de SiO₂/Al₂O₃. Variáveis inteiras em caminhões; f1 em R$, f2/f3 em p.p.². Os limites triviais de FeT não geram objetivo ou restrição ativa adicional.

### Referências propostas

Executar novamente os três problemas mono-objetivo em cinco sementes após corrigir registro e retorno. Guardar **os três objetivos de cada uma das 15 composições finais viáveis**, não só o objetivo otimizado. Construir também matriz 3×3 das melhores soluções de cada objetivo como explicação dos conflitos.

Para cada objetivo j, sobre o conjunto S_ref das 15 finais viáveis:

`a_j = min(f_j(x), x em S_ref)`; `b_j = max(f_j(x), x em S_ref)`; `g_j(x) = (f_j(x) - a_j)/(b_j - a_j)`.

São extremos empíricos derivados do TP1, **não ideal/nadir exatos nem máximo sobre todo X**. Novas soluções podem ter g<0 ou g>1; manter esses valores sem clipping. Guardar a_j, b_j, solução/run_id de origem, versão dos dados/código e hash do arquivo. Usar as mesmas referências em todas as configurações e repetições de ambos os métodos. Uma falha no TP1 impede congelar a referência oficial: registrar, investigar e repetir uma campanha explicitamente versionada, sem substituir silenciosamente sementes malsucedidas.

Alternativas permitidas pelo enunciado:

| Opção | Impacto | Recomendação |
|---|---|---|
| Extremos cruzados das 15 finais viáveis | Aproveita variabilidade do TP1 e não exige maximizações extras; depende da amostra | **Adotar** e declarar estimativa empírica |
| Matriz de payoff das 3 melhores soluções mono-objetivo | Mais compacta, mas intervalo pode ser estreito ou degenerado | Alternativa aceitável se justificada |
| Otimizar também máximos de cada objetivo | Aproxima a amplitude do conjunto viável com mais custo; foge dos três mínimos já feitos | Opcional, não necessário |

Não usar `max` dos cinco valores de f2 otimizados em f2 como teto sem considerar os valores de f2 nas outras soluções: esse intervalo mede estabilidade daquela busca e pode ser minúsculo. Se b_j<=a_j ou a amplitude for numericamente degenerada (limiar relativo 1e-12), a configuração deve falhar com diagnóstico antes da campanha. Ampliar a referência com protocolo documentado; não colocar denominador 1 arbitrariamente.

### Soma ponderada

`P_w: minimizar sum(w_j*g_j(x), j=1..3), x em X`, com w_j≥0 e soma dos pesos=1. Pesos expressam preferência após a escala; não são λ de penalidade. Validar entradas finitas e não negativas e soma com tolerância absoluta 1e-12; não corrigir pesos inválidos silenciosamente.

Malha recomendada: todos os `(i/4,j/4,k/4)` com inteiros não negativos e i+j+k=4 (15 combinações), mais `(1/3,1/3,1/3)` (16ª). Inclui extremos, bordas e centro. Pesos nulos podem gerar empates e soluções dominadas; filtrar sempre em três dimensões. Alternativa mais densa H=6 gera 28 combinações; alternativa adaptativa densifica lacunas, mas exige orçamento e protocolo adicionais. Começar com a malha fixa de 16.

### ε-restrito

`P_e: minimizar g_1(x), x em X, g_2(x)<=epsilon_2, g_3(x)<=epsilon_3`.

Manter custo como principal, conforme exemplo A6 pp. 28–30. Não remover as faixas químicas por pilha: tetos dos desvios totais não as substituem. Fixar os limites durante cada subproblema. Malha recomendada: produto cartesiano `{0,1/3,2/3,1} × {0,1/3,2/3,1}`, 16 pares, inclusive fora da diagonal. Alternativa: cinco níveis por eixo (25 pares); alternativa adaptativa a partir de soluções observadas, com maior risco de viés. O grupo escolhe a resolução; o enunciado não fixa 16.

Se nenhum candidato atender a um par, registrar `sem_viavel_encontrada` e o orçamento utilizado. Heurística não encontrar solução **não prova** que o subproblema é inviável. Pares apertados, como (0,0), podem ser incompatíveis em conjunto.

## 6. Busca, aceitação e viabilidade

### Base TP1 corrigida

Manter a penalidade histórica para limitar mudanças nos resultados e recuperar uma referência comparável. Acrescentar observação de cada candidato estruturalmente válido avaliado, inclusive dentro do SHAKE/VND e antes do filtro de aceitação. Guardar uma cópia da melhor solução fisicamente viável pelo objetivo bruto, separada da incumbente por fitness. Ao final retornar essa solução se existir; sem ela, retornar ausência explícita e diagnóstico, sem usar a inicial como sucesso. Adaptar o consumidor para não calcular estatísticas/figuras como se uma falha fosse solução válida.

### Núcleo TP2 recomendado

Três opções de política: penalidade escalar com pesos calibrados; prioridade explícita à viabilidade; reparo dedicado seguido de busca viável. **Recomenda-se prioridade à viabilidade**, para evitar nova calibração de λ a cada escalarização. Reparo dedicado exigiria desenvolvimento e validação adicionais; penalidade pode ser mantida como alternativa se o grupo a preferir, mas não substitui a melhor viável e a validação final.

Após rejeitar falhas estruturais, calcular V como soma dos excessos químicos normalizados pela amplitude da faixa de cada indicador/pilha, ao quadrado, mais excessos positivos dos dois objetivos normalizados sobre ε quando aplicável. Para consistência, aplicar tolerância química 1e-9 p.p. e tolerância ε 1e-9 na própria definição dos excessos: `max(0, L-q-tol, q-U-tol)/(U-L)` para qualidade e `max(0,g-epsilon-tol)` para ε. Assim V=0 coincide com a viabilidade numérica definida. Guardar também os excessos sem tolerância para auditoria.

Comparar por chave lexicográfica `(0,0,escalar,desempate)` se viável; `(1,V,escalar,desempate)` se inviável. Melhoria estrita dessa chave na busca local e no laço externo. Para ε, desempate após custo por `(g2+g3,g2,g3)`; para soma ponderada, por `(g1+g2+g3,g1,g2,g3)`. Não arredondar valores na comparação. Empates completos mantêm incumbente. SHAKE pode atravessar inviabilidade química/ε, mas continua rejeitando estrutura inválida; VND tenta reduzir violações a partir do ponto perturbado. Isso não garante encontrar viável para todo ε.

Manter N1/N2/N3 e tentativas atuais. Antes do limite de cinco reinícios, melhoria reinicia em N1; depois do limite, melhoria mantém a vizinhança atual; ausência de melhoria avança. Atualizar comentário, relatório e pseudocódigo para essa regra. Não alegar que cinco reinícios são um teto de avaliações.

### Parada e observação

Preservar parâmetros 200 iterações externas, 60 sem melhoria, K=3, 20 amostras, 5 reinícios como referência inicial. Acrescentar teto global de avaliações para TP2 e verificá-lo em todos os laços internos. Avaliação = chamada central que calcula o vetor completo e as restrições de uma solução estruturalmente válida; contar inclusive repetidas, sem cache inicialmente. Contar tentativas estruturalmente inválidas em campo separado. A avaliação inicial conta no orçamento. Orçamento zero retorna diagnóstico sem iniciar a busca.

O observador recebe avaliação completa antes de qualquer decisão de aceitação. Atualiza melhor viável e arquivo. Ao esgotar orçamento, propagar término preservando tudo que já foi observado. Registrar motivo da parada, iterações, avaliações, tentativas inválidas, tempo decorrido e histórico do melhor escalar viável (null antes do primeiro viável). Não comparar valores de soma ponderada de pesos diferentes como se fossem a mesma métrica.

## 7. Pareto e diversidade

Dominância para minimização: a domina b se todos os três f_j(a)<=f_j(b) e pelo menos um é estritamente menor. Comparar valores completos, sem arredondamento de apresentação e sem tolerância assimétrica que introduza ciclos. As escalas positivas fixas preservam essa ordem. Testar com exemplos calculados manualmente.

Deduplicar pela composição física: tupla ordenada de pilhas, cada qual com contagens ordenadas de minérios. Permutações internas são a mesma alternativa; permutar pilhas diferentes não é a mesma solução. Soluções diferentes com vetor objetivo idêntico podem ser mantidas, agregando os pontos iguais só no desenho. Isso preserva composições úteis para o TP3.

Manter `P_metodo,repeticao`; depois `P_metodo = ND(uniao das 5 repeticoes)`. Exportar os dois níveis. As seis projeções oficiais usam P_metodo e mostram a proveniência das repetições; conjuntos por repetição podem aparecer em painel suplementar. Se uma composição pertence a várias repetições, guardar todas as origens e usar marcadores sobrepostos/segmentados ou anotação, sem deslocar os valores reais. Filtrar no espaço **3D antes** de gerar qualquer projeção 2D.

Recomenda-se observar todos os candidatos viáveis ao subproblema, não somente seus retornos finais; aplicar a mesma política nos dois métodos. No ε-restrito, candidatos que violam os tetos não entram como resultados daquela configuração, mesmo quando fisicamente válidos. Não misturar pontos do TP1 ao arquivo de um método sem identificar a origem; usar referências TP1 como camada de comparação separada.

Não é necessária população evolutiva: o conjunto inicial de cada busca é a construtiva atual, e a diversidade vem das configurações, sementes, SHAKE e arquivo. Alternativas futuras: múltiplos pontos iniciais viáveis ou warm starts. Adiar ambos para evitar dependência da ordem de configurações. Não limitar arquivo por crowding inicialmente; se tamanho/custo se tornar problema, medir antes e não descartar pontos silenciosamente.

## 8. Contratos para trabalho paralelo

Definir em `contratos.py` dataclasses imutáveis para metadados, copiando composições ao armazenar. Nomes abaixo são a proposta a congelar em TP2-01.

```text
Solucao = dict[int, list[str]]
Vetor = tuple[float, float, float]
Referencia: minimo: Vetor, maximo: Vetor, id: str, origens: dict
ConfigEscalar: metodo: 'mono'|'ponderada'|'epsilon', id: str,
              objetivo: int|None, pesos: Vetor|None,
              epsilons: tuple[float,float]|None
ConfigBusca: max_iter=200, max_sem_melhora=60, k_max=3,
             max_amostras=20, max_restarts=5, max_avaliacoes: int|None
Avaliacao: objetivos: Vetor|None, normalizados: Vetor|None,
           estrutura_ok: bool, qualidade_ok: bool, epsilon_ok: bool,
           violacao: float, escalar: float|None, chave: tuple,
           erros: tuple[str,...]
Candidato: solucao: Solucao, avaliacao: Avaliacao, origens: list[dict]
ResultadoBusca: status: 'viavel'|'sem_viavel_encontrada',
                melhor_viavel: Candidato|None,
                melhor_busca: Candidato|None, historico: list[dict],
                avaliacoes: int, iteracoes: int, motivo_parada: str,
                tempo_s: float

avaliar(solucao: Solucao, config: ConfigEscalar,
        referencia: Referencia|None) -> Avaliacao
normalizar(objetivos: Vetor, referencia: Referencia) -> Vetor
resolver(config: ConfigEscalar, referencia: Referencia|None,
         seed: int, limites: ConfigBusca,
         observar: Callable[[Candidato], None]|None = None) -> ResultadoBusca
domina(a: Vetor, b: Vetor) -> bool
chave_solucao(solucao: Solucao) -> tuple
atualizar_arquivo(arquivo: list[Candidato], candidato: Candidato) -> list[Candidato]
executar_campanha(config_path: str, output_dir: str) -> dict
gerar_figuras(input_dir: str, output_dir: str) -> list[str]
```

No modo mono, avaliação mantém a penalidade histórica na chave de busca e usa restrições físicas para melhor viável; sem referência, `normalizados=None`. Em entrada estruturalmente inválida, objetivos/escalar são None e a busca rejeita antes de comparar chaves. A lista de candidatos observados pertence ao orquestrador/arquivo, não precisa ficar toda no ResultadoBusca. A proveniência mínima contém método, repetição, configuração, semente, run_id e índice da avaliação.

Serialização v1: um JSON por busca com configuração, seed, status, melhor solução completa, f1/f2/f3, valores normalizados, validações, violações, histórico e contadores. CSV resumo uma linha por subproblema, inclusive falhas. Manifesto com versão de Python/dependências, commit e diff/hash de código, hash dos dados/referências, agenda completa e estado de cada run. JSON recarregado converte chaves de pilha para inteiros e é revalidado. Números permanecem em precisão completa; arredondamento só no relatório.

## 9. Experimentos

### Etapa de referência

TP1 corrigido: objetivos f1/f2/f3 × sementes `[42,123,456,789,1011]` = 15 buscas. Guardar todas as composições, históricos e objetivos cruzados; gerar tabela antiga atualizada e seis figuras TP1. Valores antigos são comparação histórica, não metas obrigatórias de regressão após corrigir seleção da melhor viável.

### Piloto e campanha TP2

Piloto de poucas configurações (centro e extremos dos pesos; ε frouxo, intermediário e apertado), com sementes de piloto distintas, por exemplo 90001 e 90002. Teto inicial proposto: 10.000 avaliações por subproblema. Medir tempo, taxas de viabilidade, duplicação e dispersão; se inadequado, ajustar teto ou malha **antes** da campanha final. Salvar decisão e não reutilizar pontos de piloto como resultados oficiais.

Campanha proposta: 2 abordagens × 5 repetições × 16 configurações = **160 buscas** TP2, mais 15 TP1 = **175 buscas de referência/finais**, além do piloto. Mesmo teto de avaliações por configuração e mesmo número de configurações permitem comparação de esforço; registrar também avaliações realmente gastas, pois parada antecipada pode diferir. Não usar tempos de 16–29 s do log antigo como previsão garantida.

Usar sementes-base TP1 como identificadores das cinco repetições. Derivar seed por combinação estável `(base_seed, metodo, config_id)` usando SHA-256, convertendo os primeiros 8 bytes em inteiro; guardar valor efetivo no manifesto. Não usar `hash()` do Python. Cada configuração cria seu próprio RNG e construtiva; nenhuma dependência de ordem ou estado compartilhado entre repetições.

Executar sequencialmente primeiro; distribuir processos/máquinas apenas com manifests de shards disjuntos e mesma versão/referências. Retomada só reutiliza run concluído cujo hash/configuração/seed coincidam. Escrita temporária e renomeação atômica evitam confundir arquivos incompletos com sucesso. Mesclar resultados conferindo lista esperada de 160 identificadores.

### Tabelas, figuras e métricas

Obrigatórios: seis projeções em eixos originais (f1 pode ser exibido em milhões de R$; f2/f3 em p.p.²), legenda das cinco repetições, análise dos compromissos e comparação entre abordagens. Mesmos limites de eixos entre métodos para cada par ajudam a comparação. Não unir pontos por linha sugerindo uma frente contínua conhecida.

Decisões recomendadas: por método/repetição, registrar configurações com viável, sem viável encontrada, nº de composições distintas e de não dominadas, min/max por objetivo, tempo e avaliações. Calcular cobertura direcional `C(A,B)=|{b em B: existe a em A que domina b}|/|B|`, reportando também C(B,A); se B vazio, N/A. Contagens isoladas não medem qualidade nem comprovam superioridade. Conjuntos vazios devem ser apresentados explicitamente.

Comparar referências TP1 e compromissos TP2 usando vetores cruzados, sem exigir melhorar simultaneamente os três mínimos mono-objetivo. Discutir regiões atingidas em cada repetição e regiões perdidas entre métodos. Com cinco repetições, reportar variabilidade descritiva, evitando alegações inferenciais sem análise apropriada.

Hipervolume e espaçamento são opcionais; se adotados, usar mesma normalização e ponto de referência documentado, sem escolher o ponto para favorecer um método. IGD não é requisito e não deve ser calculado como distância à fronteira verdadeira inexistente.

## 10. Testes e validação

O backlog contém o teste específico de cada issue. Sequência: caso que falha no comportamento atual/ausente → mudança mínima → teste passa → regressão relacionada → revisão do diff. Não criar teste que apenas reproduza a fórmula do código sem valores conhecidos ou invariantes independentes.

Casos centrais: objetivo calculado manualmente; falta de pilha; disponibilidade nos limites; tolerância química; semente reproduzível; preservação de entrada nos operadores rápidos; sequência VND; viável perdida pela trajetória; orçamento exato; referência degenerada; pesos inválidos; ε individual e conjunto; Pareto com dominância só perceptível em 3D; duplicatas físicas; arquivo vazio; serialização; retomada; campanha reduzida com ambos métodos.

Antes de aceitar resultados: ler composições salvas e recalcular teores, massa, usos e objetivos em rotina de auditoria separada do arquivo já salvo. Comparar com registros em precisão completa (custo exato; tolerância numérica 1e-9 para teores e 1e-8 para objetivos quadráticos). Teste sintético pequeno de Pareto deve usar comparação manual ou enumeração, sem exigir prova global do case.

Comandos propostos após implementação: `python -m pytest -q`; `python experimentos.py --config configs/tp2.json --output results/tp2`; `python figuras_tp2.py --input results/tp2 --output figures/tp2`. Acrescentar comandos reais de TP1, verificação e empacotamento ao README quando existirem. Esses comandos novos **ainda não estão implementados**.

## 11. Trabalho paralelo e integração

Divisão por competência, sem atribuir nomes sem combinar disponibilidade:

| Frente | Conhecimento | Issues principais | Fronteira de edição |
|---|---|---|---|
| A — modelo e validação | Modelo matemático/Python | 01,02; revisão de 06/07 | `contratos.py`, `avaliacao.py`, validação em `sol_inicial.py` |
| B — núcleo e correções TP1 | GVNS, testes de fluxo | 03,04,08 | `vns.py`, `busca.py`; edições sequenciais |
| C — normalização e escalares | Multiobjetivo | 07,09,10 | `normalizacao.py`, `escalarizacoes.py`; 09/10 mesmo autor ou commits coordenados |
| D — Pareto e integração | Estruturas/testes | 12 e componente Pareto da 12 | `pareto.py`, `tests/test_pareto.py`, integração |
| E — registros e experimentos | Reprodutibilidade/execução | 05,06,11,13 | `registros.py`, `experimentos.py`, resultados |
| F — figuras e relatório | Análise/LaTeX | 14,15,16,17 | `figuras_tp2.py`, `relatorio.tex`; editor único |

Com menos pessoas, unir A+D e C+E; preservar a separação de arquivos e revisões. TP2-12 tem núcleo Pareto testável cedo e integração final depois de 08–11. Reservar primeiro esse componente para não deixar D bloqueada; o backlog o divide em TP2-12A e TP2-12B.

Branch por issue: `tp2/01-contratos`, `tp2/02-validacao` etc., criada de `main` atualizado após preservar mudanças locais. Um responsável integra PRs pequenos na ordem das dependências. Commits por alteração verificável, sem incluir PDFs de aula removidos. Antes de merge: testes do módulo e consumidores, nenhum contrato alterado sem acordo, nova saída serializável/revalidável e descrição coerente. Resultados finais só entram após congelar o código e passam por revisão de alguém que não executou a campanha.

Ordem sugerida: 01 → 02 → 03/04 (sequenciais no mesmo arquivo) → 05 → 06. Em paralelo a partir de 01: 07 com referências sintéticas, 09/10, 12A e esqueleto metodológico de 15. Depois: 08 + 11 → 12B → 13 → 14/16 → fechar 15 → 17. O grafo detalhado está no backlog.

## 12. Cronograma até 18/10

Cronograma proposto, depende da aprovação e da disponibilidade do grupo; não é promessa de esforço medido.

- **15/10:** revisar plano e contratos; preparar ambiente; começar validação/retorno viável e testes. Frentes independentes abrem Pareto, normalização/escalares e método do relatório.
- **16/10:** concluir correções, registrar e reexecutar TP1; integrar núcleo e varreduras; piloto e congelamento do protocolo.
- **17/10:** campanha completa, revalidação dos dados, figuras e análise; revisão cruzada do relatório.
- **18/10:** margem para falhas/reexecuções justificadas, compilação e conferência visual, reprodução e pacote final. Confirmar horário no canal da disciplina; não assumir 23h59.

Se houver atraso, retirar somente opcionais: métricas avançadas, refinamento de malha, novos pontos iniciais e slides. Manter ambas as abordagens, cinco repetições, normalização rastreável, seis projeções, correções e relatório cumulativo. Ajustar orçamento com justificativa antes de rodar toda a campanha, sem escolher sementes pelo resultado.

## 13. Riscos e decisões para revisão

| Risco/decisão | Tratamento proposto |
|---|---|
| Falta de dependências no ambiente da auditoria | TP2-01 instala/verifica ambiente antes de prometer reprodutibilidade |
| Referências históricas sem soluções completas | TP2-06 gera novo conjunto, não extrai composição de gráficos |
| Empates, pesos zero e soluções repetidas | Desempate explícito + Pareto 3D + chave física e todas as origens |
| ε muito apertado | Registrar falha de busca, não afirmar inviabilidade matemática |
| Referência empírica estreita | Não truncar; piloto e protocolo versionado; não mudar escalas durante campanha |
| Custos de enumeração e arquivo | Medir piloto; otimização só se evidência exigir; nunca mudar N3 para ganhar tempo sem teste |
| Conflitos em `vns.py`, `relatorio.tex` | Editor único por arquivo e integração sequencial |
| Prazo e máquinas disponíveis | Cronograma por dependências; coleta distribuída só após congelar contratos/dados |

Pontos para o grupo aprovar: (1) min–max das 15 soluções como referência; (2) prioridade à viabilidade no TP2, mantendo penalidade do TP1; (3) malhas de 16 configurações e teto inicial de piloto; (4) responsáveis e disponibilidade. As alternativas estão descritas acima e não bloqueiam a elaboração deste plano. O prazo já foi corrigido para 18/10; o horário precisa ser conferido.

## 14. Definição de concluído e checklist

- [ ] F01–F04 corrigidos com testes e texto correspondente; N3 preservada.
- [ ] TP1 corrigido com 15 registros completos e viáveis, estatísticas e figuras regeneráveis.
- [ ] Referências e matriz cruzada rastreáveis; normalização única nos dois métodos.
- [ ] Soma ponderada e ε-restrito formulados, implementados e testados via GVNS.
- [ ] Cinco varreduras completas por método, todas as configurações contabilizadas, inclusive falhas.
- [ ] Cada alternativa publicada revalidada fisicamente e, quando aplicável, contra ε de origem.
- [ ] Conjuntos não dominados em três objetivos, por repetição e consolidados, com proveniência.
- [ ] Seis projeções e comparação de compromissos/variabilidade sustentadas pelos dados.
- [ ] Relatório único mantém conteúdo relevante TP1 corrigido e incorpora TP2.
- [ ] Código, fontes, dados, figuras, dependências e instruções no pacote; reprodução conferida.
- [ ] PDF compilado, fórmulas/tabelas/legendas legíveis, sem prometer apresentação TP2.
- [ ] Revisão final da matriz: nenhuma obrigação sem evidência ou issue concluída.

O planejamento termina na revisão do usuário. A implementação começa somente após sua aprovação, como solicitado no texto de abertura.
