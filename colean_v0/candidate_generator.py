from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from correspondence import Correspondence, Event
from mathlib_verifier import MathlibCandidate


@dataclass(frozen=True)
class InformalTask:
    name: str
    description: str


class CandidateGenerator(Protocol):
    def statement_candidates(self, task: InformalTask) -> Correspondence[str, str]:
        ...

    def declaration_candidates(self) -> Correspondence[str, str]:
        ...

    def tactic_candidates(self) -> Correspondence[str, str]:
        ...

    def mathlib_candidates(self) -> list[MathlibCandidate]:
        ...


class DeterministicGenerator:
    """A reproducible stand-in for the LLM proposal generator."""

    def statement_candidates(self, task: InformalTask) -> Correspondence[str, str]:
        events = {
            "finite sum filter split": [
                Event(task.name, "finite sum filter split statement", 0.93, "generated statement: split by predicate"),
                Event(task.name, "pointwise filter equality", 0.28, "generated statement: too local"),
            ],
            "positive mass bucket": [
                Event(task.name, "positive sum iff positive fiber statement", 0.90, "generated statement: exists positive bucket"),
                Event(task.name, "all buckets positive statement", 0.22, "generated statement: too strong"),
            ],
            "incidence identity toy": [
                Event(task.name, "incidence identity reflexive statement", 0.86, "generated statement: identity"),
                Event(task.name, "filter split incidence statement", 0.24, "generated statement: wrong theorem shape"),
            ],
        }
        return Correspondence("informal task", "formal statement", events.get(task.name, []))

    def declaration_candidates(self) -> Correspondence[str, str]:
        return Correspondence(
            "formal statement",
            "mathlib declaration",
            [
                Event("finite sum filter split statement", "Finset.sum_filter_add_sum_filter_not", 0.94, "retrieved declaration"),
                Event("finite sum filter split statement", "rfl", 0.20, "bad proof candidate"),
                Event("positive sum iff positive fiber statement", "Finset.sum_pos_iff", 0.89, "retrieved declaration"),
                Event("positive sum iff positive fiber statement", "Finset.sum_pos", 0.48, "related declaration"),
                Event("all buckets positive statement", "Finset.sum_pos", 0.35, "wrong statement mapping"),
                Event("incidence identity reflexive statement", "rfl", 0.87, "retrieved declaration"),
                Event("filter split incidence statement", "Finset.sum_filter_add_sum_filter_not", 0.25, "wrong statement mapping"),
            ],
        )

    def tactic_candidates(self) -> Correspondence[str, str]:
        return Correspondence(
            "mathlib declaration",
            "tactic",
            [
                Event("Finset.sum_filter_add_sum_filter_not", "exact Finset.sum_filter_add_sum_filter_not s p f", 0.95, "direct exact"),
                Event("Finset.sum_filter_add_sum_filter_not", "rfl", 0.12, "wrong tactic"),
                Event("Finset.sum_pos_iff", "exact (Finset.sum_pos_iff).mp h", 0.92, "direct iff elimination"),
                Event("Finset.sum_pos_iff", "exact h", 0.20, "wrong type"),
                Event("Finset.sum_pos", "exact Finset.sum_pos hpos hs", 0.42, "needs stronger assumptions"),
                Event("rfl", "rfl", 0.90, "reflexivity"),
            ],
        )

    def mathlib_candidates(self) -> list[MathlibCandidate]:
        theorem_filter = (
            "theorem finite_sum_filter_split {α : Type} (s : Finset α) (p : α → Prop)\n"
            "    [DecidablePred p] (f : α → Nat) :\n"
            "    (∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x) = ∑ x ∈ s, f x := by"
        )
        theorem_positive = (
            "theorem positive_mass_bucket {α : Type} (s : Finset α) (f : α → Nat)\n"
            "    (h : 0 < ∑ x ∈ s, f x) : ∃ x ∈ s, 0 < f x := by"
        )
        theorem_incidence = (
            "theorem incidence_identity_toy {Point Tube : Type} (tubes : Finset Tube)\n"
            "    (pointsIn : Tube → Finset Point) :\n"
            "    (∑ t ∈ tubes, (pointsIn t).card) = ∑ t ∈ tubes, (pointsIn t).card := by"
        )
        return [
            MathlibCandidate("finite sum filter split", theorem_filter, "exact Finset.sum_filter_add_sum_filter_not s p f", 0.93),
            MathlibCandidate("finite sum filter split", theorem_filter, "rfl", 0.25),
            MathlibCandidate("positive mass bucket", theorem_positive, "exact (Finset.sum_pos_iff).mp h", 0.90),
            MathlibCandidate("positive mass bucket", theorem_positive, "exact h", 0.22),
            MathlibCandidate("incidence identity toy", theorem_incidence, "rfl", 0.88),
            MathlibCandidate(
                "incidence identity toy",
                theorem_incidence,
                "exact Finset.sum_filter_add_sum_filter_not tubes (fun _ => True) (fun t => (pointsIn t).card)",
                0.24,
            ),
        ]


def make_generator() -> CandidateGenerator:
    if os.environ.get("COLEAN_LLM_PROVIDER"):
        # Hook point for a future OpenAI/local-LLM implementation.
        return DeterministicGenerator()
    return DeterministicGenerator()
