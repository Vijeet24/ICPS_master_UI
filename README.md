# ICPS Master UI

Product, brand, and category management UI connected to PostgreSQL, plus a **Seller EDI workflow** dashboard for the 850 → 855 → 856 supply chain simulation.

## Features

- **Products**: view, create, edit, and delete with mandatory field validation
- **Brands**: separate brand table and management screen
- **Categories / Subcategories**: hierarchical category management (e.g. Sensors → Oxygen sensor)
- **Seller Workflow**: monitor purchase orders, EDI acknowledgements, shipments, and message audit trail
- **MQTT integration**: receive EDI 850 on MQTT, publish 855/856 responses (configurable)
- **PostgreSQL sync**: all UI changes persist to the database; use Refresh to reload from DB

## Quick start

### 1. Database (pick one)

**Recommended — local PostgreSQL (no Docker)**

You already have PostgreSQL installed on port **5432**. Run once:

```powershell
.\scripts\setup_local_db.ps1 -PostgresPassword YOUR_POSTGRES_PASSWORD
```

Copy the printed `DATABASE_URL` into your `.env` file.

**Alternative — Docker** (only if Docker Desktop is fully running)

```bash
docker compose up -d
```

Use `DATABASE_URL=postgresql://icps:icps_secret@127.0.0.1:5434/icps_master` in `.env`.

**Alternative — Neon cloud** (free, no Docker)

Sign up at [neon.tech](https://neon.tech), create a database, and paste the connection string into `.env`.

#### Docker error: `502 Bad Gateway` or `dockerDesktopLinuxEngine` not found

Docker Desktop is not running or still starting. Either:

1. Open **Docker Desktop** from the Start menu, wait until it shows **Engine running** (1–2 minutes), then retry `docker compose up -d`, or
2. Skip Docker and use local PostgreSQL (recommended on this machine) — see above.

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

Open [http://localhost:8000](http://localhost:8000) and open the **Seller Workflow** tab.

## Seller workflow (850 → 855 → 856)

The app acts as a **Seller** in a supply chain simulation:

1. **Receive PO (EDI 850)** — MQTT topic `rfid/1514032003830/1514250054321/edi/850`
2. **Send Acknowledgement (EDI 855)** — published to `rfid/1514250054321/1514032003830/edi/855`
3. **Fulfillment** — configurable delay (`FULFILLMENT_MODE`, `FULFILLMENT_DELAY_SECONDS`)
4. **Send ASN (EDI 856)** — published to `rfid/1514250054321/1514032003830/edi/856`

### Seller Workflow UI

- Summary cards by order status
- MQTT connection indicator
- Purchase order table with status badges
- Message audit log (inbound/outbound EDI)
- Order detail modal with workflow timeline, line items, and raw JSON
- **Simulate PO (850)** button for local testing without MQTT
- Auto-refresh every 5 seconds (toggle on/off)

### Sample messages

See the `samples/` folder:

- `inbound_850.json` — Purchase Order
- `outbound_855.json` — Purchase Order Acknowledgement
- `outbound_856.json` — Advance Ship Notice

### Environment variables (seller workflow)

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_ENABLED` | `true` | Enable MQTT subscriber/publisher |
| `MQTT_BROKER` | `207.246.121.211` | MQTT broker host |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_SUBSCRIBE_TOPIC` | `rfid/.../edi/850` | Inbound PO topic |
| `MQTT_ACK_TOPIC` | `rfid/.../edi/855` | Outbound acknowledgement topic |
| `MQTT_ASN_TOPIC` | `rfid/.../edi/856` | Outbound ASN topic |
| `FULFILLMENT_MODE` | `simulated` | `immediate`, `scheduled`, or `simulated` |
| `FULFILLMENT_DELAY_SECONDS` | `5` | Delay before shipping (non-immediate modes) |

Copy `.env.example` to `.env` and adjust as needed.

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
| `/api/orders` | GET |
| `/api/orders/stats` | GET |
| `/api/orders/mqtt-status` | GET |
| `/api/orders/audit` | GET |
| `/api/orders/sample/purchase-order` | GET |
| `/api/orders/simulate` | POST |
| `/api/orders/{id}` | GET |
| `/api/orders/{id}/audit` | GET |
| `/api/orders/{id}/ship` | POST |

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

## Tests

```bash
pytest
```

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
