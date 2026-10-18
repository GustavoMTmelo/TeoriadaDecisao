import json
from dataclasses import asdict

import pytest

from contratos import Candidato, ConfigEscalar, Referencia, ResultadoBusca


def test_agenda_completa_estavel_e_independente_da_ordem():
    from experimentos import criar_agenda
    agenda = criar_agenda()
    assert len(agenda) == len({r['run_id'] for r in agenda}) == 160
    assert len({r['seed'] for r in agenda}) == 160
    configs = [ConfigEscalar('ponderada', 'a', pesos=(1., 0., 0.)),
               ConfigEscalar('epsilon', 'b', epsilons=(1., 1.))]
    normal = criar_agenda(configs, [42, 123])
    inversa = criar_agenda(configs[::-1], [123, 42])
    assert {r['run_id']: r['seed'] for r in normal} == {r['run_id']: r['seed'] for r in inversa}


def preparar(tmp_path):
    import hashlib
    origens = {f'f{j}': {'minimo': ['min'], 'maximo': ['max']} for j in range(1, 4)}
    payload = {'minimo': (0., 0., 0.), 'maximo': (100000., 1., 1.), 'origens': origens}
    identidade = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    ref = Referencia(payload['minimo'], payload['maximo'], identidade, origens)
    (tmp_path / 'ref.json').write_text(json.dumps(asdict(ref)), encoding='utf-8')
    path = tmp_path / 'config.json'
    path.write_text(json.dumps({'referencia': 'ref.json', 'seeds_base': [42, 123],
        'busca': {'max_avaliacoes': 3}, 'configuracoes': [
            {'metodo': 'ponderada', 'id': 'a', 'pesos': [1., 0., 0.]},
            {'metodo': 'epsilon', 'id': 'b', 'epsilons': [1., 1.]}]}), encoding='utf-8')
    return path


def solver_para(solucao):
    def solver(config, referencia, seed, limites, observar=None):
        from avaliacao import avaliar
        candidato = Candidato(solucao, avaliar(solucao, config, referencia))
        observar(candidato)
        return ResultadoBusca('viavel', candidato, candidato, [], 1, 0, 'max_iter', 0.)
    return solver


def test_campanha_revalida_retoma_e_preserva_proveniencia(modelo_pequeno, tmp_path):
    from experimentos import executar_campanha
    path = preparar(tmp_path)
    output = tmp_path / 'campanha'
    resultado = executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))
    assert resultado['concluidas'] == 4
    manifesto = json.loads((output / 'manifesto.json').read_text(encoding='utf-8'))
    assert all(e == 'concluido' for e in manifesto['estado_runs'].values())
    assert len(list((output / 'execucoes').glob('*.json'))) == 4
    assert (output / 'resumo.csv').exists()
    assert len(resultado['arquivos_pareto']) == 6
    arquivo = json.loads((output / resultado['arquivos_pareto'][0]).read_text(encoding='utf-8'))
    assert arquivo[0]['origens'][0]['indice_avaliacao'] == 1
    def proibido(*args, **kwargs):
        pytest.fail('Retomada repetiu run concluído')
    assert executar_campanha(path, output, solver=proibido)['reutilizadas'] == 4


def test_retomada_rejeita_config_alterada(modelo_pequeno, tmp_path):
    from experimentos import executar_campanha
    path = preparar(tmp_path)
    output = tmp_path / 'campanha'
    executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))
    path.write_text(path.read_text() + '\n')
    with pytest.raises(ValueError, match='manifesto'):
        executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))


def test_retomada_rejeita_avaliacao_observada_adulterada(modelo_pequeno, tmp_path):
    from experimentos import executar_campanha
    path = preparar(tmp_path)
    output = tmp_path / 'campanha'
    executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))
    registro = next((output / 'execucoes').glob('*.json'))
    dados = json.loads(registro.read_text(encoding='utf-8'))
    dados['observados'][0]['avaliacao']['normalizados'][0] += .1
    registro.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError):
        executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))


def test_interrupcao_preserva_runs_e_ignora_temporario(modelo_pequeno, tmp_path):
    from experimentos import executar_campanha
    path = preparar(tmp_path)
    output = tmp_path / 'campanha'
    contador = 0
    real = solver_para(modelo_pequeno[1])
    def interrompido(*args, **kwargs):
        nonlocal contador
        contador += 1
        if contador == 2:
            raise KeyboardInterrupt
        return real(*args, **kwargs)
    with pytest.raises(KeyboardInterrupt):
        executar_campanha(path, output, solver=interrompido)
    (output / 'execucoes' / 'incompleto.json.tmp').write_text('{')
    resumo = executar_campanha(path, output, solver=real)
    assert resumo['concluidas'] == 4 and resumo['reutilizadas'] == 1


