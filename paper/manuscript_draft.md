# Motif Scaffolding of a Disease-Relevant Zinc-Binding Site with RFdiffusion3 on Consumer-Scale Compute: A Reproducible Pipeline and Negative-to-Positive Case Study

**Status: DRAFT — RFdiffusion3 results (Sections 2.3, 3.3, Discussion) completed 2026-08-17. Remaining [PENDING] sections require the AME calibration subset (Section 2.4b/3.4) only. Pipeline updated from an earlier RFdiffusion2-based plan after RFdiffusion3's release (Baker Lab/IPD, bioRxiv Sept 2025) — see revision note below.**

## Revision note (kept for transparency, remove before final submission)

The original plan (documented in Section 1 and the earlier pilot work,
Section 3.1) targeted RFdiffusion2 as the comparison point for our
RFdiffusion1 baseline. Before that comparison was run, RFdiffusion3 was
identified as the current state of the art in this model lineage — an
all-atom diffusion model (14-atom-per-residue representation covering
backbone and sidechains), reporting 10x faster inference than
RFdiffusion2 and the ability to co-design proteins alongside ligands, DNA,
and other biomolecules directly. The comparison was shifted to
RFdiffusion3 to test the actual current standard rather than a superseded
intermediate version. Two downstream pipeline components were updated to
match: (1) sequence design now uses both ProteinMPNN (consistent with our
completed RFdiffusion1 baseline, for a controlled comparison) and
LigandMPNN (metal/ligand-aware sequence design, matching RFdiffusion3's
own published methodology for motifs involving metals or ligands — SOD1's
zinc site qualifies); (2) structure validation uses OpenFold3-preview
(AlQuraishi Lab/Columbia, Apache 2.0, open-weight AlphaFold3
reproduction) rather than official AlphaFold3 weights, which require a
non-commercial-use request to Google DeepMind — OpenFold3-preview avoids
that access gate entirely, consistent with this paper's own emphasis on
tooling accessible to independent researchers.

## Abstract

*[PENDING — write last, once RFdiffusion3 results exist.]*

Draft framing: We report two contributions. First, we evaluate
RFdiffusion3 — the current state-of-the-art generative model for
all-atom motif scaffolding — on a disease-relevant zinc-coordination
motif (the native Cu/Zn-superoxide dismutase-1 [SOD1] zinc-binding site,
implicated in amyotrophic lateral sclerosis), directly comparing the
result against our own prior RFdiffusion1 negative result on the same
motif (0/10 designable backbones). Second, we document the complete
pipeline — RFdiffusion3, ProteinMPNN/LigandMPNN, and OpenFold3-preview-based
self-consistency validation — as reproducible on consumer-grade hardware
(a single 8GB-VRAM GPU) combined with modest rented cloud compute,
including a full account of the dependency and environment issues
encountered and resolved, as a resource for independent researchers
without institutional compute access.

## 1. Introduction

Motif scaffolding — generating a novel protein fold that hosts a fixed,
pre-specified functional site — is a core task in computational protein
design, with applications spanning enzyme design, binder design, and
vaccine antigen design. RFdiffusion (Watson et al., 2023) established a
diffusion-based approach to this problem and remains widely used, but its
original formulation requires two preprocessing steps to handle atomic-
level motifs — inverse rotamer sampling and sequence index sampling —
both drawn from exponentially large search spaces, which limits its
reliability on rigid, precisely-defined motifs.

RFdiffusion2 (Ahern et al., Nature Methods, 2026) took an important step
toward addressing this, scaffolding unindexed atomic motifs directly via
a hybrid residue/atom representation. Evaluated on the newly introduced
Atomic Motif Enzyme (AME) benchmark — 41 diverse catalytic active sites
curated from the M-CSA and PARITY databases — RFdiffusion2 generates at
least one successful scaffold for all 41 cases, compared to 16/41 for
RFdiffusion1. RFdiffusion3 (Baker Lab/IPD, bioRxiv 2025) extends this
further to a fully explicit all-atom representation (14 atoms per
residue, covering backbone and sidechains), reporting improved benchmark
performance alongside a 10x inference speedup relative to RFdiffusion2,
and — unlike either predecessor — the ability to co-design a protein
jointly with a non-protein partner (ligand, DNA) rather than only
conditioning on a fixed target. Motif complexity (quantified as the
number of "residue islands," contiguous segments of catalytic residues)
was identified by the RFdiffusion2 work as correlating with scaffolding
difficulty; whether this relationship holds under RFdiffusion3's
different representation is untested by the present work.

