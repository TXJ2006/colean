$ErrorActionPreference = "Stop"

$models = @(
  "qwen2.5-coder:1.5b",
  "qwen2.5-coder:7b"
)

foreach ($model in $models) {
  Write-Host "Pulling $model"
  ollama pull $model
}

Write-Host "Installed Ollama models:"
ollama list

