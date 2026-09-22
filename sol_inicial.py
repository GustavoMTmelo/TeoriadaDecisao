from collections import defaultdict, Counter


# ============================================================
# 1. CONSTANTES
# ============================================================

# Cada caminhão transporta 2 kt = 2000 toneladas
CAPACIDADE_CAMINHAO_KT = 2
CAPACIDADE_CAMINHAO_T = 2000


# ============================================================
# 2. DADOS DOS MINÉRIOS
# ============================================================
#
# custo: R$/t
# fet, sio2, al2o3: porcentagem (%)
# disp_min e disp_max: número de caminhões
# s1 / s2: indica se o minério pode alimentar o Sinter
#

minerios = {
    "M1": {
        "custo": 320,
        "fet": 66.0,
        "sio2": 5.0,
        "al2o3": 1.0,
        "disp_min": 0,
        "disp_max": 6,
        "s1": True,
        "s2": True,
    },

    "M2": {
        "custo": 280,
        "fet": 64.0,
        "sio2": 3.0,
        "al2o3": 3.0,
        "disp_min": 0,
        "disp_max": 8,
        "s1": True,
        "s2": True,
    },

    "M3": {
        "custo": 270,
        "fet": 62.0,
        "sio2": 9.0,
        "al2o3": 0.6,
        "disp_min": 0,
        "disp_max": 8,
        "s1": True,
        "s2": True,
    },

    "M4": {
        "custo": 190,
        "fet": 58.0,
        "sio2": 8.0,
        "al2o3": 2.8,
        "disp_min": 2,
        "disp_max": 12,
        "s1": True,
        "s2": True,
    },

    "M5": {
        "custo": 230,
        "fet": 60.0,
        "sio2": 6.0,
        "al2o3": 1.5,
        "disp_min": 0,
        "disp_max": 10,
        "s1": True,
        "s2": True,
    },

    "M6": {
        "custo": 300,
        "fet": 63.0,
        "sio2": 5.5,
        "al2o3": 1.2,
        "disp_min": 0,
        "disp_max": 8,
        "s1": True,
        "s2": True,
    },

    "M7": {
        "custo": 260,
        "fet": 65.0,
        "sio2": 5.5,
        "al2o3": 1.1,
        "disp_min": 0,
        "disp_max": 8,
        "s1": True,
        "s2": True,
    },

    "M8": {
        "custo": 240,
        "fet": 61.0,
        "sio2": 6.2,
        "al2o3": 1.6,
        "disp_min": 0,
        "disp_max": 8,
        "s1": True,
        "s2": False,
    },

    "M9": {
        "custo": 210,
        "fet": 59.0,
        "sio2": 6.5,
        "al2o3": 1.8,
        "disp_min": 0,
        "disp_max": 8,
        "s1": True,
        "s2": False,
    },

    "M10": {
        "custo": 180,
        "fet": 57.0,
        "sio2": 7.0,
        "al2o3": 2.5,
        "disp_min": 2,
        "disp_max": 10,
        "s1": True,
        "s2": False,
    },

    "M11": {
        "custo": 310,
        "fet": 66.0,
        "sio2": 4.7,
        "al2o3": 0.7,
        "disp_min": 1,
        "disp_max": 6,
        "s1": True,
        "s2": False,
    },

    "M12": {
        "custo": 200,
        "fet": 60.0,
        "sio2": 5.8,
        "al2o3": 1.4,
        "disp_min": 0,
        "disp_max": 8,
        "s1": True,
        "s2": False,
    },

    "M13": {
        "custo": 160,
        "fet": 56.0,
        "sio2": 9.0,
        "al2o3": 3.2,
        "disp_min": 0,
        "disp_max": 10,
        "s1": True,
        "s2": True,
    },

    "M14": {
        "custo": 150,
        "fet": 56.0,
        "sio2": 6.0,
        "al2o3": 1.3,
        "disp_min": 0,
        "disp_max": 6,
        "s1": True,
        "s2": True,
    },

    "M15": {
        "custo": 170,
        "fet": 58.0,
        "sio2": 8.0,
        "al2o3": 3.5,
        "disp_min": 0,
        "disp_max": 8,
        "s1": True,
        "s2": True,
    },

    "M16": {
        "custo": 220,
        "fet": 59.0,
        "sio2": 6.0,
        "al2o3": 1.5,
        "disp_min": 0,
        "disp_max": 8,
        "s1": False,
        "s2": True,
    },

    "M17": {
        "custo": 140,
        "fet": 56.0,
        "sio2": 8.5,
        "al2o3": 3.6,
        "disp_min": 0,
        "disp_max": 10,
        "s1": False,
        "s2": True,
    },

    "M18": {
        "custo": 260,
        "fet": 62.0,
        "sio2": 5.0,
        "al2o3": 1.0,
        "disp_min": 0,
        "disp_max": 8,
        "s1": False,
        "s2": True,
    },

    "M19": {
        "custo": 190,
        "fet": 57.0,
        "sio2": 6.3,
        "al2o3": 1.4,
        "disp_min": 0,
        "disp_max": 8,
        "s1": False,
        "s2": True,
    },

    "M20": {
        "custo": 130,
        "fet": 56.0,
        "sio2": 3.8,
        "al2o3": 3.8,
        "disp_min": 1,
        "disp_max": 8,
        "s1": False,
        "s2": True,
    },
}


