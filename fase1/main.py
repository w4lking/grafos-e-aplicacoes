import os
from fase1.leitura import parse_dat_file
from fase1.estatisticas import calcular_estatisticas_sem_networkx
from fase1.grafo import gerar_grafo_como_lista_adjacencia, desenhar_grafo_no_notebook


# Função principal que percorre os arquivos .dat na pasta "selected_instances"
# Obs: ao rodar o main ele vai ler todos os arquivos .dat que estão na pasta "selected_instances" e gerar os grafo correspondentes a cada arquivo .dat.
# Por tanto é importante rodar no notebook se não quiser que leia 50 arquivos .dat de uma vez só
def main():
    pasta = "sele"

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
