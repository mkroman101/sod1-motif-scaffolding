# SOD1 Motif Scaffolding — Reproducibility Archive

Companion archive to the manuscript in `paper/manuscript_final.docx`
("Motif Scaffolding of a Disease-Relevant Zinc-Binding Site with
RFdiffusion3 on Consumer-Scale Compute: A Reproducible Computational
Pipeline and Case Study"). A plain-text extraction is provided at
`paper/manuscript_final.md` for readability/diffing on GitHub — the
`.docx` is the source of truth if the two ever disagree.

## Status of this archive (updated 2026-08-20)

All experiments the manuscript reports on are complete. Sections are
marked accordingly throughout this archive:

- **[VERIFIED]** — content transcribed directly from commands/output
  actually run and reported during the project (exact commands, exact
  numeric results, exact file paths).
- **[CORRECTED]** — content that was originally [PENDING] and has since
  been pulled directly from the research machine or fixed after review:
  real `conda env export` output, corrected slash-delimited contig
  strings, full `*_full_results.csv` tables (cross-checked against
  narrative summaries), and one confirmed table error (see below).
- **[PENDING]** (genuinely, still) — the AME-benchmark calibration
  subset and the conditioning-ablation experiment (full-residue-frame
  vs. minimal-atom fixing), both explicitly future work per the
  manuscript's Discussion (Section 4.2) — not required for the
  manuscript's present conclusions. Also still pending: GitHub
  repository URL (this repo), Zenodo DOI, and ModelArchive accession —
  not yet requested/deposited.

**One confirmed correction, disclosed rather than silently fixed:**
`results/sod1_zn_pilot_rfdiffusion3_summary.md`'s "RFdiffusion1 vs.
RFdiffusion3" table previously mislabeled the RFdiffusion1 sc_rmsd-alone
count (4/80) as the strict combined pass figure; the correct value is
0/80 (no RFdiffusion1 sequence's motif deviation goes below 2.102 Å, so
none can satisfy the <0.5 Å strict bar). This is now corrected in that
file, and was independently verified during the same-validator
cross-check below.

`CLAUDE_CODE_HANDOFF.md` is kept in this archive as a record of the
prompt used to originally fill in this archive's pending sections, for
provenance.

## Contents

- `paper/manuscript_final.docx` — the current manuscript (source of truth)
- `paper/manuscript_final.md` — plain-text extraction of the above
- `paper/manuscript_draft.md` — superseded working draft, kept for provenance only (see the banner at its top)
- `scripts/motif_geom.py` — Kabsch-alignment motif geometry comparison script
- `scripts/pipeline_commands.md` — verified command history for RFdiffusion1/ProteinMPNN/ColabFold pilots
- `results/sod1_zn_pilot_rfdiffusion1_summary.md` — RFdiffusion1 SOD1 Zn-motif baseline (negative, 0/10)
- `results/sod1_zn_pilot_rfdiffusion3_summary.md` — RFdiffusion3 SOD1 Zn-motif result (primary headline result)
- `results/sod1_zn_rfdiffusion1_openfold3preview_crosscheck.md` — Experiment 2: same-validator cross-check
- `results/disulfide_control_pilot_summary.md` — RFdiffusion1 disulfide control (positive, 4-7/10) — resolves motif-rigidity-vs-batch-size question
- `results/hcar1_pocket_pilot_summary.md` — RFdiffusion1 HCAR1 pocket pilot — exploratory, supplementary only, not carried into the RFdiffusion3 comparison (see manuscript's Supplementary Materials)
- `results/openfold3preview_calibration_summary.md` — OpenFold3-preview wild-type SOD1 calibration vs. 1SOS (PASS)
- `results/phase3_timing_cost_estimate.md` — real timing/VRAM data and compute budget for RFdiffusion3/LigandMPNN/OpenFold3-preview
- `environment/README.md` — environment/dependency notes and version pins for all five tools (rfdiffusion, proteinmpnn, rfdiffusion3, ligandmpnn, openfold3preview)
- `troubleshooting_log.md` — full debugging history across all five tool installs and two RunPod compute runs

## Completed

- **RFdiffusion1 baseline** on the SOD1 Zn motif: negative, 0/10 backbones pass the strict bar
- **Disulfide control**: positive, 4/10 backbones pass the strict bar — resolves that the SOD1 Zn-motif failure is motif-rigidity-specific, not a general pipeline/batch-size limitation
- **RFdiffusion3 comparison** (the manuscript's headline result): 51/80 (64%) ProteinMPNN sequences pass sc_rmsd<2Å, vs. 4/80 (5%) for RFdiffusion1 — a ~12x effect at matched n=10
- **OpenFold3-preview calibration**: PASS, 0.26–0.30 Å RMSD vs. 1SOS across 5 independent samples
- **Experiment 2 (same-validator cross-check)**: the RFdiffusion1-vs-RFdiffusion3 self-consistency advantage persists essentially unchanged (5/80, 6% vs. 51/80, 64%) once the validator confound is removed. A secondary, exploratory finding: on the loosened combined bar (motif geometry included), RFdiffusion1 actually outperforms RFdiffusion3 (4/80 vs. 0/80) — explained by the two models' different geometry trade-offs (Section 3.3/Discussion).
- **HCAR1 pocket pilot**: negative, 0/10 — retained as exploratory supplementary context (domain-mismatch confound noted in its own summary), not part of the main RFdiffusion1-vs-RFdiffusion3 comparison

## What's still genuinely outstanding (not fabricated)

- **AME-benchmark calibration subset** — future calibration work per the manuscript's Discussion; not required for the present conclusions
- **Conditioning-ablation experiment** (full-residue-frame vs. minimal-atom fixing on RFdiffusion3) — future work, specified in the accompanying research plan
- **GitHub repository URL, Zenodo DOI, ModelArchive accession** — the manuscript's Data and Code Availability section still marks these [PENDING]

## Deposition pathway

- **Zenodo** — this archive (versioned, DOI'd) once finalized
- **ModelArchive** — final structure coordinates (best designs)
- **bioRxiv** — the manuscript itself, citing the Zenodo DOI
