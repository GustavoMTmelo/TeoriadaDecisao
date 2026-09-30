# Prompt mestre para o NotebookLM — vídeo explicativo do TP1 Case Cassotis

Copie todo o texto abaixo e use-o como instrução para gerar o vídeo. Antes de gerar, adicione ao notebook pelo menos o enunciado do case, o relatório final, os três códigos Python, os gráficos de convergência e, se possível, a apresentação.

---

## PROMPT

Crie um vídeo explicativo extenso, rigoroso e didático, em português do Brasil, sobre o trabalho **“Otimização Mono-objetivo de Pilhas de Minério — Entrega 1 do Case Cassotis”**, desenvolvido na disciplina de Teoria da Decisão da UFMG.

O vídeo deve funcionar como uma explicação completa do projeto para alguém que conhece conceitos básicos de otimização, mas ainda não leu o enunciado, o relatório ou o código. O público deve terminar o vídeo entendendo:

1. o contexto industrial e o problema de decisão;
2. tudo o que foi exigido na Entrega 1;
3. a formulação matemática;
4. como a solução foi representada no código;
5. como a heurística construtiva foi feita;
6. como funciona a metaheurística GVNS;
7. por que cada decisão algorítmica foi tomada;
8. como as soluções inviáveis foram tratadas;
9. como os experimentos foram planejados e reproduzidos;
10. quais resultados foram obtidos e o que eles realmente permitem concluir;
11. como o trabalho foi validado e organizado para entrega.

Produza a versão mais completa possível do vídeo, preferencialmente com **20 a 30 minutos**, sem omitir conteúdo técnico relevante. Se houver limitação de duração, priorize a explicação do modelo, da heurística construtiva, do GVNS, das três vizinhanças, do tratamento de inviabilidade, dos experimentos e da interpretação dos resultados. Não transforme o vídeo em uma simples leitura dos slides ou do relatório.

### Regras de fidelidade às fontes

- Use como fontes principais o enunciado do Case Cassotis, `relatorio.pdf` ou `relatorio.tex`, `sol_inicial.py`, `vizinhancas.py`, `vns.py`, `README.md`, os gráficos e as tabelas de resultados.
- Diferencie claramente três categorias:
  1. **exigências do enunciado**;
  2. **decisões de implementação tomadas pelo grupo**;
  3. **resultados observados nos experimentos**.
- Não apresente uma decisão do grupo como se tivesse sido imposta pelo enunciado.
- Não invente dados, limites, parâmetros, resultados, provas de otimalidade ou detalhes que não estejam nas fontes.
- Não afirme que foi encontrado o ótimo global. Use expressões como “melhor solução encontrada pelo GVNS nas execuções realizadas”.
- Não compare diretamente os valores numéricos de `f1`, `f2` e `f3` como se estivessem na mesma escala. Eles representam objetivos e unidades diferentes.
- Explique que a solução construtiva inicial é estruturalmente viável, mas possui violações de qualidade. Portanto, seus valores brutos são apenas referências iniciais, e não resultados finais viáveis.
- Explique que os resultados de `f2` e `f3` são somas de desvios quadráticos, e não percentuais de redução nem teores químicos.
- Ao mencionar redução próxima de 90% em `f2` e `f3`, esclareça que é a redução do valor bruto da função objetivo em relação à solução inicial inviável, acompanhada da obtenção de viabilidade.
- Explique que FeT aparece nos dados, mas não é uma restrição ativa nesta etapa, pois os limites fornecidos são 0% e 100%.

## Estrutura obrigatória do vídeo

### 1. Abertura e visão geral

Comece apresentando o trabalho, a disciplina e a finalidade da Entrega 1. Explique que o estudo trata da formação de pilhas de minério para alimentar dois equipamentos de sinterização da empresa Cassotis.

Apresente a pergunta central de decisão:

> Como definir a composição de dez pilhas de minério, respeitando restrições físicas, logísticas e químicas, enquanto se otimiza separadamente custo, desvio de sílica e desvio de alumina?

