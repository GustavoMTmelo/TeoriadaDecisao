# Etapa 1 — Base técnica para retomar o TP2

Registro de 18/10/2026. Escopo: revisar o que já existe e tornar explícitas
as escolhas da continuidade. Nenhum resultado novo de otimização é produzido
nesta etapa. Prazo confirmado: 18/10/2026 às 23:59, Brasília.

## O que estamos tentando obter

Uma receita para cada uma das dez pilhas, respeitando massa, disponibilidade,
compatibilidade e limites químicos. Cada receita completa tem três medidas:
custo em reais, desvio quadrático de SiO₂ e desvio quadrático de Al₂O₃.
Quanto menor, melhor em cada medida. O TP2 procura alternativas de compromisso;
a escolha de uma ação por métodos multicritério pertence ao TP3.

## Decisões existentes que serão preservadas

| Decisão | Justificativa e consequência |
|---|---|
| Manter GVNS, construtiva e N1/N2/N3 | Reutiliza a base exigida pelo trabalho. Não redesenhar os operadores nesta etapa |
| Usar os dois métodos | Soma ponderada e ε-restrito são ambos parte da entrega |
| Normalizar por referências TP1 | Permite combinar objetivos de unidades diferentes sem confundir pesos com penalidades |
| Preservar 16 configurações por método | Explora diferentes preferências e limites sem criar uma malha nova antes do piloto |
| Comparar com mesmo teto de avaliações | Dá um orçamento comum por subproblema; registrar também o esforço efetivamente usado |
| Priorizar viabilidade no TP2 | Uma solução com escalar menor não compensa violar as restrições |
| Guardar a melhor viável e observar candidatos rejeitados | A trajetória aceita não contém necessariamente todas as boas alternativas visitadas |
| Filtrar Pareto em três dimensões | Um ponto pode parecer dominado numa projeção 2D e continuar relevante em 3D |
| Reutilizar sementes-base oficiais | 42, 123, 456, 789 e 1011; cada método/configuração recebe seed efetiva derivada por SHA-256 |
| Relatório único cumulativo | Corrigir e ampliar `relatorio.tex`, preservando o conteúdo relevante do TP1 |

Essas decisões já constam da implementação e do planejamento recebido.
Não são novas escolhas atribuídas ao grupo nesta sessão. O teto definitivo
de avaliações continua condicionado à análise conjunta do piloto.

## Como os métodos funcionam

Para cada objetivo, `g_j(x) = (f_j(x) - a_j) / (b_j - a_j)`.
Os extremos são os valores observados nas 15 soluções finais viáveis do TP1:

| Objetivo | a_j | b_j |
|---|---:|---:|
| f1 | 60.300.000 | 65.840.000 |
| f2 | 2,3727567955223003 | 6,705745397999253 |
| f3 | 1,4361688772162504 | 5,995129496821073 |

Usar a precisão completa de `results/referencias_tp1.json` nos cálculos.
São referências empíricas: uma solução nova pode ter g negativo ou maior
que 1. Isso não causa truncamento nem é, por si só, erro de normalização.

**Soma ponderada:** minimizar `w1*g1 + w2*g2 + w3*g3`. Há 15 triplas de
pesos em passos de 0,25 cuja soma é 1, mais o centro (1/3, 1/3, 1/3).
Os pesos representam preferências entre objetivos normalizados, não multas
por violação física. Por exemplo, (1,0,0) prioriza custo sem dispensar qualidade.

**ε-restrito:** minimizar `g1`, sujeito a `g2 <= epsilon2` e
`g3 <= epsilon3`, além das restrições físicas originais. Os limites são
0, 1/3, 2/3 e 1 em produto cartesiano, totalizando 16 pares. Um teto zero
exige um desvio no máximo igual ao mínimo empírico TP1 daquele objetivo;
não significa desvio bruto zero. A combinação dos dois tetos pode ser difícil
para a busca, mesmo quando cada extremo isolado foi observado no TP1.

