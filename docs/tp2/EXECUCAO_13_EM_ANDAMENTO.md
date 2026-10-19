# Continuidade TP2 — piloto, figuras e metodologia

## Autorização e decisões

Em 18/10/2026 o usuário solicitou iniciar o desenvolvimento seguindo o plano
e esclareceu que o TP1 foi compilado com LaTeX em outro computador.
Esse ambiente será usado para a compilação final; não foi instalado Tectonic
nem uma distribuição LaTeX nesta máquina. O PDF versionado ainda é o TP1;
a fonte em evolução não equivale à entrega final compilada.

## Estado por etapa

| Etapa | Estado | Evidência / pendência |
|---|---|---|
| 0 — setup | Concluída | Ambiente, VS Code e validação inicial |
| 1 — decisões | Concluída | `DECISOES_ETAPA_1.md`, compilação no outro computador |
| 2 — preparar piloto | Concluída | Configuração, runner, protocolo e lock local |
| 3 — executar/avaliar piloto | Concluída | 64/64 runs auditadas; usuário aprovou teto de 10.000 |
| 4 — campanha oficial | Coleta concluída; auditoria em andamento | 160/160 buscas, 1.600.000 avaliações; fontes iguais ao piloto |
| 5 — figuras | Gerador validado com integração | Dados oficiais pendentes |
| 6 — metodologia | Fonte inicial implementada | Revisão, orçamento final e compilação pendentes |
| 7 — análise | Pendente | Requer resultados oficiais |
| 8 — pacote e PDF | Pendente | Requer frentes anteriores |

## Piloto e desempenho

São duas sementes externas, 16 configurações por método e teto de 10.000
avaliações: 64 runs, até 640.000 avaliações. A primeira tentativa foi
interrompida ao identificar cópias sucessivas e agregação custosa no arquivo
Pareto; dois registros completos permanecem em `results/piloto_tp2/`.

Foi implementada consolidação em lote antes da campanha oficial. A ordenação
lexicográfica dos objetivos permite filtrar sem copiar todo o arquivo por
observação; composição e origens são agrupadas antes das cópias defensivas.
A função incremental permanece como referência e mantém sua interface.
`experimentos.py` usa lotes por run e por união. Novos hashes exigiram novo
diretório de piloto desde o início.

O auditor revalida cada candidato e indexa a origem com a identidade física
SHA-256 da composição, evitando varreduras repetidas por origem exportada.
Consolida por varredura e reconstrói as uniões a partir desses arquivos,
sem manter todas as composições da campanha na memória até o fim.

## Figuras e relatório

`figuras_tp2.py` audita os dados e gera seis projeções, preservando ND em 3D
e origens por repetição. Eixos têm escalas comuns entre métodos e f1 em
milhões de reais. Exporta PNG/PDF, dois CSVs, tabela LaTeX e manifesto.
Os seis gráficos da prévia `tmp/figuras_integracao_tp2/` foram inspecionados
visualmente; não são resultados oficiais.

`relatorio.tex` inclui `docs/tp2/METODOLOGIA_TP2.tex` após os resultados TP1.
Foram acrescentados normalização, formulações, malhas, comparação,
inviabilidade, pseudocódigo, orçamento, varreduras e reprodutibilidade.
O orçamento oficial não é apresentado como aprovado. O fonte precisa de
compilação e revisão visual no ambiente LaTeX do grupo.

## Validações

- Suíte completa após runner, gerador e consolidação: **167 passaram em 14,14 s**.
- Após ajustar o auditor: **35 testes focais passaram em 7,38 s**, incluindo
  rejeição de adulterações, ausência de viável, origem e integração.
- Integração real nova: oito buscas, 260 observados, seis arquivos e 179
  entradas exportadas; auditor aprovado.
- **Os seis arquivos Pareto novos são idênticos aos históricos**, comparando
  os dados completos, inclusive composições e origens.
- Lote comparado à inserção incremental em cinco ordens aleatórias de
  150 observações/30 composições: igualdade completa em todos os casos.
