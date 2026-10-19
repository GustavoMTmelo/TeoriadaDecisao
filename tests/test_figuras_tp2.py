from pathlib import Path

from figuras_tp2 import preparar_dados, resumir_metodos


def test_dados_auditados_preservam_repeticoes_falhas_e_nd_tridimensional():
    raiz = Path(__file__).resolve().parents[1]
    dados = preparar_dados(raiz/'results/integracao_tp2_final')
    assert dados['repeticoes'] == [90001, 90002]
    assert sum(r['runs'] for r in dados['tabelas']) == 8
    assert sum(r['viaveis'] for r in dados['tabelas']) == 5
    assert sum(r['sem_viavel_encontrada'] for r in dados['tabelas']) == 3
    assert len(dados['series']['ponderada', 90001]) == 13
    assert len(dados['series']['ponderada', 90002]) == 38
    assert len(dados['series']['epsilon', 90001]) == 21
    assert len(dados['series']['epsilon', 90002]) == 21
    resumo = resumir_metodos(dados)
    assert resumo['ponderada']['composicoes_uniao_nd_3d'] == 49
    assert resumo['epsilon']['composicoes_uniao_nd_3d'] == 37
    assert resumo['ponderada']['viaveis'] == 3
    assert resumo['epsilon']['sem_viavel_encontrada'] == 2
    for candidatos in dados['series'].values():
        for candidato in candidatos:
            assert candidato['origens']
            for j, valor in enumerate(candidato['avaliacao']['objetivos']):
                baixo, alto = dados['limites'][j]
                assert baixo < valor / (1e6 if j == 0 else 1) < alto
