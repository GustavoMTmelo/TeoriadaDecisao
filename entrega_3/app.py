"""Painel de apoio à decisão da Entrega 3."""

import json
import os
import runpy
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


RAIZ = Path(__file__).resolve().parent
RESULTADOS = Path(os.environ.get("TP3_RESULTADOS", RAIZ / "results_tp3_oficial"))
CRITERIOS = {
    "custo_rs": "Custo (R$)",
    "desvio_sio2_pp2": "Desvio de SiO₂ (p.p.²)",
    "desvio_al2o3_pp2": "Desvio de Al₂O₃ (p.p.²)",
    "variacao_receita": "Variação da receita (%)",
}
METODOS = {"AHP": "ahp", "PROMETHEE II": "promethee_ii"}
PROJECOES = {
    "Custo × Sílica": ("custo_rs", "desvio_sio2_pp2"),
    "Custo × Alumina": ("custo_rs", "desvio_al2o3_pp2"),
    "Sílica × Alumina": ("desvio_sio2_pp2", "desvio_al2o3_pp2"),
}
ARQUIVOS = (
    "alternativas.csv", "alternativas.json", "ranking_ahp.csv",
    "ranking_promethee_ii.csv", "resumo_sensibilidade.json",
)


def numero(valor, decimais=2):
    return f"{valor:,.{decimais}f}".translate(str.maketrans(",.", ".,"))


def tabela_criterios(tabela):
    tabela = tabela.rename(columns={**CRITERIOS, "id": "Alternativa"})
    campo = CRITERIOS["variacao_receita"]
    tabela[campo] *= 100
    return tabela


@st.cache_data(show_spinner=False)
def carregar_resultados(pasta, versoes):
    # versoes invalida o cache se uma nova execução regenerar os arquivos.
    alternativas = pd.read_csv(pasta / "alternativas.csv", dtype={"id": str})
    alternativas = alternativas.set_index("id", verify_integrity=True)
    registros = json.loads((pasta / "alternativas.json").read_text(encoding="utf-8"))
    receitas = {r["id"]: r["caminhoes_por_pilha"] for r in registros}
    rankings = {
        metodo: pd.read_csv(pasta / f"ranking_{chave}.csv", dtype={"id": str})
        for metodo, chave in METODOS.items()
    }
    sensibilidade = json.loads((pasta / "resumo_sensibilidade.json").read_text(encoding="utf-8"))
    return alternativas, receitas, rankings, sensibilidade


def ids_base(sensibilidade):
    return sorted({id_ for grupo in sensibilidade["vencedoras_base"].values() for id_ in grupo})


def comparacao_custo(sensibilidade, referencia):
    for cenario in sensibilidade["cenarios"]:
        if cenario["cenario"] == "peso_custo_40":
            return [r["id"] for r in cenario["metodos"]["promethee_ii"]["vencedoras"]
                    if r["id"] not in referencia]
    return []


def formatar_id(id_, alternativas):
    return f"{id_} · R$ {numero(alternativas.at[id_, 'custo_rs'] / 1e6)} mi"


def grafico_projecao(x, y, destaques):
    def valores(tabela, criterio):
        return tabela[criterio] / 1e6 if criterio == "custo_rs" else tabela[criterio]

    def eixo(criterio):
        return "Custo (R$ milhões)" if criterio == "custo_rs" else CRITERIOS[criterio]

    figura = go.Figure()
    for grupo, tabela, cor in destaques:
        if tabela.empty:
            continue
        selecionada = grupo in {"Vencedora no cenário-base", "Em comparação"}
        figura.add_trace(go.Scattergl(
            x=valores(tabela, x), y=valores(tabela, y), text=tabela.index,
            mode="markers", name=grupo,
            marker={"color": cor, "size": 14 if selecionada else 6,
                    "opacity": 1 if selecionada else 0.48,
                    "symbol": "diamond" if selecionada else "circle"},
            hovertemplate="%{text}<br>%{x:.3f} × %{y:.3f}<extra>%{fullData.name}</extra>",
        ))
    figura.update_layout(
        xaxis_title=eixo(x), yaxis_title=eixo(y), height=500,
        margin={"t": 16, "b": 35, "l": 35, "r": 16},
        legend={"orientation": "h", "y": -0.22},
    )
    return figura


