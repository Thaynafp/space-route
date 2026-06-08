# SpaceRoute Manager 🚀

Sistema de inteligência orbital focado em **roteamento seguro e otimização de missões** para satélites, desenvolvido como Global Solution.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python
* **Bibliotecas:** `pandas`, `numpy`, `heapq` (Fila de Prioridade), `matplotlib`, `IPython`
* **Algoritmos:** Dijkstra (Roteamento), Programação Dinâmica (Otimização de Missões 0/1)

## 📋 Funcionalidades
1. **Monitoramento de Risco:** Processa dados da [Space-Track](https://www.space-track.org/) para identificar colisões potenciais.
2. **Fila de Prioridade (HeapQ):** Triagem automatizada de alertas orbitais, classificando riscos em *CRÍTICO* ou *ALTO*.
3. **Otimização de Missões (DP):** Seleção inteligente de tarefas de manutenção respeitando a limitação de combustível (litros).
4. **Roteamento Espacial (Dijkstra):** Cálculo da rota mais eficiente desviando de zonas de detritos.
5. **Visualização:** Gráfico dinâmico da malha orbital com destaque para a rota otimizada.

## 🚀 Como Executar
1. Certifique-se de ter o arquivo `objetos_orbitais_brutos.csv` na pasta `/data`.
2. Instale as dependências:
   ```bash
   pip install pandas numpy matplotlib ipython