# fase2/main.py
import os
import sys
import time
import math # Para uso em Dijkstra ou no seu algoritmo
import heapq # Para a fila de prioridade de Dijkstra (ainda necessário para Dijkstra individual)

current_file_dir = os.path.dirname(os.path.abspath(__file__)) # Diretório de main.py (fase2/)
project_root_dir = os.path.dirname(current_file_dir) # Diretório pai (GRAFOS-E-APLICACOES/)
sys.path.insert(0, project_root_dir) # Adiciona ao início do path de busca de módulos

# importando módulos
from leitura import parse_dat_file
from algoritmos.dijkstra import dijkstra # Ainda importamos, mas será menos usado
from algoritmos.floyd_warshall import floyd_warshall # NOVO IMPORT
from algoritmos.path_scanning import meu_algoritmo_construtivo

def main():
    pasta_instancias = os.path.join(current_file_dir, "dados", "MCGRP")
    pasta_saida = os.path.join(current_file_dir, "solucoes")
    os.makedirs(pasta_saida, exist_ok=True)

    print(f"Procurando instâncias em: {pasta_instancias}")

    for arquivo_nome in os.listdir(pasta_instancias):
        if arquivo_nome.endswith(".dat"):
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
            print(f"  DEBUG Main: {len(vertices_requeridos_detalhes)} ReN, {len(arestas_requeridas_detalhes)} ReE, {len(arcos_requeridos_detalhes)} ReA")
            print(f"  DEBUG Main: {len(arestas_opcionais_travessia)} EDGE, {len(arcos_opcionais_travessia)} ARC")

            # NOVO PASSO: Pré-calcular todas as distâncias de caminho mínimo com Floyd-Warshall
            print(f"  DEBUG Main: Calculando todas as distâncias de caminho mínimo (Floyd-Warshall) para {n_vertices} vértices...")
            inicio_floyd = time.monotonic_ns()
            distancias_apsp = floyd_warshall(matriz_adj)
            fim_floyd = time.monotonic_ns()
            print(f"  DEBUG Main: Cálculo de todas as distâncias concluído em {(fim_floyd - inicio_floyd) / 1e9:.4f}s.")

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

            # DEBUG: Verificando a matriz de adjacência (amostra) antes do algoritmo
            # A matriz_adj original é usada para Floyd-Warshall.
            # A matriz distancias_apsp é que será usada no algoritmo construtivo.
            print("  DEBUG Main: Amostra da matriz de distâncias APSP (primeiras 5x5 células):")
            for r_idx in range(min(5, n_vertices)):
                row_str = "    "
                for c_idx in range(min(5, n_vertices)):
                    val = distancias_apsp[r_idx][c_idx]
                    if val == math.inf:
                        row_str += "inf "
                    else:
                        row_str += f"{val:<4.0f}" 
                print(row_str)
            
            print("  DEBUG Main: Verificando todos_os_servicos_pendentes (primeiros 5 e tipos) antes do algoritmo:")
            for i, serv in enumerate(todos_os_servicos_pendentes[:5]): 
                print(f"    Serviço {i} (ID Output: {serv['id_output']}):")
                for k, v in serv.items():
                    if k in ["no_inicial_acesso", "no_final_apos_servico", "demanda", "custo_servico_proprio", "custo_travessia_interno"]:
                        if not isinstance(v, (int, float)):
                            print(f"      ALERTA TIPO SERVIÇO: {k} = {v} (tipo: {type(v)})")

            # Verificação de alcançabilidade dos serviços a partir do depósito (usando APSP)
            print(f"  DEBUG Main: Verificando alcançabilidade dos serviços a partir do depósito {depot_idx+1} (usando APSP)...")
            unreachable_services_from_depot = []
            for serv in todos_os_servicos_pendentes:
                no_acesso = serv["no_inicial_acesso"]
                # Agora usamos a matriz APSP para verificar a alcançabilidade
                cost_from_depot = distancias_apsp[depot_idx][no_acesso]
                if cost_from_depot == math.inf:
                    unreachable_services_from_depot.append(serv["nome_original"])
            
            if unreachable_services_from_depot:
                print(f"  ALERTA CONECTIVIDADE ({arquivo_nome}): Os seguintes serviços são INALCANÇÁVEIS do depósito: {', '.join(unreachable_services_from_depot)}")
                print(f"  Isso pode causar lentidão e rotas incompletas. Verifique a estrutura do grafo ou a lógica de leitura.")
            else:
                print(f"  DEBUG Main: Todos os {len(todos_os_servicos_pendentes)} serviços são alcançáveis do depósito.")


            # 3. Chamar seu novo algoritmo construtivo
            try:
                custo_total_sol, num_rotas_sol, clocks_sol, rotas_finais_sol, tempo_total_s_sol = meu_algoritmo_construtivo(
                    # Passamos a matriz de distâncias APSP em vez da matriz_adj original
                    distancias_apsp, # NOVO ARGUMENTO
                    capacidade_veiculo,
                    depot_idx,
                    todos_os_servicos_pendentes,
                    n_vertices,
                    # dijkstra_func=dijkstra, # Dijkstra não será mais chamado diretamente aqui
                    arquivo_nome_debug=arquivo_nome 
                )
                print(f"  Solução construída: Custo={custo_total_sol:.2f}, Rotas={num_rotas_sol}, Tempo={tempo_total_s_sol:.4f}s")

            except Exception as e:
                print(f"  ERRO ao executar o algoritmo construtivo para {arquivo_nome}: {e}")
                import traceback
                traceback.print_exc()
                continue

            # 4. Escrita no arquivo de saída
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
            
            # break # Descomente para testar com apenas um arquivo

if __name__ == "__main__":
    main()