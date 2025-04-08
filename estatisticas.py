from floyd_warshall import floyd_warshall 

def calcular_grau(matriz, arestas, arcos):
    n = len(matriz)
    grau = [0] * n

    # Arestas não direcionadas
    for u, v, _ in arestas:
        grau[u] += 1
        grau[v] += 1

    # Arcos direcionados (grau total: entrada + saída)
    for u, v, _ in arcos:
        grau[u] += 1  # grau de saída
        grau[v] += 1  # grau de entrada

    return grau 

def calcular_estatisticas(matriz, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos):
    n = len(matriz)
    grau = [0] * n

    # Arestas não direcionadas
    for u, v, _ in arestas:
        grau[u] += 1
        grau[v] += 1

    # Arcos direcionados (grau total: entrada + saída)
    for u, v, _ in arcos:
        grau[u] += 1  # grau de saída
        grau[v] += 1  # grau de entrada

    # Densidade: ajustando para considerar arcos como dirigidos
    max_arestas_possiveis = n * (n - 1)  # sem laços
    densidade = (len(arestas) + len(arcos)) / max_arestas_possiveis if n > 1 else 0

    grau_min = min(grau)
    grau_max = max(grau)

    distancias = floyd_warshall(matriz)
    soma_caminhos = 0
    num_caminhos = 0
    diametro = 0

    for i in range(n):
        for j in range(n):
            if i != j and distancias[i][j] < float('inf'):
                soma_caminhos += distancias[i][j]
                num_caminhos += 1
                diametro = max(diametro, distancias[i][j])

    caminho_medio = soma_caminhos / num_caminhos if num_caminhos else float('inf')

    return {
        "Quantidade de vértices": n,
        "Quantidade de arestas": len(arestas),
        "Quantidade de arcos": len(arcos),
        "Quantidade de vértices requeridos": len(vertices_requeridos),
        "Quantidade de arestas requeridas": len(arestas_requeridas),
        "Quantidade de arcos requeridos": len(arcos_requeridos),
        "Densidade do grafo": round(densidade, 4),
        "Grau mínimo": grau_min,
        "Grau máximo": grau_max,
        "Caminho médio": round(caminho_medio, 4),
        "Diâmetro": diametro
    }

