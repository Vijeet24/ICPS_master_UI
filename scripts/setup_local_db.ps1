# One-time setup for local PostgreSQL (no Docker)
param(
    [string]$PostgresPassword
)

Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    .\.venv\Scripts\pip install psycopg2-binary
}

if ($PostgresPassword) {
    $env:POSTGRES_ADMIN_PASSWORD = $PostgresPassword
}

.\.venv\Scripts\python scripts/setup_local_db.py
