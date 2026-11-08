"""Gera a base de decisão da Entrega 3 a partir dos arquivos Pareto do TP2."""

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from src.usecases.usecase_rankings import gerar_rankings
from src.usecases.usecase_sensibilidade import gerar_sensibilidade
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
ARQUIVOS_TP2 = ("ponderada_uniao.json", "epsilon_uniao.json")
GRUPOS = (range(1, 6), range(6, 11))
CRITERIOS = (
    "custo_rs",
    "desvio_sio2_pp2",
    "desvio_al2o3_pp2",
    "variacao_receita",
)


@dataclass
class Alternativa:
    id: str
    composicao: dict
    objetivos: tuple
    variacoes_sinter: tuple
    fontes: list = field(default_factory=list)

    @property
    def criterios(self):
        return (*self.objetivos, sum(self.variacoes_sinter) / len(GRUPOS))


def variacao_grupo(receitas):
    """Distância média de variação total em relação à receita média."""
    totais = [sum(receita.values()) for receita in receitas]
    escala = math.lcm(*totais)
    proporcoes = [
        {minerio: quantidade * (escala // total) for minerio, quantidade in receita.items()}
        for receita, total in zip(receitas, totais)
    ]
    soma = Counter()
    for proporcao in proporcoes:
        soma.update(proporcao)
    n = len(receitas)
    desvios = sum(
        abs(n * proporcao.get(minerio, 0) - total)
        for proporcao in proporcoes
        for minerio, total in soma.items()
    )
    return Fraction(desvios, 2 * n * n * escala)


def ler_alternativas(arquivos):
    por_composicao = {}
    for arquivo in arquivos:
        registros = json.loads(arquivo.read_text(encoding="utf-8-sig"))
        if not isinstance(registros, list):
            raise ValueError(f"{arquivo}: esperado um JSON com uma lista de alternativas.")
        for indice, registro in enumerate(registros, start=1):
            try:
                solucao = registro["solucao"]
                avaliacao = registro["avaliacao"]
                objetivos = tuple(avaliacao["objetivos"])
                if len(objetivos) != 3 or not all(math.isfinite(v) for v in objetivos):
                    raise ValueError("esperados três objetivos numéricos e finitos")
                if not all(avaliacao[campo] is True for campo in
                           ("estrutura_ok", "qualidade_ok", "epsilon_ok")):
                    raise ValueError("o registro não está marcado como viável")
                if set(solucao) != {str(i) for i in range(1, 11)}:
                    raise ValueError("esperadas as pilhas 1 a 10")
                for i in range(1, 11):
                    caminhoes = solucao[str(i)]
                    if (not isinstance(caminhoes, list) or len(caminhoes) != i + 9
                            or not all(isinstance(m, str) and m for m in caminhoes)):
                        raise ValueError(f"lista de caminhões inválida na pilha {i}")
                composicao = {str(i): Counter(solucao[str(i)]) for i in range(1, 11)}
                origens = registro["origens"]
                if not isinstance(origens, list) or not origens:
                    raise ValueError("esperada uma lista de origens")
                if not all(isinstance(origem["metodo"], str) and origem["metodo"]
                           for origem in origens):
                    raise ValueError("método ausente em uma das origens")
                chave = json.dumps(list(composicao.values()), sort_keys=True, separators=(",", ":"))
                alternativa = por_composicao.get(chave)
                if alternativa is None:
                    variacoes = tuple(
                        variacao_grupo([composicao[str(i)] for i in grupo])
                        for grupo in GRUPOS
                    )
                    id_ = hashlib.sha256(chave.encode("utf-8")).hexdigest()[:16]
                    alternativa = Alternativa(id_, composicao, objetivos, variacoes)
                    por_composicao[chave] = alternativa
                elif alternativa.objetivos != objetivos:
                    raise ValueError("a mesma composição tem valores de objetivos divergentes")
                alternativa.fontes.append({
                    "arquivo": arquivo.name,
                    "registro": indice,
                    "origens": origens,
                })
            except (KeyError, TypeError, ValueError) as erro:
                raise ValueError(f"{arquivo}, registro {indice}: {erro}") from erro

    alternativas = sorted(por_composicao.values(), key=lambda alternativa: alternativa.id)
    if not alternativas:
        raise ValueError("Nenhuma alternativa encontrada nos arquivos de entrada.")
    if len({alternativa.id for alternativa in alternativas}) != len(alternativas):
        raise ValueError("Colisão nos identificadores das alternativas.")
    return alternativas


def frente_pareto(alternativas):
    """Em ordem lexicográfica, apenas vetores anteriores podem dominar."""
    frente = []
    for vetor, id_ in sorted((a.criterios, a.id) for a in alternativas):
        _, silica, alumina, variacao = vetor
        dominada = any(
            anterior[1] <= silica and anterior[2] <= alumina
            and anterior[3] <= variacao and anterior != vetor
            for anterior, _ in frente
        )
        if not dominada:
            frente.append((vetor, id_))
    return {id_ for _, id_ in frente}


def exportar(alternativas, frente, destino):
    linhas = []
    registros = []
    for alternativa in alternativas:
        metodos = sorted({
            origem["metodo"]
            for fonte in alternativa.fontes
            for origem in fonte["origens"]
        })
        sinter_1, sinter_2 = alternativa.variacoes_sinter
        custo, silica, alumina, variacao = alternativa.criterios
        linha = {
            "id": alternativa.id,
            "metodos_tp2": "|".join(metodos),
            "custo_rs": custo,
            "desvio_sio2_pp2": silica,
            "desvio_al2o3_pp2": alumina,
            "variacao_receita": float(variacao),
            "variacao_sinter_1": float(sinter_1),
            "variacao_sinter_2": float(sinter_2),
            "pareto_4d": alternativa.id in frente,
        }
        linhas.append(linha)
        registros.append({
            **linha,
            "caminhoes_por_pilha": alternativa.composicao,
            "fontes": alternativa.fontes,
        })

    destino.mkdir(parents=True, exist_ok=True)
    tabelas = {
        "alternativas.csv": linhas,
        "pareto_4d.csv": [linha for linha in linhas if linha["pareto_4d"]],
    }
    for nome, tabela in tabelas.items():
        with (destino / nome).open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
            escritor.writeheader()
            escritor.writerows(tabela)
    with (destino / "alternativas.json").open("w", encoding="utf-8") as arquivo:
        json.dump(registros, arquivo, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        arquivo.write("\n")

    resumo = {
        "total_alternativas": len(alternativas),
        "total_pareto_4d": len(frente),
        "minimos_por_criterio": {},
    }
    for indice, criterio in enumerate(CRITERIOS):
        minimo = min(a.criterios[indice] for a in alternativas)
        resumo["minimos_por_criterio"][criterio] = {
            "valor": float(minimo),
            "ids": [a.id for a in alternativas if a.criterios[indice] == minimo],
        }
    with (destino / "resumo.json").open("w", encoding="utf-8") as arquivo:
        json.dump(resumo, arquivo, ensure_ascii=False, indent=2, allow_nan=False)
        arquivo.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=RAIZ / "results_tp2")
    parser.add_argument("--saida", type=Path, default=RAIZ / "results_tp3")
    args = parser.parse_args()

    if args.entrada.is_file():
        arquivos = [args.entrada]
    else:
        pasta = args.entrada
        if not (pasta / ARQUIVOS_TP2[0]).is_file() and (pasta / "pareto").is_dir():
            pasta = pasta / "pareto"
        arquivos = [pasta / nome for nome in ARQUIVOS_TP2]
    if args.saida.resolve() / "alternativas.json" in [p.resolve() for p in arquivos]:
        parser.error("Escolha uma pasta de saída que não sobrescreva o JSON de entrada.")
    try:
        alternativas = ler_alternativas(arquivos)
        frente = frente_pareto(alternativas)
        exportar(alternativas, frente, args.saida)
        gerar_rankings(args.saida / "pareto_4d.csv", args.saida)
        gerar_sensibilidade(args.saida / "pareto_4d.csv", args.saida)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    print(f"{len(alternativas)} alternativas, {len(frente)} não dominadas em quatro critérios.")
    print(f"Arquivos gerados em: {args.saida.resolve()}")


if __name__ == "__main__":
    main()
