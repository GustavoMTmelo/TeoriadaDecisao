# Parte 2 — códigos atualizados da entrega

Esta pasta contém cópias dos códigos atuais, preservando nomes e estrutura
de importação. Os arquivos originais do projeto não foram movidos nem alterados.
`MANIFESTO_COPIA.json` registra os hashes SHA-256 dos 106 arquivos copiados.

## Conteúdo solicitado

| Componente | Arquivos principais |
|---|---|
| Códigos atualizados da Entrega 1 | `sol_inicial.py`, `vizinhancas.py`, `vns.py`, `avaliacao.py`, `busca.py`, `contratos.py`, `registros.py`, `reproduzir_tp1.py`, `relatorio_tp1.py` |
| Soma ponderada e ε-restrito | `escalarizacoes.py`, com normalização em `normalizacao.py` e busca comum em `busca.py` |
| Diferentes configurações e repetições | `experimentos.py`, `executar_tp2.py`, `configs/tp2.json`, `configs/tp2_agenda.json` |
| Identificação das soluções não dominadas | `pareto.py`; integração e exportação em `experimentos.py` |
| Tabelas e figuras do relatório | `figuras_tp2.py`, `relatorio_tp2.py`; para TP1, `reproduzir_tp1.py`, `relatorio_tp1.py` e funções de plotagem em `vns.py` |
| Verificação e reprodução | `verificar_tp2.py`, `tests/`, `test_vizinhancas.py`, configurações de integração e arquivos de dependências |

Também foram incluídos os dados de entrada embutidos em `sol_inicial.py`,
as referências congeladas em `results/referencias_tp1.json`, a campanha TP1
corrigida e a integração TP2 reduzida usada pelos testes. Os scripts auxiliares,
o piloto e as configurações VS Code foram copiados junto com os módulos.

## Executar a partir desta pasta

Abra esta pasta no VS Code ou entre nela pelo terminal. Para um ambiente próprio:

```powershell
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r requirements-tp2-lock.txt
& ./.venv/Scripts/python.exe -m pytest -q
```

O ambiente validado do projeto usa CPython 3.13.5. Se esta pasta permanecer
dentro do projeto original, o ambiente existente pode ser usado sem reinstalar:

```powershell
& ../.venv/Scripts/python.exe -m pytest -q
```

Para uma execução curta, com saída própria:

```powershell
python experimentos.py --config configs/tp2_integracao.json --output tmp/integracao
python verificar_tp2.py --output tmp/integracao
python figuras_tp2.py --campanha tmp/integracao --output tmp/integracao/figuras
python relatorio_tp2.py --campanha tmp/integracao
```

Para revalidar ou regenerar as tabelas e seis figuras do TP1 copiado:

```powershell
python reproduzir_tp1.py --output results/tp1_corrigido --verificar
python reproduzir_tp1.py --output results/tp1_corrigido --regerar
```

Para executar uma nova campanha completa TP2 e gerar os produtos:

```powershell
python executar_tp2.py
python relatorio_tp2.py
```

Esse último fluxo executa 160 buscas com teto de 10.000 avaliações cada,
audita os resultados e gera seis projeções PNG/PDF, tabelas CSV/LaTeX,
análise JSON e fragmento de resultados do relatório. Não foi repetido na
montagem desta cópia.

## Resultados da campanha oficial já realizada

Os registros completos da campanha oficial, com aproximadamente 4 GiB,
permanecem em `../results/tp2/` no projeto original. Eles não foram duplicados
nesta pasta de códigos. Para regenerar os produtos desses dados numa cópia
isolada, copie também esse diretório para `results/tp2/` e execute:

```powershell
python figuras_tp2.py --campanha results/tp2 --output results/tp2/figuras
python relatorio_tp2.py --campanha results/tp2
```

O fonte cumulativo completo do relatório e o PDF compilado permanecem no
projeto original (`../relatorio.tex` e `../build/latex/relatorio.pdf`).
Esta pasta reúne os códigos e rotinas pedidos, com os arquivos de apoio.
