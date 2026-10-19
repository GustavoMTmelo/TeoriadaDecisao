import random

import vns


def test_melhoria_apos_quinto_reinicio_permanece_em_n2(monkeypatch):
    geradores = [object(), object(), object()]
    monkeypatch.setattr(vns, '_GERADORES_VND', geradores)
    # Cinco melhorias/reinícios em N1; N1 falha; N2 melhora e depois falha; N3 falha.
    respostas = iter([True] * 5 + [False, True, False, False])
    chamadas = []
    def busca(sol, obj, gerador, rng, acompanhamento=None):
        chamadas.append(geradores.index(gerador) + 1)
        return sol + 1, next(respostas)
    monkeypatch.setattr(vns, '_busca_local_n', busca)
    vns.vnd(0, 'f1', random.Random(1), max_restarts=5)
    assert chamadas == [1, 1, 1, 1, 1, 1, 2, 2, 3]


def test_melhoria_antes_do_limite_reinicia_n1(monkeypatch):
    geradores = [object(), object(), object()]
    monkeypatch.setattr(vns, '_GERADORES_VND', geradores)
    respostas = iter([False, True, False, False, False])
    chamadas = []
    def busca(sol, obj, gerador, rng, acompanhamento=None):
        chamadas.append(geradores.index(gerador) + 1)
        return sol, next(respostas)
    monkeypatch.setattr(vns, '_busca_local_n', busca)
    vns.vnd(0, 'f1', random.Random(1), max_restarts=5)
    assert chamadas == [1, 2, 1, 2, 3]
