import copy
import random
from collections import Counter

import pytest

from sol_inicial import (
    contar_uso_minerios,
    eh_compativel,
    gerar_solucao_inicial,
    minerios,
    pilhas,
)
from vizinhancas import gerar_vizinho_n1, gerar_vizinho_n2, gerar_vizinho_n3


def localizar_alteracoes(solucao, nova_solucao):
    alteracoes = []
    for p in solucao:
        for idx, minerio_atual in enumerate(solucao[p]):
            minerio_novo = nova_solucao[p][idx]
            if minerio_atual != minerio_novo:
                alteracoes.append((p, idx, minerio_atual, minerio_novo))
    return alteracoes


def test_n1_substituicao_preserva_pilha_e_altera_uma_posicao():
    solucao = gerar_solucao_inicial()
    original = copy.deepcopy(solucao)
    rng = random.Random(11)

    vizinho = gerar_vizinho_n1(solucao, rng)

    assert vizinho is not None
    assert solucao == original

    mudancas = localizar_alteracoes(solucao, vizinho)
    assert len(mudancas) == 1

    pilha, indice, antigo, novo = mudancas[0]
    assert len(vizinho[pilha]) == len(solucao[pilha])
    assert eh_compativel(novo, pilhas[pilha]["sinter"])
    assert novo != antigo


def test_n2_troca_entre_pilhas_preserva_massa_e_disponibilidade_global():
    solucao = gerar_solucao_inicial()
    original = copy.deepcopy(solucao)
    rng = random.Random(23)

    vizinho = gerar_vizinho_n2(solucao, rng)

    assert vizinho is not None
    assert solucao == original

    mudancas = localizar_alteracoes(solucao, vizinho)
    assert len(mudancas) == 2

    p1, i1, velho_1, novo_1 = mudancas[0]
    p2, i2, velho_2, novo_2 = mudancas[1]

    assert p1 != p2
    assert len(vizinho[p1]) == len(solucao[p1])
    assert len(vizinho[p2]) == len(solucao[p2])
    assert novo_1 == velho_2
    assert novo_2 == velho_1
    assert eh_compativel(novo_1, pilhas[p1]["sinter"])
    assert eh_compativel(novo_2, pilhas[p2]["sinter"])
    assert Counter(contar_uso_minerios(vizinho)) == Counter(contar_uso_minerios(solucao))


def test_n3_duas_posicoes_alteradas_com_compativel_e_distinto_de_troca_interna():
    solucao = gerar_solucao_inicial()
    original = copy.deepcopy(solucao)
    rng = random.Random(31)

    vizinho = gerar_vizinho_n3(solucao, rng)

    assert vizinho is not None
    assert solucao == original

    alteradas = []
    for pilha in solucao:
        for indice, minerio_atual in enumerate(solucao[pilha]):
            minerio_novo = vizinho[pilha][indice]
            if minerio_atual != minerio_novo:
                alteradas.append((pilha, indice, minerio_atual, minerio_novo))

    assert len(alteradas) == 2
    pilha_1, _, _, _ = alteradas[0]
    pilha_2, _, _, _ = alteradas[1]
    assert pilha_1 == pilha_2

    for _, _, antigo, novo in alteradas:
        assert novo != antigo
        assert eh_compativel(novo, pilhas[pilha_1]["sinter"])

    composicao_original = solucao[pilha_1]
    composicao_nova = vizinho[pilha_1]
    assert Counter(composicao_nova) != Counter(composicao_original)


def test_gerar_vizinhos_retorna_estrutura_consistente():
    solucao = gerar_solucao_inicial()
    original = copy.deepcopy(solucao)

    v1 = gerar_vizinho_n1(solucao)
    v2 = gerar_vizinho_n2(solucao)
    v3 = gerar_vizinho_n3(solucao)

    for vizinho in (v1, v2, v3):
        assert isinstance(vizinho, dict)
        assert set(vizinho) == set(solucao)
        for pilha in solucao:
            assert isinstance(vizinho[pilha], list)
            assert len(vizinho[pilha]) == len(solucao[pilha])

    assert solucao == original


def test_movimentos_impossiveis_retorna_none():
    solucao = {1: ["M1", "M1"], 2: ["M1", "M1"]}

    # Salva a compatibilidade original para restaurar após o teste.
    compatibilidade_original = {
        minerio: (dados["s1"], dados["s2"])
        for minerio, dados in minerios.items()
    }

    try:
        # Força ausência de qualquer minério compatível.
        for minerio in minerios:
            minerios[minerio]["s1"] = False
            minerios[minerio]["s2"] = False

        assert gerar_vizinho_n1(solucao) is None
        assert gerar_vizinho_n2(solucao) is None
        assert gerar_vizinho_n3(solucao) is None

    finally:
        # Restaura exatamente os valores originais.
        for minerio, (s1, s2) in compatibilidade_original.items():
            minerios[minerio]["s1"] = s1
            minerios[minerio]["s2"] = s2


def test_reproducibilidade_com_mesma_semente():
    solucao = gerar_solucao_inicial()

    rng1 = random.Random(999)
    v1 = gerar_vizinho_n1(solucao, rng1)
    rng2 = random.Random(999)
    v2 = gerar_vizinho_n1(solucao, rng2)

    assert v1 == v2

    rng3 = random.Random(888)
    v3 = gerar_vizinho_n2(solucao, rng3)
    rng4 = random.Random(888)
    v4 = gerar_vizinho_n2(solucao, rng4)

    assert v3 == v4

    rng5 = random.Random(777)
    v5 = gerar_vizinho_n3(solucao, rng5)
    rng6 = random.Random(777)
    v6 = gerar_vizinho_n3(solucao, rng6)

    assert v5 == v6
