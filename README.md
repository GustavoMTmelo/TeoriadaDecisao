# Otimização de Pilhas de Minério — Teoria da Decisão UFMG 2026/2

Case Cassotis: otimização de custo e qualidade na formação de pilhas de minério para sinterização.

## Continuidade: planejamento da Entrega 2

Em 15/10/2026 foi preparada a [auditoria atual](docs/tp2/AUDITORIA.md), com o feedback da professora, e o [plano multiobjetivo](docs/tp2/PLANEJAMENTO.md), acompanhado da [matriz de requisitos](docs/tp2/MATRIZ_REQUISITOS.md) e do [backlog de issues](docs/tp2/BACKLOG.md). Prazo atualizado informado pelo grupo: **18/10/2026**. As tarefas TP2-01 a TP2-06 foram autorizadas; o [registro de execução](docs/tp2/EXECUCAO_01_06.md) acompanha testes e resultados.

Em 18/10, o escopo TP2-07 a TP2-12B foi autorizado e implementado:
normalização, dois métodos escalares, núcleo GVNS comum, agenda reproduzível,
persistência/retomada e arquivo Pareto 3D. Consulte o
[registro de execução e auditoria](docs/tp2/EXECUCAO_07_12.md).
A campanha oficial TP2-13 e as figuras/análises/relatório TP2-14 a TP2-17
continuam posteriores.

Os resultados antigos estão preservados em `resultados_vns.txt` e nas figuras
da raiz. A implementação corrigida guarda a melhor viável observada, valida
cada rodada e salva composições e objetivos cruzados. Os registros completos
da nova campanha ficam em `results/tp1_corrigido/`.

## Pré-requisitos

- Python 3.12+
- `matplotlib`
- `pytest`
- Uma distribuição LaTeX com `pdflatex` e os pacotes `amsmath`, `amssymb`,
  `graphicx`, `float`, `booktabs`, `array`, `geometry`, `siunitx`, `caption`,
  `titlesec`, `algorithms`, `algorithmicx` e `color`

```bash
python -m pip install -r requirements.txt
```

Para reproduzir o ambiente validado das tarefas TP2-01 a TP2-06, use
`python -m pip install -r requirements-lock.txt` em um ambiente virtual Python
3.12. Os contratos compartilhados estão em `contratos.py`. O comando
`python -m pytest -q` inclui os testes novos em `tests/` e os testes anteriores.

`statistics`, `copy`, `random` e `collections` fazem parte da biblioteca padrão.

## Estrutura do repositório

```text
.
├── sol_inicial.py        # Dados, heurística construtiva e funções de avaliação
├── vizinhancas.py        # Estruturas de vizinhança N1, N2 e N3
├── vns.py                # GVNS mono-objetivo (Entrega 1)
├── test_vizinhancas.py   # Testes unitários das vizinhanças e da validação
├── requirements.txt      # Dependências Python
├── resultados_vns.txt    # Log salvo da execução oficial
├── convergencia_f*.png   # Curvas de convergência geradas pelo algoritmo
├── melhor_solucao_f*.png # Composição das melhores soluções
├── relatorio.tex         # Fonte LaTeX da Entrega 1
└── relatorio.pdf         # Relatório final compilado
```

## Reproduzir as 15 buscas corrigidas, tabelas, referências e figuras

```bash
python reproduzir_tp1.py --output results/nova_campanha_tp1
```

Esse comando cria um manifesto e executa cinco rodadas por objetivo (`f1`,
`f2`, `f3`), com sementes `[42, 123, 456, 789, 1011]`. A saída deve estar vazia
para preservar campanhas anteriores. Ao concluir, revalida independentemente
as 15 composições e produz seis gráficos, CSV de 15 vetores cruzados, matriz
3×3 das melhores soluções, estatísticas e `referencias_tp1.json` com extremos
empíricos e origem de cada valor. Uma rodada sem viável impede congelar
referências oficiais.

Para conferir a campanha salva ou regenerar seus produtos sem repetir buscas:

