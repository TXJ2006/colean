import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Combinatorics.Pigeonhole
import Mathlib.Tactic

set_option linter.style.header false
open scoped BigOperators

namespace ColeanMathlib

theorem finite_sum_filter_split {α : Type} (s : Finset α) (p : α → Prop)
    [DecidablePred p] (f : α → Nat) :
    (∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x) = ∑ x ∈ s, f x := by
  exact Finset.sum_filter_add_sum_filter_not s p f

theorem incidence_identity_toy {Point Tube : Type} (tubes : Finset Tube)
    (pointsIn : Tube → Finset Point) :
    (∑ t ∈ tubes, (pointsIn t).card) = ∑ t ∈ tubes, (pointsIn t).card := by
  rfl

theorem positive_mass_bucket {α : Type} (s : Finset α) (f : α → Nat)
    (h : 0 < ∑ x ∈ s, f x) : ∃ x ∈ s, 0 < f x := by
  exact (Finset.sum_pos_iff).mp h

theorem split_positive_mass_bucket {α : Type} (s : Finset α) (p : α → Prop)
    [DecidablePred p] (f : α → Nat)
    (h : 0 < (∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x)) :
    ∃ x ∈ s, 0 < f x := by
  rw [Finset.sum_filter_add_sum_filter_not] at h
  exact (Finset.sum_pos_iff).mp h

theorem binary_level_positive_bucket {α : Type} (s : Finset α) (p : α → Prop)
    [DecidablePred p] (f : α → Nat)
    (h : 0 < (∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x)) :
    (∃ x ∈ s.filter p, 0 < f x) ∨ (∃ x ∈ s.filter (fun x => ¬ p x), 0 < f x) := by
  have hside :
      0 < (∑ x ∈ s.filter p, f x) ∨ 0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by
    omega
  rcases hside with hp | hnp
  · left
    exact (Finset.sum_pos_iff).mp hp
  · right
    exact (Finset.sum_pos_iff).mp hnp

theorem finite_level_positive_bucket {α β : Type} [DecidableEq β]
    (s : Finset α) (levels : Finset β) (level : α → β) (f : α → Nat)
    (hcover : ∀ x ∈ s, level x ∈ levels)
    (h : 0 < ∑ x ∈ s, f x) :
    ∃ b ∈ levels, 0 < ∑ x ∈ s.filter (fun x => level x = b), f x := by
  rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩
  refine ⟨level x, hcover x hxs, ?_⟩
  exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩

theorem finite_level_threshold_bucket {α β : Type} [DecidableEq β]
    (s : Finset α) (levels : Finset β) (level : α → β) (f : α → Nat)
    (threshold : Nat)
    (hcover : ∀ x ∈ s, level x ∈ levels)
    (hnonempty : levels.Nonempty)
    (hbig : levels.card • threshold ≤ ∑ x ∈ s, f x) :
    ∃ b ∈ levels, threshold ≤ ∑ x ∈ s.filter (fun x => level x = b), f x := by
  exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty hbig

end ColeanMathlib
