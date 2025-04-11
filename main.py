import os
from leitura import parse_dat_file
from estatisticas import calcular_estatisticas_sem_networkx
from grafo import gerar_grafo_como_lista_adjacencia, desenhar_grafo_no_notebook

def main():
    pasta = "selected_instances"

    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".dat"):  # Verifica se o arquivo tem extensão .dat
            caminho = os.path.join(pasta, arquivo)

            # Processa o arquivo e extrai os dados
            matriz, n_vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos,  = parse_dat_file(caminho)

            # Exibe as estatísticas no terminal
            print(f"\nEstatísticas para o arquivo: {arquivo}")
            calcular_estatisticas_sem_networkx(matriz, n_vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos, )

            # Gera o grafo e salva como imagem
            grafo = gerar_grafo_como_lista_adjacencia(n_vertices, arestas, arcos)
            nome_arquivo = os.path.splitext(arquivo)[0]
            desenhar_grafo_no_notebook(grafo, nome_arquivo, vertices_requeridos, arestas_requeridas, arcos_requeridos)

if __name__ == "__main__":
    main()
