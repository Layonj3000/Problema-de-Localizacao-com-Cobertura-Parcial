"""
main.py
-------
Roda todas as instâncias do PLCP com CPLEX e Gurobi.
"""
import os, argparse
from parser_plcp import read_opl_dat, build_coverage_matrix
from solver_gurobi import solve_gurobi
from solver_cplex import solve_cplex
from utils import write_solution_txt, save_results_xlsx

R_LIST = [5.5, 5.75, 6.0, 6.25]
D_PERCENT = 0.5

def run_all(inst_dir: str, out_dir: str, time_limit: int = 3600):
    records = []
    for fn in sorted(os.listdir(inst_dir)):
        if not fn.endswith(".dat"):
            continue
        inst_name = os.path.splitext(fn)[0]
        inst_path = os.path.join(inst_dir, fn)
        inst = read_opl_dat(inst_path)
        total_demand = sum(c[3] for c in inst["clients"])
        D_min = D_PERCENT * total_demand

        for R in R_LIST:
            print(f"\n[{inst_name}] Rodando R={R} D=50% ...")
            A = build_coverage_matrix(inst, R)

            # GUROBI
            res_g = solve_gurobi(inst_name, inst, A, D_min, time_limit)
            write_solution_txt(inst_name, R, "GUROBI", res_g["y"], res_g["z"], f"{out_dir}/solutions")
            records.append({"Instância": inst_name, "Solver": "GUROBI", "R": R, **{k: res_g[k] for k in ["LB","UB","GAP","TIME"]}})

            # CPLEX
            res_c = solve_cplex(inst_name, inst, A, D_min, time_limit)
            write_solution_txt(inst_name, R, "CPLEX", res_c["y"], res_c["z"], f"{out_dir}/solutions")
            records.append({"Instância": inst_name, "Solver": "CPLEX", "R": R, **{k: res_c[k] for k in ["LB","UB","GAP","TIME"]}})

    save_results_xlsx(records, f"{out_dir}/results.xlsx")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inst_dir", default="instances")
    parser.add_argument("--out_dir", default="results")
    parser.add_argument("--time_limit", type=int, default=3600)
    args = parser.parse_args()
    run_all(args.inst_dir, args.out_dir, args.time_limit)
