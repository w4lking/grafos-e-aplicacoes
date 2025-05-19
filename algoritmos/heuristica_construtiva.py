from leitura import ler_arquivo
from grafo import construir_grafo
from algoritmos.floyd_warshall import floyd_warshall

def construir_solucao(nome_arquivo):
    # 1. Ler dados do arquivo: Feito ✔
    dados = ler_arquivo(nome_arquivo)

    # 2. Construir grafo: Feito ✔
    G = construir_grafo(dados)

    # 3. Calcular matriz de distâncias usando Floyd-Warshall: Feito ✔
    distancias = floyd_warshall(G)

    # 4. Aplicar heurística (ex: varrer os serviços requeridos em ordem simples) Não implementado ❌
    # Aqui você pode implementar uma versão básica da heurística de custo mínimo, ou inserção: Não implementado ❌

    # 5. Montar estrutura da solução (custo, rotas, visitas, etc): Não implementado ❌

    # 6. Escrever solução no formato correto
    salvar_arquivo_solucao('dados/padrao_solucoes/sol-BHW1.dat', estrutura_solucao)

    return
