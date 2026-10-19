# Plano conjunto de conclusão do TP2 — 18/10/2026

Prazo confirmado pelo grupo neste chat: **18/10/2026 às 23:59, horário de Brasília**.
Este documento atualiza o diagnóstico operacional sem substituir o backlog e
a matriz de requisitos. Após o planejamento, o usuário autorizou desenvolvimento
e campanha oficial com 10.000 avaliações por busca.
**Situação: 160/160 buscas concluídas e auditadas; análise e fontes cumulativas
integradas. Seis figuras finais conferidas; pacote de fontes/resultados gerado
e validado.**
**Atualização posterior:** usuário solicitou instalação LaTeX local; MiKTeX
instalado e relatório de 30 páginas compilado e inspecionado neste computador.
Ver [setup local](SETUP_LATEX_LOCAL.md). Aprovação do grupo e envio permanecem
pendentes; referências ao outro computador abaixo registram a decisão anterior.

## Avaliação de `TP2.md`

Na avaliação inicial, o [guia de passagem para o grupo](TP2.md) estava
**condizente com o plano e com o estado local conferido**:
branch `tp2/07-12-multiobjetivo`, HEAD `2787ceb`;
métodos e infraestrutura presentes; `figuras_tp2.py` e `results/tp2/` ausentes.
Os mínimos/máximos apresentados correspondem, com arredondamento, à referência
canônica. As malhas de 16 pesos e 16 pares ε correspondem a `escalarizacoes.py`.
As pendências TP2-13 a TP2-17 e a distinção entre integração e coleta oficial
coincidem nos dois documentos. Não há divergência de escopo científico.

| Ponto a ajustar no guia | Avaliação e tratamento neste plano |
|---|---|
| Horário de envio não registrado | Informação superada: usuário confirmou 23:59 de 18/10/2026, Brasília |
| Caminhos do Henry e instrução de novo clone | Contexto de outra máquina; aqui já há checkout e `.venv` prontos. Não repetir clone ou trocar branch |
| Python 3.14.4 e lock antigo | Evidência histórica válida, diferente do setup atual CPython 3.13.5. Congelar as versões da nova coleta |
| PRs “abertos nesta conferência” | Registro histórico do guia; estado remoto não foi consultado nesta revisão e não é necessário para começar localmente |
| Fórmula com `g\<sub\>j` e tolerâncias com `\<super\>` | Marcação escapada prejudica leitura. Na revisão editorial, usar `g_j=(f_j-a_j)/(b_j-a_j)`, `1e-9` e `1e-12` |
| Divisão entre vários colegas | Adaptada abaixo para trabalho por etapas entre usuário e assistente, com revisão do grupo quando pertinente |
| Compilação LaTeX | Dependência operacional que o guia não resolve; escolher o ambiente antes de fechar o relatório |

O guia foi preservado nesta revisão. Ele serve como visão geral; este arquivo
passa a ser o roteiro operacional do trabalho conjunto. O pedido de avaliação
e planejamento não autoriza executar a campanha ou desenvolver as pendências.

## Diagnóstico inicial e atualização da continuidade

O projeto resolve a composição de dez pilhas de minério por GVNS com três
objetivos de minimização: custo (f1), desvio quadrático de SiO₂ (f2) e de
Al₂O₃ (f3). É um conjunto de programas Python executados no terminal;
não há servidor ou interface gráfica a iniciar para a Entrega 2.

Fluxo principal:

`sol_inicial` + `vizinhancas` → `busca` → `avaliacao` + `normalizacao` +
`escalarizacoes` → `experimentos` → `registros` + `pareto` → `verificar_tp2`.

`vns.py` mantém a interface histórica do TP1; `reproduzir_tp1.py` e
`relatorio_tp1.py` consolidam essa campanha. `contratos.py` define os tipos.
Os módulos estão na raiz, com importações simples e testes em `tests/`.

