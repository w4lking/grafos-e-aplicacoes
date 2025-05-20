import time

def roteirizacao_referencia(matriz, vertices_requeridos, arestas_requeridas, arcos_requeridos, deposito=0):
    inicio_total_ns = time.monotonic_ns()

    # Etapa 1: Preparação
    inicio_prep_ns = time.monotonic_ns()

    rotas = []
    identificador_rota = 1
    dia = 1
    custo_total = 0
    demanda_total = 1

    mapa_servicos = {}
    for id, (u, v, custo) in enumerate(arestas_requeridas, 1):
        mapa_servicos[(u, v)] = (id, u, v)
        mapa_servicos[(v, u)] = (id, v, u)

    offset = len(arestas_requeridas)
    for id, (u, v, custo) in enumerate(arcos_requeridos, 1):
        mapa_servicos[(u, v)] = (offset + id, u, v)

    fim_prep_ns = time.monotonic_ns()

    # Etapa 2: Geração das rotas
    inicio_rotas_ns = time.monotonic_ns()

    for chave, (id_servico, u, v) in mapa_servicos.items():
        rota = []

        custo_ida = matriz[deposito][u]
        custo_volta = matriz[v][deposito]

        if custo_ida == float('inf') or custo_volta == float('inf'):
            custo_total_rota = float('inf')
        else:
            custo_total_rota = custo_ida + custo_volta
            custo_total += custo_total_rota

        rota.append(f"(D {deposito},{dia},{identificador_rota})")
        rota.append(f"(S {id_servico},{u},{v})")
        rota.append(f"(D {deposito},{dia},{identificador_rota})")

        rotas.append({
            "deposito": deposito,
            "dia": dia,
            "id_rota": identificador_rota,
            "demanda": demanda_total,
            "custo": custo_total_rota,
            "visitas": 3,
            "rota": rota
        })

        identificador_rota += 1

    fim_rotas_ns = time.monotonic_ns()
    fim_total_ns = time.monotonic_ns()

    # Cálculo dos tempos
    tempo_prep = (fim_prep_ns - inicio_prep_ns) / 1e9
    tempo_rotas = (fim_rotas_ns - inicio_rotas_ns) / 1e9
    tempo_total = (fim_total_ns - inicio_total_ns) / 1e9

    # Você pode retornar os tempos também se quiser analisar:
    tempos_execucao = {
        "tempo_preparacao": tempo_prep,
        "tempo_geracao_rotas": tempo_rotas,
        "tempo_total": tempo_total
    }

    print(f"Tempo de preparação: {tempo_prep:.4f}s")
    print(f"Tempo de geração de rotas: {tempo_rotas:.4f}s")
    print(f"Tempo total: {tempo_total:.4f}s")

    return custo_total, len(rotas), tempo_total, rotas, tempos_execucao
