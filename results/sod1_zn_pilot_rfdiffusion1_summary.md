# SOD1 Zn-Site Motif Scaffolding — RFdiffusion1 Pilot Results [VERIFIED]

## Target
Human SOD1 (PDB 1SOS), native zinc-binding motif: His63, His71, His80,
Asp83 (chain A). Tetrahedral His3Asp1 coordination. Motif scaffolded
"isolated" — no disulfide-subloop structural context included. Checkpoint:
`ActiveSite_ckpt.pt`. Target scaffold size ~150 aa, unconstrained novel
topology.

## Raw RFdiffusion output
10 unique designs (MD5-verified, no duplication), 119–169 aa. Motif CA-CA
geometry within 0.17–0.52 Å of native 1SOS geometry across all 10 — raw
backbone motif placement is tight and reliable.

## ProteinMPNN sequence design
8 sequences per backbone, 80 sequences total. Fixed positions built
per-backbone from each design's own `con_hal_pdb_idx`. 0/80 sequence-
identity violations at the motif positions.

## AF2 self-consistency (local, num_recycle=0)
0/10 backbones designable by the strict bar (self-consistency RMSD < 2 Å
AND motif CA deviation < 0.5 Å from native).

`design_3` was the standout backbone — 4 of its 8 sequences passed the
RMSD threshold:

| Sequence | sc_rmsd (Å) | mean_plddt | max_motif_ca_dev (Å) |
|---|---|---|---|
| design_3_seq6 | 1.146 | 81.0 | 2.68 |
| design_3_seq3 | 1.148 | 85.35 | 2.102 |
| design_3_seq7 | 1.482 | 74.95 | 2.835 |
| design_3_seq4 | 1.571 | 78.85 | 2.919 |
| design_3_seq8 | 3.251 | 73.28 | 3.288 |
| design_3_seq5 | 3.293 | 62.79 | 8.595 |
| design_3_seq2 | 3.53 | 71.38 | 7.339 |
| design_2_seq4 | 3.61 | 65.86 | 13.264 |
| design_3_seq1 | 4.341 | 76.15 | 14.333 |
| design_2_seq8 | 4.374 | 61.23 | 14.018 |

(Top 10 by sc_rmsd shown. Full 80-row table: `results/sod1_zn_full_results.csv`,
copied directly from `~/proteinmpnn_output/track3_results.csv` on the
research machine, 2026-08-15. **Verification: the 10 rows above were
checked programmatically against the real CSV — sc_rmsd, mean_plddt, and
max_motif_ca_dev match exactly for all 10 rows, no discrepancy found.**
Aggregate stats elsewhere in this file (mean pLDDT 47.7, 4/80 self-consistency
pass, best motif dev 2.102 Å, 0/80 at loosened 1.5 Å) were independently
recomputed from the full CSV and also match exactly.)

## Recycling confound — resolved
`design_3_seq3` was refolded on Google Colab with full settings
(`num_recycle=3`, 5 models) to test whether the local `num_recycle=0`
hardware constraint was suppressing a real result.

| Metric | recycle=0 (local) | recycle=3 (Colab) |
|---|---|---|
| mean_plddt | 85.35 | 85–88 (across 5 models) |
| pTM | — | 0.75–0.79 |
| max_motif_ca_dev | 2.102 Å | 1.747 Å |
| motif RMSD (4 pts, Kabsch) | n/a | 1.145 Å |

Per-residue deviation at recycle=3: His63 1.256 Å, His71 0.526 Å, His80
0.580 Å, Asp83 1.747 Å (worst offender, unchanged as the primary problem
residue).

**Verdict:** Recycling produced a real but modest improvement (−17% in max
deviation) that tracked with the overall confidence gain, but did not
close the gap to the 0.5 Å tolerance (still ~3.5×). This is a genuine
negative result at n=10, not a hardware-constraint artifact.

## Interpretation
Pipeline runs correctly end-to-end (raw motif placement is precise;
sequence design has 0 identity violations). The failure is specifically in
the ProteinMPNN→AF2 refold stage — designed sequences do not reliably fold
back into structures that preserve this particular rigid 4-point motif
geometry, at this batch size, using RFdiffusion1 + ActiveSite_ckpt.pt.