- Amostra real de 200 candidatos: igualdade completa; 0,451 s incremental e
  0,017 s em lote. Os 7.423 observados completos: 1,118 s e 186 ND.
- JSONs, compilação sintática dos módulos e `git diff --check` conferidos.

## Próximo ponto de decisão

Piloto concluído: 32/32 ponderadas e 18/32 ε-restritas viáveis; 640.000
avaliações, 200.496 observados, seis arquivos e 8.752 entradas auditadas.
Uniões com 2.703 composições ponderadas e 870 ε-restritas. Coleta aproximada
de 17,13 min, auditoria atual de 7,44 min e volume de cerca de 1,87 GB.
As duas sementes falharam nos mesmos sete pares ε mais restritivos.

A recomendação de manter 10.000 avaliações foi aprovada explicitamente pelo
usuário, com autorização para iniciar as 160 buscas oficiais. O detalhe das medições,
incluindo reconstrução aproximada da duração, está no protocolo e no JSON.
O processo do runner foi encerrado apenas durante a auditoria antiga
redundante, depois de concluir buscas e obter aprovação do auditor atual.

Teste adicional de origem ambígua: os dez testes de auditoria passaram em
1,69 s. A nova verificação completa do piloto aprovou todos os observados
em 446,42 s. O conjunto de testes tem agora 168 casos; a execução completa
mais recente foi de 167 antes dessa adição, com validação focal posterior.

## Início da campanha oficial

Em 18/10/2026, após a aprovação: todas as versões do lock local, os 11 hashes
científicos do piloto, teto 10.000 e agenda de 160 identidades foram conferidos.
Nenhuma fonte científica será modificada durante a coleta.
O runner `executar_tp2.py` foi validado em oito buscas reduzidas, com auditoria
e 16 produtos de figuras/tabelas; preserva a medição da coleta antes da auditoria.
Execução oficial iniciada às aproximadamente 20:25 (Brasília).

O relatório metodológico já registra a decisão final de orçamento e os dados
piloto como fundamentação, sem misturá-los à comparação oficial.

## Preparação da análise e pacote durante a coleta

`relatorio_tp2.py` verifica hashes dos produtos e fontes já auditados,
gera contabilidade, intervalos, esforço, comparação bidirecional por
dominância estrita e um fragmento de resultados LaTeX. Foi validado apenas
com a integração enquanto os dados oficiais ainda não estavam completos.
`empacotar_tp2.py` inclui fontes e resultados oficiais, exclui dados brutos
do piloto e o PDF TP1 antigo, e impede empacotar campanha não auditada.
O script LaTeX compila até estabilizar referências, com limite de cinco
passagens, sem substituir o PDF da raiz antes de conclusão bem-sucedida.

Suíte completa após esses componentes: **172 testes passaram em 19,36 s**.

## Retomada após interrupção da conversa

O processo original continuou em segundo plano. A coleta encerrou 160/160
buscas sem reutilização, com 1.600.000 avaliações. Tempo de coleta:
2.760,61 s (46,01 min); tempo somado dos solvers: 1.837,18 s (30,62 min).
A medição foi salva antes da auditoria, ainda com fase pendente.
Não iniciar outra execução na mesma saída nem repetir buscas.

Contabilidade preliminar do resumo: 80/80 ponderadas e 45/80 ε-restritas
com viável; 35 ausências nos mesmos sete pares ε, em todas as sementes.
As uniões têm 3.961 e 1.206 composições, respectivamente. Esses números
serão incorporados ao relatório após aprovação do auditor em andamento.

O consolidador foi ampliado para guardar exemplos de alternativas completas
nos extremos, com composição e origens, sem inventar um vetor ideal pela
combinação de mínimos. Discussão em `DISCUSSAO_TP2.tex`, ainda não incluída
no documento principal antes da auditoria. Suíte final: **173 testes
passaram em 16,15 s**.

## Auditoria oficial aprovada e integração do relatório

