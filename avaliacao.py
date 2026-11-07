"""Avaliação física conjunta e fitness histórico mono-objetivo.

Os pesos abaixo não normalizam objetivos nem certificam viabilidade.
"""

from contratos import Avaliacao, ConfigEscalar
from sol_inicial import (calcular_f1, calcular_f2, calcular_f3,
                         calcular_teores_pilha, pilhas, sinters,
                         validar_estrutura, validar_qualidade)

PESOS_PENALIDADE = {'f1': 1e12, 'f2': 1e4, 'f3': 1e4}


def calcular_penalidade(solucao):
    """Soma quadrática dos excessos químicos, sem tolerância (fitness TP1)."""
    total = 0.0
    for p, composicao in solucao.items():
        limites = sinters[pilhas[p]['sinter']]
        teores = calcular_teores_pilha(composicao)
        for indicador in ('sio2', 'al2o3'):
            q = teores[indicador]
            total += max(0, limites[indicador + '_min'] - q,
                         q - limites[indicador + '_max']) ** 2
    return total


def avaliar(solucao, config: ConfigEscalar, referencia=None):
    """Valida primeiro a estrutura; não calcula objetivos em entrada inválida.

    Escalarizações TP2 serão implementadas em TP2-07 a TP2-10.
    """
    if config.metodo != 'mono' or referencia is not None:
        raise NotImplementedError('Nesta etapa somente avaliação mono-objetivo.')
    estrutura_ok, erros = validar_estrutura(solucao)
    if not estrutura_ok:
        return Avaliacao(None, None, False, False, True, float('inf'),
                         None, (), tuple(erros))
    qualidade_ok, erros = validar_qualidade(solucao)
    objetivos = (calcular_f1(solucao), calcular_f2(solucao), calcular_f3(solucao))
    penalidade = calcular_penalidade(solucao)
    escalar = objetivos[config.objetivo - 1]
    fitness = escalar + PESOS_PENALIDADE[f'f{config.objetivo}'] * penalidade
    return Avaliacao(objetivos, None, True, qualidade_ok, True,
                     penalidade, escalar, (fitness,), tuple(erros))
