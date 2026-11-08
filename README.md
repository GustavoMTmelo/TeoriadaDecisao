# Otimização de Pilhas de Minério — Teoria da Decisão UFMG 2026/2

Case Cassotis: otimização de custo e qualidade na formação de pilhas de minério para sinterização.

## VS Code e conclusão da Entrega 2

O [diagnóstico e plano de conclusão de 18/10](docs/tp2/PLANO_CONCLUSAO_18_10.md)
registra o estado atual, as pendências TP2-13 a TP2-17 e a divisão proposta de
trabalho até **18/10/2026 às 23:59 (Brasília)**, prazo confirmado pelo grupo.

A continuidade está registrada em [execução das etapas atuais](docs/tp2/EXECUCAO_13_EM_ANDAMENTO.md).
O relatório fonte já inclui metodologia, resultados e discussão TP2;
**`relatorio.pdf` ainda é o PDF anterior do TP1**. O MiKTeX já foi instalado
neste computador e a compilação local gera `build/latex/relatorio.pdf`.
Consulte o [setup LaTeX local](docs/tp2/SETUP_LATEX_LOCAL.md).

O workspace está configurado em `.vscode/`: interpretador
`.venv/Scripts/python.exe`, testes pytest, tarefas de terminal e perfis F5.
Abra esta pasta no VS Code e selecione **TP2: integração local (8 buscas)**
para executar. A saída local fica em `tmp/integracao_vscode`, separada dos
resultados versionados. Em **Terminal > Run Task**, há testes e auditores.
Se o VS Code já lembrar outro interpretador, use **Python: Select Interpreter**
para escolher a `.venv`. O projeto executa pelo terminal, sem servidor web.

Para recriar o ambiente no Windows com um CPython 3.12+ instalado:

```powershell
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
& ./.venv/Scripts/python.exe -m pytest -q
```

Use um CPython Windows; se `python` apontar para MSYS2, invoque o executável
do CPython pelo caminho completo. Nesta máquina foi validado Python 3.13.5.
As extensões de Python e LaTeX e a distribuição MiKTeX estão instaladas.
Reabra o VS Code e os terminais para reconhecer o PATH atualizado.

## Continuidade: planejamento da Entrega 2

Em 15/10/2026 foi preparada a [auditoria atual](docs/tp2/AUDITORIA.md), com o feedback da professora, e o [plano multiobjetivo](docs/tp2/PLANEJAMENTO.md), acompanhado da [matriz de requisitos](docs/tp2/MATRIZ_REQUISITOS.md) e do [backlog de issues](docs/tp2/BACKLOG.md). Prazo atualizado informado pelo grupo: **18/10/2026**. As tarefas TP2-01 a TP2-06 foram autorizadas; o [registro de execução](docs/tp2/EXECUCAO_01_06.md) acompanha testes e resultados.

Em 18/10, o escopo TP2-07 a TP2-12B foi autorizado e implementado:
normalização, dois métodos escalares, núcleo GVNS comum, agenda reproduzível,
persistência/retomada e arquivo Pareto 3D. Consulte o
[registro de execução e auditoria](docs/tp2/EXECUCAO_07_12.md).
Na continuidade autorizada, a campanha oficial TP2-13 foi concluída e
auditada; figuras, análise e fontes cumulativas foram desenvolvidas.
O fechamento do PDF e o envio seguem pendentes no computador do grupo.

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

### Piloto e geração de figuras

O [protocolo experimental](docs/tp2/PROTOCOLO_EXPERIMENTAL.md) registra o piloto
de 64 buscas auditadas e a aprovação de **10.000 avaliações por busca oficial**.
Para reproduzir ou retomar o piloto:

```powershell
& ./.venv/Scripts/python.exe -X utf8 piloto_tp2.py
```

O runner mede tempo total e auditoria; salva em `results/piloto_tp2_lote/`.
`results/piloto_tp2/` preserva a tentativa interrompida anterior à otimização
de consolidação e não é resultado oficial. O ambiente atual está congelado
em `requirements-tp2-lock.txt` (CPython 3.13.5), separado do lock histórico.

O gerador exige campanha completa e auditada. Para uma prévia reduzida:

```powershell
& ./.venv/Scripts/python.exe -X utf8 figuras_tp2.py --campanha results/integracao_tp2_final --output tmp/figuras_integracao_tp2 --titulo "Integração reduzida"
```

