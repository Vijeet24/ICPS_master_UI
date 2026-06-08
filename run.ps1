# Start ICPS Master UI (PostgreSQL + FastAPI)
Set-Location $PSScriptRoot

if (-not (docker ps -q -f name=icps_postgres)) {
    Write-Host "Starting PostgreSQL..."
    docker compose up -d
    Start-Sleep -Seconds 5
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

Write-Host "Starting server at http://127.0.0.1:8000"
.\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
