# algoritmos/busca_local.py
import math
import time
import random
import copy # Importar para deepcopy
from typing import List, Tuple, Any, Optional
from modelos.instancia import Instancia
from modelos.solucao import Solucao, Rota
from modelos.servico import Servico # Importa Servico para manipulação de objetos

# --- Funções Auxiliares para Busca Local ---

def recalcular_custo_e_demanda_rota(
    id_rota: int, # ID da rota
    servicos_na_rota: List[Servico], # Lista de objetos Servico
    instancia: Instancia, 
    distancias_apsp: List[List[float]]
) -> Tuple[float, float, List[int], str]:
    """
    Recalcula o custo e a demanda de uma rota baseada em sua nova sequência de serviços.
    Retorna o novo custo, nova demanda, nova sequência de nós percorrida e a nova string de trajeto formatada.
    """
    nova_custo_total = 0.0
    nova_carga_total = 0.0
    
    nova_sequencia_nos_percorridos: List[int] = [instancia.depot_idx]
    nova_trajeto_string_output_list: List[str] = [f"(D {instancia.depot_idx},{1},{id_rota})"] 
    
    localizacao_atual = instancia.depot_idx
    servicos_ja_contabilizados_nesta_rota_ids = set() 

    if not servicos_na_rota: # Rota vazia (apenas depósito)
        return 0.0, 0.0, [instancia.depot_idx], f"(D {instancia.depot_idx},{1},{id_rota})"

    for servico in servicos_na_rota:
        if not (0 <= localizacao_atual < instancia.n_vertices and 
                0 <= servico.no_inicial_acesso < instancia.n_vertices):
            return math.inf, math.inf, [], "" 

        custo_desloc = distancias_apsp[localizacao_atual][servico.no_inicial_acesso]
        if custo_desloc == math.inf: 
            return math.inf, math.inf, [], "" 
        nova_custo_total += custo_desloc

        if localizacao_atual != servico.no_inicial_acesso:
            nova_sequencia_nos_percorridos.append(servico.no_inicial_acesso)
        
        if servico.id_output not in servicos_ja_contabilizados_nesta_rota_ids:
            nova_carga_total += servico.demanda
            nova_custo_total += servico.custo_servico_proprio
            servicos_ja_contabilizados_nesta_rota_ids.add(servico.id_output)
        
        nova_custo_total += servico.custo_travessia_interno
        
        if servico.no_inicial_acesso != servico.no_final_apos_servico and \
           servico.no_final_apos_servico not in nova_sequencia_nos_percorridos:
            nova_sequencia_nos_percorridos.append(servico.no_final_apos_servico)

        id_s_output = servico.id_output 
        if servico.tipo == "no":
            no_idx_output_1_indexed = servico.definicao_original.no_idx + 1 
            nova_trajeto_string_output_list.append(f"(S {id_s_output},{no_idx_output_1_indexed},{no_idx_output_1_indexed})")
        else: # aresta ou arco
            u_output_1_indexed = servico.definicao_original.u + 1
            v_output_1_indexed = servico.definicao_original.v + 1
            nova_trajeto_string_output_list.append(f"(S {id_s_output},{u_output_1_indexed},{v_output_1_indexed})")
        
        localizacao_atual = servico.no_final_apos_servico

    if not (0 <= localizacao_atual < instancia.n_vertices and 
            0 <= instancia.depot_idx < instancia.n_vertices):
        return math.inf, math.inf, [], "" 

    custo_retorno_depot = distancias_apsp[localizacao_atual][instancia.depot_idx]
    if custo_retorno_depot == math.inf: 
        return math.inf, math.inf, [], ""
    nova_custo_total += custo_retorno_depot
    
    nova_sequencia_nos_percorridos.append(instancia.depot_idx)
    nova_trajeto_string_output_list.append(f"(D {instancia.depot_idx},{1},{id_rota})")

    return nova_custo_total, nova_carga_total, nova_sequencia_nos_percorridos, " ".join(nova_trajeto_string_output_list)

