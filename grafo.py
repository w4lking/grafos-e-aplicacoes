import os
import matplotlib.pyplot as plt
import math

def gerar_grafo_como_lista_adjacencia(n_vertices, arestas, arcos):
    grafo = {v: [] for v in range(n_vertices)}
    for u, v, custo in arestas:
        grafo[u].append((v, custo))
        grafo[v].append((u, custo))  # Arestas são bidirecionais
    for u, v, custo in arcos:
        grafo[u].append((v, custo))  # Arcos são direcionais
    return grafo

def desenhar_grafo(grafo, nome, vertices_requeridos, arestas_requeridas, arcos_requeridos):
    num_vertices = len(grafo)
    angulo = 2 * math.pi / num_vertices
    posicoes = {v: (math.cos(i * angulo), math.sin(i * angulo)) for i, v in enumerate(grafo)}
    
    plt.figure(figsize=(10, 8))

    # Desenho de arestas e arcos
    for v, vizinhos in grafo.items():
        x, y = posicoes[v]
        for u, peso in vizinhos:
            x2, y2 = posicoes[u]
            cor = 'gray'  # Padrão: não requerida
            estilo = '-'  # Padrão: aresta
            alpha = 0.5

            if (v, u, peso) in arestas_requeridas or (u, v, peso) in arestas_requeridas:
                cor = 'blue'
            elif (v, u, peso) in arcos_requeridos or (u, v, peso) in arcos_requeridos:
                cor = 'green'
                estilo = '--'  # Direção (arcos)
            
            plt.plot([x, x2], [y, y2], linestyle=estilo, color=cor, alpha=alpha)
            mx, my = (x + x2) / 2, (y + y2) / 2
            plt.text(mx, my, f"{peso:.0f}", fontsize=8, color='red')

    # Desenho de vértices
    for v, (x, y) in posicoes.items():
        cor_vertice = 'purple' if v in vertices_requeridos else 'skyblue'
        plt.plot(x, y, 'o', color=cor_vertice, markersize=10)
        plt.text(x, y, str(v + 1), fontsize=10, ha='center', va='center', color='white')

    # Título e descrição
    plt.title(f"Grafo: {nome}", fontsize=16)
    descricao = f"""Vertices relevantes (ReN): {', '.join(map(str, [v + 1 for v in vertices_requeridos]))}
    Arestas requeridas (ReE): {len(arestas_requeridas)}
    Arcos requeridos (ReA): {len(arcos_requeridos)}"""
    plt.gcf().text(0.1, 0.02, descricao, fontsize=10)

    plt.axis('off')
    os.makedirs("grafos_gerados", exist_ok=True)
    plt.savefig(f"grafos_gerados/{nome}.png")
    plt.close()
