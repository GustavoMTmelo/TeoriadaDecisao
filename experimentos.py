"""Campanhas TP2 reproduzíveis, registros atômicos e retomada revalidada."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import subprocess
from dataclasses import asdict
from pathlib import Path

from contratos import Candidato, ConfigBusca, ConfigEscalar
from registros import _ler_candidato, escrever_json, ler_resultado, salvar_resultado

SEEDS_BASE = (42, 123, 456, 789, 1011)


def criar_agenda(configuracoes=None, seeds_base=SEEDS_BASE):
    if configuracoes is None:
        from escalarizacoes import configuracoes_epsilon, configuracoes_ponderadas
        configuracoes = configuracoes_ponderadas() + configuracoes_epsilon()
    configuracoes, seeds_base = list(configuracoes), list(seeds_base)
    if (not configuracoes or not seeds_base or len(set(seeds_base)) != len(seeds_base)
            or any(type(s) is not int or s < 0 for s in seeds_base)):
        raise ValueError('Configurações e sementes-base devem ser não vazias e únicas.')
    agenda = []
    for base in seeds_base:
        for config in configuracoes:
            if config.metodo not in ('ponderada', 'epsilon'):
                raise ValueError('Campanha TP2 exige métodos ponderada ou epsilon.')
            payload = json.dumps([base, config.metodo, config.id], separators=(',', ':'))
            seed = int.from_bytes(hashlib.sha256(payload.encode()).digest()[:8], 'big')
            # IDs físicos derivam da identidade inteira, sem aceitar caminhos externos.
            identidade = hashlib.sha256(payload.encode()).hexdigest()
            agenda.append({'run_id': f'{config.metodo}_{base}_{identidade}',
                           'metodo': config.metodo, 'repeticao': base,
                           'config': asdict(config), 'seed': seed})
    if len({r['run_id'] for r in agenda}) != len(agenda):
        raise ValueError('Configurações com identidades duplicadas.')
    return agenda


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _manifesto(config_path, referencia_path, agenda, limites):
    import sol_inicial
    raiz = Path(__file__).parent
    dados = {nome: getattr(sol_inicial, nome) for nome in ('minerios', 'pilhas', 'sinters')}
    fontes = ('avaliacao.py', 'busca.py', 'contratos.py', 'escalarizacoes.py',
              'experimentos.py', 'normalizacao.py', 'pareto.py', 'registros.py',
              'sol_inicial.py', 'vizinhancas.py', 'vns.py')
    versoes = {'python': platform.python_version()}
    for nome in ('pytest', 'matplotlib'):
        try:
            versoes[nome] = importlib.metadata.version(nome)
        except importlib.metadata.PackageNotFoundError:
            versoes[nome] = None
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=raiz,
                                         text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        commit = None
    return {'schema_version': 1, 'git_commit_informativo': commit,
            'config_sha256': _hash(config_path),
            'referencia_sha256': _hash(referencia_path),
            'dados_sha256': hashlib.sha256(json.dumps(dados, sort_keys=True).encode()).hexdigest(),
            'codigo_sha256': {nome: _hash(raiz / nome) for nome in fontes if (raiz / nome).exists()},
            'versoes': versoes, 'limites': asdict(limites), 'agenda': agenda}


def executar_campanha(config_path, output_dir, *, solver=None):
    """Executa agenda completa; reutiliza somente arquivos íntegros do mesmo manifesto.

    Uma exceção/interrupção preserva runs concluídos. Arquivos .tmp nunca são lidos.
    Configurações e seeds explícitas permitem piloto e integração fora da campanha oficial.
    """
    from normalizacao import carregar_referencia
    from pareto import atualizar_arquivo
    if solver is None:
        from busca import resolver
        solver = resolver
    config_path, output = Path(config_path), Path(output_dir)
    dados = json.loads(config_path.read_text(encoding='utf-8'))
    ref_path = config_path.parent / dados['referencia']
    referencia = carregar_referencia(ref_path)
    limites = ConfigBusca(**dados.get('busca', {'max_avaliacoes': 10000}))
    if limites.max_avaliacoes is None:
        raise ValueError('Campanha exige teto de avaliações explícito.')
    configs = dados.get('configuracoes')
    configs = [ConfigEscalar(**{k: tuple(v) if isinstance(v, list) else v
                                for k, v in c.items()}) for c in configs] if configs is not None else None
    agenda = criar_agenda(configs, dados.get('seeds_base', SEEDS_BASE))
    manifesto = _manifesto(config_path, ref_path, agenda, limites)
    # Canonicaliza tuplas, garantindo comparação com manifesto previamente serializado.
    manifesto = json.loads(json.dumps(manifesto))
    manifest_path = output / 'manifesto.json'
    estado_runs = {r['run_id']: 'pendente' for r in agenda}
    if manifest_path.exists():
        anterior = json.loads(manifest_path.read_text(encoding='utf-8'))
        anterior.pop('estado_runs', None)
        atual_comparavel = dict(manifesto)
        anterior.pop('git_commit_informativo', None)
        atual_comparavel.pop('git_commit_informativo', None)
        if anterior != atual_comparavel:
            raise ValueError('Incompatibilidade de manifesto; use novo diretório de campanha.')
    else:
        if list((output / 'execucoes').glob('*.json')):
            raise ValueError('Registros existentes sem manifesto; use novo diretório.')
        escrever_json(manifest_path, {**manifesto, 'estado_runs': estado_runs})
    esperados = {r['run_id'] for r in agenda}
    encontrados = {p.stem for p in (output / 'execucoes').glob('*.json')}
    if encontrados - esperados:
        raise ValueError('Registros não previstos no manifesto.')
    arquivos, linhas, reutilizadas = {}, [], 0
    for run in agenda:
        config = ConfigEscalar(**{k: tuple(v) if isinstance(v, list) else v
                                  for k, v in run['config'].items()})
        meta = {**run, 'referencia': asdict(referencia), 'limites': asdict(limites)}
        meta = json.loads(json.dumps(meta))
        path = output / 'execucoes' / (run['run_id'] + '.json')
        observados = []
        if path.exists():
            resultado, salva = ler_resultado(path)
            if salva != meta:
                raise ValueError('Registro incompatível com manifesto.')
            payload = json.loads(path.read_text(encoding='utf-8'))
            if 'observados' not in payload:
                raise ValueError('Registro incompleto: faltam candidatos observados.')
            observados = [_ler_candidato(c, config, referencia) for c in payload['observados']]
            reutilizadas += 1
        else:
            indice = 0
            def observar(candidato):
                nonlocal indice
                indice += 1
                if candidato.avaliacao.viavel:
                    origem = {k: run[k] for k in ('metodo', 'repeticao', 'seed', 'run_id')}
                    origem.update(config_id=config.id, indice_avaliacao=indice)
                    observados.append(Candidato(candidato.solucao, candidato.avaliacao,
                                                [{**o, **origem} for o in candidato.origens]
                                                if candidato.origens else [origem]))
            resultado = solver(config, referencia, run['seed'], limites, observar=observar)
            if resultado.avaliacoes > limites.max_avaliacoes:
                raise ValueError('Solver excedeu orçamento de avaliações.')
            salvar_resultado(resultado, meta, path, observados)
            resultado, _ = ler_resultado(path)
        if resultado.avaliacoes > limites.max_avaliacoes:
            raise ValueError('Registro excedeu orçamento de avaliações.')
        estado_runs[run['run_id']] = 'concluido'
        escrever_json(manifest_path, {**manifesto, 'estado_runs': estado_runs})
        grupo = (run['metodo'], run['repeticao'])
        arquivo = arquivos.setdefault(grupo, [])
        for candidato in observados:
            arquivo = atualizar_arquivo(arquivo, candidato)
        arquivos[grupo] = arquivo
        melhor = resultado.melhor_viavel
        av = melhor.avaliacao if melhor else None
        linhas.append({**{k: run[k] for k in ('run_id', 'metodo', 'repeticao', 'seed')},
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
                       'motivo_parada': resultado.motivo_parada, 'tempo_s': resultado.tempo_s})
    caminhos = []
    conjuntos = dict(arquivos)
    for (metodo, _), arquivo in arquivos.items():
        unido = conjuntos.setdefault((metodo, 'uniao'), [])
        for candidato in arquivo:
            unido = atualizar_arquivo(unido, candidato)
        conjuntos[(metodo, 'uniao')] = unido
    for (metodo, repeticao), arquivo in sorted(conjuntos.items(), key=lambda item: str(item[0])):
        nome = f'pareto/{metodo}_{repeticao}.json'
        escrever_json(output / nome, [asdict(c) for c in arquivo])
        caminhos.append(nome)
    with (output / 'resumo.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=linhas[0].keys())
        writer.writeheader()
        writer.writerows(linhas)
    resumo = {'esperadas': len(agenda), 'concluidas': len(linhas), 'reutilizadas': reutilizadas,
              'arquivos_pareto': caminhos, 'execucoes': linhas}
    escrever_json(output / 'resumo.json', resumo)
    return resumo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=str(Path(__file__).parent / 'configs/tp2.json'))
    parser.add_argument('--output', default='results/tp2')
    args = parser.parse_args()
    print(json.dumps(executar_campanha(args.config, args.output), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
