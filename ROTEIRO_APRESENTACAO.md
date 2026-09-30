# Roteiro de apresentação — TP1 Case Cassotis

**Duração planejada:** aproximadamente 8 minutos e 30 segundos

**Limite:** 10 minutos

**Margem para trocas e imprevistos:** aproximadamente 1 minuto e 30 segundos

## 1. Felipe — Capa e agenda

**Slides:** 1 e 2

**Tempo:** 40 segundos

> Boa noite. Nosso trabalho trata da otimização mono-objetivo da formação de pilhas de minério no case Cassotis. Nós modelamos e resolvemos separadamente três objetivos: custo, desvio de sílica e desvio de alumina. Primeiro apresentaremos o problema e a representação da solução. Depois, explicaremos a metaheurística GVNS e as principais decisões do grupo. Por fim, mostraremos o planejamento experimental e os resultados.

**Transição:** “O Gustavo vai apresentar o problema e os objetivos considerados.”

## 2. Gustavo — Problema e objetivos

**Slide:** 3

**Tempo:** 1 minuto

> O problema consiste em definir a composição de dez pilhas que alimentam dois equipamentos de sinterização. Cada elemento da solução representa um caminhão de 2 mil toneladas de um minério. A composição deve atender à massa exata de cada pilha, à compatibilidade entre minério e equipamento, às disponibilidades mínima e máxima e aos limites químicos de sílica e alumina. Resolvemos três versões mono-objetivo sobre o mesmo conjunto viável. A primeira minimiza o custo total de aquisição. A segunda minimiza o desvio quadrático de sílica em relação às metas. A terceira faz o mesmo para a alumina. Assim, as restrições permanecem iguais e somente o objetivo otimizado muda.

**Transição:** “O Henry explica agora como representamos e construímos a solução inicial.”

## 3. Henry — Representação e solução inicial

**Slide:** 4

**Tempo:** 1 minuto e 10 segundos

> A solução é um conjunto de dez vetores, um para cada pilha. Cada posição do vetor identifica o minério de um caminhão. Essa representação facilita substituições dentro de uma pilha e trocas entre pilhas. A heurística construtiva começa inserindo as quantidades mínimas obrigatórias de cada minério. Depois, completa as pilhas com o minério compatível de menor custo. Ela gera uma solução estruturalmente válida, com custo de 60,4 milhões de reais, mas ainda com 12 violações de qualidade. Por isso, usamos essa solução apenas como ponto inicial. Durante a busca, as restrições estruturais continuam preservadas, enquanto o GVNS ajusta a composição química.

**Transição:** “A partir desse ponto inicial, o Lucas apresenta o fluxo completo do GVNS.”

## 4. Lucas — Pseudocódigo do GVNS

**Slide:** 5

**Tempo:** 1 minuto e 20 segundos

> O algoritmo começa com a solução construtiva e controla o número de iterações sem melhoria. Em cada iteração externa, iniciamos com intensidade de perturbação igual a um. O SHAKE perturba a melhor solução, e o VND faz o refinamento local usando as três vizinhanças. A comparação utiliza a função de fitness, que soma o objetivo e a penalização de qualidade. Se a solução refinada melhorar estritamente a incumbente, ela é aceita e a intensidade volta para um. Caso contrário, aumentamos a intensidade até o máximo de três. Ao final de cada ciclo, atualizamos o contador de estagnação. A execução termina ao alcançar o limite de iterações ou o limite sem melhoria. Por fim, a solução retornada é validada estrutural e quimicamente.

**Transição:** “A Luisa detalha as vizinhanças e as regras de busca e viabilidade.”

## 5. Luisa — Vizinhanças, busca e inviabilidade

**Slides:** 6 e 7

**Tempo:** 2 minutos

> Utilizamos três vizinhanças. A N1 substitui um caminhão por outro minério compatível. A N2 troca caminhões entre duas pilhas, desde que exista compatibilidade cruzada com os equipamentos. Como decisão adicional do grupo, a N3 substitui dois caminhões da mesma pilha simultaneamente. Ela permite realizar ajustes químicos combinados que poderiam exigir um passo intermediário pior se fossem feitos apenas pela N1. O SHAKE aplica de um a três movimentos aleatórios para diversificar a busca. Depois, o VND percorre N1, N2 e N3 com First Improvement e retorna à N1 sempre que encontra melhora. Usamos amostragem de vizinhos para controlar o tempo computacional.
>
> As restrições estruturais são mantidas por construção ou pela rejeição do movimento. Já as violações de sílica e alumina são penalizadas na função de fitness. O peso é de dez elevado a doze para o custo e dez elevado a quatro para os objetivos químicos, considerando suas diferentes escalas. Tanto o VND quanto o laço externo aceitam apenas melhorias estritas. Cada execução permite até 200 iterações, para após 60 iterações sem melhoria, avalia 20 vizinhos por busca local e limita o VND a cinco reinícios.

**Transição:** “O Thales encerra com os experimentos e os principais resultados.”

## 6. Thales — Experimentos, resultados e conclusão

**Slides:** 8 e 9

**Tempo:** 2 minutos e 20 segundos

> Para avaliar o comportamento estocástico, executamos cinco sementes fixas para cada objetivo, totalizando 15 execuções. Em todas elas, os parâmetros foram mantidos e as soluções finais passaram pelas verificações estruturais e de qualidade. Para o custo, o melhor resultado foi 60,3 milhões de reais. Para sílica, o melhor valor foi 2,372757 e houve a menor dispersão relativa entre as sementes. Para alumina, o melhor valor foi 1,436169, com uma sensibilidade um pouco maior às sementes.
>
> As curvas mostram que a maior parte da melhoria ocorre nas primeiras iterações, seguida de estabilização. Em comparação com a solução construtiva inicial, os desvios de sílica e alumina foram reduzidos em aproximadamente 90%, além de eliminarmos as violações de qualidade. Concluímos que o GVNS conseguiu combinar diversificação, por meio do SHAKE, e intensificação, por meio do VND. A vizinhança N3 ampliou a capacidade de ajuste da composição, e a penalização permitiu tratar a qualidade sem perder a viabilidade estrutural. Assim, o método produziu soluções finais viáveis em todas as 15 execuções. Obrigado.

## Resumo dos tempos

| Integrante | Slides | Tempo |
|---|---:|---:|
| Felipe | 1–2 | 0:40 |
| Gustavo | 3 | 1:00 |
| Henry | 4 | 1:10 |
| Lucas | 5 | 1:20 |
| Luisa | 6–7 | 2:00 |
| Thales | 8–9 | 2:20 |
| **Total de fala** | **1–9** | **8:30** |

## Orientações rápidas

- Não ler títulos, tabela inteira ou pseudocódigo linha por linha.
- Apontar apenas os valores destacados e explicar a conclusão de cada slide.
- Fazer as transições em uma frase e trocar de apresentador sem pausa longa.
- Ensaiar uma vez com cronômetro. Se passar de 9 minutos, reduzir exemplos e preservar os resultados e as justificativas de N3, penalização e critérios de parada.