| Frente | Estado observado | Evidência |
|---|---|---|
| Correções TP1 e referências | Implementadas; dados salvos revalidados nesta análise | 15/15 finais viáveis; 14 produtos e seis figuras conferidos |
| Normalização e dois métodos escalares | Implementados | `normalizacao.py`, `escalarizacoes.py`, testes próprios |
| GVNS comum e orçamento | Implementados | `busca.py`, observação de candidatos, melhor viável separada |
| Agenda, persistência e Pareto 3D | Implementados | `experimentos.py`, `registros.py`, `pareto.py` |
| Integração salva | Auditada nesta análise | Oito buscas, 260 candidatos observados, seis arquivos Pareto, 179 entradas somando arquivos por repetição e união |
| Campanha oficial | Concluída e auditada | 160/160 buscas, 1.600.000 avaliações, 487.200 observações verificadas |
| Figuras e tabelas TP2 | Concluídas e inspecionadas após ajuste de exportação | `results/tp2/figuras/`, seis pares PNG/PDF e tabelas |
| Relatório cumulativo TP2 | Fontes de método, resultados e discussão integradas; PDF pendente | `relatorio.tex`, `analise.json`, fragmentos LaTeX |
| Pacote de fontes/resultados | Gerado e validado; PDF final pendente | `dist/tp2_fontes_resultados.zip` e manifesto externo |

O resultado `codigo_atual_confere=false` na verificação TP1 é esperado: o
código evoluiu depois da coleta. Não significa que as composições ou os
produtos salvos falharam; a referência continua revalidada.

As auditorias antigas descrevem estados anteriores, inclusive caminhos e
máquinas diferentes. Para a situação atual, usar os arquivos efetivos e os
registros `EXECUCAO_01_06.md` e `EXECUCAO_07_12.md`.

## Ambiente local e VS Code

- CPython local: **3.13.5**, em `.venv/`, com matplotlib e pytest instalados.
- O `python` global aponta para MSYS2; os atalhos usam explicitamente o
  executável da `.venv` para evitar esse conflito.
- Extensões Python, Pylance, Debugger e LaTeX Workshop já estão instaladas.
- `.vscode/settings.json`: interpretador local, UTF-8 e descoberta pytest.
- `.vscode/launch.json`: F5 para integração local, auditoria salva ou testes.
- `.vscode/tasks.json`: testes, verificação TP1, integração local, campanha
  oficial e auditoria. A campanha oficial é uma ação manual após o piloto.
- `pdflatex` e `latexmk` não foram encontrados no PATH. O usuário confirmou
  LaTeX em outro computador como ambiente usado no TP1; a compilação final
  será realizada nesse ambiente. Instalação local não é pré-requisito da coleta.

Abrir a raiz deste repositório no VS Code. Se o editor já tiver memorizado
outro Python, executar **Python: Select Interpreter** e selecionar
`.venv/Scripts/python.exe`; a configuração padrão não substitui uma seleção
anterior. Selecionar **TP2: integração local (8 buscas)** e pressionar F5.
Para tarefas, usar **Terminal > Run Task**. Para a suíte, usar a aba Testing.

No PowerShell, sem depender de ativação ou política de scripts:

```powershell
& ./.venv/Scripts/python.exe -m pytest -q
& ./.venv/Scripts/python.exe experimentos.py --config configs/tp2_integracao.json --output tmp/integracao_vscode
& ./.venv/Scripts/python.exe verificar_tp2.py --output tmp/integracao_vscode
```

`tmp/integracao_vscode` é saída local ignorada pelo Git. Rodar novamente retoma
a campanha se o manifesto coincidir. Se mudar Python, versões, código,
referência ou configuração, usar um diretório novo. Não tentar retomar a
campanha histórica com este ambiente: o manifesto também compara versões.

O lock histórico permanece intacto. O ambiente foi instalado com
`requirements.txt`; as versões locais devem ser congeladas no protocolo
antes da campanha oficial. Não declarar este ambiente idêntico ao histórico.

### Verificação realizada no setup inicial

- Suíte completa: **162 testes passaram em 14,77 s** no CPython 3.13.5.
  O runner precisou executar fora do sandbox por restrições de criação dos
  diretórios temporários do pytest; não houve alteração dos testes.
- `pip check`: nenhuma dependência incompatível; matplotlib 3.11.2,
  pytest 8.4.2 e Pillow 13.0.0 instalados. O Pillow difere do lock histórico.
- Nova integração local: **8/8 buscas**, 4.000 avaliações; auditor aprovou
  260 observados, seis arquivos Pareto e 179 entradas exportadas. Cinco buscas
  encontraram viável e três não encontraram, como na integração histórica.