## Como a busca decide e registra

1. A construtiva produz a receita inicial; a estrutura é validada antes dos objetivos.
2. SHAKE perturba a receita e VND explora as vizinhanças.
3. Cada candidato estruturalmente válido é avaliado e observado antes do filtro
   de aceitação. Avaliações iniciais e repetidas contam no orçamento.
4. A comparação prioriza viabilidade, depois violação, escalar e desempate
   determinístico. A melhor viável permanece separada da incumbente da trajetória.
5. No VND, após o limite de cinco reinícios, melhoria mantém a vizinhança;
   ausência de melhoria avança. Não descrever o limite como cinco melhorias.
6. A campanha persiste os candidatos viáveis observados e reconstrói o arquivo
   não dominado; composições iguais agregam todas as origens.

A violação TP2 soma excessos químicos relativos ao quadrado e, no ε-restrito,
excessos dos dois limites normalizados. Qualidade e ε usam tolerância 1e-9.
Na ponderada, o desempate usa soma dos g e o vetor g; no ε-restrito, soma
dos dois desvios normalizados e seus valores. Empate completo mantém a incumbente.

Paradas propostas: 200 iterações externas, 60 iterações externas sem melhoria
ou teto de 10.000 avaliações por busca, o que ocorrer primeiro. O teto ainda
será validado no piloto; N1/N2/N3, 20 amostras, k máximo 3 e cinco reinícios
permanecem iguais entre os métodos.

## O que significa uma campanha completa

- Uma **run** é uma busca de uma configuração com sua seed efetiva.
- Uma **varredura** executa as 16 configurações de um método para uma seed-base.
- A coleta oficial tem **2 métodos × 5 varreduras × 16 configurações = 160 runs**.
- O piloto usa seeds-base 90001/90002 e diretório próprio; não integra a coleta oficial.
- Uma run concluída sem viável encontrada deve permanecer no resumo. É
  diferente de uma run não executada e não prova inviabilidade matemática.

As cinco repetições são as varreduras, e não os 160 subproblemas individuais.
Os arquivos por repetição mostram variabilidade; a união por método mostra
o conjunto não dominado combinado, mantendo proveniência.

## Produtos que ainda faltam

| Produto | Etapa do roteiro | Como verificaremos |
|---|---|---|
| Configuração e protocolo do piloto | 2 | Entradas, saída e critérios explícitos |
| Piloto e decisão do orçamento | 3 | Tempo, esforço e viabilidade auditados; decisão registrada |
| Campanha oficial | 4 | 160 registros contabilizados e auditor aprovado |
| Gerador, seis projeções e tabelas | 5 | Dados oficiais, unidades e cinco repetições identificadas |
| Metodologia cumulativa | 6 | Fórmulas e pseudocódigo conferidos contra implementação |
| Análise comparativa | 7 | Compromissos, regiões e variabilidade sustentados pelos dados |
| PDF e pacote final | 8 | Reprodução, auditoria e revisão visual; envio pelo grupo |

## Participação conjunta e pendências

O assistente prepara os artefatos e evidências de cada etapa. O usuário e o
grupo participam das decisões de orçamento, da interpretação dos resultados,
da revisão e do envio final. Não é necessário reimplementar os métodos ou
reexecutar o TP1 para começar o piloto.

A revisão técnica está registrada e a etapa 1 está concluída para continuidade.
O usuário confirmou que o TP1 foi compilado com LaTeX em outro computador.
Usaremos esse ambiente para compilar e revisar o PDF cumulativo na etapa 8;
não é necessário instalar Tectonic ou uma distribuição local para executar
os experimentos. Nenhum compilador novo foi instalado nesta sessão.

O ambiente Python já foi validado no setup. A compilação final permanece
uma validação obrigatória: disponibilidade histórica do outro computador
não equivale à confirmação de que o fonte atualizado compila.
