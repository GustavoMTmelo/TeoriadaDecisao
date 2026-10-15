from copy import deepcopy

import pytest

from contratos import ConfigEscalar
from sol_inicial import gerar_solucao_inicial, validar_estrutura, minerios


def test_pilha_ausente_rejeitada():
    sol = gerar_solucao_inicial()
    del sol[2]
    assert not validar_estrutura(sol)[0]


@pytest.mark.parametrize('modificar', [
    lambda s: s.update({11: ['M1']}),
    lambda s: s[1].__setitem__(0, 'M999'),
    lambda s: s[1].__setitem__(0, []),
    lambda s: s.update({1: None}),
    lambda s: s[1].pop(),
    lambda s: s[1].__setitem__(0, 'M20'),
])
def test_entrada_invalida_diagnosticada_sem_excecao(modificar):
    sol = gerar_solucao_inicial()
    modificar(sol)
    ok, erros = validar_estrutura(sol)
    assert not ok and erros


def test_avaliacao_invalida_nao_calcula_objetivos():
    from avaliacao import avaliar
    sol = gerar_solucao_inicial()
    del sol[2]
    av = avaliar(sol, ConfigEscalar('mono', 'f1', objetivo=1))
    assert not av.estrutura_ok
    assert av.objetivos is None and av.escalar is None


def test_construtiva_preserva_valores_e_avaliacao_nao_muta():
    from avaliacao import avaliar
    sol = gerar_solucao_inicial()
    original = deepcopy(sol)
    av = avaliar(sol, ConfigEscalar('mono', 'f1', objetivo=1))
    assert sol == original
    assert av.estrutura_ok and not av.qualidade_ok
    assert av.objetivos == pytest.approx((60400000, 23.48105481043885, 14.909887547238732))
    assert len(av.erros) == 12
    assert av.violacao > 0


def test_disponibilidade_maxima_rejeitada():
    sol = gerar_solucao_inicial()
    sol[1] = ['M1'] * 10
    ok, erros = validar_estrutura(sol)
    assert not ok
    assert any('máximo' in e for e in erros)


def test_disponibilidade_minima_rejeitada():
    sol = gerar_solucao_inicial()
    for composicao in sol.values():
        composicao[:] = ['M1' if m == 'M4' else m for m in composicao]
    ok, erros = validar_estrutura(sol)
    assert not ok
    assert any('M4' in e and 'mínimo' in e for e in erros)


def test_objetivos_com_calculo_manual(monkeypatch):
    from avaliacao import avaliar
    sol = gerar_solucao_inicial()
    # Mesmos teores em todos os caminhões: 10 desvios conhecidos e custo 145*2000*200.
    for dados in minerios.values():
        monkeypatch.setitem(dados, 'sio2', 5.5)
        monkeypatch.setitem(dados, 'al2o3', 1.5)
        monkeypatch.setitem(dados, 'custo', 200)
    av = avaliar(sol, ConfigEscalar('mono', 'f2', objetivo=2))
    assert av.viavel
    assert av.objetivos == pytest.approx((58000000, .0125, .3125))
