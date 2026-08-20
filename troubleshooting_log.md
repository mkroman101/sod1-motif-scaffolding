# Troubleshooting Log — RFdiffusion Install & Pipeline on Consumer Hardware

This is the "Lane 3" content: a documented account of every real problem
hit while getting this pipeline running on an 8GB consumer GPU under
WSL2, intended to be directly useful to another independent researcher
attempting the same thing. All entries [VERIFIED] from actual command
output during this project.

## 1. Miniconda install — wrong URL path
`https://repo.anaconda.com/miniconda3/Miniconda3-latest-Linux-x86_64.sh`
returns 404. The correct path omits the "3": `.../miniconda/Miniconda3-...`.

## 2. SE3Transformer is bundled, not a standalone dependency
The intuitive move — cloning `NVIDIA/SE3Transformer` directly from GitHub
— triggered an unexpected credential prompt (the repo path appears to be
gated/reorganized) and failed with "Invalid username or token. Password
authentication is not supported." The correct approach: SE3Transformer
ships inside the RFdiffusion repo itself, at `env/SE3Transformer/`. No
separate clone needed.

## 3. `setup.py install` vs `pip install .`
Installing SE3Transformer via `python env/SE3Transformer/setup.py install`
completed without error and printed output suggesting success (egg-info
copied), but the actual package directory was never created — only
`se3_transformer-1.0.0-py3.9.egg-info` existed, no `se3_transformer/`
package. `import se3_transformer` failed. Fix: `pip install .` from the
same directory — pip built a real wheel and installed actual package
files. Old-style `setup.py install` can silently under-deliver; prefer
`pip install .` for any package install in this pipeline going forward.

