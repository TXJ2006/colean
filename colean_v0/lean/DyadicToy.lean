import Mathlib

namespace CoLeanToy

/-!
This is a Lean draft for the next CoLean experiment.
It is intentionally small: the real v1 goal is to have the correspondence
search loop choose a short tactic path and then let Lean check it.
-/

theorem finite_sum_filter_split {α : Type} [DecidableEq α] (s : Finset α) (p : α -> Prop)
    [DecidablePred p] (f : α -> Nat) :
    (∑ x in s.filter p, f x) + (∑ x in s.filter (fun x => ¬ p x), f x) = ∑ x in s, f x := by
  classical
  rw [← Finset.sum_filter_add_sum_filter_not s p f]

theorem incidence_identity_toy {Point Tube : Type} [DecidableEq Point] [DecidableEq Tube]
    (tubes : Finset Tube) (pointsIn : Tube -> Finset Point) :
    (∑ t in tubes, (pointsIn t).card)
      =
    (Finset.univ.filter (fun _p : Point => False)).card
      + (∑ t in tubes, (pointsIn t).card) := by
  simp

end CoLeanToy
