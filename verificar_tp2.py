"""Audita campanha TP2 salva, sem buscas e sem modificar qualquer artefato."""
import argparse
import csv
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from avaliacao import avaliar
from contratos import Candidato, ConfigEscalar, Referencia
from normalizacao import validar_referencia
from pareto import chave_solucao, consolidar_arquivo
from registros import ler_resultado, _ler_candidato
from sol_inicial import calcular_f1, calcular_f2, calcular_f3, validar_estrutura, validar_qualidade


def _json(valor):
    return json.dumps(valor, sort_keys=True, ensure_ascii=False)


def _ler(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def _config(dados):
    return ConfigEscalar(**{k: tuple(v) if isinstance(v, list) else v for k, v in dados.items()})


def _referencia(dados):
    ref = Referencia(tuple(dados['minimo']), tuple(dados['maximo']), dados['id'], dados['origens'])
    validar_referencia(ref)
    payload = {k: dados[k] for k in ('minimo', 'maximo', 'origens')}
    identidade = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    _exigir(ref.id == identidade, 'Identidade da referência divergente.')
    return ref


def _fisica(candidato):
    sol = candidato.solucao
    _exigir(validar_estrutura(sol)[0], 'Estrutura física inválida.')
    vetor = (calcular_f1(sol), calcular_f2(sol), calcular_f3(sol))
    _exigir(vetor == candidato.avaliacao.objetivos, 'Objetivos brutos divergem do recálculo direto.')
    _exigir(validar_qualidade(sol)[0] == candidato.avaliacao.qualidade_ok,
            'Qualidade física divergente.')


def _linha(run, resultado):
    config = _config(run['config'])
    av = resultado.melhor_viavel.avaliacao if resultado.melhor_viavel else None
    return {**{k: run[k] for k in ('run_id', 'metodo', 'repeticao', 'seed')},
            'config_id': config.id, 'status': resultado.status,
            'pesos': json.dumps(config.pesos), 'epsilons': json.dumps(config.epsilons),
            'f1': av.objetivos[0] if av else None,
            'f2': av.objetivos[1] if av else None,
            'f3': av.objetivos[2] if av else None,
            'escalar': av.escalar if av else None,
            'normalizados': json.dumps(av.normalizados) if av else None,
            'estrutura_ok': av.estrutura_ok if av else None,
            'qualidade_ok': av.qualidade_ok if av else None,
            'epsilon_ok': av.epsilon_ok if av else None,
            'violacao': av.violacao if av else None,
            'avaliacoes': resultado.avaliacoes, 'iteracoes': resultado.iteracoes,
            'motivo_parada': resultado.motivo_parada, 'tempo_s': resultado.tempo_s}


def _assinatura(candidato):
    return (chave_solucao(candidato.solucao), candidato.avaliacao.objetivos,
            tuple(sorted(_json(o) for o in candidato.origens)))


def verificar_campanha(output_dir):
    """Revalida todas as execuções, origens, arquivos ND 3D e resumos da campanha."""
    try:
        return _verificar(Path(output_dir))
    except (KeyError, TypeError, IndexError, OSError, json.JSONDecodeError) as erro:
        raise ValueError(f'Campanha incompleta ou malformada: {erro}') from erro


def _verificar(output):
    manifesto = _ler(output/'manifesto.json')
    _exigir(manifesto['schema_version'] == 1, 'Versão de manifesto desconhecida.')
    agenda = manifesto['agenda']
    ids = [r['run_id'] for r in agenda]
    _exigir(ids and len(set(ids)) == len(ids), 'Agenda vazia ou duplicada.')
    _exigir(manifesto['estado_runs'] == {i: 'concluido' for i in ids}, 'Agenda não concluída.')
    _exigir({p.stem for p in (output/'execucoes').glob('*.json')} == set(ids),
            'Registros diferem da agenda.')
    runs, observados, linhas = {}, [], []
    ref_comum = None
    for run in agenda:
        rid = run['run_id']
        identidade = json.dumps([run['repeticao'], run['metodo'], run['config']['id']], separators=(',', ':'))
        digest = hashlib.sha256(identidade.encode()).digest()
        _exigir(run['seed'] == int.from_bytes(digest[:8], 'big') and
                rid == f"{run['metodo']}_{run['repeticao']}_{digest.hex()}", 'Identidade ou seed da agenda divergente.')
        _exigir(Path(rid).name == rid, 'Identidade de execução inválida.')
        path = output/'execucoes'/f'{rid}.json'
        resultado, meta = ler_resultado(path)
        _exigir(all(meta[k] == v for k, v in run.items()), 'Metadados divergem da agenda.')
        _exigir(meta['limites'] == manifesto['limites'], 'Limites divergem do manifesto.')
        teto = manifesto['limites']['max_avaliacoes']
        _exigir(teto is not None and resultado.avaliacoes <= teto, 'Orçamento violado.')
        referencia = _referencia(meta['referencia'])
        if ref_comum is None:
            ref_comum = _json(meta['referencia'])
        _exigir(ref_comum == _json(meta['referencia']), 'Referências diferentes entre execuções.')
        config = _config(run['config'])
        payload = _ler(path)
        for c in (resultado.melhor_viavel, resultado.melhor_busca):
            if c is not None:
                _fisica(c)
        atuais = [_ler_candidato(d, config, referencia) for d in payload['observados']]
        for c in atuais:
            _fisica(c)
            _exigir(c.avaliacao.viavel, 'Observado inviável.')
        runs[rid] = (config, referencia, atuais)
        observados.extend(atuais)
        linhas.append(_linha(run, resultado))

    grupos = {(r['metodo'], r['repeticao']) for r in agenda}
    grupos |= {(r['metodo'], 'uniao') for r in agenda}
    nomes = []
    total_pontos = 0
    for metodo, repeticao in sorted(grupos, key=str):
        nome = f'pareto/{metodo}_{repeticao}.json'
        nomes.append(nome)
        esperado = consolidar_arquivo(observados, metodo=metodo,
                                      repeticao=None if repeticao == 'uniao' else repeticao)
        exportados = _ler(output/nome)
        candidatos = []
        for dados in exportados:
            solucao = {int(p): xs for p, xs in dados['solucao'].items()}
            origens = dados['origens']
            _exigir(isinstance(origens, list) and bool(origens), 'Origem ausente no Pareto.')
            chave = chave_solucao(solucao)
            for origem in origens:
                config, referencia, fontes = runs[origem['run_id']]
                _exigir(any(chave_solucao(c.solucao) == chave and origem in c.origens for c in fontes),
                        'Origem Pareto não corresponde a candidato observado.')
                _exigir(avaliar(solucao, config, referencia).viavel, 'Ponto viola restrições da origem.')
            config, referencia, _ = runs[origens[0]['run_id']]
            av = avaliar(solucao, config, referencia)
            _exigir(_json(dados['avaliacao']) == _json(asdict(av)), 'Avaliação Pareto divergente.')
            c = Candidato(solucao, av, origens)
            _fisica(c)
            candidatos.append(c)
        _exigir(sorted(map(_assinatura, candidatos)) == sorted(map(_assinatura, esperado)),
                'Arquivo Pareto diverge da consolidação 3D e proveniência.')
        _exigir(len({chave_solucao(c.solucao) for c in candidatos}) == len(candidatos), 'Composição Pareto duplicada.')
        total_pontos += len(candidatos)
    _exigir({str(p.relative_to(output)).replace('\\', '/') for p in (output/'pareto').glob('*.json')} == set(nomes),
            'Conjunto de exportações Pareto divergente.')
    resumo = _ler(output/'resumo.json')
    _exigir(resumo['esperadas'] == resumo['concluidas'] == len(agenda), 'Contadores do resumo divergentes.')
    _exigir(type(resumo['reutilizadas']) is int and 0 <= resumo['reutilizadas'] <= len(agenda), 'Contagem de reutilizações inválida.')
    _exigir(resumo['execucoes'] == linhas and resumo['arquivos_pareto'] == nomes, 'Resumo JSON divergente dos registros.')
    with (output/'resumo.csv').open(encoding='utf-8', newline='') as arquivo:
        csv_salvo = list(csv.DictReader(arquivo))
    csv_esperado = [{k: '' if v is None else str(v) for k, v in linha.items()} for linha in linhas]
    _exigir(csv_salvo == csv_esperado, 'Resumo CSV divergente dos registros.')
    return {'execucoes': len(agenda), 'observados': len(observados),
            'arquivos_pareto': len(nomes), 'pontos_exportados': total_pontos,
            'status': 'verificado'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(verificar_campanha(args.output), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
