# Integração reduzida TP2-12B

Campanha de verificação, **não oficial TP2-13**, com dados físicos reais,
referências TP1 congeladas e configuração `configs/tp2_integracao.json`.

- Dois métodos, duas configurações por método, sementes-base 90001 e 90002.
- Oito buscas; teto 500 avaliações por busca; 4.000 avaliações efetivas.
- Ponderada: três finais viáveis e uma sem viável encontrada.
- Epsilon: duas finais viáveis e duas sem viável encontrada (tetos 0,0).
- 260 candidatos viáveis observados, registrados com composição e auditoria.
- Arquivos não dominados por método: 49 composições ponderadas e 37 epsilon.
- Por repetição: ponderada 13/38 e epsilon 21/21 composições não dominadas.
- Retomada reutilizou 8/8 registros sem executar novas buscas.

Cada ponto pertence ao arquivo não dominado entre os candidatos observados;
isso não certifica ótimo global nem fronteira completa. Ausência de viável no
orçamento é falha de busca, inclusive na soma ponderada, sem prova de
inviabilidade matemática.

Para verificar sem modificar arquivos nem executar buscas, na raiz Git:

```bash
python verificar_tp2.py --output results/integracao_tp2_final
```

O verificador recalcula os três objetivos e restrições a partir das
composições, confere cada origem, reconstrói os arquivos Pareto e confronta
manifesto e resumos. A auditoria final está em `auditoria.json`.

Para reproduzir, escolha uma saída nova:

```bash
python experimentos.py --config configs/tp2_integracao.json --output results/minha_integracao
```

Os JSON preservam precisão completa; o manifesto registra hashes dos fontes,
dados e referência, parâmetros, versões e agenda. O commit Git é informativo;
a retomada depende dos hashes efetivos, inclusive quando commits posteriores
alteram apenas documentação, testes ou o verificador independente.
