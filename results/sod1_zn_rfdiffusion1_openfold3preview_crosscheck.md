# RFdiffusion1 Same-Validator Cross-Check — OpenFold3-preview

**[VERIFIED] — 2026-08-20.** Experiment 2 (same-validator cross-check),
run per `handoff_experiment2_same_validator.md`. Purpose: test whether the
RFdiffusion1-vs-RFdiffusion3 self-consistency advantage (4/80, 5% vs
51/80, 64%) survives when both design sets are folded by the *same*
validator (OpenFold3-preview), removing the AF2/ColabFold-vs-OpenFold3
validator confound present in the original comparison.

## What was run

The existing 80 RFdiffusion1 ProteinMPNN sequences (10 backbones × 8
sequences, already designed — no new generative modeling) were pulled
directly from `~/proteinmpnn_output/seqs/design_{0..9}.fa` on the local
research machine (not previously copied into this archive) and folded
through the same already-calibrated OpenFold3-preview setup used for the
RFdiffusion3 validation (checkpoint `of3-p2-155k.pt`, public ColabFold MSA
server, `--num-diffusion-samples 1`), on a fresh RunPod A100 pod, batched
10× (8 sequences/backbone/batch) per the project's established
cost-control finding (Section 2.4a of the environment notes).

- Pod environment verified before the full run: single-sequence test fold
  succeeded (exit 0, real output, pLDDT consistent with that sequence's
  original AF2 score) before committing to the batch of 80.
- All 80 sequences folded successfully, 0 failures, ~68 min total A100
  wall time.
- Backbone→sequence structure preserved throughout (10 backbones × 8
  sequences), required for the backbone-level analysis below.
- Self-consistency RMSD computed against each sequence's own source
  RFdiffusion1 backbone (`pilot_zn_scaffold/design_N.pdb`, Kabsch-aligned
  full-chain Cα, matching how self-consistency RMSD is computed elsewhere
  in this project). Motif Cα deviation computed with the project's own
  `scripts/motif_geom.py` method (Kabsch-aligned 4-point, His63/71/80/83
  vs. each backbone's `con_hal_pdb_idx` positions from its `.trb` file).

## Same-validator RFdiffusion1 numbers (n=80)

| Metric | Value |
|---|---|
| Mean pLDDT | 55.44 |
| Mean self-consistency RMSD (global/unfiltered) | 12.26 Å |
| sc_rmsd < 2 Å alone (sequence-level) | 5/80 (6.2%) |
| sc_rmsd < 2 Å alone (backbone-level, ≥1 passing seq) | 1/10 |
| Best motif max-deviation | 1.136 Å (`design_3_seq5`) |
| Strict pass (sc_rmsd<2 Å AND motif dev<0.5 Å), sequence-level | 0/80 |
| Strict pass, backbone-level | 0/10 |
| Loosened pass (sc_rmsd<2 Å AND motif dev<1.5 Å), sequence-level | **4/80 (5%)** |
| Loosened pass, backbone-level | **1/10** |

All 4 loosened-passing sequences are from `design_3` (the same backbone
that was already the standout under the original AF2 validator) —
`design_3_seq5/6/7/8`, motif deviations 1.14–1.40 Å, sc_rmsd 1.29–1.45 Å,
pLDDT 82–88.

**Outlier-rejected self-consistency RMSD, reported separately per the
task's own instruction — with a caveat, not silently trusted:** an
iterative 5-cycle/2.0 Å-cutoff outlier-rejection alignment (matching the
PyMOL method used for the WT calibration) was also computed for every
sequence. For 28/80 sequences it converged to keeping under 50% of the
backbone's residues — on a poorly-folded structure, unbounded outlier
rejection can shrink to a small locally-consistent patch that fits
trivially well, which is not a meaningful "the fold matches" signal. The
outlier-rejected numbers are in the full CSV
(`sc_rmsd_outlier_rejected`, `outlier_residues_retained` /
`outlier_residues_total`) for transparency, but **the pass/fail bars
above use the global/unfiltered sc_rmsd only** — the same metric already
used for every other pass/fail determination in this project — precisely
so this number isn't silently substituted in as if it were comparable.

Full per-sequence results:
`results/sod1_zn_rfdiffusion1_openfold3preview_crosscheck_full_results.csv`
(80 rows: backbone, seq_id, both sc_rmsd variants, motif deviation,
pLDDT).

## Table 3.3-2, restated with the same-validator column added

Matched on ProteinMPNN (n=80) for both RFdiffusion1 and RFdiffusion3, per
this experiment's own framing (both models' apples-to-apples subset —
the manuscript's existing Table 3.3-2 instead compares RFdiffusion1
(n=80) against RFdiffusion3's *combined* ProteinMPNN+LigandMPNN pool
(n=160); that is a separate, pre-existing methodological choice, flagged
here rather than silently carried over into this restatement).

