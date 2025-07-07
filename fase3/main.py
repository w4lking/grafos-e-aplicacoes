# fase2/main.py
import os
import sys
import time
import math 

# Configura o sys.path para encontrar os módulos na raiz do projeto
current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.dirname(current_file_dir)
sys.path.insert(0, project_root_dir)

# Importando os módulos e as novas classes de modelo
from leitura import parse_dat_file
from algoritmos.floyd_warshall import floyd_warshall
from algoritmos.path_scanning import meu_algoritmo_construtivo
from algoritmos.busca_local import otimizar_solucao # Importa a nova função de otimização
from modelos.instancia import Instancia, VerticeRequerido, LigacaoRequerida 
from modelos.solucao import Solucao, Rota 

def main():
    pasta_instancias = os.path.join(current_file_dir, "dados", "MCGRP")
    pasta_saida = os.path.join(current_file_dir, "G20")
    os.makedirs(pasta_saida, exist_ok=True)

    print(f"Buscando instâncias em: {pasta_instancias}")

    arquivos_para_processar = []
    salvar_solucao_para_este_arquivo = True 

    # --- Opção de processamento interativa ---
    escolha_processamento = input("Deseja processar TODOS os arquivos (.dat) ou um ESPECÍFICO? (digite 't' ou 'e'): ").strip().lower()
    
    if escolha_processamento == 't':
        print("Modo: Processando todos os arquivos .dat na pasta...")
        for arquivo_nome in os.listdir(pasta_instancias):
            if arquivo_nome.endswith(".dat"):
                arquivos_para_processar.append(arquivo_nome)
        salvar_solucao_para_este_arquivo = True 
    elif escolha_processamento == 'e':
        arquivo_especifico_nome = input("Digite o NOME do arquivo .dat específico (ex: BHW1.dat): ").strip()
        if not arquivo_especifico_nome.lower().endswith(".dat"):
            arquivo_especifico_nome += ".dat" 
        
        caminho_arquivo_especifico = os.path.join(pasta_instancias, arquivo_especifico_nome)
        if os.path.exists(caminho_arquivo_especifico):
            arquivos_para_processar.append(arquivo_especifico_nome)
            print(f"Modo: Processando arquivo específico: {arquivo_especifico_nome}")
            
            salvar_escolha = input(f"Deseja salvar a solução para '{arquivo_especifico_nome}'? (s/n): ").strip().lower()
            salvar_solucao_para_este_arquivo = (salvar_escolha == 's')
        else:
            print(f"ERRO: Arquivo '{arquivo_especifico_nome}' não encontrado em '{pasta_instancias}'. Encerrando.")
            return 
    else:
        print("Opção inválida. Por favor, digite 'todos' ou 'especifico'. Encerrando.")
        return

    # --- Loop de processamento das instâncias ---
    if not arquivos_para_processar:
        print("Nenhum arquivo .dat encontrado para processar.")
        return

    for arquivo_nome in arquivos_para_processar:
        caminho_completo_instancia = os.path.join(pasta_instancias, arquivo_nome)
        print(f"\n--- Processando instância: {arquivo_nome} ---")

        try:
            # 1. Leitura dos dados e criação do objeto Instancia
            instancia: Instancia = parse_dat_file(caminho_completo_instancia)
        except Exception as e:
            print(f"  ERRO ao ler a instância {arquivo_nome}: {e}")
            import traceback
            traceback.print_exc() 
            continue

        if instancia.capacidade_veiculo == -1:
            print(f"  AVISO: Capacidade do veículo não encontrada ou inválida para {arquivo_nome}. Pulando.")
            continue
        
        print(f"  Dados lidos: {instancia.n_vertices} vértices, Capacidade={instancia.capacidade_veiculo}, Depósito={instancia.depot_idx+1}")

        # 2. Pré-calcular todas as distâncias de caminho mínimo com Floyd-Warshall
        print(f"  Calculando todas as distâncias de caminho mínimo (Floyd-Warshall) para {instancia.n_vertices} vértices...")
        inicio_floyd = time.monotonic_ns()
        distancias_apsp = floyd_warshall(instancia.matriz_adj)
        fim_floyd = time.monotonic_ns()
        print(f"  Cálculo de todas as distâncias concluído em {(fim_floyd - inicio_floyd) / 1e9:.4f}s.")

        # Verificação de alcançabilidade dos serviços a partir do depósito (usando APSP)
        print(f"  Verificando alcançabilidade dos serviços a partir do depósito {instancia.depot_idx+1} (usando APSP)...")
        unreachable_services_from_depot = []
        all_required_elements = (instancia.vertices_requeridos_detalhes +
                                 instancia.arestas_requeridas_detalhes +
                                 instancia.arcos_requeridos_detalhes)
        
        for element in all_required_elements:
            if isinstance(element, VerticeRequerido):
                no_acesso = element.no_idx
                nome_original = f"N{element.no_idx + 1}"
            elif isinstance(element, LigacaoRequerida):
                no_acesso = element.u 
                nome_original = f"{element.tipo.split('_')[0].upper()}_{element.u+1}_{element.v+1}" 
            else:
                nome_original = "Tipo Desconhecido" 
                no_acesso = -1 
                print(f"  AVISO: Elemento de serviço requerido com tipo inesperado: {type(element)}. Pulando.")
                continue

            if not (0 <= no_acesso < instancia.n_vertices):
                print(f"  AVISO: Nó de acesso ({no_acesso+1}) fora dos limites para {nome_original}. Pulando.")
                continue

            cost_from_depot = distancias_apsp[instancia.depot_idx][no_acesso]
            if cost_from_depot == math.inf:
                unreachable_services_from_depot.append(nome_original)
        
        if unreachable_services_from_depot:
            print(f"  ALERTA CONECTIVIDADE ({arquivo_nome}): Os seguintes serviços são INALCANÇÁVEIS do depósito: {', '.join(unreachable_services_from_depot)}")
            print(f"  Isso pode causar rotas incompletas. Verifique a estrutura do grafo ou a leitura dos dados.")
        else:
            print(f"  Todos os {len(all_required_elements)} serviços requeridos são alcançáveis do depósito.")

        # 3. Gerar a solução inicial (Fase 2)
        try:
            solucao_inicial: Solucao = meu_algoritmo_construtivo(
                instancia=instancia, 
                distancias_apsp=distancias_apsp, 
                arquivo_nome_debug=arquivo_nome
            )
            print(f"  Solução inicial construída: Custo={solucao_inicial.custo_total_solucao:.2f}, Rotas={solucao_inicial.num_rotas_solucao}, Tempo={solucao_inicial.tempo_total_s:.4f}s")
            
            # 4. (Fase 3) Otimizar a solução usando busca local
            print("  Aplicando otimização por busca local (Fase 3)...")
            solucao_otimizada: Solucao = otimizar_solucao(
                solucao_inicial=solucao_inicial, # Passa a solução gerada pelo construtivo
                instancia=instancia, 
                distancias_apsp=distancias_apsp
            )
            print(f"  Solução OTIMIZADA: Custo={solucao_otimizada.custo_total_solucao:.2f}, Rotas={solucao_otimizada.num_rotas_solucao}, Tempo={solucao_otimizada.tempo_total_s:.4f}s")

            # A solução final para escrita será a otimizada
            solucao_final_para_escrita = solucao_otimizada 

        except Exception as e:
            print(f"  ERRO ao executar o algoritmo ou otimizador para {arquivo_nome}: {e}")
            import traceback
            traceback.print_exc()
            continue

        # 5. Escrita no arquivo de saída (condicional ao modo e escolha do usuário)
        if salvar_solucao_para_este_arquivo:
            nome_arquivo_saida = f"sol-{os.path.splitext(arquivo_nome)[0]}.dat"
            caminho_saida = os.path.join(pasta_saida, nome_arquivo_saida)

            try:
                with open(caminho_saida, "w") as f_out:
                    # Linhas de cabeçalho da solução
                    f_out.write(f"{solucao_final_para_escrita.custo_total_solucao:.2f}\n")
                    f_out.write(f"{solucao_final_para_escrita.num_rotas_solucao}\n")
                    f_out.write(f"{int(solucao_final_para_escrita.clocks_execucao)}\n") 
                    f_out.write(f"{int(solucao_final_para_escrita.tempo_total_s * 1e9)}\n")

                    # Detalhes de cada rota
                    for rota_info in solucao_final_para_escrita.rotas:
                        # Formato CORRIGIDO para bater com a imagem do professor:
                        # PREFIX_0 PREFIX_1 ID_ROTA DEMANDA CUSTO TOTAL_VISITAS TRAJETORY_STRING
                        # PREFIX_0 = depot_idx (0-indexed)
                        # PREFIX_1 = DIA_ROTEIRIZACAO (1)
                        f_out.write(
                            f"{instancia.depot_idx} {1} {rota_info.id_rota_output} "
                            f"{rota_info.demanda_total_rota:.0f} {rota_info.custo_total_rota:.2f} " 
                            f"{rota_info.total_visitas} {rota_info.trajeto_string_output}\n"
                        )
                print(f"  Solução salva em: {caminho_saida}")
            except Exception as e:
                print(f"  ERRO ao salvar a solução para {arquivo_nome}: {e}")
        else:
            print(f"  Solução para '{arquivo_nome}' não foi salva conforme sua escolha.")
        
if __name__ == "__main__":
    main()
