import os
from fase1.leitura import parse_dat_file
from fase1.estatisticas import calcular_estatisticas_sem_networkx
from fase1.grafo import gerar_grafo_como_lista_adjacencia, desenhar_grafo_no_notebook
from referencia import roteirizacao_referencia  # Importa a roteirização de referência

# Função principal para processamento dos arquivos .dat
def main():
    pasta = "dados/MCGRP"

    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".dat"):  # Garante que só arquivos .dat sejam processados
            caminho = os.path.join(pasta, arquivo)

            # Processa o arquivo e extrai os dados estruturados
            matriz, n_vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos = parse_dat_file(caminho)

            # Exibe estatísticas do grafo baseado nos dados lidos
            print(f"\nEstatísticas para o arquivo: {arquivo}")
            calcular_estatisticas_sem_networkx(
                matriz,
                n_vertices,
                arestas,
                arcos,
                vertices_requeridos,
                arestas_requeridas,
                arcos_requeridos
            )

            # Geração da solução de referência
            custo_total, num_rotas, clocks, rotas = roteirizacao_referencia(
                matriz,
                vertices_requeridos,
                arestas_requeridas,
                arcos_requeridos
            )

            # Exibe as informações da solução de roteirização
            print(f"\nSolução de referência para {arquivo}:")
            print(f"  Custo total: {custo_total}")
            print(f"  Número de rotas: {num_rotas}")
            print(f"  Tempo de CPU: {clocks:.4f}s")

            for rota in rotas:
                print(f"  Rota {rota['id_rota']}: {' -> '.join(rota['rota'])} | Custo: {rota['custo']}")

            # Para testar apenas o primeiro arquivo, descomente a linha abaixo
            break

            # Gera o grafo e desenha no notebook (útil para visualização)
            grafo = gerar_grafo_como_lista_adjacencia(n_vertices, arestas, arcos)
            nome_arquivo = os.path.splitext(arquivo)[0]
            desenhar_grafo_no_notebook(grafo, nome_arquivo, vertices_requeridos, arestas_requeridas, arcos_requeridos)

if __name__ == "__main__":
    main()