# ============================================================
# 3. DADOS DOS SINTERS
# ============================================================

sinters = {
    1: {
        "sio2_min": 5.0,
        "sio2_alvo": 5.55,
        "sio2_max": 6.2,

        "al2o3_min": 1.0,
        "al2o3_alvo": 1.25,
        "al2o3_max": 2.3,
    },

    2: {
        "sio2_min": 5.0,
        "sio2_alvo": 5.50,
        "sio2_max": 6.5,

        "al2o3_min": 1.0,
        "al2o3_alvo": 1.50,
        "al2o3_max": 2.2,
    },
}


# ============================================================
# 4. DADOS DAS PILHAS
# ============================================================

pilhas = {
    1: {"sinter": 1, "massa_kt": 20},
    2: {"sinter": 1, "massa_kt": 22},
    3: {"sinter": 1, "massa_kt": 24},
    4: {"sinter": 1, "massa_kt": 26},
    5: {"sinter": 1, "massa_kt": 28},

    6: {"sinter": 2, "massa_kt": 30},
    7: {"sinter": 2, "massa_kt": 32},
    8: {"sinter": 2, "massa_kt": 34},
    9: {"sinter": 2, "massa_kt": 36},
    10: {"sinter": 2, "massa_kt": 38},
}


# ============================================================
# 5. FUNÇÕES AUXILIARES
# ============================================================

def numero_caminhoes_pilha(pilha):
    """
    Retorna quantos caminhões são necessários para uma pilha.
    """

    massa = pilhas[pilha]["massa_kt"]

    return massa // CAPACIDADE_CAMINHAO_KT


def eh_compativel(minerio, sinter):
    """
    Verifica se um minério pode alimentar determinado Sinter.
    """

    if sinter == 1:
        return minerios[minerio]["s1"]

    if sinter == 2:
        return minerios[minerio]["s2"]

    return False


def contar_uso_minerios(solucao):
    """
    Conta quantos caminhões de cada minério aparecem
    em toda a solução.
    """

    uso = Counter()

    for composicao in solucao.values():
        uso.update(composicao)

    return uso


# ============================================================
# 6. HEURÍSTICA CONSTRUTIVA
# ============================================================