def explorar(alternativas, sensibilidade):
    st.header("Explorar alternativas")
    referencia = ids_base(sensibilidade)
    filtros, projecao = st.columns(2)
    apenas_frente = filtros.checkbox("Mostrar apenas a fronteira em quatro critérios", value=True)
    x, y = PROJECOES[projecao.selectbox("Projeção", list(PROJECOES))]
    comparadas = st.multiselect(
        "Comparar até cinco composições",
        alternativas.index.tolist(),
        default=comparacao_custo(sensibilidade, referencia)[:5],
        max_selections=5,
        format_func=lambda id_: formatar_id(id_, alternativas),
    )
    pontos = alternativas.loc[alternativas["pareto_4d"]] if apenas_frente else alternativas
    pontos = pontos.drop(index=referencia + comparadas, errors="ignore")
    destaques = [
        ("Demais candidatas", pontos.loc[~pontos["pareto_4d"]], "#A1AEB6"),
        ("Fronteira em quatro critérios", pontos.loc[pontos["pareto_4d"]], "#429495"),
        ("Em comparação", alternativas.loc[[id_ for id_ in comparadas if id_ not in referencia]], "#D46A35"),
        ("Vencedora no cenário-base", alternativas.loc[referencia], "#154C65"),
    ]
    st.plotly_chart(grafico_projecao(x, y, destaques))
    st.subheader("Valores das alternativas destacadas")
    ids = list(dict.fromkeys(referencia + comparadas))
    tabela = alternativas.loc[ids, list(CRITERIOS)].reset_index()
    st.dataframe(tabela_criterios(tabela), hide_index=True, width="stretch")


def nome_cenario(cenario):
    if cenario.startswith("peso_"):
        _, criterio, peso = cenario.split("_")
        nome = {"custo": "Custo", "silica": "Sílica", "alumina": "Alumina",
                "receita": "Uniformidade da receita", "qualidade": "Qualidade química"}[criterio]
        return f"{nome} com {peso}% do peso"
    return cenario.replace("_", " ").replace("silica", "sílica").capitalize()


def mostrar_rankings(rankings, sensibilidade):
    st.header("Rankings e sensibilidade")
    metodo = st.selectbox("Método", list(rankings))
    n = st.select_slider("Posições exibidas do cenário-base", [5, 10, 20, 50], value=10)
    ranking = rankings[metodo]
    st.dataframe(tabela_criterios(ranking.loc[ranking["posicao"] <= n].rename(
        columns={"posicao": "Posição", "prioridade_ahp": "Prioridade AHP",
                 "fluxo_positivo": "Fluxo positivo", "fluxo_negativo": "Fluxo negativo",
                 "fluxo_liquido": "Fluxo líquido"})), hide_index=True, width="stretch")
    st.subheader("Como as preferências mudam a decisão")
    cenarios = {r["cenario"]: r for r in sensibilidade["cenarios"]}
    nome = st.selectbox("Cenário de sensibilidade", list(cenarios), format_func=nome_cenario)
    cenario = cenarios[nome]
    pesos = cenario["pesos"]
    st.caption(" · ".join(f"{rotulo}: {numero(pesos[c] * 100, 0)}%"
                          for c, rotulo in zip(CRITERIOS, ("Custo", "Sílica", "Alumina", "Receita"))))
    linhas = []
    for titulo, chave in METODOS.items():
        resultado = cenario["metodos"][chave]
        posicoes = ", ".join(f"{id_} em {p}º" for id_, p in
                             resultado["posicoes_vencedoras_base"].items())
        for vencedora in resultado["vencedoras"]:
            linhas.append({"Método": titulo, "Posição da vencedora-base": posicoes,
                           **{k: vencedora[k] for k in ("id", *CRITERIOS)}})
    st.dataframe(tabela_criterios(pd.DataFrame(linhas)), hide_index=True, width="stretch")
    with st.expander("Limiar de indiferença e de preferência do PROMETHEE II"):
        limiares = pd.DataFrame.from_dict(cenario["limiares_unidades_originais"], orient="index")
        limiares.index = [CRITERIOS[c].replace(" (%)", " (p.p.)") for c in limiares.index]
        limiares.loc["Variação da receita (p.p.)"] *= 100
        st.dataframe(limiares.rename(columns={"q": "Indiferença (q)", "p": "Preferência (p)"}),
                     width="stretch")


@st.cache_data(show_spinner=False)
def ler_modelo(arquivo, versao):
    dados = runpy.run_path(str(arquivo))
    return {chave: dados[chave] for chave in ("minerios", "sinters", "pilhas", "CAPACIDADE_CAMINHAO_KT")}


