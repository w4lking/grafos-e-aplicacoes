from dataclasses import dataclass, field
from typing import List, Tuple, Any # Importar Any para Servico (importação cíclica)

# Forward declaration para evitar importação circular com modelos.servico
# Em Python 3.7+, `from __future__ import annotations` (no topo do arquivo)
# permite type hints de classes que ainda não foram definidas.
# No dataclass, podemos usar 'Servico' como string para o type hint.
# No entanto, para manipulação de listas, precisaremos do objeto real.
# A melhor abordagem é importar Servico no runtime ou usar 'Any' ou 'str' como type hint
# e garantir o import no módulo que realmente cria/manipula as listas.
# Para manter a simplicidade e evitar refatorar todos os imports agora:
# Vamos usar 'Any' no type hint e garantir que `Servico` esteja acessível
# nos módulos que populam estas listas.

# Representa uma única rota gerada pelo algoritmo
@dataclass
class Rota:
    id_rota_output: int        # ID da rota (começando de 1)
    demanda_total_rota: float  # Soma das demandas dos serviços únicos nesta rota
    custo_total_rota: float    # Custo total da rota (deslocamento + serviço)
    total_visitas: int         # Número total de nós visitados na rota (incluindo depósito)
    
    # NOVOS CAMPOS PARA FACILITAR A BUSCA LOCAL:
    # A sequência de nós que o veículo realmente percorre, incluindo o depósito e nós intermediários
    # Ex: [depot_idx, nó_serviço1_inicio, nó_serviço1_fim, nó_serviço2_inicio, ..., depot_idx]
    sequencia_nos_percorridos: List[int] 
    
    # A lista dos objetos Servico que foram atendidos por esta rota, na ordem.
    # Isso é fundamental para 2-Opt/Relocate em nível de serviço.
    # NOTA: O type hint 'Any' é usado aqui para evitar importação circular com 'modelos.servico'.
    # O módulo que criar/usar 'Rota' e seus `sequencia_servicos` precisará importar `Servico`.
    servicos_atendidos: List[Any] 

    # String formatada da rota (e.g., "(D 0,1,1) (S 5,2,2) ...")
    # Este campo é apenas para a saída final, não para manipulação interna.
    trajeto_string_output: str = field(repr=False) 


# Representa a solução completa do problema, contendo todas as rotas e métricas gerais
@dataclass
class Solucao:
    custo_total_solucao: float  # Custo total de todas as rotas
    num_rotas_solucao: int      # Número total de rotas
    clocks_execucao: int        # Tempo de execução em nanossegundos (inteiro)
    tempo_total_s: float        # Tempo de execução total em segundos (float)
    rotas: List[Rota]           # Lista de objetos Rota
