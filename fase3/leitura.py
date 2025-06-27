import re
import math
from modelos.instancia import Instancia, VerticeRequerido, LigacaoRequerida, LigacaoOpcional

def ler_cabecalho(linhas):
    """Lê o cabeçalho do arquivo e extrai número de vértices, arestas, arcos, capacidade e depósito."""
    cabecalho = '\n'.join(linhas[:30])
    
    nome_match = re.search(r"Name:\s*([^\n]+)", cabecalho)
    nome = nome_match.group(1).strip() if nome_match else "Desconhecido"

    n_vertices = int(re.search(r"#Nodes:\s*(\d+)", cabecalho).group(1))
    n_arestas = int(re.search(r"#Edges:\s*(\d+)", cabecalho).group(1)) # Arestas opcionais (total de edges)
    n_arcos = int(re.search(r"#Arcs:\s*(\d+)", cabecalho).group(1)) # Arcos opcionais (total de arcs)
    
    capacidade_match = re.search(r"Capacity:\s*(\d+)", cabecalho)
    capacidade = int(capacidade_match.group(1)) if capacidade_match else -1 # Retorna -1 se não encontrar

    depot_node_match = re.search(r"Depot Node:\s*(\d+)", cabecalho)
    # O depósito é 1-indexed no arquivo, convertemos para 0-indexed para uso interno
    depot_node = int(depot_node_match.group(1)) - 1 if depot_node_match else 0 
    
    return nome, n_vertices, n_arestas, n_arcos, capacidade, depot_node

def ler_vertices_requeridos_com_detalhes(linhas_secao_ren):
    """Extrai os vértices requeridos com suas demandas e custos de serviço."""
    vertices_detalhados = []
    linhas_dados_ren = linhas_secao_ren
    if linhas_dados_ren and "DEMAND" in linhas_dados_ren[0] and "S. COST" in linhas_dados_ren[0]:
        linhas_dados_ren = linhas_dados_ren[1:]

    for linha in linhas_dados_ren:
        partes = linha.split()
        if len(partes) >= 3 and partes[0].startswith("N"):
            try:
                id_no_str = partes[0][1:] # Remove 'N'
                no_idx = int(id_no_str) - 1 # Converte para 0-indexed
                demanda = int(partes[1])
                custo_servico = int(partes[2])
                vertices_detalhados.append(VerticeRequerido(no_idx, demanda, custo_servico))
            except ValueError:
                # print(f"Aviso Leitura (ReN): Não foi possível parsear a linha: '{linha}'")
                continue
    return vertices_detalhados

def ler_ligacoes_requeridas_com_detalhes(linhas_secao, tipo_ligacao="aresta_req"):
    """Lê arestas ou arcos requeridos com custo de travessia, demanda e custo de serviço."""
    ligacoes_detalhadas = []
    linhas_dados = linhas_secao
    if linhas_dados and "From N." in linhas_dados[0]:
         linhas_dados = linhas_dados[1:]

    for linha in linhas_dados:
        partes = linha.split()
        if len(partes) >= 6: # ID, From, To, T.COST, DEMAND, S.COST
            try:
                u = int(partes[1]) - 1 # Converte para 0-indexed
                v = int(partes[2]) - 1 # Converte para 0-indexed
                custo_travessia = float(partes[3])
                demanda = int(partes[4])
                custo_servico = int(partes[5])
                ligacoes_detalhadas.append(LigacaoRequerida(u, v, custo_travessia, demanda, custo_servico, tipo_ligacao))
            except ValueError:
                # print(f"Aviso Leitura ({tipo_ligacao}): Não foi possível parsear a linha: '{linha}'")
                continue
    return ligacoes_detalhadas

