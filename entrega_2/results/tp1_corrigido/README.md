# Campanha TP1 corrigida — TP2-06

15 execuções completas e 15 soluções finais viáveis, com as sementes oficiais
42, 123, 456, 789 e 1011 por objetivo. O manifesto registra código, dados,
dependências, configurações, agenda e hashes.

- `execucoes/`: um JSON v1 por rodada, com melhor viável, incumbente da trajetória, validações, três objetivos, histórico, contadores, motivo de parada e tempo decorrido.
- `resumo.csv`: uma linha por execução, incluindo status e esforço.
- `objetivos_cruzados.csv`: 15 composições × três objetivos em precisão completa.
- `matriz_payoff.csv`: três objetivos avaliados na melhor composição de cada problema.
- `estatisticas_f*.json`: estatísticas e dados usados nas seis figuras.
- `referencias_tp1.json`: extremos empíricos das 15 finais, origem e hash das fontes; cópia canônica em `../referencias_tp1.json`.
- `auditoria.json`: resumo dos valores e da matriz cruzada.
- `resultados_tp1.tex`: fragmento gerado e incluído no relatório cumulativo.

Unidades: custo em R$; f2/f3 em pontos percentuais ao quadrado. Referências
empíricas não constituem extremos globais. A melhor viável pode ser um
candidato observado e não aceito pela trajetória penalizada; por isso seus
valores podem melhorar em relação ao log histórico preservado na raiz.

Na raiz do repositório:

```bash
python reproduzir_tp1.py --output results/tp1_corrigido --verificar
python reproduzir_tp1.py --output results/tp1_corrigido --regerar
python reproduzir_tp1.py --output results/nova_campanha_tp1
```

O primeiro comando é somente leitura e verifica composições, referências,
estatísticas e integridade de todos os produtos. O segundo regenera os
produtos a partir dos registros existentes. O terceiro reexecuta as 15 buscas;
exige diretório de saída vazio. Depois de regenerar o fragmento, compilar
`relatorio.tex` duas vezes para atualizar o PDF e suas referências.

As fontes de coleta e de consolidação têm hashes separados: o código de
busca foi congelado durante a campanha; o verificador e a geração do texto
foram aprimorados durante a revisão. `.gitattributes` preserva os bytes
dos resultados para que os hashes sejam verificáveis em outros sistemas.
