from algoritmos.floyd_warshall import floyd_warshall 

def calcular_estatisticas_sem_networkx(matriz, n_vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos):
    direcionado = len(arcos) > 0
    total_arestas = len(arestas)
    total_arcos = len(arcos)
    total_arestas_arcos = total_arestas + total_arcos

    # Densidade
    if direcionado:
        densidade = total_arestas_arcos / (n_vertices * (n_vertices - 1))
    else:
        densidade = (2 * total_arestas) / (n_vertices * (n_vertices - 1))

    # Graus
    graus = [0] * n_vertices
    for u, v, _ in arestas:
        graus[u] += 1
        graus[v] += 1
    for u, v, _ in arcos:
        graus[u] += 1  # somente o nó de saída conta em arcos

    grau_min = min(graus)
    grau_max = max(graus)

    # Floyd-Warshall
    dist = floyd_warshall(matriz)

    # Caminho médio e diâmetro
    soma = 0
    cont = 0
    diametro = 0
    for i in range(n_vertices):
        for j in range(n_vertices):
            if i != j and dist[i][j] != float('inf'):
                soma += dist[i][j]
                cont += 1
                diametro = max(diametro, dist[i][j])
    caminho_medio = soma / cont if cont else float('inf')

    # Intermediação (versão simplificada)
    intermediacao = [0] * n_vertices
    for i in range(n_vertices):
        for j in range(n_vertices):
            if i != j and dist[i][j] != float('inf'):
                for k in range(n_vertices):
                    if k != i and k != j:
                        if dist[i][j] == dist[i][k] + dist[k][j]:
                            intermediacao[k] += 1
    intermediacao_media = sum(intermediacao) / n_vertices

    print(f"Quantidade de nós: {n_vertices}")
    print(f"Quantidade de arestas: {total_arestas}")
    print(f"Quantidade de arcos: {total_arcos}")
    print(f"Quantidade de nós requeridos: {len(vertices_requeridos)}")
    print(f"Quantidade de arestas requeridas: {len(arestas_requeridas)}")
    print(f"Quantidade de arcos requeridos: {len(arcos_requeridos)}")
    print(f"Densidade do grafo: {densidade:.4f}")
    print(f"Grau mínimo dos nós: {grau_min}")
    print(f"Grau máximo dos nós: {grau_max}")
    print(f"Grau médio dos nós: {sum(graus) / n_vertices:.4f}")
    print(f"Intermediação: {intermediacao}")
    print(f"Intermediação média: {intermediacao_media:.4f}")
    print(f"Caminho médio: {caminho_medio:.4f}")
    print(f"Diâmetro: {diametro}")
