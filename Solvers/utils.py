"""
utils.py
--------
Funções auxiliares para salvar soluções e gerar relatórios.
"""
import os, pandas as pd
from typing import List, Dict

def write_solution_txt(inst_name: str, R: float, solver: str, y: List[int], z: List[int], outdir: str):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{inst_name}_R{R}_{solver}.txt")
    with open(path, "w") as f:
        f.write(" ".join(str(i+1) for i in y) + "\n")
        f.write(" ".join(str(j+1) for j in z) + "\n")
    return path

def save_results_xlsx(records: List[Dict], out_path: str):
    df = pd.DataFrame(records)
    mean = df.mean(numeric_only=True)
    mean_row = {"Instância": "MÉDIA", **mean.to_dict()}
    df = pd.concat([df, pd.DataFrame([mean_row])], ignore_index=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_excel(out_path, index=False)
    print(f"Resultados salvos em: {out_path}")
