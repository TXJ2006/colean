# CoLean v0 Experiment Report

## What this tests

Keep candidate fibers instead of collapsing the proof task into a single prompt.

## Pipeline

- paper lemma -> formal statement
- formal statement -> mathlib declaration
- mathlib declaration -> tactic
- compose by fiber join, reduce by endpoints, update weights from verifier feedback

## Composition Stats

```json
{
  "paper_statement_to_declaration": {
    "left_events": 6,
    "right_events": 8,
    "join_pairs": 8,
    "output_events_before_reduce": 8,
    "output_events_after_reduce": 8,
    "max_middle_fiber_product": 3,
    "materialized_matrix_cells": 144
  },
  "paper_to_tactic": {
    "left_events": 8,
    "right_events": 8,
    "join_pairs": 8,
    "output_events_before_reduce": 8,
    "output_events_after_reduce": 8,
    "max_middle_fiber_product": 1,
    "materialized_matrix_cells": 192
  }
}
```

## Top Composed Proof Candidates

| paper lemma | tactic | score | path |
|---|---:|---:|---|
| dyadic mass lemma | `simp [Finset.sum_filter]` | 0.4766 | correct statement -> filter decomposition -> rewrite filtered sum |
| incidence identity | `rw [Finset.sum_biUnion]` | 0.4765 | correct statement -> incidence expansion -> expand incidence |
| incidence identity | `rw [Finset.sum_sigma']` | 0.4654 | correct statement -> swap summation -> swap summation |
| tube density toy | `exact Finset.sum_le_sum hcell` | 0.295 | usable statement -> monotonicity -> pointwise bound |
| dyadic mass lemma | `obtain <x, hx> := ...` | 0.2944 | correct statement -> nonzero bucket -> extract level |
| dyadic mass lemma | `obtain <k, hk> := Nat.exists_pow_le n` | 0.2153 | correct statement -> dyadic scale -> choose dyadic k |
| tube density toy | `nlinarith` | 0.1991 | usable statement -> scale inequality -> close arithmetic |
| dyadic mass lemma | `exact Finset.card_pos.mp h` | 0.1092 | related -> cardinality witness -> card witness |

## Stateful Verifier Trace

| lemma | old stage | tactic | accepted | new stage | weight update |
|---|---|---:|---:|---|---:|
| dyadic mass lemma | start | `simp [Finset.sum_filter]` | True | filtered_sum | 0.4766 -> 0.5766 |
| dyadic mass lemma | filtered_sum | `simp [Finset.sum_filter]` | False | filtered_sum | 0.4766 -> 0.4166 |
| dyadic mass lemma | filtered_sum | `obtain <x, hx> := ...` | True | done | 0.2944 -> 0.3944 |
| incidence identity | start | `rw [Finset.sum_biUnion]` | True | expanded_incidence | 0.4765 -> 0.5765 |
| incidence identity | expanded_incidence | `rw [Finset.sum_biUnion]` | False | expanded_incidence | 0.4765 -> 0.4165 |
| incidence identity | expanded_incidence | `rw [Finset.sum_sigma']` | True | done | 0.4654 -> 0.5654 |
| tube density toy | start | `exact Finset.sum_le_sum hcell` | True | pointwise_bound | 0.295 -> 0.395 |
| tube density toy | pointwise_bound | `exact Finset.sum_le_sum hcell` | False | pointwise_bound | 0.295 -> 0.235 |
| tube density toy | pointwise_bound | `nlinarith` | True | done | 0.1991 -> 0.2991 |

## Verifier Summary

```json
{
  "lemmas_seen": 3,
  "lemmas_completed": 3,
  "completed_lemmas": [
    "dyadic mass lemma",
    "incidence identity",
    "tube density toy"
  ],
  "total_tactic_attempts": 9,
  "accepted_attempts": 6,
  "rejected_attempts": 3,
  "attempts_by_lemma": {
    "dyadic mass lemma": 3,
    "incidence identity": 3,
    "tube density toy": 3
  },
  "accepted_steps_by_lemma": {
    "dyadic mass lemma": 2,
    "incidence identity": 2,
    "tube density toy": 2
  },
  "mean_attempts_per_completed_lemma": 3.0
}
```

