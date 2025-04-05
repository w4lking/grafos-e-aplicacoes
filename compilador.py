import os
from leitura import parse_dat_file
from estatisticas import calcular_estatisticas

# Pasta onde estão os arquivos fixos
PASTA_INSTANCIAS = "dados"

def processar_instancias():
    arquivos = sorted([f for f in os.listdir(PASTA_INSTANCIAS) if f.endswith(".dat")])

    for arquivo in arquivos:
        caminho = os.path.join(PASTA_INSTANCIAS, arquivo)
        print(f"\n📁 Processando: {arquivo}")
        print("=" * 50)

        try:
            matriz, arestas, arcos, n, vertices_requeridos = parse_dat_file(caminho)
            estatisticas = calcular_estatisticas(matriz, arestas, arcos, vertices_requeridos)

            for chave, valor in estatisticas.items():
                print(f"{chave}: {valor}")
        except Exception as e:
            print(f"❌ Erro ao processar {arquivo}: {e}")
        print("=" * 50)

if __name__ == "__main__":
    processar_instancias()