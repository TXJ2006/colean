from __future__ import annotations

from dataclasses import dataclass

from correspondence import Event


@dataclass(frozen=True)
class ProofState:
    lemma: str
    goal: str
    stage: str


@dataclass(frozen=True)
class VerificationResult:
    accepted: bool
    old_state: ProofState
    new_state: ProofState
    tactic: str
    message: str
    weight_delta: float


class ToyVerifier:
    """A tiny deterministic verifier that mimics Lean-style state transitions."""

    def initial_state(self, lemma: str) -> ProofState:
        goals = {
            "dyadic mass lemma": "find a nonempty dyadic bucket carrying mass",
            "incidence identity": "rewrite incidence count as swapped finite sum",
            "tube density toy": "derive a selected-cell density lower bound",
        }
        return ProofState(lemma=lemma, goal=goals.get(lemma, "unknown goal"), stage="start")

    def check(self, state: ProofState, candidate: Event[str, str]) -> VerificationResult:
        transition_key = (state.lemma, state.stage, candidate.target)
        transitions = {
            (
                "dyadic mass lemma",
                "start",
                "simp [Finset.sum_filter]",
            ): ("filtered_sum", "accepted filter decomposition"),
            (
                "dyadic mass lemma",
                "filtered_sum",
                "obtain <x, hx> := ...",
            ): ("done", "accepted bucket witness extraction"),
            (
                "incidence identity",
                "start",
                "rw [Finset.sum_biUnion]",
            ): ("expanded_incidence", "accepted incidence expansion"),
            (
                "incidence identity",
                "expanded_incidence",
                "rw [Finset.sum_sigma']",
            ): ("done", "accepted summation swap"),
            (
                "tube density toy",
                "start",
                "exact Finset.sum_le_sum hcell",
            ): ("pointwise_bound", "accepted pointwise finite-sum bound"),
            (
                "tube density toy",
                "pointwise_bound",
                "nlinarith",
            ): ("done", "accepted arithmetic closure"),
        }
        if transition_key in transitions:
            new_stage, message = transitions[transition_key]
            return VerificationResult(
                accepted=True,
                old_state=state,
                new_state=ProofState(state.lemma, state.goal, new_stage),
                tactic=candidate.target,
                message=message,
                weight_delta=0.10,
            )
        return VerificationResult(
            accepted=False,
            old_state=state,
            new_state=state,
            tactic=candidate.target,
            message=f"rejected tactic at stage {state.stage}",
            weight_delta=-0.06,
        )


def run_stateful_search(candidates: list[Event[str, str]], max_steps: int = 6) -> list[dict[str, object]]:
    verifier = ToyVerifier()
    grouped: dict[str, list[Event[str, str]]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.source, []).append(candidate)

    trace: list[dict[str, object]] = []
    for lemma, lemma_candidates in grouped.items():
        state = verifier.initial_state(lemma)
        ranked = sorted(lemma_candidates, key=lambda event: event.weight, reverse=True)
        attempts = 0
        while state.stage != "done" and attempts < max_steps:
            progressed = False
            for candidate in ranked:
                attempts += 1
                result = verifier.check(state, candidate)
                trace.append(
                    {
                        "lemma": lemma,
                        "old_stage": result.old_state.stage,
                        "tactic": result.tactic,
                        "accepted": result.accepted,
                        "new_stage": result.new_state.stage,
                        "message": result.message,
                        "old_weight": round(candidate.weight, 4),
                        "new_weight": round(max(0.0, candidate.weight + result.weight_delta), 4),
                    }
                )
                if result.accepted:
                    state = result.new_state
                    progressed = True
                    break
            if not progressed:
                break
    return trace
