# algoritmos/path_scanning.py
import math
import time

def meu_algoritmo_construtivo(distancias_apsp, capacidade_veiculo, depot_idx,
                                 lista_inicial_servicos, n_total_vertices, arquivo_nome_debug=""):
    inicio_execucao_ns = time.monotonic_ns()
    
    servicos_pendentes = [s.copy() for s in lista_inicial_servicos]
    rotas_finais_para_output = []
    custo_geral_solucao = 0.0
    id_rota_contador = 0
    DIA_ROTEIRIZACAO = 1

    print(f"DEBUG Algoritmo: Iniciando algoritmo para {arquivo_nome_debug}. Total de serviços: {len(servicos_pendentes)}. Capacidade Veículo: {capacidade_veiculo}")

    loop_count_outer = 0 # Contador para o loop externo
    while servicos_pendentes:
        loop_count_outer += 1
        if loop_count_outer > len(lista_inicial_servicos) + 5 and loop_count_outer > 20: # Limite para evitar loop infinito real nos testes
             print(f"ALERTA ({arquivo_nome_debug}): Loop externo excedeu {loop_count_outer} iterações. Interrompendo para evitar loop infinito.")
             break

        id_rota_contador += 1
        carga_atual_veiculo = 0.0
        custo_parcial_rota = 0.0
        servicos_feitos_nesta_rota = set() 
        sequencia_visitas_output = [] 
        
        localizacao_atual = depot_idx
        sequencia_visitas_output.append(f"(D {depot_idx + 1},{DIA_ROTEIRIZACAO},{id_rota_contador})")
        print(f"DEBUG Algoritmo ({arquivo_nome_debug}, Rota {id_rota_contador}): Iniciando Rota do depósito {depot_idx+1}. Serviços pendentes: {len(servicos_pendentes)}")

        servicos_adicionados_nesta_iteracao_rota = 0 
        while True: # Loop para construir a rota atual
            melhor_candidato_info = None 
            
            servicos_pendentes_para_busca = list(servicos_pendentes) 
            
            print(f"  DEBUG Rota {id_rota_contador}: Buscando próximo serviço. Localização atual: {localizacao_atual+1}. Carga atual: {carga_atual_veiculo:.0f}")
            if not servicos_pendentes_para_busca:
                print(f"  DEBUG Rota {id_rota_contador}: Nenhum serviço pendente para busca.")
                break

            for i, servico_potencial in enumerate(servicos_pendentes_para_busca):
                no_acesso_servico = servico_potencial["no_inicial_acesso"]
                
                # Verifica se os índices são válidos antes de acessar distancias_apsp
                if not (0 <= localizacao_atual < n_total_vertices and 0 <= no_acesso_servico < n_total_vertices):
                    print(f"    ERRO DE ÍNDICE ({arquivo_nome_debug}): Índices inválidos para APSP! loc_atual={localizacao_atual}, no_acesso={no_acesso_servico}, N_vertices={n_total_vertices}")
                    # Decide como lidar com isso, talvez pular este serviço potencial
                    continue 
                
                custo_deslocamento_ate_servico = distancias_apsp[localizacao_atual][no_acesso_servico]

                demanda_adicional = 0
                custo_servico_proprio_adicional = 0
                
                if servico_potencial["id_output"] not in servicos_feitos_nesta_rota: # Sempre verdadeiro para o primeiro serviço na rota
                    demanda_adicional = servico_potencial["demanda"]
                    custo_servico_proprio_adicional = servico_potencial["custo_servico_proprio"]
                
                # Print detalhado para cada candidato:
                # print(f"    Candidato {i+1} (ID {servico_potencial['id_output']}, {servico_potencial['nome_original']}): "
                #       f"Destino {no_acesso_servico+1}. Custo Desloc: {custo_deslocamento_ate_servico:.2f}. "
                #       f"Demanda Adic: {demanda_adicional}. Carga Atual+Adic: {carga_atual_veiculo + demanda_adicional:.0f}. "
                #       f"Capacidade: {capacidade_veiculo}")

                if custo_deslocamento_ate_servico == math.inf:
                    # print(f"      --> Inalcançável.")
                    continue

                if carga_atual_veiculo + demanda_adicional > capacidade_veiculo:
                    # print(f"      --> Excede capacidade.")
                    continue
                
                # Se chegou aqui, o serviço é alcançável e cabe na capacidade
                custo_total_insercao_candidato = (custo_deslocamento_ate_servico +
                                                 custo_servico_proprio_adicional +
                                                 servico_potencial["custo_travessia_interno"])
                
                # print(f"      --> Custo Inserção Total: {custo_total_insercao_candidato:.2f}")

                if melhor_candidato_info is None or custo_total_insercao_candidato < melhor_candidato_info["custo_insercao"]:
                    melhor_candidato_info = {
                        "servico": servico_potencial,
                        "custo_insercao": custo_total_insercao_candidato,
                        "custo_deslocamento_apenas": custo_deslocamento_ate_servico,
                        # idx_lista não é mais necessário aqui se removemos por ID/objeto
                    }
                    # print(f"      --> NOVO MELHOR CANDIDATO: ID {servico_potencial['id_output']} com custo {custo_total_insercao_candidato:.2f}")
            
            if melhor_candidato_info is None:
                print(f"  DEBUG Rota {id_rota_contador}: Nenhum serviço viável encontrado para adicionar nesta iteração da rota.")
                break 
            
            servico_escolhido = melhor_candidato_info["servico"]
            
            # Remoção robusta do serviço da lista original `servicos_pendentes`
            idx_para_remover = -1
            for k, s_p in enumerate(servicos_pendentes):
                if s_p["id_output"] == servico_escolhido["id_output"]: # Compara pelo ID único
                    idx_para_remover = k
                    break
            
            if idx_para_remover != -1:
                servicos_pendentes.pop(idx_para_remover)
                servicos_adicionados_nesta_iteracao_rota += 1
                print(f"  DEBUG Rota {id_rota_contador}: Adicionado serviço {servico_escolhido['id_output']} ({servico_escolhido['nome_original']}). Custo Inserção: {melhor_candidato_info['custo_insercao']:.2f}. Serviços pendentes restantes: {len(servicos_pendentes)}")
            else:
                print(f"  ALERTA ({arquivo_nome_debug}, Rota {id_rota_contador}): Serviço escolhido {servico_escolhido['id_output']} NÃO encontrado na lista de pendentes para remoção. Interrompendo rota.")
                break 

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
            
        # Fim da construção da rota atual
        if servicos_adicionados_nesta_iteracao_rota > 0: 
            print(f"DEBUG Algoritmo ({arquivo_nome_debug}, Rota {id_rota_contador}): Finalizando rota. Retornando de {localizacao_atual+1} para depósito {depot_idx+1}.")
            custo_retorno_depot = distancias_apsp[localizacao_atual][depot_idx]
            if custo_retorno_depot != math.inf:
                custo_parcial_rota += custo_retorno_depot
            else:
                print(f"  ALERTA ({arquivo_nome_debug}, Rota {id_rota_contador}): Não foi possível retornar ao depósito de {localizacao_atual+1}. Custo da rota pode ser INF.")
            
            sequencia_visitas_output.append(f"(D {depot_idx + 1},{DIA_ROTEIRIZACAO},{id_rota_contador})")
            
            rotas_finais_para_output.append({
                "id_rota_output": id_rota_contador,
                "demanda_total_rota_output": carga_atual_veiculo,
                "custo_total_rota_output": custo_parcial_rota,
                "total_visitas_output": len(sequencia_visitas_output),
                "trajeto_string_output": " ".join(sequencia_visitas_output)
            })
            custo_geral_solucao += custo_parcial_rota
        else: # Rota vazia
            print(f"DEBUG Algoritmo ({arquivo_nome_debug}, Rota {id_rota_contador}): Rota vazia (nenhum serviço adicionado). Não será contabilizada.")
            # REMOVIDO: id_rota_contador -= 1 # Para evitar que o ID da rota fique preso
            if not servicos_pendentes: # Se não há mais serviços pendentes, não há porque continuar
                break
            # Se ainda há serviços pendentes mas esta rota ficou vazia, algo está errado
            # (ou todos os restantes são inalcançáveis/não cabem).
            # Se a verificação de conectividade em main.py passou, isso é estranho.
            # Pode ser que os serviços restantes tenham demandas muito altas individualmente.
            # Ou, mais provavelmente, um bug na lógica de seleção ou atualização de estado.
            
    fim_execucao_ns = time.monotonic_ns()
    tempo_total_s = (fim_execucao_ns - inicio_execucao_ns) / 1e9
    clocks_execucao = fim_execucao_ns - inicio_execucao_ns

    print(f"DEBUG Algoritmo ({arquivo_nome_debug}): Algoritmo concluído. Custo Total: {custo_geral_solucao:.2f}, Rotas: {len(rotas_finais_para_output)}")
    return custo_geral_solucao, len(rotas_finais_para_output), clocks_execucao, rotas_finais_para_output, tempo_total_s