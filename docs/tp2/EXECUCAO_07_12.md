# Execução TP2-07 a TP2-12B — 18/10/2026

Meta persistente sem orçamento; escopo autorizado em texto anexado pelo usuário.
TP2-13 (campanha oficial) permanece posterior. Plano e matriz existentes regem
esta execução. Aprovações intermediárias dispensadas explicitamente pelo usuário.

## Estado inicial e decisões

- Base `31c5807`, PR #4 aberto, head remoto idêntico após fetch; main `bac0f06`.
- Cinco PDFs excluídos no checkout original permanecem intocados; novo worktree
  `TD/tp2-multiobjetivo`, branch `tp2/07-12-multiobjetivo`, derivada da base.
- Ausência de AGENTS.md na árvore TD. Baseline: **69 testes passaram em 18,83 s**,
  Python 3.14.4; nenhum módulo TP2-07+ previamente implementado.
- Fontes: enunciado oficial pp. 4–5, A5 pp. 8–9, A6 pp. 28–36; plano,
  backlog, matriz e execução 01–06. Não alterar dados ou referências TP1.
- Usar prioridade de viabilidade, escalar e desempate lexicográfico conforme
  plano; modo mono conserva fitness histórico. Operadores existentes preservados.
- Execução em frentes autorizadas: 07→09→10 (modelagem), 12A (Pareto),
  11 (persistência/agenda); núcleo 08 e integração 12B pelo coordenador.
- Interfaces verificadas: 07 normaliza para 09/10 e avaliação; 09/10 fornecem
  configurações para 08/11; 08 observa Candidato antes da aceitação para 11/12A;
  11 persiste referências/configuração e todas as alternativas necessárias
  para reconstrução do Pareto. Contratos existentes suficientes.

## Sequência e verificação

- [x] 07: normalização — testes sintéticos, degeneração, hash e referência real.
- [x] 09: ponderada — pesos inválidos, malha 16, valores manuais.
- [x] 10: epsilon — produto 4×4, tetos independentes, qualidade e tolerância.
- [x] 08: GVNS — orçamento interno, observação, melhor viável, mono e VND.
- [x] 12A: Pareto — 3D, deduplicação física, cópia e proveniência.
- [x] 11: campanha — 160 IDs, seeds estáveis, manifesto, falhas e retomada.
- [x] 12B: integração — ambos métodos, persistência/revalidação, Pareto,
  repetibilidade e retomada; campanha reduzida, suíte completa.
- [x] Auditoria dos critérios e documentação/backlog; publicação registrada abaixo.

Cada implementação começa com teste falhando e termina com evidência e commit.
O histórico Git e este registro permitem retomar após interrupção.

## Evidências intermediárias

- 07: `b55f371`, 11 falhas antes do código e 80 testes aprovados depois;
  regressão de referência ausente em `dc48ace`.
- 09: `c4bb7f7`, 9 testes novos de pesos, malha e avaliação.
- 10: `ae5f0f3`, 8 testes de epsilon mais auditoria e limite químico exato.
  Corrigida diferença de arredondamento que produzia V residual positivo
  para qualidade numericamente viável; mesma ordem das operações no validador.
- 12A: `fa944d4`, 19 testes focais; dominância 3D e proveniência independentes.
- 08: nove falhas pela ausência do módulo, adaptador VNS inicialmente ausente;
  depois 12 testes focais aprovados, inclusive mono e ambos métodos TP2.
  Uma revisão independente não encontrou falha importante no núcleo.
- Execução real exploratória de 1.000 avaliações (seed 90001, pesos iguais):
  viável, vetor `(64020000, 2.8847442348231698, 2.7388207881301305)`.
  Apenas verificação de funcionamento, sem uso como resultado oficial.
- Suíte conjunta após integração inicial: **149 passaram em 35,32 s**.
- Revisão detectou e encaminhou correções de retomada (contadores inválidos,
  viável final ausente dos observados, origens incompletas) e exportação ND
  da união por método, além dos arquivos por repetição.

## Auditoria dos critérios de aceitação

| Tarefa | Critérios conferidos | Evidências |
|---|---|---|
| 07 | Mínimo→0, máximo→1, externos preservados; rejeição não finitos/degeneração relativa; hash e origens preservados | `tests/test_normalizacao.py`; referência real ID `4eed0304…` |
| 09 | 16 pesos únicos, três vértices e centro; soma 1/não negatividade/finitude; valor manual 0,35 e desempate | `tests/test_ponderada.py`; malha exportada na agenda |
| 10 | 16 pares independentes incluindo (1/3,1); custo principal; ambos tetos e todas as faixas físicas; tolerância e excesso bruto auditáveis | `tests/test_epsilon.py`, casos U/V/W e referência sintética |
| 08 | Viabilidade prioritária; menor V/escalar/desempate; SHAKE estrutural; orçamento 0/1/2/7 nos laços; callback antes da aceitação; último candidato guardado; mono e sequência VND preservados | 12 testes de `test_busca.py`; reprodução real dos dois métodos em `test_integracao_tp2.py` |
| 11 | 160 IDs e seeds SHA-256; cinco varreduras ×16 por método; manifesto, registros, falhas e temporários; hash incompatível rejeitado; round-trip e retomada | `test_experimentos.py`, `test_registros.py`; agenda completa executada com orçamento zero e reutilização 160/160 |
| 12A | ND nos três objetivos; dominador remove dominados; duplicata física agrega origens; vetores iguais de composições distintas preservados; ordem e cópia | 19 testes em `test_pareto.py`; revisões independentes |
| 12B | Recomputação física/ε de cada origem; falhas no resumo e fora do arquivo; ausência não apaga outros resultados; retorno foi observado; reprodução e arquivos recarregáveis | quatro testes de integração, nove de auditoria; campanha real e verificador somente leitura |