def ler_ligacoes_opcionais(linhas_secao):
    """Lê arestas ou arcos opcionais com apenas o custo de travessia."""
    ligacoes = []
    linhas_dados = linhas_secao
    if linhas_dados and "FROM N." in linhas_dados[0].upper():
         linhas_dados = linhas_dados[1:]

    for linha in linhas_dados:
        partes = linha.split()
        idx_offset = 0
        if partes and not partes[0].replace('.','',1).isdigit():
            idx_offset = 1
            if len(partes) < 4:
                continue
        elif len(partes) < 3:
            continue
        
        try:
            u = int(partes[idx_offset + 0]) - 1 # Converte para 0-indexed
            v = int(partes[idx_offset + 1]) - 1 # Converte para 0-indexed
            custo = float(partes[idx_offset + 2])
            ligacoes.append(LigacaoOpcional(u, v, custo))
        except ValueError:
            # print(f"Aviso Leitura (Opcional - Valor): Não foi possível parsear a linha: '{linha}'")
            continue
    return ligacoes

def parse_dat_file(caminho_arquivo) -> Instancia:
    """
    Função principal para parsear o arquivo .dat e extrair todas as informações do grafo.
    Retorna um objeto Instancia contendo todos os dados.
    """
    with open(caminho_arquivo, 'r') as arquivo:
        linhas = [linha.strip() for linha in arquivo if linha.strip()]

    nome_instancia, n_vertices, n_arestas_opcionais_total, n_arcos_opcionais_total, capacidade_veiculo, depot_idx = ler_cabecalho(linhas)

    secoes = {
        "ReN": [], "ReE": [], "ReA": [], "EDGE": [], "ARC": []
    }

    secao_atual = None
    for linha in linhas:
        if linha.startswith("ReN."): secao_atual = "ReN"
        elif linha.startswith("ReE."): secao_atual = "ReE"
        elif linha.startswith("ReA."): secao_atual = "ReA"
        elif linha.startswith("EDGE."): secao_atual = "EDGE"
        elif linha.startswith("ARC."): secao_atual = "ARC"
        elif secao_atual: secoes[secao_atual].append(linha)

    vertices_requeridos_detalhes = ler_vertices_requeridos_com_detalhes(secoes["ReN"])
    arestas_requeridas_detalhes = ler_ligacoes_requeridas_com_detalhes(secoes["ReE"], "aresta_req")
    arcos_requeridos_detalhes = ler_ligacoes_requeridas_com_detalhes(secoes["ReA"], "arco_req")
    arestas_opcionais_travessia = ler_ligacoes_opcionais(secoes["EDGE"])
    arcos_opcionais_travessia = ler_ligacoes_opcionais(secoes["ARC"])

    matriz = [[math.inf] * n_vertices for _ in range(n_vertices)]
    for i in range(n_vertices):
        matriz[i][i] = 0 

    for aresta_req in arestas_requeridas_detalhes:
        u, v, custo_t = aresta_req.u, aresta_req.v, aresta_req.custo_travessia
        matriz[u][v] = min(matriz[u][v], custo_t)
        matriz[v][u] = min(matriz[v][u], custo_t)

    for u, v, custo_t in arestas_opcionais_travessia:
        matriz[u][v] = min(matriz[u][v], custo_t)
        matriz[v][u] = min(matriz[v][u], custo_t)

    for arco_req in arcos_requeridos_detalhes:
        u, v, custo_t = arco_req.u, arco_req.v, arco_req.custo_travessia
        matriz[u][v] = min(matriz[u][v], custo_t)

    for u, v, custo_t in arcos_opcionais_travessia:
        matriz[u][v] = min(matriz[u][v], custo_t)

    return Instancia(
        nome=nome_instancia,
        n_vertices=n_vertices,
        capacidade_veiculo=capacidade_veiculo,
        depot_idx=depot_idx,
        vertices_requeridos_detalhes=vertices_requeridos_detalhes,
        arestas_requeridas_detalhes=arestas_requeridas_detalhes,
        arcos_requeridos_detalhes=arcos_requeridos_detalhes,
        arestas_opcionais_travessia=arestas_opcionais_travessia,
        arcos_opcionais_travessia=arcos_opcionais_travessia,
        matriz_adj=matriz
    )