Explique que esta primeira entrega é mono-objetivo. Foram resolvidas três versões do mesmo problema, com o mesmo conjunto viável e uma função objetivo diferente em cada execução:

- `f1`: minimizar o custo total de aquisição;
- `f2`: minimizar o desvio quadrático dos teores de SiO₂ em relação aos alvos;
- `f3`: minimizar o desvio quadrático dos teores de Al₂O₃ em relação aos alvos.

Apresente o fluxo geral do trabalho em uma visão única:

**dados do case → formulação matemática → representação computacional → heurística construtiva → GVNS com SHAKE e VND → experimentos com sementes fixas → validação → tabelas, gráficos e conclusões.**

### 2. O que foi pedido na Entrega 1

Dedique uma seção específica às exigências da atividade.

Explique que deveriam ser entregues todos os códigos usados nas versões mono-objetivo, incluindo:

- representação da solução;
- heurística construtiva;
- VNS ou GVNS;
- estruturas de vizinhança;
- procedimento de perturbação;
- busca local;
- tratamento de soluções inviáveis;
- cálculo das funções objetivo;
- verificação das restrições;
- rotinas para gerar resultados, tabelas e figuras.

Explique que o relatório deveria apresentar:

- formulação matemática;
- representação computacional;
- heurística construtiva;
- metaheurística desenvolvida;
- vizinhanças;
- perturbação;
- busca local;
- critério de aceitação;
- tratamento de inviabilidades;
- critérios de parada;
- parâmetros;
- planejamento dos experimentos;
- análise dos resultados;
- pseudocódigo completo integrando todas as etapas;
- justificativas para todas as decisões não determinadas pelo enunciado.

Explique também que a apresentação de até 10 minutos deveria priorizar a metaheurística, principalmente as decisões tomadas pelo grupo sobre N3, perturbação, inviabilidade, organização da busca local, aceitação e parada. Diferencie essa apresentação curta do vídeo atual, que deve ser mais detalhado e servir como material explicativo completo.

### 3. Contexto e dados do problema

Explique os elementos básicos do case:

- existem 20 minérios, indexados por `i`;
- existem 10 pilhas, indexadas por `p`;
- existem dois equipamentos de sinterização, indexados por `g`;
- as pilhas 1 a 5 alimentam o Sinter 1;
- as pilhas 6 a 10 alimentam o Sinter 2;
- cada caminhão transporta 2 kt, equivalentes a 2.000 toneladas;
- cada pilha possui uma massa final exigida;
- cada minério possui custo, teores de SiO₂, Al₂O₃ e FeT, limites de disponibilidade e elegibilidade por equipamento;
- cada equipamento possui limites mínimo e máximo e valores-alvo para SiO₂ e Al₂O₃.

Mostre visualmente dois equipamentos recebendo cinco pilhas cada, e cada pilha sendo formada por blocos ou caminhões coloridos que representam os diferentes minérios.

### 4. Formulação matemática

Apresente a variável de decisão:

`x_ip` é o número inteiro e não negativo de caminhões do minério `i` alocados à pilha `p`.

Explique que, como cada caminhão possui 2 kt, a massa do minério `i` na pilha `p` é `2 x_ip` kt.

#### 4.1 Qualidade das pilhas

Explique as médias ponderadas:

- `Si_p = (2 / M_p) × soma_i(s_i x_ip)`;
- `Al_p = (2 / M_p) × soma_i(a_i x_ip)`.

Mostre que os teores resultantes dependem da composição completa de cada pilha e da massa final dessa pilha.

#### 4.2 Restrições

Explique uma por uma:

1. **Massa exata:** `2 × soma_i(x_ip) = M_p` para toda pilha.
2. **Limites de SiO₂:** o teor de cada pilha deve ficar entre os limites do equipamento correspondente.
3. **Limites de Al₂O₃:** regra análoga para alumina.
4. **Compatibilidade:** um minério somente pode ser alocado a uma pilha se for elegível para o equipamento alimentado por ela.
5. **Disponibilidade:** a soma de caminhões de cada minério em todas as pilhas deve ficar entre os limites mínimo e máximo desse minério.
6. **Integralidade e não negatividade:** não existem frações de caminhão.

Explique que essas restrições formam o conjunto viável comum `X` dos três problemas.

#### 4.3 Funções objetivo

Apresente e interprete:

- `f1(x) = soma_p soma_i 2000 c_i x_ip`, correspondente ao custo total em reais;
- `f2(x) = soma_p (Si_p − alvo de SiO₂ do equipamento)^2`;
- `f3(x) = soma_p (Al_p − alvo de Al₂O₃ do equipamento)^2`.

Explique por que os desvios são elevados ao quadrado: desvios positivos e negativos não se anulam e desvios maiores recebem peso crescente.

Reforce que são três otimizações independentes:

- minimizar `f1` sujeito a `x` pertencente a `X`;
- minimizar `f2` sujeito a `x` pertencente a `X`;
- minimizar `f3` sujeito a `x` pertencente a `X`.

### 5. Representação computacional

Explique que, embora o modelo matemático utilize contagens `x_ip`, o código representa cada pilha como um vetor de minérios. Cada posição do vetor equivale a um caminhão de 2 kt.

Uma pilha de massa `M_p` possui `M_p / 2` posições. Use um exemplo visual semelhante a:

`P1 = [M4, M4, M10, M10, M11, M14, M14, M14, M14, M14]`.

Explique por que essa escolha é conveniente:

- a massa da pilha é representada pelo tamanho do vetor;
- substituir um caminhão equivale a alterar uma posição;
- trocar caminhões entre pilhas equivale a trocar posições;
- os movimentos de vizinhança ficam simples de implementar e interpretar;
- a contagem global de cada minério pode ser calculada diretamente.

Mencione a organização do código:

- `sol_inicial.py`: dados do problema, construção inicial, cálculo de teores, funções objetivo e validações;
- `vizinhancas.py`: implementações de N1, N2 e N3;
- `vns.py`: penalidade, fitness, SHAKE, busca local, VND, GVNS, experimentos e gráficos;
- `test_vizinhancas.py`: testes das vizinhanças, reprodução e validação numérica.

### 6. Heurística construtiva

Explique que a solução inicial é gerada por uma heurística gulosa baseada em custo. Ela foi projetada para obter rapidamente uma solução estruturalmente consistente, que depois é refinada pelo GVNS.

Descreva as duas fases:

1. **Atendimento das disponibilidades mínimas:** para cada minério com quantidade mínima obrigatória, inserir os caminhões necessários em pilhas com espaço e equipamento compatível.
2. **Preenchimento das pilhas:** percorrer as pilhas, ordenar os minérios compatíveis por custo crescente e preencher as posições restantes com o minério mais barato que ainda tenha disponibilidade.

Explique a decisão de não exigir viabilidade química nessa construção. Incluir qualidade diretamente poderia tornar a heurística mais complexa e dificultar a obtenção rápida de um ponto inicial. O grupo preferiu garantir massa, compatibilidade e disponibilidade na construção e deixar o GVNS corrigir a qualidade por meio da penalização.

Apresente os valores da solução inicial:

- `f1 = R$ 60.400.000`;
- `f2 = 23,48`;
- `f3 = 14,91`;
- 12 violações de qualidade.

Deixe claro que essa solução é estruturalmente válida, mas não é uma solução final viável quanto à qualidade.

### 7. Por que utilizar GVNS

Explique de forma intuitiva que uma solução gulosa ou uma única busca local pode ficar presa em uma região limitada do espaço de soluções. O **General Variable Neighborhood Search** combina:

- **diversificação**, por meio do SHAKE, que perturba a solução atual;
- **intensificação**, por meio do VND, que explora sistematicamente vizinhanças locais;
- múltiplas estruturas de vizinhança, que enxergam diferentes tipos de movimento.

