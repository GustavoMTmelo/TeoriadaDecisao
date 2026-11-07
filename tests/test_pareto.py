"""Arquivo não dominado: comparação 3D e identidade física independente da ordem."""

from copy import deepcopy
from itertools import permutations

import pytest

from contratos import Avaliacao, Candidato
from pareto import atualizar_arquivo, chave_solucao, consolidar_arquivo, domina


def candidato(vetor=(1, 2, 3), solucao=None, origens=None, **flags):
    avaliacao = Avaliacao(vetor, None, flags.get('estrutura_ok', True),
                         flags.get('qualidade_ok', True),
                         flags.get('epsilon_ok', True), 0, 1, (1,), ())
    return Candidato(solucao or {1: ['A', 'B']}, avaliacao, origens or [])


def test_dominancia_exige_tres_objetivos_e_melhoria_estrita():
    assert domina((1, 2, 3), (2, 3, 4))
    assert not domina((1, 2, 3), (0, 4, 2))
    assert not domina((1, 2, 3), (2, 3, 1))
    assert not domina((1, 2, 3), (1, 2, 3))
    assert domina((1, 2, 3), (1, 2, 3.000000000000001))


@pytest.mark.parametrize('vetor', [None, (), (1, 2), (1, 2, 3, 4),
                                  (1, float('nan'), 3), (1, 2, float('inf')),
                                  (float('-inf'), 2, 3), ('1', 2, 3)])
def test_rejeita_vetores_invalidos_em_ambos_os_argumentos(vetor):
    with pytest.raises(ValueError):
        domina(vetor, (1, 2, 3))
    with pytest.raises(ValueError):
        domina((1, 2, 3), vetor)


def test_chave_ordena_pilhas_e_minerios_preservando_multiplicidade():
    assert chave_solucao({2: ['C'], 1: ['B', 'A', 'A']}) == (
        (1, ('A', 'A', 'B')), (2, ('C',)))
    assert chave_solucao({1: ['A', 'B']}) != chave_solucao({1: ['A', 'A', 'B']})


def test_dominador_remove_dominados_sem_filtrar_em_duas_dimensoes():
    arquivo = [candidato((2, 3, 4), {1: ['B']}),
               candidato((2, 3, 1), {1: ['C']})]
    novo = atualizar_arquivo(arquivo, candidato())
    assert {c.avaliacao.objetivos for c in novo} == {(1, 2, 3), (2, 3, 1)}
    assert len(arquivo) == 2
    assert len(atualizar_arquivo(novo, candidato((9, 9, 9)))) == 2


def test_duplicata_fisica_agrega_origens_sem_aliases_ou_repeticoes():
    a = candidato(origens=[{'seed': 42, 'config': {'pesos': [1, 0, 0]}}])
    b = candidato(solucao={1: ['B', 'A']}, origens=[{'seed': 123}, {'seed': 42,
                         'config': {'pesos': [1, 0, 0]}}])
    arquivo = [a]
    novo = atualizar_arquivo(arquivo, b)
    assert len(novo) == 1
    assert novo[0].origens == [a.origens[0], {'seed': 123}]
    novo[0].origens[0]['config']['pesos'][0] = 99
    novo[0].solucao[1].append('C')
    assert a.origens[0]['config']['pesos'] == [1, 0, 0]
    assert b.origens[1]['config']['pesos'] == [1, 0, 0]
    assert a.solucao == {1: ['A', 'B']}
    assert b.solucao == {1: ['B', 'A']}


def test_vetores_iguais_nao_deduplicam_composicoes_distintas():
    novo = atualizar_arquivo([candidato()], candidato(solucao={1: ['C']}))
    assert len(novo) == 2


@pytest.mark.parametrize('flag', ['estrutura_ok', 'qualidade_ok', 'epsilon_ok'])
def test_arquivo_rejeita_inviaveis_inclusive_epsilon(flag):
    with pytest.raises(ValueError):
        atualizar_arquivo([], candidato(**{flag: False}))


def test_arquivo_rejeita_objetivos_nao_finitos_mesmo_quando_vazio():
    with pytest.raises(ValueError):
        atualizar_arquivo([], candidato((1, 2, float('nan'))))


def test_insercao_em_qualquer_ordem_preserva_conjunto_e_proveniencia():
    pontos = [candidato((2, 3, 4), {1: ['C']}),
              candidato(origens=[{'seed': 42}]),
              candidato(solucao={1: ['B', 'A']}, origens=[{'seed': 123}]),
              candidato((2, 3, 1), {1: ['D']})]
    for ordem in permutations(pontos):
        arquivo = consolidar_arquivo(ordem)
        assert {chave_solucao(c.solucao) for c in arquivo} == {
            ((1, ('A', 'B')),), ((1, ('D',)),)}
        ab = next(c for c in arquivo if c.avaliacao.objetivos == (1, 2, 3))
        assert {o['seed'] for o in ab.origens} == {42, 123}


def test_consolidacao_filtra_origens_antes_da_dominancia():
    pontos = [candidato(origens=[{'metodo': 'ponderada', 'repeticao': 1},
                                {'metodo': 'epsilon', 'repeticao': 2}]),
              candidato((2, 3, 4), {1: ['C']},
                        [{'metodo': 'ponderada', 'repeticao': 2}])]
    copia = deepcopy(pontos)
    assert consolidar_arquivo([]) == []
    assert len(consolidar_arquivo(pontos)) == 1
    selecionados = consolidar_arquivo(pontos, metodo='ponderada', repeticao=2)
    assert len(selecionados) == 1
    assert selecionados[0].solucao == {1: ['C']}
    selecionados = consolidar_arquivo(pontos, metodo='epsilon')
    assert selecionados[0].origens == [{'metodo': 'epsilon', 'repeticao': 2}]
    assert pontos == copia
