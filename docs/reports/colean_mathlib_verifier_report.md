# CoLean Mathlib-Backed Verifier Report

Lean: `Lean (version 4.30.0, x86_64-w64-windows-gnu, commit d024af099ca4bf2c86f649261ebf59565dc8c622, Release)`

Candidates checked: `6`
Accepted: `3`
Rejected: `3`

| lemma | tactic | accepted | weight update |
|---|---:|---:|---:|
| finite sum filter split | `exact Finset.sum_filter_add_sum_filter_not s p f` | True | 0.93 -> 1.03 |
| finite sum filter split | `rfl` | False | 0.25 -> 0.19 |
| positive mass bucket | `exact (Finset.sum_pos_iff).mp h` | True | 0.9 -> 1.0 |
| positive mass bucket | `exact h` | False | 0.22 -> 0.16 |
| incidence identity toy | `rfl` | True | 0.88 -> 0.98 |
| incidence identity toy | `exact Finset.sum_filter_add_sum_filter_not tubes (fun _ => True) (fun t => (pointsIn t).card)` | False | 0.24 -> 0.18 |
