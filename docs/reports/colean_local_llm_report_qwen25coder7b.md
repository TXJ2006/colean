# CoLean Local LLM Report

Host: `http://127.0.0.1:11434`
Model: `qwen2.5-coder:7b`
Candidates checked: `4`
Accepted: `0`
Rejected: `4`

| lemma | accepted | elapsed seconds | tactics | parse error |
|---|---:|---:|---|---|
| split positive mass bucket | False | 38.871 | `rewrite Finset.sum_filter_add_sum_filter_not`<br>`apply Finset.sum_pos_iff` |  |
| binary level positive bucket | False | 24.713 | `omega`<br>`rcases hside with hp | hnp`<br>`Finset.sum_pos_iff` |  |
| finite level positive bucket | False | 24.374 | `first tactic`<br>`second tactic` |  |
| finite level threshold bucket | False | 26.357 | `Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum`<br>`exists` |  |

## Constrained CoLean Ranking

Candidates checked: `4`
Accepted: `4`
Rejected: `0`

Top-k summary:

```json
{
  "top_1": {
    "hits": 4,
    "total": 4,
    "rate": 1.0
  },
  "top_2": {
    "hits": 4,
    "total": 4,
    "rate": 1.0
  },
  "top_3": {
    "hits": 4,
    "total": 4,
    "rate": 1.0
  }
}
```

| lemma | accepted | first accepted rank | model ranking |
|---|---:|---:|---|
| split positive mass bucket | True | 1 | `A, C, B` |
| binary level positive bucket | True | 1 | `A, C, B` |
| finite level positive bucket | True | 1 | `A, C, B` |
| finite level threshold bucket | True | 1 | `A, B, C` |
