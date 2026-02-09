import argparse
import random
from parser_plcp import read_opl_dat, build_coverage_matrix
from solver_sa import solve_sa

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('configuration_id')
    parser.add_argument('instance_id')
    parser.add_argument('seed', type=int)
    parser.add_argument('instance')

    parser.add_argument('--alpha', type=float, required=True)
    parser.add_argument('--beta', type=int, required=True)
    parser.add_argument('--Ti', type=float, required=True)
    
    args = parser.parse_args()

    random.seed(args.seed)
    
    inst = read_opl_dat(args.instance)
    
    R = 3.25 
    
    D_PERCENT = 0.7
    total_demand = sum(c[3] for c in inst["clients"])
    D_min = D_PERCENT * total_demand
    
    A = build_coverage_matrix(inst, R)
    
    result = solve_sa(
        inst_name="IRACE_TUNING",
        inst=inst,
        A=A,
        D_min=D_min,
        time_limit=300, 
        alpha=args.alpha,
        beta=args.beta,
        Ti=args.Ti,
        seed=args.seed,
        verbose=False
    )

    if result["UB"] is None or result["UB"] == float('inf'):
        print(99999999)
    else:
        print(result["UB"])

if __name__ == "__main__":
    main()