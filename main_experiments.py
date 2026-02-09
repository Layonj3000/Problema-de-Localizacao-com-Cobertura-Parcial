"""
main_experiments.py
-------------------
Script para gerar os resultados finais (Tabela 2) e arquivos de solução.
Itera sobre todas as instâncias e sobre a lista de Raios (R).
"""
import os
import statistics
import random
from parser_plcp import read_opl_dat, build_coverage_matrix
from solver_sa import solve_sa

# --- CONFIGURAÇÃO ---
# Parâmetros calibrados (Tabela 1)
ALPHA = 0.9888
BETA = 4083
TI = 462.63

TIME_LIMIT = 300  # 5 minutos
NUM_EXECUCOES = 3  # 3 execuções com sementes diferentes

# Lista de Raios para testar 
R_LIST = [3.25, 3.5, 3.75, 4, 4.25]
D_PERCENT = 0.7  # Demanda mínima

# Diretórios
INST_DIR = "instances"  # Pasta onde estão os .dat
OUT_DIR = "final_results" # Pasta para salvar as soluções

def save_best_solution(inst_name, R, result, inst, A_list, out_dir):
    """Salva o arquivo de solução com a melhor FO encontrada."""
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    # Reconstrói Z para o arquivo
    n_cli = inst["n_cli"]
    y_set = set(result["y"])
    covered_clients = set()
    for fac_idx in y_set:
        covered_clients.update(A_list[fac_idx])
    
    # Nome do arquivo inclui o RAIO agora para não sobrescrever
    filename = os.path.join(out_dir, f"solucao_{inst_name}_R{R}.txt")
    
    with open(filename, "w") as f:
        f.write(f"Instancia: {inst_name}\n")
        f.write(f"Raio (R): {R}\n")
        f.write(f"Melhor FO: {result['UB']}\n")
        f.write(f"Tempo Total: {result['TIME']:.4f}\n")
        f.write(f"Facilidades Abertas (y): {sorted(list(y_set))}\n")

def run_experiments():
    # Cabeçalho da tabela
    print(f"{'Instância (Raio)':<50} | {'Melhor FO':<10} | {'FO Média':<10} | {'Desvio(%)':<10} | {'T. Médio':<10} | {'T. Melhor':<10}")
    print("-" * 115)

    # Listas para calcular a média GERAL (de todas as linhas)
    summary_melhor_fo = []
    summary_fo_media = []
    summary_desvio = []
    summary_t_medio = []
    summary_t_melhor = []

    # Itera sobre os arquivos
    files = sorted([f for f in os.listdir(INST_DIR) if f.endswith(".dat")])
    
    for fn in files:
        inst_name_clean = os.path.splitext(fn)[0]
        inst_path = os.path.join(INST_DIR, fn)
        
        # Leitura da Instância (feita uma vez por arquivo)
        inst = read_opl_dat(inst_path)
        total_demand = sum(c[3] for c in inst["clients"])
        D_min = D_PERCENT * total_demand
        n_fac = inst["n_fac"]
        n_cli = inst["n_cli"]

        # --- LOOP DOS RAIOS ---
        for R in R_LIST:
            # Constrói matriz de cobertura para ESTE Raio
            A = build_coverage_matrix(inst, R)
            
            # Lista de adjacência auxiliar para salvar o arquivo final
            A_list_aux = []
            for i in range(n_fac):
                A_list_aux.append({j for j in range(n_cli) if A[i][j] == 1})

            # Armazenar resultados das 3 execuções
            run_fos = []
            run_times = []
            run_t_bests = []
            
            best_run_result = None
            best_fo_global = float('inf')

            # Executa 3 vezes (Seeds)
            for i in range(NUM_EXECUCOES):
                # Gera uma semente aleatória entre 0 e 1 milhão
                seed_aleatoria = random.randint(0, 1000000)
                        
                res = solve_sa(
                    inst_name=inst_name_clean,
                    inst=inst,
                    A=A,
                    D_min=D_min,
                    time_limit=TIME_LIMIT,
                    alpha=ALPHA,
                    beta=BETA,
                    Ti=TI,
                    seed=seed_aleatoria,
                    verbose=False
                )
                
                # Coleta métricas
                fo = res["UB"]
                time_total = res["TIME"]
                t_best = res.get("T_BEST", time_total) 
                
                run_fos.append(fo)
                run_times.append(time_total)
                run_t_bests.append(t_best)

                if fo < best_fo_global:
                    best_fo_global = fo
                    best_run_result = res

            # --- CÁLCULOS DA TABELA ---
            melhor_fo = min(run_fos)
            fo_media = statistics.mean(run_fos)
            
            # Desvio: (|FO Média – Melhor FO| / Melhor FO) * 100
            if melhor_fo > 0:
                desvio = (abs(fo_media - melhor_fo) / melhor_fo) * 100
            else:
                desvio = 0.0
                
            tempo_medio = statistics.mean(run_times)
            t_melhor_medio = statistics.mean(run_t_bests)

            # Nome para exibição na tabela: "Instancia_X (R=3.25)"
            display_name = f"{inst_name_clean} (R={R})"

            print(f"{display_name:<50} | {melhor_fo:<10.2f} | {fo_media:<10.2f} | {desvio:<10.2f} | {tempo_medio:<10.2f} | {t_melhor_medio:<10.2f}")

            # Salva a melhor solução deste Raio
            save_best_solution(inst_name_clean, R, best_run_result, inst, A_list_aux, OUT_DIR)

            # Acumula para a média geral
            summary_melhor_fo.append(melhor_fo)
            summary_fo_media.append(fo_media)
            summary_desvio.append(desvio)
            summary_t_medio.append(tempo_medio)
            summary_t_melhor.append(t_melhor_medio)

    # --- LINHA FINAL DE MÉDIA GERAL ---
    print("-" * 115)
    print(f"{'MÉDIA GERAL':<50} | {statistics.mean(summary_melhor_fo):<10.2f} | {statistics.mean(summary_fo_media):<10.2f} | {statistics.mean(summary_desvio):<10.2f} | {statistics.mean(summary_t_medio):<10.2f} | {statistics.mean(summary_t_melhor):<10.2f}")

if __name__ == "__main__":
    if not os.path.exists(INST_DIR):
        print(f"ERRO: Pasta '{INST_DIR}' não encontrada.")
    else:
        run_experiments()