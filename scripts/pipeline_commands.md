# Pipeline Commands — Verified Command History

All commands below were actually run (or are the corrected versions of
commands that were run and then fixed) during the RFdiffusion1 pilots.
[VERIFIED] unless noted.

## Environment setup — `rfdiffusion` conda env

```bash
conda create -n rfdiffusion python=3.10 -y
conda activate rfdiffusion
git clone https://github.com/RosettaCommons/RFdiffusion.git
cd RFdiffusion
```

**Final working install sequence** (after resolving a torch/CUDA/DGL version
cascade — see `troubleshooting_log.md` for the full debugging path):

```bash
# Env was rebuilt from the repo's own pinned environment file rather than
# hand-resolved, after repeated dependency conflicts:
conda env create -f env/SE3nv.yml -n rfdiffusion
conda activate rfdiffusion

# se3-transformer must be installed via `pip install .`, NOT
# `python setup.py install` (the latter silently registers egg-info
# metadata without copying the actual package files):
cd env/SE3Transformer
pip install .
cd ../..

pip install -e . --no-deps   # RFdiffusion itself

# Additional runtime dependencies not captured by SE3nv.yml or pyproject.toml:
pip install opt_einsum
pip install e3nn
```

Final Python version in this env: 3.9 (via SE3nv.yml, not the original 3.10).
Final torch: 2.1.0+cu121 (explicitly pinned — see troubleshooting log for why).

## Model weights

```bash
mkdir -p models
bash scripts/download_models.sh models
```

7 checkpoints downloaded, 3.2 GB total. Only `ActiveSite_ckpt.pt` was used
for the motif-scaffolding pilots (fine-tuned for keeping small motifs in
place during scaffolding — a better fit than the base checkpoint for
4-6 residue point motifs).

## RFdiffusion motif scaffolding — SOD1 Zn site

