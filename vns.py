"""GVNS mono-objetivo para composição de pilhas de minério.

Algoritmo: General Variable Neighborhood Search (GVNS)
    — perturbação SHAKE com intensidade k = 1 … K_MAX;
    — refinamento por VND com vizinhanças N1, N2 e N3.

Tratamento de inviabilidade: penalização da função objetivo.
    — violações de disponibilidade mínima/máxima são rejeitadas
      (restrição estrutural, preservada por construção nos movimentos);
    — violações de qualidade (SiO2 e Al2O3 fora de [min, max])
      são penalizadas com peso λ na função fitness.

Critério de parada: número fixo de iterações externas (MAX_ITER).
"""

import copy
import random
import statistics
import time
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sol_inicial import (
    calcular_f1,
    calcular_f2,
    calcular_f3,
    calcular_teores_pilha,
    eh_compativel,
    gerar_solucao_inicial,
    minerios,
    pilhas,
    resumir_composicao,
    sinters,
    validar_estrutura,
    validar_qualidade,
)
from vizinhancas import gerar_vizinho_n1
from contratos import Candidato, ConfigBusca, ConfigEscalar, ResultadoBusca
from avaliacao import avaliar, PESOS_PENALIDADE, calcular_penalidade


# ============================================================
# 1. PARÂMETROS
# ============================================================

K_MAX = 3              # intensidades de perturbação (P1, P2, P3)
MAX_ITER = 200         # iterações externas do GVNS por execução
MAX_AMOSTRAS = 20      # vizinhos amostrados por vizinhança no VND
MAX_RESTARTS_VND = 5   # reinícios máximos dentro do VND
MAX_SEM_MELHORA = 60   # parada antecipada: iterações sem melhora global

# Pesos da penalidade por objetivo
LAMBDA = PESOS_PENALIDADE  # pesos históricos; não são normalização ou garantia de viabilidade

# Seeds fixas para as 5 execuções independentes
SEMENTES = [42, 123, 456, 789, 1011]


# ============================================================
# 2. FUNÇÕES OBJETIVO
# ============================================================

def calcular_objetivo(solucao, objetivo):
    if objetivo == "f1":
        return calcular_f1(solucao)
    elif objetivo == "f2":
        return calcular_f2(solucao)
    elif objetivo == "f3":
        return calcular_f3(solucao)
    raise ValueError("Objetivo deve ser f1, f2 ou f3.")


# ============================================================
# 3. PENALIDADE E FITNESS
# ============================================================

def calcular_fitness(solucao, objetivo):
    """fitness = f(x) + λ · penalidade(x)."""
    return (
        calcular_objetivo(solucao, objetivo)
        + LAMBDA[objetivo] * calcular_penalidade(solucao)
    )


# ============================================================
# 4. VIZINHANÇAS POR AMOSTRAGEM (versões rápidas)
# ============================================================

def _gerar_vizinho_n2_rapido(solucao, rng, tentativas=40):
    """N2: troca um caminhão entre duas pilhas distintas.

    Versão por amostragem aleatória — evita enumerar os ~50 mil pares
    candidatos da implementação exaustiva de gerar_vizinho_n2.
    """
    pilhas_lista = list(solucao.keys())

    for _ in range(tentativas):
        p1, p2 = rng.sample(pilhas_lista, 2)
        if not solucao[p1] or not solucao[p2]:
            continue

        sinter_p1 = pilhas[p1]["sinter"]
        sinter_p2 = pilhas[p2]["sinter"]

        i = rng.randrange(len(solucao[p1]))
        j = rng.randrange(len(solucao[p2]))

        m1 = solucao[p1][i]
        m2 = solucao[p2][j]

        if m1 == m2:
            continue

        if not (eh_compativel(m2, sinter_p1) and eh_compativel(m1, sinter_p2)):
            continue

        nova_solucao = copy.deepcopy(solucao)
        nova_solucao[p1][i] = m2
        nova_solucao[p2][j] = m1
        return nova_solucao

    return None

