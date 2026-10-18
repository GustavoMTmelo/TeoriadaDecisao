"""Referências empíricas do TP1. Aplicação da normalização pertence a TP2-07."""

import hashlib
import json
import math

from contratos import Referencia


def construir_referencia(candidatos_viaveis):
    if not candidatos_viaveis or any(not c.avaliacao.viavel for c in candidatos_viaveis):
        raise ValueError('Referência requer amostra não vazia de soluções viáveis.')
    vetores = [c.avaliacao.objetivos for c in candidatos_viaveis]
    if any(v is None or len(v) != 3 or any(not math.isfinite(x) for x in v) for v in vetores):
        raise ValueError('Objetivos inválidos na referência.')
    minimo = tuple(min(v[j] for v in vetores) for j in range(3))
    maximo = tuple(max(v[j] for v in vetores) for j in range(3))
    if any(b-a <= 1e-12 * max(1, abs(a), abs(b)) for a, b in zip(minimo, maximo)):
        raise ValueError('Amplitude empírica degenerada; não congelar a referência.')
    origens = {}
    for j in range(3):
        origens[f'f{j+1}'] = {}
        for campo, extremo in [('minimo', minimo[j]), ('maximo', maximo[j])]:
            ids = sorted({o['run_id'] for c in candidatos_viaveis
                          if c.avaliacao.objetivos[j] == extremo for o in c.origens})
            if not ids:
                raise ValueError('Extremo sem run_id de origem.')
            origens[f'f{j+1}'][campo] = ids
    payload = {'minimo': minimo, 'maximo': maximo, 'origens': origens}
    identidade = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return Referencia(minimo, maximo, identidade, origens)


def validar_vetor(vetor, tamanho=3):
    """Rejeita dimensão incorreta e números não finitos nas APIs numéricas."""
    try:
        valido = (len(vetor) == tamanho and all(
            not isinstance(x, bool) and isinstance(x, (int, float)) and math.isfinite(x)
            for x in vetor))
    except TypeError:
        valido = False
    if not valido:
        raise ValueError(f'Esperado vetor com {tamanho} números finitos.')


def validar_referencia(referencia):
    validar_vetor(referencia.minimo)
    validar_vetor(referencia.maximo)
    for a, b in zip(referencia.minimo, referencia.maximo):
        if not math.isfinite(b - a) or b - a <= 1e-12 * max(1, abs(a), abs(b)):
            raise ValueError('Amplitude empírica degenerada ou inválida.')


def normalizar(objetivos, referencia):
    """Aplica extremos empíricos fixos; valores externos não são truncados."""
    validar_referencia(referencia)
    validar_vetor(objetivos)
    resultado = tuple((x-a)/(b-a) for x, a, b in
                      zip(objetivos, referencia.minimo, referencia.maximo))
    validar_vetor(resultado)
    return resultado


def carregar_referencia(caminho):
    """Carrega referência congelada, preservando origem e conferindo seu ID SHA256."""
    from pathlib import Path
    dados = json.loads(Path(caminho).read_text(encoding='utf-8'))
    try:
        ref = Referencia(tuple(dados['minimo']), tuple(dados['maximo']),
                         dados['id'], dados['origens'])
        validar_referencia(ref)
        for j in range(1, 4):
            for extremo in ('minimo', 'maximo'):
                ids = ref.origens[f'f{j}'][extremo]
                if not isinstance(ids, list) or not ids or any(
                        not isinstance(run_id, str) or not run_id for run_id in ids):
                    raise ValueError('Origem do extremo inválida.')
    except (KeyError, TypeError) as erro:
        raise ValueError('Referência incompleta ou inválida.') from erro
    payload = {'minimo': ref.minimo, 'maximo': ref.maximo, 'origens': ref.origens}
    esperado = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    if ref.id != esperado:
        raise ValueError('Hash de identidade da referência divergente.')
    return ref
