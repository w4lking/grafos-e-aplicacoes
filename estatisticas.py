def floyd_warshall(matriz):
    n = len(matriz)
    dist = [row[:] for row in matriz]

    for k in range(n):
        if k % 10 == 0:  # printa a cada 10 passos
            print(f"Processando k = {k}/{n}")
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist

def calcular_estatisticas(matriz, arestas, arcos, vertices_requeridos):
    n = len(matriz)
    grau = [0] * n

    for u, v, _ in arestas:
        grau[u] += 1
        grau[v] += 1

    for u, v, _ in arcos:
        grau[u] += 1

    densidade = (len(arestas) + len(arcos)) / (n * (n - 1))
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

    caminho_medio = soma_caminhos / num_caminhos if num_caminhos > 0 else float('inf')

    return {
        "n_vertices": n,
        "n_arestas": len(arestas),
        "n_arcos": len(arcos),
        "n_vertices_requeridos": len(vertices_requeridos),
        "n_arestas_requeridas": len(arestas),
        "n_arcos_requeridos": len(arcos),
        "densidade": densidade,
        "grau_min": grau_min,
        "grau_max": grau_max,
        "caminho_medio": caminho_medio,
        "diametro": diametro
    }
