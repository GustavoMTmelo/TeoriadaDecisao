"""Executar, revalidar independentemente e consolidar as 15 buscas TP1."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import subprocess
from collections import Counter
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

from contratos import ConfigBusca
from normalizacao import construir_referencia
from registros import (carregar_experimento, escrever_json, gerar_resumo_csv,
                       ler_resultado)
from sol_inicial import minerios, pilhas, sinters
from vns import (LAMBDA, SEMENTES, executar_experimento, plotar_convergencia,
                 plotar_melhor_solucao)

RAIZ = Path(__file__).resolve().parent
CODIGO = ('contratos.py', 'sol_inicial.py', 'avaliacao.py', 'vizinhancas.py',
          'vns.py', 'registros.py', 'normalizacao.py', 'reproduzir_tp1.py')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha256_codigo(path):
    """Git pode converter CRLF/LF em outro checkout; o código é o mesmo."""
    return hashlib.sha256(Path(path).read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def hash_dados():
    dados = {'minerios': minerios, 'pilhas': pilhas, 'sinters': sinters}
    return hashlib.sha256(json.dumps(dados, sort_keys=True).encode()).hexdigest()


def criar_manifesto(limites):
    def git(*args):
        try:
            return subprocess.check_output(['git', '-C', str(RAIZ), *args],
                                           text=True, encoding='utf-8').strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    agenda = [{'run_id': f'{obj}_{i:02}_seed{seed}', 'objetivo': obj, 'repeticao': i,
               'seed': seed} for obj in ('f1', 'f2', 'f3')
              for i, seed in enumerate(SEMENTES, 1)]
    return {'schema_version': 1, 'criado_utc': datetime.now(timezone.utc).isoformat(),
            'python': platform.python_version(), 'plataforma': platform.platform(),
            'dependencias': {p: importlib.metadata.version(p) for p in ('matplotlib', 'pytest', 'numpy')},
            'commit': git('rev-parse', 'HEAD'), 'git_status_inicial': git('status', '--short'),
            'codigo_sha256': {nome: sha256_codigo(RAIZ/nome) for nome in CODIGO},
            'codigo_hash_normaliza_linhas': True,
            'dados_sha256': hash_dados(), 'configuracao_busca': asdict(limites),
            'lambdas': dict(LAMBDA), 'agenda': agenda, 'estado': 'em_execucao'}


def verificar_composicao_independente(solucao):
    """Não usa os validadores ou funções objetivo da busca como oráculo."""
    if set(solucao) != set(pilhas):
        raise ValueError('Faltam/sobram pilhas na auditoria independente.')
    uso = Counter()
    custo, f2, f3 = 0, 0., 0.
    for p, composicao in solucao.items():
        dados_pilha = pilhas[p]
        if not isinstance(composicao, list) or len(composicao)*2 != dados_pilha['massa_kt']:
            raise ValueError(f'Massa inválida na pilha {p}.')
        quantidades = Counter(composicao)
        uso.update(quantidades)
        grupo = dados_pilha['sinter']
        if any(m not in minerios or not minerios[m][f's{grupo}'] for m in quantidades):
            raise ValueError(f'Compatibilidade inválida na pilha {p}.')
        medias = {q: sum(minerios[m][q]*n*2 for m, n in quantidades.items()) /
                  dados_pilha['massa_kt'] for q in ('sio2', 'al2o3')}
        for q, valor in medias.items():
            limites = sinters[grupo]
            if not limites[q+'_min']-1e-9 <= valor <= limites[q+'_max']+1e-9:
                raise ValueError(f'Qualidade inválida na pilha {p}: {q}.')
        custo += sum(minerios[m]['custo']*n*2000 for m, n in quantidades.items())
        f2 += (medias['sio2']-sinters[grupo]['sio2_alvo'])**2
        f3 += (medias['al2o3']-sinters[grupo]['al2o3_alvo'])**2
    if any(not d['disp_min'] <= uso[m] <= d['disp_max'] for m, d in minerios.items()):
        raise ValueError('Disponibilidade inválida na auditoria independente.')
    return custo, f2, f3


def verificar_campanha(diretorio):
    d = Path(diretorio)
    manifesto = json.loads((d/'manifesto.json').read_text(encoding='utf-8'))
    esperado = {f'{obj}_{i:02}_seed{seed}' for obj in ('f1', 'f2', 'f3')
                for i, seed in enumerate(SEMENTES, 1)}
    arquivos = {p.stem: p for p in (d/'execucoes').glob('*.json')}
    if set(arquivos) != esperado:
        raise ValueError('Campanha deve conter exatamente as 15 execuções previstas.')
    if {r['run_id'] for r in manifesto['agenda']} != esperado or len(manifesto['agenda']) != 15:
        raise ValueError('Agenda não corresponde às 15 execuções.')
    if manifesto['dados_sha256'] != hash_dados():
        raise ValueError('Dados atuais diferem dos usados na campanha.')
    registros = []
    for item in manifesto['agenda']:
        r, meta = ler_resultado(arquivos[item['run_id']])
        if any(meta[k] != item[k] for k in ('run_id', 'objetivo', 'seed', 'repeticao')):
            raise ValueError('Identidade da execução divergente da agenda.')
        if (meta['configuracao_busca'] != manifesto['configuracao_busca']
                or meta['lambda'] != manifesto['lambdas'][meta['objetivo']]):
            raise ValueError('Parâmetros da configuração divergentes do manifesto.')
        if r.melhor_viavel is None:
            raise ValueError(f"{item['run_id']}: sem viável; não congelar referências.")
        vetor = verificar_composicao_independente(r.melhor_viavel.solucao)
        salvo = r.melhor_viavel.avaliacao.objetivos
        if vetor[0] != salvo[0] or any(abs(a-b) > 1e-8 for a,b in zip(vetor[1:], salvo[1:])):
            raise ValueError('Objetivos divergentes na auditoria independente.')
        c = replace(r.melhor_viavel, origens=[dict(o, run_id=item['run_id'])
                                            for o in r.melhor_viavel.origens] or [item])
        registros.append((r, meta, c))
    return registros, manifesto


def _referencia_documentada(d, registros, manifesto):
    ref = construir_referencia([c for _, _, c in registros])
    return dict(asdict(ref), schema_version=1, tipo='extremos_empiricos_15_finais_tp1',
                dados_sha256=manifesto['dados_sha256'],
                fontes={meta['run_id']: sha256(d/'execucoes'/f"{meta['run_id']}.json")
                        for _, meta, _ in registros})


def consolidar(diretorio, gerar_figuras=True):
    d = Path(diretorio)
    registros, manifesto = verificar_campanha(d)
    if not manifesto.get('codigo_hash_normaliza_linhas'):
        # Compatibilidade com a coleta iniciada antes da revisão do verificador.
        # Apenas fontes de consolidação podem ter mudado; não reatribuir hashes
        # atuais a um algoritmo de busca diferente daquele efetivamente executado.
        permitidos = {'reproduzir_tp1.py', 'normalizacao.py'}
        for nome, valor in manifesto['codigo_sha256'].items():
            if nome not in permitidos and sha256(RAIZ/nome) != valor:
                raise ValueError('Código de busca alterado desde a coleta: ' + nome)
        manifesto['codigo_coleta_sha256_bytes'] = dict(manifesto['codigo_sha256'])
        manifesto['codigo_sha256'] = {nome: sha256_codigo(RAIZ/nome)
                                      for nome in manifesto['codigo_sha256']}
        manifesto['codigo_hash_normaliza_linhas'] = True
    referencia = _referencia_documentada(d, registros, manifesto)
    # Só publicar referências depois de verificar as 15, nunca parcialmente.
    escrever_json(d/'referencias_tp1.json', referencia)
    if d.resolve() == (RAIZ/'results/tp1_corrigido').resolve():
        escrever_json(RAIZ/'results/referencias_tp1.json', referencia)
    linhas = gerar_resumo_csv(d)
    campos = ['run_id', 'objetivo', 'seed', 'f1', 'f2', 'f3']
    with (d/'objetivos_cruzados.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows({k: linha[k] for k in campos} for linha in linhas)
    matriz = []
    estatisticas = {}
    for obj in ('f1', 'f2', 'f3'):
        r, meta, cand = min((x for x in registros if x[1]['objetivo'] == obj),
                            key=lambda x: x[2].avaliacao.escalar)
        matriz.append({'objetivo_otimizado': obj, 'run_id': meta['run_id'],
                       **dict(zip(('f1', 'f2', 'f3'), cand.avaliacao.objetivos))})
        exp = carregar_experimento(d, obj)
        estatisticas[obj] = {k: exp[k] for k in ('minimo','media','desvio','maximo','n_viaveis','n_falhas')}
        escrever_json(d/f'estatisticas_{obj}.json', exp)
        if gerar_figuras:
            plotar_convergencia(exp, d/f'convergencia_{obj}.png')
            plotar_melhor_solucao(exp, d/f'melhor_solucao_{obj}.png')
    with (d/'matriz_payoff.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=matriz[0].keys())
        w.writeheader(); w.writerows(matriz)
    resumo = {'n_execucoes': len(registros), 'n_viaveis': len(registros),
              'referencia_id': referencia['id'], 'estatisticas': estatisticas,
              'matriz_payoff': matriz}
    escrever_json(d/'auditoria.json', resumo)
    from relatorio_tp1 import gerar_fragmento
    gerar_fragmento(d, resumo, referencia)
    manifesto['estado'] = 'concluida_validada'
    manifesto['referencia_id'] = referencia['id']
    manifesto['execucoes_sha256'] = referencia['fontes']
    # Preserva os hashes da coleta original e registra separadamente a consolidação.
    manifesto['codigo_consolidacao_sha256'] = {nome: sha256_codigo(RAIZ/nome)
                                              for nome in ('reproduzir_tp1.py', 'normalizacao.py', 'relatorio_tp1.py')}
    manifesto['figuras_geradas'] = gerar_figuras
    produtos = ['resumo.csv', 'objetivos_cruzados.csv', 'matriz_payoff.csv', 'auditoria.json', 'resultados_tp1.tex']
    produtos += [f'estatisticas_{obj}.json' for obj in ('f1', 'f2', 'f3')]
    if gerar_figuras:
        produtos += [f'{tipo}_{obj}.png' for obj in ('f1', 'f2', 'f3')
                     for tipo in ('convergencia', 'melhor_solucao')]
    manifesto['artefatos_sha256'] = {nome: sha256(d/nome) for nome in produtos}
    manifesto['consolidado_utc'] = datetime.now(timezone.utc).isoformat()
    escrever_json(d/'manifesto.json', manifesto)
    return resumo


def verificar_artefatos(diretorio):
    d = Path(diretorio)
    registros, manifesto = verificar_campanha(d)
    esperado = _referencia_documentada(d, registros, manifesto)
    salvo = json.loads((d/'referencias_tp1.json').read_text(encoding='utf-8'))
    # JSON converte tuplas em listas; comparação canônica preserva os números.
    if json.dumps(salvo, sort_keys=True) != json.dumps(esperado, sort_keys=True):
        raise ValueError('Referências ou hashes das fontes divergentes.')
    if d.resolve() == (RAIZ/'results/tp1_corrigido').resolve():
        canonico = RAIZ/'results/referencias_tp1.json'
        if not canonico.is_file() or json.loads(canonico.read_text(encoding='utf-8')) != salvo:
            raise ValueError('Referência canônica em results/referencias_tp1.json divergente.')
    if manifesto.get('estado') != 'concluida_validada':
        raise ValueError('Manifesto não concluído.')
    obrigatorios = {'resumo.csv', 'objetivos_cruzados.csv', 'matriz_payoff.csv', 'auditoria.json', 'resultados_tp1.tex'}
    obrigatorios.update(f'estatisticas_{obj}.json' for obj in ('f1', 'f2', 'f3'))
    if manifesto.get('figuras_geradas'):
        obrigatorios.update(f'{tipo}_{obj}.png' for obj in ('f1','f2','f3')
                            for tipo in ('convergencia', 'melhor_solucao'))
    hashes = manifesto.get('artefatos_sha256', {})
    if set(hashes) != obrigatorios:
        raise ValueError('Manifesto não contém todos os produtos esperados.')
    for nome, identidade in hashes.items():
        if not (d/nome).is_file() or sha256(d/nome) != identidade:
            raise ValueError(f'Artefato ausente ou alterado: {nome}.')
    for obj in ('f1', 'f2', 'f3'):
        esperado_exp = carregar_experimento(d, obj)
        salvo_exp = json.loads((d/f'estatisticas_{obj}.json').read_text(encoding='utf-8'))
        if json.loads(json.dumps(esperado_exp)) != salvo_exp:
            raise ValueError(f'Estatísticas divergem dos registros de {obj}.')
    hashes_codigo = dict(manifesto['codigo_sha256'])
    hashes_codigo.update(manifesto.get('codigo_consolidacao_sha256', {}))
    return {'n_execucoes': len(registros), 'n_viaveis': len(registros),
            'referencia_id': salvo['id'],
            'codigo_atual_confere': all(sha256_codigo(RAIZ/n)==h for n,h in hashes_codigo.items()),
            'artefatos_verificados': len(hashes), 'figuras_verificadas': 6 if manifesto.get('figuras_geradas') else 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('results/tp1_corrigido'))
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument('--verificar', action='store_true', help='Somente revalidar arquivos existentes.')
    modo.add_argument('--regerar', action='store_true', help='Regerar referências, tabelas e figuras dos registros.')
    args = parser.parse_args()
    d = args.output
    if args.verificar:
        print(json.dumps(verificar_artefatos(d), ensure_ascii=False, indent=2))
        return
    if not args.regerar:
        if d.exists() and any(d.iterdir()):
            raise ValueError('Saída não vazia; escolha novo diretório ou use --regerar/--verificar.')
        escrever_json(d/'manifesto.json', criar_manifesto(ConfigBusca()))
        for obj in ('f1', 'f2', 'f3'):
            executar_experimento(obj, output_dir=d)
    resumo = consolidar(d)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