def verificar_viabilidade_rota(custo: float, demanda: float, capacidade_veiculo: int) -> bool:
    """Verifica se uma rota é viável em termos de custo e capacidade."""
    return custo != math.inf and demanda <= capacidade_veiculo


# --- Operadores de Busca Local (Otimizados) ---

def aplicar_2opt(solucao: Solucao, instancia: Instancia, distancias_apsp: List[List[float]]) -> Solucao:
    """
    Tenta aplicar o operador 2-Opt (estratégia First Improvement).
    Aplica a primeira melhora encontrada para acelerar o processo.
    """
    for idx_rota in range(len(solucao.rotas)):
        rota = solucao.rotas[idx_rota]
        num_servicos = len(rota.servicos_atendidos)
        if num_servicos < 2:
            continue

        for i in range(num_servicos - 1):
            for j in range(i + 1, num_servicos):
                # Calcula o delta_custo sem modificar a rota
                servico_i = rota.servicos_atendidos[i]
                servico_j = rota.servicos_atendidos[j]
                
                no_anterior_i = rota.servicos_atendidos[i-1].no_final_apos_servico if i > 0 else instancia.depot_idx
                no_posterior_j = rota.servicos_atendidos[j+1].no_inicial_acesso if j < num_servicos - 1 else instancia.depot_idx

                custo_original = (distancias_apsp[no_anterior_i][servico_i.no_inicial_acesso] +
                                  distancias_apsp[servico_j.no_final_apos_servico][no_posterior_j])
                
                custo_novo = (distancias_apsp[no_anterior_i][servico_j.no_inicial_acesso] +
                              distancias_apsp[servico_i.no_final_apos_servico][no_posterior_j])

                if custo_novo < custo_original:
                    # Encontrou uma melhora, aplica e retorna imediatamente (First Improvement)
                    solucao_melhorada = copy.deepcopy(solucao)
                    rota_a_modificar = solucao_melhorada.rotas[idx_rota]
                    
                    segmento_invertido = rota_a_modificar.servicos_atendidos[i:j+1][::-1]
                    rota_a_modificar.servicos_atendidos = rota_a_modificar.servicos_atendidos[:i] + segmento_invertido + rota_a_modificar.servicos_atendidos[j+1:]
                    
                    # Recalcula apenas a rota modificada
                    custo, demanda, seq_nos, traj_str = recalcular_custo_e_demanda_rota(
                        rota_a_modificar.id_rota_output, rota_a_modificar.servicos_atendidos, instancia, distancias_apsp
                    )
                    rota_a_modificar.custo_total_rota = custo
                    rota_a_modificar.demanda_total_rota = demanda
                    rota_a_modificar.sequencia_nos_percorridos = seq_nos
                    rota_a_modificar.trajeto_string_output = traj_str

                    # Atualiza custo da solução e retorna
                    solucao_melhorada.custo_total_solucao = sum(r.custo_total_rota for r in solucao_melhorada.rotas)
                    return solucao_melhorada

    return solucao # Retorna a solução original se nenhuma melhora foi encontrada