def dados_pilhas(receita, modelo):
    linhas = []
    for id_, contagens in sorted(receita.items(), key=lambda r: int(r[0])):
        pilha = modelo["pilhas"][int(id_)]
        sinter = pilha["sinter"]
        regras = modelo["sinters"][sinter]
        total = sum(contagens.values())
        teores = {
            t: sum(n * modelo["minerios"][m][t] for m, n in contagens.items()) / total
            for t in ("fet", "sio2", "al2o3")
        }
        linhas.append({
            "Pilha": int(id_), "Sinter": sinter, "Massa (kt)": total * modelo["CAPACIDADE_CAMINHAO_KT"],
            "FeT (%)": teores["fet"], "SiO₂ (%)": teores["sio2"], "Al₂O₃ (%)": teores["al2o3"],
            "Alvo SiO₂ (%)": regras["sio2_alvo"], "Alvo Al₂O₃ (%)": regras["al2o3_alvo"],
            "Qualidade dentro dos limites": all(regras[f"{t}_min"] - 1e-9 <= teores[t]
                                                 <= regras[f"{t}_max"] + 1e-9
                                                 for t in ("sio2", "al2o3")),
        })
    return linhas


def mostrar_receita(alternativas, receitas, sensibilidade):
    st.header("Composição das pilhas")
    referencia = ids_base(sensibilidade)
    opcoes = list(dict.fromkeys(referencia + alternativas.index.tolist()))
    id_ = st.selectbox("Composição", opcoes, format_func=lambda i: formatar_id(i, alternativas))
    if id_ in referencia:
        st.caption("Vencedora de pelo menos um método no cenário-base, com os pesos e limiares registrados.")
    linha = alternativas.loc[id_]
    colunas = st.columns(4)
    metricas = [
        ("Custo", f"R$ {numero(linha['custo_rs'] / 1e6)} mi"),
        ("Desvio de SiO₂", f"{numero(linha['desvio_sio2_pp2'], 3)} p.p.²"),
        ("Desvio de Al₂O₃", f"{numero(linha['desvio_al2o3_pp2'], 3)} p.p.²"),
        ("Variação da receita", f"{numero(linha['variacao_receita'] * 100)}%"),
    ]
    for coluna, (rotulo, valor) in zip(colunas, metricas):
        coluna.metric(rotulo, valor)

    receita = receitas[id_]
    tabela = pd.DataFrame.from_dict(receita, orient="index").fillna(0).astype(int)
    tabela = tabela.reindex(index=sorted(tabela.index, key=int),
                            columns=sorted(tabela.columns, key=lambda m: int(m[1:])))
    valores = tabela.to_numpy().T
    figura = go.Figure(go.Heatmap(
        x=[f"P{i}" for i in tabela.index], y=tabela.columns, z=valores,
        colorscale=[[0, "#F1F7F5"], [1, "#70B6AE"]], colorbar={"title": "Caminhões"},
        text=[[str(n) if n else "" for n in linha] for linha in valores],
        texttemplate="%{text}", textfont={"color": "#183338"},
        hovertemplate="%{x} · %{y}: %{z} caminhões<extra></extra>",
    ))
    figura.update_layout(height=500, margin={"t": 12, "b": 28, "l": 20, "r": 20})
    figura.update_yaxes(autorange="reversed")
    st.subheader("Quantidade de cada minério por pilha")
    st.plotly_chart(figura)
    st.caption("P1–P5 alimentam o Sinter 1. P6–P10 alimentam o Sinter 2.")

    st.subheader("Massa, teores e alvos por pilha")
    opcoes_modelo = [RAIZ / "sol_inicial.py", RAIZ.parent / "sol_inicial.py"]
    modelo = next((p for p in opcoes_modelo if p.is_file()), None)
    if modelo is None:
        st.warning("Coloque o sol_inicial.py do projeto ao lado de app.py para exibir os teores.")
        return
    teores = pd.DataFrame(dados_pilhas(receita, ler_modelo(modelo, modelo.stat().st_mtime_ns)))
    st.dataframe(teores.round(3), hide_index=True, width="stretch")


def main():
    st.set_page_config(page_title="Decisão de pilhas | TP3", layout="wide")
    st.title("Decisão multicritério de pilhas")
    st.caption("Case Cassotis · Teoria da Decisão · UFMG")
    try:
        versoes = tuple((RESULTADOS / nome).stat().st_mtime_ns for nome in ARQUIVOS)
        alternativas, receitas, rankings, sensibilidade = carregar_resultados(RESULTADOS, versoes)
    except (OSError, ValueError) as erro:
        st.error(f"Não foi possível carregar os resultados de {RESULTADOS.name}. {erro}")
        st.stop()
    st.sidebar.caption(f"{numero(len(alternativas), 0)} alternativas na campanha")
    st.sidebar.caption(f"{numero(int(alternativas['pareto_4d'].sum()), 0)} na fronteira em quatro critérios")
    pagina = st.sidebar.radio("Navegação", ("Alternativas", "Rankings", "Composição"))
    if pagina == "Alternativas":
        explorar(alternativas, sensibilidade)
    elif pagina == "Rankings":
        mostrar_rankings(rankings, sensibilidade)
    else:
        mostrar_receita(alternativas, receitas, sensibilidade)


if __name__ == "__main__":
    main()