def test_sem_viavel_registrado_e_arquivo_vazio(modelo_pequeno, tmp_path):
    from experimentos import executar_campanha
    path = preparar(tmp_path)
    def solver(config, referencia, seed, limites, observar):
        from avaliacao import avaliar
        ruim = Candidato(modelo_pequeno[0], avaliar(modelo_pequeno[0], config, referencia))
        observar(ruim)
        return ResultadoBusca('sem_viavel_encontrada', None, ruim, [], 1, 0, 'max_iter', 0.)
    output = tmp_path / 'campanha'
    resumo = executar_campanha(path, output, solver=solver)
    assert len(resumo['execucoes']) == 4
    assert all(r['f1'] is None for r in resumo['execucoes'])
    assert all(json.loads((output / p).read_text()) == [] for p in resumo['arquivos_pareto'])


def test_todos_viaveis_observados_entram_no_pareto(modelo_pequeno, tmp_path):
    from experimentos import executar_campanha
    path = preparar(tmp_path)
    def solver(config, referencia, seed, limites, observar):
        from avaliacao import avaliar
        bom = Candidato(modelo_pequeno[1], avaliar(modelo_pequeno[1], config, referencia))
        pior = Candidato(modelo_pequeno[2], avaliar(modelo_pequeno[2], config, referencia))
        observar(bom)
        observar(pior)
        return ResultadoBusca('viavel', pior, pior, [], 2, 0, 'max_iter', 0.)
    output = tmp_path / 'campanha'
    resumo = executar_campanha(path, output, solver=solver)
    for p in resumo['arquivos_pareto']:
        arquivo = json.loads((output / p).read_text(encoding='utf-8'))
        assert len(arquivo) == 1
        assert arquivo[0]['avaliacao']['objetivos'][0] == 40000


@pytest.mark.parametrize('campo', ['chave', 'escalar', 'epsilon_ok'])
def test_roundtrip_tp2_rejeita_derivados_adulterados(modelo_pequeno, tmp_path, campo):
    from avaliacao import avaliar
    from registros import salvar_resultado, ler_resultado
    from normalizacao import carregar_referencia
    path = preparar(tmp_path)
    ref = carregar_referencia(tmp_path / 'ref.json')
    config = ConfigEscalar('ponderada', 'a', pesos=(1., 0., 0.))
    candidato = Candidato(modelo_pequeno[1], avaliar(modelo_pequeno[1], config, ref))
    resultado = ResultadoBusca('viavel', candidato, candidato, [], 1, 0, 'max_iter', 0.)
    registro = tmp_path / 'r.json'
    salvar_resultado(resultado, {'config': asdict(config), 'referencia': asdict(ref)}, registro)
    dados = json.loads(registro.read_text(encoding='utf-8'))
    av = dados['resultado']['melhor_viavel']['avaliacao']
    if campo == 'chave':
        av[campo][-1][-1] += 1
    elif campo == 'escalar':
        av[campo] += .1
    else:
        av[campo] = False
    registro.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError):
        ler_resultado(registro)


@pytest.mark.parametrize('campo', ['seed', 'run_id', 'repeticao', 'indice_avaliacao', 'auditoria', 'avaliacoes'])
def test_retomada_rejeita_proveniencia_e_contadores_adulterados(modelo_pequeno, tmp_path, campo):
    from experimentos import executar_campanha
    path = preparar(tmp_path)
    output = tmp_path / 'campanha'
    executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))
    registro = next((output / 'execucoes').glob('*.json'))
    dados = json.loads(registro.read_text(encoding='utf-8'))
    if campo == 'auditoria':
        dados['observados'][0]['auditoria']['qualidade'][0]['excesso_bruto'] = 99
    elif campo == 'avaliacoes':
        dados['resultado']['avaliacoes'] = -1
    else:
        dados['observados'][0]['origens'][-1][campo] = 'adulterado'
    registro.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError):
        executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))


def test_retomada_rejeita_origem_adulterada_antes_da_ultima(modelo_pequeno, tmp_path):
    from experimentos import executar_campanha
    path = preparar(tmp_path)
    output = tmp_path / 'campanha'
    executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))
    registro = next((output / 'execucoes').glob('*.json'))
    dados = json.loads(registro.read_text(encoding='utf-8'))
    origens = dados['observados'][0]['origens']
    origens.insert(0, {**origens[0], 'seed': 'adulterada'})
    registro.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError, match='Proveniência'):
        executar_campanha(path, output, solver=solver_para(modelo_pequeno[1]))
