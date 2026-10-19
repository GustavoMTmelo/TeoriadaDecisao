import json

import pytest

from empacotar_tp2 import arquivos_entrega, montar_pacote


def test_selecao_inclui_oficial_e_exclui_pdf_antigo_piloto_bruto_e_ambiente(tmp_path):
    nomes = ['relatorio.tex', 'relatorio.pdf', '.venv/segredo.txt',
             'results/tp2/execucoes/run.json', 'results/piloto_tp2_lote/execucoes/run.json',
             'results/piloto_tp2_lote/medicao_piloto.json', 'results/tp2/a.json.tmp',
             'docs/tp2/METODOLOGIA_TP2.tex', 'scripts/compilar_relatorio.ps1']
    for nome in nomes:
        p = tmp_path/nome
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('teste')
    selecionados = {p.relative_to(tmp_path).as_posix() for p in arquivos_entrega(tmp_path)}
    assert selecionados == {'relatorio.tex', 'results/tp2/execucoes/run.json',
                            'results/piloto_tp2_lote/medicao_piloto.json',
                            'docs/tp2/METODOLOGIA_TP2.tex', 'scripts/compilar_relatorio.ps1'}


def test_nao_monta_pacote_quando_auditoria_esta_pendente(tmp_path):
    p = tmp_path/'results/tp2/medicao_oficial.json'
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({'fase': 'coleta_concluida_auditoria_pendente', 'concluidas': 160}))
    destino = tmp_path/'entrega.zip'
    with pytest.raises(ValueError, match='auditadas'):
        montar_pacote(tmp_path, destino)
    assert not destino.exists()
