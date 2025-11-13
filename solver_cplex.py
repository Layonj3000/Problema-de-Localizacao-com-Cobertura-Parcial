"""
solver_cplex.py
---------------
Modelo de resolução do PLCP usando o solver CPLEX.
"""

from __future__ import annotations
from typing import Dict
import os, time
from docplex.mp.model import Model

def solve_cplex(
    inst_name: str,
    inst: Dict[str, object],
    A,
    D_min: float,
    time_limit: int = 3600,
    verbose: bool = False,
    outdir: str = "results/models"
) -> Dict[str, object]:
    os.makedirs(outdir, exist_ok=True)
    n_fac, n_cli = inst["n_fac"], inst["n_cli"]
    f_costs = [f[3] for f in inst["facilities"]]
    d_dem = [c[3] for c in inst["clients"]]

    mdl = Model(name=f"PLCP_CPLEX_{inst_name}")
    mdl.parameters.timelimit = time_limit
    mdl.context.solver.show_progress = verbose

    y = {i: mdl.binary_var(name=f"y_{i}") for i in range(n_fac)}
    z = {j: mdl.binary_var(name=f"z_{j}") for j in range(n_cli)}

    mdl.minimize(mdl.sum(f_costs[i]*y[i] for i in range(n_fac)))

    for j in range(n_cli):
        mdl.add_constraint(mdl.sum(A[i][j]*y[i] for i in range(n_fac)) >= z[j])

    mdl.add_constraint(mdl.sum(d_dem[j]*z[j] for j in range(n_cli)) >= D_min)

    lp_path = os.path.join(outdir, f"{inst_name}_cplex.lp")
    mdl.export_as_lp(lp_path)

    t0 = time.time()
    sol = mdl.solve(log_output=verbose)
    t1 = time.time()

    LB = getattr(mdl.get_solve_details(), "best_bound", None)
    UB = sol.get_objective_value() if sol else None
    GAP = 100 * abs(UB - LB) / max(abs(UB), 1e-9) if UB and LB else None

    y_sol = [i for i in range(n_fac) if y[i].solution_value > 0.5]
    z_sol = [j for j in range(n_cli) if z[j].solution_value > 0.5]

    return {"LB": LB, "UB": UB, "GAP": GAP, "TIME": t1-t0, "y": y_sol, "z": z_sol, "model_file": lp_path}
