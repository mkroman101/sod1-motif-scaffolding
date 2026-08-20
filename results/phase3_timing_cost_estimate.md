# Phase 3 — Real Timing/VRAM Data and Compute Budget Estimate

**[VERIFIED] — 2026-08-16.** All figures below are real measurements from
this handoff (install/verify/calibrate for RFdiffusion3, LigandMPNN,
OpenFold3-preview), not vendor-quoted or estimated numbers, except where
explicitly marked "extrapolated."

## Real per-tool data, at the project's ~150aa target scale

### RFdiffusion3 — local, RTX 3070, $0
| run | wall clock | peak VRAM (`torch.cuda.max_memory_allocated`) |
|---|---|---|
| 50aa, unconditional, n=1 | 45.7s | 1.69 GiB |
| 150aa, unconditional, n=1 | 51.9s | 4.66 GiB |
| 150aa, unconditional, batch of 4 in one job | 74.0s total | 4.66 GiB (unchanged from n=1) |

Marginal cost per design once batched: ~7.2s, at essentially no extra
VRAM. Extrapolated (not measured) to a batch of 10: ~117s (~2 min) total,
comfortably inside the 8GB budget.

### LigandMPNN — local, RTX 3070, $0
8 sequences on the real ~143-residue SOD1 Zn pilot backbone
(`design_3.pdb`): 5.5s wall, 0.26 GiB peak. For the full 80 LigandMPNN
sequences needed (10 backbones × 8 seqs), ~10 × 5.5s ≈ 55s total if run
one backbone at a time; likely less if batched further (not tested).

### OpenFold3-preview — RunPod A100 SXM4 80GB, real $ cost
Peak VRAM for a single ~154-residue monomer fold: **~3.7 GiB** (real
`nvidia-smi` polling — confirmed reliable on this genuine Linux instance,
unlike the WSL2 unreliability documented in troubleshooting log #11).
Dramatically below the official docs' 32GB minimum, which is presumably
calibrated for larger/multimeric targets.

Wall time is dominated by **fixed per-job startup overhead** (env init,
checkpoint load onto GPU, MSA-server round-trip, template preprocessing),
not by the diffusion sampling itself:

| run | total wall clock | of which diffusion sampling |
|---|---|---|
| 1 query, 1 diffusion sample | 6m44.9s | ~15s |
| 1 query, 5 diffusion samples | 6m55.5s | ~23s |
| 3 queries batched in 1 job, 1 sample each | 6m53.0s | ~40s (3×~13s) |

**This is the single most important cost-control finding from this
handoff: batch queries into as few `run_openfold` jobs as possible.**
Marginal cost per additional query within a batched job: ~13s at 1
sample, ~13s + ~2.7s/extra-sample beyond the first. Running queries
one-per-job instead of batched would cost roughly **27× more** in wall
time for the same workload.

## Full planned-experiment cost projection

Target workload (not yet run — this handoff is install/verify only):
n=10 RFdiffusion3 backbones, 8 sequences/backbone via both ProteinMPNN
and LigandMPNN (160 sequences total), OpenFold3-preview self-consistency
validation on all 160, plus a small AME-benchmark calibration subset.

| stage | estimate | basis |
|---|---|---|
| RFdiffusion3, 10 backbones | ~2 min, $0 | extrapolated from real batch-of-4 data, local |
| LigandMPNN, 80 sequences | ~1 min, $0 | real per-backbone data, local |
| ProteinMPNN, 80 sequences | not separately re-benchmarked this handoff | already-working env from prior project phase, known cheap |
| OpenFold3-preview, 160-sequence validation, batched, 5 samples/seq | ~70 min (~1.2 hr) | real fixed overhead (~6.9 min) + real marginal cost (~13s + 4×2.7s per query) × 159 |
| AME calibration subset, 15–20 cases, batched, 5 samples/case | ~6–8 min | same real marginal-cost figures |
| **Total estimated A100 compute** | **~1.3–1.5 hr** | |

**Recommended budget with realistic buffer** (mid-scale batch validation
before committing to one 160-query job, MSA-server variance across truly
distinct sequences rather than the identical-sequence test case used
here, output review time): **3–4 hours of A100 time.**

### Cost, current RunPod on-demand A100 pricing (checked 2026-08-15)
- Community Cloud: ~$1.39/hr → **$4.17–5.56** for 3–4 hr
- Secure Cloud: ~$2.19/hr → **$6.57–8.76** for 3–4 hr

**Total recommended compute budget for the full planned experiment:
under $10, likely $4–9, provided queries are batched as described above.**
This is far below what the same workload would cost run naively
one-job-per-query (~18 hours unbatched ≈ $25–40+).

### Caveats on this estimate
- The 3-query batching test used 3 copies of the *same* sequence; a real
  batch of 160 *distinct* designed sequences will each need their own
  unique MSA-server lookup. Single-sequence MSA fetches were observed to
  take only ~1–4s each in this handoff's calibration runs, so this is
  expected to be a minor effect, not a major one — but it hasn't been
  validated at full scale.
- Recommend a mid-scale validation batch (e.g. 20–30 queries) before
  committing to one very large batched job, consistent with this
  project's established "verify cheaply before scaling" discipline.
- RFdiffusion3's n=10 batching figure is extrapolated from a real n=4
  data point, not directly measured at n=10.
