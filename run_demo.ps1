$ErrorActionPreference = "Stop"
$env:DEMO_MODE = "true"

python "backend/analysis/main.py"