- Segunda execução local: **8/8 reutilizadas** pelo mecanismo de retomada.
- Auditores dos dados versionados TP1 e TP2 aprovados; JSONs do VS Code
  parseados e `git diff --check` sem erros. Fontes dos algoritmos,
  configurações científicas e resultados versionados não foram alterados.
- Na etapa inicial de setup, a campanha oficial, o piloto e a compilação do
  relatório TP2 ainda não tinham sido executados. F5 foi configurado; a validação
  dos comandos ocorreu pelo terminal, sem interação visual com o editor.

Referências de configuração consultadas: [ambientes e configurações Python](https://code.visualstudio.com/docs/python/settings-reference)
e [depuração com debugpy](https://code.visualstudio.com/docs/python/debugging).

## Etapas para fazermos juntos

Cada etapa produz algo revisável. Ao encerrá-la, registramos o que foi feito,
as evidências, decisões e pendências antes de escolher a próxima. O setup está
concluído; a etapa 1 está concluída; o piloto está em preparação/execução.

### Etapa 0 — Setup e ponto de partida — concluída

- **Objetivo:** conseguir executar e testar o código recebido sem alterar os métodos.
- **Já feito:** `.venv`, configurações VS Code, 162 testes aprovados, auditorias
  TP1/integração e execução local reduzida com retomada 8/8.
- **Sua participação na retomada:** abrir o workspace e conferir o interpretador
  selecionado; isso ainda não foi verificado visualmente no editor.
- **Saída:** ambiente pronto e evidências registradas acima. Não repetir buscas
  de integração apenas por iniciar uma nova sessão.

### Etapa 1 — Entender e fechar as decisões da entrega

- **Estado:** concluída. Revisão técnica registrada em
  [DECISOES_ETAPA_1.md](DECISOES_ETAPA_1.md); usuário confirmou compilação
  com LaTeX em outro computador. Validar o fonte final nesse ambiente na etapa 8.
- **Objetivo:** todos entenderem o que será entregue e por quê.
- **Minha parte:** explicar o fluxo do código, normalização, diferença entre
  soma ponderada e ε-restrito, run versus varredura e resultados já disponíveis.
  Relacionar cada pendência ao backlog e esclarecer as escolhas existentes.
- **Sua parte:** trazer dúvidas, materiais adicionais da professora e decisões
  do grupo; confirmar entendimento das malhas e prioridades. Escolher comigo
  onde compilaremos o relatório, pois não há compilador LaTeX no PATH atual.
- **Saída:** lista curta de decisões e roteiro aceito pelo grupo.
- **Conclui quando:** não há dúvida de escopo, responsabilidades ou ambiente
  de compilação. Não envolve executar a campanha.

### Etapa 2 — Preparar o piloto — TP2-13, preparação

- **Estado:** concluída. Configuração, runner e critérios em
  [PROTOCOLO_EXPERIMENTAL.md](PROTOCOLO_EXPERIMENTAL.md).
- **Depende de:** etapa 1.
- **Minha parte:** preparar configuração própria com sementes externas
  90001/90002, saída separada e os mesmos parâmetros de referência da campanha;
  rascunhar `PROTOCOLO_EXPERIMENTAL.md` com métricas e critérios de decisão.
- **Sua parte:** conferir o desenho do piloto, disponibilidade da máquina e
  o tempo que podemos dedicar à coleta antes do fechamento.
- **Saída:** configuração e protocolo revisáveis, ainda sem resultados.
- **Conclui quando:** sabemos o que executar, onde salvar e como avaliar o
  teto proposto de 10.000 avaliações. O piloto não começa nesta preparação.

### Etapa 3 — Rodar e avaliar o piloto — TP2-13, decisão

- **Estado:** concluída. Piloto auditado e usuário aprovou 10.000 avaliações.
  Ver [protocolo e resultados](PROTOCOLO_EXPERIMENTAL.md).
- **Depende de:** etapa 2.
- **Minha parte:** executar o piloto, auditar, medir tempo total, esforço,
  viabilidade e tamanho dos arquivos; apresentar estimativa para 160 buscas.
- **Sua parte:** interpretar comigo as falhas e compromissos de tempo/qualidade;
  decidir o orçamento final antes de congelar a coleta.
- **Saída:** resumo do piloto e protocolo com decisão justificada. Congelar
  dependências, código, referências, configuração e sementes da coleta oficial.
- **Conclui quando:** o orçamento é igual entre métodos, a estimativa cabe no
  prazo e a decisão fica registrada. Falha de busca não justifica trocar seed.

### Etapa 4 — Coletar e auditar os resultados oficiais — TP2-13

- **Estado:** concluída; 160/160 buscas e auditoria integral aprovada.
  Registros e falhas preservados; não é necessário repetir as buscas.
- **Depende de:** etapa 3.
- **Minha parte:** executar sequencialmente 160 buscas, retomar se necessário,
  preservar falhas e aplicar `verificar_tp2.py` na campanha completa.
- **Sua parte:** manter a máquina disponível e revisar comigo o resumo de
  conclusão, as falhas e a correspondência com o protocolo.
- **Saída:** `results/tp2/`, manifesto, 160 registros, resumos e arquivos Pareto
  por varredura e união de cada método; evidência de auditoria.
- **Conclui quando:** 160/160 buscas contabilizadas e auditoria aprovada.
  Runs sem viável encontrada continuam nos resultados; não equivalem a run ausente.

### Etapa 5 — Construir figuras e tabelas — TP2-14

- **Estado:** concluída; seis projeções finais inspecionadas após ajuste de
  exportação e nova auditoria integral aprovada.
- **Depende de:** etapa 4 para produtos oficiais. Desenvolvimento com os dados
  reduzidos pode ser antecipado se você solicitar essa ordem.
- **Minha parte:** criar `figuras_tp2.py`, gerar seis projeções e tabelas a
  partir dos registros auditados; manter identidade visual das cinco repetições
  e todas as origens das composições compartilhadas.
- **Sua parte:** conferir clareza de eixos, escalas, unidades, legendas e quais
  tabelas ajudam a responder às perguntas da professora.
- **Saída:** gerador reproduzível, figuras e tabelas oficiais.
- **Conclui quando:** são três pares de objetivos por método, com dominância
  filtrada em 3D e distinção clara entre repetições e união não dominada.

### Etapa 6 — Escrever a metodologia cumulativa — TP2-15

- **Estado:** fontes cumulativas incorporadas com orçamento final aprovado.
  Revisão do grupo e compilação do PDF continuam pendentes.
- **Depende de:** etapa 3 para os parâmetros definitivos; pode ser antecipada
  durante a coleta a seu pedido, sem apresentar resultados ainda não obtidos.
- **Minha parte:** atualizar o mesmo `relatorio.tex`, preservando TP1 corrigido
  e incluindo formulações, normalização, malhas, política de viabilidade,
  desempates, VND, orçamento, pseudocódigo e protocolo experimental.
- **Sua parte:** revisar comigo as explicações e justificativas; conferir que
  o grupo entende e consegue defender as escolhas descritas.
- **Saída:** texto metodológico cumulativo e prévia compilada no ambiente escolhido.
- **Conclui quando:** fórmulas e pseudocódigo correspondem ao código e as
  escolhas estão justificadas sem alegações de otimalidade ou viabilidade garantida.

### Etapa 7 — Interpretar os resultados juntos — TP2-16

- **Estado:** análise numérica e discussão integradas; revisão do grupo pendente.
- **Depende de:** etapas 4, 5 e 6.
- **Minha parte:** apresentar comparações com números rastreáveis, redigir a
  análise e explicitar limitações da heurística, malhas e orçamento.
- **Sua parte:** discutir os compromissos custo/qualidade, diferenças entre
  métodos e se as repetições alcançaram regiões semelhantes; conferir exemplos.
- **Saída:** resultados, discussão e conclusão no relatório cumulativo.
- **Conclui quando:** as perguntas do enunciado estão respondidas com figuras
  e tabelas; falhas e variabilidade são discutidas sem inferências indevidas.

### Etapa 8 — Revisar e montar a entrega — TP2-17

- **Depende de:** etapas 5 a 7.
- **Minha parte:** verificar suíte e auditores, reprodução dos produtos,
  comandos do README e matriz de requisitos; compilar e revisar visualmente
  o PDF; preparar pacote e lista do conteúdo.
- **Sua parte:** fazer a revisão final comigo, confirmar identificação dos
  integrantes e instruções de submissão; enviar o pacote na plataforma.
- **Saída:** código, dependências, configurações, referências, resultados,
  geradores, figuras e relatório cumulativo em pacote conferido.
- **Conclui quando:** checklist abaixo cumprido e grupo confere o arquivo
  efetivamente enviado até 23:59.

### Ordem e reserva de tempo

Sequência padrão: **0 concluída → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8**.
As etapas 5 e 6 podem avançar durante a coleta mediante escolha explícita de
ordem; isso não implica delegação nem execução automática em paralelo.

O custo da etapa 4 será estimado no piloto. Para planejamento, preparação e
avaliação do piloto podem exigir 45–90 min além das buscas; figuras 1–2 h;
metodologia 1–2 h; análise 45–90 min; revisão/pacote 60–90 min. São estimativas,
não compromisso de duração. Recalcular após o piloto e reservar, se possível,
**22:30–23:59** para fechamento e envio. Não reduzir requisitos obrigatórios
para acomodar o cronograma; adiar melhorias opcionais.

### Protocolo do piloto

Usar sementes externas, não substituir as sementes oficiais por sucesso.
O teto proposto é 10.000 avaliações por subproblema; considerar extremos e
centro da ponderada e limites frouxos/apertados de ε. Uma primeira amostra
curta estima o custo; se houver tempo, completar as duas varreduras externas.
A integração de 500 avaliações comprova funcionamento, mas não valida o
orçamento de qualidade da campanha final.

Medir tempo total, avaliações efetivas, motivo de parada, fração de buscas
com viável por método/configuração, cardinalidade Pareto e volume dos JSONs.
Estimar o custo das 160 buscas com folga para persistência e consolidação.
Fixar o mesmo teto para ambos os métodos e justificar a decisão antes da
coleta. Se o piloto indicar risco de prazo, simplificar a apresentação e
adiar melhorias opcionais; qualquer redução do orçamento deve ser registrada
antes de iniciar a campanha definitiva.

Não mudar fontes ou atualizar dependências no meio da campanha. A retomada
revalida runs concluídos; uma run interrompida recomeça. Não misturar resultados
do piloto com os oficiais nem apagar as buscas sem solução viável.

### Critérios para fechar cada frente

- **Campanha:** 160 buscas contabilizadas; cinco varreduras completas por
  método; cada alternativa publicada com composição e proveniência;
  `verificar_tp2.py` aprovado; falhas explícitas não provam inviabilidade matemática.
- **Figuras:** filtrar dominância em três objetivos antes das projeções;
  f1×f2, f1×f3 e f2×f3 para cada método, com as cinco repetições identificadas.
  Explicar a diferença entre arquivo por repetição e união filtrada.
- **Texto:** referências empíricas TP1, sem chamá-las de ideal/nadir exatos;
  justificar 16 pesos e 16 pares ε; explicar viabilidade prioritária no TP2,
  orçamento, aceitação, arquivo e melhor viável; incorporar correções TP1.
- **Análise:** responder se as repetições alcançaram regiões semelhantes;
  discutir custo versus qualidade e comparar esforço efetivo; não usar apenas
  número de pontos para declarar um método superior.
- **Entrega:** testes e auditores aprovados; tabelas/figuras regeneráveis;
  relatório único compilado e visualmente revisado; pacote com código,
  dependências, referências, configurações, dados, figuras e fontes do relatório;
  matriz E01–E18/F01–F04 com evidências. Grupo confere o arquivo enviado.

## Escopo que pode esperar

O enunciado dispensa apresentação oral no TP2. Streamlit e decisão com dois
métodos entre AHP/ELECTRE/PROMETHEE e ao menos quatro critérios pertencem ao
TP3. NSGA-II, interface gráfica, migração para `src/`, otimizações estruturais
e métricas avançadas não ajudam a fechar o caminho crítico de hoje.

## Ponto de retomada

A **etapa 1 está concluída**: decisões técnicas e explicação dos métodos
estão em [DECISOES_ETAPA_1.md](DECISOES_ETAPA_1.md). A continuidade autorizada
está no fechamento do pacote e do PDF, com campanha auditada conforme
[registro de execução](EXECUCAO_13_EM_ANDAMENTO.md).
O usuário aprovou 10.000 avaliações; as 160 buscas e 1.600.000 avaliações terminaram;
a compilação e revisão visual finais ocorrerão com LaTeX no outro computador,
seguindo o [checklist](CHECKLIST_ENTREGA_TP2.md).
