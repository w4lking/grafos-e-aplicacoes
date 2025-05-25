# algoritmos/dijkstra.py
import math
import heapq

def dijkstra(matriz_adj, no_origem, no_destino):
    # ... (código da função dijkstra que fornecemos anteriormente) ...
    # Certifique-se de que ela retorna o custo (e opcionalmente o caminho)
    num_vertices = len(matriz_adj)
    distancias = [math.inf] * num_vertices
    distancias[no_origem] = 0
    
    fila_prioridade = [(0, no_origem)] # (distancia, no)

    while fila_prioridade:
        dist_atual, u = heapq.heappop(fila_prioridade)

        if dist_atual > distancias[u]:
            continue
        
        if u == no_destino and no_destino is not None: # Otimização se só queremos um destino
             break 

        for v_vizinho in range(num_vertices):
            peso_aresta = matriz_adj[u][v_vizinho]
            if peso_aresta != math.inf:
                if distancias[u] + peso_aresta < distancias[v_vizinho]:
                    distancias[v_vizinho] = distancias[u] + peso_aresta
                    heapq.heappush(fila_prioridade, (distancias[v_vizinho], v_vizinho))
    
    return distancias[no_destino] if no_destino is not None else distancias