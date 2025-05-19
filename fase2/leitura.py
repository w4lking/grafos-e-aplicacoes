import re

def ler_cabecalho(linhas):
    """Lê o cabeçalho do arquivo e extrai número de vértices, arestas e arcos."""
    cabecalho = '\n'.join(linhas[:30])  # Considera até 30 linhas para garantir leitura
    n_vertices = int(re.search(r"#Nodes:\s+(\d+)", cabecalho).group(1))
    n_arestas = int(re.search(r"#Edges:\s+(\d+)", cabecalho).group(1))
    n_arcos = int(re.search(r"#Arcs:\s+(\d+)", cabecalho).group(1))
    return n_vertices, n_arestas, n_arcos

def ler_vertices_requeridos(linhas):
    """Extrai os vértices requeridos a partir da seção ReN."""
    vertices = set()
    for linha in linhas:
        if linha.startswith("N"):
            match = re.match(r"N(\d+)", linha)
            if match:
                vertices.add(int(match.group(1)) - 1)
    return vertices

def ler_ligacoes(linhas):
    """Lê arestas ou arcos de uma lista de linhas."""
    ligacoes = []
    for linha in linhas:
        partes = linha.split()
        if len(partes) >= 4:
            try:
                u = int(partes[1]) - 1
                v = int(partes[2]) - 1
                custo = float(partes[3])
                ligacoes.append((u, v, custo))
            except ValueError:
                continue
    return ligacoes

def parse_dat_file(caminho_arquivo):
    with open(caminho_arquivo, 'r') as arquivo:
        linhas = [linha.strip() for linha in arquivo if linha.strip()]

    n_vertices, n_arestas, n_arcos = ler_cabecalho(linhas)

    # Armazenamento por seções
    secoes = {
        "ReN": [],
        "ReE": [],
        "ReA": [],
        "EDGE": [],
        "ARC": []
    }

    secao_atual = None
    for linha in linhas:
        if linha.startswith("ReN."):
            secao_atual = "ReN"
        elif linha.startswith("ReE."):
            secao_atual = "ReE"
        elif linha.startswith("ReA."):
            secao_atual = "ReA"
        elif linha.startswith("EDGE."):
            secao_atual = "EDGE"
        elif linha.startswith("ARC."):
            secao_atual = "ARC"
        elif secao_atual:
            secoes[secao_atual].append(linha)

    # Coleta dos dados
    vertices_requeridos = ler_vertices_requeridos(secoes["ReN"])
    arestas_requeridas = ler_ligacoes(secoes["ReE"])
    arcos_requeridos = ler_ligacoes(secoes["ReA"])
    arestas_opcionais = ler_ligacoes(secoes["EDGE"])
    arcos_opcionais = ler_ligacoes(secoes["ARC"])

    # Concatenação final de arestas e arcos
    arestas = arestas_requeridas + arestas_opcionais
    arcos = arcos_requeridos + arcos_opcionais

    # Geração da matriz de adjacência (com float('inf') para não conexões)
    matriz = [[float('inf')] * n_vertices for _ in range(n_vertices)]
    for i in range(n_vertices):
        matriz[i][i] = 0

    for u, v, custo in arestas:
        matriz[u][v] = custo
        matriz[v][u] = custo
    for u, v, custo in arcos:
        matriz[u][v] = custo  # Direcionado

    return matriz, n_vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos
