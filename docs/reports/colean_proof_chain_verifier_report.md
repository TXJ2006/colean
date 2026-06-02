# CoLean Multi-Step Proof-Chain Verifier Report

Lean: `Lean (version 4.30.0, x86_64-w64-windows-gnu, commit d024af099ca4bf2c86f649261ebf59565dc8c622, Release)`

Scripts checked: `13`
Accepted: `4`
Rejected: `9`

| lemma | script | accepted | weight update |
|---|---|---:|---:|
| split positive mass bucket | `rw [Finset.sum_filter_add_sum_filter_not] at h`<br>`exact (Finset.sum_pos_iff).mp h` | True | 0.91 -> 1.03 |
| split positive mass bucket | `exact (Finset.sum_pos_iff).mp h` | False | 0.46 -> 0.39 |
| split positive mass bucket | `exact (Finset.sum_pos_iff).mp h`<br>`rw [Finset.sum_filter_add_sum_filter_not] at h` | False | 0.31 -> 0.24 |
| split positive mass bucket | `rfl` | False | 0.12 -> 0.05 |
| binary level positive bucket | `have hside : 0 < (∑ x ∈ s.filter p, f x) ∨ 0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by`<br>`  omega`<br>`rcases hside with hp | hnp`<br>`· left`<br>`  exact (Finset.sum_pos_iff).mp hp`<br>`· right`<br>`  exact (Finset.sum_pos_iff).mp hnp` | True | 0.88 -> 1.0 |
| binary level positive bucket | `left`<br>`exact (Finset.sum_pos_iff).mp h` | False | 0.34 -> 0.27 |
| binary level positive bucket | `have hside : 0 < (∑ x ∈ s.filter p, f x) ∨ 0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by`<br>`  omega`<br>`exact hside` | False | 0.28 -> 0.21 |
| finite level positive bucket | `rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩`<br>`refine ⟨level x, hcover x hxs, ?_⟩`<br>`exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩` | True | 0.86 -> 0.98 |
| finite level positive bucket | `rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩`<br>`exact ⟨level x, hcover x hxs, hfx⟩` | False | 0.33 -> 0.26 |
| finite level positive bucket | `rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩`<br>`refine ⟨level x, ?_, ?_⟩`<br>`exact hxs`<br>`exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩` | False | 0.25 -> 0.18 |
| finite level threshold bucket | `exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty hbig` | True | 0.9 -> 1.02 |
| finite level threshold bucket | `exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty` | False | 0.32 -> 0.25 |
| finite level threshold bucket | `rcases (Finset.sum_pos_iff).mp (Nat.lt_of_lt_of_le (Nat.succ_pos 0) hbig) with ⟨x, hxs, hfx⟩`<br>`refine ⟨level x, hcover x hxs, ?_⟩`<br>`exact Nat.le_of_lt hfx` | False | 0.2 -> 0.13 |
