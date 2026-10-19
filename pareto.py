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
    # Agrupar primeiro evita copiar todo o arquivo a cada observação repetida.
    # Composições iguais têm objetivos brutos iguais; a primeira avaliação
    # (que pode conter outro escalar) continua sendo a avaliação preservada.
    grupos = {}
    for candidato in candidatos:
        origens = candidato.origens
        if metodo is not None or repeticao is not None:
            origens = [o for o in candidato.origens
                       if (metodo is None or o.get('metodo') == metodo)
                       and (repeticao is None or o.get('repeticao') == repeticao)]
            if not origens:
                continue
        _validar_candidato(candidato)
        chave = chave_solucao(candidato.solucao)
        if chave not in grupos:
            grupos[chave] = (candidato, [], set())
        _, unidas, vistas = grupos[chave]
        for origem in origens:
            chave_origem = _chave_origem(origem)
            if chave_origem not in vistas:
                vistas.add(chave_origem)
                unidas.append(origem)

    # Em ordem lexicográfica dos três objetivos, um ponto posterior não
    # domina um anterior. Vetores iguais de composições distintas permanecem.
    frente = []
    for chave, (candidato, origens, _) in sorted(
            grupos.items(), key=lambda item: (tuple(item[1][0].avaliacao.objetivos), item[0])):
        vetor = candidato.avaliacao.objetivos
        if any(all(x <= y for x, y in zip(anterior.avaliacao.objetivos, vetor))
               and any(x < y for x, y in zip(anterior.avaliacao.objetivos, vetor))
               for _, anterior, _ in frente):
            continue
        frente.append((chave, candidato, origens))
    return [Candidato(c.solucao, deepcopy(c.avaliacao), origens)
            for _, c, origens in sorted(frente, key=lambda item: item[0])]


def _chave_origem(valor):
    """Chave hashable com igualdade de dict/list, inclusive 1 == 1.0."""
    if isinstance(valor, dict):
        return (dict, frozenset((k, _chave_origem(v)) for k, v in valor.items()))
    if isinstance(valor, list):
        return (list, tuple(_chave_origem(v) for v in valor))
    if isinstance(valor, tuple):
        return (tuple, tuple(_chave_origem(v) for v in valor))
    return valor