## Generated Correspondence Summary

```json
{
  "statement_events": 6,
  "declaration_events": 7,
  "tactic_events": 6,
  "task_to_declaration_join_pairs": 7,
  "task_to_tactic_join_pairs": 9,
  "raw_task_to_tactic_paths": 9,
  "top_generated_paths": [
    {
      "task": "finite sum filter split",
      "tactic": "exact Finset.sum_filter_add_sum_filter_not s p f",
      "score": 0.8305,
      "path": "generated statement: split by predicate -> retrieved declaration -> direct exact"
    },
    {
      "task": "positive mass bucket",
      "tactic": "exact (Finset.sum_pos_iff).mp h",
      "score": 0.7369,
      "path": "generated statement: exists positive bucket -> retrieved declaration -> direct iff elimination"
    },
    {
      "task": "incidence identity toy",
      "tactic": "rfl",
      "score": 0.6806,
      "path": "generated statement: identity -> retrieved declaration -> reflexivity + generated statement: wrong theorem shape -> wrong statement mapping -> wrong tactic"
    },
    {
      "task": "finite sum filter split",
      "tactic": "rfl",
      "score": 0.2723,
      "path": "generated statement: split by predicate -> bad proof candidate -> reflexivity + generated statement: split by predicate -> retrieved declaration -> wrong tactic"
    },
    {
      "task": "positive mass bucket",
      "tactic": "exact Finset.sum_pos hpos hs",
      "score": 0.2138,
      "path": "generated statement: exists positive bucket -> related declaration + generated statement: too strong -> wrong statement mapping -> needs stronger assumptions"
    },
    {
      "task": "positive mass bucket",
      "tactic": "exact h",
      "score": 0.1602,
      "path": "generated statement: exists positive bucket -> retrieved declaration -> wrong type"
    }
  ],
  "top_raw_paths": [
    {
      "task": "finite sum filter split",
      "tactic": "exact Finset.sum_filter_add_sum_filter_not s p f",
      "score": 0.8305,
      "path": "generated statement: split by predicate -> retrieved declaration -> direct exact"
    },
    {
      "task": "positive mass bucket",
      "tactic": "exact (Finset.sum_pos_iff).mp h",
      "score": 0.7369,
      "path": "generated statement: exists positive bucket -> retrieved declaration -> direct iff elimination"
    },
    {
      "task": "incidence identity toy",
      "tactic": "rfl",
      "score": 0.6734,
      "path": "generated statement: identity -> retrieved declaration -> reflexivity"
    },
    {
      "task": "positive mass bucket",
      "tactic": "exact Finset.sum_pos hpos hs",
      "score": 0.2138,
      "path": "generated statement: exists positive bucket -> related declaration + generated statement: too strong -> wrong statement mapping -> needs stronger assumptions"
    },
    {
      "task": "finite sum filter split",
      "tactic": "rfl",
      "score": 0.1674,
      "path": "generated statement: split by predicate -> bad proof candidate -> reflexivity"
    },
    {
      "task": "positive mass bucket",
      "tactic": "exact h",
      "score": 0.1602,
      "path": "generated statement: exists positive bucket -> retrieved declaration -> wrong type"
    },
    {
      "task": "finite sum filter split",
      "tactic": "rfl",
      "score": 0.1049,
      "path": "generated statement: split by predicate -> retrieved declaration -> wrong tactic"
    },
    {
      "task": "incidence identity toy",
      "tactic": "exact Finset.sum_filter_add_sum_filter_not s p f",
      "score": 0.057,
      "path": "generated statement: wrong theorem shape -> wrong statement mapping -> direct exact"
    }
  ]
}
```