## Correções da revisão e decisões finais

- `241bd64`: validar todas as origens, inclusive as anteriores à última, na
  retomada. Regressão de origem adulterada reproduzida antes da correção.
- `08bd29d`: impedir status de ausência quando existem observados viáveis.
  A causa era validação unilateral da presença da melhor, sem conferir a
  equivalência entre observados, status e melhor viável. Regressão RED→GREEN.
- `003d9c4`: verificador independente somente leitura. Recalcula objetivos
  diretamente das composições, verifica cada origem com sua configuração,
  recompõe ND 3D e confronta JSON/CSV, agenda, estados e orçamento.
- `67ccdab`: fontes Python e configurações fixadas em LF via `.gitattributes`.
  O Git local usa autocrlf; sem essa regra os hashes brutos mudariam em outro
  checkout. Fontes normalizados antes da coleta final; resultados conservam
  bytes originais pela regra histórica `/results/** -text`.
- O núcleo novo atende ambos os métodos e o modo mono por `busca.resolver`;
  `vns.resolver` é o adaptador. `vns.gvns` histórico permanece para reprodução
  estrita da coleta TP1 e seus testes de instrumentação. Não reescrever a
  trajetória antiga evita invalidar a interpretação das referências empíricas.
- O commit do manifesto é informativo; hashes efetivos dos módulos, dados,
  configuração e referência regem a retomada. Commits de documentação/testes
  ou verificador não invalidam buscas já congeladas.
- Os diretórios intermediários criados nesta execução foram preservados
  localmente e excluídos localmente do Git; somente `integracao_tp2_final`
  compõe a entrega. A revisão automática bloqueou a remoção dos temporários
  por política; nenhuma exclusão foi executada.

## Evidência experimental reduzida

Configuração `configs/tp2_integracao.json`: duas seeds-base externas à campanha
oficial (90001/90002), custo puro e centro na ponderada, epsilon (1,1) e (0,0),
teto de 500 avaliações por subproblema, oito buscas reais, 4.000 avaliações.

- Cinco finais viáveis (três ponderadas, duas epsilon); três sem viável
  encontrada (uma ponderada, duas epsilon). Não são provas de inviabilidade.
- 260 candidatos viáveis observados; arquivos ND por repetição: ponderada
  13/38, epsilon 21/21; união de método 49/37 composições distintas.
- Seis arquivos de Pareto, 179 entradas exportadas somando ambos os níveis.
- Retomada integral reutilizou 8/8, com solver configurado para lançar erro se chamado.
- A campanha oficial de 160 buscas com teto 10.000 **não foi executada**;
  `configs/tp2.json` e `configs/tp2_agenda.json` deixam sua infraestrutura
  pronta. O piloto e a escolha final do teto pertencem a TP2-13.
- Base TP1 revalidada: 15/15 finais viáveis, 14 produtos consolidados e seis
  figuras. O verificador informa `codigo_atual_confere=false`, esperado porque
  os módulos evoluíram desde a coleta TP1; referências e resultados não mudaram.

## Verificação final e publicação

- `8223522`: quatro testes de integração, configuração reduzida e agenda
  completa com 160 identidades/seeds; `003d9c4`: nove testes do verificador.
- Suíte completa após todas as correções: **162 passaram em 34,92 s**
  (Python 3.14.4, dependências registradas no manifesto).
- Campanha final em `results/integracao_tp2_final/`: auditor independente
  confirmou 8 execuções, 260 observados, seis arquivos, 179 pontos exportados.
- Retomada executada com solver que lança erro se chamado: **8/8 reutilizadas**.
- Os 11 hashes dos módulos, hash da configuração e hash da referência
  conferidos com bytes atuais antes de salvar `auditoria.json`.
- Checklist de aceitação das sete tarefas auditado acima. Falhas reais de
  revisão têm regressões e commits separados. TP2-13 permanece posterior.
- Checkout limpo destacado em `460064b`: **162 testes passaram em 31,61 s**;
  auditor confirmou os 8 registros, 260 observados, seis arquivos e 179 pontos.
  Os hashes brutos de todos os fontes/configuração/referência conferem também
  nesse checkout. Cópia temporária da campanha retomou 8/8 com solver proibido,
  sem alterar os artefatos versionados.
- Gate final da revisão independente aprovado: correções de status e origens
  confirmadas, 22 testes focais passaram, auditoria e retomada reais conferidas.
- Checkout original permanece na branch anterior com exatamente as cinco
  exclusões locais de PDFs, sem inclusão destas no histórico novo.
- A branch nova deriva de #4 ainda aberto; o PR será encadeado à branch base
  `tp2/01-06-base-viavel`, evitando misturar o diff anterior com as sete tarefas.
