import re

def parse_dat_file(path_arquivo):
    with open(path_arquivo, 'r') as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    n_vertices = int(re.search(r"#Nodes:\s+(\d+)", '\n'.join(linhas)).group(1))

    matriz = [[float('inf')] * n_vertices for _ in range(n_vertices)]
    for i in range(n_vertices):
        matriz[i][i] = 0

    arestas = []
    arcos = []
    vertices_requeridos = set()

    lendo_arestas = False
    lendo_arcos = False

    for linha in linhas:
        if linha.startswith("ReE."):
            lendo_arestas = True
            lendo_arcos = False
            continue
        elif linha.startswith("ReA."):
            lendo_arestas = False
            lendo_arcos = True
            continue
        elif linha.startswith("ARC") or linha.startswith("EDGE") or linha.startswith("the data"):
            lendo_arestas = False
            lendo_arcos = False
            continue

        if lendo_arestas:
            parts = linha.split()
            _, u, v, custo, demanda, _ = parts
            u, v, custo = int(u), int(v), float(custo)
            matriz[u - 1][v - 1] = custo
            matriz[v - 1][u - 1] = custo
            arestas.append((u - 1, v - 1, custo))
            vertices_requeridos.update([u - 1, v - 1])
        elif lendo_arcos:
            parts = linha.split()
            _, u, v, custo, demanda, _ = parts
            u, v, custo = int(u), int(v), float(custo)
            matriz[u - 1][v - 1] = custo
            arcos.append((u - 1, v - 1, custo))
            vertices_requeridos.update([u - 1, v - 1])

    return matriz, arestas, arcos, n_vertices, vertices_requeridos