## 4. `se3-transformer` not resolvable from PyPI
`pip install -e .` on RFdiffusion itself fails with "Could not find a
version that satisfies the requirement se3-transformer" — this package
genuinely isn't published to PyPI. It must be installed locally first
(per #2/#3 above) so it's already importable when RFdiffusion's own
install resolves its dependency list.

## 5. Default pip resolution grabs an incompatible torch/CUDA combination
`pip install -e .` on a fresh env pulled `torch-2.13.0+cu130` — the
newest available build. DGL's official releases only support CUDA up to
12.1, nowhere near 13.0. This is a genuine version-lag gap in the
ecosystem (DGL trails current PyTorch/CUDA releases), not a
misconfiguration. Fix: explicitly pin `torch==2.1.0` from the `cu121`
wheel index, then install DGL matching `cu121`, before installing
anything downstream that would otherwise re-resolve torch to something
newer.

## 6. Rebuilding the env doesn't guarantee a complete dependency set
After pinning torch/DGL correctly and reinstalling SE3Transformer +
RFdiffusion, `import dgl` still failed — first on a NumPy 1.x/2.x ABI
mismatch (`numpy<2` required alongside the DGL/torch pin), then on
missing `omegaconf`/`hydra-core` (needed by `run_inference.py` itself,
not captured by RFdiffusion's own `pyproject.toml`), then on missing
`dgl` backend shared libraries.

## 7. `libcusparse.so.12` not found — despite the pip package being installed
DGL's compiled C extension does a raw `dlopen` on CUDA runtime shared
libraries. The relevant `nvidia-cusparse-cu12` pip package existed but its
`.so` file wasn't on the system/env's shared-library search path.
Fix: explicitly build `LD_LIBRARY_PATH` from the actual `nvidia/*/lib`
directories under the env's `site-packages`, e.g.:
```bash
export LD_LIBRARY_PATH=$(find <env>/lib/python3.x/site-packages/nvidia \
  -name "lib" -type d | tr '\n' ':')$LD_LIBRARY_PATH
```
(An earlier attempt using a narrower `find` pattern returned nothing —
the actual package hadn't been installed yet at that point in the
debugging sequence; re-running after the package was present resolved it.)

## 8. `torchdata.datapipes` missing — version mismatch, not a missing package
Newer `torchdata` releases (0.8+) dropped the `datapipes` module that this
version of DGL still imports internally. Fix: `pip install "torchdata<0.8"`.

## 9. Given repeated cascading breaks, switched to the repo's own pinned env file
After the numpy/torchdata fixes, `pandas` came up missing next — a third
consecutive break. At that point, continuing to chase individual imports
was abandoned in favor of rebuilding the environment from RFdiffusion's
own `env/SE3nv.yml` (a maintainer-tested, coherent pin set), rather than
continuing to hand-assemble versions one failure at a time:
```bash
conda env remove -n rfdiffusion
conda env create -f env/SE3nv.yml -n rfdiffusion
```
This resolved most of the cascade but was not fully complete — `opt_einsum`
(an `e3nn` dependency) and `e3nn` itself were still missing afterward, and
SE3Transformer needed to be reinstalled in the new env (env rebuild via
the yml pins dependencies but doesn't install SE3Transformer's own
package — that step, #3 above, had to be redone).

## 10. RFdiffusion contig map: comma vs. slash delimiters
`contigmap.contigs=[30-40,A63-63,20-30,...]` (comma-delimited) parses
successfully into RFdiffusion's stored config (`config.contigmap.contigs`
shows the intended list correctly) but silently collapses to unconditional
generation at the actual sampler level — `sampled_mask` shows a single
unconstrained block instead of the intended multi-segment structure, and
`con_ref_pdb_idx`/`con_hal_pdb_idx` come back as empty lists. No error is
raised. Fix: slash-delimited segments. This is a dangerous silent-failure
class of bug — always verify `sampled_mask` and `con_*_pdb_idx` are
populated as expected on a small test batch (`num_designs=2`) before
committing to a full run.

## 11. `nvidia-smi` inside WSL2 does not reliably show per-process VRAM
Repeatedly showed "No running processes found" and a flat memory reading
even during confirmed active GPU compute (high `torch.cuda.is_available()`
confirmation, high GPU-Util% at larger design sizes). This is a known
WSL2 GPU-passthrough limitation, not a bug in the pipeline. Reliable
alternatives: `torch.cuda.max_memory_allocated()` from inside the actual
process, or Windows Task Manager's GPU performance tab (which does see
WSL2 GPU usage correctly).

## 12. RFdiffusion3 (foundry/rfd3): Triton JIT needs a C compiler, none present
`rc-foundry[rfd3]` installs and imports cleanly, but the first actual
`rfd3 design` call fails deep in a Triton kernel launch with
`RuntimeError: Failed to find C compiler. Please specify via CC
environment variable...`. This WSL2 install has no system `gcc` (only the
`gcc-16-base` runtime library package, not the compiler). Fix, without
sudo/apt: `conda install -c conda-forge gcc gxx` into the same env. Same
fix was needed again for LigandMPNN's ProDy C extension (#13) — worth
doing proactively for any new env in this project going forward.

## 13. LigandMPNN: ProDy has a C extension too — same gcc fix
`pip install -r requirements.txt` fails building ProDy's wheel with the
same `gcc: No such file or directory` as #12. Same fix:
`conda install -c conda-forge gcc gxx` into the `ligandmpnn` env before
retrying the requirements install.

## 14. LigandMPNN: ProDy imports the now-removed `pkg_resources`
After #13's fix, `run.py` fails on `ModuleNotFoundError: No module named
'pkg_resources'` — modern `setuptools` (83.x, installed by default in a
fresh env) dropped `pkg_resources` as an importable API, but ProDy 2.4.1
(pinned by LigandMPNN's `requirements.txt`, itself several years old)
still imports it directly. Fix: `pip install "setuptools<81"`.

## 15. Custom in-process instrumentation broke OpenFold3-preview's multiprocessing DataLoader
To get real VRAM numbers via `torch.cuda.max_memory_allocated()` (the
same method used successfully for RFdiffusion3 and LigandMPNN), a wrapper
script called `run_openfold`'s CLI via `runpy.run_path(..., run_name=
"__main__")` plus an `atexit` hook to print stats after the run. This
silently broke PyTorch DataLoader's multiprocessing worker bootstrap
(`RuntimeError: An attempt has been made to start a new process before
the current process has finished its bootstrapping phase...`) — because
the real installed CLI entry-point script has the required
`if __name__ == "__main__":` guard, and the `runpy` wrapper does not.
Worse than a clean crash: the failure mode was the **entire pipeline
silently re-executing from the top** (visible only as the ColabFold
MSA-submission log appearing twice in one run's output) before finally
erroring out — a genuinely dangerous silent-duplication failure mode if
the run had happened to succeed on the "retry" without anyone noticing
two executions had occurred. Fix: don't wrap CLIs that use
`torch.utils.data.DataLoader` multiprocessing workers via `runpy`; call
the plain installed CLI entry point instead (which has the correct guard)
and get VRAM externally (nvidia-smi polling, since this instance is real
Linux — see #16 — not the in-process `torch.cuda` approach used for the
other two tools).

## 16. Confirmed: `nvidia-smi` IS reliable on real Linux cloud instances (unlike WSL2)
Directly tested the open question from entry #11: on the RunPod A100
instance (genuine Linux, not WSL2), `nvidia-smi --query-gpu=memory.used`
polled every 1s correctly showed 0 MiB at idle and tracked real usage
during active OpenFold3-preview inference (peaking ~3.2–3.7 GiB across
several runs, cross-checked against process start/end times). WSL2's
unreliability (entry #11) is specific to WSL2's GPU-passthrough layer, not
a general nvidia-smi limitation — on real Linux it works as expected.

## 17. Dropped SSH connection mid-install — but the install had actually finished
A `pip install openfold3` run over a plain (non-tmux) SSH session was cut
off by `Connection reset by peer` partway through, which looked like a
failure. Reconnecting and checking `pip show openfold3` revealed the
install had actually completed successfully just before the connection
dropped — the SSH session died on output flush/cleanup, not mid-install.
Lesson (applied for the rest of this handoff): always run long remote
installs/downloads inside `tmux` on the remote host, with output
redirected to a log file and an explicit `echo EXIT_CODE:$?` sentinel
appended — makes job completion independently verifiable by reconnecting,
regardless of whether the SSH session itself survives.

## 18. `df -h` on a MooseFS network volume reports cluster-wide capacity, not the pod's actual quota
When self-hosting an MMseqs2 MSA server (to avoid overloading ColabFold's
public API for a 160+ sequence batch, per their own guidance against
large-scale use of the shared server), a large database download
repeatedly failed partway through with no clear error. `df -h /workspace`
consistently showed `404T 116T avail` throughout — badly misleading. The
mount is MooseFS-backed (`mfs#us-md-1.runpod.net:9421`), and `df` reports
the underlying cluster's total capacity, not this pod's actual
provisioned quota. No client-side MooseFS quota tools were available
inside the container to query the real limit directly (`mfsgetgoal`,
`mfsdirinfo`, etc. all absent). Confirmed the real limit empirically: a
controlled `dd` write past current usage hit `dd: error writing
'...': Disk quota exceeded` at exactly the pod's actual 50GB allocation.
**Lesson: on FUSE/network-mounted volumes, don't trust `df -h` for
capacity planning — verify the real quota with a controlled test write,
or check the provider's dashboard, before diagnosing failures as
network/software issues.** This one cost real debugging time chasing a
"network instability" theory before the actual cause (undersized volume)
was found.

## 19. `aria2c`'s default file-allocation hangs indefinitely on a MooseFS network volume
After resizing the volume, large downloads (UniRef30, ~103GB) reliably
stalled forever at the exact same byte count (`41003515904` bytes) on
two separate attempts, with no error — just silence for 45+ minutes
until manually killed. This is `aria2c`'s default disk-space
pre-allocation step (`fallocate`-equivalent), which behaves fine on
local disk but can hang indefinitely on some FUSE-backed distributed
filesystems that don't support fast pre-allocation. Fix: add
`--file-allocation=none` to the `aria2c` command. After the fix, real
download progress was confirmed immediately via `aria2c`'s own progress
line (real MiB/s, real % complete) rather than assumed.

## 20. Sustained large writes to the MooseFS volume intermittently fail with genuine I/O errors — but are resumable
Even with `--file-allocation=none`, both `aria2c` downloads and `tar`
extraction of large files (100GB+) intermittently failed mid-transfer
with real `Input/output error` (`errno=5`, EIO) — not hangs, actual
write failures, at unpredictable points (sometimes >95% through a
transfer). This appears to be a genuine reliability characteristic of
this network volume under sustained large sequential writes, not a
one-off fluke — it recurred across many separate attempts. `aria2c`
handles this gracefully: it leaves a `.aria2` control file and resumes
from the failure point on the next invocation (confirmed: a download
resumed from 89.8GB rather than restarting from zero). `tar` has no
equivalent resume capability — a failed extraction must restart from the
beginning of the archive, making it far more expensive to recover from
on a flaky filesystem. Mitigation: wrap both download and extraction in
a retry loop (`until CMD; do sleep N; done`), and expect extraction of a
100GB+ archive on this kind of volume to need many attempts (raised the
retry ceiling to 20 in practice) and substantial wall-clock time, since
each failed extraction attempt burns most of its elapsed time before
failing late.

## 21. Separately, `tar`'s default ownership-preservation fatally aborts extraction on this filesystem
Independent of the I/O-error issue above, `tar -xzf` on this network
volume also failed deterministically (not intermittently) with `tar:
Cannot change ownership to uid ...: Operation not permitted`, aborting
extraction of the archive's later members entirely once it hit a file
whose original archived ownership didn't match. This is the same class
of issue as the mmseqs binary tarballs (troubleshooting notes during
setup), but there the archive was small enough that the one failing file
was inconsequential; for a large multi-file database archive, it
truncated extraction partway through. Fix: `tar --no-same-owner
--no-same-permissions -xzf ...` — tells tar not to attempt to preserve
the archive's original ownership/permissions at all, avoiding the
`chown()` call (and its failure) entirely rather than tolerating it.

## 22. Silent tarball corruption after multiple interrupted/resumed download sessions — no checksum available to catch it early
After finally getting a complete UniRef30 download (`aria2c` reporting
100% success) via **several** interrupted-and-resumed sessions across
entry #20's I/O errors, every subsequent extraction attempt failed
identically and quickly with `gzip: stdin: invalid compressed data
--format violated` / `tar: Unexpected EOF in archive` — not the
intermittent I/O-error pattern from #20, but a fast, deterministic
failure. This indicates the **downloaded tarball itself was corrupted**,
most likely because the multi-session resume/reassembly (repeatedly
interrupted by #20's I/O errors, sometimes requiring 3+ resumes to reach
100%) did not reconstruct a byte-perfect file on this specific volume.
Confirmed the file size matched the expected complete size exactly
(`106729528496` bytes) despite the content being invalid — a size check
alone is not sufficient to confirm integrity here. `opendata.mmseqs.org`
does not publish an MD5/SHA256 checksum for this file, so there was no
cheap way to verify integrity before committing to a full (multi-hour)
extraction attempt on a corrupted 106GB archive — the corruption was
only discovered after burning significant additional time on repeated,
guaranteed-to-fail extraction retries against the bad file. **Lesson:
after any download that required interruption/resume on an unreliable
filesystem, verify with `gzip -t <file>` (single-pass integrity check,
no output written) before attempting extraction** — cheaper than
discovering corruption via a failed extraction, though still a real cost
for very large files. No mitigation was in place for this on the
project's first pass through this issue; this is the recommended fix
for any future attempt on this class of volume.

## Net takeaway for other independent/consumer-hardware researchers
The specific errors above are individually minor, but they compound: a
naive `pip install -e .` from a fresh clone will very likely resolve an
incompatible torch/CUDA combination by default, and the resulting
cascade of missing/mismatched dependencies (DGL, numpy, torchdata,
opt_einsum, e3nn) is not obviously connected to the original torch/CUDA
choice unless you already know to look there. Starting from the repo's
own pinned `env/SE3nv.yml`, and using `pip install .` (not
`setup.py install`) for SE3Transformer specifically, would have avoided
most of this in one pass.
