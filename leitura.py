import os
import re

# Funções de leitura (as mesmas que você já fez)
def ler_cabecalho(linhas):
    cabecalho = '\n'.join(linhas[:30])
    n_vertices = int(re.search(r"#Nodes:\s+(\d+)", cabecalho).group(1))
    n_arestas = int(re.search(r"#Edges:\s+(\d+)", cabecalho).group(1))
    n_arcos = int(re.search(r"#Arcs:\s+(\d+)", cabecalho).group(1))
    return n_vertices, n_arestas, n_arcos

def ler_vertices_requeridos(sub_linhas):
    vertices_requeridos = set()
    for linha in sub_linhas:
        if linha.startswith("N"):
            id_str = re.match(r"N(\d+)", linha)
            if id_str:
                id_vertice = int(id_str.group(1)) - 1
                vertices_requeridos.add(id_vertice)
    return vertices_requeridos

def ler_arestas(sub_linhas):
    arestas = []
    for linha in sub_linhas:
        try:
            _, u, v, custo, _, _ = linha.split()
            u, v, custo = int(u), int(v), float(custo)
            arestas.append((u - 1, v - 1, custo))
        except ValueError:
            continue
    return arestas

def ler_arcos(sub_linhas):
    arcos = []
    for linha in sub_linhas:
        try:
            _, u, v, custo, _, _ = linha.split()
            u, v, custo = int(u), int(v), float(custo)
            arcos.append((u - 1, v - 1, custo))
        except ValueError:
            continue
    return arcos

def parse_dat_file(caminho_arquivo):
    with open(caminho_arquivo, 'r') as arquivo:
        linhas = [linha.strip() for linha in arquivo if linha.strip()]

    n_vertices, n_arestas, n_arcos = ler_cabecalho(linhas)

    vertices_requeridos = set()
    arestas = []
    arcos = []
    arestas_requeridas = []
    arcos_requeridos = []

    lendo_secao = None
    secao_linhas = {"ReN": [], "ReE": [], "ReA": [], "EDGE": [], "ARC": []}

    for linha in linhas:
        if linha.startswith("ReN."):
            lendo_secao = "ReN"
        elif linha.startswith("ReE."):
            lendo_secao = "ReE"
        elif linha.startswith("ReA."):
            lendo_secao = "ReA"
        elif linha.startswith("EDGE."):
            lendo_secao = "EDGE"
        elif linha.startswith("ARC."):
            lendo_secao = "ARC"
        elif lendo_secao:
            secao_linhas[lendo_secao].append(linha)

    vertices_requeridos = ler_vertices_requeridos(secao_linhas["ReN"])
    arestas = ler_arestas(secao_linhas["ReE"] + secao_linhas["EDGE"])
    arcos = ler_arcos(secao_linhas["ReA"] + secao_linhas["ARC"])
    arestas_requeridas = ler_arestas(secao_linhas["ReE"])
    arcos_requeridos = ler_arcos(secao_linhas["ReA"])

    matriz = [[float('inf')] * n_vertices for _ in range(n_vertices)]
    for i in range(n_vertices):
        matriz[i][i] = 0

    for u, v, custo in arestas:
        matriz[u][v] = custo
        matriz[v][u] = custo
    for u, v, custo in arcos:
        matriz[u][v] = custo

    return matriz, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos, n_vertices, n_arestas, n_arcos