```bash
python reproduzir_tp1.py --output results/tp1_corrigido --verificar
python reproduzir_tp1.py --output results/tp1_corrigido --regerar
```

O verificador recalcula todas as composições, confere referências e integridade
de tabelas, estatísticas e figuras. O manifesto distingue hashes do código de
coleta e de consolidação, registra parâmetros, versões e motivos de parada.
`normalizacao.py` constrói, carrega e verifica a referência e aplica a fórmula
min–max sem truncar valores externos ao intervalo empírico.

Para guardar também a saída textual de uma nova execução no PowerShell:

```powershell
python reproduzir_tp1.py --output results/nova_campanha_tp1 | Tee-Object -FilePath resultados_tp1_corrigido.txt
```

O retorno de `gvns(...)` agora é `ResultadoBusca`: use `melhor_viavel` apenas
quando `status == "viavel"`. A trajetória por fitness fica em `melhor_busca`.
Cada chamada de `executar_experimento` salva registros JSON v1 em
`results/tp1_corrigido/execucoes/`, incluindo falhas explícitas, além de CSV e
estatísticas dos retornos viáveis. A leitura em `registros.py` recalcula os
objetivos e validações da composição. Curvas usam a melhor viável, com lacunas
antes de encontrar viabilidade. Para escolher outra saída, use
`python vns.py --output results/outra_campanha`.

Em shells compatíveis com redirecionamento POSIX:

```bash
python reproduzir_tp1.py --output results/nova_campanha_tp1 | tee resultados_tp1_corrigido.txt
```

## Executar os testes

```bash
python -m pytest -v
```

## Multiobjetivo: configuração, campanha e retomada

`busca.resolver(config, referencia, seed, limites, observar=None)` atende aos
dois métodos e ao modo mono. `vns.resolver` encaminha à mesma implementação;
`vns.gvns` conserva a interface histórica para reproduzir o TP1 publicado.
N1/N2/N3, construtiva e dados físicos são preservados. A observação ocorre
antes da aceitação e mantém a melhor viável separada da trajetória.
O orçamento inclui a avaliação inicial e cada avaliação repetida; vale
também no SHAKE e no VND. Estruturas inválidas são contadas separadamente.

As escalas são `g_j=(f_j-a_j)/(b_j-a_j)`, com extremos cruzados das 15 finais
TP1 viáveis. Os extremos são empíricos, por isso g pode sair de [0,1].
Intervalos não finitos ou degenerados (limiar relativo 1e-12) são rejeitados.
A soma ponderada minimiza `sum(w_j*g_j)`; pesos devem ser finitos, não
negativos e somar 1 com tolerância absoluta 1e-12. A malha H=4 mais centro
tem 16 configurações. O ε-restrito minimiza g1 e mantém g2≤ε2 e g3≤ε3,
além de todas as restrições físicas; a malha cartesiana 4×4 também tem 16.
No TP2 a comparação prioriza viabilidade, depois violação, escalar e
desempate determinístico. Tolerâncias de qualidade e ε são 1e-9.

Para uma verificação reduzida com duas sementes externas à campanha oficial:

```bash
python experimentos.py --config configs/tp2_integracao.json --output results/minha_integracao
python verificar_tp2.py --output results/minha_integracao
```

O mesmo comando de execução retoma a saída existente, revalidando cada run
completo antes de reutilizá-lo. Configuração, referência, dados, versões e
hashes dos módulos devem coincidir; arquivos temporários não contam como runs
concluídos. A retomada recupera também os candidatos viáveis observados, com
suas composições, objetivos, auditoria dos excessos químicos/ε e proveniência.
Uma interrupção preserva os runs concluídos; a run interrompida recomeça
integralmente. Resultados corrompidos são rejeitados para investigação.

A infraestrutura oficial está pronta para a etapa TP2-13:

```bash
python experimentos.py --config configs/tp2.json --output results/tp2
python verificar_tp2.py --output results/tp2
```

