# CoLean Failure Recovery Report

LLM failures become structured correspondence events instead of discarded attempts.

| model | free accepted | CoLean accepted | top-1 | top-3 | appended missing options |
|---|---:|---:|---:|---:|---|
| qwen2.5-coder:1.5b | 0/4 | 4/4 | 4/4 | 4/4 | - |
| qwen2.5-coder:7b | 0/4 | 4/4 | 4/4 | 4/4 | - |

## qwen2.5-coder:1.5b

Failure classes:

```json
{
  "missing_intermediate_state": 1,
  "near_mathlib_declaration": 4,
  "witness_shape_incomplete": 1
}
```

Top failure -> repair edges:

| failed output | repair action | weight | class |
|---|---|---:|---|
| `split positive mass bucket::free_generation_failure` | map informal tactic phrase to exact Mathlib declaration candidate | 0.82 | near_mathlib_declaration |
| `binary level positive bucket::free_generation_failure` | map informal tactic phrase to exact Mathlib declaration candidate | 0.82 | near_mathlib_declaration |
| `finite level positive bucket::free_generation_failure` | map informal tactic phrase to exact Mathlib declaration candidate | 0.82 | near_mathlib_declaration |
| `finite level threshold bucket::free_generation_failure` | map informal tactic phrase to exact Mathlib declaration candidate | 0.82 | near_mathlib_declaration |
| `binary level positive bucket::free_generation_failure` | insert intermediate proof-state event before branch/destruct | 0.78 | missing_intermediate_state |
| `finite level threshold bucket::free_generation_failure` | rank proof-chain candidates that explicitly build the witness tuple | 0.74 | witness_shape_incomplete |

Repair -> recovery edges:

| candidate fiber | recovery | weight | evidence |
|---|---|---:|---|
| `split positive mass bucket::structured_candidate_fiber` | Lean-accepted top-k proof | 0.93 | ranked=[A, B, C] |
| `binary level positive bucket::structured_candidate_fiber` | Lean-accepted top-k proof | 0.93 | ranked=[A, B, C] |
| `finite level positive bucket::structured_candidate_fiber` | Lean-accepted top-k proof | 0.93 | ranked=[A, B, C] |
| `finite level threshold bucket::structured_candidate_fiber` | Lean-accepted top-k proof | 0.93 | ranked=[A, B, C] |

## qwen2.5-coder:7b

Failure classes:

```json
{
  "missing_intermediate_state": 1,
  "near_mathlib_declaration": 3,
  "placeholder_output": 1,
  "witness_shape_incomplete": 1
}
```

Top failure -> repair edges:

| failed output | repair action | weight | class |
|---|---|---:|---|
| `finite level positive bucket::free_generation_failure` | force candidate IDs only; reject placeholder tactic text | 0.95 | placeholder_output |
| `split positive mass bucket::free_generation_failure` | map informal tactic phrase to exact Mathlib declaration candidate | 0.82 | near_mathlib_declaration |
| `binary level positive bucket::free_generation_failure` | map informal tactic phrase to exact Mathlib declaration candidate | 0.82 | near_mathlib_declaration |
| `finite level threshold bucket::free_generation_failure` | map informal tactic phrase to exact Mathlib declaration candidate | 0.82 | near_mathlib_declaration |
| `binary level positive bucket::free_generation_failure` | insert intermediate proof-state event before branch/destruct | 0.78 | missing_intermediate_state |
| `finite level threshold bucket::free_generation_failure` | rank proof-chain candidates that explicitly build the witness tuple | 0.74 | witness_shape_incomplete |

Repair -> recovery edges:

| candidate fiber | recovery | weight | evidence |
|---|---|---:|---|
| `split positive mass bucket::structured_candidate_fiber` | Lean-accepted top-k proof | 0.93 | ranked=[A, C, B] |
| `binary level positive bucket::structured_candidate_fiber` | Lean-accepted top-k proof | 0.93 | ranked=[A, C, B] |
| `finite level positive bucket::structured_candidate_fiber` | Lean-accepted top-k proof | 0.93 | ranked=[A, C, B] |
| `finite level threshold bucket::structured_candidate_fiber` | Lean-accepted top-k proof | 0.93 | ranked=[A, B, C] |
