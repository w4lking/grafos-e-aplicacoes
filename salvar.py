import os

def salvar_estatisticas_txt(nome_instancia, estatisticas, pasta_saida="estatisticas_txt"):
    os.makedirs(pasta_saida, exist_ok=True)
    caminho = os.path.join(pasta_saida, f"{nome_instancia}_estatisticas.txt")

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"Estatísticas para {nome_instancia}\n")
        f.write("=" * 40 + "\n")
        for chave, valor in estatisticas.items():
            f.write(f"{chave}: {valor}\n")
