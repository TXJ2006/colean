import ColeanMathlib.Basic

set_option linter.style.header false
open scoped BigOperators

namespace ColeanMathlib
namespace KakeyaToy

def incidenceMass {Point Tube : Type} (tubes : Finset Tube)
    (pointsIn : Tube → Finset Point) : Nat :=
  ∑ t ∈ tubes, (pointsIn t).card

theorem incidence_mass_unfold {Point Tube : Type} (tubes : Finset Tube)
    (pointsIn : Tube → Finset Point) :
    incidenceMass tubes pointsIn = ∑ t ∈ tubes, (pointsIn t).card := by
  rfl

theorem positive_incidence_has_tube {Point Tube : Type} (tubes : Finset Tube)
    (pointsIn : Tube → Finset Point)
    (h : 0 < incidenceMass tubes pointsIn) :
    ∃ t ∈ tubes, 0 < (pointsIn t).card := by
  exact positive_mass_bucket tubes (fun t => (pointsIn t).card) h

theorem positive_incidence_has_point_on_tube {Point Tube : Type} (tubes : Finset Tube)
    (pointsIn : Tube → Finset Point)
    (h : 0 < incidenceMass tubes pointsIn) :
    ∃ t ∈ tubes, ∃ x ∈ pointsIn t, True := by
  rcases positive_incidence_has_tube tubes pointsIn h with ⟨t, ht, hcard⟩
  rcases Finset.card_pos.mp hcard with ⟨x, hx⟩
  exact ⟨t, ht, x, hx, True.intro⟩

theorem binary_direction_positive_bucket {Point Tube : Type} (tubes : Finset Tube)
    (leftDirection : Tube → Prop) [DecidablePred leftDirection]
    (pointsIn : Tube → Finset Point)
    (h : 0 < (∑ t ∈ tubes.filter leftDirection, (pointsIn t).card)
        + (∑ t ∈ tubes.filter (fun t => ¬ leftDirection t), (pointsIn t).card)) :
    (∃ t ∈ tubes.filter leftDirection, 0 < (pointsIn t).card)
      ∨ (∃ t ∈ tubes.filter (fun t => ¬ leftDirection t), 0 < (pointsIn t).card) := by
  exact binary_level_positive_bucket tubes leftDirection (fun t => (pointsIn t).card) h

theorem finite_direction_positive_bucket {Point Tube Direction : Type}
    [DecidableEq Direction]
    (tubes : Finset Tube) (directions : Finset Direction)
    (direction : Tube → Direction) (pointsIn : Tube → Finset Point)
    (hcover : ∀ t ∈ tubes, direction t ∈ directions)
    (h : 0 < incidenceMass tubes pointsIn) :
    ∃ d ∈ directions,
      0 < ∑ t ∈ tubes.filter (fun t => direction t = d), (pointsIn t).card := by
  exact finite_level_positive_bucket tubes directions direction
    (fun t => (pointsIn t).card) hcover h

theorem finite_direction_threshold_bucket {Point Tube Direction : Type}
    [DecidableEq Direction]
    (tubes : Finset Tube) (directions : Finset Direction)
    (direction : Tube → Direction) (pointsIn : Tube → Finset Point)
    (threshold : Nat)
    (hcover : ∀ t ∈ tubes, direction t ∈ directions)
    (hnonempty : directions.Nonempty)
    (hbig : directions.card • threshold ≤ incidenceMass tubes pointsIn) :
    ∃ d ∈ directions,
      threshold ≤ ∑ t ∈ tubes.filter (fun t => direction t = d), (pointsIn t).card := by
  exact finite_level_threshold_bucket tubes directions direction
    (fun t => (pointsIn t).card) threshold hcover hnonempty hbig

theorem threshold_bucket_gives_nonempty_direction_when_positive
    {Point Tube Direction : Type} [DecidableEq Direction]
    (tubes : Finset Tube) (directions : Finset Direction)
    (direction : Tube → Direction) (pointsIn : Tube → Finset Point)
    (hcover : ∀ t ∈ tubes, direction t ∈ directions)
    (hnonempty : directions.Nonempty)
    (hbig : directions.card • 1 ≤ incidenceMass tubes pointsIn) :
    ∃ d ∈ directions,
      0 < ∑ t ∈ tubes.filter (fun t => direction t = d), (pointsIn t).card := by
  rcases finite_direction_threshold_bucket tubes directions direction pointsIn 1
      hcover hnonempty hbig with ⟨d, hd, hbucket⟩
  exact ⟨d, hd, Nat.lt_of_lt_of_le Nat.zero_lt_one hbucket⟩

end KakeyaToy
end ColeanMathlib
