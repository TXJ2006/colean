$ErrorActionPreference = "Stop"

$models = @(
  "qwen2.5-coder:1.5b",
  "qwen2.5-coder:7b"
)

foreach ($model in $models) {
  Write-Host "Running CoLean local LLM benchmark with $model"
  $env:COLEAN_LOCAL_MODEL = $model
  python colean_v0\local_llm_generator.py
}

python colean_v0\failure_recovery_analyzer.py