def _gerar_vizinho_n3_rapido(solucao, rng, tentativas=50):
    """N3: substitui simultaneamente dois caminhões de uma mesma pilha.

    Usa amostragem aleatória em vez de enumerar os ~200 mil candidatos,
    o que torna a operação viável dentro do laço de busca local.
    """
    pilhas_lista = list(solucao.keys())
    rng.shuffle(pilhas_lista)

    for pilha in pilhas_lista:
        composicao = solucao[pilha]
        if len(composicao) < 2:
            continue
        sinter = pilhas[pilha]["sinter"]
        compativeis = [m for m in minerios if eh_compativel(m, sinter)]

        for _ in range(tentativas):
            i, j = sorted(rng.sample(range(len(composicao)), 2))
            atual_i = composicao[i]
            atual_j = composicao[j]
            novo_i = rng.choice(compativeis)
            novo_j = rng.choice(compativeis)

            # Ambas as posições devem mudar
            if novo_i == atual_i or novo_j == atual_j:
                continue

            nova = composicao.copy()
            nova[i] = novo_i
            nova[j] = novo_j

            # Não pode ser mera permutação interna
            if Counter(nova) == Counter(composicao):
                continue

            nova_solucao = copy.deepcopy(solucao)
            nova_solucao[pilha] = nova
            return nova_solucao

    return None


# ============================================================
# 5. SHAKE — PERTURBAÇÃO
# ============================================================

_GERADORES_SHAKE = [gerar_vizinho_n1, _gerar_vizinho_n2_rapido, _gerar_vizinho_n3_rapido]


def shake(solucao, k, rng, acompanhamento=None):
    """Aplica k movimentos aleatórios mantendo viabilidade estrutural."""
    atual = copy.deepcopy(solucao)
    for _ in range(k):
        for _ in range(30):
            gerador = rng.choice(_GERADORES_SHAKE)
            candidato = gerador(atual, rng)
            if candidato is None:
                continue
            valido, _ = validar_estrutura(candidato)
            if not valido and acompanhamento is not None:
                acompanhamento.tentativas_invalidas += 1
            if valido:
                if acompanhamento is not None:
                    acompanhamento.avaliar(candidato)
                atual = candidato
                break
    return atual


# ============================================================
# 6. BUSCA LOCAL E VND
# ============================================================

_GERADORES_VND = [gerar_vizinho_n1, _gerar_vizinho_n2_rapido, _gerar_vizinho_n3_rapido]


def _busca_local_n(solucao, objetivo, gerador, rng, acompanhamento=None):
    """First Improvement; observa candidatos antes do filtro de fitness."""
    if acompanhamento is None:
        fitness_atual = calcular_fitness(solucao, objetivo)
        max_amostras = MAX_AMOSTRAS
    else:
        fitness_atual = acompanhamento.avaliar(solucao).avaliacao.chave[0]
        max_amostras = acompanhamento.limites.max_amostras
    for _ in range(max_amostras):
        vizinho = gerador(solucao, rng)
        if vizinho is None:
            break
        valido, _ = validar_estrutura(vizinho)
        if not valido:
            if acompanhamento is not None:
                acompanhamento.tentativas_invalidas += 1
            continue
        if acompanhamento is None:
            fitness = calcular_fitness(vizinho, objetivo)
        else:
            fitness = acompanhamento.avaliar(vizinho).avaliacao.chave[0]
        if fitness < fitness_atual:
            return vizinho, True
    return solucao, False


def vnd(solucao, objetivo, rng, max_restarts=MAX_RESTARTS_VND, acompanhamento=None):
    """Variable Neighborhood Descent com N1, N2, N3.

    O número de reinícios é limitado a max_restarts para controlar
    o tempo de CPU em soluções muito distantes do ótimo.
    """
    l = 0
    atual = solucao
    restarts = 0
    while l < len(_GERADORES_VND):
        nova, melhorou = _busca_local_n(atual, objetivo, _GERADORES_VND[l], rng, acompanhamento)
        if melhorou:
            atual = nova
            if restarts < max_restarts:
                l = 0
                restarts += 1
            # após max_restarts reinícios, avança normalmente na vizinhança
        else:
            l += 1
    return atual


# ============================================================
# 7. GVNS
# ============================================================

class _OrcamentoEsgotado(Exception):
    pass