A invocação oficial encerrou com sucesso: 160 buscas, 1.600.000 avaliações,
487.200 observações recalculadas, 12 arquivos Pareto e 17.802 entradas
exportadas conferidas. Fase `auditada_com_figuras`; auditoria e figuras em
797,26 s (13,29 min), duração total da invocação de 59,30 min.

`relatorio_tp2.py` foi executado sobre os dados oficiais auditados. As uniões
confirmaram 3.961/1.206 composições e 3.830/1.182 vetores distintos
(ponderada/ε). Coberturas estritas bidirecionais: 66,24% dos vetores ε
dominados pela ponderada e 3,26% no sentido inverso. Não há vetor ou
composição comum entre as uniões. Extremos, intervalos e falhas coincidem
com a discussão preparada.

Resultados e discussão foram incluídos no `relatorio.tex`, após metodologia
e TP1 corrigido. Conferência estática de seis fontes TeX validou inclusões,
imagens, ambientes e oito referências; não substitui compilação.
Suíte final: **173 testes aprovados em 15,25 s**. `git diff --check` limpo.

As seis projeções oficiais foram inspecionadas. A exportação foi ajustada
para evitar cortes de rótulos/legendas, mantendo os mesmos dados; uma
regeneração com auditoria está em andamento. VS Code agora inclui tarefas
para análise, pacote e compilação no computador com LaTeX.

O [resumo para o grupo](RESULTADOS_OFICIAIS.md) explica os resultados; o
[checklist](CHECKLIST_ENTREGA_TP2.md) registra evidências por requisito e
o fechamento que falta no computador com compilador.

## Conferência final das figuras e preparação do pacote

A regeneração após o ajuste visual terminou com sucesso. Nova auditoria
integral aprovou os mesmos 160 registros, 487.200 observações, 12 arquivos
Pareto e 17.802 entradas. As seis imagens finais foram inspecionadas, com
legendas, eixos e rótulos completos. A correção também foi validada numa
campanha reduzida isolada; os resultados oficiais não foram reexecutados.
`relatorio_tp2.py` foi executado novamente sobre o manifesto final.

O pacote gerado em `dist/tp2_fontes_resultados.zip` preserva fontes,
configurações, dependências, resultados oficiais completos, figuras e
documentação; exclui `.venv`, temporários, dados brutos de piloto e PDF TP1
antigo. O empacotador só conclui com CRC aprovado e conjunto de entradas
igual ao manifesto. Tamanho e SHA-256 ficam no manifesto externo ao ZIP.
O conteúdo representa fontes/resultados para compilação, não PDF TP2 final.
A montagem foi aprovada com 303 arquivos de fontes/resultados mais manifesto
e orientação internos. A documentação de fechamento foi incorporada à versão
final do pacote; usar seu manifesto externo para tamanho e SHA-256 exatos.

Compilação, revisão de todas as páginas e envio continuam pendentes no
computador com LaTeX. Nenhuma publicação, push ou envio foi realizado.

## Instalação LaTeX local solicitada pelo usuário

O usuário pediu instalar LaTeX nesta máquina. MiKTeX instalado via winget no
escopo do usuário, atualizado para compilador 26.5, com instalação automática
de pacotes e PATH registrados. VS Code configurado para `pdflatex` em duas
passagens; script local também encontra o executável sem renovar o terminal.

Compilação cumulativa aprovada com 30 páginas, referências estabilizadas e
sem erros/transbordamentos no log final. Um pequeno excesso de linha na
discussão foi corrigido sem alterar números. Todas as páginas renderizadas
foram inspecionadas; tabelas/discussão também conferidas em tamanho ampliado.
PDF em `build/latex/relatorio.pdf`; PDF TP1 da raiz preservado para substituição
após aprovação. Detalhes em [SETUP_LATEX_LOCAL.md](SETUP_LATEX_LOCAL.md).
O pacote anterior não foi refeito nesta instalação e não contém o novo PDF
nem as configurações locais posteriores. Nenhum envio foi realizado.
