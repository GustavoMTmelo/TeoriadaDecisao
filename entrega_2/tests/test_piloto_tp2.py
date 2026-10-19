from piloto_tp2 import resumir_piloto


def test_medicao_distingue_falha_de_busca_e_inclui_tempo_da_consolidacao():
    runs = [
        dict(metodo='ponderada', config_id='a', status='viavel', tempo_s=2,
             avaliacoes=100, motivo_parada='max_avaliacoes'),
        dict(metodo='epsilon', config_id='b', status='sem_viavel_encontrada',
             tempo_s=3, avaliacoes=80, motivo_parada='estagnacao'),
    ]
    medicao = resumir_piloto({'execucoes': runs}, 10, 4, 1000)
    assert medicao['estimativa_160_runs_s'] == 800
    assert medicao['por_metodo']['epsilon']['viaveis'] == 0
    assert medicao['por_metodo']['epsilon']['avaliacoes'] == 80
    assert medicao['por_configuracao']['epsilon/b']['motivos_parada'] == ['estagnacao']


def test_retomada_nao_produz_estimativa_de_campanha_completa():
    run = dict(metodo='epsilon', config_id='a', status='viavel', tempo_s=8,
               avaliacoes=100, motivo_parada='max_avaliacoes')
    medicao = resumir_piloto({'execucoes': [run]}, 1, 1, 10, reutilizadas=1)
    assert medicao['estimativa_160_runs_s'] is None
    assert medicao['estimativa_160_runs_com_folga_50pct_s'] is None
