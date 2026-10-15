"""Contratos compartilhados; ausência de solução viável é um resultado explícito."""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Literal

Solucao = dict[int, list[str]]
Vetor = tuple[float, float, float]


@dataclass(frozen=True)
class Referencia:
    minimo: Vetor
    maximo: Vetor
    id: str
    origens: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ConfigEscalar:
    metodo: Literal['mono', 'ponderada', 'epsilon']
    id: str
    objetivo: int | None = None
    pesos: Vetor | None = None
    epsilons: tuple[float, float] | None = None

    def __post_init__(self):
        if self.metodo not in ('mono', 'ponderada', 'epsilon'):
            raise ValueError('Método desconhecido.')
        if self.metodo == 'mono' and self.objetivo not in (1, 2, 3):
            raise ValueError('Objetivo mono deve ser 1, 2 ou 3.')


@dataclass(frozen=True)
class ConfigBusca:
    max_iter: int = 200
    max_sem_melhora: int = 60
    k_max: int = 3
    max_amostras: int = 20
    max_restarts: int = 5
    max_avaliacoes: int | None = None

    def __post_init__(self):
        for nome, valor in vars(self).items():
            if valor is None and nome == 'max_avaliacoes':
                continue
            if type(valor) is not int or valor < 0:
                raise ValueError(f'{nome} deve ser inteiro não negativo.')


@dataclass(frozen=True)
class Avaliacao:
    objetivos: Vetor | None
    normalizados: Vetor | None
    estrutura_ok: bool
    qualidade_ok: bool
    epsilon_ok: bool
    violacao: float
    escalar: float | None
    chave: tuple
    erros: tuple[str, ...]

    @property
    def viavel(self):
        return self.estrutura_ok and self.qualidade_ok and self.epsilon_ok


@dataclass(frozen=True)
class Candidato:
    solucao: Solucao
    avaliacao: Avaliacao
    origens: list[dict] = field(default_factory=list)

    def __post_init__(self):
        object.__setattr__(self, 'solucao', deepcopy(self.solucao))
        object.__setattr__(self, 'origens', deepcopy(self.origens))


@dataclass(frozen=True)
class ResultadoBusca:
    status: Literal['viavel', 'sem_viavel_encontrada']
    melhor_viavel: Candidato | None
    melhor_busca: Candidato | None
    historico: list[dict]
    avaliacoes: int
    iteracoes: int
    motivo_parada: str
    tempo_s: float
    tentativas_invalidas: int = 0

    def __post_init__(self):
        if self.status not in ('viavel', 'sem_viavel_encontrada'):
            raise ValueError('Status desconhecido.')
        if (self.status == 'viavel') != (self.melhor_viavel is not None):
            raise ValueError('Status e presença de melhor viável inconsistentes.')
        if self.melhor_viavel is not None and not self.melhor_viavel.avaliacao.viavel:
            raise ValueError('Melhor viável não satisfaz as restrições.')