def aplicar_relocate(solucao: Solucao, instancia: Instancia, distancias_apsp: List[List[float]]) -> Solucao:
    """
    Tenta aplicar o operador Relocate (estratégia First Improvement).
    Aplica a primeira melhora encontrada para acelerar o processo.
    """
    for idx_rota_origem in range(len(solucao.rotas)):
        if not solucao.rotas[idx_rota_origem].servicos_atendidos:
            continue

        for idx_servico_a_mover in range(len(solucao.rotas[idx_rota_origem].servicos_atendidos)):
            servico_a_mover = solucao.rotas[idx_rota_origem].servicos_atendidos[idx_servico_a_mover]

            for idx_rota_destino in range(len(solucao.rotas)):
                num_posicoes_destino = len(solucao.rotas[idx_rota_destino].servicos_atendidos)
                if idx_rota_origem == idx_rota_destino:
                    num_posicoes_destino +=1 # Pode inserir na própria rota

                for idx_posicao_destino in range(num_posicoes_destino):
                    if idx_rota_origem == idx_rota_destino and idx_servico_a_mover == idx_posicao_destino:
                        continue

                    # Verifica se a capacidade da rota de destino seria violada
                    if idx_rota_origem != idx_rota_destino:
                        if solucao.rotas[idx_rota_destino].demanda_total_rota + servico_a_mover.demanda > instancia.capacidade_veiculo:
                            continue

                    # Encontrou um movimento válido, aplica e retorna (First Improvement)
                    solucao_melhorada = copy.deepcopy(solucao)
                    
                    servico_obj = solucao_melhorada.rotas[idx_rota_origem].servicos_atendidos.pop(idx_servico_a_mover)
                    
                    if idx_rota_origem == idx_rota_destino:
                        solucao_melhorada.rotas[idx_rota_origem].servicos_atendidos.insert(idx_posicao_destino, servico_obj)
                    else:
                        solucao_melhorada.rotas[idx_rota_destino].servicos_atendidos.insert(idx_posicao_destino, servico_obj)

                    custo_antigo_total = solucao.custo_total_solucao
                    
                    # Recalcula apenas rotas afetadas
                    custo_origem, demanda_origem, _, _ = recalcular_custo_e_demanda_rota(
                        solucao_melhorada.rotas[idx_rota_origem].id_rota_output, solucao_melhorada.rotas[idx_rota_origem].servicos_atendidos, instancia, distancias_apsp)
                    
                    custo_destino, demanda_destino, _, _ = recalcular_custo_e_demanda_rota(
                        solucao_melhorada.rotas[idx_rota_destino].id_rota_output, solucao_melhorada.rotas[idx_rota_destino].servicos_atendidos, instancia, distancias_apsp)
                    
                    custo_novo_parcial = custo_origem + custo_destino
                    custo_antigo_parcial = solucao.rotas[idx_rota_origem].custo_total_rota + solucao.rotas[idx_rota_destino].custo_total_rota
                    
                    if idx_rota_origem == idx_rota_destino:
                         custo_antigo_parcial /= 2 # Evita contagem dupla

                    custo_novo_total = custo_antigo_total - custo_antigo_parcial + custo_novo_parcial
                    
                    if custo_novo_total < custo_antigo_total:
                        # É uma melhora, atualiza a solução e retorna
                        solucao_melhorada.rotas = [r for r in solucao_melhorada.rotas if r.servicos_atendidos]
                        solucao_melhorada.num_rotas_solucao = len(solucao_melhorada.rotas)
                        solucao_melhorada.custo_total_solucao = sum(r.custo_total_rota for r in solucao_melhorada.rotas)
                        return solucao_melhorada

    return solucao


def perturbar_solucao(solucao: Solucao, instancia: Instancia, distancias_apsp: List[List[float]], perturb_strength: int = 2) -> Solucao:
    """
    Aplica uma perturbação na solução para tirá-la de um mínimo local.
    A força da perturbação pode ser controlada por `perturb_strength`.
    Retorna uma nova solução perturbada.
    """
    perturbada_solucao = copy.deepcopy(solucao)
    
    for _ in range(perturb_strength):
        if len(perturbada_solucao.rotas) < 1:
            break

        rotas_nao_vazias_idx = [i for i, r in enumerate(perturbada_solucao.rotas) if r.servicos_atendidos]
        if not rotas_nao_vazias_idx:
            break
        
        idx_rota_origem = random.choice(rotas_nao_vazias_idx)
        idx_rota_destino = random.randrange(len(perturbada_solucao.rotas))
        
        servico_a_mover = perturbada_solucao.rotas[idx_rota_origem].servicos_atendidos.pop(random.randrange(len(perturbada_solucao.rotas[idx_rota_origem].servicos_atendidos)))
        
        idx_posicao_destino = random.randrange(len(perturbada_solucao.rotas[idx_rota_destino].servicos_atendidos) + 1)
        perturbada_solucao.rotas[idx_rota_destino].servicos_atendidos.insert(idx_posicao_destino, servico_a_mover)

    # Recalcula todas as rotas após a perturbação (mais simples e seguro aqui)
    for rota in perturbada_solucao.rotas:
        custo, demanda, seq_nos, traj_str = recalcular_custo_e_demanda_rota(
            rota.id_rota_output, rota.servicos_atendidos, instancia, distancias_apsp)
        rota.custo_total_rota = custo
        rota.demanda_total_rota = demanda
        rota.sequencia_nos_percorridos = seq_nos
        rota.trajeto_string_output = traj_str

    perturbada_solucao.rotas = [r for r in perturbada_solucao.rotas if r.servicos_atendidos]
    perturbada_solucao.num_rotas_solucao = len(perturbada_solucao.rotas)
    perturbada_solucao.custo_total_solucao = sum(r.custo_total_rota for r in perturbada_solucao.rotas) if perturbada_solucao.rotas else 0

    return perturbada_solucao


