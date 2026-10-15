# Auditoria para a Entrega 2 — 15/10/2026

## Escopo e conclusão

Auditoria do estado existente, sem alterar os algoritmos. O TP1 fornece dados, objetivos, construtiva, vizinhanças, GVNS e material de relatório reaproveitáveis. A Entrega 2 ainda não está implementada. Antes de produzir suas referências numéricas, é necessário corrigir o retorno viável e a validação por execução. O feedback da professora confirma a adequação da N3 atual; a recomendação antiga de substituí-la fica superada.

Prazo atualizado pelo usuário: **18/10/2026**, sem horário informado. A data 16/10 da Aula 6 não deve orientar o cronograma atual.

## Fontes e precedência

As páginas abaixo são posições físicas no PDF, incluindo capa. A numeração impressa do relatório é uma página menor; a Aula 6 contém sobreposições e sua numeração impressa também difere.

| ID | Fonte | Uso |
|---|---|---|
| E | `Case-UFMG-Teoria_da_Decisão.pdf`, 8 páginas, na raiz deste repositório | Enunciado integral: descrição pp. 1–2; cumulatividade p. 2; TP1 pp. 2–4; TP2 pp. 4–5; TP3 pp. 5–6; dados pp. 6–8 |
| A5 | `../../../aulas/05-Aula.pdf`, pp. 8–9 | Motivação e fórmula da normalização; material didático, não requisitos adicionais de entrega |
| A6 | `../../../aulas/06-Aula.pdf`, pp. 28–36 | ε-restrito, dois limites, malha cartesiana, melhor viável e protocolo de cinco varreduras |
| F | Feedback da professora transcrito pelo usuário neste chat, 15/10/2026 | Quatro correções e reconhecimento positivo da N3 |
| R | `relatorio.tex` e `relatorio.pdf`, 21 páginas | Formulação, método e resultados declarados do TP1 |
| S | `apresentacao.tex` e `apresentacao.pdf`, 9 páginas | Narrativa usada no TP1 |
| H | Chat “Validar TP1 e estruturar README”, consultado pelo identificador fornecido | Histórico; não substitui código ou evidência experimental |

As três cópias locais do enunciado têm SHA-256 `64e8a40a210f23c66b6e2cd9de33c277cbb674190b62239836ca755be5bf6e39`. O relatório do repositório é idêntico ao PDF em `../../entregavel/relatório_TD1 (4).pdf`: SHA-256 `e03dd1ecf7dc261b1bffcf4c42aaf7cfa5631d40d9e37f004252a245d830fdee`. O enunciado foi extraído integralmente; as páginas 4 e 5 também foram conferidas visualmente.

O guia `Resumo_Trabalho_Teoria_da_Decisao.pdf` e `../../VALIDACAO_TP1.md` são históricos. O parecer antigo refere-se ao commit a344d55 e não descreve o estado atual. A apresentação industrial foi consultada como contexto; o enunciado detalhado e o feedback atual regem a entrega.

## Git e GitHub

- Diretório Git real: `C:/Users/henry/Desktop/UFMG/TD/tp1/TeoriadaDecisao/TeoriadaDecisao`. A pasta `TD` não é um repositório.
- Branch local `main`, HEAD e referência local `origin/main`: `bac0f06f79f8b68fa468426ce812e5da75c71eaa`.
- GitHub consultado por conector: branch `main`; commit mais recente retornado também `bac0f06`; trecho crítico de `vns.py` remoto confere com o local. Nenhuma issue ou PR aberto retornado pelas consultas. Não foi necessário fazer pull/reset.
- Alterações locais anteriores à auditoria: exclusões não staged de `01-Aula.pdf`, `02-Aula.pdf`, `04-Aula.pdf`, `05-Aula.pdf`, `06-Aula.pdf`. Preservadas; suas cópias em `TD/aulas` continuam disponíveis. Não incluir essas exclusões no commit do plano sem decisão do responsável.
- Commits recentes: `bac0f06` remove documentos auxiliares; `85a576a` reverte prompt; `3a1fab8` adiciona relatório/apresentação finais; `7955baf` finaliza validação/documentação; `4493a75` finalização do trabalho.
- Este planejamento cria documentos locais para revisão. Os identificadores TP2-01 etc. são identificadores do backlog, **não números de issues publicadas**. Nenhum push, commit ou publicação de issue realizado nesta rodada.

## Diagnóstico do código e dos artefatos