def gerar_solucao_inicial():
    """
    Gera uma solução inicial.

    Etapa 1:
        Insere as disponibilidades mínimas obrigatórias.

    Etapa 2:
        Completa cada pilha usando os minérios compatíveis
        de menor custo disponíveis.

    A solução respeita:
        - massa das pilhas;
        - compatibilidade minério/Sinter;
        - disponibilidade mínima;
        - disponibilidade máxima.

    A solução NÃO precisa respeitar inicialmente
    os limites de qualidade.
    """

    solucao = {
        p: []
        for p in pilhas
    }

    uso = defaultdict(int)

    # ========================================================
    # ETAPA 1
    # Atender disponibilidades mínimas
    # ========================================================

    for minerio, dados in minerios.items():

        quantidade_minima = dados["disp_min"]

        for _ in range(quantidade_minima):

            colocado = False

            for p, dados_pilha in pilhas.items():

                sinter = dados_pilha["sinter"]

                capacidade = numero_caminhoes_pilha(p)

                tem_espaco = (
                    len(solucao[p]) < capacidade
                )

                compativel = eh_compativel(
                    minerio,
                    sinter
                )

                if tem_espaco and compativel:

                    solucao[p].append(minerio)

                    uso[minerio] += 1

                    colocado = True

                    break

            if not colocado:
                raise ValueError(
                    f"Não foi possível atender "
                    f"a disponibilidade mínima de {minerio}."
                )

    # ========================================================
    # ETAPA 2
    # Completar pilhas por menor custo
    # ========================================================

    for p, dados_pilha in pilhas.items():

        sinter = dados_pilha["sinter"]

        capacidade = numero_caminhoes_pilha(p)

        # Minérios que podem alimentar esse Sinter
        elegiveis = [
            m
            for m in minerios
            if eh_compativel(m, sinter)
        ]

        # Ordenação crescente pelo custo
        elegiveis.sort(
            key=lambda m: minerios[m]["custo"]
        )

        while len(solucao[p]) < capacidade:

            escolhido = None

            for minerio in elegiveis:

                disponibilidade_maxima = (
                    minerios[minerio]["disp_max"]
                )

                if uso[minerio] < disponibilidade_maxima:

                    escolhido = minerio

                    break

            if escolhido is None:
                raise ValueError(
                    f"Não existem minérios disponíveis "
                    f"para completar a Pilha {p}."
                )

            solucao[p].append(escolhido)

            uso[escolhido] += 1

    return solucao


# ============================================================
# 7. CÁLCULO DOS TEORES DAS PILHAS
# ============================================================

def calcular_teores_pilha(composicao):
    """
    Calcula FeT, SiO2 e Al2O3 da pilha.

    Como todos os caminhões possuem exatamente a mesma massa,
    o teor final é a média dos teores dos caminhões.
    """

    if len(composicao) == 0:
        raise ValueError("A pilha não pode estar vazia.")

    fet = sum(
        minerios[m]["fet"]
        for m in composicao
    ) / len(composicao)

    sio2 = sum(
        minerios[m]["sio2"]
        for m in composicao
    ) / len(composicao)

    al2o3 = sum(
        minerios[m]["al2o3"]
        for m in composicao
    ) / len(composicao)

    return {
        "fet": fet,
        "sio2": sio2,
        "al2o3": al2o3,
    }


# ============================================================
# 8. VALIDAÇÃO ESTRUTURAL
# ============================================================

def validar_estrutura(solucao):
    """
    Verifica as restrições estruturais da solução:

    - massa exata de cada pilha;
    - compatibilidade minério/Sinter;
    - disponibilidade mínima;
    - disponibilidade máxima.

    Retorna:
        (True, [])
        ou
        (False, lista_de_erros)
    """

    erros = []

    uso_total = contar_uso_minerios(solucao)

    # ========================================================
    # Massa e compatibilidade
    # ========================================================

    for p, composicao in solucao.items():

        sinter = pilhas[p]["sinter"]

        capacidade_esperada = numero_caminhoes_pilha(p)

        # Massa
        if len(composicao) != capacidade_esperada:

            erros.append(
                f"Pilha {p}: deveria possuir "
                f"{capacidade_esperada} caminhões, "
                f"mas possui {len(composicao)}."
            )

        # Compatibilidade
        for minerio in composicao:

            if not eh_compativel(minerio, sinter):

                erros.append(
                    f"Pilha {p}: minério {minerio} "
                    f"não é compatível com o Sinter {sinter}."
                )

    # ========================================================
    # Disponibilidade
    # ========================================================

    for minerio, dados in minerios.items():

        quantidade = uso_total[minerio]

        minimo = dados["disp_min"]

        maximo = dados["disp_max"]

        if quantidade < minimo:

            erros.append(
                f"{minerio}: uso {quantidade} abaixo "
                f"do mínimo {minimo}."
            )

        if quantidade > maximo:

            erros.append(
                f"{minerio}: uso {quantidade} acima "
                f"do máximo {maximo}."
            )

    return len(erros) == 0, erros


