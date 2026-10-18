"""GVNS comum: avaliação central, aceitação estrita e observação antes do filtro.

Avaliações repetidas contam; tentativas estruturalmente inválidas não contam.
O orçamento é verificado antes de gerar movimentos e antes de cada avaliação.
"""
import copy
import random
import time

from avaliacao import avaliar
from contratos import Candidato, ResultadoBusca
from sol_inicial import gerar_solucao_inicial, validar_estrutura
from vns import gerar_vizinho_n1, _gerar_vizinho_n2_rapido, _gerar_vizinho_n3_rapido

GERADORES = [gerar_vizinho_n1, _gerar_vizinho_n2_rapido, _gerar_vizinho_n3_rapido]


class _FimOrcamento(Exception):
    pass


class _Acompanhamento:
    def __init__(self, config, referencia, seed, limites, observar):
        self.config = config
        self.referencia = copy.deepcopy(referencia)
        self.seed = seed
        self.limites = limites
        self.observar = observar
        self.avaliacoes = 0
        self.tentativas_invalidas = 0
        self.melhor_viavel = None

    def verificar_orcamento(self):
        if (self.limites.max_avaliacoes is not None
                and self.avaliacoes >= self.limites.max_avaliacoes):
            raise _FimOrcamento

    def avaliar(self, solucao):
        self.verificar_orcamento()
        av = avaliar(solucao, self.config, self.referencia)
        if not av.estrutura_ok:
            self.tentativas_invalidas += 1
            return None
        self.avaliacoes += 1
        c = Candidato(solucao, av, [{'metodo': self.config.metodo,
                                    'configuracao': self.config.id,
                                    'seed': self.seed, 'avaliacao': self.avaliacoes}])
        anterior = self.melhor_viavel
        # Mono guarda objetivo bruto, independentemente do fitness penalizado.
        chave = lambda x: ((x.avaliacao.escalar,) if self.config.metodo == 'mono'
                           else x.avaliacao.chave)
        if av.viavel and (anterior is None or chave(c) < chave(anterior)):
            self.melhor_viavel = c
        if self.observar is not None:
            self.observar(copy.deepcopy(c))
        return c


def _shake(atual, k, acompanhamento, rng):
    for _ in range(k):
        for _ in range(30):
            acompanhamento.verificar_orcamento()
            solucao = rng.choice(GERADORES)(atual.solucao, rng)
            if solucao is None:
                continue
            candidato = acompanhamento.avaliar(solucao)
            if candidato is not None:
                atual = candidato
                break
    return atual


def _busca_local(atual, indice, acompanhamento, rng):
    for _ in range(acompanhamento.limites.max_amostras):
        acompanhamento.verificar_orcamento()
        solucao = GERADORES[indice](atual.solucao, rng)
        if solucao is None:
            break
        candidato = acompanhamento.avaliar(solucao)
        if candidato is not None and candidato.avaliacao.chave < atual.avaliacao.chave:
            return candidato, True
    return atual, False


def _vnd(atual, acompanhamento, rng):
    indice = reinicios = 0
    while indice < len(GERADORES):
        atual, melhorou = _busca_local(atual, indice, acompanhamento, rng)
        if melhorou:
            if reinicios < acompanhamento.limites.max_restarts:
                indice = 0
                reinicios += 1
            # Após o limite mantém a vizinhança enquanto houver melhoria.
        else:
            indice += 1
    return atual


def resolver(config, referencia, seed, limites, observar=None):
    """Resolve uma configuração congelada, devolvendo ausência explícita de viável.

    O callback recebe cópia de todo candidato avaliado estruturalmente válido,
    inclusive inviáveis e candidatos rejeitados. Nenhum cache de avaliações.
    """
    if config.metodo != 'mono':
        from normalizacao import validar_referencia
        from escalarizacoes import validar_configuracao
        validar_configuracao(config)
        validar_referencia(referencia)
    inicio = time.perf_counter()
    a = _Acompanhamento(config, referencia, seed, limites, observar)
    rng = random.Random(seed)
    melhor = None
    historico = []
    iteracoes = sem_melhora = 0
    motivo = 'max_iter'

    def registrar():
        historico.append({'iteracao': iteracoes, 'avaliacoes': a.avaliacoes,
                          'melhor_viavel': (a.melhor_viavel.avaliacao.escalar
                                            if a.melhor_viavel else None),
                          'objetivo_busca': melhor.avaliacao.escalar if melhor else None,
                          'chave_busca': melhor.avaliacao.chave if melhor else None})

    try:
        a.verificar_orcamento()
        melhor = a.avaliar(gerar_solucao_inicial())
        if melhor is None:
            raise ValueError('Solução inicial estruturalmente inválida.')
        registrar()
        for iteracoes in range(1, limites.max_iter + 1):
            melhorou = False
            k = 1
            while k <= limites.k_max:
                a.verificar_orcamento()
                perturbado = _shake(melhor, k, a, rng)
                novo = _vnd(perturbado, a, rng)
                if novo.avaliacao.chave < melhor.avaliacao.chave:
                    melhor = novo
                    melhorou = True
                    k = 1
                else:
                    k += 1
            registrar()
            sem_melhora = 0 if melhorou else sem_melhora + 1
            if not melhorou and sem_melhora >= limites.max_sem_melhora:
                motivo = 'estagnacao'
                break
    except _FimOrcamento:
        motivo = 'max_avaliacoes'
        registrar()
    return ResultadoBusca('viavel' if a.melhor_viavel else 'sem_viavel_encontrada',
                          a.melhor_viavel, melhor, historico, a.avaliacoes,
                          iteracoes, motivo, time.perf_counter() - inicio,
                          a.tentativas_invalidas)
