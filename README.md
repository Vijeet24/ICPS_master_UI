# ICPS Master UI

Product, brand, and category management UI connected to PostgreSQL.

## Features

- **Products**: view, create, edit, and delete with mandatory field validation
- **Brands**: separate brand table and management screen
- **Categories / Subcategories**: hierarchical category management (e.g. Sensors → Oxygen sensor)
- **PostgreSQL sync**: all UI changes persist to the database; use Refresh to reload from DB

## Quick start

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Install Python dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000).

> **Note:** PostgreSQL runs on host port **5434** to avoid conflicts with a local PostgreSQL installation.

## API

| Endpoint | Methods |
|----------|---------|
| `/api/products` | GET, POST |
| `/api/products/{id}` | GET, PUT, DELETE |
| `/api/brands` | GET, POST |
| `/api/brands/{id}` | GET, PUT, DELETE |
| `/api/categories` | GET, POST |
| `/api/categories/{id}` | GET, PUT, DELETE |
| `/api/subcategories` | GET, POST |
| `/api/subcategories/{id}` | GET, PUT, DELETE |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Product fields

| UI label | Field | Required |
|----------|-------|----------|
| GTIN-14 | `gtin_14` | Yes |
| Product name | `product_name` | Yes |
| Description | `description` | No |
| Category | `category_id` + `sub_category_id` | No |
| Unit of measure | `unit_of_measure` | Yes |
| Default price | `default_price` | No |
| Currency | `currency` | Yes |
| Brand Name | `brand_id` (references brands) | Yes |
| GS1 Digital Link | `gs1_digital_link` | No |

## Deploy online (free)

This app needs a **web host** (FastAPI) and a **PostgreSQL database**. Both have free tiers.

### Step 1 — Push to GitHub

```bash
git add .
git commit -m "Initial ICPS Master UI"
git push -u origin main
```

### Step 2 — Free PostgreSQL (Neon)

1. Sign up at [neon.tech](https://neon.tech) (free tier).
2. Create a project and database named `icps_master`.
3. Copy the **connection string** (add `?sslmode=require` if not present).

### Step 3 — Free web hosting (Render)

1. Sign up at [render.com](https://render.com) with your GitHub account.
2. **New → Blueprint** → select the `ICPS_master_UI` repository.
3. When asked for `DATABASE_URL`, paste your Neon connection string.
4. Click **Apply** — Render builds the Docker image and deploys.

Your live URL will look like: `https://icps-master-ui.onrender.com`

> **Free tier notes:** Render free services sleep after ~15 minutes of inactivity (first load may take ~30s). Neon free tier is sufficient for development and demos.

### Alternative: run locally with Docker

```bash
docker compose up -d
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
