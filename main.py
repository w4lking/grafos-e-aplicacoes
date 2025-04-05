import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from leitura import parse_dat_file
from estatisticas import calcular_estatisticas

def processar_estatisticas_em_pasta(pasta):
    resultados = []

    for arquivo in sorted(os.listdir(pasta)):
        if arquivo.endswith(".dat"):
            caminho = os.path.join(pasta, arquivo)
            try:
                matriz, arestas, arcos, n, vertices_requeridos = parse_dat_file(caminho)
                stats = calcular_estatisticas(matriz, arestas, arcos, vertices_requeridos)
                stats['arquivo'] = arquivo
                resultados.append(stats)
            except Exception as e:
                print(f"Erro no arquivo {arquivo}: {e}")

    return pd.DataFrame(resultados)

if __name__ == "__main__":
    df = processar_estatisticas_em_pasta("selected_instances")
    print(df)

    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="n_vertices", y="diametro", hue="arquivo")
    plt.title("Relação entre número de vértices e diâmetro")
    plt.show()
