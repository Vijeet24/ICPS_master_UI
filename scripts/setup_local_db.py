"""Create icps database and user on local PostgreSQL (no Docker required)."""

import os
import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = "icps_master"
DB_USER = "icps"
DB_PASSWORD = "icps_secret"


def get_admin_url() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    env_url = os.getenv("POSTGRES_ADMIN_URL")
    if env_url:
        return env_url
    password = os.getenv("POSTGRES_ADMIN_PASSWORD")
    if password:
        return f"postgresql://postgres:{password}@127.0.0.1:5432/postgres"
    print("Usage:")
    print("  python scripts/setup_local_db.py postgresql://postgres:YOUR_PASSWORD@127.0.0.1:5432/postgres")
    print("  set POSTGRES_ADMIN_PASSWORD=YOUR_PASSWORD && python scripts/setup_local_db.py")
    sys.exit(1)


def main() -> None:
    admin_url = get_admin_url()
    conn = psycopg2.connect(admin_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (DB_USER,))
    if not cur.fetchone():
        cur.execute(f"CREATE USER {DB_USER} WITH PASSWORD %s", (DB_PASSWORD,))
        print(f"Created user '{DB_USER}'")
    else:
        cur.execute(f"ALTER USER {DB_USER} WITH PASSWORD %s", (DB_PASSWORD,))
        print(f"Updated password for user '{DB_USER}'")

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE {DB_NAME} OWNER {DB_USER}')
        print(f"Created database '{DB_NAME}'")
    else:
        print(f"Database '{DB_NAME}' already exists")

    cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}")
    cur.close()
    conn.close()

    app_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@127.0.0.1:5432/{DB_NAME}"
    print()
    print("Done. Add this to your .env file:")
    print(f"DATABASE_URL={app_url}")


if __name__ == "__main__":
    main()