Explique que o objetivo não é enumerar todas as combinações possíveis. O espaço de busca é grande, e o GVNS oferece uma estratégia prática para encontrar boas soluções viáveis em tempo computacional controlado.

### 8. Estruturas de vizinhança

Apresente cada vizinhança com animações simples de caminhões ou posições sendo alteradas.

#### N1 — substituição de um caminhão

- seleciona uma pilha e uma posição;
- substitui o minério atual por outro minério diferente;
- o novo minério deve ser compatível com o equipamento;
- o movimento altera diretamente a composição e a utilização global de minérios.

Explique que N1 realiza ajustes pequenos e precisos, adequados para refinamento local.

#### N2 — troca entre duas pilhas

- seleciona duas pilhas distintas e uma posição em cada uma;
- troca os dois minérios;
- exige compatibilidade cruzada: o minério vindo da primeira pilha deve poder alimentar o equipamento da segunda, e vice-versa;
- preserva o número de caminhões de cada pilha;
- preserva a quantidade global usada de cada minério.

Explique que N2 redistribui os minérios entre pilhas sem alterar o consumo global.

#### N3 — substituição simultânea de dois caminhões na mesma pilha

- seleciona uma pilha e duas posições distintas;
- substitui os dois minérios por novos minérios compatíveis;
- exige que as posições sejam efetivamente alteradas;
- evita aceitar uma mera permutação que deixe a composição igual.

Destaque que N3 foi uma decisão algorítmica do grupo. Justifique detalhadamente:

- alguns ajustes de qualidade exigem reduzir um componente e compensar outro ao mesmo tempo;
- duas substituições coordenadas podem alcançar uma composição que N1 só alcançaria em dois passos;
- o primeiro passo isolado de N1 poderia piorar a fitness e ser rejeitado, impedindo o segundo;
- N3 permite atravessar esse bloqueio em um único movimento;
- N3 é diferente de N2 porque altera a composição de uma única pilha e pode mudar a utilização global de minérios, enquanto N2 apenas redistribui minérios entre pilhas.

Explique que N2 e N3 usam amostragem aleatória para reduzir custo computacional. A implementação rápida tenta até 40 movimentos em N2 e até 50 tentativas por pilha em N3, em vez de enumerar toda a vizinhança.

### 9. SHAKE, busca local e VND

#### SHAKE

Explique que o SHAKE aplica `k` movimentos aleatórios escolhidos entre as três vizinhanças, com `k` em `{1, 2, 3}`. A intensidade crescente permite escapar de ótimos locais. Cada candidato precisa permanecer estruturalmente viável.

#### Busca local

Explique o uso de **First Improvement**:

- em cada chamada, são amostrados até 20 vizinhos;
- o primeiro vizinho estruturalmente válido com fitness estritamente menor é aceito;
- a busca não precisa avaliar toda a vizinhança depois de encontrar melhoria.

Justifique essa escolha como compromisso entre qualidade e tempo: Best Improvement poderia exigir muitas avaliações; First Improvement permite melhorias rápidas em um espaço grande.

#### VND

Explique que o VND percorre `N1 → N2 → N3`. Quando encontra melhoria, retorna a N1 para explorar novamente os movimentos mais simples. O número de reinícios internos é limitado a cinco. Após esse limite, a busca continua avançando pelas vizinhanças, controlando o tempo de CPU.

### 10. Tratamento de soluções inviáveis

Explique que o grupo separou a inviabilidade em duas categorias.

#### Restrições estruturais

Massa, compatibilidade e disponibilidades representam condições físicas ou operacionais. Movimentos que violem essas condições são rejeitados, e a implementação procura preservá-las por construção.

Justifique:

- massa é determinada pelo número de caminhões;
- compatibilidade é uma regra fixa dos equipamentos;
- disponibilidades refletem limites reais de fornecimento;
- manter essas restrições sempre válidas simplifica a busca e evita reparos complexos.

#### Restrições de qualidade

Violações de SiO₂ ou Al₂O₃ entram em uma penalidade quadrática:

