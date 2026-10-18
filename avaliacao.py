"""Avaliação física conjunta e fitness histórico mono-objetivo.

Os pesos abaixo não normalizam objetivos nem certificam viabilidade.
"""

from contratos import Avaliacao, ConfigEscalar
from escalarizacoes import validar_configuracao, valor_ponderado, restricoes_epsilon
from normalizacao import normalizar, validar_referencia
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


def detalhar_excessos(solucao, g=None, eps=None, tolerancia=1e-9):
    """Auditoria de excessos brutos e tolerados de solução estruturalmente válida."""
    qualidade = []
    for p, composicao in solucao.items():
        limites = sinters[pilhas[p]['sinter']]
        teores = calcular_teores_pilha(composicao)
        for indicador in ('sio2', 'al2o3'):
            q = teores[indicador]
            baixo, alto = limites[indicador+'_min'], limites[indicador+'_max']
            bruto = max(0., baixo-q, q-alto)
            # Mesma ordem de operações da validação física nos limites exatos.
            tolerado = max(0., (baixo-tolerancia)-q, q-(alto+tolerancia))
            qualidade.append(dict(pilha=p, indicador=indicador, teor=q,
                                  minimo=baixo, maximo=alto, excesso_bruto=bruto,
                                  excesso_relativo=tolerado/(alto-baixo)))
    epsilon = []
    if eps is not None:
        restricoes_epsilon(g, eps, tolerancia)
        epsilon = [dict(objetivo=j+2, limite=eps[j], valor=g[j+1],
                        excesso_bruto=max(0., g[j+1]-eps[j]),
                        excesso_tolerado=max(0., g[j+1]-eps[j]-tolerancia))
                   for j in range(2)]
    return {'qualidade': qualidade, 'epsilon': epsilon}


def calcular_violacao_qualidade(solucao, tolerancia=1e-9):
    return sum(d['excesso_relativo']**2 for d in
               detalhar_excessos(solucao, tolerancia=tolerancia)['qualidade'])


def avaliar(solucao, config: ConfigEscalar, referencia=None):
    """Avalia estrutura antes de objetivos; TP2 prioriza viabilidade lexicográfica."""
    validar_configuracao(config)
    if config.metodo != 'mono':
        if referencia is None:
            raise ValueError('Escalarização TP2 requer referência congelada.')
        validar_referencia(referencia)
    estrutura_ok, erros = validar_estrutura(solucao)
    if not estrutura_ok:
        return Avaliacao(None, None, False, False, True, float('inf'),
                         None, (2, float('inf')), tuple(erros))
    qualidade_ok, erros = validar_qualidade(solucao)
    objetivos = (calcular_f1(solucao), calcular_f2(solucao), calcular_f3(solucao))
    if config.metodo == 'mono':
        penalidade = calcular_penalidade(solucao)
        escalar = objetivos[config.objetivo - 1]
        fitness = escalar + PESOS_PENALIDADE[f'f{config.objetivo}'] * penalidade
        return Avaliacao(objetivos, None, True, qualidade_ok, True,
                         penalidade, escalar, (fitness,), tuple(erros))
    g = normalizar(objetivos, referencia)
    violacao = calcular_violacao_qualidade(solucao)
    epsilon_ok = True
    if config.metodo == 'ponderada':
        escalar = valor_ponderado(g, config.pesos)
        desempate = (sum(g), *g)
    else:
        epsilon_ok, excesso = restricoes_epsilon(g, config.epsilons)
        violacao += excesso
        escalar = g[0]
        desempate = (g[1]+g[2], g[1], g[2])
        if not epsilon_ok:
            erros = [*erros, 'Limites epsilon excedidos.']
    chave = (0 if qualidade_ok and epsilon_ok else 1, violacao, escalar, desempate)
    return Avaliacao(objetivos, g, True, qualidade_ok, epsilon_ok,
                     violacao, escalar, chave, tuple(erros))
