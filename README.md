# CoLean

CoLean is the first verification-oriented prototype of Correspondence Computing.
Lean is the current benchmark and correctness surface; the deeper project is a
mathematical substrate for next-generation AI reasoning systems and future
CoPU/C-IR execution.

The central claim is:

```text
Reasoning is not primarily dense tensor evaluation or one-shot text generation.
Reasoning is structured correspondence search over composable event spaces.
```

Instead of asking an LLM to produce one final proof, CoLean keeps weighted candidate
fibers across several layers:

```text
informal theorem
-> Lean statement
-> Mathlib declaration
-> proof state
-> tactic candidate
-> verified proof
```

Lean/Mathlib remains the correctness oracle. Local or API LLMs are proposal and
ranking signals. Failed attempts are converted into structured correspondence
events rather than discarded.

## Current Prototype

This repository currently contains:

- `colean_v0/`: Python prototype for correspondence composition, local LLM ranking, Lean verification, incremental failure localization, and feedback learning.
- `colean_mathlib/`: Lean 4 / Mathlib project with verified finite-sum, bucket, and Kakeya-toy incidence lemmas.
- `docs/source/`: original correspondence-computing lecture PDF.
- `docs/reports/`: current experiment reports and JSON outputs.
- `docs/foundation/`: foundational note in Markdown, DOCX, and PDF form.
- `docs/benchmarks/`: Lean benchmark track and harness notes.

Highlights:

```text
structured relation benchmark: 8000x candidate-enumeration reduction
scale sweep: 500x -> 72000x reduction under structured sparsity
local LLM free Lean generation: 0/4 accepted
local LLM + CoLean candidate ranking: 4/4 accepted
KakeyaToy.lean: 1 definition, 7 theorems, sorry = 0
```

## Quick Start

Run the Python prototype:

```powershell
python colean_v0\run_experiment.py
```

Run the Lean/Mathlib project:

```powershell
cd colean_mathlib
lake build
```

Run local LLM ranking with Ollama:

```powershell
ollama pull qwen2.5-coder:1.5b
$env:COLEAN_LOCAL_MODEL = "qwen2.5-coder:1.5b"
python colean_v0\local_llm_generator.py
```

Run benchmark-style top-k verification metrics:

```powershell
python colean_v0\benchmark_harness.py
```

For a stronger local model:

```powershell
ollama pull qwen2.5-coder:7b
$env:COLEAN_LOCAL_MODEL = "qwen2.5-coder:7b"
python colean_v0\local_llm_generator.py
```

## Verified Lean Artifacts

The current Lean project includes:

- finite sum filter split
- positive mass bucket
- split/binary/finite level positive buckets
- finite threshold bucket
- Kakeya-toy finite incidence skeleton

The Kakeya-toy file is:

```text
colean_mathlib/ColeanMathlib/KakeyaToy.lean
```

It formalizes:

```text
finite tube family
-> incidence mass
-> positive tube
-> positive point on a tube
-> binary/finite direction buckets
-> threshold direction bucket
```

## Research Direction

The next goal is to turn CoLean into a benchmarkable system:

1. Expand from toy proof chains to 10-20 theorem local formalization tasks.
2. Add Lean proof-state extraction and tactic-level search loops.
3. Build a Mathlib declaration index with type-aware retrieval.
4. Evaluate on established Lean autoformalization and theorem-proving benchmarks.
5. Target research-level case studies, starting from discrete/Kakeya-style local proof chains.

See [ROADMAP.md](ROADMAP.md).

For current progress, see [STATUS.md](STATUS.md).

For the core mathematical foundation, see [docs/foundation/FOUNDATIONS.md](docs/foundation/FOUNDATIONS.md),
[DOCX](docs/foundation/Correspondence_Computing_Foundations_v0_1.docx), and
[PDF](docs/foundation/Correspondence_Computing_Foundations_v0_1.pdf).

For the original source PDF, see
[docs/source/correspondence_computing_lectures_v1_2.pdf](docs/source/correspondence_computing_lectures_v1_2.pdf).

For the Lean benchmark track, see [docs/benchmarks/README.md](docs/benchmarks/README.md).

For model/toolchain asset policy, see [docs/ASSETS.md](docs/ASSETS.md).

## License

MIT.
