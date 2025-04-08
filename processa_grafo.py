import os
import math
import matplotlib.pyplot as plt
from leitura import parse_dat_file  # Importa sua função de leitura já existente

def gerar_grafo_como_lista_adjacencia(n_vertices, arestas, arcos):
    """Gera o grafo como lista de adjacência."""
    grafo = {v: [] for v in range(n_vertices)}
    for u, v, custo in arestas:
        grafo[u].append((v, custo))
        grafo[v].append((u, custo))  # Grafo não direcionado para arestas
    for u, v, custo in arcos:
        grafo[u].append((v, custo))  # Arcos são direcionados
    return grafo

def desenhar_grafo(grafo, nome):
    """Desenha e salva o grafo como PNG."""
    num_vertices = len(grafo)
    angulo = 2 * math.pi / num_vertices
    posicoes = {v: (math.cos(i * angulo), math.sin(i * angulo)) for i, v in enumerate(grafo)}

    plt.figure(figsize=(8, 6))
    for v, vizinhos in grafo.items():
        x, y = posicoes[v]
        plt.plot(x, y, 'o', color='skyblue')
        plt.text(x, y, str(v), fontsize=12, ha='center', va='center')
        for u, peso in vizinhos:
            x2, y2 = posicoes[u]
            plt.plot([x, x2], [y, y2], 'k-', alpha=0.5)
            mx, my = (x + x2) / 2, (y + y2) / 2
            plt.text(mx, my, f"{peso:.0f}", fontsize=8, color='red')

    plt.axis('off')
    plt.title(f"Grafo: {nome}")
    os.makedirs("grafos_gerados", exist_ok=True)
    plt.savefig(f"grafos_gerados/{nome}.png")
    plt.close()

def calcular_estatisticas(matriz, arestas, arcos, vertices_requeridos):
    """Calcula as estatísticas do grafo."""
    n_vertices = len(matriz)
    grau = [0] * n_vertices

    # Calcula graus para arestas e arcos
    for u, v, _ in arestas:
        grau[u] += 1
        grau[v] += 1
    for u, v, _ in arcos:
        grau[u] += 1

    densidade = (len(arestas) + len(arcos)) / (n_vertices * (n_vertices - 1))
    grau_min = min(grau)
    grau_max = max(grau)

    # Floyd-Warshall para calcular caminhos
    distancias = [[float('inf')] * n_vertices for _ in range(n_vertices)]
    for i in range(n_vertices):
        distancias[i][i] = 0
    for u, v, custo in arestas + arcos:
        distancias[u][v] = custo
        if (u, v, custo) in arestas:  # Arestas são bidirecionais
            distancias[v][u] = custo

    for k in range(n_vertices):
        for i in range(n_vertices):
            for j in range(n_vertices):
                distancias[i][j] = min(distancias[i][j], distancias[i][k] + distancias[k][j])

    soma_caminhos = 0
    num_caminhos = 0
    diametro = 0
    for i in range(n_vertices):
        for j in range(n_vertices):
            if i != j and distancias[i][j] < float('inf'):
                soma_caminhos += distancias[i][j]
                num_caminhos += 1
                diametro = max(diametro, distancias[i][j])

    caminho_medio = soma_caminhos / num_caminhos if num_caminhos else float('inf')

    return {
        "Quantidade de vértices": n_vertices,
        "Quantidade de arestas": len(arestas),
        "Quantidade de arcos": len(arcos),
        "Quantidade de vértices requeridos": len(vertices_requeridos),
        "Quantidade de arestas requeridas": len(arestas),
        "Quantidade de arcos requeridos": len(arcos),
        "Densidade do grafo (order strength)": round(densidade, 4),
        "Grau mínimo dos vértices": grau_min,
        "Grau máximo dos vértices": grau_max,
        "Caminho médio": round(caminho_medio, 4),
        "Diâmetro": diametro
    }

# Processar todos os arquivos .dat em uma pasta
pasta = "selected_instances"
for arquivo in os.listdir(pasta):
    if arquivo.endswith(".dat"):
        caminho = os.path.join(pasta, arquivo)
        matriz, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos, n_vertices, n_arestas, n_arcos = parse_dat_file(caminho)

        # Gera lista de adjacência e desenha o grafo
        grafo = gerar_grafo_como_lista_adjacencia(n_vertices, arestas, arcos)
        nome_instancia = os.path.splitext(arquivo)[0]
        desenhar_grafo(grafo, nome_instancia)

        # Calcula e exibe estatísticas
        estatisticas = calcular_estatisticas(matriz, arestas, arcos, vertices_requeridos)
        print(f"\n📊 Estatísticas do grafo: {nome_instancia}")
        print("=" * 40)
        for chave, valor in estatisticas.items():
            print(f"{chave}: {valor}")
        print("=" * 40)
# Note: Certifique-se de que a função `parse_dat_file` está corretamente implementada e importada.