# Otimização de Pilhas de Minério — Teoria da Decisão UFMG 2026/2

Case Cassotis: otimização de custo e qualidade na formação de pilhas de minério para sinterização.

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

## Executar os 15 experimentos

```bash
python vns.py
```

Esse é o comando oficial da Entrega 1. Ele executa cinco rodadas para cada
objetivo (`f1`, `f2` e `f3`) com as sementes fixas
`[42, 123, 456, 789, 1011]` e atualiza os seis gráficos.

Para também salvar a saída completa em `resultados_vns.txt` no PowerShell:

```powershell
python vns.py | Tee-Object -FilePath resultados_vns.txt
```

Em shells compatíveis com redirecionamento POSIX:

```bash
python vns.py | tee resultados_vns.txt
```

## Executar os testes

```bash
python -m pytest -v
```

## Reproduzir os resultados

As sementes fixas permitem reproduzir os valores da tabela do relatório com
`python vns.py`, usando a mesma versão do código e dependências compatíveis.

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

## Resultados obtidos

| Objetivo | Mínimo | Média | Desvio-padrão amostral | Máximo |
|---|---:|---:|---:|---:|
| `f1` (R$) | 60.300.000 | 60.512.000 | 159.123 | 60.680.000 |
| `f2` | 2,372757 | 2,373477 | 0,000543 | 2,373927 |
| `f3` | 1,436169 | 1,447180 | 0,007289 | 1,453254 |

Todas as soluções finais são estruturalmente viáveis e atendem aos limites de
qualidade de SiO₂ e Al₂O₃.
