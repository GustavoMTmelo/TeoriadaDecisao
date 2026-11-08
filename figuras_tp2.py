"""Seis projeções, tabelas e proveniência de uma campanha TP2 auditada."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from registros import escrever_json
from verificar_tp2 import verificar_campanha

METODOS = {'ponderada': 'Soma ponderada', 'epsilon': 'ε-restrito'}
ROTULOS = ('Custo (milhões de R$)', 'Desvio de SiO₂ (p.p.²)', 'Desvio de Al₂O₃ (p.p.²)')
PARES = ((0, 1), (0, 2), (1, 2))
CORES = ('#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00')
MARCADORES = ('o', 's', '^', 'D', 'v')


def ler_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def preparar_dados(campanha):
    """Preserva ND 3D por repetição; não refiltra pontos nas projeções 2D."""
    campanha = Path(campanha)
    auditoria = verificar_campanha(campanha)
    resumo = ler_json(campanha/'resumo.json')
    manifesto = ler_json(campanha/'manifesto.json')
    repeticoes = list(dict.fromkeys(r['repeticao'] for r in manifesto['agenda']))
    if len(repeticoes) > len(CORES):
        raise ValueError('Identidade visual definida para até cinco repetições.')
    series, tabelas, unioes = {}, [], {}
    fontes = [campanha/'manifesto.json', campanha/'resumo.json']
    for metodo in METODOS:
        runs_metodo = [r for r in resumo['execucoes'] if r['metodo'] == metodo]
        if not runs_metodo:
            continue
        for repeticao in repeticoes:
            runs = [r for r in runs_metodo if r['repeticao'] == repeticao]
            if not runs:
                continue
            path = campanha/'pareto'/f'{metodo}_{repeticao}.json'
            fontes.append(path)
            candidatos = ler_json(path)
            series[(metodo, repeticao)] = candidatos
            pontos = [c['avaliacao']['objetivos'] for c in candidatos]
            linha = {
                'metodo': metodo, 'repeticao': repeticao, 'runs': len(runs),
                'viaveis': sum(r['status'] == 'viavel' for r in runs),
                'sem_viavel_encontrada': sum(r['status'] == 'sem_viavel_encontrada' for r in runs),
                'avaliacoes': sum(r['avaliacoes'] for r in runs),
                'tempo_buscas_s': sum(r['tempo_s'] for r in runs),
                'composicoes_nd_3d': len(candidatos),
            }
            for j in range(3):
                linha[f'f{j+1}_min_nd'] = min((p[j] for p in pontos), default=None)
                linha[f'f{j+1}_max_nd'] = max((p[j] for p in pontos), default=None)
            tabelas.append(linha)
        path_uniao = campanha/'pareto'/f'{metodo}_uniao.json'
        fontes.append(path_uniao)
        unioes[metodo] = ler_json(path_uniao)
    # Limites comuns aos dois métodos para permitir comparar as regiões.
    limites = []
    for j in range(3):
        valores = [c['avaliacao']['objetivos'][j] / (1e6 if j == 0 else 1)
                   for candidatos in series.values() for c in candidatos]
        if not valores:
            limites.append((0, 1))
            continue
        baixo, alto = min(valores), max(valores)
        folga = (alto - baixo) * .06 or max(abs(baixo) * .02, .01)
        limites.append((baixo - folga, alto + folga))
    return dict(series=series, tabelas=tabelas, repeticoes=repeticoes,
                limites=limites, fontes=fontes, auditoria=auditoria, unioes=unioes)


def resumir_metodos(dados):
    resumo = {}
    for metodo, candidatos in dados['unioes'].items():
        linhas = [r for r in dados['tabelas'] if r['metodo'] == metodo]
        vetores = [tuple(c['avaliacao']['objetivos']) for c in candidatos]
        resumo[metodo] = {
            'runs': sum(r['runs'] for r in linhas),
            'viaveis': sum(r['viaveis'] for r in linhas),
            'sem_viavel_encontrada': sum(r['sem_viavel_encontrada'] for r in linhas),
            'avaliacoes': sum(r['avaliacoes'] for r in linhas),
            'tempo_buscas_s': sum(r['tempo_buscas_s'] for r in linhas),
            'composicoes_uniao_nd_3d': len(candidatos),
            'vetores_distintos_uniao': len(set(vetores)),
            'minimos_uniao': [min((v[j] for v in vetores), default=None) for j in range(3)],
            'maximos_uniao': [max((v[j] for v in vetores), default=None) for j in range(3)],
            'ressalva': 'Extremos marginais podem vir de composições diferentes; cardinalidade não prova superioridade.',
        }
    return resumo


def gerar_figuras(campanha, output, *, titulo='Campanha TP2'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    campanha, output = Path(campanha), Path(output)
    if output.resolve() == campanha.resolve():
        raise ValueError('Escolha um subdiretório de figuras ou uma saída separada.')
    dados = preparar_dados(campanha)
    output.mkdir(parents=True, exist_ok=True)
    gerados = []
    for metodo, nome in METODOS.items():
        for j, k in PARES:
            fig, ax = plt.subplots(figsize=(8, 5.4), layout='constrained')
            tem_pontos = False
            for i, repeticao in enumerate(dados['repeticoes']):
                candidatos = dados['series'].get((metodo, repeticao), [])
                pontos = [c['avaliacao']['objetivos'] for c in candidatos]
                tem_pontos |= bool(pontos)
                ax.scatter([p[j] / (1e6 if j == 0 else 1) for p in pontos],
                           [p[k] for p in pontos], marker=MARCADORES[i],
                           s=55 + 12*i, facecolors='none', edgecolors=CORES[i],
                           linewidths=1.25,
                           label=f'R{i+1} · base {repeticao} · ND {len(pontos)}')
            if not tem_pontos:
                ax.text(.5, .5, 'Nenhuma alternativa viável encontrada',
                        transform=ax.transAxes, ha='center', va='center')
            ax.set(xlabel=ROTULOS[j], ylabel=ROTULOS[k],
                   title=f'{titulo} — {nome}\nNão dominadas em 3D por repetição',
                   xlim=dados['limites'][j], ylim=dados['limites'][k])
            ax.grid(alpha=.2)
            ax.set_axisbelow(True)
            ax.legend(fontsize=8, loc='best')
            for extensao in ('png', 'pdf'):
                path = output/f'{metodo}_f{j+1}_f{k+1}.{extensao}'
                fig.savefig(path, dpi=180, bbox_inches='tight')
                gerados.append(path.name)
            plt.close(fig)
    with (output/'resumo_repeticoes.csv').open('w', encoding='utf-8', newline='') as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=list(dados['tabelas'][0]))
        writer.writeheader()
        writer.writerows(dados['tabelas'])
    # Exporta todas as origens; um ponto compartilhado não perde sua repetição.
    with (output/'pontos_projetados.csv').open('w', encoding='utf-8', newline='') as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=['metodo', 'repeticao', 'f1', 'f2', 'f3', 'origens'])
        writer.writeheader()
        for (metodo, repeticao), candidatos in dados['series'].items():
            for candidato in candidatos:
                writer.writerow(dict(metodo=metodo, repeticao=repeticao,
                                     **dict(zip(('f1', 'f2', 'f3'), candidato['avaliacao']['objetivos'])),
                                     origens=json.dumps(candidato['origens'], ensure_ascii=False)))
    gerados.extend(['resumo_repeticoes.csv', 'pontos_projetados.csv'])
    escrever_json(output/'resumo_metodos.json', resumir_metodos(dados))
    gerados.append('resumo_metodos.json')
    linhas_tex = [
        '% Gerado por figuras_tp2.py; não editar números manualmente.',
        r'\begin{table}[H]\centering',
        r'\caption{Resultados por varredura. ND: composições não dominadas em três objetivos.}',
        r'\label{tab:tp2_repeticoes}',
        r'\begin{tabular}{llrrrr}\toprule',
        r'Método & Semente-base & Runs & Viáveis & Sem viável & ND \\ \midrule',
    ]
    for r in dados['tabelas']:
        nome_tex = 'Ponderada' if r['metodo'] == 'ponderada' else r'$\varepsilon$-restrito'
        linhas_tex.append(f"{nome_tex} & {r['repeticao']} & {r['runs']} & {r['viaveis']} & "
                          f"{r['sem_viavel_encontrada']} & {r['composicoes_nd_3d']} " + r'\\')
    linhas_tex.extend([r'\bottomrule\end{tabular}', r'\end{table}'])
    (output/'tabela_repeticoes.tex').write_text('\n'.join(linhas_tex)+'\n', encoding='utf-8')
    gerados.append('tabela_repeticoes.tex')
    manifesto = {
        'titulo': titulo, 'campanha': str(campanha), 'auditoria': dados['auditoria'],
        'codigo_figuras_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'repeticoes': dados['repeticoes'], 'limites_comuns': dados['limites'],
        'semantica': 'ND 3D por repetição, sem nova filtragem em projeção 2D; f1 em milhões nos gráficos.',
        'fontes_sha256': {str(p.relative_to(campanha)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in dados['fontes']},
        'produtos_sha256': {nome: hashlib.sha256((output/nome).read_bytes()).hexdigest() for nome in gerados},
    }
    escrever_json(output/'manifesto_figuras.json', manifesto)
    return manifesto


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campanha', default='results/tp2')
    parser.add_argument('--output', default='results/tp2/figuras')
    parser.add_argument('--titulo', default='Campanha TP2')
    args = parser.parse_args()
    r = gerar_figuras(args.campanha, args.output, titulo=args.titulo)
    print(json.dumps({'produtos': len(r['produtos_sha256']), 'auditoria': r['auditoria']}, indent=2))


if __name__ == '__main__':
    main()
