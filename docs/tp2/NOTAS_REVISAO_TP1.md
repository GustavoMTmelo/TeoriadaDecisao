# Correções do método TP1 para o relatório cumulativo

- N3 preservada: duas posições mudam, e a composição física deve mudar. Permutação interna é rejeitada nas versões enumerada e rápida.
- VND: melhoria retorna a N1 enquanto houver menos de cinco reinícios. Depois do quinto, melhoria mantém a vizinhança atual; só a ausência de melhoria avança. Cinco reinícios não são limite de avaliações.
- N2/N3 efetivamente usadas pelo GVNS são as variantes rápidas de `vns.py`; agora cobertas por testes de tentativas, não mutação, compatibilidade, disponibilidade global de N2 e composição distinta de N3.
- Incumbente da trajetória usa fitness penalizado histórico. A melhor solução fisicamente viável é observada e guardada separadamente pelo objetivo bruto, inclusive se não for aceita pela trajetória. É retornada somente quando encontrada.
- Cada execução deve registrar status, composição, objetivos cruzados, validações, violações, contadores, motivo de parada e tempo decorrido. A avaliação inicial é parte da contagem; repetidas também contam. Curva de melhor viável é ausente antes de encontrar viabilidade e depois não aumenta.
- λ não normaliza objetivos e não garante encontrar viável. Na base TP1 os λ históricos são preservados; normalização TP2 é etapa posterior.
- Referências empíricas serão construídas das 15 soluções finais viáveis completas, nunca dos valores arredondados de gráficos. Os desvios f2/f3 antes de normalizar são expressos em p.p.².

Estas notas orientam TP2-15; a geração dos resultados novos e a atualização de suas tabelas/figuras pertencem também a TP2-06.