Esse comando executa **160 buscas**: dois métodos × cinco varreduras × 16
configurações, com teto inicial de 10.000 avaliações por busca. O teto segue
a proposta do plano e ainda deverá ser avaliado no piloto de TP2-13.
As sementes-base `[42,123,456,789,1011]` identificam as repetições; cada seed
efetiva vem dos primeiros oito bytes SHA-256 do JSON compacto
`[base_seed,metodo,config_id]`. A [agenda completa](configs/tp2_agenda.json)
registra as 160 identidades e sementes. Cada busca tem RNG próprio.

Os resultados incluem `manifesto.json`, registros individuais em `execucoes/`,
`resumo.json`, `resumo.csv` e arquivos `pareto/<metodo>_<semente-base>.json`
e `pareto/<metodo>_uniao.json`. A dominância usa os três objetivos brutos;
composições fisicamente iguais agregam todas as origens. Composições distintas
com vetor idêntico permanecem disponíveis. Runs sem viável ficam no resumo;
isso não prova inviabilidade matemática do subproblema.

A [campanha reduzida salva](results/integracao_tp2_final/README.md)
serve de evidência de integração e retomada, sem substituir a campanha oficial.

## Reproduzir os resultados

Sementes, código, dependências e parâmetros do manifesto permitem reproduzir
a campanha corrigida. `python vns.py --output ...` permanece como entrada
simples para as buscas/registros, mas a consolidação completa TP2-06 usa
`reproduzir_tp1.py`, como indicado acima.

## Compilar o relatório

Execute duas vezes para atualizar referências e numeração:

```bash
pdflatex -interaction=nonstopmode -halt-on-error relatorio.tex
pdflatex -interaction=nonstopmode -halt-on-error relatorio.tex
```

## Parâmetros do algoritmo

| Parâmetro | Valor | Descrição |
|---|---:|---|
| `MAX_ITER` | 200 | Iterações externas por execução |
| `K_MAX` | 3 | Intensidades de perturbação |
| `MAX_AMOSTRAS` | 20 | Vizinhos amostrados por chamada de busca local |
| `MAX_RESTARTS_VND` | 5 | Reinícios internos máximos do VND |
| `MAX_SEM_MELHORA` | 60 | Parada antecipada por estagnação |

## Resultados corrigidos — TP2-06

Todas as 15 soluções finais foram revalidadas individualmente e por uma rotina
independente. Os registros completos, seis figuras, matriz cruzada e manifesto
estão em [`results/tp1_corrigido/`](results/tp1_corrigido/README.md).

| Objetivo | Mínimo | Média | Desvio-padrão amostral | Máximo |
|---|---:|---:|---:|---:|
| `f1` (R$) | 60.300.000 | 60.504.000 | 164.560,02 | 60.680.000 |
| `f2` (p.p.²) | 2,372757 | 2,373477 | 0,000543 | 2,373927 |
| `f3` (p.p.²) | 1,436169 | 1,447140 | 0,007254 | 1,453254 |

As referências congeladas para a normalização estão em
[`results/referencias_tp1.json`](results/referencias_tp1.json). Elas usam os
três objetivos das 15 composições, com extremos empíricos e origem rastreável.
O relatório atualizado lê o fragmento LaTeX gerado da campanha; o fonte e o
PDF corrigidos permanecem em `relatorio.tex` e `relatorio.pdf`.

## Resultados históricos — antes das correções

| Objetivo | Mínimo | Média | Desvio-padrão amostral | Máximo |
|---|---:|---:|---:|---:|
| `f1` (R$) | 60.300.000 | 60.512.000 | 159.123 | 60.680.000 |
| `f2` | 2,372757 | 2,373477 | 0,000543 | 2,373927 |
| `f3` | 1,436169 | 1,447180 | 0,007289 | 1,453254 |

O relatório histórico declara viabilidade estrutural e química de todas as
soluções finais. A validação individual e seu registro para as 15 execuções
ainda precisam ser concluídos, conforme a auditoria vinculada acima.
