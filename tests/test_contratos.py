import pytest

from contratos import Avaliacao, Candidato, ConfigBusca, ConfigEscalar, ResultadoBusca


@pytest.mark.parametrize('campo', ['max_iter', 'max_sem_melhora', 'k_max',
                                 'max_amostras', 'max_restarts', 'max_avaliacoes'])
def test_orcamento_negativo_rejeitado(campo):
    with pytest.raises(ValueError):
        ConfigBusca(**{campo: -1})


def test_candidato_copia_composicao_e_origens():
    solucao = {1: ['M1']}
    origens = [{'seed': 42}]
    candidato = Candidato(solucao, Avaliacao((1, 2, 3), None, True, True,
                                            True, 0, 1, (1,), ()), origens)
    solucao[1].append('M2')
    origens[0]['seed'] = 99
    assert candidato.solucao == {1: ['M1']}
    assert candidato.origens == [{'seed': 42}]


def test_falha_nao_pode_ser_rotulada_como_sucesso():
    with pytest.raises(ValueError):
        ResultadoBusca('viavel', None, None, [], 0, 0, 'max_iter', 0)


def test_config_mono_rejeita_objetivo_desconhecido():
    with pytest.raises(ValueError):
        ConfigEscalar('mono', 'f4', objetivo=4)
