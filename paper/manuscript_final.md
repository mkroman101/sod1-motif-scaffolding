Motif Scaffolding of a Disease-Relevant Zinc-Binding Site with RFdiffusion3 on Consumer-Scale Compute: A Reproducible Computational Pipeline and Case Study

## Abstract

Motif scaffolding (designing novel protein backbones that host a fixed functional site) remains difficult for rigid, multi-point motifs. Here, I evaluate RFdiffusion3, an all-atom generative model, on the native zinc-binding site of human Cu/Zn-superoxide dismutase-1 (SOD1; His63, His71, His80, Asp83). This is a structural, non-catalytic metal site in a protein causally linked to a subset of familial ALS cases. I demonstrate that RFdiffusion3 substantially improves de novo backbone self-consistency on this difficult SOD1 motif over an RFdiffusion1 baseline while trading strict Cα-frame conservation for precise atom-level motif conditioning. While 0/10 generated RFdiffusion1 backbones satisfy the strict backbone-level designability criterion (a failure confirmed not to be an artifact of limited recycling), RFdiffusion3 sequences generated via ProteinMPNN achieved a 64% (51/80) self-consistency success rate (RMSD < 2 Å), with a mean pLDDT of 80.44. None of the RFdiffusion3 designs satisfy the legacy combined criterion requiring both self-consistency and <0.5 Å motif Cα deviation, which is expected because RFdiffusion3 conditions ligand-coordinating atoms rather than full residue frames. Zn-coordination geometry was preserved under the atom-level conditioning in all 10 raw RFdiffusion3 backbones, though this reflects conditioned geometry rather than independently demonstrated emergent function. This study also documents the complete RFdiffusion3/ProteinMPNN/LigandMPNN/OpenFold3-preview pipeline operating entirely on an 8GB-VRAM consumer-scale GPU plus targeted cloud compute. No experimental folding, stability, metallation, or functional validation is performed in this study.

## 1. Introduction

Motif scaffolding (generating a novel protein fold that hosts a fixed, pre-specified functional site) is a core task in computational protein design, with applications spanning enzyme design, binder design, and vaccine antigen design. RFdiffusion (Watson et al., 2023) established a diffusion-based approach to this problem and remains widely used, but its original formulation requires two preprocessing steps to handle atomic-level motifs (inverse rotamer sampling and sequence index sampling), both drawn from exponentially large search spaces, which limits its reliability on rigid, precisely-defined motifs.
RFdiffusion2 (Ahern et al., Nature Methods, 2026) took an important step toward addressing this, scaffolding unindexed atomic motifs directly via a hybrid residue/atom representation. Evaluated on the newly introduced Atomic Motif Enzyme (AME) benchmark (41 diverse catalytic active sites curated from the M-CSA and PARITY databases), RFdiffusion2 generates at least one successful scaffold for all 41 cases, compared to 16/41 for RFdiffusion1. RFdiffusion3 (Butcher et al., bioRxiv 2025) extends this further to a fully explicit all-atom representation (14 atoms per residue, covering backbone and sidechains), reporting improved benchmark performance alongside a 10x inference speedup relative to RFdiffusion2, and, unlike either predecessor, the ability to co-design a protein jointly with a non-protein partner (ligand, DNA) rather than only conditioning on a fixed target. Motif complexity (quantified as the number of “residue islands,” contiguous segments of catalytic residues) was identified by the RFdiffusion2 work as correlating with scaffolding difficulty; whether this relationship holds under RFdiffusion3's different representation is untested by the present work.
This prior work leaves open whether RFdiffusion3's advantages extend to motif types and biological contexts outside its own published benchmark set. I address this with a motif of direct biomedical relevance: the native zinc-binding site of human SOD1 (His63, His71, His80, Asp83; tetrahedral His3Asp1 coordination), a structural (not catalytic) metal site in a protein causally linked to a subset of familial ALS cases. I had previously attempted to scaffold this exact motif with RFdiffusion1 and observed a clean negative result (0/10 designable backbones by a strict criterion, confirmed not to be an artifact of limited AlphaFold2 recycling via an independent higher-fidelity refold). This provides a directly comparable RFdiffusion1 baseline, on the same motif, prior to testing RFdiffusion3.
Separately, access to state-of-the-art generative protein design tools has historically correlated strongly with institutional resources. This paper reports the full pipeline, including every dependency and environment conflict encountered, running on an 8GB-VRAM consumer-scale GPU (RFdiffusion1, RFdiffusion3, ProteinMPNN, and LigandMPNN, plus initial AlphaFold2 self-consistency screening) plus brief, targeted use of rented cloud GPU compute (OpenFold3-preview validation only), intended as a practical resource for independent researchers attempting similar work without dedicated institutional infrastructure.

