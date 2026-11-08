# Conferência da entrega TP2 — 18/10/2026

Este checklist complementa o diagnóstico histórico da matriz de requisitos.
O prazo informado pelo grupo é 18/10, às 23:59 (Brasília).

**Atualização após solicitação de instalação local:** MiKTeX instalado e
atualizado neste computador; compilação cumulativa com 30 páginas e inspeção
técnica da renderização concluídas. O PDF está em `build/latex/relatorio.pdf`.
Ver [setup local](SETUP_LATEX_LOCAL.md). As instruções abaixo também podem
ser executadas aqui; não é mais necessário outro computador.

## Evidências técnicas

| Requisitos | Evidência | Conferência necessária para fechamento |
|---|---|---|
| E01, E06, E07 | `relatorio.tex`, `results/tp1_corrigido/` | Conferir seções e seis figuras TP1 no PDF cumulativo |
| E02, E16 | `README.md`, `requirements-tp2-lock.txt`, configurações, pacote com manifesto | Conferir extração e instruções no computador do grupo |
| E03–E05, F01, F03, F04 | Avaliador, GVNS, vizinhanças, testes, `METODOLOGIA_TP2.tex` | Conferir correspondência entre descrição e implementação |
| E08–E11 | Escalarizações, referências TP1, `configs/tp2.json`, metodologia | Referências empíricas fixas, 16 pesos e 16 pares ε |
| E12, E13, F02 | `results/tp2/manifesto.json`, registros, arquivos Pareto, medição oficial | Exigir auditoria aprovada, 160 buscas e falhas explícitas |
| E14, E15 | Seis projeções em `results/tp2/figuras/` e discussão | Inspeção visual das seis figuras e das cinco identidades por repetição |
| E17, E18 | Metodologia, resultados gerados, discussão e `analise.json` | Conferir números, compromissos, variabilidade e limites das conclusões |

## Fechamento no computador com LaTeX

1. Extrair o pacote preservando a estrutura de pastas.
2. Executar `./scripts/compilar_relatorio.ps1` na raiz do projeto.
3. Abrir `build/latex/relatorio.pdf` e revisar **todas as páginas**: capa,
   seções cumulativas, tabelas, seis figuras TP1, seis projeções TP2,
   unidades, acentos, legendas, referências e eventuais cortes ou transbordamentos.
4. Corrigir fontes caso necessário e recompilar. A verificação textual local
   não substitui compilação nem revisão visual.
5. Após aprovar o PDF, executar
   `./scripts/compilar_relatorio.ps1 -PublicarPdf` para atualizar o PDF da raiz.
6. Conferir o PDF efetivamente anexado e enviar com código/resultados ou pelo
   mecanismo aceito pela plataforma. O usuário informou aceitar arquivos acima
   de 100 MB ou link do repositório; não foi realizado envio nem publicação.

O `relatorio.pdf` antigo da raiz pertence ao TP1. O empacotador o exclui;
o ZIP de fontes e resultados não equivale ao PDF final revisado.

## Estado da validação

- Suíte local: **173 testes aprovados**.
- Coleta oficial: **160 buscas, 1.600.000 avaliações**, teto comum de 10.000.
- Auditoria integral: **aprovada**, fase `auditada_com_figuras` em
  `results/tp2/medicao_oficial.json`; 487.200 observações, 12 arquivos Pareto,
  17.802 entradas somando arquivos por repetição e uniões (não são 17.802
  alternativas globalmente distintas).
- Análise: `results/tp2/analise.json` e fragmento LaTeX integrados; seis
  projeções finais inspecionadas após correção da exportação e nova auditoria.
- Pacote de fontes/resultados: `dist/tp2_fontes_resultados.zip`, montado por
  `empacotar_tp2.py` com manifesto interno, verificação CRC e hash SHA-256
  externo em `dist/tp2_fontes_resultados.manifesto.json`.
  Montagem validada com 303 arquivos de fontes/resultados, além dos dois
  arquivos de orientação/manifesto internos. Conferir o manifesto externo
  da versão transferida.
- Compilação LaTeX e conferência técnica das 30 páginas: **concluídas localmente**.
- Aprovação do conteúdo pelo grupo, publicação do PDF na raiz e envio:
  **pendentes**. O ZIP anterior não inclui o setup local nem o novo PDF.