`pen(x) = soma, para todas as pilhas, dos quadrados das violações abaixo do mínimo ou acima do máximo de SiO₂ e Al₂O₃`.

A fitness é:

`phi(x) = f(x) + lambda × pen(x)`.

Os pesos são:

- `lambda_f1 = 10^12`;
- `lambda_f2 = 10^4`;
- `lambda_f3 = 10^4`.

Explique que os pesos diferem porque as funções objetivo possuem escalas muito diferentes. `f1` é da ordem de dezenas de milhões de reais, enquanto `f2` e `f3` são da ordem de unidades. Os pesos foram calibrados para tornar soluções com violações de qualidade muito menos atraentes do que soluções viáveis competitivas, sem impedir completamente a travessia temporária de regiões levemente inviáveis.

Explique a vantagem da penalização: certas melhorias podem exigir passar por uma composição intermediária com pequena violação de qualidade. Rejeitar toda inviabilidade química imediatamente poderia bloquear caminhos úteis. Entretanto, a solução final reportada precisa ser validada e viável.

Mencione a tolerância numérica de `1e-9` usada na validação de qualidade. Ela evita falsos negativos causados por representação em ponto flutuante, como interpretar `2,3000000000000003` como violação de um limite `2,3`. Essa tolerância não altera as metas nem relaxa materialmente as restrições.

### 11. Critério de aceitação e fluxo completo do GVNS

Mostre um fluxograma ou pseudocódigo animado com o seguinte fluxo:

1. gerar a solução inicial;
2. definir essa solução como incumbente;
3. iniciar o contador de iterações sem melhoria;
4. para cada iteração externa, definir `k = 1`;
5. aplicar `SHAKE(x*, k)`;
6. refinar com `VND`;
7. calcular a fitness;
8. se houver melhoria estrita, atualizar a incumbente e voltar para `k = 1`;
9. caso contrário, aumentar `k`;
10. atualizar o contador de estagnação;
11. parar ao atingir o limite de iterações ou de estagnação;
12. retornar e validar a melhor solução.

Explique que empates não são aceitos. Tanto o VND quanto o laço externo exigem fitness estritamente menor. Essa regra evita movimentação sem ganho e deixa o histórico de melhoria monotônico para a incumbente.

### 12. Parâmetros e critérios de parada

Apresente uma tabela visual:

- `MAX_ITER = 200`: máximo de iterações externas;
- `K_MAX = 3`: três intensidades de perturbação;
- `MAX_AMOSTRAS = 20`: vizinhos amostrados por busca local;
- `MAX_RESTARTS_VND = 5`: reinícios internos máximos do VND;
- `MAX_SEM_MELHORA = 60`: parada antecipada após 60 iterações externas sem melhoria global.

Explique a função de cada parâmetro. Diferencie critérios de parada globais dos limites internos usados para controlar o custo computacional. `MAX_ITER` e `MAX_SEM_MELHORA` encerram a execução; os demais regulam a intensidade e o esforço de cada etapa.

Informe que os tempos observados ficaram aproximadamente entre 16 e 29 segundos por execução, com médias registradas de cerca de:

- 16,7 s para `f1`;
- 20,4 s para `f2`;
- 27,1 s para `f3`.

Evite afirmar qual critério encerrou cada execução individual, pois essa informação não foi registrada separadamente nos resultados.

### 13. Planejamento experimental

Explique que o GVNS é estocástico. Uma única execução não seria suficiente para avaliar estabilidade. Por isso, foram feitas cinco execuções independentes para cada objetivo, totalizando 15 execuções.

As sementes foram:

`42, 123, 456, 789 e 1011`.

Explique que sementes fixas permitem reproduzir as decisões pseudoaleatórias e comparar resultados. Todos os demais parâmetros foram mantidos entre objetivos e execuções.

Para cada execução foram registrados:

- melhor valor bruto da função objetivo, sem penalidade;
- solução final;
- viabilidade estrutural;
- viabilidade de qualidade;
- histórico de convergência;
- tempo de execução.