## 2. Methods


### 2.1 Motif and reference structure

Human SOD1, PDB 1SOS. Native zinc-binding motif: His63, His71, His80, Asp83 (chain A), independently verified against the structure's own SITE/LINK records (coordination bond lengths: His63 ND1–Zn 2.10 Å, His71 ND1–Zn 2.06 Å, His80 ND1–Zn 2.04 Å, Asp83 OD1–Zn 1.92 Å) prior to use in any design run.

### 2.2 RFdiffusion1 pilot

Checkpoint: ActiveSite_ckpt.pt. Motif scaffolded in isolation (no disulfide-subloop structural context) onto an unconstrained novel ~150 aa topology. 10 backbones generated. Sequence design: ProteinMPNN, 8 sequences per backbone (80 total), fixed positions determined per-backbone from each design's own hallucinated-motif index mapping.
Hardware Constraints & Recycling: Structure validation relied on local AlphaFold2/ColabFold, single-model-per-process, with num_recycle=0. This zero-recycling parameter is a strict hardware constraint on the local WSL2/CUDA environment, as any recycling reproducibly segfaults (see Supplementary Troubleshooting Log). Success criterion: self-consistency Cα RMSD < 2 Å AND Kabsch-aligned 4-point motif Cα deviation < 0.5 Å from native. To rule out the num_recycle=0 constraint as a confound, the best-performing sequence (by self-consistency RMSD) was independently refolded using the standard ColabFold notebook on Google Colab with full recycling (num_recycle=3, 5 models).

### 2.3 RFdiffusion3 comparison

The same motif, source structure, target scaffold scale, and number of generated backbones were used for RFdiffusion3 (n=10). RFdiffusion3 does not share RFdiffusion1's contigmap.contigs syntax; motif conditioning was specified via unindex + select_fixed_atoms (minimal-atom fixing on ligand-coordinating atoms only, e.g. ND1,CG) plus a native ligand field for the Zn ion, confirmed against the actual RFdiffusion3 (rc-foundry[rfd3]) documentation and examples. Sequence design was performed in parallel with ProteinMPNN and LigandMPNN. ProteinMPNN is the primary matched comparison because it holds the sequence-design tool constant relative to the RFdiffusion1 baseline; LigandMPNN is treated as a secondary, metal-aware sequence-design arm rather than pooled into the primary RFdiffusion1-versus-RFdiffusion3 comparison. Structure validation used OpenFold3-preview self-consistency, matching the RFdiffusion3 workflow, with the validator difference from the RFdiffusion1 baseline treated as a limitation; a same-validator cross-check addressing this limitation was subsequently run and is reported in Section 2.6 and Section 3.3. All RFdiffusion3 designs were folded via the public ColabFold MSA server in spaced batches of 8. Full methodology and results are provided in results/sod1_zn_pilot_rfdiffusion3_summary.md.

### 2.4 Validation tooling

