import json
from dataclasses import replace

import pytest

from avaliacao import avaliar
from contratos import Candidato, ConfigEscalar, ResultadoBusca
import vns


def resultado_fisico(sol):
    av = avaliar(sol, ConfigEscalar('mono', 'f1', objetivo=1))
    cand = Candidato(sol, av)
    viavel = cand if av.viavel else None
    return ResultadoBusca('viavel' if viavel else 'sem_viavel_encontrada', viavel, cand,
                          [{'iteracao': 0, 'avaliacoes': 1,
                            'melhor_viavel': av.escalar if viavel else None,
                            'objetivo_busca': av.escalar, 'fitness_busca': av.chave[0]}],
                          1, 0, 'max_iter', .1)


def test_round_trip_revalida_composicao_e_objetivos(modelo_pequeno, tmp_path):
    from registros import salvar_resultado, ler_resultado
    _, b, _ = modelo_pequeno
    r = resultado_fisico(b)
    path = tmp_path / 'run.json'
    salvar_resultado(r, {'objetivo': 'f1', 'seed': 42}, path)
    lido, meta = ler_resultado(path)
    assert lido == r
    assert meta['seed'] == 42
    assert set(lido.melhor_viavel.solucao) == {1}
    assert lido.melhor_viavel.avaliacao.objetivos == (40000, 0., 0.)


@pytest.mark.parametrize('tipo', ['objetivo', 'composicao', 'validacao'])
def test_registro_adulterado_rejeitado(modelo_pequeno, tmp_path, tipo):
    from registros import salvar_resultado, ler_resultado
    _, b, _ = modelo_pequeno
    path = tmp_path / 'run.json'
    salvar_resultado(resultado_fisico(b), {'objetivo': 'f1', 'seed': 42}, path)
    dados = json.loads(path.read_text(encoding='utf-8'))
    candidato = dados['resultado']['melhor_viavel']
    if tipo == 'objetivo':
        candidato['avaliacao']['objetivos'][0] += 1
    elif tipo == 'composicao':
        candidato['solucao']['1'][0] = 'A'
    else:
        candidato['avaliacao']['qualidade_ok'] = False
    path.write_text(json.dumps(dados), encoding='utf-8')
    with pytest.raises(ValueError):
        ler_resultado(path)


def test_falha_preservada_e_excluida_de_estatisticas(modelo_pequeno, monkeypatch, tmp_path):
    from registros import ler_resultado
    inicial, b, c = modelo_pequeno
    resultados = iter([resultado_fisico(b), resultado_fisico(c), resultado_fisico(inicial),
                       resultado_fisico(b), resultado_fisico(c)])
    monkeypatch.setattr(vns, 'gvns', lambda *a, **kw: next(resultados))
    exp = vns.executar_experimento('f1', output_dir=tmp_path)
    assert exp['n_viaveis'] == 4 and exp['n_falhas'] == 1
    assert exp['resultados'] == [40000, 80000, None, 40000, 80000]
    assert exp['media'] == 60000
    assert exp['desvio'] == pytest.approx(23094.01076758503)
    registros = list((tmp_path / 'execucoes').glob('*.json'))
    assert len(registros) == 5
    assert sum(ler_resultado(p)[0].status == 'sem_viavel_encontrada' for p in registros) == 1


@pytest.mark.parametrize('sucessos', [0, 1])
def test_estatistica_com_zero_ou_uma_viavel(modelo_pequeno, monkeypatch, tmp_path, sucessos):
    inicial, b, _ = modelo_pequeno
    resultados = iter([resultado_fisico(b)] * sucessos + [resultado_fisico(inicial)] * (5-sucessos))
    monkeypatch.setattr(vns, 'gvns', lambda *a, **kw: next(resultados))
    exp = vns.executar_experimento('f1', output_dir=tmp_path)
    assert exp['desvio'] is None
    assert exp['melhor_valor'] == (40000 if sucessos else None)
    assert len(list((tmp_path / 'execucoes').glob('*.json'))) == 5


def test_curvas_e_composicao_geradas_de_registros(modelo_pequeno, monkeypatch, tmp_path):
    from registros import carregar_experimento
    _, b, _ = modelo_pequeno
    monkeypatch.setattr(vns, 'gvns', lambda *a, **kw: resultado_fisico(b))
    vns.executar_experimento('f1', output_dir=tmp_path)
    exp = carregar_experimento(tmp_path, 'f1')
    vns.plotar_convergencia(exp, tmp_path / 'curva.png')
    vns.plotar_melhor_solucao(exp, tmp_path / 'composicao.png')
    assert exp['melhor_solucao'] == b
    assert (tmp_path / 'curva.png').stat().st_size > 1000
    assert (tmp_path / 'composicao.png').stat().st_size > 1000
