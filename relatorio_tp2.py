"""Consolida análise descritiva e fragmento LaTeX a partir dos produtos auditados."""

import argparse
import hashlib
import json
from pathlib import Path

from pareto import chave_solucao
from registros import escrever_json


def cobertura_estrita(a, b):
    """Fração dos vetores distintos de B estritamente dominados por algum A."""
    a, b = set(map(tuple, a)), set(map(tuple, b))
    if not b:
        return None
    dominados = sum(any(x[0] <= y[0] and x[1] <= y[1] and x[2] <= y[2]
                        and x != y for x in a) for y in b)
    return dominados / len(b)


def sobreposicao_intervalos(a, b):
    """Interseção/união de intervalos; igualdade degenerada tem sobreposição 1."""
    uniao = max(a[1], b[1]) - min(a[0], b[0])
    if uniao == 0:
        return 1.
    return max(0., min(a[1], b[1])-max(a[0], b[0])) / uniao


def ler_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def alternativas_extremas(candidatos):
    """Recupera composições completas; não combina mínimos de pontos distintos."""
    return {
        f'min_f{j+1}': min(candidatos, key=lambda c: (
            c['avaliacao']['objetivos'][j], tuple(c['avaliacao']['objetivos']),
            chave_solucao(c['solucao'])))
        for j in range(3)
    } if candidatos else {}


def analisar(campanha, figuras=None):
    campanha = Path(campanha)
    figuras = Path(figuras) if figuras else campanha/'figuras'
    manifesto = ler_json(figuras/'manifesto_figuras.json')
    # Não repetir a auditoria longa: checar integridade das fontes/produtos
    # que o gerador acabou de auditar. Este relatório usa apenas esses dados.
    for raiz, campo in ((campanha, 'fontes_sha256'), (figuras, 'produtos_sha256')):
        for nome, esperado in manifesto[campo].items():
            if hashlib.sha256((raiz/nome).read_bytes()).hexdigest() != esperado:
                raise ValueError(f'Fonte ou produto mudou após auditoria: {nome}')
    if manifesto['auditoria']['status'] != 'verificado':
        raise ValueError('Figuras sem auditoria aprovada.')
    resumo = ler_json(campanha/'resumo.json')
    metodos = ler_json(figuras/'resumo_metodos.json')
    unioes = {m: ler_json(campanha/'pareto'/f'{m}_uniao.json') for m in metodos}
    vetores = {m: [c['avaliacao']['objetivos'] for c in cs] for m, cs in unioes.items()}
    composicoes = {m: {chave_solucao(c['solucao']) for c in cs} for m, cs in unioes.items()}
    falhas = {}
    for run in resumo['execucoes']:
        if run['status'] != 'viavel':
            falhas.setdefault(f"{run['metodo']}/{run['config_id']}", []).append(run['repeticao'])
    repeticoes = manifesto['repeticoes']
    intervalos = {}
    for metodo in metodos:
        alcances = []
        for repeticao in repeticoes:
            pontos = [c['avaliacao']['objetivos']
                      for c in ler_json(campanha/'pareto'/f'{metodo}_{repeticao}.json')]
            if pontos:
                alcances.append([(min(p[j] for p in pontos), max(p[j] for p in pontos)) for j in range(3)])
        intervalos[metodo] = [
            min((sobreposicao_intervalos(a[j], b[j])
                 for i, a in enumerate(alcances) for b in alcances[i+1:]), default=None)
            for j in range(3)
        ]
    comparacao = {}
    if set(metodos) == {'ponderada', 'epsilon'}:
        comparacao = {
            'fracao_vetores_epsilon_dominados_por_ponderada': cobertura_estrita(vetores['ponderada'], vetores['epsilon']),
            'fracao_vetores_ponderada_dominados_por_epsilon': cobertura_estrita(vetores['epsilon'], vetores['ponderada']),
            'vetores_iguais_entre_metodos': len(set(map(tuple, vetores['ponderada'])) & set(map(tuple, vetores['epsilon']))),
            'composicoes_comuns_entre_metodos': len(composicoes['ponderada'] & composicoes['epsilon']),
        }
    path_medicao = campanha/'medicao_oficial.json'
    medicao = ler_json(path_medicao) if path_medicao.is_file() else None
    return {
        'runs': resumo['concluidas'], 'repeticoes': repeticoes, 'metodos': metodos,
        'falhas_por_configuracao': falhas, 'comparacao': comparacao,
        'sobreposicao_minima_intervalos_marginais': intervalos,
        'alternativas_extremas': {m: alternativas_extremas(cs) for m, cs in unioes.items()},
        'ressalvas': [
            'Cobertura estrita usa vetores distintos da amostra, sem igualdade ou garantia global.',
            'Sobreposição marginal não demonstra proximidade ou igualdade dos conjuntos em 3D.',
            'Cardinalidades físicas e número de vetores distintos têm significados diferentes.',
        ],
        'fontes_sha256': manifesto['fontes_sha256'],
        'medicao_execucao': medicao,
        'medicao_sha256': hashlib.sha256(path_medicao.read_bytes()).hexdigest() if medicao else None,
    }


