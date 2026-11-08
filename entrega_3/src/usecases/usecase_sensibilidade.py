"""Avalia a sensibilidade dos rankings AHP e PROMETHEE II."""

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from .usecase_rankings import (
    CRITERIOS,
    LIMIARES_PILOTO,
    MATRIZ_NEUTRA,
    gerar_rankings,
    pesos_ahp,
)


METODOS = {
    "ahp": ("ranking_ahp.csv", "prioridade_ahp"),
    "promethee_ii": ("ranking_promethee_ii.csv", "fluxo_liquido"),
}
NOMES_CRITERIOS = ("custo", "silica", "alumina", "receita")
LIMIARES_TESTE = {
    "menores": (0.02, 0.15),
    "maiores": (0.10, 0.40),
}


@dataclass(frozen=True)
class Cenario:
    nome: str
    grupo: str
    matriz: tuple
    limiares: tuple


def redistribuir_pesos(pesos_base, indices, participacao):
    """Fixa a participação do grupo e preserva as razões dentro de cada grupo."""
    peso_grupo = sum(peso for j, peso in enumerate(pesos_base) if j in indices)
    peso_restante = sum(peso for j, peso in enumerate(pesos_base) if j not in indices)
    return tuple(
        peso * participacao / peso_grupo if j in indices
        else peso * (1 - participacao) / peso_restante
        for j, peso in enumerate(pesos_base)
    )


def matriz_por_pesos(pesos):
    """Constrói uma matriz recíproca consistente para o cenário simulado."""
    return tuple(tuple(a / b for b in pesos) for a in pesos)


def criar_cenarios(matriz_base, limiares_base):
    matriz_base = tuple(tuple(linha) for linha in matriz_base)
    limiares_base = tuple(tuple(par) for par in limiares_base)
    pesos_base, _ = pesos_ahp(matriz_base)
    yield Cenario("base", "base", matriz_base, limiares_base)

    for indice, criterio in enumerate(NOMES_CRITERIOS):
        for percentual in (40, 55):
            pesos = redistribuir_pesos(pesos_base, {indice}, percentual / 100)
            yield Cenario(f"peso_{criterio}_{percentual}", "pesos",
                          matriz_por_pesos(pesos), limiares_base)
    pesos = redistribuir_pesos(pesos_base, {1, 2}, 0.70)
    yield Cenario("peso_qualidade_70", "pesos", matriz_por_pesos(pesos), limiares_base)

    for nome, par in LIMIARES_TESTE.items():
        yield Cenario(f"limiares_{nome}_todos", "limiares",
                      matriz_base, (par,) * len(CRITERIOS))
        for indice, criterio in enumerate(NOMES_CRITERIOS):
            limiares = list(limiares_base)
            limiares[indice] = par
            yield Cenario(f"limiares_{nome}_{criterio}", "limiares",
                          matriz_base, tuple(limiares))


def ler_resultado_ranking(caminho, campo_pontuacao, referencias):
    vencedoras = []
    posicoes = {}
    referencias = set(referencias)
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            id_ = linha["id"]
            posicao = int(linha["posicao"])
            if posicao == 1:
                vencedoras.append({
                    "id": id_,
                    **{criterio: float(linha[criterio]) for criterio in CRITERIOS},
                    "pontuacao": float(linha[campo_pontuacao]),
                })
            if id_ in referencias:
                posicoes[id_] = posicao
    return vencedoras, posicoes


def gerar_sensibilidade(pareto_csv, destino=None, *, matriz_base=MATRIZ_NEUTRA,
                        limiares_base=LIMIARES_PILOTO):
    """Gera uma tabela por cenário e método, mantendo todos os empates no topo."""
    caminho = Path(pareto_csv)
    destino = caminho.parent if destino is None else Path(destino)
    csv_saida = destino / "sensibilidade_cenarios.csv"
    json_saida = destino / "resumo_sensibilidade.json"
    if caminho.resolve() in {csv_saida.resolve(), json_saida.resolve()}:
        raise ValueError("A saída da análise não pode sobrescrever a entrada.")

    referencias = {metodo: [] for metodo in METODOS}
    resultados = []
    linhas = []
    destino.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".tp3_sensibilidade_", dir=destino) as temporaria:
        temporaria = Path(temporaria)
        for cenario in criar_cenarios(matriz_base, limiares_base):
            ranking = gerar_rankings(
                caminho, temporaria, matriz_ahp=cenario.matriz, limiares=cenario.limiares,
            )
            resultado = {
                "cenario": cenario.nome,
                "grupo": cenario.grupo,
                "pesos": ranking["pesos"],
                "razao_consistencia_ahp": ranking["razao_consistencia_ahp"],
                "limiares_normalizados": ranking["limiares_promethee_q_p_normalizados"],
                "limiares_unidades_originais": {
                    c: {"q": faixa["q_original"], "p": faixa["p_original"]}
                    for c, faixa in ranking["faixas_observadas"].items()
                },
                "metodos": {},
            }
            for metodo, (nome_arquivo, campo) in METODOS.items():
                vencedoras, posicoes = ler_resultado_ranking(
                    temporaria / nome_arquivo, campo, referencias[metodo],
                )
                if cenario.grupo == "base":
                    referencias[metodo] = [v["id"] for v in vencedoras]
                    posicoes = dict.fromkeys(referencias[metodo], 1)
                resultado["metodos"][metodo] = {
                    "vencedoras": vencedoras,
                    "posicoes_vencedoras_base": posicoes,
                    "alguma_vencedora_base_no_topo": 1 in posicoes.values(),
                }
                for vencedora in vencedoras:
                    linhas.append({
                        "cenario": cenario.nome,
                        "grupo": cenario.grupo,
                        "metodo": metodo,
                        "id_vencedora": vencedora["id"],
                        **{c: vencedora[c] for c in CRITERIOS},
                        "pontuacao": vencedora["pontuacao"],
                        "total_empatadas_no_topo": len(vencedoras),
                        "posicoes_vencedoras_base": json.dumps(posicoes, sort_keys=True),
                        **{f"peso_{c}": ranking["pesos"][c] for c in CRITERIOS},
                    })
            resultados.append(resultado)

    resumo = {
        "entrada": str(caminho),
        "total_alternativas": ranking["total_alternativas"],
        "total_cenarios": len(resultados),
        "vencedoras_base": referencias,
        "estabilidade_sem_cenario_base": {
            metodo: {
                grupo: {
                    "total": sum(r["grupo"] == grupo for r in resultados),
                    "com_vencedora_base_no_topo": sum(
                        r["grupo"] == grupo
                        and r["metodos"][metodo]["alguma_vencedora_base_no_topo"]
                        for r in resultados
                    ),
                }
                for grupo in ("pesos", "limiares")
            }
            for metodo in METODOS
        },
        "cenarios": resultados,
    }
    with csv_saida.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    json_saida.write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return resumo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pareto_csv", type=Path)
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    try:
        resultado = gerar_sensibilidade(args.pareto_csv, args.saida)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    print(f"Análise gerada para {resultado['total_cenarios']} cenários "
          f"e {resultado['total_alternativas']} alternativas.")
