from dataclasses import dataclass
from typing import Any, Tuple

# Representa um serviço (tarefa) a ser executado por uma rota
@dataclass
class Servico:
    id_output: int             # ID único gerado para o serviço (para a saída)
    tipo: str                  # "no", "aresta", "arco"
    nome_original: str         # Nome original do arquivo (ex: "N4", "E1", "A1")
    definicao_original: Any    # Objeto VerticeRequerido ou LigacaoRequerida que o originou
    no_inicial_acesso: int     # Nó por onde o veículo acessa o serviço (0-indexado)
    no_final_apos_servico: int # Nó onde o veículo termina após executar o serviço (0-indexado)
    demanda: int               # Demanda do serviço
    custo_servico_proprio: int # Custo próprio de executar o serviço
    custo_travessia_interno: float # Custo de travessia SE o serviço for uma aresta/arco

    # __hash__ e __eq__ são importantes se você for colocar objetos Servico em sets ou dicionários
    # e quiser que eles sejam considerados iguais se seus IDs de saída forem iguais.
    # No entanto, para a remoção da lista de pendentes, a comparação por id_output é suficiente.
    def __hash__(self):
        return hash(self.id_output) # IDs de saída são únicos, então serve como hash

    def __eq__(self, other):
        if not isinstance(other, Servico):
            return NotImplemented
        return self.id_output == other.id_output
