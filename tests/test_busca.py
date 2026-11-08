"""Regressões do núcleo: orçamento e observação nunca perdem uma viável."""
import copy
from dataclasses import asdict

import pytest

from contratos import ConfigBusca, ConfigEscalar, Referencia


def preparar(modelo_pequeno, monkeypatch):
    import busca
    inicial, b, c = modelo_pequeno
    monkeypatch.setattr(busca, 'gerar_solucao_inicial', lambda: inicial)
    return busca, inicial, b, c


@pytest.mark.parametrize('orcamento', [0, 1, 2, 7])
def test_orcamento_vale_dentro_de_todos_os_lacos(modelo_pequeno, monkeypatch, orcamento):
    busca, inicial, b, _ = preparar(modelo_pequeno, monkeypatch)
    monkeypatch.setattr(busca, 'GERADORES', [lambda s, rng: copy.deepcopy(b)] * 3)
    vistos = []
    r = busca.resolver(ConfigEscalar('mono', 'f1', objetivo=1), None, 42,
                      ConfigBusca(max_avaliacoes=orcamento), vistos.append)
    assert r.avaliacoes == orcamento == len(vistos)
    assert r.motivo_parada == 'max_avaliacoes'
    assert (r.melhor_viavel is not None) == (orcamento >= 2)
    if orcamento >= 2:
        assert r.melhor_viavel.solucao == b
    assert r.historico[-1]['avaliacoes'] == orcamento


def test_viavel_rejeitada_por_fitness_e_observada_no_ultimo_candidato(modelo_pequeno, monkeypatch):
    busca, inicial, b, _ = preparar(modelo_pequeno, monkeypatch)
    import avaliacao
    monkeypatch.setitem(avaliacao.PESOS_PENALIDADE, 'f1', 0.)
    monkeypatch.setattr(busca, 'GERADORES', [lambda s, rng: b] * 3)
    vistos = []
    r = busca.resolver(ConfigEscalar('mono', 'f1', objetivo=1), None, 2,
                      ConfigBusca(max_avaliacoes=2), vistos.append)
    assert r.melhor_busca.solucao == inicial
    assert r.melhor_viavel.solucao == b
    assert vistos[-1].solucao == b


def test_observador_nao_muta_incumbentes(modelo_pequeno, monkeypatch):
    busca, _, b, _ = preparar(modelo_pequeno, monkeypatch)
    monkeypatch.setattr(busca, 'GERADORES', [lambda s, rng: b] * 3)
    def observar(c):
        c.solucao[1][:] = ['A', 'A']
    r = busca.resolver(ConfigEscalar('mono', 'f1', objetivo=1), None, 1,
                      ConfigBusca(max_avaliacoes=2), observar)
    assert r.melhor_viavel.solucao == b


def test_sem_viavel_e_reprodutibilidade(modelo_pequeno, monkeypatch):
    busca, inicial, _, _ = preparar(modelo_pequeno, monkeypatch)
    monkeypatch.setattr(busca, 'GERADORES', [lambda s, rng: None] * 3)
    config = ConfigEscalar('mono', 'f1', objetivo=1)
    limites = ConfigBusca(max_iter=3, max_sem_melhora=2)
    r = busca.resolver(config, None, 91, limites)
    outro = busca.resolver(config, None, 91, limites)
    assert r.status == 'sem_viavel_encontrada'
    assert r.melhor_viavel is None
    assert r.motivo_parada == 'estagnacao'
    a, b = asdict(r), asdict(outro)
    a.pop('tempo_s'); b.pop('tempo_s')
    assert a == b


def test_estrutura_invalida_contada_sem_gastar_avaliacao(modelo_pequeno, monkeypatch):
    busca, _, _, _ = preparar(modelo_pequeno, monkeypatch)
    monkeypatch.setattr(busca, 'GERADORES', [lambda s, rng: {}] * 3)
    r = busca.resolver(ConfigEscalar('mono', 'f1', objetivo=1), None, 3,
                      ConfigBusca(max_iter=1, max_amostras=2))
    assert r.tentativas_invalidas > 0
    assert r.avaliacoes == 1


def test_vnd_mantem_vizinhanca_apos_limite(modelo_pequeno, monkeypatch):
    busca, _, _, _ = preparar(modelo_pequeno, monkeypatch)
    chamadas = []
    respostas = iter([True] * 5 + [False, True, False, False])
    def local(atual, indice, acompanhamento, rng):
        chamadas.append(indice + 1)
        return atual, next(respostas)
    monkeypatch.setattr(busca, '_busca_local', local)
    busca._vnd(None, type('A', (), {'limites': ConfigBusca()})(), None)
    assert chamadas == [1, 1, 1, 1, 1, 1, 2, 2, 3]


def test_interface_vns_expoe_nucleo_comum(modelo_pequeno, monkeypatch):
    busca, _, b, _ = preparar(modelo_pequeno, monkeypatch)
    import vns
    monkeypatch.setattr(busca, 'GERADORES', [lambda s, rng: b] * 3)
    r = vns.resolver(ConfigEscalar('mono', 'f1', objetivo=1), None, 7,
                     ConfigBusca(max_avaliacoes=2))
    assert r.melhor_viavel.solucao == b


@pytest.mark.parametrize('config', [
    ConfigEscalar('ponderada', 'p', pesos=(1., 0., 0.)),
    ConfigEscalar('epsilon', 'e', epsilons=(0., 0.)),
])
def test_tp2_prioriza_viabilidade_e_observa_antes_de_aceitar(modelo_pequeno, monkeypatch, config):
    busca, inicial, b, _ = preparar(modelo_pequeno, monkeypatch)
    monkeypatch.setattr(busca, 'GERADORES', [lambda s, rng: b] * 3)
    # Escala manual: qualidade ótima B tem g2=g3=0; A barato viola química.
    ref = Referencia((0., 0., 0.), (100000., 20., 20.), 'sintetica')
    vistos = []
    r = busca.resolver(config, ref, 2, ConfigBusca(max_iter=1, max_avaliacoes=6), vistos.append)
    assert not vistos[0].avaliacao.viavel
    assert r.melhor_viavel.solucao == b
    assert r.melhor_viavel.avaliacao.viavel
    assert any(c.solucao == r.melhor_viavel.solucao for c in vistos)
    assert r.avaliacoes <= 6
