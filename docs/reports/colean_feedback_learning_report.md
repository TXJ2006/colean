# CoLean Feedback Learning Report

Scripts checked: `6`
Accepted: `3`
Rejected: `3`

## Ranking Before

| path | weight |
|---|---:|
| rewrite hypothesis -> positive mass declaration | 0.91 |
| direct weighted pigeonhole declaration | 0.9 |
| positive point -> level witness -> positive bucket sum | 0.86 |
| missing rewrite | 0.46 |
| forgets bucket sum proof | 0.33 |
| missing threshold inequality | 0.32 |

## Ranking After

| path | weight |
|---|---:|
| rewrite hypothesis -> positive mass declaration | 1.06 |
| direct weighted pigeonhole declaration | 1.05 |
| positive point -> level witness -> positive bucket sum | 1.01 |
| missing rewrite | 0.38 |
| forgets bucket sum proof | 0.28 |
| missing threshold inequality | 0.24 |

## Edge Updates

| edge | reason | delta |
|---|---|---:|
| `split positive mass bucket::step1::rw [Finset.sum_filter_add_sum_filter_not] at h` | accepted proof path | 0.12 |
| `split positive mass bucket::step2::exact (Finset.sum_pos_iff).mp h` | accepted proof path | 0.12 |
| `split positive mass bucket::step1::exact (Finset.sum_pos_iff).mp h` | first failing proof step | -0.1 |
| `finite level positive bucket::step1::rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩` | accepted proof path | 0.12 |
| `finite level positive bucket::step2::refine ⟨level x, hcover x hxs, ?_⟩` | accepted proof path | 0.12 |
| `finite level positive bucket::step3::exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩` | accepted proof path | 0.12 |
| `finite level positive bucket::step1::rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩` | valid prefix before later failure | 0.03 |
| `finite level positive bucket::step2::exact ⟨level x, hcover x hxs, hfx⟩` | first failing proof step | -0.1 |
| `finite level threshold bucket::step1::exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty hbig` | accepted proof path | 0.12 |
| `finite level threshold bucket::step1::exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty` | first failing proof step | -0.1 |
