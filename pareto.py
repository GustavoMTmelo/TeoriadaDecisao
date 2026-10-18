"""Aproximação não dominada entre candidatos viáveis observados, em três objetivos.

O arquivo usa os objetivos brutos e nunca arredonda ou aplica tolerância à
dominância. A validação física pertence ao avaliador; este módulo exige sua
certificação de viabilidade, incluindo os limites epsilon da origem.
"""

from copy import deepcopy
from math import isfinite
from numbers import Real
from typing import Iterable

from contratos import Candidato, Solucao, Vetor


def _validar_vetor(vetor):
    try:
        valido = len(vetor) == 3 and all(
            isinstance(x, Real) and not isinstance(x, bool) and isfinite(x)
            for x in vetor)
    except (TypeError, OverflowError):
        valido = False
    if not valido:
        raise ValueError('Objetivos devem conter três números reais finitos.')


def domina(a: Vetor, b: Vetor) -> bool:
    """Dominância estrita de Pareto para minimização dos três objetivos."""
    _validar_vetor(a)
    _validar_vetor(b)
    return all(x <= y for x, y in zip(a, b)) and any(
        x < y for x, y in zip(a, b))


def chave_solucao(solucao: Solucao) -> tuple:
    """Identifica a composição por pilha, ignorando ordem dos caminhões.

    A multiplicidade dos minérios e a identidade de cada pilha são mantidas.
    Não substitui a validação estrutural do modelo físico.
    """
    return tuple((pilha, tuple(sorted(minerios)))
                 for pilha, minerios in sorted(solucao.items()))


def _validar_candidato(candidato):
    if not candidato.avaliacao.viavel:
        raise ValueError('O arquivo Pareto aceita somente candidatos viáveis.')
    _validar_vetor(candidato.avaliacao.objetivos)


def atualizar_arquivo(arquivo: list[Candidato], candidato: Candidato) -> list[Candidato]:
    """Insere em arquivo não dominado, sem alterar ou compartilhar suas entradas.

    Duplicatas físicas agregam origens distintas e mantêm a avaliação da
    primeira ocorrência. Vetores iguais de composições distintas permanecem.
    O chamador deve passar um arquivo já não dominado (ou uma lista vazia);
    para conjuntos arbitrários, use ``consolidar_arquivo``.
    """
    _validar_candidato(candidato)
    for existente in arquivo:
        _validar_candidato(existente)
    chave = chave_solucao(candidato.solucao)
    novo = []
    duplicado = False
    dominado = False
    for existente in arquivo:
        if chave_solucao(existente.solucao) == chave:
            origens = deepcopy(existente.origens)
            for origem in candidato.origens:
                if origem not in origens:
                    origens.append(deepcopy(origem))
            novo.append(Candidato(existente.solucao, deepcopy(existente.avaliacao), origens))
            duplicado = True
        else:
            novo.append(deepcopy(existente))
        if domina(existente.avaliacao.objetivos, candidato.avaliacao.objetivos):
            dominado = True
    if not duplicado and not dominado:
        novo = [c for c in novo if not domina(candidato.avaliacao.objetivos,
                                             c.avaliacao.objetivos)]
        novo.append(deepcopy(candidato))
    return sorted(novo, key=lambda c: chave_solucao(c.solucao))


def consolidar_arquivo(candidatos: Iterable[Candidato], *, metodo=None,
                      repeticao=None) -> list[Candidato]:
    """Filtra origens e consolida candidatos em um arquivo não dominado 3D.

    Os filtros são aplicados antes da dominância: um ponto dominado por outra
    repetição ainda pode pertencer ao arquivo da própria repetição. Para obter
    esses arquivos, forneça os candidatos originais ou a união dos arquivos
    por repetição, pois um arquivo global já perdeu seus pontos dominados.
    Sem filtros, preserva inclusive candidatos sem metadados de origem.
    """
    arquivo = []
    for candidato in candidatos:
        if metodo is not None or repeticao is not None:
            origens = [o for o in candidato.origens
                       if (metodo is None or o.get('metodo') == metodo)
                       and (repeticao is None or o.get('repeticao') == repeticao)]
            if not origens:
                continue
            candidato = Candidato(candidato.solucao,
                                  deepcopy(candidato.avaliacao), origens)
        arquivo = atualizar_arquivo(arquivo, candidato)
    return arquivo