# ============================================================
# 9. VALIDAÇÃO DA QUALIDADE
# ============================================================

def validar_qualidade(solucao):
    """
    Verifica se todas as pilhas respeitam os limites
    de SiO2 e Al2O3.

    FeT não é usado como restrição ativa no case,
    pois seus limites são 0% e 100%.
    """

    erros = []

    for p, composicao in solucao.items():

        sinter = pilhas[p]["sinter"]

        limites = sinters[sinter]

        teores = calcular_teores_pilha(composicao)

        sio2 = teores["sio2"]

        al2o3 = teores["al2o3"]

        # ====================================================
        # SiO2
        # ====================================================

        if not (
            limites["sio2_min"]
            <= sio2
            <= limites["sio2_max"]
        ):

            erros.append(
                f"Pilha {p}: SiO2 = {sio2:.4f}% "
                f"fora de "
                f"[{limites['sio2_min']}, "
                f"{limites['sio2_max']}]"
            )

        # ====================================================
        # Al2O3
        # ====================================================

        if not (
            limites["al2o3_min"]
            <= al2o3
            <= limites["al2o3_max"]
        ):

            erros.append(
                f"Pilha {p}: Al2O3 = {al2o3:.4f}% "
                f"fora de "
                f"[{limites['al2o3_min']}, "
                f"{limites['al2o3_max']}]"
            )

    return len(erros) == 0, erros


# ============================================================
# 10. FUNÇÃO OBJETIVO F1
# CUSTO TOTAL
# ============================================================

def calcular_f1(solucao):
    """
    Função objetivo f1:
    custo total de aquisição.

    custo do minério = R$/t
    caminhão = 2000 t
    """

    custo_total = 0

    for composicao in solucao.values():

        for minerio in composicao:

            custo_tonelada = (
                minerios[minerio]["custo"]
            )

            custo_caminhao = (
                custo_tonelada
                * CAPACIDADE_CAMINHAO_T
            )

            custo_total += custo_caminhao

    return custo_total


# ============================================================
# 11. FUNÇÃO OBJETIVO F2
# DESVIO QUADRÁTICO DE SiO2
# ============================================================

def calcular_f2(solucao):
    """
    Soma dos desvios quadráticos de SiO2
    em relação ao alvo do respectivo Sinter.
    """

    total = 0.0

    for p, composicao in solucao.items():

        sinter = pilhas[p]["sinter"]

        alvo = sinters[sinter]["sio2_alvo"]

        sio2 = calcular_teores_pilha(
            composicao
        )["sio2"]

        desvio = sio2 - alvo

        total += desvio ** 2

    return total


# ============================================================
# 12. FUNÇÃO OBJETIVO F3
# DESVIO QUADRÁTICO DE Al2O3
# ============================================================

def calcular_f3(solucao):
    """
    Soma dos desvios quadráticos de Al2O3
    em relação ao alvo do respectivo Sinter.
    """

    total = 0.0

    for p, composicao in solucao.items():

        sinter = pilhas[p]["sinter"]

        alvo = sinters[sinter]["al2o3_alvo"]

        al2o3 = calcular_teores_pilha(
            composicao
        )["al2o3"]

        desvio = al2o3 - alvo

        total += desvio ** 2

    return total


# ============================================================
# 13. RESUMO DE UMA COMPOSIÇÃO
# ============================================================

