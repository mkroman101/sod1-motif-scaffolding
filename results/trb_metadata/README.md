# .trb metadata — standout designs

Real `.trb` files (RFdiffusion's per-design metadata pickle) for the three
backbones singled out in the results summaries and manuscript draft as
the closest-to-passing leads, copied read-only from the original pilot
output directories on 2026-08-15:

| File | Source | `con_ref_pdb_idx` (native motif) | `con_hal_pdb_idx` (scaffold numbering) |
|---|---|---|---|
| `sod1_zn_design_3.trb` | `~/RFdiffusion/pilot_zn_scaffold/design_3.trb` | `[('A',63),('A',71),('A',80),('A',83)]` | `[('A',32),('A',59),('A',87),('A',104)]` |
| `hcar1_pocket_design_1.trb` | `~/RFdiffusion/pilot_hcar1_pocket/design_1.trb` | `[('A',71),('A',75),('A',95),('A',99),('A',268)]` | `[('A',35),('A',58),('A',81),('A',107),('A',133)]` |
| `hcar1_pocket_design_4.trb` | `~/RFdiffusion/pilot_hcar1_pocket/design_4.trb` | `[('A',71),('A',75),('A',95),('A',99),('A',268)]` | `[('A',34),('A',54),('A',78),('A',103),('A',123)]` |

`con_ref_pdb_idx`/`con_hal_pdb_idx` extracted and cross-checked directly
from each file via the same pickle-load pattern shown in
`CLAUDE_CODE_HANDOFF.md` item 2 and used throughout `scripts/motif_geom.py`.
The SOD1 `design_3` mapping above matches `motif_geom.py`'s own example
`hal_pairs` exactly, confirming internal consistency between the script
and the real metadata.

Full 10-design batches (all 20 SOD1 + HCAR1 `.trb` files, plus the 10
disulfide-control `.trb` files) remain in the original, untouched pilot
output directories on the research machine — only these three "standout
design" files were pulled into the archive per the reproducibility
request; the rest are reproducible from the corrected contig commands in
`scripts/pipeline_commands.md` plus the same checkpoint/seed-free
RFdiffusion run (RFdiffusion sampling is stochastic and not seeded in
these runs, so exact re-runs will produce different backbones with
similar aggregate statistics, not byte-identical files).
