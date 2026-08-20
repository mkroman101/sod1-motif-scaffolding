"""
Phase 4 analysis: OpenFold3-preview self-consistency validation of the
RFdiffusion3 n=10 SOD1 Zn-motif designs, 160 sequences (10 backbones x
2 arms [ProteinMPNN/LigandMPNN] x 8 seqs), folded via public ColabFold
MSA server.

For each folded model, computes:
  - avg_plddt, ptm, gpde, has_clash, disorder, sample_ranking_score
    (straight from OpenFold3's own confidences_aggregated.json)
  - self_consistency_rmsd: Kabsch CA-RMSD of the full folded backbone
    vs. the originating RFdiffusion3 backbone (same residue indices,
    fixed length per design)
  - motif_post_fold_rmsd: Kabsch CA-RMSD of the 4 Zn-coordinating
    residues (His63/His71/His80/Asp83 in native 1SOS numbering) in the
    folded structure vs. native 1SOS geometry, using each design's own
    diffused_index_map to locate the corresponding residues

Designability bar (per user spec): self_consistency_rmsd < 2.0 A AND
motif_post_fold_rmsd < 0.5 A.
"""
import json
import csv
import re
from pathlib import Path

import numpy as np
import biotite.structure as struc
import biotite.structure.io.pdbx as pdbx
import biotite.structure.io.pdb as pdb

BASE = Path("/home/mkroman/RFdiffusion3/pilot_zn_scaffold_rfd3")
OUT_DIR = BASE / "of3_validation_public_output"
MOTIF_CSV = BASE / "full_n10_motif_geometry.csv"
PDB_DIR = BASE / "full_n10_pdb"
NATIVE_PDB = BASE / "1SOS_chainA_ZN.pdb"

NATIVE_MOTIF_RESNUMS = {"His63": 63, "His71": 71, "His80": 80, "Asp83": 83}


def kabsch_rmsd(P, Q):
    Pc = P - P.mean(axis=0)
    Qc = Q - Q.mean(axis=0)
    H = Pc.T @ Qc
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1, 1, d])
    R = Vt.T @ D @ U.T
    P_aligned = (R @ Pc.T).T
    diffs = np.linalg.norm(P_aligned - Qc, axis=1)
    return diffs, float(np.sqrt((diffs ** 2).mean()))


def get_ca_from_pdb(path, chain="A"):
    """Return dict {resnum: xyz} for CA atoms of given chain."""
    arr = pdb.PDBFile.read(str(path)).get_structure(model=1)
    mask = (arr.chain_id == chain) & (arr.atom_name == "CA")
    sub = arr[mask]
    return {int(rid): xyz for rid, xyz in zip(sub.res_id, sub.coord)}


def get_ca_from_cif(path, chain="A"):
    cif = pdbx.CIFFile.read(str(path))
    arr = pdbx.get_structure(cif, model=1)
    mask = (arr.chain_id == chain) & (arr.atom_name == "CA")
    sub = arr[mask]
    return {int(rid): xyz for rid, xyz in zip(sub.res_id, sub.coord)}


# --- load native motif geometry ---
native_ca = get_ca_from_pdb(NATIVE_PDB, "A")
native_motif_coords = {name: native_ca[rn] for name, rn in NATIVE_MOTIF_RESNUMS.items()}

# --- load per-design backbone info + diffused_index_map ---
design_info = {}  # design_idx -> {"num_residues":, "map": {native_resname: design_resnum}, "backbone_ca": {}}
with open(MOTIF_CSV) as f:
    for row in csv.DictReader(f):
        m = re.search(r"sod1_zn_motif_(\d+)_model_0", row["design_id"])
        idx = int(m.group(1))
        dmap_raw = json.loads(row["diffused_index_map"])
        # dmap_raw keys like "A63" (native) -> "A40" (design); map to plain resnums
        native_to_design_resnum = {}
        for k, v in dmap_raw.items():
            native_resnum = int(k[1:])
            design_resnum = int(v[1:])
            native_to_design_resnum[native_resnum] = design_resnum
        backbone_pdb = PDB_DIR / f"design_{idx}.pdb"
        design_info[idx] = {
            "num_residues": int(row["num_residues"]),
            "native_to_design_resnum": native_to_design_resnum,
            "backbone_ca": get_ca_from_pdb(backbone_pdb, "A"),
            "raw_motif_CA_RMSD_A": float(row["raw_motif_CA_RMSD_A"]),
        }

# resnum -> motif name, for lookups
resnum_to_motifname = {v: k for k, v in NATIVE_MOTIF_RESNUMS.items()}

results = []
missing = []

query_dirs = [
    d for subbatch in OUT_DIR.iterdir() if subbatch.is_dir()
    for d in subbatch.iterdir() if d.is_dir() and re.match(r"d\d+_(proteinmpnn|ligandmpnn)_seq\d+", d.name)
]

