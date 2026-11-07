"""Integração pública: busca real, registros, química, epsilon, ND e retomada."""
import json
from dataclasses import asdict
from pathlib import Path

import pytest

from contratos import ConfigBusca, ConfigEscalar


def test_busca_real_repete_numeros_dos_dois_metodos():
    from busca import resolver
    from normalizacao import carregar_referencia
    from sol_inicial import calcular_f1, calcular_f2, calcular_f3, validar_estrutura, validar_qualidade
    ref = carregar_referencia(Path(__file__).resolve().parents[1] / 'results/referencias_tp1.json')
    configs = [ConfigEscalar('ponderada', 'p', pesos=(1/3, 1/3, 1/3)),
               ConfigEscalar('epsilon', 'e', epsilons=(1., 1.))]
    for config in configs:
        vistos = []
        a = resolver(config, ref, 90001, ConfigBusca(max_avaliacoes=200), vistos.append)
        b = resolver(config, ref, 90001, ConfigBusca(max_avaliacoes=200))
        sa, sb = asdict(a), asdict(b)
        sa.pop('tempo_s'); sb.pop('tempo_s')
        assert sa == sb
        assert len(vistos) == a.avaliacoes == 200
        assert a.motivo_parada == 'max_avaliacoes'
        for c in vistos:
            assert validar_estrutura(c.solucao)[0]
            assert c.avaliacao.objetivos == (calcular_f1(c.solucao), calcular_f2(c.solucao), calcular_f3(c.solucao))
            if c.avaliacao.viavel:
                assert validar_qualidade(c.solucao)[0]
                if config.metodo == 'epsilon':
                    assert all(g <= e + 1e-9 for g, e in zip(c.avaliacao.normalizados[1:], config.epsilons))
        if a.melhor_viavel:
            assert any(c.solucao == a.melhor_viavel.solucao for c in vistos)


@pytest.mark.parametrize('minimo_qualidade', [0, -1])
def test_campanha_real_controlada_revalida_pareto_e_retoma(modelo_pequeno, monkeypatch, tmp_path, minimo_qualidade):
    import busca
    import hashlib
    from experimentos import executar_campanha
    from registros import ler_resultado
    from sol_inicial import calcular_f1, calcular_f2, calcular_f3, validar_qualidade
    # Modelagem real de B viável e A inviável; os dois métodos exercitam o núcleo.
    a, b, _ = modelo_pequeno
    monkeypatch.setattr(busca, 'gerar_solucao_inicial', lambda: a)
    monkeypatch.setattr(busca, 'GERADORES', [lambda s, rng: b] * 3)
    origens = {f'f{j}': {'minimo': ['min'], 'maximo': ['max']} for j in range(1, 4)}
    # Com referência inferior a zero, B continua física mas viola ambos epsilon=0.
    payload = {'minimo': [0, minimo_qualidade, minimo_qualidade],
               'maximo': [100000, 20, 20], 'origens': origens}
    ref = {**payload, 'id': hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()}
    (tmp_path / 'ref.json').write_text(json.dumps(ref), encoding='utf-8')
    conf = {'referencia': 'ref.json', 'seeds_base': [90001, 90002],
            'busca': {'max_avaliacoes': 5}, 'configuracoes': [
                {'metodo': 'ponderada', 'id': 'p', 'pesos': [1, 0, 0]},
                {'metodo': 'epsilon', 'id': 'e', 'epsilons': [0, 0]}]}
    path = tmp_path / 'config.json'
    path.write_text(json.dumps(conf), encoding='utf-8')
    out = tmp_path / 'saida'
    resumo = executar_campanha(path, out)
    assert resumo['concluidas'] == 4
    for registro in (out / 'execucoes').glob('*.json'):
        resultado, meta = ler_resultado(registro)
        assert resultado.avaliacoes == 5
        if meta['metodo'] == 'epsilon' and minimo_qualidade == -1:
            assert resultado.status == 'sem_viavel_encontrada'
            assert resultado.melhor_viavel is None
            assert not resultado.melhor_busca.avaliacao.epsilon_ok
            from avaliacao import avaliar
            from normalizacao import carregar_referencia
            av_b = avaliar(b, ConfigEscalar('epsilon', 'e', epsilons=(0, 0)),
                           carregar_referencia(tmp_path / 'ref.json'))
            assert av_b.qualidade_ok and not av_b.epsilon_ok
            continue
        assert resultado.status == 'viavel'
        c = resultado.melhor_viavel
        assert c.solucao == b and validar_qualidade(c.solucao)[0]
        assert c.avaliacao.objetivos == (calcular_f1(b), calcular_f2(b), calcular_f3(b))
        assert meta['seed'] >= 0
    for arquivo in (out / 'pareto').glob('*.json'):
        candidatos = json.loads(arquivo.read_text(encoding='utf-8'))
        if arquivo.name.startswith('epsilon') and minimo_qualidade == -1:
            assert candidatos == []
            continue
        assert len(candidatos) == 1
        assert candidatos[0]['avaliacao']['objetivos'] == [40000, 0., 0.]
        assert candidatos[0]['origens']
    def proibido(*args, **kwargs):
        raise AssertionError('Retomada repetiu busca concluída')
    assert executar_campanha(path, out, solver=proibido)['reutilizadas'] == 4


def test_cinco_varreduras_completas_com_orcamento_zero(tmp_path):
    from experimentos import executar_campanha
    raiz = Path(__file__).resolve().parents[1]
    config = json.loads((raiz / 'configs/tp2.json').read_text(encoding='utf-8'))
    config['referencia'] = str(raiz / 'results/referencias_tp1.json')
    config['busca']['max_avaliacoes'] = 0
    path = tmp_path / 'config.json'
    path.write_text(json.dumps(config), encoding='utf-8')
    out = tmp_path / 'campanha'
    resumo = executar_campanha(path, out)
    assert resumo['concluidas'] == resumo['esperadas'] == 160
    assert len(resumo['arquivos_pareto']) == 12
    assert all(r['avaliacoes'] == 0 and r['status'] == 'sem_viavel_encontrada'
               and r['motivo_parada'] == 'max_avaliacoes' for r in resumo['execucoes'])
    for metodo in ('ponderada', 'epsilon'):
        linhas = [r for r in resumo['execucoes'] if r['metodo'] == metodo]
        assert len(linhas) == 80
        assert len({r['repeticao'] for r in linhas}) == 5
        assert all(sum(r['repeticao'] == s for r in linhas) == 16 for s in (42, 123, 456, 789, 1011))
    def proibido(*args, **kwargs):
        raise AssertionError('Repetiu run com orçamento zero')
    assert executar_campanha(path, out, solver=proibido)['reutilizadas'] == 160
