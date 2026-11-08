"""Gera rankings AHP e PROMETHEE II a partir de pareto_4d.csv."""

import argparse
import csv
import json
import math
from bisect import bisect_left, bisect_right
from itertools import accumulate
from pathlib import Path


CRITERIOS = (
    "custo_rs",
    "desvio_sio2_pp2",
    "desvio_al2o3_pp2",
    "variacao_receita",
)
MATRIZ_NEUTRA = ((1, 1, 1, 1),) * 4
LIMIARES_PILOTO = ((0.05, 0.25),) * 4
# Razão entre o melhor e o pior desempenho observado em cada critério.
RAZAO_EXTREMOS_AHP = 5.0


def ler_alternativas(caminho):
    alternativas = []
    ids = set()
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        obrigatorios = {"id", *CRITERIOS}
        if not obrigatorios.issubset(leitor.fieldnames or ()):
            raise ValueError(f"{caminho}: esperadas as colunas {', '.join(sorted(obrigatorios))}.")
        for linha in leitor:
            id_ = (linha["id"] or "").strip()
            if not id_ or id_ in ids:
                raise ValueError(f"{caminho}, linha {leitor.line_num}: ID vazio ou duplicado.")
            try:
                valores = tuple(float(linha[c]) for c in CRITERIOS)
            except (TypeError, ValueError) as erro:
                raise ValueError(f"{caminho}, linha {leitor.line_num}: valor inválido.") from erro
            if not all(math.isfinite(valor) and valor >= 0 for valor in valores):
                raise ValueError(f"{caminho}, linha {leitor.line_num}: valor negativo ou não finito.")
            ids.add(id_)
            alternativas.append((id_, valores))
    if not alternativas:
        raise ValueError(f"{caminho}: nenhuma alternativa encontrada.")
    return alternativas


def pesos_ahp(matriz):
    n = len(CRITERIOS)
    if len(matriz) != n or any(len(linha) != n for linha in matriz):
        raise ValueError("A matriz AHP deve ter quatro linhas e quatro colunas.")
    if not all(math.isfinite(v) and v > 0 for linha in matriz for v in linha):
        raise ValueError("A matriz AHP deve conter valores positivos e finitos.")
    for i in range(n):
        if not math.isclose(matriz[i][i], 1, abs_tol=1e-9):
            raise ValueError("A diagonal da matriz AHP deve ser 1.")
        for j in range(i + 1, n):
            if not math.isclose(matriz[i][j] * matriz[j][i], 1, rel_tol=1e-6):
                raise ValueError("A matriz AHP deve ser recíproca.")

    # Método da potência para obter o autovetor principal.
    pesos = [1 / n] * n
    for _ in range(1000):
        produto = [sum(a * b for a, b in zip(linha, pesos)) for linha in matriz]
        total = sum(produto)
        novos = [v / total for v in produto]
        if max(abs(a - b) for a, b in zip(novos, pesos)) < 1e-13:
            pesos = novos
            break
        pesos = novos
    else:
        raise ValueError("O cálculo dos pesos AHP não convergiu.")

    lambda_max = sum(sum(a * b for a, b in zip(linha, pesos)) for linha in matriz)
    # Índice aleatório de Saaty para quatro critérios.
    cr = max(0.0, (lambda_max - n) / (n - 1)) / 0.90
    if cr > 0.10:
        raise ValueError(f"Matriz AHP inconsistente (CR={cr:.3f}). Revise os julgamentos.")
    return pesos, cr


def fluxo_positivo(valores, q, p):
    """Para cada x, soma P(y - x) sobre as demais alternativas."""
    ordenados = sorted(valores)
    prefixos = list(accumulate(ordenados, initial=0.0))
    n = len(ordenados)
    if n == 1:
        return [0.0]
    fluxos = []
    for x in valores:
        inicio = bisect_right(ordenados, x + q)
        fim = bisect_left(ordenados, x + p, lo=inicio)
        # A faixa intermediária tem preferência linear. Após p, vale 1.
        parcial = (prefixos[fim] - prefixos[inicio] - (fim - inicio) * (x + q)) / (p - q)
        parcial = max(0.0, min(parcial, fim - inicio))
        fluxos.append((n - fim + parcial) / (n - 1))
    return fluxos


def classificar(linhas, campo):
    ordenadas = sorted(linhas, key=lambda linha: (-linha[campo], linha["id"]))
    anterior = None
    posicao = 0
    for indice, linha in enumerate(ordenadas, start=1):
        if linha[campo] != anterior:
            posicao = indice
        linha["posicao"] = posicao
        anterior = linha[campo]
    return ordenadas