## Real Lean Kernel Summary

```json
{
  "lean_version": "Lean (version 4.30.0, x86_64-w64-windows-gnu, commit d024af099ca4bf2c86f649261ebf59565dc8c622, Release)",
  "candidates_checked": 6,
  "accepted": 3,
  "rejected": 3
}
```

## Mathlib-Backed Verifier Summary

```json
{
  "candidates_checked": 6,
  "accepted": 3,
  "rejected": 3
}
```

## Multi-Step Proof-Chain Summary

```json
{
  "scripts_checked": 13,
  "accepted": 4,
  "rejected": 9,
  "accepted_scripts": [
    [
      "rw [Finset.sum_filter_add_sum_filter_not] at h",
      "exact (Finset.sum_pos_iff).mp h"
    ],
    [
      "have hside : 0 < (∑ x ∈ s.filter p, f x) ∨ 0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by",
      "  omega",
      "rcases hside with hp | hnp",
      "· left",
      "  exact (Finset.sum_pos_iff).mp hp",
      "· right",
      "  exact (Finset.sum_pos_iff).mp hnp"
    ],
    [
      "rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",
      "refine ⟨level x, hcover x hxs, ?_⟩",
      "exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩"
    ],
    [
      "exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty hbig"
    ]
  ]
}
```

## Incremental Proof-Chain Summary

```json
{
  "scripts_checked": 6,
  "accepted": 3,
  "rejected": 3,
  "first_failure_steps": {
    "missing rewrite": 1,
    "forgets bucket sum proof": 2,
    "missing threshold inequality": 1
  }
}
```

## Feedback Learning Summary

```json
{
  "scripts_checked": 6,
  "accepted": 3,
  "rejected": 3,
  "ranking_before": [
    [
      "rewrite hypothesis -> positive mass declaration",
      0.91
    ],
    [
      "direct weighted pigeonhole declaration",
      0.9
    ],
    [
      "positive point -> level witness -> positive bucket sum",
      0.86
    ],
    [
      "missing rewrite",
      0.46
    ],
    [
      "forgets bucket sum proof",
      0.33
    ],
    [
      "missing threshold inequality",
      0.32
    ]
  ],
  "ranking_after": [
    [
      "rewrite hypothesis -> positive mass declaration",
      1.06
    ],
    [
      "direct weighted pigeonhole declaration",
      1.05
    ],
    [
      "positive point -> level witness -> positive bucket sum",
      1.01
    ],
    [
      "missing rewrite",
      0.38
    ],
    [
      "forgets bucket sum proof",
      0.28
    ],
    [
      "missing threshold inequality",
      0.24
    ]
  ],
  "edge_update_count": 10
}
```

## Structured Relation Benchmark

```json
{
  "n_left": 400,
  "n_middle": 120,
  "n_right": 400,
  "left_events": 800,
  "right_events": 360,
  "fiber_join_pairs": 2400,
  "dense_triple_loop_cells": 19200000,
  "estimated_avoidance_ratio": 8000.0,
  "output_events_after_reduce": 2380,
  "max_middle_fiber_product": 24
}
```

## Benchmark Sweep

| X | Z | Y | dense cells | fiber join pairs | avoidance ratio |
|---:|---:|---:|---:|---:|---:|
| 100 | 30 | 100 | 300000 | 600 | 500.0x |
| 200 | 60 | 200 | 2400000 | 1200 | 2000.0x |
| 400 | 120 | 400 | 19200000 | 2400 | 8000.0x |
| 800 | 240 | 800 | 153600000 | 4800 | 32000.0x |
| 1200 | 360 | 1200 | 518400000 | 7200 | 72000.0x |

## Current Lean Status

Lean/lake are installed and linked locally. Pure-Lean and Mathlib-backed verifiers are passing.