As estatísticas calculadas sobre as cinco execuções foram:

- mínimo;
- média;
- desvio-padrão amostral, com denominador `n − 1`;
- máximo.

### 14. Resultados completos

Apresente a tabela das 15 execuções:

| Semente | f1 em R$ | f2 | f3 |
|---:|---:|---:|---:|
| 42 | 60.680.000 | 2,373029 | 1,453254 |
| 123 | 60.440.000 | 2,373828 | 1,450865 |
| 456 | 60.660.000 | 2,372757 | 1,452281 |
| 789 | 60.300.000 | 2,373927 | 1,436169 |
| 1011 | 60.480.000 | 2,373844 | 1,443334 |

Apresente também as estatísticas:

| Objetivo | Mínimo | Média | Desvio-padrão amostral | Máximo |
|---|---:|---:|---:|---:|
| f1, em R$ | 60.300.000 | 60.512.000 | 159.123 | 60.680.000 |
| f2 | 2,372757 | 2,373477 | 0,000543 | 2,373927 |
| f3 | 1,436169 | 1,447180 | 0,007289 | 1,453254 |

Destaque as melhores soluções encontradas:

- `f1 = R$ 60.300.000`, obtido com a seed 789;
- `f2 = 2,372757`, obtido com a seed 456;
- `f3 = 1,436169`, obtido com a seed 789.

Afirme explicitamente que todas as 15 soluções finais foram verificadas como estruturalmente viáveis e dentro dos limites de SiO₂ e Al₂O₃.

### 15. Interpretação dos resultados

#### Custo, f1

- a solução inicial custava R$ 60.400.000, mas era inviável em qualidade;
- a melhor solução final viável custou R$ 60.300.000;
- além de corrigir a qualidade, o GVNS reduziu o custo bruto em aproximadamente 0,17%;
- o desvio-padrão de R$ 159.123 corresponde a aproximadamente 0,26% da média;
- as cinco execuções terminaram em uma faixa relativamente estreita, indicando baixa dispersão nas sementes avaliadas.

Não diga que a solução final é apenas R$ 100.000 mais barata e, por isso, a melhoria é pequena sem contextualizar: o desafio era manter ou reduzir o custo enquanto se eliminavam 12 violações de qualidade.

#### Sílica, f2

- o valor bruto caiu de 23,48 na solução inicial inviável para cerca de 2,37 nas soluções finais viáveis;
- a redução é próxima de 90%;
- o desvio-padrão amostral é 0,000543;
- o coeficiente de variação é aproximadamente 0,0229%;
- foi o objetivo mais estável entre as sementes testadas.

#### Alumina, f3

- o valor bruto caiu de 14,91 na solução inicial inviável para cerca de 1,44 nas soluções finais viáveis;
- a redução também é próxima de 90%;
- o desvio-padrão é 0,007289, aproximadamente 0,50% da média;
- foi mais sensível às escolhas estocásticas do que `f2`, embora os valores finais ainda sejam próximos em termos absolutos.

#### Curvas de convergência

Use os três gráficos fornecidos. Explique que:

- cada linha corresponde a uma semente;
- a maior parte das melhorias aparece nas primeiras iterações;
- depois há estabilização e melhorias ocasionais;
- as curvas ajudam a observar velocidade de melhoria e dispersão entre execuções;
- elas não constituem prova de ótimo global.

#### Composição das melhores soluções

Se as figuras `melhor_solucao_f1.png`, `melhor_solucao_f2.png` e `melhor_solucao_f3.png` estiverem disponíveis, explique:

- cada barra representa uma pilha;
- cada segmento representa o número de caminhões de um minério;
- a altura total representa o total de caminhões exigido pela massa da pilha;
- as composições diferem porque cada objetivo favorece combinações químicas e econômicas distintas.

### 16. Validação técnica e controle de qualidade

Explique que o trabalho passou por uma rodada final de validação:

