# HCAR1 Lactate-Pocket Motif Scaffolding — RFdiffusion1 Pilot Results [VERIFIED]

## Purpose
Second data point to help separate two hypotheses for the SOD1 pilot's
0/10 result: (a) a general pipeline/batch-size limitation, vs. (b)
something specific to rigid, multi-point metal-coordination motifs. HCAR1's
lactate-binding pocket is a chemically distinct motif type — a
solvent-exposed small-molecule binding pocket rather than a buried rigid
metal site.

## Target
Human HCAR1 (GPR81, the lactate receptor), PDB 9IZD (cryo-EM,
HCAR1–Gi complex, agonist CHBA-bound, 3.16 Å resolution). Chain A
extracted and cleaned to `9IZD_chainA_HCAR1.pdb`.

## Motif selection
All chain-A residues within 5 Å of the CHBA ligand computed directly (13
pocket-lining residues found); closest 5-residue cluster selected as the
motif (2.45–3.37 Å closest-atom approach):

- Arg71, Arg99, Tyr268 — carboxylate-recognition shell
- Tyr75, Leu95 — packing near the chlorophenol ring

Independently re-verified against the PDB file via direct `awk`/`grep`
after an initial transcription error in a summary line (TYR95 was
mis-relayed; confirmed the real motif is TYR75 + LEU95 as two separate
residues, no TYR exists at position 95).

**Domain-mismatch caveat:** this motif natively sits within a
7-transmembrane-helix bundle embedded in a lipid membrane. Scaffolding it
"isolated" onto a soluble novel fold (for pipeline consistency with the
SOD1 pilot) is a larger structural leap than the SOD1 case, where the
motif already sat in a soluble globular domain. This confounds direct
comparison — a negative result here cannot be cleanly attributed to motif
chemistry vs. domain mismatch vs. general pipeline limits.

## Results

| Metric | SOD1 Zn site (pilot 1) | HCAR1 pocket (this pilot) |
|---|---|---|
| Designability (strict bar) | 0/10 | 0/10 |
| Self-consistency pass | 4/80 | 2/80 |
| Best motif deviation | 2.10 Å | 2.71 Å |
| Mean pLDDT | 47.7 | 64.2 |
| Loosened tolerance (1.5 Å) | still 0/10 | still 0/10 |

Raw RFdiffusion backbones hit the motif geometry tightly pre-AF2 (mean
0.33 Å across all 10 designs) — same pattern as the SOD1 pilot: the
failure is entirely downstream, in ProteinMPNN/AF2 refold, not in
RFdiffusion's raw motif placement.

Closest-to-passing leads: `design_1` and `design_4` — self-consistent
folds (pLDDT 70–80) with motif geometry still off by ~2.7–4 Å, mirroring
the SOD1 pilot's `design_3` pattern.

Full 80-row table: `results/hcar1_pocket_full_results.csv`, copied
directly from `~/proteinmpnn_output_hcar1/track3_hcar1_results.csv` on
the research machine, 2026-08-15. **Verification: all summary statistics
in the table above (mean pLDDT 64.2, self-consistency pass 2/80, best
motif deviation 2.708 Å [rounded to 2.71], 0/80 at loosened 1.5 Å) were
independently recomputed from the full CSV and match exactly — no
discrepancy found.**

## Interpretation
A chemically very different motif failed the same way, by a similar
margin, at the same pipeline stage. This leans toward a general
pipeline/batch-size limitation rather than metal-coordination-specific
difficulty — but n=10/80 per pilot and the domain-mismatch confound mean
this is not decisive on its own. This is the motivation for the planned
RFdiffusion2 comparison (see manuscript draft) and the disulfide control
pilot (see `disulfide_control_status.md`).
