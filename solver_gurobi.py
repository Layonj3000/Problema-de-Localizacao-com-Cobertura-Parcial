"""
solver_gurobi.py
----------------
Modelo de resolução do PLCP usando o solver Gurobi.
"""

from __future__ import annotations
from typing import Dict, List, Optional
import os, time
from gurobipy import Model, GRB, quicksum

def solve_gurobi(
    inst_name: str,
    inst: Dict[str, object],
    A,
    D_min: float,
    time_limit: int = 3600,
    verbose: bool = False,
    outdir: str = "results/models"
) -> Dict[str, object]:
    """
    Resolve o PLCP com Gurobi (minimiza custo de instalação).

    Args:
        inst_name: nome da instância
        inst: dados da instância
        A: matriz de cobertura
        D_min: demanda mínima a ser coberta
        time_limit: tempo limite em segundos
        verbose: modo detalhado
        outdir: pasta de saída para .lp

    Returns:
        Dicionário com LB, UB, GAP, TIME, y, z
    """
    os.makedirs(outdir, exist_ok=True)
    n_fac, n_cli = inst["n_fac"], inst["n_cli"]
    f_costs = [f[3] for f in inst["facilities"]]
    d_dem = [c[3] for c in inst["clients"]]

    model = Model(f"PLCP_GUROBI_{inst_name}")
    model.setParam("TimeLimit", time_limit)
    model.setParam("OutputFlag", 1 if verbose else 0)

    y = model.addVars(n_fac, vtype=GRB.BINARY, name="y")
    z = model.addVars(n_cli, vtype=GRB.BINARY, name="z")

    model.setObjective(quicksum(f_costs[i]*y[i] for i in range(n_fac)), GRB.MINIMIZE)

    for j in range(n_cli):
        model.addConstr(quicksum(A[i][j]*y[i] for i in range(n_fac)) >= z[j])

    model.addConstr(quicksum(d_dem[j]*z[j] for j in range(n_cli)) >= D_min)

    lp_path = os.path.join(outdir, f"{inst_name}_gurobi.lp")
    model.write(lp_path)

    t0 = time.time()
    model.optimize()
    t1 = time.time()

    res = {
        "LB": model.ObjBound if model.SolCount > 0 else None,
        "UB": model.ObjVal if model.SolCount > 0 else None,
        "GAP": None,
        "TIME": t1 - t0,
        "y": [i for i in range(n_fac) if y[i].X > 0.5],
        "z": [j for j in range(n_cli) if z[j].X > 0.5],
        "model_file": lp_path
    }

    if res["UB"] and res["LB"]:
        res["GAP"] = 100 * abs(res["UB"] - res["LB"]) / max(abs(res["UB"]), 1e-9)

    return res
