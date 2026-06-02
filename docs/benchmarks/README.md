# Lean Benchmark Track

This project treats Lean benchmarks as the main experimental challenge for the
CoLean prototype.

## Current Harness

Run the current smoke benchmark:

```powershell
python colean_v0\benchmark_harness.py
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

## Reporting Rule

Do not claim SOTA from smoke tasks. A result becomes benchmark-grade only when:

- all benchmark tasks and generated proofs are committed or reproducibly
  regenerated
- Lean accepts final files
- `sorry = 0`
- top-k pass rates are computed over the full selected split
- wall-clock and verifier-only timings are reported
- failures are included, not filtered out

