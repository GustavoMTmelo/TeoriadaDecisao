"""Persistência JSON v1, releitura com recálculo e estatísticas só de viáveis."""

import csv
import json
import math
import statistics
from dataclasses import asdict
from pathlib import Path

from avaliacao import avaliar
from contratos import Avaliacao, Candidato, ConfigEscalar, ResultadoBusca


def escrever_json(path, dados):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    temporario = path.with_suffix(path.suffix + '.tmp')
    temporario.write_text(texto, encoding='utf-8')
    temporario.replace(path)


def salvar_resultado(resultado, metadados, path):
    escrever_json(path, {'schema_version': 1, 'metadados': metadados,
                        'resultado': asdict(resultado)})
    # Não basta serializar: a mesma leitura exigida de resultados externos é aplicada.
    ler_resultado(path)


def _ler_candidato(dados, config):
    if dados is None:
        return None
    try:
        solucao = {int(p): composicao for p, composicao in dados['solucao'].items()}
        salvo = dados['avaliacao']
        atual = avaliar(solucao, config)
        if not atual.estrutura_ok:
            raise ValueError('Composição estruturalmente inválida.')
        for campo in ('estrutura_ok', 'qualidade_ok', 'epsilon_ok'):
            if salvo[campo] != getattr(atual, campo):
                raise ValueError(f'Validação divergente: {campo}.')
        for j, (a, b) in enumerate(zip(salvo['objetivos'], atual.objetivos)):
            if not math.isfinite(a) or (a != b if j == 0 else abs(a-b) > 1e-8):
                raise ValueError('Objetivos salvos divergem da composição.')
        if len(salvo['objetivos']) != 3:
            raise ValueError('Esperados três objetivos.')
        for campo in ('escalar', 'violacao'):
            if not math.isclose(salvo[campo], getattr(atual, campo), rel_tol=1e-12, abs_tol=1e-9):
                raise ValueError(f'Avaliação divergente: {campo}.')
        if (salvo['normalizados'] is not None or tuple(salvo['chave']) != atual.chave
                or tuple(salvo['erros']) != atual.erros):
            raise ValueError('Campos derivados da avaliação divergentes.')
        return Candidato(solucao, atual, dados['origens'])
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError('Registro de candidato malformado.') from exc


def ler_resultado(path):
    dados = json.loads(Path(path).read_text(encoding='utf-8'))
    if dados.get('schema_version') != 1:
        raise ValueError('Versão de registro não suportada.')
    meta = dados['metadados']
    objetivo = meta['objetivo']
    if objetivo not in ('f1', 'f2', 'f3'):
        raise ValueError('Objetivo desconhecido no registro.')
    config = ConfigEscalar('mono', objetivo, objetivo=int(objetivo[1]))
    r = dados['resultado']
    return ResultadoBusca(r['status'], _ler_candidato(r['melhor_viavel'], config),
                          _ler_candidato(r['melhor_busca'], config), r['historico'],
                          r['avaliacoes'], r['iteracoes'], r['motivo_parada'],
                          r['tempo_s'], r['tentativas_invalidas']), meta


def resumir_experimento(objetivo, execucoes):
    resultados = [r.melhor_viavel.avaliacao.escalar if r.melhor_viavel else None
                  for r in execucoes]
    validos = [v for v in resultados if v is not None]
    melhor = min((r.melhor_viavel for r in execucoes if r.melhor_viavel),
                 key=lambda c: c.avaliacao.escalar, default=None)
    return {'objetivo': objetivo, 'resultados': resultados,
            'historicos': [[h['melhor_viavel'] for h in r.historico] for r in execucoes],
            'melhor_solucao': melhor.solucao if melhor else None,
            'melhor_valor': melhor.avaliacao.escalar if melhor else None,
            'media': statistics.mean(validos) if validos else None,
            'desvio': statistics.stdev(validos) if len(validos) > 1 else None,
            'minimo': min(validos) if validos else None,
            'maximo': max(validos) if validos else None,
            'n_viaveis': len(validos), 'n_falhas': len(resultados)-len(validos)}


def carregar_experimento(diretorio, objetivo):
    registros = [ler_resultado(p) for p in sorted((Path(diretorio)/'execucoes').glob(f'{objetivo}_*.json'))]
    if not registros:
        raise ValueError(f'Não há registros de {objetivo}.')
    if any(meta['objetivo'] != objetivo for _, meta in registros):
        raise ValueError('Nome de arquivo e objetivo inconsistentes.')
    return resumir_experimento(objetivo, [r for r, _ in registros])


def gerar_resumo_csv(diretorio):
    linhas = []
    for p in sorted((Path(diretorio)/'execucoes').glob('*.json')):
        r, meta = ler_resultado(p)
        c = r.melhor_viavel
        av = c.avaliacao if c else None
        linhas.append({'run_id': p.stem, 'objetivo': meta['objetivo'], 'seed': meta['seed'],
                       'status': r.status, 'estrutura_ok': av.estrutura_ok if av else None,
                       'qualidade_ok': av.qualidade_ok if av else None,
                       'f1': av.objetivos[0] if av else None,
                       'f2': av.objetivos[1] if av else None,
                       'f3': av.objetivos[2] if av else None,
                       'penalidade': av.violacao if av else None,
                       'avaliacoes': r.avaliacoes, 'iteracoes': r.iteracoes,
                       'motivo_parada': r.motivo_parada, 'tempo_decorrido_s': r.tempo_s,
                       'tentativas_invalidas': r.tentativas_invalidas})
    if not linhas:
        raise ValueError('Nenhuma execução registrada.')
    with (Path(diretorio)/'resumo.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=linhas[0].keys())
        writer.writeheader()
        writer.writerows(linhas)
    return linhas