def resumir_composicao(composicao):
    """
    Transforma:

    ["M4", "M4", "M10", "M10", "M14"]

    em:

    M4 x2 | M10 x2 | M14 x1
    """

    contagem = Counter(composicao)

    ordenado = sorted(
        contagem.items(),
        key=lambda item: int(item[0][1:])
    )

    return " | ".join(
        f"{minerio} x{quantidade}"
        for minerio, quantidade in ordenado
    )


# ============================================================
# 14. IMPRESSÃO COMPLETA DA SOLUÇÃO
# ============================================================

def imprimir_solucao(solucao):

    print("\n" + "=" * 80)

    print("SOLUÇÃO INICIAL")

    print("=" * 80)

    for p in sorted(solucao):

        composicao = solucao[p]

        sinter = pilhas[p]["sinter"]

        massa = pilhas[p]["massa_kt"]

        teores = calcular_teores_pilha(
            composicao
        )

        print(f"\nPilha {p}")

        print(f"  Sinter: {sinter}")

        print(f"  Massa: {massa} kt")

        print(
            f"  Caminhões: {len(composicao)}"
        )

        print(
            f"  Composição: "
            f"{resumir_composicao(composicao)}"
        )

        print(
            f"  FeT:   {teores['fet']:.4f}%"
        )

        print(
            f"  SiO2:  {teores['sio2']:.4f}%"
        )

        print(
            f"  Al2O3: {teores['al2o3']:.4f}%"
        )


# ============================================================
# 15. IMPRESSÃO DAS DISPONIBILIDADES
# ============================================================

def imprimir_uso_minerios(solucao):

    uso = contar_uso_minerios(solucao)

    print("\n" + "=" * 80)

    print("USO DOS MINÉRIOS")

    print("=" * 80)

    for minerio in minerios:

        quantidade = uso[minerio]

        minimo = minerios[minerio]["disp_min"]

        maximo = minerios[minerio]["disp_max"]

        print(
            f"{minerio:>3}: "
            f"{quantidade:>2} caminhões "
            f"| mínimo = {minimo:>2} "
            f"| máximo = {maximo:>2}"
        )


# ============================================================
# 16. AVALIAÇÃO GERAL
# ============================================================

def avaliar_solucao(solucao):

    estrutural_valida, erros_estruturais = (
        validar_estrutura(solucao)
    )

    qualidade_valida, erros_qualidade = (
        validar_qualidade(solucao)
    )

    f1 = calcular_f1(solucao)

    f2 = calcular_f2(solucao)

    f3 = calcular_f3(solucao)

    print("\n" + "=" * 80)

    print("AVALIAÇÃO DA SOLUÇÃO")

    print("=" * 80)

    print(
        "\nViabilidade estrutural:",
        estrutural_valida
    )

    if not estrutural_valida:

        print("\nErros estruturais:")

        for erro in erros_estruturais:
            print(" -", erro)

    print(
        "\nViabilidade de qualidade:",
        qualidade_valida
    )

    if not qualidade_valida:

        print(
            "\nViolações de qualidade "
            "(esperadas na solução inicial):"
        )

        for erro in erros_qualidade:
            print(" -", erro)

    print("\nFUNÇÕES OBJETIVO")

    print(
        f"f1 - Custo total: "
        f"R$ {f1:,.2f}"
    )

    print(
        f"f2 - Desvio quadrático SiO2: "
        f"{f2:.6f}"
    )

    print(
        f"f3 - Desvio quadrático Al2O3: "
        f"{f3:.6f}"
    )

    return {
        "estrutural_valida": estrutural_valida,
        "qualidade_valida": qualidade_valida,
        "f1": f1,
        "f2": f2,
        "f3": f3,
        "erros_estruturais": erros_estruturais,
        "erros_qualidade": erros_qualidade,
    }


# ============================================================
# 17. EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    # Gera a solução inicial
    solucao_inicial = gerar_solucao_inicial()

    # Mostra composição das 10 pilhas
    imprimir_solucao(solucao_inicial)

    # Mostra uso de cada minério
    imprimir_uso_minerios(solucao_inicial)

    # Calcula viabilidade e funções objetivo
    resultados = avaliar_solucao(
        solucao_inicial
    )
