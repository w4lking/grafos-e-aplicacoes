import time

def roteirizacao_referencia(matriz, vertices_requeridos, arestas_requeridas, arcos_requeridos, deposito=0):

    inicio = time.process_time()

    rotas = []
    identificador_rota = 1
    deposito = 0
    dia = 1
    custo_total = 0
    demanda_total = 1  # fictício, pois não temos demanda individual

    # Indexação dos serviços
    servico_id = 1
    mapa_servicos = {}

    for id, (u, v, custo) in enumerate(arestas_requeridas, 1):
        mapa_servicos[(u, v)] = (id, u, v)
        mapa_servicos[(v, u)] = (id, v, u)

    offset = len(arestas_requeridas)
    for id, (u, v, custo) in enumerate(arcos_requeridos, 1):
        mapa_servicos[(u, v)] = (offset + id, u, v)

    # Visitar todos os serviços um a um
    for chave, (id_servico, u, v) in mapa_servicos.items():
        rota = []

        # Ida ao serviço
        custo_ida = matriz[deposito][u]
        custo_volta = matriz[v][deposito]
        custo_servico = custo_ida + custo_volta

        custo_total_rota = custo_servico  # sem contar demanda/custo de serviço, simplificado
        custo_total += custo_total_rota

        # Tripla (X i,j,k): D = depósito, S = serviço
        rota.append(f"(D {deposito},{dia},{identificador_rota})")
        rota.append(f"(S {id_servico},{u},{v})")
        rota.append(f"(D {deposito},{dia},{identificador_rota})")

        total_visitas = 3  # ida, serviço, volta

        rotas.append({
            "deposito": deposito,
            "dia": dia,
            "id_rota": identificador_rota,
            "demanda": demanda_total,
            "custo": custo_total_rota,
            "visitas": total_visitas,
            "rota": rota
        })

        identificador_rota += 1

    fim = time.process_time()
    clocks = fim - inicio

    return custo_total, len(rotas), clocks, rotas