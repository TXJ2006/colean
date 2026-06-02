from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from paths import OUT, ROOT


@dataclass(frozen=True)
class LeanCandidate:
    lemma: str
    theorem_header: str
    tactic: str
    weight: float


def check_candidate(candidate: LeanCandidate) -> dict[str, object]:
    source = "\n".join(
        [
            "namespace CoLeanKernelToy",
            "",
            candidate.theorem_header,
            f"  {candidate.tactic}",
            "",
            "end CoLeanKernelToy",
            "",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Candidate.lean"
        path.write_text(source, encoding="utf-8")
        proc = subprocess.run(
            ["lean", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    accepted = proc.returncode == 0
    return {
        "lemma": candidate.lemma,
        "tactic": candidate.tactic,
        "old_weight": candidate.weight,
        "accepted_by_lean_kernel": accepted,
        "new_weight": round(candidate.weight + (0.10 if accepted else -0.06), 4),
        "returncode": proc.returncode,
        "stderr": proc.stderr.strip(),
    }


def candidates() -> list[LeanCandidate]:
    return [
        LeanCandidate(
            "dyadic mass toy",
            "theorem dyadic_mass_toy (a b : Nat) : a + b = b + a := by",
            "exact Nat.add_comm a b",
            0.91,
        ),
        LeanCandidate(
            "dyadic mass toy",
            "theorem dyadic_mass_toy (a b : Nat) : a + b = b + a := by",
            "exact Nat.add_assoc a b 0",
            0.31,
        ),
        LeanCandidate(
            "incidence identity toy",
            "theorem incidence_identity_toy (a b c : Nat) : (a + b) + c = a + (b + c) := by",
            "exact Nat.add_assoc a b c",
            0.88,
        ),
        LeanCandidate(
            "incidence identity toy",
            "theorem incidence_identity_toy (a b c : Nat) : (a + b) + c = a + (b + c) := by",
            "exact Nat.add_comm a b",
            0.29,
        ),
        LeanCandidate(
            "tube density toy",
            "theorem tube_density_toy (a b : Nat) (h : a <= b) : a <= b := by",
            "exact h",
            0.86,
        ),
        LeanCandidate(
            "tube density toy",
            "theorem tube_density_toy (a b : Nat) (h : a <= b) : a <= b := by",
            "exact Nat.le_refl a",
            0.27,
        ),
    ]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    results = [check_candidate(candidate) for candidate in candidates()]
    summary = {
        "experiment": "real Lean kernel candidate verification",
        "lean_version": subprocess.run(
            ["lean", "--version"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        ).stdout.strip(),
        "candidates_checked": len(results),
        "accepted": sum(1 for row in results if row["accepted_by_lean_kernel"]),
        "rejected": sum(1 for row in results if not row["accepted_by_lean_kernel"]),
        "results": results,
    }
    json_path = OUT / "colean_kernel_verifier_results.json"
    md_path = OUT / "colean_kernel_verifier_report.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# CoLean Real Lean Kernel Verifier Report",
        "",
        f"Lean: `{summary['lean_version']}`",
        "",
        f"Candidates checked: `{summary['candidates_checked']}`",
        f"Accepted: `{summary['accepted']}`",
        f"Rejected: `{summary['rejected']}`",
        "",
        "| lemma | tactic | accepted | weight update |",
        "|---|---:|---:|---:|",
    ]
    for row in summary["results"]:
        lines.append(
            f"| {row['lemma']} | `{row['tactic']}` | {row['accepted_by_lean_kernel']} | "
            f"{row['old_weight']} -> {row['new_weight']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