def num(valor, casas=3):
    if valor is None:
        return '--'
    return r'\num{' + f'{valor:.{casas}f}' + '}'


def escrever_fragmento(analise, figuras, path):
    nomes = {'ponderada': 'Soma ponderada', 'epsilon': r'$\varepsilon$-restrito'}
    linhas = [
        '% Gerado de produtos auditados por relatorio_tp2.py.',
        r'\section{Resultados da Otimização Multiobjetivo}',
        r'\label{sec:resultados_tp2}',
        f"A coleta reuniu {analise['runs']} buscas, com {len(analise['repeticoes'])} "
        'varreduras por abordagem. Todas as buscas, inclusive as que não encontraram '
        'viável, permanecem contabilizadas. A auditoria recalculou objetivos e '
        'restrições das composições, verificou proveniência e recompôs os arquivos em 3D.',
        r'\begin{table}[H]\centering\small',
        r'\caption{Contabilidade das buscas e uniões não dominadas por método.}',
        r'\label{tab:tp2_metodos}',
        r'\begin{tabular}{lrrrrr}\toprule',
        r'Método & Runs & Viáveis & Sem viável & Composições ND & Vetores ND \\ \midrule',
    ]
    for metodo, r in analise['metodos'].items():
        linhas.append(f"{nomes[metodo]} & {r['runs']} & {r['viaveis']} & {r['sem_viavel_encontrada']} & "
                      f"{r['composicoes_uniao_nd_3d']} & {r['vetores_distintos_uniao']} " + r'\\')
    linhas.extend([r'\bottomrule\end{tabular}\end{table}',
                   r'\input{' + (Path(figuras)/'tabela_repeticoes.tex').as_posix() + '}',
                   r'\begin{table}[H]\centering\small',
                   r'\caption{Intervalos dos três objetivos nas uniões ND. Extremos de objetivos diferentes podem pertencer a composições diferentes.}',
                   r'\label{tab:tp2_intervalos}',
                   r'\resizebox{\linewidth}{!}{\begin{tabular}{lrrr}\toprule',
                   r'Método & Custo (milhões de R\$) & Desvio $SiO_2$ (p.p.$^2$) & Desvio $Al_2O_3$ (p.p.$^2$) \\ \midrule'])
    for metodo, r in analise['metodos'].items():
        intervalos = [f"{num(r['minimos_uniao'][j]/(1e6 if j == 0 else 1) if r['minimos_uniao'][j] is not None else None)}"
                      f" -- {num(r['maximos_uniao'][j]/(1e6 if j == 0 else 1) if r['maximos_uniao'][j] is not None else None)}"
                      for j in range(3)]
        linhas.append(nomes[metodo]+' & '+' & '.join(intervalos)+r' \\')
    linhas.extend([r'\bottomrule\end{tabular}}\end{table}',
                   r'\begin{table}[H]\centering\small',
                   r'\caption{Exemplos de composições efetivamente encontradas nos extremos marginais de cada método. Cada linha é uma alternativa completa, não uma combinação de mínimos.}',
                   r'\label{tab:tp2_extremos}',
                   r'\begin{tabular}{llrrr}\toprule',
                   r'Método & Extremo & Custo (milhões R\$) & $f_2$ (p.p.$^2$) & $f_3$ (p.p.$^2$) \\ \midrule'])
    for metodo, extremos in analise.get('alternativas_extremas', {}).items():
        for extremo, candidato in extremos.items():
            v = candidato['avaliacao']['objetivos']
            linhas.append(f"{nomes[metodo]} & $f_{extremo[-1]}$ mínimo & {num(v[0]/1e6)} & "
                          f"{num(v[1])} & {num(v[2])} " + r'\\')
    linhas.extend([r'\bottomrule\end{tabular}\end{table}',
                   r'\begin{table}[H]\centering\small',
                   r'\caption{Esforço efetivo. Tempos de busca são decorridos, não de CPU, e excluem persistência, consolidação e auditoria.}',
                   r'\label{tab:tp2_esforco}',
                   r'\begin{tabular}{lrrr}\toprule',
                   r'Método & Avaliações & Tempo de busca (s) & Média por run (s) \\ \midrule'])
    for metodo, r in analise['metodos'].items():
        linhas.append(f"{nomes[metodo]} & {num(r['avaliacoes'],0)} & {num(r['tempo_buscas_s'],2)} & "
                      f"{num(r['tempo_buscas_s']/r['runs'],2)} " + r'\\')
    linhas.extend([r'\bottomrule\end{tabular}\end{table}'])
    medicao = analise.get('medicao_execucao')
    if medicao and not medicao['reutilizadas']:
        linhas.append(f"A coleta completa, incluindo persistência e consolidação, levou "
                      f"{num(medicao['duracao_coleta_s']/60,2)} minutos. A auditoria e geração "
                      f"de figuras consumiram {num(medicao['duracao_auditoria_e_figuras_s']/60,2)} "
                      'minutos adicionais. Esses valores não se confundem com a soma dos tempos dos solvers.')
    linhas.extend([
                   r'\subsection{Projeções e variabilidade entre varreduras}',
                   'As figuras mantêm os arquivos ND de cada repetição antes da projeção. '
                   'Um ponto aparentemente dominado em 2D pode permanecer não dominado em 3D. '
                   'A mesma composição pode aparecer nas cinco varreduras, com todas as origens preservadas.'])
    for metodo in analise['metodos']:
        for j, k in ((1, 2), (1, 3), (2, 3)):
            caminho = (Path(figuras)/f'{metodo}_f{j}_f{k}.pdf').as_posix()
            linhas.extend([r'\begin{figure}[H]\centering',
                           r'\includegraphics[width=0.88\linewidth]{'+caminho+'}',
                           f"\\caption{{{nomes[metodo]}: projeção $f_{j}\\times f_{k}$, com as repetições identificadas.}}",
                           f'\\label{{fig:tp2_{metodo}_{j}_{k}}}', r'\end{figure}'])
    linhas.extend([r'\subsection{Comparação descritiva das aproximações}'])
    c = analise['comparacao']
    if c:
        a, b = c['fracao_vetores_epsilon_dominados_por_ponderada'], c['fracao_vetores_ponderada_dominados_por_epsilon']
        if a is not None and b is not None:
            linhas.append('Entre os vetores distintos encontrados, a união ponderada domina estritamente '
                          f"{num(100*a,2)}\\% dos vetores da união $\\varepsilon$-restrita; no sentido inverso, "
                          f"a fração é {num(100*b,2)}\\%. Essa comparação usa três objetivos e apenas as amostras "
                          'encontradas; não certifica superioridade global dos métodos.')
        linhas.append(f"Há {c['vetores_iguais_entre_metodos']} vetores de objetivos iguais e "
                      f"{c['composicoes_comuns_entre_metodos']} composições físicas comuns entre as uniões. "
                      'Essas contagens são distintas da quantidade de pontos sobrepostos em uma projeção.')
    linhas.append('O escalar principal não é comparável entre métodos ou configurações. A comparação '
                  'deve considerar os três objetivos brutos, as mesmas referências, o teto comum e o '
                  'esforço efetivamente realizado. Mais composições no arquivo não provam melhor método. '
                  'As cinco varreduras, e não as buscas individuais, representam as repetições do desenho.')
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text('\n'.join(linhas)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campanha', default='results/tp2')
    args = parser.parse_args()
    campanha = Path(args.campanha)
    analise = analisar(campanha)
    escrever_json(campanha/'analise.json', analise)
    escrever_fragmento(analise, campanha/'figuras', campanha/'resultados_tp2.tex')
    print(json.dumps({k: analise[k] for k in ('runs', 'comparacao', 'falhas_por_configuracao')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
