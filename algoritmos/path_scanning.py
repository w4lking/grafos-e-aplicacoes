# algoritmos/path_scanning.py
import math
import time
from modelos.instancia import Instancia, VerticeRequerido, LigacaoRequerida
from modelos.servico import Servico
from modelos.solucao import Rota, Solucao

# A função recebe a instância, não mais um monte de parâmetros soltos.
def meu_algoritmo_construtivo(instancia: Instancia, distancias_apsp: list[list[float]], arquivo_nome_debug: str = "") -> Solucao:
    inicio_execucao_ns = time.monotonic_ns()
    
    # Converter os dados da instância em objetos Servico
    todos_os_servicos_pendentes = []
    id_servico_unico_contador = 0 # Inicia em 0, para ser um ID sequencial único

    # NOTE: Os IDs de serviço (id_output) gerados aqui são sequenciais (0, 1, 2...).
    # Se o professor espera IDs específicos do arquivo de entrada (ex: 'N4', 'E1', 'A1'),
    # você precisará ajustar a leitura em 'leitura.py' para capturar esses IDs
    # e usá-los como 'id_output' no objeto Servico.

    for v_req in instancia.vertices_requeridos_detalhes:
        todos_os_servicos_pendentes.append(Servico(
            id_output=id_servico_unico_contador,
            tipo="no",
            nome_original=f"N{v_req.no_idx + 1}", # Nome original (1-indexado) para referência/debug
            definicao_original=v_req,
            no_inicial_acesso=v_req.no_idx,
            no_final_apos_servico=v_req.no_idx,
            demanda=v_req.demanda,
            custo_servico_proprio=v_req.custo_servico,
            custo_travessia_interno=0
        ))
        id_servico_unico_contador += 1
    
    for a_req in instancia.arestas_requeridas_detalhes:
        todos_os_servicos_pendentes.append(Servico(
            id_output=id_servico_unico_contador,
            tipo="aresta",
            # Exemplo de nome original para arestas: E_u_v (1-indexed)
            nome_original=f"E_{a_req.u+1}_{a_req.v+1}", 
            definicao_original=a_req, 
            no_inicial_acesso=a_req.u,
            no_final_apos_servico=a_req.v, # Finaliza no 'v' da aresta (u,v)
            demanda=a_req.demanda,
            custo_servico_proprio=a_req.custo_servico,
            custo_travessia_interno=a_req.custo_travessia
        ))
        id_servico_unico_contador += 1

    for arc_req in instancia.arcos_requeridos_detalhes:
        todos_os_servicos_pendentes.append(Servico(
            id_output=id_servico_unico_contador,
            tipo="arco",
            # Exemplo de nome original para arcos: A_u_v (1-indexed)
            nome_original=f"A_{arc_req.u+1}_{arc_req.v+1}", 
            definicao_original=arc_req,
            no_inicial_acesso=arc_req.u,
            no_final_apos_servico=arc_req.v, # Finaliza no 'v' do arco (u,v)
            demanda=arc_req.demanda,
            custo_servico_proprio=arc_req.custo_servico,
            custo_travessia_interno=arc_req.custo_travessia
        ))
        id_servico_unico_contador += 1

    servicos_pendentes = [s for s in todos_os_servicos_pendentes] # Cria uma cópia mutável
    rotas_finais_para_output: list[Rota] = []
    custo_geral_solucao = 0.0
    id_rota_contador = 0
    DIA_ROTEIRIZACAO = 1 # Definido como 1 no exemplo do professor

    # Variáveis para detectar loop infinito
    last_len_servicos_pendentes = len(servicos_pendentes)
    iterations_since_last_progress = 0
    max_iterations_no_progress = len(todos_os_servicos_pendentes) + 5 # Um limite razoável

    while servicos_pendentes:
        # Condição de parada para evitar loop infinito
        if iterations_since_last_progress >= max_iterations_no_progress:
            print(f"ALERTA ALGORITMO ({arquivo_nome_debug}): Algoritmo não fez progresso em {max_iterations_no_progress} iterações. Interrompendo. Serviços pendentes restantes: {len(servicos_pendentes)}")
            break # Sai do loop principal

        id_rota_contador += 1
        carga_atual_veiculo = 0.0
        custo_parcial_rota = 0.0
        servicos_feitos_nesta_rota = set() # Usa o Servico.id_output para unicidade
        sequencia_visitas_output_strings = [] # Guarda as strings "(D...)" e "(S...)"
        
        localizacao_actual = instancia.depot_idx
        # Formato (D 0,1,1) no exemplo do professor: depósito é 0-indexado na string
        sequencia_visitas_output_strings.append(f"(D {instancia.depot_idx},{DIA_ROTEIRIZACAO},{id_rota_contador})")

        servicos_adicionados_nesta_iteracao_rota = 0 
        while True: # Loop para construir a rota atual
            melhor_candidato_info = None 
            
            servicos_pendentes_para_busca = list(servicos_pendentes) # Copia para iteração segura
            
            # Se não há mais serviços para adicionar à rota atual ou no geral
            if not servicos_pendentes_para_busca:
                 break

            for servico_potencial in servicos_pendentes_para_busca: # Itera sobre objetos Servico
                no_acesso_servico = servico_potencial.no_inicial_acesso
                
                # Verificações de índice para evitar erros de acesso à matriz
                if not (0 <= localizacao_actual < instancia.n_vertices and 0 <= no_acesso_servico < instancia.n_vertices):
                    continue 
                
                custo_deslocamento_ate_servico = distancias_apsp[localizacao_actual][no_acesso_servico]

                demanda_adicional = 0
                custo_servico_proprio_adicional = 0
                
                # Se o serviço ainda não foi contabilizado NESTA ROTA
                if servico_potencial.id_output not in servicos_feitos_nesta_rota: 
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
                        "servico": servico_potencial, # Armazena o objeto Servico completo
                        "custo_insercao": custo_total_insercao_candidato,
                        "custo_deslocamento_apenas": custo_deslocamento_ate_servico,
                    }
            
            if melhor_candidato_info is None:
                break 
            
            servico_escolhido = melhor_candidato_info["servico"]
            
            # Remove o objeto Servico da lista original `servicos_pendentes`
            try:
                servicos_pendentes.remove(servico_escolhido)
                servicos_adicionados_nesta_iteracao_rota += 1
            except ValueError:
                # Caso o serviço já tenha sido removido por algum motivo inesperado.
                break 

            custo_parcial_rota += melhor_candidato_info["custo_deslocamento_apenas"]
            
            if servico_escolhido.id_output not in servicos_feitos_nesta_rota:
                carga_atual_veiculo += servico_escolhido.demanda
                custo_parcial_rota += servico_escolhido.custo_servico_proprio
                servicos_feitos_nesta_rota.add(servico_escolhido.id_output) # Adiciona o id_output
            
            custo_parcial_rota += servico_escolhido.custo_travessia_interno
            
            # Formatação para string de saída: ID do serviço (0-indexado), nós (1-indexados)
            id_s_output = servico_escolhido.id_output 
            if servico_escolhido.tipo == "no":
                # Nós 1-indexados na string S
                no_idx_output_1_indexed = servico_escolhido.definicao_original.no_idx + 1 
                sequencia_visitas_output_strings.append(f"(S {id_s_output},{no_idx_output_1_indexed},{no_idx_output_1_indexed})")
            elif servico_escolhido.tipo == "aresta" or servico_escolhido.tipo == "arco":
                # Nós 1-indexados na string S
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
            
            # Formato (D 0,1,1) no exemplo do professor: depósito é 0-indexado na string
            sequencia_visitas_output_strings.append(f"(D {instancia.depot_idx},{DIA_ROTEIRIZACAO},{id_rota_contador})")
            
            # Cria um objeto Rota
            rotas_finais_para_output.append(
                Rota(
                    id_rota_output=id_rota_contador,
                    demanda_total_rota=carga_atual_veiculo,
                    custo_total_rota=custo_parcial_rota,
                    total_visitas=len(sequencia_visitas_output_strings),
                    trajeto_string_output=" ".join(sequencia_visitas_output_strings)
                )
            )
            custo_geral_solucao += custo_parcial_rota

            # Resetar contador de progresso
            iterations_since_last_progress = 0
            last_len_servicos_pendentes = len(servicos_pendentes) # Atualiza o último tamanho conhecido
        else: # Rota vazia (não adicionou nenhum serviço)
            id_rota_contador -= 1 # Decrementa para não ter IDs de rota vazios
            
            # Aumenta o contador de iterações sem progresso
            iterations_since_last_progress += 1
            
            # Se não há mais serviços pendentes, o loop principal vai terminar de qualquer forma
            if not servicos_pendentes: 
                break 
            
    fim_execucao_ns = time.monotonic_ns()
    tempo_total_s = (fim_execucao_ns - inicio_execucao_ns) / 1e9
    
    # GARANTIR QUE CLOCKS NÃO É ZERO PARA INSTÂNCIAS MUITO RÁPIDAS
    clocks_execucao = fim_execucao_ns - inicio_execucao_ns
    if clocks_execucao == 0 and len(todos_os_servicos_pendentes) > 0: # Apenas se há serviços e o tempo foi 0
        clocks_execucao = 1 # Define um mínimo de 1 nanossegundo para evitar zero absoluto


    return Solucao(
        custo_total_solucao=custo_geral_solucao,
        num_rotas_solucao=len(rotas_finais_para_output),
        clocks_execucao=clocks_execucao,
        tempo_total_s=tempo_total_s,
        rotas=rotas_finais_para_output
    )
