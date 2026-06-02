from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Generic, Hashable, Iterable, TypeVar


X = TypeVar("X", bound=Hashable)
Y = TypeVar("Y", bound=Hashable)
Z = TypeVar("Z", bound=Hashable)
W = TypeVar("W")


@dataclass(frozen=True)
class Event(Generic[X, Y]):
    source: X
    target: Y
    weight: float = 1.0
    label: str = ""


@dataclass
class ComposeStats:
    left_events: int
    right_events: int
    join_pairs: int
    output_events_before_reduce: int
    output_events_after_reduce: int
    max_middle_fiber_product: int
    materialized_matrix_cells: int

    @property
    def expansion_avoidance(self) -> float:
        if self.join_pairs == 0:
            return float("inf")
        return self.materialized_matrix_cells / self.join_pairs


class Correspondence(Generic[X, Y]):
    def __init__(self, left_name: str, right_name: str, events: Iterable[Event[X, Y]]):
        self.left_name = left_name
        self.right_name = right_name
        self.events = list(events)

    @property
    def sources(self) -> set[X]:
        return {event.source for event in self.events}

    @property
    def targets(self) -> set[Y]:
        return {event.target for event in self.events}

    def by_target(self) -> dict[Y, list[Event[X, Y]]]:
        buckets: dict[Y, list[Event[X, Y]]] = defaultdict(list)
        for event in self.events:
            buckets[event.target].append(event)
        return dict(buckets)

    def by_source(self) -> dict[X, list[Event[X, Y]]]:
        buckets: dict[X, list[Event[X, Y]]] = defaultdict(list)
        for event in self.events:
            buckets[event.source].append(event)
        return dict(buckets)

    def reduce_by_endpoints(self) -> "Correspondence[X, Y]":
        weights: dict[tuple[X, Y], float] = defaultdict(float)
        labels: dict[tuple[X, Y], list[str]] = defaultdict(list)
        for event in self.events:
            key = (event.source, event.target)
            weights[key] += event.weight
            if event.label:
                labels[key].append(event.label)
        reduced = [
            Event(source, target, weight, " + ".join(labels[(source, target)][:3]))
            for (source, target), weight in weights.items()
        ]
        return Correspondence(self.left_name, self.right_name, reduced)

    def compose(
        self,
        other: "Correspondence[Y, Z]",
        *,
        weight_compose: Callable[[float, float], float] = lambda a, b: a * b,
        reduce: bool = True,
    ) -> tuple["Correspondence[X, Z]", ComposeStats]:
        left_by_middle = self.by_target()
        right_by_middle = other.by_source()
        middle_values = set(left_by_middle) | set(right_by_middle)

        out: list[Event[X, Z]] = []
        join_pairs = 0
        max_product = 0
        for middle in middle_values:
            left_fiber = left_by_middle.get(middle, [])
            right_fiber = right_by_middle.get(middle, [])
            product = len(left_fiber) * len(right_fiber)
            max_product = max(max_product, product)
            join_pairs += product
            for left in left_fiber:
                for right in right_fiber:
                    label = f"{left.label} -> {right.label}".strip()
                    out.append(
                        Event(
                            left.source,
                            right.target,
                            weight_compose(left.weight, right.weight),
                            label,
                        )
                    )

        raw = Correspondence(self.left_name, other.right_name, out)
        result = raw.reduce_by_endpoints() if reduce else raw
        stats = ComposeStats(
            left_events=len(self.events),
            right_events=len(other.events),
            join_pairs=join_pairs,
            output_events_before_reduce=len(out),
            output_events_after_reduce=len(result.events),
            max_middle_fiber_product=max_product,
            materialized_matrix_cells=max(1, len(self.sources) * len(self.targets) * len(other.targets)),
        )
        return result, stats


def top_events(correspondence: Correspondence[X, Y], n: int = 5) -> list[Event[X, Y]]:
    return sorted(correspondence.events, key=lambda event: event.weight, reverse=True)[:n]
