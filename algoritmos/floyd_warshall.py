# algoritmos/floyd_warshall.py
import math

def floyd_warshall(matriz_adj):
    """
    Implementa o algoritmo de Floyd-Warshall para encontrar os caminhos mais curtos
    entre todos os pares de vértices em um grafo.
    
    Args:
        matriz_adj (list of list of float): Matriz de adjacência do grafo,
                                            onde math.inf representa ausência de aresta.
                                            Deve conter custos de travessia.
                                            matriz_adj[i][i] deve ser 0.

    Returns:
        list of list of float: Uma matriz de distâncias onde dist[i][j] é o
                               custo do caminho mais curto de i para j.
    """
    num_vertices = len(matriz_adj)
    
    # Inicializa a matriz de distâncias com os valores da matriz de adjacência
    # Importante: Criar uma cópia profunda para não modificar a matriz_adj original
    dist = [[matriz_adj[i][j] for j in range(num_vertices)] for i in range(num_vertices)]

    # O algoritmo de Floyd-Warshall
    # k é o vértice intermediário
    for k in range(num_vertices):
        # i é o vértice de origem
        for i in range(num_vertices):
            # j é o vértice de destino
            for j in range(num_vertices):
                # Se o caminho de i para k e de k para j existe (não é infinito)
                if dist[i][k] != math.inf and dist[k][j] != math.inf:
                    # Tenta relaxar o caminho: se (i -> k -> j) é mais curto que (i -> j)
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    
    return dist

