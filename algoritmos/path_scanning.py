# algoritmos/path_scanning.py
import math
import time
from typing import List, Dict, Any
from modelos.instancia import Instancia, VerticeRequerido, LigacaoRequerida
from modelos.servico import Servico # Import Servico aqui, pois este módulo o cria
from modelos.solucao import Rota, Solucao

def meu_algoritmo_construtivo(instancia: Instancia, distancias_apsp: List[List[float]], arquivo_nome_debug: str = "") -> Solucao:
    inicio_execucao_ns = time.monotonic_ns()
    
    todos_os_servicos_originais_para_criacao_servico_obj = []
    id_servico_unico_contador = 0 

    for v_req in instancia.vertices_requeridos_detalhes:
        todos_os_servicos_originais_para_criacao_servico_obj.append(Servico(
            id_output=id_servico_unico_contador,
            tipo="no",
            nome_original=f"N{v_req.no_idx + 1}", 
            definicao_original=v_req,
            no_inicial_acesso=v_req.no_idx,
            no_final_apos_servico=v_req.no_idx,
            demanda=v_req.demanda,
            custo_servico_proprio=v_req.custo_servico,
            custo_travessia_interno=0
        ))
        id_servico_unico_contador += 1
    
    for a_req in instancia.arestas_requeridas_detalhes:
        todos_os_servicos_originais_para_criacao_servico_obj.append(Servico(
            id_output=id_servico_unico_contador,
            tipo="aresta",
            nome_original=f"E_{a_req.u+1}_{a_req.v+1}", 
            definicao_original=a_req, 
            no_inicial_acesso=a_req.u,
            no_final_apos_servico=a_req.v, 
            demanda=a_req.demanda,
            custo_servico_proprio=a_req.custo_servico,
            custo_travessia_interno=a_req.custo_travessia
        ))
        id_servico_unico_contador += 1

    for arc_req in instancia.arcos_requeridos_detalhes:
        todos_os_servicos_originais_para_criacao_servico_obj.append(Servico(
            id_output=id_servico_unico_contador,
            tipo="arco",
            nome_original=f"A_{arc_req.u+1}_{arc_req.v+1}", 
            definicao_original=arc_req,
            no_inicial_acesso=arc_req.u,
            no_final_apos_servico=arc_req.v,
            demanda=arc_req.demanda,
            custo_servico_proprio=arc_req.custo_servico,
            custo_travessia_interno=arc_req.custo_travessia
        ))
        id_servico_unico_contador += 1

    servicos_pendentes = [s for s in todos_os_servicos_originais_para_criacao_servico_obj] 
    rotas_finais_para_output: List[Rota] = []
    custo_geral_solucao = 0.0
    id_rota_contador = 0
    DIA_ROTEIRIZACAO = 1 

    last_len_servicos_pendentes = len(servicos_pendentes)
    iterations_since_last_progress = 0
    max_iterations_no_progress = len(todos_os_servicos_originais_para_criacao_servico_obj) + 5 

    while servicos_pendentes:
        if iterations_since_last_progress >= max_iterations_no_progress:
            print(f"ALERTA ALGORITMO ({arquivo_nome_debug}): Algoritmo não fez progresso em {max_iterations_no_progress} iterações. Interrompendo. Serviços pendentes restantes: {len(servicos_pendentes)}")
            break 

        id_rota_contador += 1
        carga_atual_veiculo = 0.0
        custo_parcial_rota = 0.0
        servicos_feitos_nesta_rota_ids = set() # Guarda ids_output de serviços já contabilizados para demanda/custo
        sequencia_visitas_output_strings = [] # Para a string final de saída
        
        # NOVOS CAMPOS PARA A ROTA:
        sequencia_servicos_atendidos_nesta_rota: List[Servico] = [] # Objetos Servico atendidos
        sequencia_nos_percorridos_nesta_rota: List[int] = [instancia.depot_idx] # Nós visitados

        localizacao_actual = instancia.depot_idx
        sequencia_visitas_output_strings.append(f"(D {instancia.depot_idx},{DIA_ROTEIRIZACAO},{id_rota_contador})")

        servicos_adicionados_nesta_iteracao_rota = 0 
        while True: 
            melhor_candidato_info = None 
            
            servicos_pendentes_para_busca = list(servicos_pendentes) 
            
            if not servicos_pendentes_para_busca:
                 break

            for servico_potencial in servicos_pendentes_para_busca: 
                no_acesso_servico = servico_potencial.no_inicial_acesso
                
                if not (0 <= localizacao_actual < instancia.n_vertices and 0 <= no_acesso_servico < instancia.n_vertices):
                    continue 
                
                custo_deslocamento_ate_servico = distancias_apsp[localizacao_actual][no_acesso_servico]

                demanda_adicional = 0
                custo_servico_proprio_adicional = 0
                
                if servico_potencial.id_output not in servicos_feitos_nesta_rota_ids: 
                    demanda_adicional = servico_potencial.demanda
                    custo_servico_proprio_adicional = servico_potencial.custo_servico_proprio
                
                if custo_deslocamento_ate_servico == math.inf:
                    continue

                if carga_atual_veiculo + demanda_adicional > instancia.capacidade_veiculo:
                    continue
                
                custo_total_insercao_candidato = (custo_deslocamento_ate_servico +
                                                 custo_servico_proprio_adicional +
                                                 servico_potencial.custo_travessia_interno)
                
                if melhor_candidato_info is None or custo_total_insercao_candidato < melhor_candidato_info["custo_insercao"]:
                    melhor_candidato_info = {
                        "servico": servico_potencial, 
                        "custo_insercao": custo_total_insercao_candidato,
                        "custo_deslocamento_apenas": custo_deslocamento_ate_servico,
                    }
            
            if melhor_candidato_info is None:
                break 
            
            servico_escolhido = melhor_candidato_info["servico"]
            
            # Reconstruir o caminho de nós do ponto atual até o início do serviço
            # Isso é para 'sequencia_nos_percorridos'. Para isso, o Floyd-Warshall padrão não dá o caminho,
            # apenas o custo. Você precisaria de um Floyd-Warshall modificado para predecessores
            # ou um Dijkstra para cada trecho para obter o caminho.
            # Por simplicidade inicial, vamos adicionar apenas o nó de acesso e o nó final do serviço.
            # Idealmente, aqui você adicionaria os nós intermediários do shortest path.
            
            # --- Inserção dos nós intermediários do caminho de deslocamento ---
            # Para obter os nós intermediários do caminho mais curto, você precisaria de uma versão
            # do algoritmo de caminho mais curto (como Dijkstra ou uma versão modificada de Floyd-Warshall)
            # que também retorna os predecessores. Se não quiser complicar muito agora,
            # apenas adicione o nó de destino (no_acesso_servico).
            # Para uma implementação mais robusta, você pode usar uma função de reconstrução de caminho:
            # path_nodes = reconstruir_caminho_dijkstra(matriz_adj_original, localizacao_actual, no_acesso_servico)
            # sequencia_nos_percorridos_nesta_rota.extend(path_nodes[1:]) # Ignora o nó inicial, já está lá

            # Para esta fase, vamos manter a adição dos nós principais por enquanto:
            if localizacao_actual != servico_escolhido.no_inicial_acesso: # Evita duplicar o nó se já estivermos lá
                sequencia_nos_percorridos_nesta_rota.append(servico_escolhido.no_inicial_acesso)
            
            # Remova o objeto Servico da lista original `servicos_pendentes`
            try:
                servicos_pendentes.remove(servico_escolhido)
                servicos_adicionados_nesta_iteracao_rota += 1
            except ValueError:
                break 

            custo_parcial_rota += melhor_candidato_info["custo_deslocamento_apenas"]
            
            if servico_escolhido.id_output not in servicos_feitos_nesta_rota_ids:
                carga_atual_veiculo += servico_escolhido.demanda
                custo_parcial_rota += servico_escolhido.custo_servico_proprio
                servicos_feitos_nesta_rota_ids.add(servico_escolhido.id_output) 
            
            custo_parcial_rota += servico_escolhido.custo_travessia_interno
            
            # Adicionar o serviço ao vetor de serviços atendidos pela rota
            sequencia_servicos_atendidos_nesta_rota.append(servico_escolhido)

            # Adicionar o nó final do serviço ao trajeto percorrido
            if servico_escolhido.tipo == "no":
                if servico_escolhido.no_inicial_acesso != servico_escolhido.no_final_apos_servico: # Se fosse um nó que tem um "fim" diferente
                    sequencia_nos_percorridos_nesta_rota.append(servico_escolhido.no_final_apos_servico)
            elif servico_escolhido.tipo == "aresta" or servico_escolhido.tipo == "arco":
                sequencia_nos_percorridos_nesta_rota.append(servico_escolhido.no_final_apos_servico)

            # Formatação para string de saída: ID do serviço (0-indexado), nós (1-indexados)
            id_s_output = servico_escolhido.id_output 
            if servico_escolhido.tipo == "no":
                no_idx_output_1_indexed = servico_escolhido.definicao_original.no_idx + 1 
                sequencia_visitas_output_strings.append(f"(S {id_s_output},{no_idx_output_1_indexed},{no_idx_output_1_indexed})")
            elif servico_escolhido.tipo == "aresta" or servico_escolhido.tipo == "arco":
                u_output_1_indexed = servico_escolhido.definicao_original.u + 1
                v_output_1_indexed = servico_escolhido.definicao_original.v + 1
                sequencia_visitas_output_strings.append(f"(S {id_s_output},{u_output_1_indexed},{v_output_1_indexed})")

            localizacao_actual = servico_escolhido.no_final_apos_servico
            
        # Fim da construção da rota atual
        if servicos_adicionados_nesta_iteracao_rota > 0: 
            custo_retorno_depot = distancias_apsp[localizacao_actual][instancia.depot_idx]
            if custo_retorno_depot != math.inf:
                custo_parcial_rota += custo_retorno_depot
            else:
                pass 
            
            sequencia_nos_percorridos_nesta_rota.append(instancia.depot_idx) # Adiciona o retorno ao depósito final
            sequencia_visitas_output_strings.append(f"(D {instancia.depot_idx},{DIA_ROTEIRIZACAO},{id_rota_contador})")
            
            # Cria um objeto Rota
            rotas_finais_para_output.append(
                Rota(
                    id_rota_output=id_rota_contador,
                    demanda_total_rota=carga_atual_veiculo,
                    custo_total_rota=custo_parcial_rota,
                    total_visitas=len(sequencia_visitas_output_strings),
                    sequencia_nos_percorridos=sequencia_nos_percorridos_nesta_rota,
                    servicos_atendidos=sequencia_servicos_atendidos_nesta_rota,
                    trajeto_string_output=" ".join(sequencia_visitas_output_strings)
                )
            )
            custo_geral_solucao += custo_parcial_rota

            iterations_since_last_progress = 0
            last_len_servicos_pendentes = len(servicos_pendentes) 
        else: # Rota vazia
            id_rota_contador -= 1 
            iterations_since_last_progress += 1
            if not servicos_pendentes: 
                break 
            
    fim_execucao_ns = time.monotonic_ns()
    tempo_total_s = (fim_execucao_ns - inicio_execucao_ns) / 1e9
    
    clocks_execucao = fim_execucao_ns - inicio_execucao_ns
    if clocks_execucao == 0 and len(todos_os_servicos_originais_para_criacao_servico_obj) > 0: 
        clocks_execucao = 1 


    return Solucao(
        custo_total_solucao=custo_geral_solucao,
        num_rotas_solucao=len(rotas_finais_para_output),
        clocks_execucao=clocks_execucao,
        tempo_total_s=tempo_total_s,
        rotas=rotas_finais_para_output
    )
