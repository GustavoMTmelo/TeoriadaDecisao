from relatorio_tp2 import alternativas_extremas, cobertura_estrita, sobreposicao_intervalos


def test_cobertura_exige_dominancia_estrita_nos_tres_objetivos_e_deduplica_vetores():
    a = [(1, 2, 3)]
    b = [(2, 3, 4), (2, 3, 4), (1, 2, 3), (2, 3, 1)]
    assert cobertura_estrita(a, b) == 1/3
    assert cobertura_estrita(b, a) == 0
    assert cobertura_estrita(a, []) is None


def test_sobreposicao_de_intervalos_nao_extrapola_nem_falha_com_amplitude_zero():
    assert sobreposicao_intervalos((0, 2), (1, 3)) == 1/3
    assert sobreposicao_intervalos((0, 1), (2, 3)) == 0
    assert sobreposicao_intervalos((1, 1), (1, 1)) == 1


def test_extremos_preservam_vetores_e_composicoes_sem_inventar_alternativa_ideal():
    candidatos = [dict(avaliacao={'objetivos': v}, solucao={'1': [nome]}, origens=[{'seed': i}])
                  for i, (nome, v) in enumerate([('A', (0, 10, 10)),
                                                 ('B', (10, 0, 10)), ('C', (10, 10, 0))])]
    extremos = alternativas_extremas(candidatos)
    assert [extremos[f'min_f{j}']['solucao']['1'][0] for j in (1, 2, 3)] == ['A', 'B', 'C']
    assert all(tuple(c['avaliacao']['objetivos']) != (0, 0, 0) for c in extremos.values())
    assert all(c['origens'] for c in extremos.values())