class _Acompanhamento:
    """Uma avaliação conta uma chamada completa válida, inclusive repetidas."""

    def __init__(self, objetivo, seed, limites, observar):
        self.config = ConfigEscalar('mono', objetivo, objetivo=int(objetivo[1]))
        self.seed = seed
        self.limites = limites
        self.observar = observar
        self.avaliacoes = 0
        self.tentativas_invalidas = 0
        self.melhor_viavel = None

    def avaliar(self, solucao):
        if (self.limites.max_avaliacoes is not None
                and self.avaliacoes >= self.limites.max_avaliacoes):
            raise _OrcamentoEsgotado
        av = avaliar(solucao, self.config)
        if not av.estrutura_ok:
            raise ValueError('Candidato estruturalmente inválido: ' + '; '.join(av.erros))
        self.avaliacoes += 1
        candidato = Candidato(solucao, av, [{'metodo': 'mono', 'configuracao': self.config.id,
                                            'seed': self.seed, 'avaliacao': self.avaliacoes}])
        if av.viavel and (self.melhor_viavel is None
                         or av.escalar < self.melhor_viavel.avaliacao.escalar):
            self.melhor_viavel = candidato
        if self.observar is not None:
            # O consumidor nunca recebe um alias da incumbente nem da trajetória.
            self.observar(copy.deepcopy(candidato))
        return candidato


def gvns(objetivo, seed, max_iter=MAX_ITER, k_max=K_MAX, *, limites=None, observar=None):
    """Retorna ResultadoBusca, com melhor viável separada da trajetória penalizada.

    Observa candidatos válidos de SHAKE/VND mesmo quando rejeitados por fitness.
    A configuração explícita `limites` prevalece sobre max_iter/k_max legados.
    """
    if objetivo not in LAMBDA:
        raise ValueError('Objetivo deve ser f1, f2 ou f3.')
    limites = limites or ConfigBusca(max_iter=max_iter, k_max=k_max)
    inicio = time.perf_counter()
    acompanhamento = _Acompanhamento(objetivo, seed, limites, observar)
    rng = random.Random(seed)
    melhor = None
    historico = []
    sem_melhora = 0
    iteracoes = 0
    motivo = 'max_iter'

    def registrar(iteracao):
        viavel = acompanhamento.melhor_viavel
        historico.append({'iteracao': iteracao, 'avaliacoes': acompanhamento.avaliacoes,
                          'melhor_viavel': viavel.avaliacao.escalar if viavel else None,
                          'objetivo_busca': melhor.avaliacao.escalar if melhor else None,
                          'fitness_busca': melhor.avaliacao.chave[0] if melhor else None})

    try:
        melhor = acompanhamento.avaliar(gerar_solucao_inicial())
        registrar(0)
        for it in range(1, limites.max_iter + 1):
            iteracoes = it
            melhorou = False
            k = 1
            while k <= limites.k_max:
                x_linha = shake(melhor.solucao, k, rng, acompanhamento)
                x_dois_linhas = vnd(x_linha, objetivo, rng, limites.max_restarts, acompanhamento)
                novo = acompanhamento.avaliar(x_dois_linhas)
                if novo.avaliacao.chave < melhor.avaliacao.chave:
                    melhor = novo
                    melhorou = True
                    k = 1
                else:
                    k += 1
            registrar(it)
            sem_melhora = 0 if melhorou else sem_melhora + 1
            if sem_melhora >= limites.max_sem_melhora and not melhorou:
                motivo = 'estagnacao'
                break
    except _OrcamentoEsgotado:
        motivo = 'max_avaliacoes'
        registrar(iteracoes)
    viavel = acompanhamento.melhor_viavel
    return ResultadoBusca('viavel' if viavel else 'sem_viavel_encontrada', viavel,
                          melhor, historico, acompanhamento.avaliacoes, iteracoes,
                          motivo, time.perf_counter() - inicio,
                          acompanhamento.tentativas_invalidas)


# ============================================================
# 8. EXPERIMENTO (5 EXECUÇÕES)
# ============================================================

