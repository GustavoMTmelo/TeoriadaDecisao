import importlib.util
import pytest


def modulo():
    assert importlib.util.find_spec('escalarizacoes'), 'escalarizações ausentes'
    import escalarizacoes
    return escalarizacoes


def test_soma_ponderada_e_malha():
    e = modulo()
    assert e.valor_ponderado((.2, .4, .6), (.5, .25, .25)) == pytest.approx(.35)
    configs = e.configuracoes_ponderadas()
    assert len(configs) == len({c.id for c in configs}) == len({c.pesos for c in configs}) == 16
    pesos = {c.pesos for c in configs}
    assert {(1, 0, 0), (0, 1, 0), (0, 0, 1), (1/3, 1/3, 1/3)} <= pesos
    assert all(min(c.pesos) >= 0 and sum(c.pesos) == pytest.approx(1) for c in configs)
    assert [c.id for c in configs] == [c.id for c in e.configuracoes_ponderadas()]


@pytest.mark.parametrize('pesos', [(-1, 1, 1), (0, 0, 0), (.2, .4, .5),
                                   (float('nan'), 0, 1), (1, 0), (float('inf'), 0, 0)])
def test_pesos_invalidos_rejeitados(pesos):
    e = modulo()
    with pytest.raises(ValueError):
        e.valor_ponderado((.2, .4, .6), pesos)


def test_validacao_de_configuracao_na_avaliacao(modelo_pequeno):
    from avaliacao import avaliar
    from contratos import ConfigEscalar, Referencia
    _, viavel, _ = modelo_pequeno
    with pytest.raises(ValueError):
        avaliar(viavel, ConfigEscalar('ponderada', 'ruim', pesos=(0, 0, 0)),
                Referencia((0, 0, 0), (100, 100, 100), 'teste'))


def test_tp2_prefere_viavel_e_calcula_violacao_normalizada(modelo_pequeno):
    from avaliacao import avaliar
    from contratos import ConfigEscalar, Referencia
    invalida, viavel, _ = modelo_pequeno
    config = ConfigEscalar('ponderada', 'custo', pesos=(1, 0, 0))
    ref = Referencia((0, 0, 0), (100000, 100, 100), 'teste')
    boa, ruim = avaliar(viavel, config, ref), avaliar(invalida, config, ref)
    assert boa.chave < ruim.chave
    assert boa.violacao == 0 and boa.normalizados[0] == pytest.approx(.4)
    assert ruim.violacao == pytest.approx((2-1e-9)**2)
    assert boa.chave == (0, 0, .4, (.4, .4, 0., 0.))
