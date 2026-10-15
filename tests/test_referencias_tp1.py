from dataclasses import asdict

import pytest

from contratos import Avaliacao, Candidato, ConfigBusca, ConfigEscalar, ResultadoBusca
from avaliacao import avaliar


def candidato(vetor, run_id):
    return Candidato({1: ['M1']}, Avaliacao(vetor, None, True, True, True, 0., vetor[0],
                                         (vetor[0],), ()), [{'run_id': run_id}])


def test_referencia_min_max_colunas_e_origem():
    from normalizacao import construir_referencia
    r = construir_referencia([candidato((100, 1, 5), 'a'), candidato((200, 4, 2), 'b'),
                              candidato((150, 3, 3), 'c')])
    assert r.minimo == (100, 1, 2)
    assert r.maximo == (200, 4, 5)
    assert r.origens['f1']['minimo'] == ['a']
    assert r.origens['f3']['minimo'] == ['b']
    assert r.origens['f2']['maximo'] == ['b']
    assert len(r.id) == 64


def test_referencia_independe_da_ordem_e_identifica_empates():
    from normalizacao import construir_referencia
    pontos = [candidato((100, 1, 5), 'a'), candidato((200, 4, 2), 'b'),
              candidato((100, 3, 4), 'c')]
    a = construir_referencia(pontos)
    b = construir_referencia(list(reversed(pontos)))
    assert a == b
    assert a.origens['f1']['minimo'] == ['a', 'c']


def test_referencia_recusa_amostra_vazia_ou_degenerada():
    from normalizacao import construir_referencia
    for pontos in ([], [candidato((100, 1, 5), 'a')]):
        with pytest.raises(ValueError):
            construir_referencia(pontos)


@pytest.fixture
def campanha_pequena(modelo_pequeno, monkeypatch, tmp_path):
    from registros import salvar_resultado, escrever_json
    from reproduzir_tp1 import criar_manifesto
    import sol_inicial
    monkeypatch.setitem(sol_inicial.minerios['B'], 'sio2', 5.4)
    monkeypatch.setitem(sol_inicial.minerios['B'], 'al2o3', 1.6)
    monkeypatch.setitem(sol_inicial.minerios['C'], 'sio2', 5.7)
    monkeypatch.setitem(sol_inicial.minerios['C'], 'al2o3', 1.8)
    from vns import SEMENTES
    manifest = criar_manifesto(ConfigBusca())
    escrever_json(tmp_path/'manifesto.json', manifest)
    solucoes = [{1: ['B', 'B']}, {1: ['C', 'C']}, {1: ['B', 'C']}]
    for obj in ('f1', 'f2', 'f3'):
        for i, seed in enumerate(SEMENTES, 1):
            run_id = f'{obj}_{i:02}_seed{seed}'
            sol = solucoes[(i-1) % 3]
            av = avaliar(sol, ConfigEscalar('mono', obj, objetivo=int(obj[1])))
            cand = Candidato(sol, av, [{'run_id': run_id}])
            r = ResultadoBusca('viavel', cand, cand, [], 1, 0, 'max_iter', .1)
            salvar_resultado(r, dict(objetivo=obj, seed=seed, repeticao=i, run_id=run_id,
                                    configuracao_busca=asdict(ConfigBusca()),
                                    **{'lambda': manifest['lambdas'][obj]}),
                             tmp_path/'execucoes'/f'{run_id}.json')
    return tmp_path


def test_campanha_recalcula_15_vetores_matriz_e_referencias(campanha_pequena):
    from reproduzir_tp1 import consolidar
    import json
    d = campanha_pequena
    resumo = consolidar(d, gerar_figuras=False)
    assert resumo['n_execucoes'] == 15 and resumo['n_viaveis'] == 15
    assert (d/'objetivos_cruzados.csv').is_file()
    assert (d/'matriz_payoff.csv').is_file()
    assert len(json.loads((d/'referencias_tp1.json').read_text(encoding='utf-8'))['fontes']) == 15


def test_campanha_incompleta_nao_congela_referencia(campanha_pequena):
    from reproduzir_tp1 import consolidar
    p = next((campanha_pequena/'execucoes').glob('*.json'))
    p.unlink()
    with pytest.raises(ValueError, match='15'):
        consolidar(campanha_pequena, gerar_figuras=False)
    assert not (campanha_pequena/'referencias_tp1.json').exists()


def test_campanha_nao_aceita_configuracao_alterada(campanha_pequena):
    from reproduzir_tp1 import consolidar
    import json
    p = next((campanha_pequena/'execucoes').glob('*.json'))
    dados = json.loads(p.read_text(encoding='utf-8'))
    dados['metadados']['configuracao_busca']['max_iter'] = 1
    p.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError, match='configuração'):
        consolidar(campanha_pequena, gerar_figuras=False)


@pytest.mark.parametrize('arquivo', ['resumo.csv', 'objetivos_cruzados.csv',
                                    'matriz_payoff.csv', 'estatisticas_f1.json'])
def test_verificador_rejeita_saida_ausente_ou_adulterada(campanha_pequena, arquivo):
    from reproduzir_tp1 import consolidar, verificar_artefatos
    consolidar(campanha_pequena, gerar_figuras=False)
    p = campanha_pequena/arquivo
    p.write_text('adulterado', encoding='utf-8')
    with pytest.raises(ValueError, match='Artefato ausente ou alterado'):
        verificar_artefatos(campanha_pequena)


def test_verificador_rejeita_figura_removida(campanha_pequena):
    from reproduzir_tp1 import consolidar, verificar_artefatos
    consolidar(campanha_pequena)
    (campanha_pequena/'convergencia_f1.png').unlink()
    with pytest.raises(ValueError, match='Artefato ausente ou alterado'):
        verificar_artefatos(campanha_pequena)


def test_verificador_aceita_campanha_integra(campanha_pequena):
    from reproduzir_tp1 import consolidar, verificar_artefatos
    consolidar(campanha_pequena, gerar_figuras=False)
    resultado = verificar_artefatos(campanha_pequena)
    assert resultado['n_viaveis'] == 15
    assert resultado['codigo_atual_confere']
    assert resultado['artefatos_verificados'] == 8


def test_hash_de_codigo_independe_de_final_de_linha(tmp_path):
    from reproduzir_tp1 import sha256_codigo
    p = tmp_path/'fonte.py'
    p.write_bytes(b'x = 1\r\n')
    a = sha256_codigo(p)
    p.write_bytes(b'x = 1\n')
    assert sha256_codigo(p) == a
