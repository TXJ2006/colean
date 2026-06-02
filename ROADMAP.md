# Roadmap

## Phase 0: Current State

- Weighted correspondence engine for composing candidate layers.
- Lean kernel and Mathlib-backed candidate verifiers.
- Incremental proof-chain verifier with first-failure localization.
- Feedback learner that updates edge/path weights from Lean results.
- Local Ollama LLM integration for proof-chain ranking.
- Verified Kakeya-toy finite incidence library with `sorry = 0`.

## Phase 1: System Prototype

- Normalize project layout and command-line entry points.
- Add a reusable proof-task schema.
- Add persistent graph storage for candidate edges and verifier feedback.
- Record every failed LLM/tactic attempt as a structured event.
- Add top-k metrics across tasks, not just per-example reports.

## Phase 2: Lean Proof-State Search

- Integrate Lean LSP or a stable Lean process loop.
- Capture old proof state, tactic, result, and new proof state.
- Learn tactic applicability by proof-state features.
- Add repair templates for common failures:
  - missing rewrite
  - wrong theorem arguments
  - missing witness tuple
  - missing intermediate state
  - wrong branch proof

## Phase 3: Mathlib Retrieval

- Build a type-aware Mathlib declaration index.
- Combine lexical, namespace, type-shape, simp-normal-form, and rewrite-pattern signals.
- Evaluate retrieval precision on theorem-local proof tasks.

## Phase 4: Benchmarks

Initial benchmark targets:

- miniF2F-style theorem proving tasks
- Lean Workbook / autoformalization-style statement tasks
- Mathlib proof repair tasks
- theorem-proving tasks with known proof-state traces
- custom research-level local proof-chain benchmark built from finite combinatorics and analysis fragments

Success metrics:

- Lean accepts final files
- `sorry = 0`
- top-1/top-k pass rate
- proof repair iterations
- time to first verified proof
- Mathlib retrieval precision
- human edit distance
- dependency graph coverage

## Phase 5: Research-Level Case Study

Start from a controlled Kakeya-related proof chain:

```text
finite tube families
incidence counting
dyadic/threshold pigeonholing
simple density inequalities
```

The target is not to claim a full Wang-Zahl/Guth Kakeya formalization at once.
The target is a verified local proof chain that would normally require substantial
manual Lean effort.