def executar_experimento(objetivo, n_runs=5, max_iter=MAX_ITER):
    """Roda n_runs execuções independentes e coleta estatísticas."""
    resultados = []
    historicos = []
    melhores = []

    print(f"\n{'='*60}")
    print(f"EXPERIMENTO — {objetivo.upper()}")
    print(f"{'='*60}")

    for i in range(n_runs):
        semente = SEMENTES[i]
        print(f"  Execução {i+1}/{n_runs}  (seed={semente}) ...", end=" ", flush=True)
        t0 = time.time()
        resultado = gvns(objetivo, seed=semente, max_iter=max_iter)
        if resultado.melhor_viavel is None:
            raise RuntimeError(f'Execução seed={semente} sem solução viável; não calcular estatísticas como sucesso.')
        sol = resultado.melhor_viavel.solucao
        valor = resultado.melhor_viavel.avaliacao.escalar
        hist = [x['melhor_viavel'] for x in resultado.historico]
        dt = time.time() - t0
        print(f"valor = {valor:.6f}  ({dt:.1f}s)")
        resultados.append(valor)
        historicos.append(hist)
        melhores.append(sol)

    idx_melhor = resultados.index(min(resultados))

    media = statistics.mean(resultados)
    desvio = statistics.stdev(resultados) if len(resultados) > 1 else 0.0

    print(f"\n  Estatísticas ({objetivo.upper()}):")
    print(f"    Mínimo:        {min(resultados):.6f}")
    print(f"    Média:         {media:.6f}")
    print(f"    Desvio padrão: {desvio:.6f}")
    print(f"    Máximo:        {max(resultados):.6f}")

    _, erros_qual = validar_qualidade(melhores[idx_melhor])
    print(f"    Qualidade viável: {len(erros_qual) == 0}")
    if erros_qual:
        for e in erros_qual:
            print(f"      {e}")

    return {
        "objetivo": objetivo,
        "resultados": resultados,
        "historicos": historicos,
        "melhor_solucao": melhores[idx_melhor],
        "melhor_valor": min(resultados),
        "media": media,
        "desvio": desvio,
        "maximo": max(resultados),
    }


# ============================================================
# 9. VISUALIZAÇÕES
# ============================================================

def plotar_convergencia(exp, caminho):
    """Curvas de convergência das n execuções sobrepostas."""
    obj = exp["objetivo"]
    plt.figure(figsize=(10, 5))
    for i, hist in enumerate(exp["historicos"]):
        plt.plot(hist, linewidth=1.3, alpha=0.8, label=f"Execução {i + 1}")
    plt.xlabel("Iteração externa do GVNS")
    plt.ylabel(f"Valor de {obj}")
    plt.title(f"Convergência — {obj.upper()}")
    plt.legend(fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"  Salvo: {caminho}")


def plotar_melhor_solucao(exp, caminho):
    """Barras empilhadas com a composição da melhor solução."""
    obj = exp["objetivo"]
    sol = exp["melhor_solucao"]
    pilhas_lista = sorted(sol.keys())
    todos_minerios = sorted(minerios.keys(), key=lambda m: int(m[1:]))
    cores = plt.cm.tab20.colors

    fig, ax = plt.subplots(figsize=(14, 6))
    bottoms = [0] * len(pilhas_lista)

    for idx_m, m in enumerate(todos_minerios):
        vals = [sol[p].count(m) for p in pilhas_lista]
        if any(v > 0 for v in vals):
            ax.bar(
                [f"P{p}" for p in pilhas_lista],
                vals,
                bottom=bottoms,
                label=m,
                color=cores[idx_m % len(cores)],
                edgecolor="white",
                linewidth=0.5,
            )
            for i, v in enumerate(vals):
                bottoms[i] += v

    ax.set_xlabel("Pilha")
    ax.set_ylabel("Caminhões (2 kt cada)")
    ax.set_title(f"Melhor solução — {obj.upper()} = {exp['melhor_valor']:.6f}")
    ax.legend(fontsize=7, bbox_to_anchor=(1.01, 1), loc="upper left", ncol=1)
    plt.tight_layout()
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Salvo: {caminho}")


# ============================================================
# 10. EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == "__main__":
    objetivos = ["f1", "f2", "f3"]
    experimentos = {}

    for obj in objetivos:
        exp = executar_experimento(obj)
        experimentos[obj] = exp
        plotar_convergencia(exp, f"convergencia_{obj}.png")
        plotar_melhor_solucao(exp, f"melhor_solucao_{obj}.png")

    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    for obj, exp in experimentos.items():
        print(
            f"  {obj.upper()}  min={exp['melhor_valor']:.6f}"
            f"  media={exp['media']:.6f}"
            f"  dp={exp['desvio']:.6f}"
            f"  max={exp['maximo']:.6f}"
        )
