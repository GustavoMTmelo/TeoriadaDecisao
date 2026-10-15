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
