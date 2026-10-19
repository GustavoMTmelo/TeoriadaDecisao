# Protocolo experimental — TP2

## Estado e escopo

Piloto de 64 buscas concluído e auditado. O usuário aprovou explicitamente
manter 10.000 avaliações e iniciar a campanha oficial em 18/10/2026.
O relatório será compilado com LaTeX em outro computador, conforme esclarecido
pelo usuário; instalar compilador nesta máquina não condiciona os experimentos.

## Entradas e desenho

Referência: `results/referencias_tp1.json`, ID
`4eed030453911d878065db4ddcab092db28e085de25ec7b32dd6f52aa52e02f4`.
Preservar dados, construtiva, N1/N2/N3 e núcleo GVNS. Normalizar os três
objetivos sem truncar valores fora de [0,1]. Priorizar viabilidade conforme
`avaliacao.py`; arquivo Pareto usa os três objetivos brutos.

| Parâmetro | Piloto | Coleta oficial aprovada |
|---|---|---|
| Configuração | `configs/tp2_piloto.json` | `configs/tp2.json` |
| Sementes-base | 90001, 90002 | 42, 123, 456, 789, 1011 |
| Métodos e malhas | 16 pesos + 16 pares ε | Mesmas malhas |
| Runs | 64 | 160 |
| Teto de avaliações por run | 10.000 | 10.000, aprovado pelo usuário |
| Limites restantes | 200 iterações, 60 sem melhoria, k=3, 20 amostras, 5 reinícios VND | Iguais |
| Saída | `results/piloto_tp2_lote/` | `results/tp2/` |

Sementes efetivas são derivadas de base/método/configuração pelo algoritmo
SHA-256 já implementado. As sementes externas foram usadas na integração de
500 avaliações; aqui o desenho percorre as malhas completas com os limites
propostos. Nenhum dado piloto será incorporado aos resultados oficiais.

## Execução e auditoria

Na raiz do projeto, PowerShell:

```powershell
& ./.venv/Scripts/python.exe -X utf8 piloto_tp2.py
& ./.venv/Scripts/python.exe -X utf8 verificar_tp2.py --output results/piloto_tp2_lote
```

O runner informa cada busca nova e mede o tempo total da campanha, incluindo
persistência e consolidação. Ao terminar, executa o verificador independente
e salva `medicao_piloto.json`. Uma retomada preserva a medição original e
registra `medicao_retomada.json`, sem estimar duração a partir de buscas reutilizadas.
Não executar dois processos gravando no mesmo diretório.

## Critérios de decisão antes da coleta oficial

1. Contabilizar 64/64 runs e obter auditoria aprovada; investigar qualquer erro
   de integridade antes de usar os dados para decidir.
2. Examinar fração de finais viáveis por método e configuração, especialmente
   ε apertado, motivos de parada e avaliações efetivamente realizadas.
3. Registrar tempo total, distribuição dos tempos de busca, duração da
   auditoria, cardinalidade das uniões Pareto e espaço ocupado.
4. Extrapolar custo para 160 runs com margem; consolidação pode crescer mais
   que linearmente. Não confundir tempo do solver com tempo total.
5. Manter o teto proposto se viabilidade e tempo forem adequados à entrega;
   discutir alterações antes de congelar. Não escolher sementes por sucesso
   nem apagar falhas. Sem viável encontrada não prova inviabilidade matemática.
6. Registrar decisão final nesta seção com os dados do piloto e congelar
   versões, configuração, referências e hashes dos fontes no manifesto.

**Decisão final:** manter **10.000 avaliações por run** e executar as **160
buscas oficiais**. Resposta explícita do usuário: “Manter 10.000 e iniciar a
campanha oficial”. Preservar as 16 configurações e cinco sementes por método.
Alterações após início da coleta requerem saída nova e versão explícita.

Execução com progresso e medição antes da auditoria:

```powershell
& ./.venv/Scripts/python.exe -X utf8 executar_tp2.py
```

O runner utiliza o mesmo `executar_campanha` e solver validados, salva a
medição da coleta antes de validar, e usa o gerador para auditar e produzir
as seis projeções em uma única passagem. Não executar outro processo na
mesma saída. Fontes científicos, referência, configuração e ambiente ficam
congelados durante a coleta. Texto, testes e empacotamento podem evoluir.

## Resultados do piloto e recomendação

| Medida | Resultado |
|---|---|
| Runs concluídas / avaliações | 64/64; 640.000 avaliações |
| Ponderada | 32 viáveis; nenhuma sem viável encontrada |
| ε-restrito | 18 viáveis; 14 sem viável encontrada |
| Pares ε sem viável nas duas sementes | (0,0), (0,1/3), (0,2/3), (0,1), (1/3,0), (2/3,0), (1,0) |
| Candidatos viáveis observados auditados | 200.496 |
| Arquivos / entradas Pareto auditadas | Seis arquivos; 8.752 entradas somando repetições e uniões |
| União ponderada / ε-restrita | 2.703 / 870 composições |
| Tempo de solver somado | 670,96 s (11,18 min) |
| Campanha, incluindo persistência/consolidação | Aproximadamente 1.028,09 s (17,13 min) |
| Auditoria atual | 446,42 s (7,44 min) |
| Volume descompactado | Aproximadamente 1,87 GB |

**Recomendação apresentada ao usuário:** manter teto de 10.000 avaliações
por run, mesmo esforço máximo para ambos os métodos. As ausências são
consistentes nas duas sementes, mas não provam impossibilidade dos pares.
Não substituir sementes nem retirar essas configurações da coleta.

