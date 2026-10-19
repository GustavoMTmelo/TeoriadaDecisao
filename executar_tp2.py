"""Coleta TP2 com progresso, medição persistida e auditoria/figuras em uma passagem."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from busca import resolver
from experimentos import executar_campanha
from figuras_tp2 import gerar_figuras
from registros import escrever_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='configs/tp2.json')
    parser.add_argument('--output', default='results/tp2')
    parser.add_argument('--titulo', default='Campanha oficial TP2')
    args = parser.parse_args()
    output = Path(args.output)
    inicio_utc = datetime.now(timezone.utc).isoformat()
    inicio = time.perf_counter()
    novas = 0

    def resolver_com_progresso(config, referencia, seed, limites, observar=None):
        nonlocal novas
        resultado = resolver(config, referencia, seed, limites, observar=observar)
        novas += 1
        print(f'Busca nova {novas}: {config.metodo}/{config.id}; '
              f'{resultado.status}; {resultado.avaliacoes} avaliações; '
              f'{resultado.tempo_s:.2f}s', flush=True)
        return resultado

    resumo = executar_campanha(args.config, output, solver=resolver_com_progresso)
    medicao = {
        'inicio_utc': inicio_utc, 'config': args.config,
        'fase': 'coleta_concluida_auditoria_pendente',
        'concluidas': resumo['concluidas'], 'reutilizadas': resumo['reutilizadas'],
        'duracao_coleta_s': time.perf_counter() - inicio,
        'duracao_buscas_registradas_s': sum(r['tempo_s'] for r in resumo['execucoes']),
        'avaliacoes': sum(r['avaliacoes'] for r in resumo['execucoes']),
        'ressalva': 'Tempo desta invocação; em retomada, não é duração integral de todas as buscas.',
    }
    nome = 'medicao_retomada.json' if resumo['reutilizadas'] else 'medicao_oficial.json'
    # Guardar antes da auditoria permite retomar sem perder o cronômetro da coleta.
    escrever_json(output/nome, medicao)
    print(f"Coleta concluída: {resumo['concluidas']}/{resumo['esperadas']}; "
          f"{resumo['reutilizadas']} reutilizadas. Iniciando auditoria e figuras.", flush=True)
    inicio_produtos = time.perf_counter()
    try:
        produtos = gerar_figuras(output, output/'figuras', titulo=args.titulo)
    except Exception as erro:
        medicao.update(fase='falha_auditoria_ou_figuras', erro=f'{type(erro).__name__}: {erro}')
        escrever_json(output/nome, medicao)
        raise
    medicao.update(fase='auditada_com_figuras', auditoria=produtos['auditoria'],
                   duracao_auditoria_e_figuras_s=time.perf_counter()-inicio_produtos,
                   duracao_total_s=time.perf_counter()-inicio,
                   produtos=len(produtos['produtos_sha256']))
    escrever_json(output/nome, medicao)
    print(json.dumps(medicao, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
