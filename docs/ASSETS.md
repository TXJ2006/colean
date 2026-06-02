# Assets, Models, And Toolchains

This project uses reproducible asset references instead of committing large
binary artifacts directly into git.

## Lean Toolchain

The Lean version is pinned by:

```text
colean_mathlib/lean-toolchain
```

Current value:

```text
leanprover/lean4:v4.30.0
```

Mathlib is pinned by:

```text
colean_mathlib/lake-manifest.json
```

## Local LLM Models

The local experiments use Ollama model names:

```text
qwen2.5-coder:1.5b
qwen2.5-coder:7b
```

Reproduce locally:

```powershell
ollama pull qwen2.5-coder:1.5b
ollama pull qwen2.5-coder:7b
```

Then run:

```powershell
$env:COLEAN_LOCAL_MODEL = "qwen2.5-coder:1.5b"
python colean_v0\local_llm_generator.py

$env:COLEAN_LOCAL_MODEL = "qwen2.5-coder:7b"
python colean_v0\local_llm_generator.py
```

## Why Model Binaries Are Not In Git

Ollama model files are large binary artifacts. They should not be committed into
the source repository because they make clone/pull operations slow and brittle.

The preferred strategy is:

```text
source code: git
model identity/version: git
model binary: Ollama pull, GitHub Releases, or Git LFS if a fixed artifact is needed
```

## Future Release Assets

When the system needs frozen reproducibility, use GitHub Releases for:

```text
benchmark result bundles
fixed model manifests
Mathlib retrieval indexes
small generated datasets
```

Use Git LFS only if a large artifact must be versioned with source history.

