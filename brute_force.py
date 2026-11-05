"""
TSP por força bruta usando backtracking recursivo.

O programa:
1. Gera grafos completos, não direcionados e com custos positivos.
2. Fixa a cidade inicial e enumera recursivamente todas as permutações restantes.
3. Mede o tempo total para cada quantidade de cidades.
4. Conta rotas completas e avaliações de arestas.
5. Salva os resultados em CSV e gera um gráfico com os tempos medidos.

Requisitos:
    pip install matplotlib
"""

from math import factorial
from random import Random
from time import perf_counter
import csv
import matplotlib.pyplot as plt


def gerar_matriz_custos(n, semente=2026, custo_min=1, custo_max=100):
    """
    Gera uma matriz simétrica de custos para um grafo completo.
    A diagonal principal é zero e os custos fora da diagonal são positivos.
    A semente torna os experimentos reproduzíveis.
    """
    if n < 3:
        raise ValueError("O TSP deste experimento precisa de pelo menos 3 cidades.")

    gerador = Random(semente + n)
    matriz = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            custo = gerador.randint(custo_min, custo_max)
            matriz[i][j] = custo
            matriz[j][i] = custo

    return matriz

def resolver_tsp(matriz, cidade_inicial=0):
    """
    Examina todas as (n-1)! permutações das cidades restantes.

    Retorna:
        melhor_caminho: lista com a cidade inicial repetida no final
        melhor_custo: custo da melhor rota
        rotas_avaliadas: quantidade de ciclos completos avaliados
        avaliacoes_arestas: quantidade de custos de arestas somados
        tempo_segundos: tempo total da busca
    """
    n = len(matriz)

    melhor_custo = float("inf")
    melhor_caminho = []

    rotas_avaliadas = 0
    avaliacoes_arestas = 0

    caminho = [cidade_inicial]

    cidades_restantes = [
        cidade for cidade in range(n)
        if cidade != cidade_inicial
    ]

    def calcular_custo_rota(rota):
        """
        Soma o custo das n arestas do ciclo, incluindo o retorno
        à cidade inicial. Conta cada avaliação de aresta.
        """
        nonlocal avaliacoes_arestas

        custo_total = 0

        for i in range(len(rota)):
            origem = rota[i]
            destino = rota[(i + 1) % len(rota)]

            custo_total += matriz[origem][destino]
            avaliacoes_arestas += 1

        return custo_total

    def explorar_permutacoes(restantes):

        nonlocal melhor_custo, melhor_caminho, rotas_avaliadas

        if len(restantes) == 0:
            rotas_avaliadas += 1

            custo = calcular_custo_rota(caminho)

            if custo < melhor_custo:
                melhor_custo = custo
                melhor_caminho = caminho.copy() + [cidade_inicial]

            return
        
        for indice in range(len(restantes)):
            cidade = restantes.pop(indice)
            caminho.append(cidade)

            explorar_permutacoes(restantes)

            caminho.pop()
            restantes.insert(indice, cidade)

    inicio = perf_counter()
    explorar_permutacoes(cidades_restantes)
    fim = perf_counter()

    return {
        "melhor_caminho": melhor_caminho,
        "melhor_custo": melhor_custo,
        "rotas_avaliadas": rotas_avaliadas,
        "avaliacoes_arestas": avaliacoes_arestas,
        "tempo_segundos": fim - inicio,
    }

def executar_benchmarks(n_inicial=3, n_maximo=10):

    resultados = []

    print("BENCHMARK DO TSP POR FORÇA BRUTA")
    print("--------------------------------")
    print(
        f"{'n':>3} | {'Rotas':>12} | {'Arestas':>14} | "
        f"{'n! teórico':>12} | {'Tempo (s)':>12}"
    )
    print("-" * 72)

    for n in range(n_inicial, n_maximo + 1):
        matriz = gerar_matriz_custos(n)
        resultado = resolver_tsp(matriz)

        rotas_teoricas = factorial(n - 1)
        operacoes_teoricas = n * rotas_teoricas

        assert resultado["rotas_avaliadas"] == rotas_teoricas
        assert resultado["avaliacoes_arestas"] == operacoes_teoricas

        registro = {
            "n": n,
            "rotas_avaliadas": resultado["rotas_avaliadas"],
            "avaliacoes_arestas": resultado["avaliacoes_arestas"],
            "n_fatorial_teorico": factorial(n),
            "tempo_segundos": resultado["tempo_segundos"],
            "melhor_custo": resultado["melhor_custo"],
            "melhor_caminho": " -> ".join(
                map(str, resultado["melhor_caminho"])
            ),
        }
        resultados.append(registro)

        print(
            f"{n:>3} | "
            f"{registro['rotas_avaliadas']:>12,} | "
            f"{registro['avaliacoes_arestas']:>14,} | "
            f"{registro['n_fatorial_teorico']:>12,} | "
            f"{registro['tempo_segundos']:>12.6f}"
        )

    return resultados

def salvar_csv(resultados, nome_arquivo="resultados_tsp.csv"):
    if not resultados:
        return

    with open(nome_arquivo, "w", newline="", encoding="utf-8") as arquivo:
        campos = list(resultados[0].keys())
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(resultados)

    print(f"\nTabela salva em: {nome_arquivo}")

def gerar_grafico(resultados, nome_arquivo="grafico_tsp.png"):
    """
    Gera um gráfico comparando:
    - Os tempos medidos experimentalmente;
    - A curva teórica f(n) = c * n!, com c calibrada
      usando o maior valor de n medido.
    """
    if not resultados:
        print("Não há resultados para gerar o gráfico.")
        return

    ns = [r["n"] for r in resultados]
    tempos = [r["tempo_segundos"] for r in resultados]

    maior_n = ns[-1]
    maior_tempo = tempos[-1]

    c = maior_tempo / factorial(maior_n)

    tempos_teoricos = [
        c * factorial(n) for n in ns
    ]

    plt.figure(figsize=(10, 6))

    plt.plot(
        ns,
        tempos,
        marker="o",
        label="Tempo medido experimentalmente"
    )

    plt.plot(
        ns,
        tempos_teoricos,
        marker="s",
        linestyle="--",
        label=f"Curva teórica: c * n! (c = {c:.3e})"
    )

    plt.xlabel("Número de cidades (n)")
    plt.ylabel("Tempo de execução (segundos)")
    plt.title("TSP por força bruta: curva teórica vs. empírica")

    plt.xticks(ns)

    plt.yscale("log")

    plt.grid(True, which="both", linestyle=":")
    plt.legend()

    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=200)
    plt.show()

    print(f"\nConstante de calibração: c = {c:.10e}")
    print(f"Gráfico salvo em: {nome_arquivo}")

if __name__ == "__main__":
    resultados = executar_benchmarks(n_inicial=3, n_maximo=14)

    salvar_csv(resultados)
    gerar_grafico(resultados)
