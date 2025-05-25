# algoritmos/path_scanning.py
import math
import time
# Não precisa de heapq aqui se dijkstra é importado e usado

def meu_algoritmo_construtivo(matriz_adj, capacidade_veiculo, depot_idx,
                                 lista_inicial_servicos, n_total_vertices, dijkstra_func):
    # ... (código da função meu_algoritmo_construtivo que fornecemos anteriormente) ...
    # Lembre-se que esta função agora usa 'dijkstra_func' que é passada como argumento
    # Exemplo de chamada dentro desta função:
    # custo_deslocamento = dijkstra_func(matriz_adj, localizacao_atual, no_acesso_servico)

    inicio_execucao_ns = time.monotonic_ns()
    
    servicos_pendentes = [s.copy() for s in lista_inicial_servicos]
    rotas_finais_para_output = []
    custo_geral_solucao = 0.0
    id_rota_contador = 0
    DIA_ROTEIRIZACAO = 1

    while servicos_pendentes:
        id_rota_contador += 1
        carga_atual_veiculo = 0.0
        custo_parcial_rota = 0.0
        servicos_feitos_nesta_rota = set() 
        sequencia_visitas_output = [] 
        
        localizacao_atual = depot_idx
        sequencia_visitas_output.append(f"(D {depot_idx + 1},{DIA_ROTEIRIZACAO},{id_rota_contador})")

        while True:
            melhor_candidato_info = None
            
            for i, servico_potencial in enumerate(servicos_pendentes):
                no_acesso_servico = servico_potencial["no_inicial_acesso"]
                custo_deslocamento_ate_servico = dijkstra_func(matriz_adj, localizacao_atual, no_acesso_servico)

                if custo_deslocamento_ate_servico == math.inf:
                    continue

                demanda_adicional = 0
                custo_servico_proprio_adicional = 0
                
                if servico_potencial["id_output"] not in servicos_feitos_nesta_rota:
                    demanda_adicional = servico_potencial["demanda"]
                    custo_servico_proprio_adicional = servico_potencial["custo_servico_proprio"]
                
                if carga_atual_veiculo + demanda_adicional <= capacidade_veiculo:
                    custo_total_insercao_candidato = (custo_deslocamento_ate_servico +
                                                     custo_servico_proprio_adicional +
                                                     servico_potencial["custo_travessia_interno"])
                    
                    if melhor_candidato_info is None or custo_total_insercao_candidato < melhor_candidato_info["custo_insercao"]:
                        melhor_candidato_info = {
                            "servico": servico_potencial,
                            "custo_insercao": custo_total_insercao_candidato,
                            "custo_deslocamento_apenas": custo_deslocamento_ate_servico,
                            "idx_lista": i
                        }
            
            if melhor_candidato_info is None:
                break
            
            servico_escolhido = melhor_candidato_info["servico"]
            custo_parcial_rota += melhor_candidato_info["custo_deslocamento_apenas"]
            
            if servico_escolhido["id_output"] not in servicos_feitos_nesta_rota:
                carga_atual_veiculo += servico_escolhido["demanda"]
                custo_parcial_rota += servico_escolhido["custo_servico_proprio"]
                servicos_feitos_nesta_rota.add(servico_escolhido["id_output"])
            
            custo_parcial_rota += servico_escolhido["custo_travessia_interno"]
            
            id_s = servico_escolhido["id_output"]
            if servico_escolhido["tipo"] == "no":
                no_idx = servico_escolhido["definicao_original"]["no_idx"]
                sequencia_visitas_output.append(f"(S {id_s},{no_idx + 1},{no_idx + 1})")
            elif servico_escolhido["tipo"] == "aresta" or servico_escolhido["tipo"] == "arco":
                u, v = servico_escolhido["definicao_original"]["u"], servico_escolhido["definicao_original"]["v"]
                sequencia_visitas_output.append(f"(S {id_s},{u + 1},{v + 1})")

            localizacao_atual = servico_escolhido["no_final_apos_servico"]
            servicos_pendentes.pop(melhor_candidato_info["idx_lista"])

        if len(sequencia_visitas_output) > 1: # Se a rota serviu alguém além do D inicial
            custo_retorno_depot = dijkstra_func(matriz_adj, localizacao_atual, depot_idx)
            if custo_retorno_depot != math.inf:
                custo_parcial_rota += custo_retorno_depot
            
            sequencia_visitas_output.append(f"(D {depot_idx + 1},{DIA_ROTEIRIZACAO},{id_rota_contador})")
            
            rotas_finais_para_output.append({
                "id_rota_output": id_rota_contador,
                "demanda_total_rota_output": carga_atual_veiculo,
                "custo_total_rota_output": custo_parcial_rota,
                "total_visitas_output": len(sequencia_visitas_output),
                "trajeto_string_output": " ".join(sequencia_visitas_output)
            })
            custo_geral_solucao += custo_parcial_rota
            
    fim_execucao_ns = time.monotonic_ns()
    tempo_total_s = (fim_execucao_ns - inicio_execucao_ns) / 1e9
    clocks_execucao = fim_execucao_ns - inicio_execucao_ns

    return custo_geral_solucao, len(rotas_finais_para_output), clocks_execucao, rotas_finais_para_output, tempo_total_s