import json
from pathlib import Path

import pytest
import normalizacao as n
from contratos import Referencia


def test_normaliza_extremos_e_nao_trunca():
    ref = Referencia((10, 2, 4), (20, 6, 8), 'exemplo')
    assert hasattr(n, 'normalizar'), 'normalizador público ausente'
    assert n.normalizar((10, 2, 4), ref) == (0., 0., 0.)
    assert n.normalizar((20, 6, 8), ref) == (1., 1., 1.)
    assert n.normalizar((15, 4, 6), ref) == (.5, .5, .5)
    assert n.normalizar((5, 8, 10), ref) == (-.5, 1.5, 1.5)


@pytest.mark.parametrize('minimo,maximo', [
    ((1, 2, 3), (1, 4, 5)), ((2, 2, 3), (1, 4, 5)),
    ((1e12, 2, 3), (1e12+.5, 4, 5)),
    ((float('nan'), 2, 3), (4, 4, 5)), ((1, 2), (3, 4)),
    ((1, 2, 3), (float('inf'), 4, 5)),
])
def test_rejeita_referencia_invalida(minimo, maximo):
    assert hasattr(n, 'normalizar'), 'normalizador público ausente'
    with pytest.raises(ValueError):
        n.normalizar((1, 2, 3), Referencia(minimo, maximo, 'teste'))


@pytest.mark.parametrize('vetor', [(1, 2), (1, float('nan'), 2), (1, 2, float('inf'))])
def test_rejeita_objetivos_invalidos(vetor):
    assert hasattr(n, 'normalizar'), 'normalizador público ausente'
    with pytest.raises(ValueError):
        n.normalizar(vetor, Referencia((0, 0, 0), (1, 1, 1), 'teste'))


def test_carrega_referencia_real_e_rejeita_adulteracao(tmp_path):
    assert hasattr(n, 'carregar_referencia'), 'leitor público ausente'
    origem = Path('results/referencias_tp1.json')
    ref = n.carregar_referencia(origem)
    assert ref.id == '4eed030453911d878065db4ddcab092db28e085de25ec7b32dd6f52aa52e02f4'
    assert ref.origens['f1']['minimo'] == ['f1_04_seed789']
    assert n.normalizar(ref.minimo, ref) == (0., 0., 0.)
    dados = json.loads(origem.read_text(encoding='utf-8'))
    dados['minimo'][0] += 1
    destino = tmp_path / 'adulterada.json'
    destino.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError, match='[Hh]ash|identidade'):
        n.carregar_referencia(destino)


def test_referencia_ausente_falha_com_diagnostico():
    with pytest.raises(ValueError):
        n.validar_referencia(None)
