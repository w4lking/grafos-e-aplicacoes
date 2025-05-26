# fase2/main.py
import os
import sys
import time
import math # Para uso em Dijkstra
import heapq # Para a fila de prioridade de Dijkstra

current_file_dir = os.path.dirname(os.path.abspath(__file__)) # Diretório de main.py (fase2/)
project_root_dir = os.path.dirname(current_file_dir) # Diretório pai (GRAFOS-E-APLICACOES/)
sys.path.insert(0, project_root_dir) # Adiciona ao início do path de busca de módulos

# importando módulos
from leitura import parse_dat_file
from algoritmos.dijkstra import dijkstra # Ainda importa
from algoritmos.floyd_warshall import floyd_warshall # Importado para o APSP
from algoritmos.path_scanning import meu_algoritmo_construtivo

def main():
    pasta_instancias = os.path.join(current_file_dir, "dados", "MCGRP")
    pasta_saida = os.path.join(current_file_dir, "solucoes")
    os.makedirs(pasta_saida, exist_ok=True)

    print(f"Procurando instâncias em: {pasta_instancias}")

    arquivos_para_processar = []
    salvar_solucao_para_este_arquivo = True # Flag de salvamento

    # --- Opção de processamento ---
    escolha_processamento = input("Deseja processar TODOS os arquivos (.dat) ou um ESPECÍFICO? (digite 'todos' ou 'especifico'): ").strip().lower()
    
    if escolha_processamento == 't' or escolha_processamento == 'todos' or escolha_processamento == 'tudo':
        print("Modo: Processando todos os arquivos .dat na pasta...")
        for arquivo_nome in os.listdir(pasta_instancias):
            if arquivo_nome.endswith(".dat"):
                arquivos_para_processar.append(arquivo_nome)
        # No modo 'todos', sempre salvamos a solução
        salvar_solucao_para_este_arquivo = True 
    elif escolha_processamento == 'e' or escolha_processamento == 'especifico':
        arquivo_especifico_nome = input("Digite o NOME do arquivo .dat específico (ex: BHW1.dat): ").strip()
        if not arquivo_especifico_nome.lower().endswith(".dat"):
            arquivo_especifico_nome += ".dat" 
        
        caminho_arquivo_especifico = os.path.join(pasta_instancias, arquivo_especifico_nome)
        if os.path.exists(caminho_arquivo_especifico):
            arquivos_para_processar.append(arquivo_especifico_nome)
            print(f"Modo: Processando arquivo específico: {arquivo_especifico_nome}")
            
            # Pergunta se deseja salvar a solução para este arquivo específico
            salvar_escolha = input(f"Deseja salvar a solução para '{arquivo_especifico_nome}'? (s/n): ").strip().lower()
            salvar_solucao_para_este_arquivo = (salvar_escolha == 's')
        else:
            print(f"ERRO: Arquivo '{arquivo_especifico_nome}' não encontrado em '{pasta_instancias}'. Encerrando.")
            return # Sai da função main se o arquivo não for encontrado
    else:
        print("Opção inválida. Por favor, digite 'todos' ou 'especifico'. Encerrando.")
        return

    # --- Loop de processamento ---
    if not arquivos_para_processar:
        print("Nenhum arquivo .dat encontrado para processar.")
        return

    for arquivo_nome in arquivos_para_processar:
        caminho_completo_instancia = os.path.join(pasta_instancias, arquivo_nome)
        print(f"\n--- Processando instância: {arquivo_nome} ---")

        try:
            # 1. Leitura dos dados
            (matriz_adj, n_vertices, capacidade_veiculo, depot_idx,
             vertices_requeridos_detalhes, 
             arestas_requeridas_detalhes, 
             arcos_requeridos_detalhes,
             arestas_opcionais_travessia, 
             arcos_opcionais_travessia) = parse_dat_file(caminho_completo_instancia)
        except Exception as e:
            print(f"  ERRO ao ler a instância {arquivo_nome}: {e}")
            import traceback
            traceback.print_exc() 
            continue

        if capacidade_veiculo == -1:
            print(f"  AVISO: Capacidade do veículo não encontrada ou inválida para {arquivo_nome}. Pulando.")
            continue
        
        print(f"  Dados lidos: {n_vertices} vértices, Capacidade={capacidade_veiculo}, Depósito={depot_idx+1}")
        # print(f"  DEBUG Main: {len(vertices_requeridos_detalhes)} ReN, {len(arestas_requeridas_detalhes)} ReE, {len(arcos_requeridos_detalhes)} ReA")
        # print(f"  DEBUG Main: {len(arestas_opcionais_travessia)} EDGE, {len(arcos_opcionais_travessia)} ARC")

        # NOVO PASSO: Pré-calcular todas as distâncias de caminho mínimo com Floyd-Warshall
        print(f"  Calculando todas as distâncias de caminho mínimo (Floyd-Warshall) para {n_vertices} vértices...")
        inicio_floyd = time.monotonic_ns()
        distancias_apsp = floyd_warshall(matriz_adj)
        fim_floyd = time.monotonic_ns()
        print(f"  Cálculo de todas as distâncias concluído em {(fim_floyd - inicio_floyd) / 1e9:.4f}s.")

        # 2. Preparar a lista unificada de serviços
        todos_os_servicos_pendentes = []
        id_servico_unico_contador = 1 

        for v_req in vertices_requeridos_detalhes:
            todos_os_servicos_pendentes.append({
                "id_output": id_servico_unico_contador,
                "tipo": "no", "nome_original": f"N{v_req['no_idx']+1}", 
                "definicao_original": v_req,
                "no_inicial_acesso": v_req["no_idx"],
                "no_final_apos_servico": v_req["no_idx"],
                "demanda": v_req["demanda"],
                "custo_servico_proprio": v_req["custo_servico"],
                "custo_travessia_interno": 0
            })
            id_servico_unico_contador += 1
        
        for idx_aresta, a_req in enumerate(arestas_requeridas_detalhes):
            todos_os_servicos_pendentes.append({
                "id_output": id_servico_unico_contador,
                "tipo": "aresta", "nome_original": f"E{idx_aresta+1}", 
                "definicao_original": a_req, 
                "no_inicial_acesso": a_req["u"],
                "no_final_apos_servico": a_req["v"], 
                "demanda": a_req["demanda"],
                "custo_servico_proprio": a_req["custo_servico"],
                "custo_travessia_interno": a_req["custo_travessia"]
            })
            id_servico_unico_contador += 1

        for idx_arco, arc_req in enumerate(arcos_requeridos_detalhes):
             todos_os_servicos_pendentes.append({
                "id_output": id_servico_unico_contador,
                "tipo": "arco", "nome_original": f"A{idx_arco+1}", 
                "definicao_original": arc_req,
                "no_inicial_acesso": arc_req["u"],
                "no_final_apos_servico": arc_req["v"],
                "demanda": arc_req["demanda"],
                "custo_servico_proprio": arc_req["custo_servico"],
                "custo_travessia_interno": arc_req["custo_travessia"]
            })
             id_servico_unico_contador += 1
        
        print(f"  Total de serviços requeridos a processar: {len(todos_os_servicos_pendentes)}")

        # DEBUG: Verificando a matriz de distâncias APSP
        # print("  DEBUG Main: Amostra da matriz de distâncias APSP (primeiras 5x5 células):")
        # for r_idx in range(min(5, n_vertices)):
        #     row_str = "    "
        #     for c_idx in range(min(5, n_vertices)):
        #         val = distancias_apsp[r_idx][c_idx]
        #         if val == math.inf:
        #             row_str += "inf "
        #         else:
        #             row_str += f"{val:<4.0f}" 
        #     print(row_str)
        
        # print("  DEBUG Main: Verificando todos_os_servicos_pendentes (primeiros 5 e tipos) antes do algoritmo:")
        # for i, serv in enumerate(todos_os_servicos_pendentes[:5]): 
        #     print(f"    Serviço {i} (ID Output: {serv['id_output']}):")
        #     for k, v in serv.items():
        #         if k in ["no_inicial_acesso", "no_final_apos_servico", "demanda", "custo_servico_proprio", "custo_travessia_interno"]:
        #             if not isinstance(v, (int, float)):
        #                 print(f"      ALERTA TIPO SERVIÇO: {k} = {v} (tipo: {type(v)})")

        # Verificação de alcançabilidade dos serviços a partir do depósito (usando APSP)
        print(f"  Verificando alcançabilidade dos serviços a partir do depósito {depot_idx+1} (usando APSP)...")
        unreachable_services_from_depot = []
        for serv in todos_os_servicos_pendentes:
            no_acesso = serv["no_inicial_acesso"]
            cost_from_depot = distancias_apsp[depot_idx][no_acesso]
            if cost_from_depot == math.inf:
                unreachable_services_from_depot.append(serv["nome_original"])
        
        if unreachable_services_from_depot:
            print(f"  ALERTA CONECTIVIDADE ({arquivo_nome}): Os seguintes serviços são INALCANÇÁVEIS do depósito: {', '.join(unreachable_services_from_depot)}")
            print(f"  Isso pode causar lentidão e rotas incompletas. Verifique a estrutura do grafo ou a lógica de leitura.")
        else:
            print(f"  Todos os {len(todos_os_servicos_pendentes)} serviços são alcançáveis do depósito.")


        # 3. Chamar seu novo algoritmo construtivo
        try:
            custo_total_sol, num_rotas_sol, clocks_sol, rotas_finais_sol, tempo_total_s_sol = meu_algoritmo_construtivo(
                distancias_apsp, 
                capacidade_veiculo,
                depot_idx,
                todos_os_servicos_pendentes,
                n_vertices,
                arquivo_nome_debug=arquivo_nome 
            )
            print(f"  Solução construída: Custo={custo_total_sol:.2f}, Rotas={num_rotas_sol}, Tempo={tempo_total_s_sol:.4f}s")

        except Exception as e:
            print(f"  ERRO ao executar o algoritmo construtivo para {arquivo_nome}: {e}")
            import traceback
            traceback.print_exc()
            continue

        # 4. Escrita no arquivo de saída (condicional)
        if salvar_solucao_para_este_arquivo: # Verifica a flag antes de salvar
            nome_arquivo_saida = f"sol-{os.path.splitext(arquivo_nome)[0]}.dat"
            caminho_saida = os.path.join(pasta_saida, nome_arquivo_saida)

            try:
                with open(caminho_saida, "w") as f_out:
                    f_out.write(f"{custo_total_sol:.2f}\n")
                    f_out.write(f"{num_rotas_sol}\n")
                    f_out.write(f"{int(clocks_sol)}\n") 
                    f_out.write(f"{int(tempo_total_s_sol * 1e9)}\n")

                    for rota_info in rotas_finais_sol:
                        f_out.write(f"{rota_info['id_rota_output']} {rota_info['demanda_total_rota_output']:.0f} {rota_info['custo_total_rota_output']:.2f} {rota_info['total_visitas_output']} {rota_info['trajeto_string_output']}\n")
                print(f"  Solução salva em: {caminho_saida}")
            except Exception as e:
                print(f"  ERRO ao salvar a solução para {arquivo_nome}: {e}")
        else:
            print(f"  Solução para '{arquivo_nome}' não foi salva conforme sua escolha.")
        
if __name__ == "__main__":
    main()