- foram mantidos os seis testes existentes;
- foram adicionados três testes para valores exatamente no limite, dentro da tolerância e realmente fora da tolerância;
- os nove testes passaram;
- as 15 combinações de objetivo e semente foram reexecutadas;
- os custos foram reproduzidos exatamente;
- `f2` e `f3` foram confirmados com tolerância de `5 × 10^-7`;
- a seed 123 de `f1` reproduziu R$ 60.440.000 e passou na validação de qualidade;
- todas as soluções foram verificadas estrutural e quimicamente;
- os gráficos e números foram mantidos porque a reprodução confirmou os valores;
- o relatório foi compilado duas vezes e revisado visualmente;
- os arquivos auxiliares e caches foram excluídos da entrega.

Explique que essa validação final não modificou o algoritmo ou os resultados. A principal correção funcional foi a tolerância de `1e-9` para evitar um falso erro de ponto flutuante.

### 17. Estrutura da entrega

Mostre como os arquivos finais se relacionam:

- `sol_inicial.py`: representação, dados, construção, objetivos e validadores;
- `vizinhancas.py`: N1, N2 e N3;
- `vns.py`: fitness, penalidade, SHAKE, busca local, VND, GVNS, experimentos e gráficos;
- `relatorio.pdf`: formulação, método, pseudocódigo, planejamento e resultados;
- `apresentacao.pdf`: síntese da metaheurística e dos resultados;
- `README.md`: instruções de instalação, execução, testes e reprodução;
- `requirements.txt`: dependências Python;
- figuras de convergência e composição das melhores soluções.

Informe que o comando oficial para reproduzir os 15 experimentos é:

`python vns.py`

E que os testes são executados com:

`python -m pytest -v`

### 18. Avaliação crítica das escolhas

Inclua uma seção que avalie as decisões sem exagerar suas garantias.

#### Pontos fortes

- representação simples e diretamente ligada aos caminhões;
- preservação das restrições estruturais por construção;
- combinação de movimentos locais e movimentos de maior amplitude;
- N3 permite ajustes químicos coordenados;
- SHAKE e VND equilibram diversificação e intensificação;
- penalização permite explorar regiões temporariamente inviáveis em qualidade;
- sementes fixas e testes aumentam a reprodutibilidade;
- todas as soluções finais foram validadas.

#### Limitações

- cinco sementes fornecem evidência experimental, mas não uma caracterização estatística exaustiva;
- não existe prova de ótimo global;
- os parâmetros adotados não passaram por uma análise de sensibilidade extensa;
- o critério exato que encerrou cada execução não foi registrado separadamente;
- a amostragem de vizinhos reduz custo, mas pode deixar de avaliar movimentos promissores;
- a Entrega 1 trata os objetivos separadamente e ainda não analisa formalmente os compromissos multiobjetivo;
- os pesos de penalidade foram calibrados pela escala, mas poderiam ser estudados de forma sistemática em trabalhos futuros.

### 19. Conclusão final

Feche o vídeo retomando a pergunta central e respondendo de forma objetiva:

- o grupo formalizou três problemas mono-objetivo sobre o mesmo conjunto viável;
- criou uma representação baseada em caminhões e uma solução construtiva estruturalmente válida;
- implementou um GVNS com SHAKE, VND e três vizinhanças;
- tratou restrições estruturais por preservação ou rejeição e restrições químicas por penalização;
- realizou 15 execuções reproduzíveis;
- obteve soluções finais viáveis em todos os casos;
- encontrou custo mínimo de R$ 60.300.000, `f2` mínimo de 2,372757 e `f3` mínimo de 1,436169;
- reduziu os desvios químicos brutos em aproximadamente 90% em relação à solução inicial inviável;
- observou maior estabilidade em `f2` e maior sensibilidade às sementes em `f3`;
- produziu uma base consistente para as etapas posteriores, nas quais os objetivos poderão ser considerados conjuntamente.

Finalize reforçando que o principal resultado não é apenas um número menor. O método conseguiu transformar uma composição inicial barata, porém inadequada em qualidade, em soluções que conciliam as regras operacionais com cada objetivo estudado.

