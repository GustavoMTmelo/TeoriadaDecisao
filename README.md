# Otimização de Pilhas de Minério — Teoria da Decisão UFMG 2026/2

Case Cassotis: otimização de custo e qualidade na formação de pilhas de minério para sinterização.

## Pré-requisitos

- Python 3.12+
- matplotlib >= 3.11

```bash
pip install matplotlib
```

Não há outras dependências externas; `statistics`, `copy`, `random` e `collections` são bibliotecas padrão.

## Estrutura do repositório

```
.
├── sol_inicial.py        # Dados do problema + heurística construtiva + funções de avaliação
├── vizinhancas.py        # Estruturas de vizinhança N1, N2, N3
├── vns.py                # GVNS mono-objetivo (Entrega 1)
├── test_vizinhancas.py   # Testes unitários das vizinhanças
├── resultados_vns.txt    # Saída dos experimentos (gerado automaticamente)
├── convergencia_f*.png   # Curvas de convergência (geradas automaticamente)
├── melhor_solucao_f*.png # Composição das melhores soluções (geradas automaticamente)
└── latex_relatorio       # Relatório LaTeX da Entrega 1 (compilar com pdflatex)
```

## Como executar — Entrega 1

### Rodar os experimentos completos (15 execuções: 5 por objetivo)

```bash
python3 vns.py
```

Isso executa 5 runs independentes para f1, f2 e f3 com seeds fixas [42, 123, 456, 789, 1011] e salva:
- `resultados_vns.txt` — valores individuais e estatísticas
- `convergencia_f1.png`, `convergencia_f2.png`, `convergencia_f3.png`
- `melhor_solucao_f1.png`, `melhor_solucao_f2.png`, `melhor_solucao_f3.png`

Tempo estimado: ~10 minutos.

### Rodar os testes unitários das vizinhanças

```bash
python3 -m pytest test_vizinhancas.py -v
```

ou

```bash
python3 test_vizinhancas.py
```

## Reprodução dos resultados

Os resultados são completamente reproduzíveis. As sementes fixas garantem que rodar `python3 vns.py` em qualquer máquina com Python 3.12 e matplotlib produza os mesmos valores da Tabela de resultados do relatório.

## Parâmetros do algoritmo (vns.py)

| Parâmetro | Valor | Descrição |
|---|---|---|
| MAX_ITER | 200 | Iterações externas por execução |
| K_MAX | 3 | Intensidades de perturbação |
| MAX_AMOSTRAS | 20 | Vizinhos amostrados por chamada de busca local |
| MAX_RESTARTS_VND | 5 | Reinícios internos máximos do VND |
| MAX_SEM_MELHORA | 60 | Parada antecipada por estagnação |

## Resultados obtidos (Entrega 1)

| Objetivo | Mínimo | Média | Desvio-padrão | Máximo |
|---|---|---|---|---|
| f1 (R$) | 60.300.000 | 60.512.000 | 159.123 | 60.680.000 |
| f2 | 2,372757 | 2,373477 | 0,000543 | 2,373927 |
| f3 | 1,436169 | 1,447180 | 0,007289 | 1,453254 |

Todas as soluções são viáveis quanto à qualidade (SiO₂ e Al₂O₃ dentro dos limites).