| Componente | Diagnóstico | Destino |
|---|---|---|
| Dados em `sol_inicial.py` | 20 minérios, 10 pilhas, 2 kt/caminhão; dados conferem com E pp. 7–8; FeT não ativo | Reutilizar |
| `calcular_f1/f2/f3`, teores | Custo em R$ e desvios quadráticos em pontos percentuais ao quadrado; cálculo usa média dos caminhões de mesma massa | Reutilizar; expor vetor dos três objetivos |
| `gerar_solucao_inicial` | Determinística, 145 caminhões, 290 kt; válida estruturalmente, 12 violações químicas | Reutilizar como ponto inicial, sem tratá-la como alternativa final |
| `validar_estrutura` | Não confere conjunto completo de chaves; remover a pilha 2 da construtiva ainda retorna `(True, [])` | Corrigir antes de importar/exportar soluções |
| `validar_qualidade` | Tolerância 1e-9; trabalha nas pilhas recebidas, não substitui validação estrutural | Reutilizar com validação estrutural prévia |
| `vizinhancas.py` | N1 substitui 1 posição; N2 troca entre pilhas; N3 altera ambas as posições e rejeita composição idêntica | Preservar sem redesenhar N3 |
| N2/N3 rápidas em `vns.py` | Usadas efetivamente pelo GVNS; testes existentes cobrem versões enumeradas, não as rápidas | Acrescentar testes dos operadores reais |
| Penalidade | Soma quadrática de violações químicas; λ diferentes por objetivo | Não é normalização nem certificado de viabilidade |
| `gvns` | Guarda apenas melhor fitness; não mantém incumbente viável nem valida retorno | Corrigir e instrumentar observação de candidatos |
| `executar_experimento` | Seleciona menor objetivo bruto; só valida química dessa solução; estatísticas incluem qualquer retorno | Validar e registrar cada execução; separar falhas |
| `vnd` | Cinco reinícios; depois disso permanece na vizinhança se melhora; só avança se não melhora | Preservar fluxo e corrigir descrição/comentário; testar sequência |
| Histórico | Objetivo bruto da incumbente penalizada; não necessariamente melhor valor viável, nem curva monotônica do objetivo bruto | Registrar curvas com semântica explícita e ausência de viável |
| `resultados_vns.txt` | 15 valores finais e tempos, somente 3 mensagens de qualidade; sem composições completas nem vetores cruzados | Histórico insuficiente para referências auditáveis; regenerar |
| Relatório §§6.1, 6.4, 7 e conclusão | Afirma retorno obrigatório viável e viabilidade das 15 rodadas sem garantia correspondente no código; fluxo VND divergente | Corrigir no relatório cumulativo |
| Apresentação pp. 5–9 | Repete garantia de validação/viabilidade e simplifica reinícios VND | Preservar como histórico; revisão opcional se reutilizada no TP3 |
| README deste repositório | Instruções e dependências presentes; afirmação de todas as soluções viáveis não sustentada pelo log individual | Atualizar junto com correções |
| README em `TD` e parecer antigo | Ainda dizem que GVNS falta e N3 precisa ser trocada | Marcar como históricos e apontar para auditoria atual |
| Multiobjetivo | Não encontrados módulos de normalização, escalares, arquivo não dominado ou varredura | Criar |

Nuances adicionais para o texto: N1 sorteia uniformemente entre movimentos enumerados, não por três sorteios uniformes independentes. `time.time()` mede tempo decorrido, não tempo de CPU. O máximo de cinco reinícios não limita sozinho o número de melhorias na mesma vizinhança. Os desvios f2/f3 são em p.p.² antes da normalização; a tabela atual chama-os de adimensionais.

## Feedback convertido em correções verificáveis

| Feedback | Evidência | Correção e teste planejado |
|---|---|---|
| F1 — pesos não normalizam nem garantem viabilidade | `calcular_fitness = f + lambda*pen`; nenhuma condição de retorno com qualidade válida | Normalização separada (TP2-07), validação explícita e retorno sem viável identificado (TP2-02/03) |
| F2 — verificar cada execução | `validar_qualidade(melhores[idx_melhor])` ocorre depois do laço | Registro com estrutura, qualidade, violações e três objetivos para cada rodada, inclusive falhas (TP2-05) |
| F3 — guardar melhor viável | `melhor` atualizado apenas por fitness | Observador de cada candidato avaliado; cópia da melhor viável independente de aceitação; testar viável visitada e depois perdida pela trajetória (TP2-03) |
| F4 — coerência VND | `l += 1` apenas no `else` de `melhorou` | Manter comportamento atual; teste com melhoria em N2 após quinto reinício exige nova chamada a N2 (TP2-04) |

Não concluir que as 15 soluções históricas são inviáveis: o defeito é a ausência de garantia e de registros individuais suficientes. Também não concluir que são todas viáveis com base em três verificações.

## Verificação executada nesta auditoria

1. Seis testes sem fixtures de `test_vizinhancas.py` executados diretamente: todos passaram (N1, N2, N3, estrutura dos movimentos, movimentos impossíveis e reprodutibilidade).
2. Três verificações independentes reproduziram os casos da tolerância química: limite exato e excesso 5e-10 aceitos; excesso 2e-9 rejeitado, com tolerância 1e-9. Não foram executadas pelo runner pytest.
3. Construtiva reproduzida: `f1=60400000`, `f2=23.48105481043885`, `f3=14.909887547238732`, 145 caminhões, estrutura válida e 12 violações de qualidade.
4. Caso de pilha ausente reproduzido: exclusão da chave 2 retorna estrutura válida indevidamente.
5. A suíte via `python -m pytest -q` não pôde rodar: pytest ausente no Python disponível. Importar GVNS também falhou por matplotlib ausente. A tentativa de instalar pytest em pasta temporária falhou por resolução de rede. Não houve reexecução das 15 buscas nem certificação dos resultados históricos.

Os diagnósticos de GVNS acima são sustentados pela leitura do código local e remoto, não por execução integral. A próxima etapa deve preparar um ambiente com `requirements.txt`, rodar a suíte e gerar resultados novos com trilha de auditoria.

## Limites do escopo

A entrega exige soma ponderada **e** ε-restrito, não uma escolha entre ambos. Não exige NSGA-II, população evolutiva, hipervolume, prova de otimalidade, Streamlit ou apresentação oral nesta etapa. Os últimos itens de interface e decisão multicritério pertencem ao TP3. Nenhuma exigência nova foi inferida do pedido de cobertura ampla: a [matriz](MATRIZ_REQUISITOS.md) distingue obrigação, decisão técnica e melhoria opcional.
