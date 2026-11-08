"""Gera as projeções dos objetivos e a figura da receita recomendada no TP3."""

import argparse
import csv
import json
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator


OBJETIVOS = ("custo_rs", "desvio_sio2_pp2", "desvio_al2o3_pp2")
EIXOS = ("Custo (R$ milhões)", "Desvio quadrático de SiO₂ (p.p.²)",
         "Desvio quadrático de Al₂O₃ (p.p.²)")
AZUL = "#17676C"
VERMELHO = "#BD4C29"
TEXTO = "#20343C"


def carregar_json(caminho):
    return json.loads(caminho.read_text(encoding="utf-8-sig"))


def selecionar_ids(resumo, recomendada, comparacao):
    if recomendada is None:
        vencedoras = {
            id_
            for ids in resumo["vencedoras_base"].values()
            for id_ in ids
        }
        if len(vencedoras) != 1:
            raise ValueError("O cenário-base não tem uma vencedora única. Informe --recomendada.")
        recomendada = vencedoras.pop()

    if comparacao is None:
        for cenario in resumo["cenarios"]:
            if cenario["cenario"] == "peso_custo_40":
                vencedoras = cenario["metodos"]["promethee_ii"]["vencedoras"]
                if len(vencedoras) == 1:
                    comparacao = vencedoras[0]["id"]
                break
    return recomendada, comparacao if comparacao != recomendada else None


def salvar(figura, pasta, nome):
    # Canvas não interativo para usar o módulo pela main, inclusive sem janela.
    FigureCanvasAgg(figura)
    caminhos = [pasta / f"{nome}.{extensao}" for extensao in ("png", "pdf")]
    for caminho in caminhos:
        figura.savefig(caminho, dpi=200, facecolor="white")
    return caminhos


def projetar(alternativas, recomendada, comparacao):
    figura = Figure(figsize=(13.6, 4.65), layout="constrained")
    figura.suptitle("Compromissos entre custo e qualidade", fontsize=18,
                    fontweight="bold", color=TEXTO)
    paineis = figura.subplots(1, 3)
    dados = {}
    for linha in alternativas:
        custo, silica, alumina = (float(linha[c]) for c in OBJETIVOS)
        dados[linha["id"]] = (custo / 1_000_000, silica, alumina)
    grupos = [
        ("Demais candidatas do TP2", "#A7B4BE", 0.30,
         [dados[r["id"]] for r in alternativas if r["pareto_4d"].lower() == "false"]),
        ("Não dominadas em 4 critérios", "#529493", 0.45,
         [dados[r["id"]] for r in alternativas if r["pareto_4d"].lower() == "true"]),
    ]
    custo_recomendada = f"{dados[recomendada][0]:.2f}".replace(".", ",")
    destaques = [(recomendada, f"Recomendada (R$ {custo_recomendada} mi)", AZUL, "*", 245)]
    if comparacao:
        custo_comparacao = f"{dados[comparacao][0]:.2f}".replace(".", ",")
        destaques.append((comparacao, f"Comparação (R$ {custo_comparacao} mi)", VERMELHO, "D", 85))

    for painel, (x, y) in zip(paineis, ((0, 1), (0, 2), (1, 2))):
        for legenda, cor, alpha, pontos in grupos:
            if pontos:
                painel.scatter([p[x] for p in pontos], [p[y] for p in pontos],
                               s=13, alpha=alpha, color=cor, linewidths=0, label=legenda)
        for id_, legenda, cor, marcador, tamanho in destaques:
            ponto = dados[id_]
            painel.scatter(ponto[x], ponto[y], s=tamanho, marker=marcador, color=cor,
                           edgecolor="white", linewidth=1, label=legenda, zorder=5)
        painel.set_xlabel(EIXOS[x], color=TEXTO)
        painel.set_ylabel(EIXOS[y], color=TEXTO)
        painel.set_axisbelow(True)
        painel.grid(color="#E5ECEE", linewidth=0.8)
        painel.spines[["top", "right"]].set_visible(False)
        painel.tick_params(length=3, colors=TEXTO)
        for eixo in (painel.xaxis, painel.yaxis):
            eixo.set_major_locator(MaxNLocator(nbins=5))
            eixo.set_major_formatter(FuncFormatter(lambda valor, _: f"{valor:g}".replace(".", ",")))
    handles, labels = paineis[0].get_legend_handles_labels()
    figura.legend(handles, labels, loc="outside lower center", ncol=len(labels),
                  frameon=False, fontsize=10, labelcolor=TEXTO)
    return figura