| | RFdiffusion1 + AF2/ColabFold (n=80) | RFdiffusion3 + OpenFold3-preview, ProteinMPNN (n=80) | **RFdiffusion1 + OpenFold3-preview (n=80)** |
|---|---|---|---|
| Mean pLDDT | 47.7 | 80.44 | **55.44** |
| Mean self-consistency RMSD | 14.25 Å | 3.01 Å | **12.26 Å** |
| sc_rmsd < 2 Å alone | 4/80 (5%) | 51/80 (64%) | **5/80 (6%)** |
| sc_rmsd < 2 Å alone, backbone-level | 1/10 | 9/10 | **1/10** |
| Best motif max-deviation | 2.102 Å | 1.649 Å | **1.136 Å** |
| Strict pass (sc_rmsd<2 Å AND motif<0.5 Å) | 0/80 † | 0/80 | **0/80** |
| Loosened pass (sc_rmsd<2 Å AND motif<1.5 Å) | 0/80 | 0/80 ‡ | **4/80 (5%)** |
| Loosened pass, backbone-level | 0/10 | 0/10 ‡ | **1/10** |

† **Correction to the manuscript's existing Table 3.3-2:** that table's
"Strict pass (both criteria)" row currently shows **4/80** for
RFdiffusion1 — this is inconsistent with the same table's own "Best
motif max-deviation: 2.102 Å" row (2.102 Å is not <0.5 Å, so no sequence
can satisfy the strict bar) and with the pilot summary's own text ("0/10
backbones designable by the strict bar"). Independently recomputed here
from the raw CSV: the true value is **0/80**. This appears to be the
same underlying issue as the `motif_within_tol=True` labels on
`design_3_seq3/4/6/7` in `sod1_zn_full_results.csv` despite those rows'
own `max_motif_ca_dev` of 2.1–2.9 Å — flagged separately, not silently
carried forward here. **This should be corrected when Table 3.3-2 is
updated**, independent of this cross-check experiment.

‡ Not previously reported in the manuscript (Section 3.3's tables only
show the strict bar for RFdiffusion3). Recomputed here directly from
`sod1_zn_rfdiffusion3_full_results.csv`'s `motif_post_fold_max_dev_A`
column for the ProteinMPNN arm, for comparability with the loosened
figures above.

## Interpretation

This experiment asked one specific, pre-registered question: does the
**sc_rmsd<2 Å-alone** self-consistency advantage (4/80, 5% vs 51/80, 64%
— the metric explicitly named in the handoff) survive once both design
sets are folded by the same validator. It does: **the advantage
persists, essentially unchanged.** RFdiffusion1 + OpenFold3-preview
scores 5/80 (6%), statistically indistinguishable from the original 4/80
(5%) under AF2/ColabFold, against RFdiffusion3's 51/80 (64%) — a ~10×
effect either way. The original comparison was not an artifact of
AF2/ColabFold being a harsher or more permissive validator than
OpenFold3-preview for this class of design; RFdiffusion1 backbones
genuinely do not fold into themselves reliably, regardless of which tool
folds them.

**A second, unplanned finding surfaced by also computing the
strict/loosened combined bars (as separately instructed for this
experiment):** once motif Cα geometry is required alongside backbone
self-consistency, the picture partially inverts. RFdiffusion1 +
OpenFold3-preview passes the loosened bar on 4/80 sequences (1/10
backbones); RFdiffusion3 + OpenFold3-preview, ProteinMPNN arm, passes on
**0/80** — a number not previously reported in the manuscript, since only
the strict bar was shown for RFdiffusion3 there. This is consistent with,
and explained by, the manuscript's own existing mechanistic account
(Section 3.3): RFdiffusion3's minimal-atom-fixing philosophy guarantees
coordinating-atom geometry but does not tightly constrain the Cα frame,
so raw backbone motif Cα-RMSD is already 1.2–2.1 Å before any folding —
already outside the loosened 1.5 Å bar for most designs, independent of
fold quality. RFdiffusion1's contig-based fixing does the opposite: it
guarantees tight Cα-frame placement (0.17–0.52 Å raw) at the cost of the
fold succeeding at all. Neither model is unambiguously "better" once
motif fidelity, not just backbone foldability, is the question — which
of the two properties matters depends on whether the downstream use case
needs precise catalytic-residue backbone geometry or precise
coordinating-atom placement.

**Bottom line for the research plan's three-way outcome:** on the
specific metric this experiment was designed to test, **the advantage
persists** (not shrinks, not disappears). The loosened-bar finding above
is a genuine, separate result worth carrying into Section 3.3/4.2 — not
a modifier of the primary verdict, but an important caveat on how
"advantage" should be read once motif geometry is factored in.

## Files

- `sod1_zn_rfdiffusion1_openfold3preview_crosscheck_full_results.csv` —
  full 80-row per-sequence results (both sc_rmsd variants, motif
  deviation, pLDDT, outlier-rejection retention diagnostics)
