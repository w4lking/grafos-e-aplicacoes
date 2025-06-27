from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Tuple

# Representa um vértice requerido na instância
@dataclass
class VerticeRequerido:
    no_idx: int          # Índice do nó (0-indexado)
    demanda: int         # Demanda associada ao serviço no nó
    custo_servico: int   # Custo de serviço associado ao nó

# Representa uma aresta ou arco requerido na instância
@dataclass
class LigacaoRequerida:
    u: int                 # Nó de origem (0-indexado)
    v: int                 # Nó de destino (0-indexado)
    custo_travessia: float # Custo de travessia da ligação
    demanda: int           # Demanda associada ao serviço na ligação
    custo_servico: int     # Custo de serviço associado à ligação
    tipo: str              # "aresta_req" ou "arco_req"

# Representa uma aresta ou arco opcional na instância
@dataclass
class LigacaoOpcional:
    u: int          # Nó de origem (0-indexado)
    v: int          # Nó de destino (0-indexado)
    custo: float    # Custo de travessia da ligação

# Representa todos os dados de uma instância completa do problema
@dataclass
class Instancia:
    nome: str
    n_vertices: int
    capacidade_veiculo: int
    depot_idx: int
    vertices_requeridos_detalhes: List[VerticeRequerido]
    arestas_requeridas_detalhes: List[LigacaoRequerida]
    arcos_requeridos_detalhes: List[LigacaoRequerida]
    arestas_opcionais_travessia: List[LigacaoOpcional]
    arcos_opcionais_travessia: List[LigacaoOpcional]
    matriz_adj: List[List[float]] = field(repr=False) # Matriz de adjacência, excluída do repr padrão
