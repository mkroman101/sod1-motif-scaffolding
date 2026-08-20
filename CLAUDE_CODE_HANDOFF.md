GOAL: Fill in the [PENDING] sections of a reproducibility archive assembled
from a conversation transcript, replacing placeholder/transcribed content
with real exports and data pulled directly from the local research
machine, in preparation for a Zenodo deposit alongside a bioRxiv
manuscript draft.

BACKGROUND: An archive skeleton was built from conversation history and
uploaded/exists at [PATH — attach or specify where this archive was
extracted to on the local machine, e.g. ~/paper_archive/]. It contains a
manuscript draft, verified pipeline documentation, and results summaries
for two completed pilots (SOD1 zinc-site motif scaffolding, HCAR1 pocket
motif scaffolding), but several pieces of real data were not available in
the conversation transcript and need to be pulled from disk.

TASK — for each item below, locate the real file/data, and either copy it
into the archive at the specified location or update the specified
markdown file with the real content, clearly replacing any [PENDING]
marker:

1. REAL CONDA ENVIRONMENT EXPORTS
   Run and save output to environment/rfdiffusion_env_export.yml and
   environment/proteinmpnn_env_export.yml:
     conda activate rfdiffusion && conda env export > <path>/environment/rfdiffusion_env_export.yml
     conda activate proteinmpnn && conda env export > <path>/environment/proteinmpnn_env_export.yml
   Update environment/README.md to reference these real files instead of
   the transcribed version-pin notes (keep the transcribed notes as
   narrative context, but note that the yml files are now the source of
   truth).

2. CORRECTED CONTIG STRINGS
   Find the actual working (slash-delimited) contigmap.contigs strings
   used for both the SOD1 Zn pilot and the HCAR1 pocket pilot — check
   shell history, or extract from each design's .trb file
   (config.contigmap.contigs field) via:
     python3 -c "
     import pickle
     with open('<path-to-any-design-in-batch>.trb', 'rb') as f:
         d = pickle.load(f)
     print(d['config']['contigmap']['contigs'])
     "
   Update scripts/pipeline_commands.md, replacing the [PENDING] notes with
   the real corrected commands (keep the buggy comma-delimited version
   alongside it for the troubleshooting log's illustrative value — do not
   delete it).

3. FULL RESULT TABLES
   Locate the full results CSVs for both completed pilots (likely named
   something like track3_results.csv for SOD1, and an HCAR1-equivalent
   file under a directory like proteinmpnn_output_hcar1/ or
   af2_output_hcar1/). Copy both into results/ as
   results/sod1_zn_full_results.csv and results/hcar1_pocket_full_results.csv.
   Update results/sod1_zn_pilot_rfdiffusion1_summary.md and
   results/hcar1_pocket_pilot_summary.md to reference the full CSVs
   (the markdown summaries currently only show a top-10 subset
   transcribed from conversation — verify those 10 rows match the real
   CSV exactly and flag any discrepancy rather than silently trusting
   either source).

4. DISULFIDE CONTROL PILOT RESULTS
   A separate Claude Code session ("SOD1 disulfide bond scaffolding
   pilot") was tasked with running a third pilot (Cys57-Cys146 disulfide
   motif, same pipeline). Check whether that session has completed:
     - If complete: pull its full results and rewrite
       results/disulfide_control_status.md in the same format as the
       other two pilot summaries (rename the file to
       results/disulfide_control_pilot_summary.md), and copy its full
       results CSV into results/.
     - If not yet complete or not yet started: leave
       results/disulfide_control_status.md as-is, but confirm current
       status (running / not started / errored) and update the file with
       an accurate current status rather than assuming.

5. .TRB METADATA FILES
   Copy the .trb files for the standout designs referenced in the archive
   (design_3 from the SOD1 pilot; design_1 and design_4 from the HCAR1
   pilot) into a new results/trb_metadata/ subdirectory, for full
   reproducibility of the con_ref_pdb_idx/con_hal_pdb_idx mappings
   referenced in the writeups.

6. GIT REPOSITORY
   Initialize a git repository at the archive root (if not already done),
   commit everything as an initial commit with a clear message, and
   report the resulting commit hash. This repo is what should eventually
   be pushed to GitHub and referenced in the manuscript's Data and Code
   Availability section.

7. RE-ZIP
   Once all of the above is complete, create a fresh zip of the entire
   archive directory (excluding any .git internals if git history is
   large — use judgment, but prefer including a shallow/single-commit
   .git if size permits, since that preserves provenance) and report its
   final size and location.

IMPORTANT: For any item where you cannot find the real source data (e.g.
a file genuinely doesn't exist yet, like the RFdiffusion2 or AME
calibration results, since those experiments haven't been run), do NOT
fabricate placeholder data. Leave the [PENDING] marker in place and state
clearly in your final report which items remain genuinely outstanding
versus which were successfully filled in.

Do not modify any of the original pilot output directories
(pilot_zn_scaffold/, pilot_hcar1_pocket/, proteinmpnn_output/,
af2_output_hcar1/, etc.) — only copy from them, read-only.

DELIVERABLE: A final report listing, for each of the 7 numbered items
above: done / not applicable / genuinely blocked (with reason), plus the
final archive size and location, and the git commit hash.
