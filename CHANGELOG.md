# Changelog — TP1 Case Cassotis

## Referência

- Versão-base da Luiza: commit `4493a75` (`finalização do trabalho`).
- Commit de correções: `7955baf` (`fix: finalize TP1 validation and documentation`).
- Data da preparação final: 27 de setembro de 2026.

## Alterações realizadas após o commit da Luiza

### 1. Validação numérica

- Adicionada tolerância padrão de `1e-9` à função `validar_qualidade()`.
- Valores afetados apenas por imprecisão de ponto flutuante, como `2,3000000000000003`, passaram a ser aceitos corretamente nos limites de qualidade.
- A assinatura final ficou `validar_qualidade(solucao, tolerancia=1e-9)`, mantendo compatibilidade com as chamadas existentes.
- Nenhuma função objetivo, estrutura de vizinhança, semente, parâmetro ou regra do GVNS foi alterada.

### 2. Testes e reprodução dos resultados

- Mantidos os seis testes existentes.
- Adicionados três testes para a validação de qualidade:
  - valor exatamente no limite;
  - valor dentro da tolerância;
  - valor realmente fora da tolerância.
- Resultado final: 9 testes aprovados.
- Reexecutadas as 15 combinações de objetivo e semente: cinco execuções para cada um de `f1`, `f2` e `f3`.
- Os valores de referência foram reproduzidos, incluindo `f1 = R$ 60.440.000` para a seed 123.
- As 15 soluções finais foram verificadas quanto à estrutura e à qualidade.
- Os resultados e gráficos originais foram preservados após a confirmação da reprodução.

### 3. Relatório

- Consolidado o relatório completo em `relatorio.tex`.
- Removido o antigo arquivo LaTeX sem extensão (`latex_relatorio`).
- Corrigido o coeficiente de variação de `f2` para aproximadamente `0,0229%`.
- Explicitado que o desvio-padrão apresentado é amostral, calculado com denominador `n-1`.
- Reorganizada a equação da penalidade para respeitar as margens da página.
- Ajustada a tabela de parâmetros para evitar estouro horizontal.
- Ampliadas as explicações sobre:
  - formulação matemática;
  - representação computacional;
  - solução construtiva inicial;
  - GVNS e VND;
  - vizinhanças N1, N2 e N3;
  - justificativa da vizinhança N3;
  - perturbação SHAKE;
  - tratamento de inviabilidades;
  - critério de aceitação;
  - critérios de parada;
  - planejamento dos experimentos;
  - análise dos resultados.
- Mantido o pseudocódigo completo, integrando solução inicial, perturbação, vizinhanças, busca local, penalização, aceitação e parada.
- Inserida a capa institucional da UFMG com logo, integrantes, matrículas, disciplina, local e data.
- Inserido sumário.
- O PDF final foi compilado e revisado visualmente em suas 21 páginas.

### 4. Documentação e organização do projeto

- Atualizado o `README.md` com:
  - estrutura do repositório;
  - instalação das dependências;
  - comando oficial para os 15 experimentos;
  - forma de salvar o log com redirecionamento ou `Tee`;
  - execução dos testes;
  - compilação do relatório;
  - parâmetros e resultados de referência.
- Criado `requirements.txt` com `matplotlib` e `pytest`.
- Criado `.gitignore` para `.claude/`, caches Python, cache do pytest e arquivos auxiliares do LaTeX.
- Removidos do versionamento os caches Python existentes.

### 5. Apresentação

- Criada apresentação em LaTeX Beamer com base no template Madrid fornecido.
- Aplicado formato 16:9, identidade visual em vermelho UFMG e logo institucional.
- Preparados nove slides, planejados para uma apresentação de até 10 minutos:
  1. capa;
  2. agenda;
  3. problema e objetivos;
  4. representação e solução inicial;
  5. pseudocódigo completo do GVNS;
  6. vizinhanças, SHAKE e VND;
  7. inviabilidades, aceitação e parada;
  8. planejamento experimental e resultados;
  9. convergência e conclusão.
- O PDF da apresentação foi compilado e todas as páginas foram revisadas visualmente.
- Também foi preparada uma versão em PowerPoint como alternativa.
- Criado um pacote próprio para edição da apresentação no Overleaf, incluindo o fonte, logo e gráficos necessários.

## Verificações finais

- 9 testes automatizados aprovados.
- 15 execuções oficiais reproduzidas.
- Custos reproduzidos exatamente.
- Resultados de `f2` e `f3` confirmados dentro da tolerância de `5e-7`.
- Todas as soluções finais confirmadas como estruturalmente viáveis e dentro dos limites de qualidade.
- Relatório compilado duas vezes para atualização de referências e sumário.
- Relatório de 21 páginas revisado visualmente.
- Apresentação Beamer de 9 páginas revisada visualmente.
- Conteúdo dos arquivos ZIP conferido após a criação.

## Arquivos entregues

### Pacote principal — `TP1_Cassotis.zip`

Contém exatamente:

- `sol_inicial.py` — dados, representação, heurística construtiva, objetivos e validações;
- `vizinhancas.py` — vizinhanças N1, N2 e N3;
- `vns.py` — GVNS, SHAKE, VND, experimentos, tabelas e figuras;
- `relatorio.pdf` — relatório final de 21 páginas;
- `apresentacao.pdf` — apresentação Beamer final de 9 slides.

### Materiais adicionais

- `relatório_TD1 (4).pdf` — cópia individual do relatório final.
- `Apresentacao_TP1_Beamer.pdf` — cópia individual da apresentação final.
- `apresentacao.tex` — fonte LaTeX da apresentação.
- `Apresentacao_TP1_Overleaf.zip` — projeto pronto para importação no Overleaf, contendo `apresentacao.tex`, `image.png` e os três gráficos de convergência.
- `Apresentacao_TP1_Cassotis.pptx` — versão alternativa em PowerPoint.
- `TP1_Cassotisv0.zip` e `TP1_Cassotisv0.1.zip` — versões intermediárias preservadas para histórico.

## Situação do GitHub

- O commit `7955baf` foi criado localmente sobre o commit da Luiza.
- Uma tentativa anterior de envio ao repositório `GustavoMTmelo/TeoriadaDecisao` não foi concluída porque a conta autenticada `henrydsra` não tinha permissão de escrita e o GitHub respondeu com erro 403.
- A capa definitiva, a apresentação e este changelog foram preparados depois do commit `7955baf` e reunidos no commit final de publicação.
- Os arquivos entregues no Moodle foram gerados a partir da versão local final, incluindo essas alterações posteriores.