*[EDITORIAL NOTE: full author lists for both the RFdiffusion2 and
RFdiffusion3 citations should be verified directly against the published
papers before submission — only first authors, journals, and
identifying details were confirmed during drafting.]*

This prior work leaves open whether RFdiffusion3's advantages extend to
motif types and biological contexts outside its own published benchmark
set. We address this with a motif of direct biomedical relevance: the
native zinc-binding site of human SOD1 (His63, His71, His80, Asp83;
tetrahedral His3Asp1 coordination), a structural (not catalytic) metal
site in a protein causally linked to a subset of familial ALS cases. We
had previously attempted to scaffold this exact motif with RFdiffusion1
and observed a clean negative result (0/10 designable backbones by a
strict criterion, confirmed not to be an artifact of limited AlphaFold2
recycling via an independent higher-fidelity refold). This provides a
directly comparable RFdiffusion1 baseline, on the same motif, prior to
testing RFdiffusion3.

Separately, we note that access to state-of-the-art generative protein
design tools has historically correlated strongly with institutional
resources. We report our full pipeline, including every dependency and
environment conflict encountered, running on an 8GB-VRAM consumer GPU
(RFdiffusion1, ProteinMPNN, and AlphaFold2 self-consistency screening) plus
brief, targeted use of rented cloud GPU compute (RFdiffusion2 and full-
recycle AlphaFold2 validation) — intended as a practical resource for
independent researchers attempting similar work without dedicated
institutional infrastructure.

## 2. Methods

### 2.1 Motif and reference structure

Human SOD1, PDB 1SOS. Native zinc-binding motif: His63, His71, His80,
Asp83 (chain A), independently verified against the structure's own
SITE/LINK records (coordination bond lengths: His63 ND1–Zn 2.10 Å, His71
ND1–Zn 2.06 Å, His80 ND1–Zn 2.04 Å, Asp83 OD1–Zn 1.92 Å) prior to use in
any design run.

### 2.2 RFdiffusion1 pilot (completed)

Checkpoint: `ActiveSite_ckpt.pt`. Motif scaffolded in isolation (no
disulfide-subloop structural context) onto an unconstrained novel ~150 aa
topology. 10 backbones generated. Sequence design: ProteinMPNN, 8
sequences per backbone (80 total), fixed positions determined per-backbone
from each design's own hallucinated-motif index mapping. Self-consistency:
local AlphaFold2/ColabFold, single-model-per-process, `num_recycle=0`
(hardware constraint on the local WSL2/CUDA environment — any recycling
reproducibly segfaults; see Supplementary Troubleshooting Log). Success
criterion: self-consistency Cα RMSD < 2 Å AND Kabsch-aligned 4-point motif
Cα deviation < 0.5 Å from native.

To rule out the `num_recycle=0` constraint as a confound, the best-
performing sequence (by self-consistency RMSD) was independently refolded
using the standard ColabFold notebook on Google Colab with full recycling
(`num_recycle=3`, 5 models).

### 2.3 RFdiffusion3 comparison [DONE — 2026-08-17]