Produz seis PNG e seis PDFs, CSVs de pontos/proveniência e resumo por
repetição, tabela LaTeX e manifesto de hashes. Após a coleta oficial,
`python figuras_tp2.py` usa `results/tp2/` e gera em `results/tp2/figuras/`.
As projeções mantêm ND 3D por repetição e escalas comuns entre métodos.

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

A coleta oficial usa o teto aprovado após o piloto. Para executar/retomar com
progresso, medição persistida e auditoria/figuras em uma única passagem:

```powershell
& ./.venv/Scripts/python.exe -X utf8 executar_tp2.py
```

Não executar duas instâncias na mesma saída. O comando direto continua disponível:

```bash
python experimentos.py --config configs/tp2.json --output results/tp2
python verificar_tp2.py --output results/tp2
```

Esse comando executa **160 buscas**: dois métodos × cinco varreduras × 16
configurações, com teto aprovado de 10.000 avaliações por busca.
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

Depois da auditoria e geração de figuras oficiais, `python relatorio_tp2.py`
gera análise JSON e fragmento LaTeX a partir dos produtos verificados.
O empacotador `python empacotar_tp2.py` monta fontes e resultados em `dist/`,
excluindo o PDF antigo e dados brutos do piloto. O pacote não substitui a
compilação e revisão do PDF final.

Neste computador, com MiKTeX instalado, o script PowerShell compila pelo menos duas vezes,
até estabilizar as referências (limite de cinco passagens), em
`build/latex/` e preserva o PDF versionado da raiz:

```powershell
./scripts/compilar_relatorio.ps1
```

Depois de conferir o resultado, `./scripts/compilar_relatorio.ps1 -PublicarPdf`
atualiza `relatorio.pdf` na raiz. A compilação local foi validada com MiKTeX;
o script também encontra a instalação do usuário caso o PATH do terminal
ainda não tenha sido atualizado.

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
O relatório atualizado lê o fragmento LaTeX gerado da campanha em
`relatorio.tex`. O `relatorio.pdf` da raiz ainda é o documento anterior;
a versão cumulativa TP2 precisa ser compilada e revisada no computador com
LaTeX, conforme o [checklist de fechamento](docs/tp2/CHECKLIST_ENTREGA_TP2.md).

## Campanha oficial TP2 — 18/10/2026

As **160 buscas** terminaram com **1.600.000 avaliações**. A auditoria
integral aprovou 487.200 observações e os 12 arquivos Pareto. Foram encontradas
soluções viáveis em 80/80 buscas ponderadas e 45/80 buscas ε-restritas; as 35
ausências permanecem nos resultados e não provam inviabilidade matemática.
As uniões por método contêm 3.961 e 1.206 composições ND, respectivamente.

Coleta: 46,01 min; primeira auditoria e geração de figuras: 13,29 min.
Os gráficos foram inspecionados e sua exportação ajustada para evitar cortes.
O relatório cumulativo inclui método, resultados gerados e discussão.
Detalhes e interpretação em [RESULTADOS_OFICIAIS.md](docs/tp2/RESULTADOS_OFICIAIS.md);
dados em `results/tp2/analise.json` e figuras em `results/tp2/figuras/`.

Última suíte: **173 testes aprovados**. As fontes científicas, configuração e
referências coincidem com os hashes congelados no manifesto. A campanha não
foi repetida integralmente em outra máquina. Compilação/revisão do PDF e envio
seguem o [checklist](docs/tp2/CHECKLIST_ENTREGA_TP2.md).

## Resultados históricos — antes das correções

| Objetivo | Mínimo | Média | Desvio-padrão amostral | Máximo |
|---|---:|---:|---:|---:|
| `f1` (R$) | 60.300.000 | 60.512.000 | 159.123 | 60.680.000 |
| `f2` | 2,372757 | 2,373477 | 0,000543 | 2,373927 |
| `f3` | 1,436169 | 1,447180 | 0,007289 | 1,453254 |

O log histórico não sustentava sozinho a viabilidade individual das 15
rodadas. A campanha corrigida posterior registrou e revalidou as 15 soluções;
suas evidências estão em `results/tp1_corrigido/`, sem substituir os logs antigos.
