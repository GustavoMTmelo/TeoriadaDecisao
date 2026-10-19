import copy
import random
from collections import Counter

import pytest

from sol_inicial import gerar_solucao_inicial, contar_uso_minerios, eh_compativel, pilhas
from vns import _gerar_vizinho_n2_rapido as n2, _gerar_vizinho_n3_rapido as n3


@pytest.mark.parametrize('gerador', [n2, n3])
def test_operador_rapido_preserva_entrada_e_reproduz_seed(gerador):
    sol = gerar_solucao_inicial()
    original = copy.deepcopy(sol)
    viz = gerador(sol, random.Random(42))
    assert viz is not None
    assert sol == original
    assert viz == gerador(sol, random.Random(42))
    assert set(viz) == set(sol)
    for p in sol:
        assert len(viz[p]) == len(sol[p])
        assert all(eh_compativel(m, pilhas[p]['sinter']) for m in viz[p])
    alteracoes = [(p, i) for p in sol for i in range(len(sol[p])) if sol[p][i] != viz[p][i]]
    assert len(alteracoes) == 2
    if gerador is n2:
        assert alteracoes[0][0] != alteracoes[1][0]
        assert contar_uso_minerios(viz) == contar_uso_minerios(sol)
    else:
        p = alteracoes[0][0]
        assert p == alteracoes[1][0]
        assert Counter(viz[p]) != Counter(sol[p])


@pytest.mark.parametrize('gerador,solucao', [
    (n2, {}), (n2, {1: ['M1']}), (n3, {}), (n3, {1: ['M1']})])
def test_operador_sem_posicoes_suficientes_retorna_none(gerador, solucao):
    assert gerador(solucao, random.Random(1)) is None


class SempreIgual:
    def __init__(self):
        self.sorteios = 0

    def sample(self, seq, n):
        self.sorteios += 1
        return list(seq)[:n]

    def randrange(self, n):
        return 0

    def shuffle(self, seq):
        pass

    def choice(self, seq):
        return 'M1'


def test_n2_esgota_tentativas_sem_swap_de_minerios_iguais():
    rng = SempreIgual()
    assert n2({1: ['M1'], 2: ['M1']}, rng, tentativas=3) is None
    assert rng.sorteios == 3


def test_n3_esgota_tentativas_sem_mudancas_unitarias():
    rng = SempreIgual()
    assert n3({1: ['M1', 'M1']}, rng, tentativas=3) is None
    assert rng.sorteios == 3


def test_n3_rejeita_permutacao_interna():
    rng = SempreIgual()
    respostas = iter(['M2', 'M1'])
    rng.choice = lambda seq: next(respostas)
    assert n3({1: ['M1', 'M2']}, rng, tentativas=1) is None
