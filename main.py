import os
import math
import matplotlib.pyplot as plt
from leitura import parse_dat_file
from estatisticas import calcular_estatisticas


def gerar_lista_adjacencia(n_vertices, arestas, arcos):
    grafo = {v: [] for v in range(n_vertices)}

    for u, v, custo in arestas:
        grafo[u].append((v, custo))
        grafo[v].append((u, custo))  # Arestas são não direcionadas

    for u, v, custo in arcos:
        grafo[u].append((v, custo))  # Arcos são direcionados

    return grafo


def desenhar_grafo(grafo, nome_arquivo):
    angulo = 2 * math.pi / len(grafo)
    posicoes = {
        v: (math.cos(i * angulo), math.sin(i * angulo))
        for i, v in enumerate(grafo)
    }

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
    plt.title(f"Grafo: {nome_arquivo}")
    os.makedirs("grafos_gerados", exist_ok=True)
    plt.savefig(f"grafos_gerados/{nome_arquivo}.png")
    plt.close()


def processa_grafo(path_arquivo):
    # Faz o parsing do .dat
    matriz, arestas_total, arcos_total, arestas_req, arcos_req, n_vertices, vertices_req = parse_dat_file(path_arquivo)

    # Gera a lista de adjacência
    grafo = gerar_lista_adjacencia(n_vertices, arestas_total, arcos_total)

    # Nome base da instância
    nome_base = os.path.splitext(os.path.basename(path_arquivo))[0]

    # Desenhar e salvar imagem
    desenhar_grafo(grafo, nome_base)

    # Calcula e imprime estatísticas
    estatisticas = calcular_estatisticas(
        matriz, arestas_total, arcos_total, arestas_req, arcos_req, vertices_req
    )

    print(f"\n📄 Estatísticas do grafo: {nome_base}")
    print("=" * 40)
    for chave, valor in estatisticas.items():
        print(f"{chave}: {valor}")
    print("=" * 40)


if __name__ == "__main__":
    pasta = "selected_instances"
    arquivos_dat = [f for f in os.listdir(pasta) if f.endswith(".dat")]

    for arquivo in arquivos_dat:
        caminho = os.path.join(pasta, arquivo)
        processa_grafo(caminho)
