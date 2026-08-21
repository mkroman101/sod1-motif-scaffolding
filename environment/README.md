# Environment Documentation

**Source of truth: `rfdiffusion_env_export.yml` and
`proteinmpnn_env_export.yml` in this directory are the real, literal
output of `conda env export` run directly on the research machine
(2026-08-15). The narrative notes below were transcribed from
conversation during the project and are kept for readability/context, but
where they disagree with the `.yml` files, trust the `.yml` files.**

**⚠️ Known discrepancy, flagged rather than silently resolved:** the
narrative note below states the `rfdiffusion` env's torch was "explicitly
pinned" to `2.1.0+cu121`. The real `rfdiffusion_env_export.yml` captured
on 2026-08-15 shows **torch 2.8.0** (paired with `cu128`-series NVIDIA
packages, e.g. `nvidia-cublas-cu12==12.8.4.1`), not 2.1.0+cu121. This
could mean the pin was later intentionally upgraded, or a subsequent
`pip install` re-resolved torch past the original pin (the exact failure
mode described in troubleshooting-log entry #5). No conversation record
explains the change, so this is left as an open discrepancy rather than
guessed at — check `rfdiffusion_env_export.yml` for the ground truth of
what's actually installed, and treat the "2.1.0+cu121" figure elsewhere
in this archive (including `scripts/pipeline_commands.md`) as the
version documented *at the time the pilots were run*, not necessarily
the version in the environment today. The `proteinmpnn` env's export
matches its documented pin (`torch==2.3.1+cu121`) exactly — no
discrepancy there.

## Hardware
RTX 3070 (8GB VRAM), Windows 11, WSL2/Ubuntu. GPU passthrough confirmed
working (`torch.cuda.is_available() == True`, correctly identifies
"NVIDIA GeForce RTX 3070").

## `rfdiffusion` conda environment
- Python: 3.9 (final — built from `env/SE3nv.yml`, not the original 3.10
  `conda create` target)
- torch: 2.1.0+cu121 (explicitly pinned — the default `pip install`
  resolution grabbed torch 2.13.0+cu130, which is incompatible with DGL;
  see troubleshooting log)
- DGL: installed matching cu121
- se3-transformer: 1.0.0, installed via `pip install .` from
  `env/SE3Transformer/` (bundled in the RFdiffusion repo, not a standalone
  clone — the standalone `NVIDIA/SE3Transformer` GitHub repo triggered an
  unexpected auth prompt and was abandoned in favor of the bundled copy)
- Additional runtime deps installed on top of `SE3nv.yml`: `opt_einsum`,
  `e3nn`, `omegaconf`, `hydra-core`, `numpy<2`, `torchdata<0.8`
- RFdiffusion: 1.1.0, `pip install -e . --no-deps`
- Checkpoint used: `ActiveSite_ckpt.pt` (of 7 downloaded, 3.2 GB total via
  `scripts/download_models.sh`)

## `proteinmpnn` conda environment
- Separate from `rfdiffusion` — deliberate isolation
- torch: 2.3.1+cu121
- Lighter dependency footprint than RFdiffusion (no DGL/SE3-Transformer
  requirement)

## ColabFold (local)
- LocalColabFold 1.6.2
- MSA server timeout patched from 6.02s to 60s (fixes silent failures)
- Must run from native Linux filesystem, not a Windows-mounted path

## Known WSL2-specific issues (confirmed, not assumed)
1. `nvidia-smi` inside WSL2 does not reliably attribute per-process VRAM
   usage — will show "No running processes found" even during active,
   confirmed GPU compute. Cross-check with `torch.cuda.is_available()` /
   `torch.cuda.max_memory_allocated()` from inside the actual process
   instead, or monitor via Windows Task Manager's GPU tab.
2. ColabFold (`colabfold_batch`) segfaults reliably when running >1 model
   in a single process, or with `--num-recycle` ≥ 1 (confirmed even at
   exactly 1). Root cause appears to be JAX/CUDA-specific to this WSL2
   driver-passthrough combination — matches an open, unresolved upstream
   GitHub issue.
3. This JAX-specific instability was explicitly tested and does NOT
   reproduce in RFdiffusion/ProteinMPNN (PyTorch-based) — multi-design
   batches in a single process are stable (verified: 5/5 unique outputs,
   no crash).

## `rfdiffusion3` conda environment (added 2026-08-16)
- Python 3.12, installed **locally** (RTX 3070) — despite the assumption
  that all three new tools would need rented cloud compute, real
  measurement showed RFdiffusion3 fits comfortably in 8GB (see below), so
  no cloud instance was used for this one.
- Real repo: [RosettaCommons/foundry](https://github.com/RosettaCommons/foundry),
  RFdiffusion3 (`rfd3`) lives at `models/rfd3` — **not** a standalone repo;
  the old `RosettaCommons/RFdiffusion` repo (this project's `rfdiffusion`
  env) has no RFdiffusion3 content, confirmed by direct README check.
- Install: `pip install "rc-foundry[rfd3]"` — pulled torch 2.13.0+cu130
  cleanly, CUDA detected correctly on the 3070 (`torch.cuda.is_available()
  == True`), no manual torch pin needed this time (unlike RFdiffusion1).
- Checkpoint: `rfd3_latest.ckpt`, 2.7 GB, via `foundry install rfd3`.
- New dependency issue (see troubleshooting log #12): RFdiffusion3 JIT-compiles
  Triton kernels at runtime, which needs a C compiler. This WSL2 install has
  no system `gcc`. Fixed via `conda install -c conda-forge gcc gxx` into the
  env — no sudo/apt needed.
- **Real measured VRAM/timing** (smoke test + Phase-3 timing runs, via
  `torch.cuda.max_memory_allocated()`, not nvidia-smi):
  - 50aa, unconditional, n=1: 45.7s wall, 1.69 GiB peak
  - 150aa (project target scale), n=1: 51.9s wall, 4.66 GiB peak
  - 150aa, batch of 4 in one job: 74.0s wall total, peak VRAM **unchanged**
    at 4.66 GiB — batching adds ~7.2s/design marginal cost at essentially
    no VRAM cost. Recommend batching for the real n=10 run.

## `ligandmpnn` conda environment (added 2026-08-16)
- Python 3.11, installed **locally** (RTX 3070) — also well within the 8GB
  budget, no cloud needed.
- Real repo: [dauparas/LigandMPNN](https://github.com/dauparas/LigandMPNN)
  (Justas Dauparas, ProteinMPNN's original author), confirmed via IPD's
  "Introducing LigandMPNN" announcement post.
- Install: pinned `requirements.txt` (torch==2.2.1+cu121). Two new
  dependency issues (troubleshooting log #13, #14): ProDy has a C
  extension (same gcc fix as above), and ProDy 2.4.1 imports the now-removed
  `pkg_resources` from modern setuptools — fixed with `pip install
  "setuptools<81"`.
- Weights: all model variants via `bash get_model_params.sh`, 118 MB total
  (tiny compared to the diffusion models).
- **Verified genuinely metal-aware, not just fixing positions**: run on
  the completed RFdiffusion1 SOD1 Zn pilot backbone
  (`RFdiffusion/pilot_zn_scaffold/design_3.pdb`), with a Zn ion
  Kabsch-transplanted into the backbone's coordinate frame from 1SOS
  (reusing `scripts/motif_geom.py`'s alignment method, ~0.6 Å residual —
  a smoke-test approximation, not a final placement). Log confirms
  `The number of ligand atoms parsed is equal to: 1, Type: ZN`; output
  reports a distinct `ligand_confidence` separate from `overall_confidence`,
  and a control run with `--ligand_mpnn_use_atom_context 0` on the
  identical input changes `ligand_confidence` (0.6034 → 0.4874),
  confirming the ligand-aware pathway is actually engaged. Fixed motif
  identities (His/His/His/Asp) preserved correctly.
- **Real measured VRAM/timing**: 8 sequences on the ~143-residue pilot
  backbone: 5.5s wall, 0.26 GiB peak. Trivially cheap.

## `openfold3preview` environment (added 2026-08-16) — rented, RunPod A100
- The only one of the three new tools that genuinely needed rented
  compute: official docs state a 32GB GPU memory minimum (tested on A100
  40GB), beyond the local 8GB budget. Installed via plain `pip` (no conda)
  into a venv on a user-provisioned RunPod pod (A100 SXM4 80GB), Python
  3.12, at `/workspace/openfold3/venv` (kept off the pod's small ~30GB
  root disk).
- Real repo: [aqlaboratory/openfold-3](https://github.com/aqlaboratory/openfold-3)
  (AlQuraishi Lab / OpenFold consortium), confirmed via the consortium's
  press release and HuggingFace org page.
- Install: `pip install openfold3` (0.4.5), then `setup_openfold
  --non-interactive` for weights (checkpoint `of3-p2-155k.pt`, 2.29 GB) and
  the Biotite CCD component dictionary (63 MB).
- New dependency/operational issues (troubleshooting log #15, #16):
  wrapping the CLI in a custom `runpy`-based instrumentation script broke
  PyTorch DataLoader's multiprocessing worker bootstrap (the CLI's own
  entry-point script has the required `if __name__ == "__main__":` guard;
  a `runpy.run_path` wrapper does not), causing the entire pipeline to
  silently re-execute recursively rather than crash cleanly — visible only
  as duplicated MSA-submission logs. Fixed by dropping the in-process
  wrapper and using the plain CLI + external `nvidia-smi` polling instead.
  Also: a long `pip install` and a `setup_openfold` weight download both
  need to run inside `tmux` on the pod — a dropped SSH connection killed
  one attempt mid-install (the install had actually completed already by
  the time the connection dropped).
- **`nvidia-smi` is reliable here** — unlike the WSL2 finding in
  troubleshooting log #11, this is a genuine Linux cloud instance;
  `nvidia-smi` correctly showed 0 MiB at idle and tracked real usage
  during compute. Confirmed by polling `nvidia-smi --query-gpu=memory.used`
  every 1s throughout each run.
- **Real measured VRAM/timing** — the standout finding: **peak VRAM for a
  single ~154-residue monomer fold was only ~3.7 GiB**, dramatically below
  the documented 32GB minimum (that guidance is presumably calibrated for
  larger/multimeric targets, not this project's small-monomer use case).
  Per-job wall time is dominated by **fixed startup overhead (~6.5–6.9
  min: env init, checkpoint load, MSA/template preprocessing)**, not by
  the actual diffusion sampling:
  - 1 query, 1 sample: 6m44.9s total (only 15s of which was the actual
    diffusion step)
  - 1 query, 5 samples: 6m55.5s total (23s diffusion step) — extra
    samples cost only ~2.7s each
  - 3 queries batched into 1 job, 1 sample each: 6m53.0s total — ~13s
    marginal cost per additional query (from the DataLoader's own
    per-query progress timing)
  - **Implication for the real 160-sequence validation run: batch all
    queries into one (or a few) `run_openfold` job(s).** Unbatched
    (160 separate jobs) would cost an estimated ~18 hours; batched, an
    estimated ~1.2 hours. This is the single most important operational
    finding from this handoff for cost control.

## Status (updated 2026-08-20)
All tool installation is complete, and the experiments this environment
was built for have since been run: the n=10 RFdiffusion3-vs-RFdiffusion1
comparison (`results/sod1_zn_pilot_rfdiffusion3_summary.md`) and the
same-validator cross-check (Experiment 2,
`results/sod1_zn_rfdiffusion1_openfold3preview_crosscheck.md`), both
using this OpenFold3-preview setup. See `paper/manuscript_final.docx`
for the current manuscript. Remaining future work (AME-benchmark
calibration subset, conditioning-ablation experiment) is described in
the manuscript's Discussion (Sections 4.2) rather than tracked here.

## Real environment exports

- `rfdiffusion_env_export.yml` — full `conda env export` output, `rfdiffusion` env, captured 2026-08-15
- `proteinmpnn_env_export.yml` — full `conda env export` output, `proteinmpnn` env, captured 2026-08-15
- `rfdiffusion3_env_export.yml` — full `conda env export` output, `rfdiffusion3` env, captured 2026-08-16
- `ligandmpnn_env_export.yml` — full `conda env export` output, `ligandmpnn` env, captured 2026-08-16
- `openfold3preview_pip_freeze.txt` — full `pip freeze` output from the RunPod pod's venv, captured 2026-08-16 (no conda used for this one — plain venv on the rented instance)

All were generated by activating each env directly on the machine it runs
on and exporting with no edits. `pip`-installed packages (34 in
`rfdiffusion`, 23 in `proteinmpnn`) are listed inside each yml's own
`pip:` block — conda flagged both exports with its standard
`CondaExportWarning` that these can't be conda-locked, which is expected
and does not affect reproducibility from the yml as long as the same pip
package/version list is honored.
