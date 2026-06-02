# CoLean Real Lean Kernel Verifier Report

Lean: `Lean (version 4.30.0, x86_64-w64-windows-gnu, commit d024af099ca4bf2c86f649261ebf59565dc8c622, Release)`

Candidates checked: `6`
Accepted: `3`
Rejected: `3`

| lemma | tactic | accepted | weight update |
|---|---:|---:|---:|
| dyadic mass toy | `exact Nat.add_comm a b` | True | 0.91 -> 1.01 |
| dyadic mass toy | `exact Nat.add_assoc a b 0` | False | 0.31 -> 0.25 |
| incidence identity toy | `exact Nat.add_assoc a b c` | True | 0.88 -> 0.98 |
| incidence identity toy | `exact Nat.add_comm a b` | False | 0.29 -> 0.23 |
| tube density toy | `exact h` | True | 0.86 -> 0.96 |
| tube density toy | `exact Nat.le_refl a` | False | 0.27 -> 0.21 |
