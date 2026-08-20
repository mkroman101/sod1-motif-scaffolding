"""
Motif geometry comparison via Kabsch-aligned CA RMSD.

[VERIFIED] — this is the exact script used to compare RFdiffusion-designed
motif geometry (raw backbone output, and post-AF2-self-consistency-fold
output) against native reference structure geometry throughout the SOD1
and HCAR1 pilots. No BioPython dependency, numpy only.

Usage pattern used in this project:
- ref_pairs: (chain, resnum) tuples for the native motif residues (e.g.
  SOD1's His63/71/80/83 in 1SOS numbering)
- hal_pairs: (chain, resnum) tuples for the same motif in the RFdiffusion
  "hallucinated" scaffold's own numbering (from each design's .trb file,
  con_hal_pdb_idx field)
"""

import numpy as np


def get_ca_coords(pdb_path, chain_resnum_pairs):
    coords = {}
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                chain = line[21].strip()
                resnum = int(line[22:26])
                if (chain, resnum) in chain_resnum_pairs:
                    x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                    coords[(chain, resnum)] = np.array([x, y, z])
    return coords


def kabsch_rmsd(P, Q):
    """P, Q: Nx3 arrays. Returns (per-point deviation after alignment, RMSD)."""
    Pc = P - P.mean(axis=0)
    Qc = Q - Q.mean(axis=0)
    H = Pc.T @ Qc
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1, 1, d])
    R = Vt.T @ D @ U.T
    P_aligned = (R @ Pc.T).T
    diffs = np.linalg.norm(P_aligned - Qc, axis=1)
    return diffs, np.sqrt((diffs ** 2).mean())


if __name__ == "__main__":
    # Example invocation (SOD1 Zn motif, design_3_seq3 recycled refold vs. native 1SOS)
    ref_pairs = [('A', 63), ('A', 71), ('A', 80), ('A', 83)]
    hal_pairs = [('A', 32), ('A', 59), ('A', 87), ('A', 104)]

    ref_coords = get_ca_coords('reference_structures/1SOS.pdb', ref_pairs)
    hal_coords = get_ca_coords('af2_refold_structure.pdb', hal_pairs)

    P = np.array([hal_coords[p] for p in hal_pairs])
    Q = np.array([ref_coords[p] for p in ref_pairs])

    diffs, rmsd = kabsch_rmsd(P, Q)
    print("Per-residue deviation after alignment (Å):", diffs)
    print("Max deviation:", diffs.max())
    print("RMSD:", rmsd)