Extrapolação linear do tempo total: 160 runs em aproximadamente 42,84 min;
com margem de 50%, 64,26 min, **mais auditoria**. A auditoria de 64 runs levou
7,44 min; sua extrapolação linear para 160 seria 18,60 min, sem garantia
de crescimento linear. Reservar aproximadamente 1h30–2h para coleta e
validação, antes de figuras, análise e compilação.

Detalhes gerados em `results/piloto_tp2_lote/medicao_piloto.json` e auditoria
em `auditoria_independente.json`. O tempo de campanha foi reconstituído
aproximadamente entre a criação do processo (22:53:46,277428 UTC) e o mtime
do resumo final (20:10:54,367131, Brasília); inclui inicialização.
O runner carregara o auditor anterior antes da atualização do módulo e foi
interrompido durante essa conferência redundante após a auditoria atual
aprovar os dados. Nenhuma busca foi perdida; a medição registra explicitamente
a origem aproximada do tempo. Não apresentar esse intervalo como cronômetro
de alta precisão. A auditoria atual usou medição por `perf_counter`.

## Ambiente e entrega

Ambiente de coleta local: `.venv`, CPython 3.13.5. Versões efetivas são
registradas pelo manifesto; `pip freeze` salvo em `requirements-tp2-lock.txt`.
Não substituir o lock histórico do TP1. O verificador TP1 foi aprovado no setup;
seu indicador de código atual diferente da coleta é esperado e não invalida
as composições e referências revalidadas.

O piloto prepara TP2-13. Figuras TP2-14 podem ser desenvolvidas com a
integração auditada; números da comparação e figuras oficiais devem vir
exclusivamente da coleta oficial aprovada. O usuário aprovou o orçamento
com as evidências apresentadas. Compilação e revisão visual finais permanecem
obrigatórias na etapa 8, usando o ambiente LaTeX do outro computador.

O usuário informou que a entrega aceita mais de 100 MB ou link do repositório.
Preparar um pacote compactado e separar dados oficiais e piloto; não assumir
limite ilimitado nem publicar arquivos automaticamente. Validar formato e
tamanho do arquivo final antes do envio pelo grupo.

## Gargalo identificado e correção operacional

A primeira tentativa em `results/piloto_tp2/` foi interrompida após duas
buscas novas devido ao custo da consolidação incremental. Os registros
completos foram preservados; esse diretório não é uma campanha concluída.
Uma run produziu 7.423 observações e um JSON de cerca de 67,5 MB. A busca
levou aproximadamente nove segundos, mas as cópias sucessivas do arquivo
Pareto custavam muito mais.

A consolidação em lote mantém filtragem em 3D, deduplicação física, avaliação
da primeira ocorrência e todas as origens distintas. O teste aleatorizado
compara o resultado completo com a inserção incremental. Nos mesmos 200
candidatos reais, ambos produziram resultados iguais: 0,451 s incremental
contra 0,017 s em lote. Os 7.423 observados foram consolidados em 1,118 s
(186 composições ND). São medições pontuais, não garantia de desempenho.

Fontes e hashes mudaram; a nova execução usa `results/piloto_tp2_lote/`,
desde o início, com manifesto próprio. Uma integração nova de oito buscas
reproduziu exatamente os seis arquivos Pareto históricos, incluindo origens.
O auditor indexa proveniência e consolida por varredura sem reter todas as
composições simultaneamente; mantém recálculo e rejeição de adulterações.

## Resultado da campanha oficial

A invocação de `executar_tp2.py` começou em 18/10/2026 às 20:25:25
(Brasília). Concluiu **160 buscas novas, sem reutilização**, com
**1.600.000 avaliações**. A coleta levou 2.760,61 s (46,01 min), incluindo
persistência e consolidação; a soma dos tempos dos solvers foi 1.837,18 s.
A primeira auditoria e geração de figuras levaram 797,26 s (13,29 min),
totalizando 3.557,88 s (59,30 min) nessa invocação.

O auditor aprovou **487.200 candidatos observados, 12 arquivos Pareto e
17.802 entradas exportadas**. Esta última contagem soma arquivos por
repetição e uniões, portanto não representa alternativas globalmente únicas.
As uniões por método têm 3.961 composições ponderadas (3.830 vetores distintos)
e 1.206 ε-restritas (1.182 vetores distintos). Viabilidade encontrada em
80/80 e 45/80 buscas, respectivamente. Falhas preservadas no resumo.

`medicao_oficial.json` registra fase `auditada_com_figuras`. Os hashes das
11 fontes científicas, configuração e referências conferem com o manifesto
congelado. Não houve nova execução das buscas para melhorar resultados.
Não foi realizada segunda campanha integral em outra máquina.

A revisão visual detectou cortes em rótulos/legendas de algumas projeções.
Foi ajustada apenas a exportação: legendas mais curtas e caixa de recorte
que inclui os elementos externos. A regeneração das figuras executa de novo
o auditor, preservando os registros e as composições. Essa revisão posterior
não integra o tempo original da invocação oficial.

Análise e discussão: [RESULTADOS_OFICIAIS.md](RESULTADOS_OFICIAIS.md),
`results/tp2/analise.json`, fragmentos de resultados e discussão incluídos
em `relatorio.tex`. A suíte final aprovou **173 testes em 15,25 s**.
Compilação e revisão visual do PDF continuam pendentes no computador com
LaTeX, conforme [checklist](CHECKLIST_ENTREGA_TP2.md).
