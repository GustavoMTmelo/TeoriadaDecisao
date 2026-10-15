# Registro de execução — plano: docs/tp2/PLANEJAMENTO.md

Escopo autorizado: TP2-01 a TP2-06, testes por tarefa, backlog atualizado e commits enviados ao GitHub. Implementação própria com revisão independente final, conforme habilidade executing-plans.

## Decisões de execução

- Branch `tp2/01-06-base-viavel` no checkout atual; a autorização de ponta a ponta permite criar branch e publicar commits. As cinco exclusões preexistentes de PDFs serão mantidas fora do stage. O planejamento local aprovado acompanha o primeiro commit.
- Os scripts auxiliares da habilidade presumem plano com headings `Task N` e shell POSIX; este backlog usa IDs TP2 e PowerShell. Registro equivalente versionado neste arquivo: teste RED, implementação, teste GREEN e commit por tarefa. Não adicionar outra dependência de shell para controle de progresso.
- Contratos 01→02→03→05→06 conferidos: Avaliacao com objetivos opcionais, ResultadoBusca com ausência explícita, Candidato com cópia da composição; consumidor de registros deve verificar estrutura/qualidade e recalcular objetivos ao ler.
- 03/04/05 compartilham `vns.py`: execução sequencial. 06 fornece referências e matriz cruzada; a função de normalização de 07 continua fora do escopo, apenas construção dos extremos pertence a 06.
- O plano cita imutabilidade de metadados, mas a composição pública permanece dicionário de listas para compatibilidade; usar dataclasses frozen e cópias defensivas ao armazenar/observar. Mudanças de contrato posteriores devem ser documentadas.

## Evidências por tarefa

- TP2-01 concluída: baseline 9 testes passaram; RED confirmou módulo `contratos` ausente; GREEN suíte completa com 18 testes. Ambiente instalado via `requirements.txt`, versões congeladas em `requirements-lock.txt`. Configuração negativa rejeitada, cópia defensiva e ausência explícita de sucesso testadas. Comando: `python -m pytest -q` (Python disponível via caminho absoluto; dependências temporárias via PYTHONPATH).
