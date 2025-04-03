import pandas as pd
import os

def ler_arquivo_grafos(caminho):
    if not os.path.exists(caminho):
        print(f"Erro: Arquivo '{caminho}' não encontrado.")
        return None

    dados = {
        "ReN": [],
        "ReE": [],
        "ReA": [],
        "ARC": []
    }
    secao_atual = None

    with open(caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            # Identifica a seção atual
            if linha.startswith("ReN."):
                secao_atual = "ReN"
                continue
            elif linha.startswith("ReE."):
                secao_atual = "ReE"
                continue
            elif linha.startswith("ReA."):
                secao_atual = "ReA"
                continue
            elif linha.startswith("ARC"):
                secao_atual = "ARC"
                continue

            # Ignorar linhas vazias ou cabeçalhos
            if not linha or linha.startswith(("EDGE", "NrA")):
                continue

            # Adiciona os dados da seção correspondente
            if secao_atual:
                dados[secao_atual].append(linha.split())

    return dados

# diretório pai (volta um nível)
diretorio_pai = os.path.dirname(os.getcwd())

# Caminho para selected_instances
pasta_selected_instances = os.path.join(diretorio_pai, "selected_instances")

# Caminho do arquivo dentro desssa pasta
caminho_arquivo = os.path.join(pasta_selected_instances, "BHW1.dat")

# Verificar os arquivos na pasta pra ver se é a certa
if os.path.exists(pasta_selected_instances):
    print("Arquivos na pasta 'selected_instances':", os.listdir(pasta_selected_instances))
else:
    print("Erro: Pasta 'selected_instances' não encontrada.")

dados_processados = ler_arquivo_grafos(caminho_arquivo)

# Se o arquivo foi encontrado e processado, exibir no terminal os dados
if dados_processados:
    for secao, valores in dados_processados.items():
        print(f"\nSeção: {secao}")
        df = pd.DataFrame(valores)
        print(df)
