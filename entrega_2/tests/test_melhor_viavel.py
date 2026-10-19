import copy

import pytest

from contratos import ConfigBusca
import vns


def test_viavel_rejeitada_por_fitness_e_preservada(modelo_pequeno, monkeypatch):
    inicial, b, c = modelo_pequeno
    monkeypatch.setitem(vns.LAMBDA, 'f1', 0.)
    candidatos = iter([c, b, None])
    monkeypatch.setattr(vns, '_GERADORES_VND', [lambda sol, rng: next(candidatos, None)])
    monkeypatch.setattr(vns, '_GERADORES_SHAKE', [lambda sol, rng: None])
    vistos = []
    resultado = vns.gvns('f1', 42, max_iter=1, observar=vistos.append)
    assert resultado.status == 'viavel'
    assert resultado.melhor_viavel.solucao == b
    assert resultado.melhor_viavel.avaliacao.escalar == 40000
    assert resultado.melhor_busca.solucao == inicial  # trajetória penalizada não aceitou B/C
    assert any(x.solucao == c for x in vistos)
    assert any(x.solucao == b for x in vistos)


def test_viavel_intermediaria_do_shake_guardada(modelo_pequeno, monkeypatch):
    inicial, b, _ = modelo_pequeno
    monkeypatch.setattr(vns, '_GERADORES_SHAKE', [lambda sol, rng: copy.deepcopy(b)])
    monkeypatch.setattr(vns, '_GERADORES_VND', [lambda sol, rng: None])
    resultado = vns.gvns('f1', 42, max_iter=1)
    assert resultado.melhor_viavel.solucao == b
    b[1][0] = 'A'
    assert resultado.melhor_viavel.solucao == {1: ['B', 'B']}


@pytest.mark.parametrize('limites', [ConfigBusca(max_iter=0),
                                  ConfigBusca(max_avaliacoes=0)])
def test_sem_viavel_nao_retorna_inicial_como_sucesso(modelo_pequeno, limites):
    resultado = vns.gvns('f1', 42, limites=limites)
    assert resultado.status == 'sem_viavel_encontrada'
    assert resultado.melhor_viavel is None
    if limites.max_avaliacoes == 0:
        assert resultado.avaliacoes == 0


def test_ultima_avaliacao_viavel_preservada_no_limite(modelo_pequeno, monkeypatch):
    _, b, _ = modelo_pequeno
    monkeypatch.setattr(vns, '_GERADORES_SHAKE', [lambda sol, rng: b])
    resultado = vns.gvns('f1', 42, limites=ConfigBusca(max_avaliacoes=2))
    assert resultado.melhor_viavel.solucao == b
    assert resultado.avaliacoes == 2
    assert resultado.motivo_parada == 'max_avaliacoes'


def test_observador_nao_pode_mutar_melhor_viavel(modelo_pequeno, monkeypatch):
    _, b, _ = modelo_pequeno
    monkeypatch.setattr(vns, '_GERADORES_SHAKE', [lambda sol, rng: b])
    def observar(candidato):
        candidato.solucao[1][:] = ['A', 'A']
    resultado = vns.gvns('f1', 42, limites=ConfigBusca(max_avaliacoes=2), observar=observar)
    assert resultado.melhor_viavel.solucao == b


def test_objetivo_desconhecido_rejeitado():
    with pytest.raises(ValueError):
        vns.gvns('f4', 42, max_iter=0)
