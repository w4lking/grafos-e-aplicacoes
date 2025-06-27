from dataclasses import dataclass
from typing import List

# Representa uma única rota gerada pelo algoritmo
@dataclass
class Rota:
    id_rota_output: int        # ID da rota (começando de 1)
    demanda_total_rota: float  # Soma das demandas dos serviços únicos nesta rota
    custo_total_rota: float    # Custo total da rota (deslocamento + serviço)
    total_visitas: int         # Número total de nós visitados na rota (incluindo depósito)
    trajeto_string_output: str # String formatada da rota (e.g., "(D 0,1,1) (S 5,2,2) ...")

# Representa a solução completa do problema, contendo todas as rotas e métricas gerais
@dataclass
class Solucao:
    custo_total_solucao: float  # Custo total de todas as rotas
    num_rotas_solucao: int      # Número total de rotas
    clocks_execucao: int        # Tempo de execução em nanossegundos (inteiro)
    tempo_total_s: float        # Tempo de execução total em segundos (float)
    rotas: List[Rota]           # Lista de objetos Rota
