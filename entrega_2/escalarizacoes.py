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
    elif config.metodo == 'epsilon':
        validar_epsilons(config.epsilons)
        if config.objetivo is not None or config.pesos is not None:
            raise ValueError('Epsilon contém parâmetros de outro método.')
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


def validar_epsilons(eps):
    validar_vetor(eps, tamanho=2)
    if min(eps) < 0:
        raise ValueError('Limites epsilon devem ser não negativos.')


def restricoes_epsilon(g, eps, tol=1e-9):
    """Dois tetos independentes; retorna viabilidade e soma dos excessos positivos."""
    validar_vetor(g)
    validar_epsilons(eps)
    if not isinstance(tol, (int, float)) or not math.isfinite(tol) or tol < 0:
        raise ValueError('Tolerância epsilon inválida.')
    excessos = [max(0., g[j+1]-eps[j]-tol) for j in range(2)]
    return not any(excessos), sum(excessos)


def configuracoes_epsilon():
    return [ConfigEscalar('epsilon', f'eps_{i}{j}', epsilons=(i/3, j/3))
            for i in range(4) for j in range(4)]