def escrever_csv(caminho, linhas):
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        campos = ["posicao"] + [campo for campo in linhas[0] if campo != "posicao"]
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)


def gerar_rankings(pareto_csv, destino=None, *, matriz_ahp=MATRIZ_NEUTRA,
                   limiares=LIMIARES_PILOTO):
    """Salva os dois rankings e retorna seus primeiros colocados e parâmetros.

    A ordem das linhas e colunas da matriz AHP segue CRITERIOS. Cada par (q, p)
    em limiares usa a escala de 0 a 1 da amplitude observada do critério.
    Os pesos derivados da matriz são compartilhados entre os métodos.
    """
    caminho = Path(pareto_csv)
    destino = caminho.parent if destino is None else Path(destino)
    pesos, cr = pesos_ahp(matriz_ahp)
    if len(limiares) != len(CRITERIOS) or not all(0 <= q < p <= 1 for q, p in limiares):
        raise ValueError("Informe quatro pares (q, p), com 0 <= q < p <= 1.")
    alternativas = ler_alternativas(caminho)
    n = len(alternativas)
    ahp = [0.0] * n
    positivos = [0.0] * n
    negativos = [0.0] * n
    faixas = {}

    for j, criterio in enumerate(CRITERIOS):
        valores = [valores[j] for _, valores in alternativas]
        minimo, maximo = min(valores), max(valores)
        amplitude = maximo - minimo
        q, p = limiares[j]
        faixas[criterio] = {
            "minimo": minimo, "maximo": maximo,
            "q_original": q * amplitude, "p_original": p * amplitude,
        }
        normalizados = [(valor - minimo) / amplitude for valor in valores] if amplitude else [0.0] * n
        for i, valor in enumerate(normalizados):
            # Para a escala s_i = 5**(-x_i), a comparação s_i/s_k produz
            # uma matriz recíproca consistente. Seu autovetor, dividido pela
            # melhor prioridade (modo ideal), é a própria escala s.
            ahp[i] += pesos[j] * RAZAO_EXTREMOS_AHP ** (-valor)
        if amplitude:
            favor = fluxo_positivo(normalizados, q, p)
            contra = fluxo_positivo([-valor for valor in normalizados], q, p)
            for i in range(n):
                positivos[i] += pesos[j] * favor[i]
                negativos[i] += pesos[j] * contra[i]

    linhas_ahp = []
    linhas_promethee = []
    for i, (id_, valores) in enumerate(alternativas):
        dados = {"id": id_, **dict(zip(CRITERIOS, valores))}
        linhas_ahp.append({**dados, "prioridade_ahp": round(ahp[i], 12)})
        linhas_promethee.append({
            **dados,
            "fluxo_positivo": positivos[i],
            "fluxo_negativo": negativos[i],
            "fluxo_liquido": round(positivos[i] - negativos[i], 12),
        })
    ranking_ahp = classificar(linhas_ahp, "prioridade_ahp")
    ranking_promethee = classificar(linhas_promethee, "fluxo_liquido")
    resumo = {
        "entrada": str(caminho),
        "total_alternativas": n,
        "criterios": CRITERIOS,
        "pesos": dict(zip(CRITERIOS, pesos)),
        "matriz_ahp": matriz_ahp,
        "razao_consistencia_ahp": cr,
        "ahp_escala_alternativas": "modo ideal, prioridade local = 5 ** (-valor_normalizado)",
        "razao_extremos_ahp": RAZAO_EXTREMOS_AHP,
        "limiares_promethee_q_p_normalizados": dict(zip(CRITERIOS, limiares)),
        "faixas_observadas": faixas,
        "primeiros_ahp": [linha["id"] for linha in ranking_ahp if linha["posicao"] == 1],
        "primeiros_promethee_ii": [
            linha["id"] for linha in ranking_promethee if linha["posicao"] == 1
        ],
    }
    saidas = [destino / nome for nome in (
        "ranking_ahp.csv", "ranking_promethee_ii.csv", "resumo_rankings.json",
    )]
    if caminho.resolve() in {saida.resolve() for saida in saidas}:
        raise ValueError("A saída dos rankings não pode sobrescrever a entrada.")
    destino.mkdir(parents=True, exist_ok=True)
    escrever_csv(saidas[0], ranking_ahp)
    escrever_csv(saidas[1], ranking_promethee)
    saidas[2].write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pareto_csv", type=Path)
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    try:
        resultado = gerar_rankings(args.pareto_csv, args.saida)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    print(f"Rankings gerados para {resultado['total_alternativas']} alternativas.")