OpenFold3-preview calibration. Before trusting OpenFold3-preview on any novel design, I calibrated it against the same known-answer problem established in prior work: wild-type SOD1 folded and compared to the 1SOS crystal structure (previously validated via AlphaFold2/ColabFold at 0.361 Å RMSD over 150/153 residues). OpenFold3-preview (checkpoint of3-p2-155k.pt) was run on the same full-length wild-type sequence via the ColabFold MSA server, 5 independent diffusion samples/seeds. Each sample was superposed onto 1SOS chain A with PyMOL align (5-cycle outlier-rejecting refinement, matching the project's established superposition methodology):

[TABLE]
Sample | RMSD after refinement (Å) | Residues retained | RMSD before refinement (Å) | Avg. pLDDT
1 | 0.263 | 140/153 | 0.627 | 89.41
2 | 0.273 | 140/153 | 0.632 | 89.51
3 (top-ranked) | 0.283 | 140/153 | 0.628 | 89.78
4 | 0.297 | 144/153 | 0.639 | 89.34
5 | 0.261 | 138/153 | 0.362 | 88.66
[/TABLE]

Table 2.4-1. OpenFold3-preview calibration against 1SOS chain A (wild-type SOD1), 5 independent diffusion samples.
Result: PASS for reproduction of the known-answer structural benchmark, with an important limitation. All 5/5 independent OpenFold3-preview samples reproduce the WT SOD1 fold with outlier-rejected RMSDs of 0.261–0.297 Å. This establishes that the validation tool can accurately reproduce the known SOD1 structure under the tested workflow; it does not by itself establish that OpenFold3-preview is a validated surrogate for experimental correctness of de novo designs. PyMOL outlier rejection retained 138–144/153 residues versus 150/153 in the original AF2 benchmark, so both filtered and unfiltered metrics should be interpreted explicitly. Full per-sample data, structures, and the PyMOL session are in results/openfold3preview_calibration/.

### 2.5 Compute environment

Local: RTX 3070 (8GB VRAM), WSL2/Ubuntu, used for RFdiffusion1, ProteinMPNN, RFdiffusion3, LigandMPNN, and initial AlphaFold2 self-consistency screening. RFdiffusion3 peaked at 4.66 GiB and LigandMPNN at 0.26 GiB at the project's ~150 aa target scale. OpenFold3-preview was run on a rented A100 SXM4 80GB instance. Because the RFdiffusion1 and RFdiffusion3 comparisons use different structure-prediction validators (AlphaFold2/ColabFold versus OpenFold3-preview), quantitative validator-dependent differences were interpreted cautiously pending a same-validator cross-check; that cross-check (Section 2.6, Section 3.3) was subsequently run and found the RFdiffusion1-versus-RFdiffusion3 self-consistency difference to persist in the direction tested.

### 2.6 Same-validator cross-check (RFdiffusion1 designs, OpenFold3-preview)

To address the validator difference noted in Section 2.3, the existing 80 RFdiffusion1 ProteinMPNN sequences (Section 2.2) were folded through the same OpenFold3-preview setup used for RFdiffusion3 validation (checkpoint of3-p2-155k.pt, public ColabFold MSA server), rather than generating new designs. Folding was run on a RunPod A100 instance, batched in 10 groups of 8 sequences per backbone; the environment was verified with a single-sequence test fold (successful, pLDDT consistent with that sequence's original AlphaFold2 score) before committing to the full batch. All 80 sequences folded successfully. Self-consistency RMSD was computed against each sequence's own source RFdiffusion1 backbone (Kabsch-aligned full-chain Cα), and motif Cα deviation was computed with the project's motif_geom.py method (Kabsch-aligned 4-point, matching Section 2.2), preserving the backbone-to-sequence structure (10 backbones × 8 sequences) throughout for backbone-level analysis. An outlier-rejected self-consistency RMSD variant was also computed for transparency but is not used for the primary pass/fail determination (Section 3.3), consistent with this project's practice of using the global/unfiltered metric as the primary criterion throughout.

## 3. Results


### 3.1 RFdiffusion1 baseline (SOD1 Zn motif)

0/10 generated RFdiffusion1 backbones satisfied the strict backbone-level designability criterion (self-consistency RMSD < 2 Å AND motif Cα deviation < 0.5 Å). Among the 80 ProteinMPNN sequences, 4/80 (5%) satisfied the self-consistency criterion alone (sc_rmsd < 2 Å); none of these sequences also satisfied the motif-deviation threshold, consistent with the 0/10 backbone-level result. The best-performing candidate by self-consistency RMSD was design_3; its best sequence (design_3_seq3) had a minimum motif deviation of 2.102 Å, 4.2× the 0.5 Å tolerance. Independent full-recycling refolding of this post hoc selected candidate improved overall fold confidence substantially (mean pLDDT 85.35 → 85–88 across 5 models) but only modestly tightened motif geometry (2.102 Å → 1.747 Å; still ~3.5× the tolerance, driven primarily by the Asp83 position). Full results are in Supplementary Table 1.

### 3.2 Disulfide control (RFdiffusion1)

To distinguish whether the RFdiffusion1 SOD1-motif result reflects a general pipeline limitation or difficulty associated with the motif being tested, I ran an otherwise matched RFdiffusion1 pipeline on the Cys57–Cys146 disulfide bond from the same protein. The principal experimental difference was motif type and geometry: a rigid four-point Zn-coordination site versus a two-point disulfide constraint. The control therefore provides evidence that the RFdiffusion1 workflow can generate successful designs at the same batch size, while not isolating geometric complexity from every chemical and sequence-context difference.
Raw RFdiffusion1 backbone geometry was tight (max deviation 0.182 Å across 10/10 unique designs), consistent with the prior pilot. ProteinMPNN produced 80 sequences (8/backbone) with 0/160 identity violations at the fixed cysteine positions. AF2 self-consistency (num_recycle=0) gave a mean pLDDT of 70.9 (versus 47.7 for the SOD1 Zn motif).
4 of 10 backbones passed the strict designability bar (self-consistency RMSD < 2 Å AND motif deviation < 0.5 Å), and 7 of 10 passed a loosened 1.5 Å motif tolerance, compared with 0/10 on both bars for the SOD1 Zn motif (Section 3.1).

[TABLE]
Metric | SOD1 Zn (4-pt, rigid) | Disulfide (2-pt, this pilot)
Best motif deviation | 2.10 Å | 0.017 Å
Mean pLDDT | 47.7 | 70.9
Backbones passing strict bar | 0/10 | 4/10
Backbones passing loose bar (1.5 Å) | 0/10 | 7/10
[/TABLE]

Table 3.2-1. Motif-rigidity comparison across two RFdiffusion1 pilots on human SOD1 (1SOS), matched checkpoint, batch size, and contig mechanics.
The disulfide control provides evidence against a trivial inability of the RFdiffusion1 workflow to produce successful designs at n=10: changing the tested motif from the rigid four-point Zn site to a two-point disulfide constraint changed the observed outcome from 0/10 to 4/10 successful backbones under the same general pipeline. This is consistent with motif-dependent difficulty, but the experiment does not prove that geometric complexity alone caused the difference because motif chemistry, residue identity, local sequence context, and structural environment also change. The control is therefore used as supporting, not definitive, evidence for motif-dependent difficulty.

### 3.3 RFdiffusion3 (SOD1 Zn motif)

10 backbones (matched n, md5-verified unique, 126–155 aa), 8 ProteinMPNN sequences per backbone and 8 LigandMPNN sequences per backbone, 160 total. There were 0/320 identity violations at fixed motif positions. All 160 sequences were folded via OpenFold3-preview self-consistency against the public ColabFold MSA server. ProteinMPNN is the primary matched comparison to RFdiffusion1; LigandMPNN results are reported separately.

[TABLE]
Metric | ProteinMPNN (n=80) | LigandMPNN (n=80) | Overall (n=160)
Mean pLDDT | 80.44 | 76.97 | 78.7
Mean self-consistency RMSD | 3.01 Å | 4.58 Å | 3.80 Å
sc_rmsd < 2 Å alone | 51/80 (64%) | 49/80 (61%) | 100/160 (63%)
Best motif max-deviation | 1.649 Å | 1.755 Å | 1.649 Å
Strict pass (sc_rmsd<2 Å AND motif max-dev<0.5 Å) | 0/80 | 0/80 | 0/160
[/TABLE]

Table 3.3-1. RFdiffusion3 self-consistency results on the SOD1 Zn motif, by sequence-design arm. ProteinMPNN is the primary matched comparison; LigandMPNN is reported as a secondary metal-aware arm.
Primary matched comparison: RFdiffusion1 ProteinMPNN (n=80 sequences from 10 backbones) versus RFdiffusion3 ProteinMPNN (n=80 sequences from 10 backbones). The observed sequence-level self-consistency pass rate increased from 4/80 (5%) to 51/80 (64%). Because sequences are nested within only 10 independently generated backbones per model, these percentages should be interpreted as descriptive pilot results rather than as a statistically powered estimate of population-level performance.

[TABLE]
 | RFdiffusion1 + AlphaFold2/ColabFold (n=80) | RFdiffusion3 + OpenFold3-preview, ProteinMPNN (n=80) | RFdiffusion1 + OpenFold3-preview (n=80)
Mean pLDDT | 47.7 | 80.44 | 55.44
Mean self-consistency RMSD | 14.25 Å | 3.01 Å | 12.26 Å
sc_rmsd < 2 Å alone (sequence-level) | 4/80 (5%) | 51/80 (64%) | 5/80 (6%)
sc_rmsd < 2 Å alone, backbone-level (≥1 passing seq) | 1/10 | 9/10 | 1/10
Best motif max-deviation | 2.102 Å | 1.649 Å | 1.136 Å
Strict pass (sc_rmsd<2 Å AND motif<0.5 Å) | 0/80 | 0/80 | 0/80
Loosened pass (sc_rmsd<2 Å AND motif<1.5 Å) | 0/80 | 0/80 | 4/80 (5%)
[/TABLE]

Table 3.3-2. Primary matched comparison of RFdiffusion1 and RFdiffusion3 on the identical SOD1 Zn motif using ProteinMPNN for both models, n=10 generated backbones per model, with a same-validator RFdiffusion1 column added (Experiment 2, Section 3.3).
The primary matched comparison shows a large observed difference in computational self-consistency: 51/80 (64%) RFdiffusion3 ProteinMPNN sequences passed sc_rmsd <2 Å compared with 4/80 (5%) RFdiffusion1 ProteinMPNN sequences. Mean pLDDT was also higher for RFdiffusion3 (80.44 versus 47.7), and mean self-consistency RMSD was lower (3.01 Å versus 14.25 Å). Because the 80 sequences in each arm arise from only 10 generated backbones, these results should be treated as a matched pilot observation rather than evidence that the difference cannot arise from sampling variability.
A same-validator cross-check (pre-registered in the accompanying research plan; methodology in Section 2.6) addresses a distinct question from the sampling-variability point above: whether the observed difference depends on which structure-prediction tool folds the designs, rather than on the designs themselves (Table 3.3-2, third column). The self-consistency advantage persists essentially unchanged: RFdiffusion1 + OpenFold3-preview passes sc_rmsd < 2 Å on 5/80 sequences (6%), compared with 4/80 (5%) under the original AlphaFold2/ColabFold validator, against RFdiffusion3's 51/80 (64%). In the direction tested, this finding does not support validator choice as an explanation for the observed effect.
The same cross-check also surfaced an unplanned, exploratory result once the loosened combined bar (sc_rmsd < 2 Å AND motif deviation < 1.5 Å) is applied to both models under the same validator: RFdiffusion1 + OpenFold3-preview passes on 4/80 sequences (1/10 backbones), while RFdiffusion3 + OpenFold3-preview, ProteinMPNN arm, passes on 0/80. This is consistent with, not a contradiction of, the three-endpoint framework introduced below: RFdiffusion1's contig-based fixing constrains the Cα frame tightly at the cost of overall foldability, while RFdiffusion3's atom-level conditioning achieves reliable foldability and preserves coordinating-atom geometry by explicit conditioning, rather than by any independent constraint on the Cα frame.
Note that the strict combined criterion is not an appropriate standalone measure for RFdiffusion3, as its strategy fixes selected ligand-coordinating atoms rather than complete Cα residue frames (raw RFdiffusion3 backbone motif Cα-RMSD was already 1.2–2.1 Å before folding). A detailed breakdown of how to interpret these varying design objectives — computational self-consistency, Cα-frame conservation, and atom-level geometry — is reserved for the Discussion.

## 4. Discussion

The disulfide control (Section 3.2) substantially narrows the space of honest interpretations available for the RFdiffusion3 result, and is discussed here first because it changes how that result should be read.
On motif type and geometric complexity as supporting explanatory variables. Holding checkpoint, batch size, contig mechanics, and source structure fixed, the RFdiffusion1 pilots produced different outcomes for different motif types: the rigid four-point Zn site failed under the tested strict criteria, while the two-point disulfide control produced 4/10 successful backbones. This pattern is consistent with the residue-island difficulty relationship reported for catalytic sites in the AME benchmark, but the present controls do not isolate geometric complexity from differences in chemistry, residue identity, local sequence context, or structural environment.
RFdiffusion3 on the SOD1 Zn motif: improved computational self-consistency without satisfying the legacy Cα-frame criterion. RFdiffusion3 increased the observed ProteinMPNN self-consistency pass fraction from 5% to 64% at matched n=10 backbone generation, with mean pLDDT increasing from 47.7 to 80.44 and mean self-consistency RMSD decreasing from 14.25 Å to 3.01 Å, a difference subsequently confirmed to persist under a same-validator cross-check (Section 3.3). The result is best interpreted as evidence that RFdiffusion3 can substantially improve computational self-consistency on this motif under the tested workflow.
RFdiffusion3 does not satisfy the strict Cα-motif bar: 0/80 ProteinMPNN sequences and 0/80 LigandMPNN sequences pass the combined criterion. This should not be interpreted as evidence that RFdiffusion3 places the functionally relevant motif worse than RFdiffusion1, because the conditioning objectives differ. A post hoc, exploratory same-validator comparison on the loosened combined bar (Section 3.3) found RFdiffusion1 designs passing more often than RFdiffusion3 designs under this metric (4/80 versus 0/80), reinforcing that the two models are optimizing different, not strictly ordered, properties. A fairer future comparison should therefore either use a motif metric aligned to atom-level conditioning or explicitly compare RFdiffusion3 conditions that fix complete residue frames.
The result is best read using three independent properties rather than a single binary notion of “designability”: computational self-consistency, Cα-frame motif conservation, and atom-level coordination geometry. RFdiffusion3 substantially improves the first under the tested workflow. It does not satisfy the second under the stringent legacy threshold used here. The third is preserved by the conditioning procedure, but because those coordinating atoms are explicitly conditioned, the result is not equivalent to experimentally demonstrated metal binding. This distinction is central to the interpretation of the present computational case study.

### 4.1 On accessible reproducibility

This pipeline ran end-to-end on a single 8GB-VRAM consumer-scale GPU, plus targeted A100 compute for OpenFold3-preview. The detailed environment and troubleshooting records are useful reproducibility resources. The present study nevertheless has several limitations: only 10 independent backbones were generated per model; sequence-level observations are nested within those backbones; the RFdiffusion1 and RFdiffusion3 primary self-consistency numbers were initially validated with different structure-prediction tools, a difference a same-validator cross-check (Section 3.3) found does not account for the result, though only in the RFdiffusion1→OpenFold3-preview direction (RFdiffusion3 designs were not reciprocally folded through AlphaFold2/ColabFold); no experimental folding, stability, solubility, metallation, or functional assays were performed; and the strict Cα motif criterion is not fully aligned with RFdiffusion3's minimal-atom conditioning strategy. These limitations motivate the follow-up work described below and should be considered when generalizing beyond this SOD1 case.

### 4.2 Limitations and interpretation

The study is intentionally a computational pilot rather than an experimental validation study. The most important limitations are the small number of independent generated backbones (n=10 per model), the nesting of sequence-level observations within those backbones, the use of a stringent Cα motif metric that does not directly correspond to RFdiffusion3's minimal-atom conditioning, and the initial use of different structure-prediction validators for the RFdiffusion1 and RFdiffusion3 workflows (subsequently found in a same-validator cross-check, Section 3.3, not to account for the observed self-consistency difference, though only in the RFdiffusion1→OpenFold3-preview direction). In addition, preservation of Zn-coordination geometry in the raw designs is partly a consequence of the conditioning specification and therefore should not be interpreted as evidence of emergent metalloprotein function. The conclusions are consequently limited to the observed computational behavior of this pipeline on the SOD1 Zn motif.
A same-validator cross-check of RFdiffusion1 and RFdiffusion3 designs (Section 2.6, Section 3.3) has since been completed and found the self-consistency advantage to persist in the direction tested. The conditioning-ablation experiment comparing minimal atom fixing with full residue-frame conditioning, specified in the accompanying research plan, remains future work. Finally, reproducing a subset of the published Atomic Motif Enzyme (AME) benchmark within this local environment is planned as future calibration work to confirm broad alignment with published performance trends, though it is not required for the specific conclusions drawn here regarding the SOD1 structural motif.

## Data and Code Availability

Code and analysis scripts: https://github.com/mkroman101/sod1-motif-scaffolding
Versioned reproducibility archive (code, environment files, full result tables): Zenodo, DOI 10.5281/zenodo.22038707
Final structure coordinates: ModelArchive, accession [PENDING]

## References

Watson, J.L. et al. De novo design of protein structure and function with RFdiffusion. Nature 620, 1089–1100 (2023).
Ahern, W., Yim, J., Tischer, D., Salike, S., Woodbury, S.M., Kim, D., Kalvet, I., Kipnis, Y., Coventry, B., Altae-Tran, H.R., Bauer, M.S., Barzilay, R., Jaakkola, T.S., Krishna, R. & Baker, D. Atom-level enzyme active site scaffolding using RFdiffusion2. Nature Methods 23, 96–105 (2026). DOI: 10.1038/s41592-025-02975-x
Butcher, J., Krishna, R., Mitra, R., Brent, R.I., Li, Y., Corley, N., Kim, P.T., Funk, J., Mathis, S., Salike, S., Muraishi, A., Eisenach, H., Thompson, T.R., Chen, J., Politanska, Y., Sehgal, E., Coventry, B., Zhang, O., Qiang, B., Didi, K., Kazman, M., DiMaio, F. & Baker, D. De novo Design of All-atom Biomolecular Interactions with RFdiffusion3. bioRxiv 2025.09.18.676967 (2025). DOI: 10.1101/2025.09.18.676967. [Preprint.]
Dauparas, J., Anishchenko, I., Bennett, N., Bai, H., Ragotte, R.J., Milles, L.F., Wicky, B.I.M., Courbet, A., de Haas, R.J., Bethel, N. et al. Robust deep learning-based protein sequence design using ProteinMPNN. Science 378, 49–56 (2022).
Dauparas, J., Lee, G.R., Pecoraro, R., An, L., Anishchenko, I., Glasscock, C. & Baker, D. Atomic context-conditioned protein sequence design using LigandMPNN. Nature Methods 22, 717–723 (2025). DOI: 10.1038/s41592-025-02626-1.
AlQuraishi Lab, Columbia University & OpenFold Consortium. OpenFold3-preview [Software]. https://github.com/aqlaboratory/openfold-3. Checkpoint of3-p2-155k.pt, accessed 2026-08-16.
[1SOS — PDB structure citation, to be formatted per journal style]
Divakaruni, A., Bares, F. & Phalippou, L. AI-qualizing Science. bioRxiv 2025.02.11.637417 (2025). DOI: 10.1101/2025.02.11.637417.

## Supplementary Materials

(Separate files in this archive.)
Supplementary Table 1: Full RFdiffusion1 SOD1 pilot results — see results/sod1_zn_full_results.csv
Supplementary Table 2: Same-validator cross-check full results (Experiment 2, 80 rows) — see results/sod1_zn_rfdiffusion1_openfold3preview_crosscheck_full_results.csv
Supplementary Environment Documentation — see environment/README.md
Supplementary Troubleshooting Log — see troubleshooting_log.md
Supplementary Methods (HCAR1 comparison pilot, RFdiffusion1 only, exploratory contextual comparison; not re-run under RFdiffusion3) — see results/hcar1_pocket_pilot_summary.md