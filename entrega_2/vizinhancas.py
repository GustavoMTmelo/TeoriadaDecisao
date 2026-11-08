"""Estruturas de vizinhança para a solução do problema de composição de pilhas.

O módulo define três movimentos básicos usados por VNS/GVNS:

- N1: substituição de um caminhão em uma pilha por outro minério compatível;
- N2: troca de caminhões entre duas pilhas;
- N3: substituição simultânea de dois caminhões de uma mesma pilha.

As funções geram um vizinho novo a partir de uma solução existente, sem
modificar a solução original. Em alguns casos não existe um movimento válido
para a vizinhança; nesses cenários, a função retorna None.

Observação importante: as vizinhanças podem gerar soluções inviáveis do ponto
de vista de disponibilidade mínima/máxima ou qualidade. Essa decisão fica a
cargo da busca local, que pode validá-las com as funções já presentes em
sol_inicial.py.
"""

import copy
import random
from collections import Counter

from sol_inicial import eh_compativel, minerios, pilhas


__all__ = [
    "gerar_vizinho_n1",
    "gerar_vizinho_n2",
    "gerar_vizinho_n3",
]


def _normalizar_rng(rng=None):
    """Converte semente em gerador aleatório e mantém o objeto quando fornecido."""

    if rng is None:
        return random

    if isinstance(rng, int):
        return random.Random(rng)

    return rng


def _gerar_vizinho_n1_candidatos(solucao):
    """Lista todos os movimentos N1 possíveis para uma solução."""

    candidatos = []

    for pilha, composicao in solucao.items():
        sinter = pilhas[pilha]["sinter"]

        for indice, minerio_atual in enumerate(composicao):
            for novo_minerio in minerios:
                if (
                    novo_minerio != minerio_atual
                    and eh_compativel(novo_minerio, sinter)
                ):
                    candidatos.append((pilha, indice, novo_minerio))

    return candidatos


def _gerar_vizinho_n2_candidatos(solucao):
    """Lista todos os swaps válidos entre duas pilhas distintas."""

    candidatos = []
    chaves = list(solucao.keys())

    for idx_p1, p1 in enumerate(chaves):
        for p2 in chaves[idx_p1 + 1 :]:
            sinter_p1 = pilhas[p1]["sinter"]
            sinter_p2 = pilhas[p2]["sinter"]

            for i, minerio_p1 in enumerate(solucao[p1]):
                for j, minerio_p2 in enumerate(solucao[p2]):
                    if minerio_p1 == minerio_p2:
                        continue

                    if (
                        eh_compativel(minerio_p2, sinter_p1)
                        and eh_compativel(minerio_p1, sinter_p2)
                    ):
                        candidatos.append((p1, p2, i, j))

    return candidatos


def _gerar_vizinho_n3_candidatos(solucao):
    """Lista todos os movimentos N3 válidos em uma mesma pilha.

    Um movimento N3 seleciona duas posições de uma mesma pilha e altera ambas
    simultaneamente. Para evitar que o movimento seja equivalente a um simples
    N1 ou a uma troca interna sem alteração da composição física, exigimos:

    - duas posições distintas;
    - ambos os minérios trocados devem mudar;
    - a composição da pilha após o movimento deve diferir da original;
    - não pode ser apenas uma permutação interna do mesmo conjunto de minérios.
    """

    candidatos = []

    for pilha, composicao in solucao.items():
        sinter = pilhas[pilha]["sinter"]
        minerais_compativeis = [
            m for m in minerios if eh_compativel(m, sinter)
        ]

        for i in range(len(composicao)):
            for j in range(i + 1, len(composicao)):
                atual_i = composicao[i]
                atual_j = composicao[j]

                for novo_i in minerais_compativeis:
                    for novo_j in minerais_compativeis:
                        if novo_i == atual_i and novo_j == atual_j:
                            continue

                        nova_composicao = composicao.copy()
                        nova_composicao[i] = novo_i
                        nova_composicao[j] = novo_j

                        if Counter(nova_composicao) == Counter(composicao):
                            continue

                        if novo_i == atual_i or novo_j == atual_j:
                            continue

                        candidatos.append((pilha, i, j, novo_i, novo_j))

    return candidatos


def gerar_vizinho_n1(solucao, rng=None):
    """Gera um vizinho N1 por substituição de um caminhão.

    O movimento escolhe aleatoriamente uma pilha, uma posição da composição e
    um minério diferente, compatível com o Sinter da pilha. Como a estrutura
    global de disponibilidade é alterada, a solução resultante pode ser
    estruturalmente inviável ou violar limites de qualidade; essa avaliação
    fica para a fase de busca local.
    """

    gerador = _normalizar_rng(rng)
    movimentos = _gerar_vizinho_n1_candidatos(solucao)

    if not movimentos:
        return None

    pilha, indice, novo_minerio = gerador.choice(movimentos)
    nova_solucao = copy.deepcopy(solucao)
    nova_solucao[pilha][indice] = novo_minerio

    return nova_solucao


def gerar_vizinho_n2(solucao, rng=None):
    """Gera um vizinho N2 por troca de caminhões entre duas pilhas.

    A troca só é válida quando os dois minérios trocados são compatíveis com
    os respectivos Sinters de destino. O movimento preserva a massa das duas
    pilhas e a disponibilidade total de cada minério, porque a troca apenas
    redistribui caminhões entre os conjuntos.
    """

    gerador = _normalizar_rng(rng)
    movimentos = _gerar_vizinho_n2_candidatos(solucao)

    if not movimentos:
        return None

    p1, p2, i, j = gerador.choice(movimentos)
    nova_solucao = copy.deepcopy(solucao)

    minerio_a = nova_solucao[p1][i]
    minerio_b = nova_solucao[p2][j]
    nova_solucao[p1][i] = minerio_b
    nova_solucao[p2][j] = minerio_a

    return nova_solucao


def gerar_vizinho_n3(solucao, rng=None):
    """Gera um vizinho N3 por substituição simultânea de dois caminhões.

    O modelo escolhido é a substituição coordenada de duas posições dentro da
    mesma pilha. Isso permite explorar mudanças que não são alcançáveis por um
    único N1 ou por uma troca N2, e pode compensar desvios de qualidade em
    relação ao SiO2 e ao Al2O3 de forma mais específica.
    """

    gerador = _normalizar_rng(rng)
    movimentos = _gerar_vizinho_n3_candidatos(solucao)

    if not movimentos:
        return None

    pilha, i, j, novo_i, novo_j = gerador.choice(movimentos)
    nova_solucao = copy.deepcopy(solucao)
    nova_solucao[pilha][i] = novo_i
    nova_solucao[pilha][j] = novo_j

    return nova_solucao
