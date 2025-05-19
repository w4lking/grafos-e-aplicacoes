import matplotlib.pyplot as plt
import math

# Função para criar um grafo como lista de adjacência
def gerar_grafo_como_lista_adjacencia(n_vertices, arestas, arcos):
    grafo = {v: [] for v in range(n_vertices)}  # Inicializa o grafo
    for u, v, custo in arestas:
        grafo[u].append((v, custo))  # Adiciona arestas bidirecionais
        grafo[v].append((u, custo))  # Arestas são bidirecionais
    for u, v, custo in arcos:
        grafo[u].append((v, custo))  # Adiciona arcos unidirecionais
    return grafo

# Função para desenhar um grafo no notebook
def desenhar_grafo_no_notebook(grafo, nome, vertices_requeridos, arestas_requeridas, arcos_requeridos):
    num_vertices = len(grafo)
    angulo = 2 * math.pi / num_vertices  # Determina a posição circular dos vértices
    posicoes = {v: (math.cos(i * angulo), math.sin(i * angulo)) for i, v in enumerate(grafo)}
    
    plt.figure(figsize=(10, 8))

    # Desenho de arestas e arcos com descrições
    for v, vizinhos in grafo.items():
        x, y = posicoes[v]
        for u, peso in vizinhos:
            x2, y2 = posicoes[u]
            cor = 'gray'  # Cor padrão: não requerida
            estilo = '-'  # Estilo padrão: aresta
            alpha = 0.5

            if (v, u, peso) in arestas_requeridas or (u, v, peso) in arestas_requeridas:
                cor = 'blue'  # Arestas requeridas em azul
            elif (v, u, peso) in arcos_requeridos or (u, v, peso) in arcos_requeridos:
                cor = 'green'  # Arcos requeridos em verde
                estilo = '--'  # Arcos são desenhados com linhas tracejadas
            
            plt.plot([x, x2], [y, y2], linestyle=estilo, color=cor, alpha=alpha)
            mx, my = (x + x2) / 2, (y + y2) / 2
            plt.text(mx, my, f"{peso:.0f}", fontsize=8, color='red')  # Mostra o peso na aresta ou arco

    # Desenho de vértices
    for v, (x, y) in posicoes.items():
        cor_vertice = 'purple' if v in vertices_requeridos else 'skyblue'
        plt.plot(x, y, 'o', color=cor_vertice, markersize=10)
        plt.text(x, y, str(v + 1), fontsize=10, ha='center', va='center', color='white')  # Identifica os vértices com números

    # Título e descrição adicional do grafo
    plt.title(f"Grafo: {nome}", fontsize=16)
    descricao = f"""Vertices relevantes (ReN): {', '.join(map(str, [v + 1 for v in vertices_requeridos]))}
    Arestas requeridas (ReE): {len(arestas_requeridas)} (em azul)
    Arcos requeridos (ReA): {len(arcos_requeridos)} (em verde)"""
    plt.gcf().text(0.1, 0.02, descricao, fontsize=10)

    # Remove os eixos e exibe o grafo no notebook
    plt.axis('off')
    plt.show()  # Exibe diretamente no notebook
