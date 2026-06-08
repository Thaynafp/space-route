import pandas as pd
import numpy as np
import heapq
import math
from IPython.display import display

import matplotlib.pyplot as plt


# SIMULAÇÃO DE DADOS PARA O GRAFO 
PONTOS = [
    (1, "SGDC-1", 3500, 0.0, -50.0, 0.5), (2, "LEO-N-002", 580, -23.5, -46.6, 2.2),
    (3, "LEO-S-001", 600, -30.0, -51.2, 2.5), (4, "LEO-E-001", 560, -20.0, -35.0, 1.5),
    (5, "LEO-W-001", 540, -10.0, -68.0, 1.1), (14, "LEO-RISCO-1", 560, -22.0, -43.0, 15.0),
    (16, "LEO-RISCO-3", 575, -18.0, -44.0, 18.0), (27, "LEO-SP-001", 555, -21.0, -48.0, 2.2),
    (31, "LEO-MT-001", 530, -15.6, -56.1, 1.8), (32, "LEO-GO-001", 545, -16.6, -49.2, 1.1)
]

def dados():
    df = pd.read_csv('data/objetos_orbitais_brutos.csv')
    
    # Ajuste de nomes de colunas 
    df = df.rename(columns={
        'NORAD_CAT_ID': 'norad_id', 
        'OBJECT_TYPE': 'tipo', 
        'SATNAME': 'nome'
    })
    
    # Cálculo de Altitude 
    df['altitude'] = (df['APOGEE'] + df['PERIGEE']) / 2
    
    # Calculo de simulação de risco de colisão
    df['risco'] = np.where(df['tipo'] == 'DEBRIS', 15.0, 2.0)
    df['risco'] += np.where(df['PERIGEE'] < 600, 5.0, 0.0)
    
    # Separar os conjuntos
    sats = df[df['tipo'] == 'PAYLOAD']
    lixos = df[df['tipo'] == 'DEBRIS']

    return sats, lixos


#ALERTAS 
def processar_alertas(sats, lixos):
    fila_alertas = []
    
    limiar_critico = lixos['risco'].quantile(0.99) 

    for sat in sats.itertuples():
        for lixo in lixos.itertuples():
            if abs(sat.altitude - lixo.altitude) < 50:
                prioridade = 1 if lixo.risco >= limiar_critico else 2
                heapq.heappush(fila_alertas, (prioridade, lixo.risco * -1, sat.nome, lixo.norad_id, lixo.risco))
    
    lista = []
    while fila_alertas:
        p, _, s, n, r = heapq.heappop(fila_alertas)
        lista.append({"Nível": "CRÍTICO" if p == 1 else "ALTO", "Satélite": s, "ID": n, "Risco": round(r, 2)})
    
    if lista:
        df_final = pd.DataFrame(lista)
        display(df_final.head(5))

#GRAFO DE ROTAS 
def construir_grafo(pontos):
    grafo = {p[0]: [] for p in pontos}
    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            p1, p2 = pontos[i], pontos[j]
            dist = math.sqrt((p2[2]-p1[2])**2 + (p2[3]-p1[3])**2 + (p2[4]-p1[4])**2)
            if dist <= 4000:
                peso = dist * (1 + (p1[5] + p2[5]) / 2)
                grafo[p1[0]].append((p2[0], peso)); grafo[p2[0]].append((p1[0], peso))
    return grafo

# LOGICA DAS ROTAS 
def dijkstra(grafo, origem, destino):
    dist = {n: float("inf") for n in grafo}; dist[origem] = 0
    ant = {n: None for n in grafo}; heap = [(0, origem)]
    while heap:
        d, n = heapq.heappop(heap)
        if n == destino: break
        for viz, peso in grafo[n]:
            if d + peso < dist[viz]:
                dist[viz] = d + peso; ant[viz] = n; heapq.heappush(heap, (dist[viz], viz))
    path = []; cur = destino
    while cur: path.append(cur); cur = ant[cur]
    return path[::-1], dist[destino]


# LÓGICA DE OTMIZAÇÃO DE MISSÕES  

def otimizar_missoes(missoes, capacidade):
    n = len(missoes)
    dp = [[0 for _ in range(capacidade + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        nome, risco, custo = missoes[i-1]
        for w in range(capacidade + 1):
            if custo <= w: dp[i][w] = max(risco + dp[i-1][w-custo], dp[i-1][w])
            else: dp[i][w] = dp[i-1][w]
    
    # Rastreamento
    selecionadas, w, custo_total = [], capacidade, 0
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selecionadas.append(missoes[i-1])
            w -= missoes[i-1][2]
            custo_total += missoes[i-1][2]
            

    lista_missao = []
    for m in missoes:
        lista_missao.append({
            "Missão": m[0],
            "Consumo (L)": m[2],
            "Status": "REALIZADA" if m in selecionadas else "PENDENTE"
        })
    return dp[n][capacidade], lista_missao, custo_total

def main():
    print("\nSTATUS DE ALERTA \n")
    
    sats, lixos = dados()
    
    
    processar_alertas(sats, lixos)
    
    missoes = [("Manutencao_GEO", 15, 10), ("Correcao_CBERS", 40, 30), 
               ("Emergencia_SCD", 80, 70), ("Ajuste_Fino", 20, 15)]
    combustivel_total = 100
    ganho, tabela_missoes, gasto = otimizar_missoes(missoes, combustivel_total)
    
    
    print(f"\n\n  OTIMIZAÇÃO EM TAREFAS")
    df_resumo = pd.DataFrame([{
        "Cap Total (L)": combustivel_total,
        "Combus Gasto (L)": gasto,
    }])
    display(df_resumo)
    
    print()
  
    display(pd.DataFrame(tabela_missoes))
    
# 3. Rota Dijkstra
    grafo_calc = construir_grafo(PONTOS)
    rota, custo = dijkstra(grafo_calc, 1, 27)
    
    print(f"\n    ROTA DE DESVIO ")
    
    # Criando o DataFrame para exibir a rota de forma elegante
    df_rota = pd.DataFrame([{
        "Nós da Rota": " -> ".join(map(str, rota)),
        "Custo Total (Litros)": round(custo, 2)
    }])
    
    display(df_rota)
    

    # 2. Visualização 
    plt.figure(figsize=(10, 6), facecolor="#050A1A")
    ax = plt.gca(); ax.set_facecolor("#050A1A")

    # Desenhar conexões
    for nid, vizinhos in grafo_calc.items():
        p1 = next(p for p in PONTOS if p[0] == nid)
        for viz, _ in vizinhos:
            p2 = next(p for p in PONTOS if p[0] == viz)
            plt.plot([p1[4], p2[4]], [p1[3], p2[3]], color="#1A6FA8", alpha=0.3, zorder=1)

    # Desenhar rota otimizada
    for i in range(len(rota)-1):
        n1 = next(p for p in PONTOS if p[0] == rota[i])
        n2 = next(p for p in PONTOS if p[0] == rota[i+1])
        plt.plot([n1[4], n2[4]], [n1[3], n2[3]], color="#4CAF50", linewidth=3, zorder=2)

    # Desenhar nós
    for p in PONTOS:
        cor = "#EF5350" if p[5] > 8 else ("#4FC3F7" if p[0] in [1, 27] else "#4CAF50")
        plt.scatter(p[4], p[3], c=cor, s=150, zorder=3, edgecolors="white")
        plt.text(p[4]+0.5, p[3]+0.5, p[1], color="white", fontsize=8, fontweight='bold', zorder=4)

    plt.title("SpaceRoute Manager: Rota Otimizada do SGDC-1", color="white")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    main()