## Direção visual do vídeo

Use visuais técnicos e limpos, com linguagem gráfica consistente. Sempre que possível:

- represente os minérios por cores fixas;
- mostre caminhões ou blocos entrando nas pilhas;
- use um diagrama com dois equipamentos e cinco pilhas para cada um;
- anime N1 como uma substituição, N2 como uma troca entre pilhas e N3 como duas substituições simultâneas;
- apresente SHAKE como uma perturbação e VND como refinamento em sequência;
- destaque em cores diferentes restrições estruturais e restrições de qualidade;
- mostre a função de fitness como objetivo mais penalidade;
- use fluxograma para o GVNS;
- mostre a tabela das 15 execuções antes das estatísticas agregadas;
- apresente os gráficos reais de convergência fornecidos nas fontes;
- destaque os melhores valores sem ocultar média, dispersão e máximo;
- identifique claramente quando uma solução é inviável, temporariamente penalizada ou final e viável.

Evite imagens genéricas de mineração que não ajudem a explicar o método. Priorize diagramas, equações legíveis, animações da representação e gráficos reais do trabalho.

## Estilo de narração

- Narração em português do Brasil.
- Tom acadêmico, claro e natural.
- Defina cada sigla na primeira ocorrência: VNS, GVNS, VND e SHAKE.
- Explique as equações em linguagem verbal depois de mostrá-las.
- Use exemplos curtos para tornar N1, N2 e N3 intuitivas.
- Faça transições que conectem problema, modelagem, código, experimento e conclusão.
- Não apenas enumere itens; explique as relações de causa e efeito.
- Não omita as justificativas das decisões do grupo.
- Não sobrecarregue uma única tela com texto ou equações.
- Exiba fontes, unidades e rótulos legíveis.

## Checklist obrigatório antes de finalizar o vídeo

Confirme que o vídeo incluiu:

- [ ] o contexto das dez pilhas e dos dois equipamentos;
- [ ] os três objetivos mono-objetivo;
- [ ] todos os entregáveis exigidos;
- [ ] variável, parâmetros, restrições e funções objetivo;
- [ ] o papel não ativo de FeT;
- [ ] a representação por vetores de caminhões;
- [ ] as duas fases da heurística construtiva;
- [ ] a inviabilidade química da solução inicial;
- [ ] o motivo para usar GVNS;
- [ ] N1, N2 e N3 e a justificativa específica de N3;
- [ ] SHAKE, First Improvement e VND;
- [ ] penalidade, pesos e separação entre inviabilidade estrutural e de qualidade;
- [ ] aceitação estrita;
- [ ] parâmetros e critérios de parada;
- [ ] cinco sementes por objetivo e 15 execuções;
- [ ] a tabela completa dos resultados;
- [ ] mínimo, média, desvio-padrão amostral e máximo;
- [ ] interpretação das curvas de convergência;
- [ ] melhores valores por objetivo;
- [ ] viabilidade das 15 soluções finais;
- [ ] tolerância numérica e nove testes aprovados;
- [ ] limitações e ausência de prova de ótimo global;
- [ ] conclusão conectada às exigências da Entrega 1.

Se algum desses itens não puder ser sustentado pelas fontes fornecidas, sinalize a ausência em vez de inventar informações.

---

## Fontes recomendadas para adicionar ao NotebookLM

1. `Case Pilhas UFMG e Cassotis.pdf` ou o PDF oficial equivalente do enunciado.
2. `relatorio.pdf`.
3. `sol_inicial.py`.
4. `vizinhancas.py`.
5. `vns.py`.
6. `README.md`.
7. `CHANGELOG.md`.
8. `resultados_vns.txt`.
9. `convergencia_f1.png`, `convergencia_f2.png` e `convergencia_f3.png`.
10. `melhor_solucao_f1.png`, `melhor_solucao_f2.png` e `melhor_solucao_f3.png`.
11. `apresentacao.pdf`, como referência de síntese e identidade visual.
