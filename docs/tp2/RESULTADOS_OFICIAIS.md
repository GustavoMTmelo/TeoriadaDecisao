# Resultados oficiais TP2 — leitura para o grupo

Campanha executada em 18/10/2026, após aprovação do teto de **10.000 avaliações
por busca**. São cinco varreduras por abordagem, cada uma com 16 configurações:
160 buscas e 1.600.000 avaliações. As sementes-base são 42, 123, 456, 789 e 1011.

## O que foi encontrado

| Indicador | Soma ponderada | ε-restrito |
|---|---:|---:|
| Buscas | 80 | 80 |
| Com solução viável encontrada | 80 | 45 |
| Sem solução viável encontrada | 0 | 35 |
| Composições físicas na união ND 3D do método | 3.961 | 1.206 |
| Vetores de objetivos distintos nessa união | 3.830 | 1.182 |
| Menor custo (R$) | 60.740.000 | 60.460.000 |
| Menor desvio SiO₂ (p.p.²) | 2,406656 | 3,039322 |
| Menor desvio Al₂O₃ (p.p.²) | 1,452043 | 2,324603 |
| Tempo somado dos solvers (s) | 955,32 | 881,86 |

Os mínimos de uma coluna **não pertencem todos à mesma composição**.
As receitas completas e suas origens estão em `results/tp2/analise.json`,
campo `alternativas_extremas`, e nos arquivos Pareto.
As uniões são filtradas separadamente por método, não uma fronteira conjunta.

A união ponderada domina estritamente 66,24% dos **vetores distintos** da
união ε-restrita; no sentido inverso, 3,26%. Não há vetor exatamente igual
nem composição física comum entre as duas uniões. Essa cobertura compara
apenas as amostras encontradas e não prova superioridade global.

As 35 buscas ε sem viável são os mesmos sete pares em todas as sementes:
`eps_00`, `eps_01`, `eps_02`, `eps_03`, `eps_10`, `eps_20`, `eps_30`.
Todos têm ao menos um limite normalizado zero. Não encontrar uma solução
com o orçamento adotado não prova inviabilidade matemática desses pares.

## Como interpretar as figuras

Cada método tem três projeções: custo × SiO₂, custo × Al₂O₃ e SiO₂ × Al₂O₃.
Cor e símbolo identificam cada varredura. A filtragem é feita em três
objetivos antes da projeção; um ponto aparentemente dominado em 2D pode
continuar ND em 3D. Os eixos usam os mesmos limites entre os dois métodos.

As repetições alcançaram regiões projetadas amplamente sobrepostas.
A ponderada teve intervalos marginais mais estáveis; o ε-restrito apresentou
maior variação de extensão em custo e Al₂O₃. A sobreposição não significa
que os conjuntos de receitas ou os conjuntos tridimensionais sejam iguais.

## Evidência e duração

- Auditoria integral aprovada: 160 execuções, 487.200 candidatos observados,
  12 arquivos Pareto e 17.802 entradas exportadas somando repetições e uniões.
  A mesma alternativa pode estar em mais de um arquivo.
- Coleta completa com persistência/consolidação: **46,01 minutos**.
- Primeira auditoria e geração de figuras: **13,29 minutos**.
- Total da invocação oficial: **59,30 minutos**. Ajustes posteriores de
  apresentação não integram esse tempo original e não repetem as buscas.
- Suíte de testes: **173 aprovados**. Os hashes das 11 fontes científicas,
  configuração e referência foram conferidos contra o manifesto da campanha.
- Não foi repetida a campanha inteira em outra máquina: a auditoria recalcula
  resultados e proveniência, mas não equivale a uma segunda campanha.

Fontes numéricas: `results/tp2/analise.json`, `resumo.json`,
`medicao_oficial.json` e `figuras/manifesto_figuras.json`.

## O que precisamos concluir juntos

1. O grupo confere a interpretação dos compromissos e da variabilidade.
2. No computador com LaTeX, compilar as fontes cumulativas e revisar todas
   as páginas, conforme [checklist de entrega](CHECKLIST_ENTREGA_TP2.md).
3. Entregar o PDF revisado com código e resultados. O envio permanece sob
   controle do grupo; o ZIP de fontes não substitui o PDF final.

Escolher uma única ação e aplicar métodos multicritério pertence ao TP3.
