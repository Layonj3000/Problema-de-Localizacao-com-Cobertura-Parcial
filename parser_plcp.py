"""
parser_plcp.py
-------------
Módulo responsável pela leitura e interpretação das instâncias
do Problema de Localização com Cobertura Parcial (PLCP) no formato .dat.

Formato esperado:
    Primeira linha: <n_facilities> <n_clients>
    Linhas seguintes:
        F id x y cost
        C id x y demand
"""

from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np

def read_opl_dat(path: str) -> Dict[str, object]:
    """
    Lê uma instância PLCP no formato .dat (estilo OPL).

    Args:
        path: Caminho para o arquivo .dat

    Returns:
        Um dicionário com:
            - n_fac (int): número de instalações
            - n_cli (int): número de clientes
            - facilities (list[tuple]): (id, x, y, cost)
            - clients (list[tuple]): (id, x, y, demand)
    """
    facilities: List[Tuple[int, float, float, float]] = []
    clients: List[Tuple[int, float, float, float]] = []

    with open(path, 'r') as f:
        lines = [
            ln.strip() for ln in f
            if ln.strip() and not ln.strip().startswith(("//", "#"))
        ]

    if not lines:
        raise ValueError("Arquivo vazio ou inválido.")

    header = lines[0].split()
    if len(header) < 2:
        raise ValueError("Primeira linha deve conter n_fac e n_cli.")

    n_fac, n_cli = map(int, header[:2])

    for ln in lines[1:]:
        parts = ln.split()
        if parts[0].upper() == 'F':
            fid, x, y, cost = int(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            facilities.append((fid, x, y, cost))
        elif parts[0].upper() == 'C':
            cid, x, y, demand = int(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            clients.append((cid, x, y, demand))

    return {
        "n_fac": len(facilities),
        "n_cli": len(clients),
        "facilities": sorted(facilities),
        "clients": sorted(clients)
    }

def build_coverage_matrix(inst: Dict[str, object], R: float) -> np.ndarray:
    """
    Constrói a matriz de cobertura A[i][j] = 1 se dist(i,j) <= R.

    Args:
        inst: Dicionário retornado por read_opl_dat
        R: Raio de cobertura

    Returns:
        np.ndarray binária de tamanho (n_fac, n_cli)
    """
    fac_xy = np.array([[f[1], f[2]] for f in inst["facilities"]])
    cli_xy = np.array([[c[1], c[2]] for c in inst["clients"]])
    dist = np.sqrt(((fac_xy[:, None, :] - cli_xy[None, :, :]) ** 2).sum(axis=2))
    return (dist <= R).astype(int)