def composicao(alternativa):
    receitas = [alternativa["caminhoes_por_pilha"][str(i)] for i in range(1, 11)]
    minerios = sorted({m for receita in receitas for m in receita}, key=lambda m: int(m[1:]))
    contagens = [[receita.get(m, 0) for receita in receitas] for m in minerios]
    maior = max(max(linha) for linha in contagens)
    figura = Figure(figsize=(10.7, 2.7 + 0.25 * len(minerios)), layout="constrained")
    painel = figura.subplots()
    figura.suptitle(f"Receita recomendada · {alternativa['id']}", fontsize=18,
                    fontweight="bold", color=TEXTO)
    custo = f"{alternativa['custo_rs'] / 1_000_000:.2f}".replace(".", ",")
    variacao = f"{100 * alternativa['variacao_receita']:.2f}".replace(".", ",")
    painel.set_title(f"R$ {custo} milhões   |   Variação de receita: {variacao}%",
                     color=TEXTO, fontsize=11, pad=33)
    mapa = painel.imshow(contagens, vmin=0, vmax=maior, aspect="auto", cmap="GnBu")
    for y, linha in enumerate(contagens):
        for x, valor in enumerate(linha):
            if valor:
                painel.text(x, y, str(valor), ha="center", va="center", fontsize=9,
                            color="white" if valor / maior >= 0.68 else TEXTO)
    painel.set_xticks(range(10), [
        f"P{i}\n{2 * sum(receita.values())} kt"
        for i, receita in enumerate(receitas, start=1)
    ])
    painel.set_yticks(range(len(minerios)), minerios)
    painel.set_xlabel("Pilha e massa total", labelpad=9, color=TEXTO)
    painel.set_ylabel("Minério", labelpad=9, color=TEXTO)
    painel.set_xticks([x - 0.5 for x in range(1, 10)], minor=True)
    painel.set_yticks([y - 0.5 for y in range(1, len(minerios))], minor=True)
    painel.grid(which="minor", color="white", linewidth=0.8)
    painel.axvline(4.5, color=TEXTO, linewidth=1.7)
    for x, nome in ((0.25, "Sinter 1"), (0.75, "Sinter 2")):
        painel.text(x, 1.015, nome, transform=painel.transAxes, ha="center",
                    va="bottom", color=TEXTO, fontweight="bold")
    painel.tick_params(which="both", length=0, colors=TEXTO)
    painel.spines[:].set_visible(False)
    escala = figura.colorbar(mapa, ax=painel, shrink=0.82, pad=0.025,
                            ticks=MaxNLocator(integer=True))
    escala.set_label("Caminhões de 2 kt", color=TEXTO)
    escala.outline.set_visible(False)
    return figura


def gerar_figuras(pasta_resultados, destino=None, *, recomendada=None, comparacao=None):
    """Lê as saídas do TP3 e retorna os caminhos das quatro figuras exportadas."""
    pasta = Path(pasta_resultados)
    destino = pasta / "figuras" if destino is None else Path(destino)
    resumo = carregar_json(pasta / "resumo_sensibilidade.json")
    recomendada, comparacao = selecionar_ids(resumo, recomendada, comparacao)
    with (pasta / "alternativas.csv").open(encoding="utf-8-sig", newline="") as arquivo:
        alternativas = list(csv.DictReader(arquivo))
    ids = {linha["id"] for linha in alternativas}
    for id_ in (recomendada, comparacao):
        if id_ is not None and id_ not in ids:
            raise ValueError(f"Composição {id_!r} ausente em alternativas.csv.")
    registros = carregar_json(pasta / "alternativas.json")
    receita = next((linha for linha in registros if linha["id"] == recomendada), None)
    if receita is None:
        raise ValueError(f"Composição {recomendada!r} ausente em alternativas.json.")
    destino.mkdir(parents=True, exist_ok=True)
    projecoes = salvar(projetar(alternativas, recomendada, comparacao), destino, "projecoes_objetivos")
    receita_plot = salvar(composicao(receita), destino, "composicao_pilhas")
    return [*projecoes, *receita_plot]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pasta_resultados", type=Path)
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--recomendada", help="ID da solução recomendada pelo grupo")
    parser.add_argument("--comparacao", help="ID de uma solução adicional para as projeções")
    args = parser.parse_args()
    try:
        caminhos = gerar_figuras(args.pasta_resultados, args.saida,
                                 recomendada=args.recomendada, comparacao=args.comparacao)
    except (OSError, ValueError, KeyError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    print(f"{len(caminhos)} arquivos de figura gerados em {caminhos[0].parent.resolve()}.")
