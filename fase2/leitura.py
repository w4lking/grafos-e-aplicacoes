import re
import math

def ler_cabecalho(linhas):
    """Lê o cabeçalho do arquivo e extrai número de vértices, arestas, arcos, capacidade e depósito."""
    cabecalho = '\n'.join(linhas[:30])
    n_vertices = int(re.search(r"#Nodes:\s*(\d+)", cabecalho).group(1))
    n_arestas = int(re.search(r"#Edges:\s*(\d+)", cabecalho).group(1)) # Arestas opcionais (total de edges)
    n_arcos = int(re.search(r"#Arcs:\s*(\d+)", cabecalho).group(1)) # Arcos opcionais (total de arcs)
    
    capacidade_match = re.search(r"Capacity:\s*(\d+)", cabecalho)
    capacidade = int(capacidade_match.group(1)) if capacidade_match else -1 # Retorna -1 se não encontrar

    depot_node_match = re.search(r"Depot Node:\s*(\d+)", cabecalho)
    # O depósito é 1-indexed no arquivo, convertemos para 0-indexed para uso interno
    depot_node = int(depot_node_match.group(1)) - 1 if depot_node_match else 0 
    
    # print(f"DEBUG Leitura: Cabeçalho lido - N_Vertices={n_vertices}, Capacidade={capacidade}, Depósito={depot_node+1}")
    return n_vertices, n_arestas, n_arcos, capacidade, depot_node

def ler_vertices_requeridos_com_detalhes(linhas_secao_ren):
    """Extrai os vértices requeridos com suas demandas e custos de serviço."""
    vertices_detalhados = []
    linhas_dados_ren = linhas_secao_ren
    # Pula a linha de cabeçalho da seção se ela estiver presente
    if linhas_dados_ren and "DEMAND" in linhas_dados_ren[0] and "S. COST" in linhas_dados_ren[0]:
        linhas_dados_ren = linhas_dados_ren[1:]

    for linha in linhas_dados_ren:
        partes = linha.split()
        if len(partes) >= 3 and partes[0].startswith("N"):
            try:
                id_no_str = partes[0][1:] # Remove 'N'
                id_no_idx = int(id_no_str) - 1 # Converte para 0-indexed
                demanda = int(partes[1])
                custo_servico = int(partes[2])
                vertices_detalhados.append({
                    "no_idx": id_no_idx,
                    "demanda": demanda,
                    "custo_servico": custo_servico
                })
            except ValueError:
                # print(f"Aviso Leitura (ReN): Não foi possível parsear a linha: '{linha}'")
                continue
    # print(f"DEBUG Leitura: {len(vertices_detalhados)} vértices requeridos lidos.")
    return vertices_detalhados

def ler_ligacoes_requeridas_com_detalhes(linhas_secao, tipo_ligacao="aresta_req"):
    """Lê arestas ou arcos requeridos com custo de travessia, demanda e custo de serviço."""
    ligacoes_detalhadas = []
    linhas_dados = linhas_secao
    # Pula a linha de cabeçalho da seção se ela estiver presente
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
                ligacoes_detalhadas.append({
                    "u": u, "v": v,
                    "custo_travessia": custo_travessia,
                    "demanda": demanda,
                    "custo_servico": custo_servico,
                    "tipo": tipo_ligacao
                })
            except ValueError:
                # print(f"Aviso Leitura ({tipo_ligacao}): Não foi possível parsear a linha: '{linha}'")
                continue
    # print(f"DEBUG Leitura: {len(ligacoes_detalhadas)} ligações requeridas ({tipo_ligacao}) lidas.")
    return ligacoes_detalhadas

def ler_ligacoes_opcionais(linhas_secao):
    """Lê arestas ou arcos opcionais com apenas o custo de travessia."""
    ligacoes = []
    linhas_dados = linhas_secao
    # Pula a linha de cabeçalho da seção se ela estiver presente
    if linhas_dados and "FROM N." in linhas_dados[0].upper():
         linhas_dados = linhas_dados[1:]

    for linha in linhas_dados:
        partes = linha.split()
        idx_offset = 0
        # Verifica se o primeiro elemento é um ID não numérico (ex: 'NrA1')
        if partes and not partes[0].replace('.','',1).isdigit():
            idx_offset = 1
            if len(partes) < 4: # Se tem ID, precisa de pelo menos 4 partes (ID, u, v, custo)
                # print(f"Aviso Leitura (Opcional - Formato): Linha muito curta para ID e dados: '{linha}'")
                continue
        elif len(partes) < 3: # Se não tem ID, precisa de pelo menos 3 partes (u, v, custo)
            # print(f"Aviso Leitura (Opcional - Formato): Linha muito curta para dados: '{linha}'")
            continue
        
        try:
            u = int(partes[idx_offset + 0]) - 1 # Converte para 0-indexed
            v = int(partes[idx_offset + 1]) - 1 # Converte para 0-indexed
            custo = float(partes[idx_offset + 2])
            ligacoes.append((u, v, custo))
        except ValueError:
            # print(f"Aviso Leitura (Opcional - Valor): Não foi possível parsear a linha: '{linha}'")
            continue
    # print(f"DEBUG Leitura: {len(ligacoes)} ligações opcionais lidas.")
    return ligacoes

