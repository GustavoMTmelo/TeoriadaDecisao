"""Executa e audita o piloto externo, medindo também persistência e consolidação."""

import argparse
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

from experimentos import executar_campanha
from registros import escrever_json
from verificar_tp2 import verificar_campanha


def resumir_piloto(resumo, duracao_s, auditoria_s, tamanho_bytes, reutilizadas=0):
    """Estima custo somente se a medição inclui todas as buscas, sem retomada."""
    grupos = defaultdict(list)
    for run in resumo['execucoes']:
        grupos[run['metodo']].append(run)
    por_metodo = {}
    por_configuracao = {}
    for metodo, runs in sorted(grupos.items()):
        tempos = [r['tempo_s'] for r in runs]
        viaveis = sum(r['status'] == 'viavel' for r in runs)
        por_metodo[metodo] = {
            'runs': len(runs), 'viaveis': viaveis,
            'sem_viavel_encontrada': len(runs) - viaveis,
            'fracao_viaveis': viaveis / len(runs),
            'avaliacoes': sum(r['avaliacoes'] for r in runs),
            'tempo_buscas_s': sum(tempos),
            'mediana_busca_s': statistics.median(tempos),
            'maximo_busca_s': max(tempos),
        }
        for config_id in sorted({r['config_id'] for r in runs}):
            selecionadas = [r for r in runs if r['config_id'] == config_id]
            por_configuracao[f'{metodo}/{config_id}'] = {
                'runs': len(selecionadas),
                'viaveis': sum(r['status'] == 'viavel' for r in selecionadas),
                'avaliacoes': sum(r['avaliacoes'] for r in selecionadas),
                'motivos_parada': sorted({r['motivo_parada'] for r in selecionadas}),
            }
    n = len(resumo['execucoes'])
    pode_estimar = bool(n) and not reutilizadas
    return {
        'runs': n, 'reutilizadas': reutilizadas,
        'duracao_campanha_s': duracao_s, 'duracao_auditoria_s': auditoria_s,
        'tamanho_campanha_bytes': tamanho_bytes,
        'por_metodo': por_metodo, 'por_configuracao': por_configuracao,
        'estimativa_160_runs_s': duracao_s * 160 / n if pode_estimar else None,
        'estimativa_160_runs_com_folga_50pct_s': duracao_s * 240 / n if pode_estimar else None,
        'ressalva_estimativa': (
            'Extrapolação de tempo total; consolidação Pareto e auditoria podem crescer '
            'mais que linearmente. Não é garantia de duração.' if pode_estimar else
            'Retomada não mede o custo de todas as buscas; preservar a medição original.'
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='configs/tp2_piloto.json')
    parser.add_argument('--output', default='results/piloto_tp2_lote')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    if set(config.get('seeds_base', ())) & {42, 123, 456, 789, 1011}:
        parser.error('O piloto deve usar sementes-base externas à campanha oficial.')
    output = Path(args.output)
    inicio = time.perf_counter()
    from busca import resolver

    concluidas = 0

    def observar_progresso(*pos, **kw):
        nonlocal concluidas
        resultado = resolver(*pos, **kw)
        concluidas += 1
        print(f'Busca nova {concluidas}: {pos[0].metodo}/{pos[0].id}; '
              f'{resultado.status}; {resultado.avaliacoes} avaliações; '
              f'{resultado.tempo_s:.2f}s', flush=True)
        return resultado

    resumo = executar_campanha(args.config, output, solver=observar_progresso)
    duracao = time.perf_counter() - inicio
    inicio_auditoria = time.perf_counter()
    auditoria = verificar_campanha(output)
    tempo_auditoria = time.perf_counter() - inicio_auditoria
    tamanho = sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
    medicao = resumir_piloto(resumo, duracao, tempo_auditoria, tamanho, resumo['reutilizadas'])
    medicao['auditoria'] = auditoria
    medicao['pareto_uniao'] = {
        metodo: len(json.loads((output/'pareto'/f'{metodo}_uniao.json').read_text(encoding='utf-8')))
        for metodo in medicao['por_metodo']
    }
    # Não substituir tempo de uma campanha completa pelo tempo de uma retomada.
    nome = 'medicao_retomada.json' if resumo['reutilizadas'] else 'medicao_piloto.json'
    escrever_json(output/nome, medicao)
    print(json.dumps(medicao, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
