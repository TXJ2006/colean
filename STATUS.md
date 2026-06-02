# CoLean Status

Last updated: 2026-06-02

## Current Public Prototype

Repository:

```text
https://github.com/TXJ2006/colean
```

CI status:

```text
Python compile: pass
Lean/Mathlib build: pass
```

## Implemented Components

| area | status | notes |
|---|---|---|
| Correspondence Computing foundation | done v0.1 | Markdown, DOCX, and PDF uploaded under `docs/foundation/` |
| Original source PDF | done v0 | uploaded under `docs/source/` |
| Correspondence engine | done v0 | weighted events, fiber join, compose, push/reduce |
| Lean kernel verifier | done v0 | pure Lean candidate checking |
| Mathlib verifier | done v0 | `lake env lean` candidate checking |
| Proof-chain verifier | done v0 | multi-step Mathlib proof scripts |
| Incremental verifier | done v0 | first failing step localization |
| Feedback learner | done v0 | edge/path weight updates from verifier feedback |
| Local LLM ranking | done v0 | Ollama + `qwen2.5-coder` candidate ranking |
| Failure recovery analyzer | done v0 | failed LLM output -> repair events |
| Benchmark harness | done v0 | top-k, first accepted rank, time-to-first-verified metrics |
| KakeyaToy library | done v0 | finite incidence skeleton, `sorry = 0` |
| GitHub CI | done v0 | Python + Lean build |

## Current Experimental Results

```text
structured relation benchmark: 8000x candidate-enumeration reduction
scale sweep: 500x -> 72000x reduction under structured sparsity
local LLM free Lean generation: 0/4 accepted
local LLM + CoLean candidate ranking: 4/4 accepted
KakeyaToy.lean: 1 definition, 7 theorems, sorry = 0
```

## What Gets Uploaded Where

| asset | storage plan | current status |
|---|---|---|
| Python prototype | Git repository | uploaded |
| Lean source | Git repository | uploaded |
| Experiment reports | Git repository | uploaded |
| Core foundation note | Git repository | Markdown, DOCX, and PDF uploaded |
| Original lecture PDF | Git repository | uploaded |
| Lean toolchain version | `lean-toolchain` file | uploaded |
| Mathlib dependency lock | `lake-manifest.json` | uploaded |
| Ollama model names | `docs/ASSETS.md` and scripts | uploaded |
| Model binaries | not in git; use Ollama pull or future Releases/LFS if needed | planned |
| Local build cache `.lake` | not uploaded | excluded |
| Downloaded Lean toolchain archives | not uploaded | excluded |

## Next Milestones

1. Import the first external Lean benchmark subset into the harness.
2. Add more verified Mathlib theorem chains, aiming for 20 local tasks.
3. Build a type-aware Mathlib retrieval index.
4. Connect proof-state search through Lean/LSP or a stable Lean process loop.
5. Start full Lean benchmark challenges with reproducible top-k metrics.
