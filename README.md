# SOD1 Motif Scaffolding — Reproducibility Archive

Companion archive to the manuscript draft in `paper/manuscript_draft.md`.

## Status of this archive

This bundle was originally assembled from a working conversation log, not
by direct export from the source machine. It has since been filled in
(2026-08-15) by running the prompt in `CLAUDE_CODE_HANDOFF.md` directly on
the research machine (WSL2/Ubuntu, RTX 3070). Sections are marked
accordingly:

- **[VERIFIED]** — content transcribed directly from commands/output actually
  run and reported during the project (exact commands, exact numeric
  results, exact file paths).
- **[CORRECTED]** / real exports — content that was originally
  [PENDING] and has now been pulled directly from the research machine:
  real `conda env export` output, the corrected slash-delimited contig
  strings (pulled from each pilot's `.trb` `config.contigmap.contigs`
  field), the full `*_full_results.csv` tables (all cross-checked against
  the narrative summaries — no discrepancies found), the disulfide-control
  pilot's full results, and `.trb` metadata for the three standout
  designs.
- **[PENDING]** (genuinely, still) — content that does not yet exist
  because the underlying experiment has not been run: RFdiffusion3,
  OpenFold3-preview calibration, AME-benchmark calibration subset,
  LigandMPNN, and the GitHub/Zenodo/ModelArchive accession numbers (this
  repository has not yet been pushed anywhere). See the manuscript draft
  for exactly which sections remain open.

`CLAUDE_CODE_HANDOFF.md` is kept in this archive as a record of the
prompt used to do the above, for provenance.

## Contents

- `paper/manuscript_draft.md` — working manuscript draft
- `scripts/motif_geom.py` — Kabsch-alignment motif geometry comparison script (verified, full content)
- `scripts/pipeline_commands.md` — verified command history for RFdiffusion1/ProteinMPNN/ColabFold pilots
- `results/sod1_zn_pilot_rfdiffusion1_summary.md` — completed pilot 1 results
- `results/hcar1_pocket_pilot_summary.md` — completed pilot 2 results
- `results/disulfide_control_pilot_summary.md` — completed pilot 3 results (positive — resolves the rigidity-vs-batch-size question)
- `results/openfold3preview_calibration_summary.md` — OpenFold3-preview wild-type SOD1 calibration vs. 1SOS (PASS)
- `results/phase3_timing_cost_estimate.md` — real timing/VRAM data for RFdiffusion3/LigandMPNN/OpenFold3-preview and full experiment compute budget
- `environment/README.md` — environment/dependency notes and known version pins (now including `rfdiffusion3`, `ligandmpnn`, `openfold3preview`)
- `troubleshooting_log.md` — full debugging history (WSL2/CUDA/DGL/RFdiffusion install issues and fixes; now including RFdiffusion3/LigandMPNN/OpenFold3-preview issues, entries #12–#17)

## What's NOT yet in this archive (genuinely outstanding, not fabricated)

- RFdiffusion3 results on the SOD1 motif (not yet run — this is the paper's headline result; tooling is now installed/verified, see below)
- AME-benchmark calibration subset results (not yet run; real per-case cost data now available to size the subset — see `results/phase3_timing_cost_estimate.md`)
- LigandMPNN results on the novel SOD1-motif designs (not yet run — tool is installed and verified on the existing pilot backbone; the actual n=10 experiment is a separate, explicit go-ahead)
- GitHub repository URL, Zenodo DOI, ModelArchive accession — this repo has not yet been pushed/deposited anywhere

## Now included (filled in 2026-08-16 — RFdiffusion3/LigandMPNN/OpenFold3-preview install, verify, calibrate handoff)

- RFdiffusion3, LigandMPNN, and OpenFold3-preview all installed and verified (`environment/README.md`)
- **OpenFold3-preview calibration: PASS** — wild-type SOD1 vs. 1SOS, 0.26–0.30 Å RMSD across 5 independent samples, beats the 0.361 Å AF2/ColabFold benchmark (`results/openfold3preview_calibration_summary.md`)
- Real timing/VRAM data for all three tools at the project's ~150aa target scale, plus a full compute budget estimate for the eventual n=10 experiment (`results/phase3_timing_cost_estimate.md`) — headline finding: only OpenFold3-preview needed rented compute, and batching queries into it cuts projected cost by ~27×
- 6 new troubleshooting log entries (`troubleshooting_log.md`, #12–#17)

## Previously included (filled in 2026-08-15, previously [PENDING])

- Full raw `.csv` result tables for all three completed pilots (`results/*_full_results.csv`)
- Real `conda env export` output for both the `rfdiffusion` and `proteinmpnn` environments (`environment/*_env_export.yml`) — flagged one real discrepancy vs. the transcribed torch pin, see `environment/README.md`
- Real `.trb` metadata for the three standout designs (`results/trb_metadata/`)
- Corrected, verified slash-delimited `contigmap.contigs` strings for all three pilots (`scripts/pipeline_commands.md`)
- Disulfide-control pilot results, confirmed complete and cross-verified against its full CSV

## Completed (as of this snapshot)

All three RFdiffusion1 pilots are complete: SOD1 zinc site (negative,
0/10), HCAR1 lactate pocket (negative, 0/10), and the disulfide control
(positive, 4-7/10) — together resolving that RFdiffusion1's failures were
motif-rigidity-specific, not a general pipeline/batch-size limitation.
This is the empirical baseline the RFdiffusion3 comparison is designed to
extend.

## Deposition pathway

- **Zenodo** — this archive (versioned, DOI'd) once finalized
- **ModelArchive** — final structure coordinates (best designs, both RFdiffusion1 and RFdiffusion2 outputs)
- **Pfam/UniProt** — not applicable to this sub-project (used for Track 2 DUF work)
- **bioRxiv** — the manuscript itself, citing the Zenodo DOI
