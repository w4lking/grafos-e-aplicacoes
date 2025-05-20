import os
from leitura import parse_dat_file
from referencia import roteirizacao_referencia

def main():
    pasta = "fase2/dados/MCGRP"
    pasta_saida = "fase2/soluções"
    os.makedirs(pasta_saida, exist_ok=True)  # Cria a pasta se não existir

    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".dat"):
            caminho = os.path.join(pasta, arquivo)

            matriz, n_vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos = parse_dat_file(caminho)

            custo_total, num_rotas, clocks, rotas, tempos = roteirizacao_referencia(
                matriz,
                vertices_requeridos,
                arestas_requeridas,
                arcos_requeridos
            )

            print(f"\nSolução de referência para {arquivo}:")
            print(f"  Custo total: {custo_total}")
            print(f"  Número de rotas: {num_rotas}")

            for rota in rotas:
                print(f"  Rota {rota['id_rota']}: {' -> '.join(rota['rota'])} | Custo: {rota['custo']}")

            # Escrita no arquivo de saída
            nome_arquivo_saida = f"sol-{os.path.splitext(arquivo)[0]}.dat"
            caminho_saida = os.path.join(pasta_saida, nome_arquivo_saida)

            with open(caminho_saida, "w") as f:
                f.write(f"{custo_total}\n")
                f.write(f"{num_rotas}\n")
                f.write(f"{clocks}\n")  # Pode ser usado como tempo total em nanossegundos
                f.write(f"{tempos:.0f}\n" if isinstance(tempos, float) else "0\n")  # Ex: 64474 no seu exemplo

                for rota in rotas:
                    rota_id = rota["id_rota"]
                    custo = rota["custo"]
                    caminho_formatado = " ".join(
                        f"(D {v})" if i == 0 or i == len(rota['rota']) - 1 else f"(S {v})"
                        for i, v in enumerate(rota["rota"])
                    )
                    f.write(f"{rota_id} {len(rota['rota'])} {custo} {caminho_formatado}\n")

            break  # Comente para testar todos os arquivos

if __name__ == "__main__":
    main()