def otimizar_solucao(solucao_inicial: Solucao, instancia: Instancia, distancias_apsp: List[List[float]]) -> Solucao:
    """
    Aplica o Iterated Local Search (ILS) para otimizar a solução.
    """
    inicio_execucao_total_ils_ns = time.monotonic_ns() 

    melhor_solucao_global = copy.deepcopy(solucao_inicial)
    solucao_atual = copy.deepcopy(solucao_inicial)

    max_iter_ils = 10 
    iter_ils = 0

    print("--- INICIANDO BUSCA LOCAL (ITERATED LOCAL SEARCH - ILS OTIMIZADO) ---")
    print(f"Custo inicial da solução: {solucao_inicial.custo_total_solucao:.2f}")

    while iter_ils < max_iter_ils:
        iter_ils += 1
        print(f"\nILS Iteration {iter_ils}/{max_iter_ils}")

        # 1. Busca Local (Refinement)
        while True:
            custo_antes_da_busca = solucao_atual.custo_total_solucao

            # Tenta aplicar 2-Opt (First Improvement)
            solucao_atual = aplicar_2opt(solucao_atual, instancia, distancias_apsp)
            if solucao_atual.custo_total_solucao < custo_antes_da_busca:
                print(f"  Refinement: Melhoria 2-Opt. Custo: {solucao_atual.custo_total_solucao:.2f}")
                continue # Volta ao início do refinamento

            # Tenta aplicar Relocate (First Improvement)
            solucao_atual = aplicar_relocate(solucao_atual, instancia, distancias_apsp)
            if solucao_atual.custo_total_solucao < custo_antes_da_busca:
                print(f"  Refinement: Melhoria Relocate. Custo: {solucao_atual.custo_total_solucao:.2f}")
                continue # Volta ao início do refinamento
            
            # Se nenhum operador melhorou a solução, sai do loop de refinamento
            break

        print(f"  Refinement concluído. Custo atual: {solucao_atual.custo_total_solucao:.2f}")

        # 2. Critério de Aceitação
        if solucao_atual.custo_total_solucao < melhor_solucao_global.custo_total_solucao:
            melhor_solucao_global = copy.deepcopy(solucao_atual)
            print(f"  NOVA MELHOR SOLUÇÃO GLOBAL ENCONTRADA! Custo: {melhor_solucao_global.custo_total_solucao:.2f}")
        
        # 3. Perturbação
        if iter_ils < max_iter_ils:
            solucao_atual = perturbar_solucao(melhor_solucao_global, instancia, distancias_apsp, perturb_strength=4)
            print(f"  Solução perturbada. Custo: {solucao_atual.custo_total_solucao:.2f}")
    
    print(f"\n--- FIM DO ITERATED LOCAL SEARCH ---")
    
    fim_execucao_total_ils_ns = time.monotonic_ns() 
    total_clocks = fim_execucao_total_ils_ns - inicio_execucao_total_ils_ns
    melhor_solucao_global.clocks_execucao = total_clocks
    melhor_solucao_global.tempo_total_s = total_clocks / 1e9 

    return melhor_solucao_global