def parse_dat_file(caminho_arquivo):
    """
    Função principal para parsear o arquivo .dat e extrair todas as informações do grafo.
    Retorna: matriz de adjacência, número de vértices, capacidade do veículo,
    índice do depósito, e listas detalhadas de serviços requeridos e ligações opcionais.
    """
    # print(f"DEBUG Leitura: Iniciando parse de '{caminho_arquivo}'")
    with open(caminho_arquivo, 'r') as arquivo:
        linhas = [linha.strip() for linha in arquivo if linha.strip()]

    n_vertices, n_arestas_opcionais_total, n_arcos_opcionais_total, capacidade_veiculo, depot_idx = ler_cabecalho(linhas)

    # Armazeno por seções
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

    # Coleta dos dados mais detalhados
    vertices_requeridos_detalhes = ler_vertices_requeridos_com_detalhes(secoes["ReN"])
    arestas_requeridas_detalhes = ler_ligacoes_requeridas_com_detalhes(secoes["ReE"], "aresta_req")
    arcos_requeridos_detalhes = ler_ligacoes_requeridas_com_detalhes(secoes["ReA"], "arco_req")
    arestas_opcionais_travessia = ler_ligacoes_opcionais(secoes["EDGE"])
    arcos_opcionais_travessia = ler_ligacoes_opcionais(secoes["ARC"])

    # Geração da matriz de adjacência (com float('inf') para não conexões)
    matriz = [[math.inf] * n_vertices for _ in range(n_vertices)]
    for i in range(n_vertices):
        matriz[i][i] = 0 # Custo zero para ir de um nó para ele mesmo. Posso mudar isso dps, Tarko ;|

    # Adicionar custos de travessia das arestas requeridas
    for aresta_req in arestas_requeridas_detalhes:
        u, v, custo_t = aresta_req["u"], aresta_req["v"], aresta_req["custo_travessia"]
        matriz[u][v] = min(matriz[u][v], custo_t) # Usa min para lidar com múltiplas arestas/arcos
        matriz[v][u] = min(matriz[v][u], custo_t) # Arestas são bidirecionais

    # Adicionar custos de travessia das arestas opcionais
    for u, v, custo_t in arestas_opcionais_travessia:
        matriz[u][v] = min(matriz[u][v], custo_t)
        matriz[v][u] = min(matriz[v][u], custo_t)

    # Adicionar custos de travessia dos arcos requeridos
    for arco_req in arcos_requeridos_detalhes:
        u, v, custo_t = arco_req["u"], arco_req["v"], arco_req["custo_travessia"]
        matriz[u][v] = min(matriz[u][v], custo_t) # Arcos são direcionais

    # Adicionar custos de travessia dos arcos opcionais
    for u, v, custo_t in arcos_opcionais_travessia:
        matriz[u][v] = min(matriz[u][v], custo_t) # Arcos são direcionais

    # print(f"DEBUG Leitura: Matriz de adjacência construída para {n_vertices} vértices.")
    # Exemplo de print da matriz (apenas uma amostra para não sobrecarregar)
    # for r_idx in range(min(5, n_vertices)):
    #     print(f"  Matriz linha {r_idx}: {[f'{val:.1f}' if val != math.inf else 'inf' for val in matriz[r_idx][:min(5, n_vertices)]]}...")

    # Retorna todas as informações parseadas
    # print(f"DEBUG Leitura: Parse de '{caminho_arquivo}' concluído. Retornando dados.")
    return (matriz, n_vertices, capacidade_veiculo, depot_idx,
            vertices_requeridos_detalhes, 
            arestas_requeridas_detalhes, 
            arcos_requeridos_detalhes,
            arestas_opcionais_travessia, 
            arcos_opcionais_travessia)