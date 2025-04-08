import os
from leitura import parse_dat_file
from estatisticas import calcular_estatisticas_sem_networkx

def main():
    pasta = "selected_instances"  # Define a pasta onde os arquivos .dat estão localizados

    # Itera sobre todos os arquivos na pasta
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".dat"):  # Verifica se o arquivo tem extensão .dat
            caminho = os.path.join(pasta, arquivo)

            # Processa o arquivo e extrai os dados
            matriz, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos, n_vertices, n_arestas, n_arcos = parse_dat_file(caminho)

            # Exibe as estatísticas no terminal
            print(f"\nEstatísticas para o arquivo: {arquivo}")
            calcular_estatisticas_sem_networkx(matriz, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos, n_vertices)

if __name__ == "__main__":
    main()
