"""Fragmento LaTeX dos resultados TP1, sempre derivado dos registros completos."""

from pathlib import Path
import statistics

from registros import carregar_experimento, ler_resultado


def gerar_fragmento(diretorio, resumo, referencia):
    d = Path(diretorio)
    try:
        imagens = d.resolve().relative_to(Path(__file__).resolve().parent).as_posix()
    except ValueError:
        imagens = d.resolve().as_posix()
    exps = {obj: carregar_experimento(d, obj) for obj in ('f1','f2','f3')}
    registros = [ler_resultado(p) for p in sorted((d/'execucoes').glob('*.json'))]
    def num(v, dec=6):
        return r'\num{' + f'{v:.{dec}f}' + '}'
    linhas = [r'\section{Resultados Computacionais}',
              r'\subsection{Planejamento e validação dos experimentos}',
              r'Esta revisão reexecutou os três problemas em cinco sementes '
              r'($42$, $123$, $456$, $789$, $1011$), totalizando 15 buscas. '
              r'Os parâmetros da Tabela~\ref{tab:parametros} e os pesos históricos de penalidade '
              r'foram preservados. O retorno passou a ser a melhor solução viável observada, '
              r'independentemente da incumbente por fitness.',
              r'Cada rodada tem composição, três objetivos, violações, status, histórico, '
              r'contadores, motivo de parada e tempo decorrido em JSON. A releitura recalcula '
              r'os valores; uma segunda rotina confere massa, compatibilidade, usos globais, '
              r'faixas químicas e objetivos por contagens de minérios. As 15 soluções finais '
              r'passaram pelas duas verificações. As estatísticas usam desvio-padrão amostral '
              r'com denominador $n-1$.',
              r'\begin{table}[H]\centering\small',
              r'\caption{Resultados finais viáveis das cinco execuções por objetivo. '
              r'Cada coluna corresponde a um problema otimizado separadamente.}',
              r'\label{tab:resultados}', r'\begin{tabular}{lrrr}\toprule',
              r'Execução & $f_1$ (R\$) & $f_2$ (p.p.$^2$) & $f_3$ (p.p.$^2$) \\ \midrule']
    for i, seed in enumerate((42,123,456,789,1011)):
        linhas.append(f'{i+1} (seed {seed}) & ' + ' & '.join(num(exps[o]['resultados'][i], 0 if o=='f1' else 6)
                                                        for o in exps) + r' \\')
    linhas.append(r'\midrule')
    for titulo, campo in [('Mínimo','minimo'),('Média','media'),('Desvio-padrão','desvio'),('Máximo','maximo')]:
        linhas.append(titulo + ' & ' + ' & '.join(num(exps[o][campo], 0 if o=='f1' else 6)
                                                for o in exps) + r' \\')
    linhas += [r'\bottomrule\end{tabular}\end{table}',
               r'\subsection{Esforço e parada}',
               r'Os tempos abaixo são de relógio e dependem da máquina e da instrumentação. '
               r'Não são tempos de CPU nem devem ser comparados diretamente aos do log antigo.',
               r'\begin{table}[H]\centering\small',
               r'\caption{Esforço da campanha corrigida por objetivo}',
               r'\begin{tabular}{lrrrr}\toprule',
               r'Objetivo & Tempo médio (s) & Avaliações médias & Máx. iterações & Estagnação \\ \midrule']
    for obj in exps:
        runs = [r for r,m in registros if m['objetivo']==obj]
        linhas.append(f'${obj[0]}_{obj[1]}$ & {num(statistics.mean(r.tempo_s for r in runs),1)} & '
                      f'{num(statistics.mean(r.avaliacoes for r in runs),0)} & '
                      f'{sum(r.motivo_parada=="max_iter" for r in runs)} & '
                      f'{sum(r.motivo_parada=="estagnacao" for r in runs)}' + r' \\')
    linhas += [r'\bottomrule\end{tabular}\end{table}',
               r'\subsection{Curvas de convergência}',
               r'Cada figura sobrepõe as cinco sementes. O eixo vertical representa a melhor '
               r'solução viável já observada, não o objetivo bruto da trajetória penalizada. '
               r'Antes do primeiro candidato viável o valor é ausente; após esse momento, '
               r'a curva não aumenta. A construtiva ($f_1=60{.}400{.}000$ R\$, '
               r'$f_2\approx23{,}481055$, $f_3\approx14{,}909888$) tem 12 violações '
               r'químicas e é apenas ponto de partida.']
    for obj in exps:
        linhas += [r'\begin{figure}[H]\centering',
                   r'\includegraphics[width=0.88\textwidth]{'+imagens+f'/convergencia_{obj}.png'+'}',
                   r'\caption{Melhor valor viável observado de $f_'+obj[1]+r'$ nas cinco execuções}',
                   r'\label{fig:conv_'+obj+'}', r'\end{figure}']
    linhas += [r'\subsection{Melhores composições e compromissos}',
               r'As barras mostram caminhões de 2 kt por minério em cada pilha; as alturas '
               r'vão de 10 a 19 caminhões. As composições completas estão nos registros JSON.']
    for obj in exps:
        linha = next(x for x in resumo['matriz_payoff'] if x['objetivo_otimizado']==obj)
        seed = next(m['seed'] for _,m in registros if m['run_id']==linha['run_id'])
        linhas += [r'\begin{figure}[H]\centering',
                   r'\includegraphics[width=\textwidth]{'+imagens+f'/melhor_solucao_{obj}.png'+'}',
                   r'\caption{Melhor composição para $f_'+obj[1]+'='+num(exps[obj]['melhor_valor'],0 if obj=='f1' else 6)+
                   '$'+f' (seed {seed})'+'}',
                   r'\label{fig:sol_'+obj+'}', r'\end{figure}']
    linhas += [r'\begin{table}[H]\centering\small',
               r'\caption{Matriz cruzada das melhores soluções mono-objetivo}',
               r'\begin{tabular}{lrrr}\toprule',
               r'Objetivo otimizado & $f_1$ (R\$) & $f_2$ (p.p.$^2$) & $f_3$ (p.p.$^2$) \\ \midrule']
    for linha in resumo['matriz_payoff']:
        linhas.append('$f_'+linha['objetivo_otimizado'][1]+'$ & '+
                      ' & '.join(num(linha[o],0 if o=='f1' else 6) for o in exps)+r' \\')
    linhas += [r'\bottomrule\end{tabular}\end{table}',
               r'A matriz evidencia que os desempenhos devem ser comparados na mesma '
               r'composição. O mínimo de cada coluna da tabela das cinco rodadas pertence '
               r'a uma otimização independente; combinar esses três mínimos não define '
               r'uma receita realizável. A matriz cruzada conserva os três valores de cada alternativa.',
               r'\subsection{Referências para a próxima etapa}',
               r'Os extremos abaixo são calculados sobre os 15 vetores finais viáveis, '
               r'incluindo os valores de cada objetivo nas buscas dos outros dois. '
               r'São referências empíricas, não provas de ideal, nadir ou ótimo global.',
               r'\begin{table}[H]\centering\small',
               r'\caption{Extremos empíricos para normalização na Entrega 2}',
               r'\begin{tabular}{lrr}\toprule Objetivo & Mínimo observado & Máximo observado \\ \midrule']
    for j,obj in enumerate(exps):
        linhas.append('$f_'+str(j+1)+'$ & '+num(referencia['minimo'][j],0 if j==0 else 6)+
                      ' & '+num(referencia['maximo'][j],0 if j==0 else 6)+r' \\')
    linhas += [r'\bottomrule\end{tabular}\end{table}',
               r'Cada extremo aponta ao identificador da execução e ao hash do arquivo que contém sua composição '
               r'em \texttt{referencias\_tp1.json}. A próxima etapa aplicará a mesma transformação '
               r'min--max nos dois métodos. Novas soluções poderão extrapolar o intervalo '
               r'empírico; os valores não devem ser truncados.',
               r'\subsection{Análise da revisão}',
               r'O acompanhamento separado pode melhorar o retorno sem alterar a trajetória '
               r'estocástica por fitness: candidatos viáveis anteriormente descartados como '
               r'incumbentes agora continuam disponíveis. Por isso, diferenças em relação '
               r'ao log histórico não são tratadas como erro de reprodução. A disponibilidade '
               r'das 15 composições permite conferir cada uma das alegações de viabilidade.']
    for obj in exps:
        exp=exps[obj]
        cv=exp['desvio']/exp['media']*100
        linhas.append('$f_'+obj[1]+'$: mínimo '+num(exp['minimo'],0 if obj=='f1' else 6)+
                      ', máximo '+num(exp['maximo'],0 if obj=='f1' else 6)+
                      r', coeficiente de variação amostral de '+num(cv,4)+r'\%.')
    linhas += [r'Com cinco sementes, essa comparação é descritiva e não comprova '
               r'superioridade estatística, otimalidade ou cobertura do espaço de soluções.',
               r'\section{Conclusão}',
               r'A base mono-objetivo foi corrigida para separar fitness, qualidade e retorno '
               r'viável. As três funções, a representação por caminhões, N1/N2/N3 e o fluxo '
               r'de busca foram preservados. Todas as 15 soluções desta campanha passaram '
               r'pela validação individual e pela auditoria independente. Os registros, '
               r'as figuras e os extremos empíricos rastreáveis sustentam a implementação '
               r'posterior de soma ponderada e $\varepsilon$-restrito; estes métodos ainda '
               r'não fazem parte dos resultados apresentados nesta revisão.']
    (d/'resultados_tp1.tex').write_text('\n\n'.join(linhas)+'\n', encoding='utf-8')