**[CORRECTED — pulled directly from `design_0.trb` and `design_5.trb`'s
`config.contigmap.contigs` field on 2026-08-15, both agree.]**
The comma-delimited contig string below is the ORIGINAL, BUGGY version —
it parsed into RFdiffusion's config correctly but silently collapsed to
unconditional generation at the sampler level (`sampled_mask` showed a
single unconstrained block; `con_ref_pdb_idx`/`con_hal_pdb_idx` came back
empty). The fix (found via Claude Code) was switching to slash-delimited
segments. Kept side by side deliberately — the buggy version has
illustrative value for the troubleshooting log (see entry #10 there);
do not delete it.

```bash
# BUGGY (comma-delimited — DO NOT USE, kept here for reference/troubleshooting log):
python scripts/run_inference.py \
  inference.output_prefix=pilot_zn_scaffold/design \
  inference.ckpt_override_path=models/ActiveSite_ckpt.pt \
  'contigmap.contigs=[30-40,A63-63,20-30,A71-71,20-30,A80-80,15-25,A83-83,30-40]' \
  inference.input_pdb=/home/mkroman/reference_structures/1SOS.pdb \
  inference.num_designs=10
```

```bash
# CORRECTED (slash-delimited — this is what was actually run to produce
# pilot_zn_scaffold/design_0..9.pdb, confirmed via .trb config.contigmap.contigs):
python scripts/run_inference.py \
  inference.output_prefix=pilot_zn_scaffold/design \
  inference.ckpt_override_path=models/ActiveSite_ckpt.pt \
  'contigmap.contigs=[30-40/A63-63/20-30/A71-71/20-30/A80-80/15-25/A83-83/30-40]' \
  inference.input_pdb=/home/mkroman/reference_structures/1SOS.pdb \
  inference.num_designs=10
```

Motif: His63, His71, His80, Asp83 (chain A of 1SOS.pdb), tetrahedral
His3Asp1 zinc coordination, verified directly against 1SOS's own
SITE/LINK records before use (bond lengths: His63 ND1–Zn 2.10 Å, His71
ND1–Zn 2.06 Å, His80 ND1–Zn 2.04 Å, Asp83 OD1–Zn 1.92 Å).

## RFdiffusion motif scaffolding — HCAR1 pocket

**[CORRECTED — pulled directly from `design_0.trb` and `design_5.trb`'s
`config.contigmap.contigs` field on 2026-08-15, both agree.]**

```bash
# CORRECTED (slash-delimited — this is what was actually run to produce
# pilot_hcar1_pocket/design_0..9.pdb, confirmed via .trb config.contigmap.contigs):
python scripts/run_inference.py \
  inference.output_prefix=pilot_hcar1_pocket/design \
  inference.ckpt_override_path=models/ActiveSite_ckpt.pt \
  'contigmap.contigs=[25-35/A71-71/15-25/A75-75/15-25/A95-95/15-25/A99-99/15-25/A268-268/25-35]' \
  inference.input_pdb=/home/mkroman/reference_structures/hcar1/9IZD_chainA_HCAR1.pdb \
  inference.num_designs=10
```

Motif: Arg71, Tyr75, Leu95, Arg99, Tyr268 (chain A of
`9IZD_chainA_HCAR1.pdb`, cleaned from PDB 9IZD), independently
re-verified via direct `awk`/`grep` against the PDB file after an initial
transcription error was caught (TYR95 was mis-relayed in a summary line;
the real motif — TYR75 + LEU95 as two separate residues — was confirmed
correct in the actual `.trb`/contig data).

## RFdiffusion motif scaffolding — disulfide control pilot (Cys57–Cys146)

Pulled the same way, from `pilot_disulfide_control/design_0.trb`'s
`config.contigmap.contigs` field, for completeness alongside the other
two (this third pilot was run and completed after the SOD1/HCAR1 pilots
documented above — see `results/disulfide_control_pilot_summary.md`):

```bash
python scripts/run_inference.py \
  inference.output_prefix=pilot_disulfide_control/design \
  inference.ckpt_override_path=models/ActiveSite_ckpt.pt \
  'contigmap.contigs=[30-50/A57-57/40-60/A146-146/30-50]' \
  inference.input_pdb=/home/mkroman/reference_structures/1SOS.pdb \
  inference.num_designs=10
```

## ProteinMPNN sequence design

```bash
conda create -n proteinmpnn python=3.10 -y
conda activate proteinmpnn
git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN
pip install torch numpy
```

Final torch in this env: 2.3.1+cu121 (separate from the `rfdiffusion` env's
2.1.0+cu121 pin — kept isolated deliberately).

Fixed positions were built **per-backbone** from each design's own `.trb`
file (`con_hal_pdb_idx` field) — not a shared/hardcoded position list,
since hallucinated motif positions differ per backbone. 8 sequences per
backbone (80 total per pilot). Verified 0/80 sequence-identity violations
at the fixed motif positions in both pilots before proceeding to folding.

## AF2 self-consistency (local ColabFold)

Hard local constraint: `--num-recycle 0` only. Any recycling (confirmed
even at `--num-recycle 1`) segfaults on this WSL2/JAX/CUDA setup. Root
cause is JAX-specific — confirmed NOT to reproduce in the PyTorch-based
RFdiffusion/ProteinMPNN steps (5-design-in-one-process stability test
passed with 5/5 distinct MD5 hashes).

Sequences batched per-backbone into single ColabFold processes (never
switching models mid-process) to avoid the known cross-model-transition
segfault.

## Recycled refold verification (Google Colab, standard ColabFold notebook)

Used to rule out the `num_recycle=0` local constraint as a confound for
the pilot's negative result. Settings: `model_type=auto` (resolves to
`alphafold2_ptm` for monomers), `num_recycles=3`, `num_models=5`,
`msa_mode=mmseqs2_uniref_env`, `template_mode=none`, `pair_mode=unpaired_paired`.

Run on `design_3_seq3` (SOD1 Zn pilot's best candidate). Result: pLDDT
improved from the recycle=0 baseline (85.35) to 85–88 across all 5 models;
motif geometry (Kabsch-aligned, 4-point) tightened only modestly (max
deviation 2.102 Å → 1.747 Å) — did not close the gap to the 0.5 Å
tolerance. Full per-residue deviations: His63 1.256 Å, His71 0.526 Å,
His80 0.580 Å, Asp83 1.747 Å (worst offender).
