# Lean Benchmark Track

This project treats Lean benchmarks as the main experimental challenge for the
CoLean prototype.

## Current Harness

Run the current smoke benchmark:

```powershell
python colean_v0\benchmark_harness.py
```

Generate the current miniF2F sample task file after cloning the benchmark under
`downloads/miniF2F-lean4`:

```powershell
python scripts\import_minif2f_subset.py --limit 10
python colean_v0\benchmark_harness.py --suite miniF2F_sample_v0 --tasks-json docs\benchmarks\miniF2F_sample_v0.json
```

For local Windows runs where the benchmark project lives outside the repository
or under a short F-drive path, set `COLEAN_MATHLIB_PROJECT`:

```powershell
$env:COLEAN_MATHLIB_PROJECT='F:\CodexAssets\colean\miniF2F-lean4'
$env:MATHLIB_CACHE_DIR='F:\CodexAssets\colean\mathlib-cache'
python colean_v0\benchmark_harness.py --suite miniF2F_sample_v0_quick_top1 `
  --tasks-json docs\benchmarks\miniF2F_sample_v0.json `
  --max-tasks 3 --max-candidates 1 --candidate-timeout 90 --progress
```

The harness reports:

- accepted / rejected task count
- top-1, top-2, top-3, and top-5 pass rate
- first accepted candidate rank
- time to first verified proof
- per-candidate Lean verification time

Outputs are written under:

```text
outputs/benchmarks/
```

## External Benchmark Interface

The harness can also read an external task file:

```powershell
python colean_v0\benchmark_harness.py --suite external_v0 --tasks-json path\to\tasks.json
```

Expected JSON shape:

```json
{
  "tasks": [
    {
      "task_id": "example_001",
      "source": "benchmark_name",
      "project_path": "downloads/miniF2F-lean4",
      "imports": ["Mathlib"],
      "lemma": "human readable lemma name",
      "theorem_header": "theorem ... := by",
      "informal_goal": "optional informal statement",
      "candidates": [
        {
          "option_id": "A",
          "weight": 0.9,
          "tactics": ["exact ..."]
        }
      ]
    }
  ]
}
```

## Target Benchmarks

The near-term targets are established Lean theorem-proving and
autoformalization-style suites:

- miniF2F-style mathematical theorem proving tasks
- ProofNet-style informal-to-formal theorem tasks
- LeanWorkbook-style large-scale Lean theorem proving tasks
- selected Mathlib local theorem chains for controlled ablations

The first imported external subset is
[`miniF2F_sample_v0.json`](miniF2F_sample_v0.json), generated from
`yangky11/miniF2F-lean4` at the recorded source revision.

## Current miniF2F Pilot

The first verified miniF2F pilot uses Lean 4.24.0 with Mathlib cache on F drive.
On the first three imported Test tasks with only the top-ranked candidate per
task, the current prototype verifies 1 / 3 tasks:

- `aime_1983_p2`: accepted at rank 1 by the structured `abs_split_linarith`
  candidate
- `aime_1983_p1`: rejected by the current weak baseline candidate
- `aime_1983_p3`: rejected by the current weak baseline candidate

This is a pipeline milestone, not a benchmark-grade score: it proves that the
external miniF2F import, Mathlib toolchain, candidate ranking, and Lean verifier
loop are connected end to end. The next benchmark step is to improve generated
structured candidates and then expand from the quick slice to the full selected
miniF2F subset.

## Reporting Rule

Do not claim SOTA from smoke tasks. A result becomes benchmark-grade only when:

- all benchmark tasks and generated proofs are committed or reproducibly
  regenerated
- Lean accepts final files
- `sorry = 0`
- top-k pass rates are computed over the full selected split
- wall-clock and verifier-only timings are reported
- failures are included, not filtered out
