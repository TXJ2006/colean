# CoLean Incremental Proof-Chain Verifier Report

Scripts checked: `6`
Accepted: `3`
Rejected: `3`

| lemma | source path | accepted | first failure step |
|---|---|---:|---:|
| split positive mass bucket | rewrite hypothesis -> positive mass declaration | True | None |
| split positive mass bucket | missing rewrite | False | 1 |
| finite level positive bucket | positive point -> level witness -> positive bucket sum | True | None |
| finite level positive bucket | forgets bucket sum proof | False | 2 |
| finite level threshold bucket | direct weighted pigeonhole declaration | True | None |
| finite level threshold bucket | missing threshold inequality | False | 1 |
