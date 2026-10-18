"""Escalarizações puras e malhas fixas; pesos nunca corrigidos implicitamente."""

import math
from contratos import ConfigEscalar
from normalizacao import validar_vetor


def validar_pesos(pesos):
    validar_vetor(pesos)
    if min(pesos) < 0 or not math.isclose(sum(pesos), 1., rel_tol=0., abs_tol=1e-12):
        raise ValueError('Pesos devem ser não negativos e somar 1 (tolerância 1e-12).')


def validar_configuracao(config):
    if not isinstance(config.id, str) or not config.id:
        raise ValueError('Configuração requer ID não vazio.')
    if config.metodo == 'mono':
        if type(config.objetivo) is not int or config.objetivo not in (1, 2, 3):
            raise ValueError('Objetivo mono deve ser 1, 2 ou 3.')
        if config.pesos is not None or config.epsilons is not None:
            raise ValueError('Configuração mono contém parâmetros de outro método.')
    elif config.metodo == 'ponderada':
        validar_pesos(config.pesos)
        if config.objetivo is not None or config.epsilons is not None:
            raise ValueError('Soma ponderada contém parâmetros de outro método.')
    else:
        raise ValueError('Método desconhecido.')


def valor_ponderado(g, pesos):
    validar_vetor(g)
    validar_pesos(pesos)
    valor = sum(w*x for w, x in zip(pesos, g))
    if not math.isfinite(valor):
        raise ValueError('Valor escalar não finito.')
    return valor


def configuracoes_ponderadas():
    configs = [ConfigEscalar('ponderada', f'pond_{i}{j}{4-i-j}',
                            pesos=(i/4, j/4, (4-i-j)/4))
               for i in range(5) for j in range(5-i)]
    configs.append(ConfigEscalar('ponderada', 'pond_centro', pesos=(1/3,)*3))
    return configs