for qdir in sorted(query_dirs, key=lambda p: p.name):
    qname = qdir.name
    m = re.match(r"d(\d+)_(proteinmpnn|ligandmpnn)_seq(\d+)", qname)
    design_idx, arm, seq_idx = int(m.group(1)), m.group(2), int(m.group(3))

    seed_dirs = list(qdir.glob("seed_*"))
    if not seed_dirs:
        missing.append(qname)
        continue
    seed_dir = seed_dirs[0]
    cif_files = list(seed_dir.glob("*_sample_1_model.cif"))
    conf_files = list(seed_dir.glob("*_sample_1_confidences_aggregated.json"))
    if not cif_files or not conf_files:
        missing.append(qname)
        continue

    conf = json.load(open(conf_files[0]))
    folded_ca = get_ca_from_cif(cif_files[0], "A")

    dinfo = design_info[design_idx]
    backbone_ca = dinfo["backbone_ca"]

    # --- self-consistency RMSD: full backbone, matched residue indices ---
    common_resnums = sorted(set(folded_ca.keys()) & set(backbone_ca.keys()))
    P = np.array([folded_ca[r] for r in common_resnums])
    Q = np.array([backbone_ca[r] for r in common_resnums])
    _, sc_rmsd = kabsch_rmsd(P, Q)

    # --- post-fold motif geometry vs native ---
    native_to_design = dinfo["native_to_design_resnum"]
    motif_names_ordered = ["His63", "His71", "His80", "Asp83"]
    try:
        folded_motif_coords = []
        native_motif_ordered = []
        for name in motif_names_ordered:
            native_resnum = NATIVE_MOTIF_RESNUMS[name]
            design_resnum = native_to_design[native_resnum]
            folded_motif_coords.append(folded_ca[design_resnum])
            native_motif_ordered.append(native_motif_coords[name])
        P2 = np.array(folded_motif_coords)
        Q2 = np.array(native_motif_ordered)
        diffs2, motif_rmsd = kabsch_rmsd(P2, Q2)
        motif_max_dev = float(diffs2.max())
    except KeyError:
        motif_rmsd = float("nan")
        motif_max_dev = float("nan")

    # NOTE: designability bar matches the RFdiffusion1 baseline methodology
    # exactly (results/sod1_zn_full_results.csv): motif criterion is MAX
    # per-residue deviation after Kabsch alignment, not RMSD across the 4
    # points (RMSD is reported alongside for reference but not used for
    # the pass/fail bar).
    designable = (sc_rmsd < 2.0) and (motif_max_dev < 0.5)

    results.append({
        "query": qname,
        "design_idx": design_idx,
        "arm": arm,
        "seq_idx": seq_idx,
        "num_residues_matched": len(common_resnums),
        "num_residues_expected": dinfo["num_residues"],
        "avg_plddt": conf["avg_plddt"],
        "ptm": conf["ptm"],
        "gpde": conf["gpde"],
        "has_clash": conf["has_clash"],
        "disorder": conf["disorder"],
        "sample_ranking_score": conf["sample_ranking_score"],
        "self_consistency_rmsd_A": round(sc_rmsd, 4),
        "motif_post_fold_rmsd_A": round(motif_rmsd, 4),
        "motif_post_fold_max_dev_A": round(motif_max_dev, 4),
        "raw_backbone_motif_rmsd_A": dinfo["raw_motif_CA_RMSD_A"],
        "designable_strict": designable,
    })

print(f"Processed {len(results)} / 160 queries. Missing: {missing}")

out_csv = BASE / "of3_validation_public_results.csv"
with open(out_csv, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    writer.writeheader()
    writer.writerows(results)
print(f"Wrote {out_csv}")

# --- summary stats ---
import statistics as stats

for arm in ["proteinmpnn", "ligandmpnn"]:
    arm_rows = [r for r in results if r["arm"] == arm]
    n = len(arm_rows)
    n_pass = sum(r["designable_strict"] for r in arm_rows)
    mean_plddt = stats.mean(r["avg_plddt"] for r in arm_rows)
    mean_sc = stats.mean(r["self_consistency_rmsd_A"] for r in arm_rows)
    mean_motif = stats.mean(r["motif_post_fold_rmsd_A"] for r in arm_rows)
    mean_motif_max = stats.mean(r["motif_post_fold_max_dev_A"] for r in arm_rows)
    best_motif_max = min(r["motif_post_fold_max_dev_A"] for r in arm_rows)
    n_sc_only = sum(r["self_consistency_rmsd_A"] < 2.0 for r in arm_rows)
    print(f"\n=== {arm} (n={n}) ===")
    print(f"  designability strict (sc_rmsd<2A AND max_motif_dev<0.5A): {n_pass}/{n}")
    print(f"  sc_rmsd<2A alone: {n_sc_only}/{n}")
    print(f"  mean avg_plddt: {mean_plddt:.2f}")
    print(f"  mean self_consistency_rmsd: {mean_sc:.3f} A")
    print(f"  mean motif_post_fold_rmsd (4-pt Kabsch): {mean_motif:.3f} A")
    print(f"  mean motif_post_fold_max_dev: {mean_motif_max:.3f} A")
    print(f"  best (min) motif_post_fold_max_dev: {best_motif_max:.3f} A")

n_pass_total = sum(r["designable_strict"] for r in results)
print(f"\n=== OVERALL (n={len(results)}) ===")
print(f"  designability: {n_pass_total}/{len(results)}")
