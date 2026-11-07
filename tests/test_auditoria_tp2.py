"""Auditoria somente leitura de campanha, exportações e proveniência."""
import importlib.util
import json
from pathlib import Path
from dataclasses import asdict
import hashlib

import pytest
from contratos import Referencia, Candidato, ResultadoBusca


@pytest.fixture
def campanha(modelo_pequeno, tmp_path, request):
    from avaliacao import avaliar
    from experimentos import executar_campanha
    origens = {f'f{j}': {'minimo': ['min'], 'maximo': ['max']} for j in range(1, 4)}
    payload = {'minimo': [0, 0, 0], 'maximo': [100000, 1, 1], 'origens': origens}
    ref = {**payload, 'id': hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()}
    (tmp_path/'ref.json').write_text(json.dumps(ref), encoding='utf-8')
    config = {'referencia': 'ref.json', 'seeds_base': [42, 123], 'busca': {'max_avaliacoes': 3},
              'configuracoes': [{'metodo': 'ponderada', 'id': 'p', 'pesos': [1, 0, 0]},
                               {'metodo': 'epsilon', 'id': 'e', 'epsilons': [0, 0]}]}
    path = tmp_path/'config.json'
    path.write_text(json.dumps(config), encoding='utf-8')
    def solver(config, referencia, seed, limites, observar):
        sol = modelo_pequeno[0] if getattr(request, 'param', None) == 'sem_viavel' else modelo_pequeno[1]
        c = Candidato(sol, avaliar(sol, config, referencia))
        observar(c)
        return ResultadoBusca('viavel' if c.avaliacao.viavel else 'sem_viavel_encontrada',
                              c if c.avaliacao.viavel else None, c, [], 1, 0, 'max_iter', 0.)
    out = tmp_path/'out'
    executar_campanha(path, out, solver=solver)
    return out


def verificar(out):
    assert importlib.util.find_spec('verificar_tp2'), 'verificador independente ausente'
    from verificar_tp2 import verificar_campanha
    return verificar_campanha(out)


def test_auditoria_recalcula_sem_escrever_ou_buscar(campanha, monkeypatch):
    import busca
    def proibido(*args, **kwargs):
        raise AssertionError('Auditoria executou busca')
    monkeypatch.setattr(busca, 'resolver', proibido)
    antes = {p.relative_to(campanha): p.read_bytes() for p in campanha.rglob('*') if p.is_file()}
    resultado = verificar(campanha)
    assert resultado['execucoes'] == 4 and resultado['arquivos_pareto'] == 6
    assert resultado['observados'] == 4
    assert antes == {p.relative_to(campanha): p.read_bytes() for p in campanha.rglob('*') if p.is_file()}


@pytest.mark.parametrize('alvo', ['objetivo', 'origem', 'resumo_json', 'resumo_csv', 'estado', 'ponto_ausente'])
def test_auditoria_rejeita_artefatos_adulterados(campanha, alvo):
    if alvo in ('objetivo', 'origem', 'ponto_ausente'):
        path = next((campanha/'pareto').glob('*.json'))
        dados = json.loads(path.read_text(encoding='utf-8'))
        if alvo == 'objetivo': dados[0]['avaliacao']['objetivos'][0] += 1
        elif alvo == 'origem': dados[0]['origens'][0]['seed'] += 1
        else: dados = []
    elif alvo == 'estado':
        path = campanha/'manifesto.json'
        dados = json.loads(path.read_text(encoding='utf-8'))
        dados['estado_runs'][next(iter(dados['estado_runs']))] = 'pendente'
    elif alvo == 'resumo_json':
        path = campanha/'resumo.json'
        dados = json.loads(path.read_text(encoding='utf-8'))
        dados['execucoes'][0]['f1'] += 1
    else:
        path = campanha/'resumo.csv'
        path.write_text(path.read_text(encoding='utf-8').replace('40000', '40001'), encoding='utf-8')
        dados = None
    if dados is not None: path.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError): verificar(campanha)


@pytest.mark.parametrize('campanha', ['sem_viavel'], indirect=True)
def test_auditoria_ausencia_de_viavel_e_exports_vazios(campanha):
    resultado = verificar(campanha)
    assert resultado['execucoes'] == 4
    assert resultado['observados'] == resultado['pontos_exportados'] == 0


def test_cli_auditoria(campanha, monkeypatch, capsys):
    verificar(campanha)
    from verificar_tp2 import main
    monkeypatch.setattr('sys.argv', ['verificar_tp2.py', '--output', str(campanha)])
    main()
    assert json.loads(capsys.readouterr().out)['status'] == 'verificado'
