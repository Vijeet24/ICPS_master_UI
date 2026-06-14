# Start ICPS Master UI (FastAPI)
Set-Location $PSScriptRoot

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — set DATABASE_URL before first run."
    Write-Host "Local Postgres (no Docker): .\scripts\setup_local_db.ps1 -PostgresPassword YOUR_PASSWORD"
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

Write-Host "Starting server at http://127.0.0.1:8000"
.\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
