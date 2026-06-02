# CoLean v0

This is the first local experiment for correspondence-guided proof search.

The goal is not to claim a complete Lean autoformalization system yet. The goal
is to validate the computational mechanism:

```text
paper lemma -> formal statement -> Mathlib declaration -> tactic
```

Each arrow is represented as a weighted correspondence:

```text
X <- E -> Y
```

The experiment composes these layers by fiber join, local weight composition,
push/reduce, and verifier feedback.

## Run

From the repository/workspace root:

```powershell
python work\colean_v0\run_experiment.py
```

Outputs:

```text
outputs/colean_v0_results.json
outputs/colean_v0_report.md
outputs/colean_v0_experiment_note.md
```

To run the real Lean kernel candidate verifier:

```powershell
python work\colean_v0\lean_kernel_verifier.py
```

Additional outputs:

```text
outputs/colean_kernel_verifier_results.json
outputs/colean_kernel_verifier_report.md
```

To run the Mathlib-backed verifier:

```powershell
python work\colean_v0\mathlib_verifier.py
```

Additional outputs:

```text
outputs/colean_mathlib_verifier_results.json
outputs/colean_mathlib_verifier_report.md
```

To run the multi-step proof-chain verifier:

```powershell
python work\colean_v0\proof_chain_verifier.py
```

Additional outputs:

```text
outputs/colean_proof_chain_verifier_results.json
outputs/colean_proof_chain_verifier_report.md
```

To run the incremental proof-chain verifier:

```powershell
python work\colean_v0\incremental_proof_chain_verifier.py
```

Additional outputs:

```text
outputs/colean_incremental_verifier_results.json
outputs/colean_incremental_verifier_report.md
```

To run the feedback learning round:

```powershell
python work\colean_v0\feedback_learner.py
```

Additional outputs:

```text
outputs/colean_feedback_learning_results.json
outputs/colean_feedback_learning_report.md
```

To run the local Ollama LLM experiment:

```powershell
python work\colean_v0\local_llm_generator.py
```

This uses `qwen2.5-coder:1.5b` by default. Override it with:

```powershell
$env:COLEAN_LOCAL_MODEL = "qwen2.5-coder:7b"
python work\colean_v0\local_llm_generator.py
```

Additional outputs:

```text
outputs/colean_local_llm_results.json
outputs/colean_local_llm_report.md
```

## What v0 Shows

The structured relation benchmark compares:

```text
naive materialized search space: |X| * |Z| * |Y|
correspondence search space:    sum_z |E_z| * |F_z|
```

For the default case, the experiment gets:

```text
dense_triple_loop_cells = 19,200,000
fiber_join_pairs = 2,400
avoidance_ratio = 8000x
```

In the scale sweep, the ratio grows from `500x` to `72000x` under the same
structured sparsity pattern.

## What v0 Does Not Yet Show

The Lean toolchain is now installed and linked locally:

```text
Lean 4.30.0
Lake 5.0.0
```

`lean/KernelToy.lean` is accepted by the real Lean kernel. The verifier script
checks six candidate tactic proofs and records three accepted candidates and
three rejected candidates.

A Mathlib project now exists at `work/colean_mathlib`. It proves a Finset finite
sum split theorem and an incidence-counting toy identity. The Mathlib verifier
checks four candidate tactic proofs and records two accepted candidates and two
rejected candidates.

The current version also proves a two-step Mathlib proof-chain:

```text
split finite sum hypothesis
-> rewrite hypothesis with Finset.sum_filter_add_sum_filter_not
-> apply Finset.sum_pos_iff
-> obtain a positive-mass bucket
```

The proof-chain verifier checks four candidate tactic scripts. Lean accepts the
correct two-step script and rejects the three wrong scripts.

It also proves a binary-level positive-bucket theorem:

```text
positive split sum
-> use omega to show one side has positive mass
-> branch on the positive side
-> apply Finset.sum_pos_iff on that side
```

The proof-chain verifier now checks seven candidate tactic scripts across two
proof-chain targets. Lean accepts the two correct scripts and rejects the five
wrong scripts.

The newest proof-chain target is a finite-level positive-bucket theorem:

```text
total mass on s is positive
-> extract a positive-mass point
-> map the point to its level
-> use the level cover hypothesis
-> prove that level bucket has positive total mass
```

The proof-chain verifier now checks ten candidate tactic scripts across three
proof-chain targets. Lean accepts the three correct scripts and rejects seven
wrong scripts.

The latest target is a threshold pigeonhole theorem:

```text
levels.card • threshold ≤ total mass
-> some level bucket has mass at least threshold
```

This uses Mathlib's weighted pigeonhole theorem:

```lean
Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum
```

The proof-chain verifier now checks thirteen candidate tactic scripts across
four proof-chain targets. Lean accepts the four correct scripts and rejects nine
wrong scripts.

The incremental verifier checks proof-chain prefixes. It can locate the first
failing step, for example:

```text
missing rewrite -> step 1
forgets bucket sum proof -> step 2
missing threshold inequality -> step 1
```

The feedback learner converts this into edge updates. Accepted proof steps are
reinforced, first failing steps are penalized, and valid prefixes before a later
failure are preserved with a small positive update.

The local LLM experiment is now wired through Ollama. On this machine, both
tested local models fail when asked to freely write full Lean tactics:

```text
qwen2.5-coder:1.5b free generation: accepted = 0/4
qwen2.5-coder:7b   free generation: accepted = 0/4
```

But the same models become useful when CoLean gives them structured proof
chains to rank and Lean checks the ranked options:

```text
qwen2.5-coder:1.5b CoLean ranking: top-1 = 4/4, top-3 = 4/4
qwen2.5-coder:7b   CoLean ranking: top-1 = 4/4, top-3 = 4/4
```

This supports the intended division of labor: local LLMs provide cheap proposal
or ranking signals, CoLean preserves the candidate graph, and Lean/Mathlib
remain the correctness oracle.

The failure recovery analyzer also turns failed free-generation attempts into
structured events:

```text
free-generation failure
-> failure class
-> repair action
-> structured candidate fiber
-> Lean-accepted top-k proof
```

This reflects the original CoPU/C-IR principle that failures should leave
weighted correspondence events rather than disappearing as discarded prompts.

The model comparison note is written to:

```text
outputs/colean_local_llm_model_comparison.md
outputs/colean_failure_recovery_report.md
```

A Kakeya-related toy Mathlib library is now included at:

```text
work/colean_mathlib/ColeanMathlib/KakeyaToy.lean
```

It formalizes a finite incidence-counting skeleton:

```text
finite tube family
-> incidence mass
-> positive tube
-> positive point on a tube
-> binary/finite direction buckets
-> threshold direction bucket
```

The file currently has one definition, seven theorems, `sorry = 0`, and
`lake build` passes.

The report is written to:

```text
outputs/colean_kakeya_toy_report.md
```

## Next Milestone

Move from candidate-chain checking to incremental proof-state search:

```text
tactic candidate -> Lean process/LSP -> success or error -> weight update
```

The first larger theorem target should be a dyadic-pigeonhole lemma with
`sorry = 0`, using the split-positive-mass chain as its inner skeleton.
