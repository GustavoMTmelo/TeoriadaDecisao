import pytest


@pytest.fixture
def modelo_pequeno(monkeypatch):
    """Modelo físico mínimo: A barato e químico inválido; B/C viáveis."""
    import sol_inicial as s
    import avaliacao as a
    import vns as v
    ores = {
        m: dict(custo=custo, fet=60., sio2=sio2, al2o3=1.5,
                disp_min=0, disp_max=2, s1=True, s2=True)
        for m, custo, sio2 in [('A', 1, 8.), ('B', 10, 5.5), ('C', 20, 5.5)]
    }
    piles = {1: {'sinter': 1, 'massa_kt': 4}}
    sinters = {1: dict(sio2_min=5., sio2_max=6., sio2_alvo=5.5,
                      al2o3_min=1., al2o3_max=2., al2o3_alvo=1.5)}
    for mod in (s, a, v):
        for name, value in [('minerios', ores), ('pilhas', piles), ('sinters', sinters)]:
            if hasattr(mod, name):
                monkeypatch.setattr(mod, name, value)
    monkeypatch.setattr(v, 'gerar_solucao_inicial', lambda: {1: ['A', 'A']})
    return {1: ['A', 'A']}, {1: ['B', 'B']}, {1: ['C', 'C']}
