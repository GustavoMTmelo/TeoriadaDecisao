import pytest
import escalarizacoes as e
from contratos import ConfigEscalar, Referencia
from avaliacao import avaliar


def test_epsilon_dois_limites_e_cenarios_didaticos():
    assert hasattr(e, 'restricoes_epsilon'), 'restrições epsilon ausentes'
    pontos = [(.2, .8, .2), (.5, .2, .8), (.6, .4, .4)]
    assert [e.restricoes_epsilon(g, (.8, .8))[0] for g in pontos] == [True]*3
    assert [e.restricoes_epsilon(g, (.4, .4))[0] for g in pontos] == [False, False, True]
    assert not any(e.restricoes_epsilon(g, (.2, .2))[0] for g in pontos)
    assert e.restricoes_epsilon((0, .4+5e-10, .4), (.4, .4)) == (True, 0.)
    ok, excesso = e.restricoes_epsilon((0, .5, .6), (.4, .4))
    assert not ok and excesso == pytest.approx(.3-2e-9)


def test_malha_epsilon_cartesiana():
    assert hasattr(e, 'configuracoes_epsilon'), 'malha epsilon ausente'
    configs = e.configuracoes_epsilon()
    assert len(configs) == len({c.id for c in configs}) == len({c.epsilons for c in configs}) == 16
    assert (1/3, 1.) in {c.epsilons for c in configs}


@pytest.mark.parametrize('eps', [(0,), (float('nan'), 0), (float('inf'), 0), (-.1, .4)])
def test_rejeita_epsilon_invalido(eps):
    assert hasattr(e, 'restricoes_epsilon'), 'restrições epsilon ausentes'
    with pytest.raises(ValueError):
        e.restricoes_epsilon((0, 0, 0), eps)


def test_qualidade_fisica_preservada_e_desempate_custo(modelo_pequeno):
    invalida, viavel, cara = modelo_pequeno
    ref = Referencia((0, 0, 0), (100000, 100, 100), 'teste')
    config = ConfigEscalar('epsilon', 'eps', epsilons=(1, 1))
    boa, ruim, cara = [avaliar(x, config, ref) for x in (viavel, invalida, cara)]
    assert ruim.epsilon_ok and not ruim.viavel
    assert boa.chave < ruim.chave and boa.chave < cara.chave
    assert boa.escalar == .4 and boa.chave == (0, 0., .4, (0., 0., 0.))


def test_epsilon_violado_mesmo_com_qualidade_valida(modelo_pequeno):
    _, viavel, _ = modelo_pequeno
    ref = Referencia((0, -1, -1), (100000, 1, 1), 'teste')
    av = avaliar(viavel, ConfigEscalar('epsilon', 'eps', epsilons=(.2, .2)), ref)
    assert av.qualidade_ok and not av.epsilon_ok and not av.viavel
    assert av.violacao == pytest.approx(.6-2e-9)


def test_auditoria_excessos_sem_tolerancia(modelo_pequeno):
    import avaliacao as a
    assert hasattr(a, 'detalhar_excessos'), 'auditoria de excessos ausente'
    dados = a.detalhar_excessos(modelo_pequeno[0], (0, .5, .6), (.4, .4))
    assert dados['qualidade'][0]['excesso_bruto'] == 2.
    assert dados['qualidade'][0]['excesso_relativo'] == pytest.approx(2.-1e-9)
    assert dados['epsilon'][0]['excesso_bruto'] == pytest.approx(.1)
    assert dados['epsilon'][1]['excesso_bruto'] == pytest.approx(.2)


def test_tolerancia_qualidade_limite_exato_tem_violacao_zero(modelo_pequeno, monkeypatch):
    import sol_inicial
    ref = Referencia((0, 0, 0), (100000, 100, 100), 'teste')
    monkeypatch.setitem(sol_inicial.minerios['B'], 'sio2', 6.+1e-9)
    av = avaliar(modelo_pequeno[1], ConfigEscalar('epsilon', 'eps', epsilons=(1, 1)), ref)
    assert av.qualidade_ok and av.violacao == 0.