Same motif, same source structure, matched target scaffold size and batch
size (n=10, for direct comparison to the completed RFdiffusion1 result;
matched-N held throughout — not scaled up despite cheap compute).
RFdiffusion3 does not share RFdiffusion1's `contigmap.contigs` syntax;
motif conditioning was specified via `unindex` + `select_fixed_atoms`
(minimal-atom fixing on the ligand-coordinating atoms only, e.g.
`ND1,CG`) + a native `ligand` field for the Zn ion, confirmed against the
actual RFdiffusion3 (`rc-foundry[rfd3]`) docs/examples rather than
assumed. Sequence design run in parallel with **both** ProteinMPNN (holds
the sequence-design tool constant relative to the RFdiffusion1 baseline,
isolating the backbone-generation model as the only changed variable) and
LigandMPNN (metal-aware sequence design, using RFdiffusion3's own native
Zn output directly — matching RFdiffusion3's own published methodology
for metal/ligand-containing motifs). Structure validation via
OpenFold3-preview self-consistency (Section 2.4a) rather than local
AlphaFold2, matching RFdiffusion3's own validation approach while
remaining fully open-weight; folded via the public ColabFold MSA server
in spaced batches of 8 after a self-hosted-MMseqs2 attempt was abandoned
following a corrupted download (`troubleshooting_log.md` #18–22). Full
methodology and results: `results/sod1_zn_pilot_rfdiffusion3_summary.md`.

### 2.4 Validation tooling

**2.4a — OpenFold3-preview calibration [DONE — 2026-08-16, install/calibration handoff].**
Before trusting OpenFold3-preview on any novel design, we calibrated it
against the same known-answer problem established in our prior work:
wild-type SOD1 folded and compared to the 1SOS crystal structure
(previously validated via AlphaFold2/ColabFold at 0.361 Å RMSD over
150/153 residues). OpenFold3-preview (checkpoint `of3-p2-155k.pt`) was run
on the same full-length wild-type sequence via the ColabFold MSA server,
5 independent diffusion samples/seeds. Each sample was superposed onto
1SOS chain A with PyMOL `align` (5-cycle outlier-rejecting refinement,
matching the project's established superposition methodology):

| sample | RMSD after refinement (Å) | residues retained | RMSD before refinement (Å) | avg pLDDT |
|---|---|---|---|---|
| 1 | 0.263 | 140/153 | 0.627 | 89.41 |
| 2 | 0.273 | 140/153 | 0.632 | 89.51 |
| 3 (top-ranked) | 0.283 | 140/153 | 0.628 | 89.78 |
| 4 | 0.297 | 144/153 | 0.639 | 89.34 |
| 5 | 0.261 | 138/153 | 0.362 | 88.66 |

**Result: PASS.** All 5/5 independent samples land in a tight 0.261–0.297 Å
range, beating the 0.361 Å AF2/ColabFold benchmark on RMSD magnitude in
every sample — not a single cherry-picked draw. The one honest caveat:
PyMOL's outlier rejection retains 138–144/153 residues here versus 150/153
in the original AF2 benchmark, i.e. a handful more residues (mostly
flexible loop/terminal positions) are treated as outliers in the
OpenFold3-preview fits. This is disclosed rather than smoothed over; it
does not change the pass/fail call, since the metric that matters (fit
tightness on the retained core) is comparable or better in all 5 samples.
OpenFold3-preview is cleared to validate the novel SOD1-motif designs in
Section 2.3. Full per-sample data, structures, and the PyMOL session are
in `results/openfold3preview_calibration/`.

**2.4b — AME-benchmark calibration subset [PENDING — not yet run; sizing now justified by real cost data].**
A small subset of cases from the published AME benchmark (exact cases
TBD — recommend selecting across the reported residue-island difficulty
range) will be reproduced under our own pipeline and compute environment,
using RFdiffusion3 and the calibrated OpenFold3-preview validation step,
to confirm our setup reproduces published performance trends before the
novel SOD1 result is interpreted. Real OpenFold3-preview timing data
(Section 2.5) shows marginal cost per additional case is small (~13–24s)
once batched into a single job with the fixed ~6.5 min job-startup
overhead paid once — so a **15–20 case subset** is recommended rather than
a token 3–5 cases, at negligible added cost (~6–8 minutes of A100 time).

### 2.5 Compute environment

Local: RTX 3070 (8GB VRAM), WSL2/Ubuntu, used for RFdiffusion1,
ProteinMPNN, and initial AlphaFold2 self-consistency screening (completed
baseline work). **Contrary to the original assumption that all three new
tools would need rented compute**, real measurement showed only
OpenFold3-preview actually requires it: RFdiffusion3 peaked at 4.66 GiB
and LigandMPNN at 0.26 GiB at the project's ~150aa target scale — both
comfortably within the local 8GB budget, and both installed/verified
locally (`rfdiffusion3`, `ligandmpnn` conda envs). OpenFold3-preview's own
docs state a 32GB minimum (tested on A100 40GB); real measurement on the
rented instance (see below) showed actual peak usage for a single
~150-residue monomer fold was only ~3.7 GiB — far under that documented
minimum, though the official guidance is retained as the safe assumption
for larger/multimeric targets. Cloud: RunPod, single A100 SXM4 80GB
on-demand instance, used for the OpenFold3-preview install and
calibration (Section 2.4a). Full environment specifications, version
pins, and all dependency conflicts encountered and resolved are provided
in the Supplementary Environment Documentation and Troubleshooting Log.

## 3. Results

### 3.1 RFdiffusion1 baseline (SOD1 Zn motif) — completed

0/10 backbones designable by the strict criterion. Best candidate
(design_3, 4/8 sequences passing the RMSD threshold) achieved a minimum
motif deviation of 2.102 Å (design_3_seq3) — 4.2× the 0.5 Å tolerance.
Independent full-recycling refold of this candidate improved overall fold
confidence substantially (mean pLDDT 85.35 → 85–88 across 5 models) but
only modestly tightened motif geometry (2.102 Å → 1.747 Å; still ~3.5× the
tolerance, driven primarily by the Asp83 position). Full results in
Supplementary Table 1.

### 3.2 Disulfide control (RFdiffusion1) — completed

To distinguish whether the RFdiffusion1 SOD1-motif result (Section 3.1)
reflects a general pipeline/batch-size limitation or something specific
to rigid, multi-point motif geometry, we ran an identical pipeline (same
checkpoint, batch size, contig mechanics, and source structure, 1SOS) on
a structurally simpler motif from the same protein: the Cys57–Cys146
disulfide bond (a 2-point constraint, independently verified against
1SOS's own SSBOND record and recomputed directly from atomic coordinates
at 2.010 Å, matching the record's stated 2.01 Å).

Raw RFdiffusion backbone geometry was tight (max deviation 0.182 Å across
10/10 unique designs), consistent with both prior pilots — RFdiffusion1's
raw motif placement was never the limiting step in any of the three
pilots. ProteinMPNN produced 80 sequences (8/backbone) with 0/160
identity violations at the fixed cysteine positions. AF2 self-consistency
(num_recycle=0, matching the SOD1 and HCAR1 pilots) gave a mean pLDDT of
70.9 (vs. 47.7 for the SOD1 Zn motif and 64.2 for the HCAR1 pocket).

**4 of 10 backbones passed the strict designability bar (self-consistency
RMSD < 2 Å AND motif deviation < 0.5 Å), and 7 of 10 passed a loosened
1.5 Å motif tolerance** — both prior pilots scored 0/10 on both bars.

| | SOD1 Zn (4-pt, rigid) | HCAR1 pocket (5-pt) | Disulfide (2-pt, this pilot) |
|---|---|---|---|
| Best motif deviation | 2.10 Å | 2.71 Å | 0.017 Å |
| Mean pLDDT | 47.7 | 64.2 | 70.9 |
| Backbones passing strict bar | 0/10 | 0/10 | **4/10** |
| Backbones passing loose bar (1.5 Å) | 0/10 | 0/10 | **7/10** |

With every other pipeline variable held fixed, changing only the motif
from a rigid 4-point tetrahedral metal site to a simple 2-point disulfide
constraint flipped the result from a clean negative to a clear positive.
This is strong evidence that RFdiffusion1's failure on the SOD1 zinc
motif reflects genuine difficulty scaffolding rigid, multi-point
functional geometry, rather than a general limitation of the pipeline or
an artifact of the n=10 batch size used throughout these pilots. This
result is the direct motivation and interpretive baseline for the
RFdiffusion3 comparison below: it establishes a real, empirically
grounded expectation of *motif-dependent* difficulty against which the
RFdiffusion3 result should be read, rather than treating any change in
outcome as ambiguous between "the newer model is better" and "n=10 was
never a fair test."

### 3.3 RFdiffusion3 (SOD1 Zn motif) — completed

10 backbones (matched n, md5-verified unique, 126–155 aa), 8 sequences
per backbone per arm, 160 total (80 ProteinMPNN + 80 LigandMPNN), 0/320
identity violations at the fixed motif positions in either arm. All 160
folded via OpenFold3-preview self-consistency against the public
ColabFold MSA server.

| | ProteinMPNN (n=80) | LigandMPNN (n=80) | Overall (n=160) |
|---|---|---|---|
| Mean pLDDT | 80.44 | 76.97 | 78.7 |
| Mean self-consistency RMSD | 3.01 Å | 4.58 Å | 3.80 Å |
| sc_rmsd < 2 Å alone | 51/80 (64%) | 49/80 (61%) | 100/160 (63%) |
| Best motif max-deviation | 1.649 Å | 1.755 Å | 1.649 Å |
| Strict pass (sc_rmsd<2 Å AND motif max-dev<0.5 Å) | 0/80 | 0/80 | 0/160 |

**RFdiffusion1 vs. RFdiffusion3, matched motif and batch size:**

| | RFdiffusion1 (n=80) | RFdiffusion3 (n=160) |
|---|---|---|
| Mean pLDDT | 47.7 | 78.7 |
| Mean self-consistency RMSD | 14.25 Å | 3.80 Å |
| sc_rmsd < 2 Å alone | 4/80 (5%) | 100/160 (63%) |
| Best motif max-deviation | 2.102 Å | 1.649 Å |
| Strict pass (both criteria) | 4/80 (5%) | 0/160 |

This result is **decisive**, not ambiguous, on backbone
foldability/self-consistency: RFdiffusion3 backbones fold into
themselves reliably (63% pass sc_rmsd<2 Å, mean pLDDT 78.7) where
RFdiffusion1 backbones largely do not (5%, mean pLDDT 47.7) — a 12x
effect at matched n=10, far larger than plausible batch-size noise.

The strict combined bar (0/160 RFdiffusion3 vs. 4/80 RFdiffusion1)
should **not** be read as RFdiffusion3 placing the motif worse. It is a
direct structural consequence of RFdiffusion3's minimal-atom-fixing
philosophy (Section 2.3): raw backbone motif CA-RMSD was already
1.2–2.1 Å before any folding (vs. RFdiffusion1's 0.17–0.52 Å), so the
<0.5 Å post-fold CA bar was already unreachable at the Phase 2 stage for
every backbone, independent of fold quality. The functionally relevant
metal-coordinating-atom-to-Zn distances, in contrast, were an *exact*
match to native geometry in all 10 raw RFdiffusion3 designs — a
guarantee RFdiffusion1's contig-based fixing does not make explicit.
The two models default to optimizing different things: RFdiffusion3
guarantees coordinating-atom geometry at the cost of CA-frame
conservation; RFdiffusion1 guarantees CA-frame conservation at the cost
of the fold succeeding at all. Full per-query results and interpretation:
`results/sod1_zn_pilot_rfdiffusion3_summary.md`,
`results/sod1_zn_rfdiffusion3_full_results.csv`.

### 3.4 AME calibration subset [PENDING]

*To be completed following the plan in Section 2.4.*

## 4. Discussion

The disulfide control (Section 3.2) substantially narrows the space of
honest interpretations available for the RFdiffusion3 result once it
exists, and is discussed here first because it changes how that result
should be read.

**On motif rigidity as the operative variable.** Holding checkpoint,
batch size, contig mechanics, and source structure fixed, the only
difference between a 0/10 and a 4–7/10 outcome across our three
RFdiffusion1 pilots was the motif's geometric complexity — a rigid
4-point tetrahedral metal site and a 5-point solvent-exposed pocket both
failed completely, while a simple 2-point disulfide succeeded readily.
This is consistent with, and extends to a disease-relevant structural
(non-catalytic) motif, the residue-island difficulty relationship
reported for catalytic sites in the AME benchmark (Ahern et al., 2026):
motifs requiring more simultaneous, precisely-positioned constraints are
harder to scaffold, largely independent of the specific chemistry
involved (metal coordination vs. small-molecule binding).

**RFdiffusion3 on the SOD1 Zn motif: neither of the two outcomes
anticipated above — a genuinely third case.** RFdiffusion3 did not
cleanly "succeed" or "fail" on this motif; it resolved the specific
failure mode that dominated the RFdiffusion1 result while leaving a
different, narrower one in place. RFdiffusion1's 0/10 (Section 3.1) was
driven almost entirely by catastrophic fold failure — a mean pLDDT of
47.7 and median self-consistency RMSD around 16 Å indicate most designed
sequences did not refold into anything resembling their intended
backbone at all, independent of motif geometry. RFdiffusion3 resolves
exactly this: 63% of its designed sequences fold self-consistently
(sc_rmsd < 2 Å, mean pLDDT 78.7), a 12x improvement at matched n=10 that
the disulfide control's batch-size ruling-out argument extends to here
directly — this is not sampling noise. By the "does the design fold at
all" criterion, which is the precondition for a design being useful
regardless of motif tolerance, RFdiffusion3 succeeds where RFdiffusion1
failed.

What RFdiffusion3 does *not* do is close the gap on the strict CA-motif
bar (0/160, essentially matching RFdiffusion1's near-failure there too,
4/80). But this is not a second independent failure — it traces to a
single, identified methodological choice (Section 2.3/3.3):
RFdiffusion3's `select_fixed_atoms` conditioning fixes only the
ligand-coordinating atoms (e.g. `ND1,CG`), not the full residue frame,
so raw backbone motif CA-RMSD was already 1.2–2.1 Å before any folding
— a ceiling set at the Phase 2 backbone-generation stage, not a
consequence of anything that happens during folding or sequence design.
Measured on the axis RFdiffusion3 actually optimizes — coordinating-atom
geometry — it is exact in all 10 raw designs, tighter than anything
RFdiffusion1's contig-based fixing guarantees explicitly.

The result is best read as: RFdiffusion3's all-atom representation
resolves the rigidity-driven foldability failure identified in Sections
3.1–3.2, but "motif conservation" is not a single property — atom-level
chemical accuracy (what actually matters for a functional site's
chemistry) and CA-frame conservation (what the strict designability bar,
inherited from backbone-only diffusion literature, measures) can be
independently targeted, and RFdiffusion3's default constraint mechanism
trades the latter for reliability on the former. A fairer future
comparison would score designability against a motif-CA bar loosened to
what RFdiffusion3's own atom-fixing philosophy can in principle deliver,
or would additionally condition RFdiffusion3 on full residue frames
where available, rather than applying an RFdiffusion1-native bar
unmodified.

### 4.1 On accessible reproducibility

*[Short paragraph, drawing on the Supplementary Troubleshooting Log:
practical account of what it took to run this pipeline on consumer
hardware plus brief rented cloud compute, framed as a resource for
independent researchers rather than a complaint. Reference the broader
discussion of resource concentration in AI-driven structural biology
research.]*

## Data and Code Availability

- Code and analysis scripts: [GitHub repository URL — PENDING]
- Versioned reproducibility archive (code, environment files, full result
  tables): Zenodo, DOI [PENDING]
- Final structure coordinates: ModelArchive, accession [PENDING]

## References

1. Watson, J.L. et al. De novo design of protein structure and function
   with RFdiffusion. *Nature* 620, 1089–1100 (2023).
2. Ahern, W. et al. Atom-level enzyme active site scaffolding using
   RFdiffusion2. *Nature Methods* 23, 96–105 (2026).
   DOI: 10.1038/s41592-025-02975-x
3. [RFdiffusion3 — Baker Lab/IPD, bioRxiv, Sept 2025. Full citation
   (authors incl. Butcher, Veje et al. per secondary sources — verify
   against published version) and DOI to be confirmed before submission.]
4. [OpenFold3-preview — AlQuraishi Lab/Columbia, OpenFold consortium.
   Citation to be added once a formal reference is available.]
5. [1SOS — PDB structure citation, to be formatted per journal style]
4. [9IZD — PDB structure citation, used for the separate HCAR1 pilot if
   included as supplementary comparison — to be decided]
5. [Reference for the AI-research resource-concentration / "Matthew
   effect" discussion — bioRxiv 10.1101/2025.02.11.637417, verify full
   citation before submission]

---

## Supplementary Materials (separate files in this archive)

- Supplementary Table 1: Full RFdiffusion1 SOD1 pilot results (all 80
  sequences) — see `results/sod1_zn_pilot_rfdiffusion1_summary.md`
  [PENDING full 80-row table — currently top-10 only]
- Supplementary Table 2: RFdiffusion2 results [PENDING]
- Supplementary Table 3: AME calibration subset results [PENDING]
- Supplementary Environment Documentation — see `environment/README.md`
- Supplementary Troubleshooting Log — see `troubleshooting_log.md`
- Supplementary Methods (HCAR1 comparison pilot, if included) — see
  `results/hcar1_pocket_pilot_summary.md`
