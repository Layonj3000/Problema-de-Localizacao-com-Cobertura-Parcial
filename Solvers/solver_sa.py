"""
solver_sa.py
------------
Meta-heurística Simulated Annealing (SA) para o PLCP.
Versão SUPER OTIMIZADA com Avaliação Delta (Incremental).
"""

from __future__ import annotations
from typing import Dict, List
import time, random, math

def solve_sa(
    inst_name: str,
    inst: Dict[str, object],
    A, 
    D_min: float,
    time_limit: int,
    alpha: float,
    beta: int,
    Ti: float,
    seed: int,
    verbose: bool = False
) -> Dict[str, object]:

    random.seed(seed)
    t0 = time.time()

    n_fac = inst["n_fac"]
    n_cli = inst["n_cli"]
    
    # Pré-processamento rápido para acesso direto
    f_costs = [f[3] for f in inst["facilities"]]
    d_dem = [c[3] for c in inst["clients"]]

    # --- 1. CONSTRUÇÃO DA ADJACÊNCIA (Tuplas são mais rápidas que sets para iterar) ---
    # adj[i] = tupla de índices dos clientes que a facilidade i cobre
    adj = []
    for i in range(n_fac):
        # Cria lista temporária e converte para tupla (imutável e rápida)
        covered_by_i = tuple([j for j in range(n_cli) if A[i][j] == 1])
        adj.append(covered_by_i)
    
    # --- 2. SOLUÇÃO INICIAL ---
    # Precisamos criar o vetor de cobertura inicial
    y_indices = set()
    facilities = list(range(n_fac))
    random.shuffle(facilities)
    
    current_demand = 0.0
    current_cost = 0.0
    
    # coverage_count[j] = quantas facilidades abertas cobrem o cliente j
    coverage_count = [0] * n_cli 
    
    # Construção Gulosa/Aleatória Inicial
    while current_demand < D_min and facilities:
        fac = facilities.pop()
        y_indices.add(fac)
        current_cost += f_costs[fac]
        
        # Atualiza cobertura incrementalmente
        for cli in adj[fac]:
            if coverage_count[cli] == 0:
                current_demand += d_dem[cli]
            coverage_count[cli] += 1
            
    best_y = y_indices.copy()
    best_cost = current_cost
    t_best = 0.0
    T = Ti

    # Cache de variáveis locais para velocidade dentro do loop
    rand_random = random.random
    rand_randint = random.randint
    math_exp = math.exp

    # --- 3. LOOP PRINCIPAL OTIMIZADO ---
    while (time.time() - t0 < time_limit) and (T > 0.01):
        
        for _ in range(beta):
            # Gera candidato aleatório
            cand = rand_randint(0, n_fac - 1)
            
            # --- Lógica Delta (Incremental) ---
            delta_cost = 0.0
            delta_demand = 0.0
            is_removal = cand in y_indices
            
            if is_removal:
                # TENTATIVA DE REMOÇÃO
                # Se eu tirar essa facilidade, quem deixa de ser coberto?
                # Só perde demanda se coverage_count cair de 1 para 0
                for cli in adj[cand]:
                    if coverage_count[cli] == 1:
                        delta_demand -= d_dem[cli]
                
                new_demand = current_demand + delta_demand
                
                # Verifica INVIABILIDADE imediatamente (Short-circuit)
                if new_demand < D_min:
                    continue 

                delta_cost = -f_costs[cand] # Custo diminui
                
            else:
                # TENTATIVA DE ADIÇÃO
                # Se eu colocar essa, quem passa a ser coberto?
                # Só ganha demanda se coverage_count for 0
                for cli in adj[cand]:
                    if coverage_count[cli] == 0:
                        delta_demand += d_dem[cli]
                
                new_demand = current_demand + delta_demand
                delta_cost = f_costs[cand] # Custo aumenta

            # --- Critério de Aceitação (Metropolis) ---
            # delta_cost < 0 (melhorou) ou probabilidade
            accept = False
            if delta_cost < 0:
                accept = True
            else:
                # Otimização: se delta for muito grande, exp é zero, evita overflow
                if rand_random() < math_exp(-delta_cost / T):
                    accept = True
            
            if accept:
                # APLICAR AS MUDANÇAS DEFINITIVAMENTE
                current_cost += delta_cost
                current_demand = new_demand
                
                if is_removal:
                    y_indices.remove(cand)
                    # Atualiza vetor de contagem (Decrementa)
                    for cli in adj[cand]:
                        coverage_count[cli] -= 1
                else:
                    y_indices.add(cand)
                    # Atualiza vetor de contagem (Incrementa)
                    for cli in adj[cand]:
                        coverage_count[cli] += 1
                
                # Atualiza melhor solução
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_y = y_indices.copy() # Aqui o copy é inevitável, mas é raro
                    t_best = time.time() - t0

        # Resfriamento
        T *= alpha

    total_time = time.time() - t0

    if verbose:
        print(f"[SA] FO={best_cost:.2f} | Time={total_time:.2f}s")

    return {
        "UB": best_cost,
        "TIME": total_time,
        "T_BEST": t_best,
        "y": list(best_y)
    }