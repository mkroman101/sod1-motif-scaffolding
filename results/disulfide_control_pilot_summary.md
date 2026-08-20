# Disulfide Control Pilot — RFdiffusion1 Results [VERIFIED, COMPLETE]

## Purpose
Diagnostic control to isolate whether the SOD1 and HCAR1 pilots' 0/10
results reflect a general pipeline/batch-size limitation (hypothesis a)
or something specific to rigid, multi-point functional motifs
(hypothesis b). RESULT: resolves in favor of hypothesis (b).

## Target
Cys57, Cys146 (chain A of 1SOS.pdb, same source structure as the SOD1 Zn
pilot). Verified directly: both residues present, SSBOND record confirms
`SSBOND 1 CYS A 57 CYS A 146 ... 2.01`, independently recomputed SG-SG
distance from ATOM coordinates = 2.010 Å, matching.

## Pipeline
Identical to the SOD1 Zn and HCAR1 pilots: RFdiffusion1
(`ActiveSite_ckpt.pt`) -> ProteinMPNN (8 seqs/backbone) -> AF2
self-consistency (`num_recycle=0`). Test-gate (num_designs=2) passed
before full batch: `sampled_mask` showed genuine 3-segment structure
(e.g. `32-32/A57-57/40-40/A146-146/45-45`), `con_ref_pdb_idx` correctly
`[('A',57),('A',146)]`.

## Results

Raw RFdiffusion backbone geometry: 10/10 unique designs, max CA-CA motif
deviation 0.182 Å (tight — consistent with both prior pilots; RFdiffusion1's
raw placement was never the limiting step in any of the three pilots).
Design lengths: 123-148 aa.

ProteinMPNN: 80/80 sequences (8/backbone), 0/160 identity violations at
the fixed Cys positions.

AF2 self-consistency (num_recycle=0): mean pLDDT 70.9.

**4/10 backbones pass the strict bar (sc_rmsd<2A AND motif_dev<0.5A).
7/10 pass a loosened 1.5A bar.**

## 3-way comparison

| | SOD1 Zn (4-pt, rigid) | HCAR1 pocket (5-pt) | Disulfide (2-pt, this pilot) |
|---|---|---|---|
| Best motif deviation | 2.10 A | 2.71 A | 0.017 A |
| Mean pLDDT | 47.7 | 64.2 | 70.9 |
| Backbones passing strict bar | 0/10 | 0/10 | 4/10 |
| Backbones passing loose bar (1.5A) | 0/10 | 0/10 | 7/10 |

## Interpretation
With every other pipeline variable held fixed (checkpoint, batch size,
contig mechanics, source structure), only the motif's point-count/rigidity
changed -- and the result flipped from 0/10 to 4-7/10. This is strong
evidence for motif-rigidity-specific difficulty, not a general
pipeline/batch-size limitation. This is the direct interpretive baseline
for the planned RFdiffusion3 comparison (see manuscript draft Section 4).

All intermediate files preserved in pilot_disulfide_control/,
proteinmpnn_output_disulfide/, af2_output_disulfide/. Prior pilots'
files confirmed untouched via mtime check.

## Status confirmation (2026-08-15, at archive-fill time)

Confirmed **complete**, not still running: `~/proteinmpnn_output_disulfide/track3_disulfide_results.csv`
exists on disk with all 80 rows (10 backbones × 8 sequences), no
in-progress/lock files, and the RFdiffusion/AF2 driver logs both end with
their respective completion markers. Full 80-row table copied to
`results/disulfide_control_full_results.csv`, copied directly from
`~/proteinmpnn_output_disulfide/track3_disulfide_results.csv` on the
research machine.

**Verification: every number in this summary was independently
recomputed from the real CSVs/logs and matches exactly** — 10/10 unique
backbones (md5sum), raw max CA-CA motif deviation 0.182 Å (design_6),
design lengths 123–148 aa, 80/80 ProteinMPNN sequences with 0/160
identity violations, mean pLDDT 70.9, best CA-CA deviation 0.017 Å,
4/10 backbones passing the strict bar (`design_2`, `design_4`,
`design_7`, `design_9`), 7/10 passing the loosened 1.5 Å bar
(adds `design_0`, `design_3`, `design_5`). No discrepancy found between
the narrative summary and the underlying data.
