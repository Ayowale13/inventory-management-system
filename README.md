# Store Inventory Management System

A production-ready inventory management system built with Flask 3, SQLAlchemy, Flask-Login, and Bootstrap 5. Supports SQLite (development) and PostgreSQL (production).

## Features

- **Authentication & Roles** — Admin and Staff, secure password hashing, sessions, RBAC
- **Dashboard** — KPIs, charts, recent activity, low/out-of-stock alerts
- **Products** — Full CRUD, search, filter, category
- **Real-time Inventory** — Atomic sales (`stock − qty`) and restocks (`stock + qty`); stock can never go negative
- **Sales & Restock Records** — Permanent, queryable history
- **Dynamic Custom Fields** — Add/Edit/Delete/Hide/Reorder without changing the schema
- **Reports** — Daily / Weekly / Monthly sales, low stock, inventory snapshot. Export as CSV / Excel / PDF
- **Activity Logs** — Full audit trail
- **REST API** — JSON endpoints for products, sales, restocks
- **CSRF protection, input validation, flash notifications, professional UI**

## Project structure

```
inventory-system/
├── app/
│   ├── __init__.py            # Application factory
│   ├── models/                # SQLAlchemy models
│   ├── routes/                # Blueprints (auth, products, sales, …)
│   ├── services/              # Business logic (inventory_service, report_service)
│   ├── utils/                 # forms, decorators, cli, logger
│   ├── templates/             # Jinja2 templates
│   └── static/                # CSS / JS / images
├── migrations/                # Flask-Migrate (auto-generated)
├── instance/                  # SQLite DB lives here (dev)
├── deployment/                # gunicorn.conf.py, nginx.conf, systemd unit
├── run.py
├── config.py
├── requirements.txt
├── .env.example
└── README.md
```

## Installation (local / VS Code)

```bash
# 1. Clone & enter
cd inventory-system

# 2. Create virtualenv
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template and edit
cp .env.example .env
# (set SECRET_KEY to a long random string)

# 5. Initialize the database
flask --app run.py db init        # only first time
flask --app run.py db migrate -m "init"
flask --app run.py db upgrade

# 6. Seed demo data (creates admin/admin123 and staff/staff123 + sample products)
flask --app run.py seed

# 7. Run
flask --app run.py run            # http://127.0.0.1:5000
# or
python run.py
```

### Create your own admin instead of using the seed

```bash
flask --app run.py create-admin
```

## Environment variables (`.env`)

| Key            | Example                                          | Notes                  |
|----------------|--------------------------------------------------|------------------------|
| `FLASK_APP`    | `run.py`                                         | Required by Flask CLI  |
| `FLASK_ENV`    | `development` or `production`                    |                        |
| `SECRET_KEY`   | `a-long-random-string`                           | Required               |
| `DATABASE_URL` | `sqlite:///instance/inventory.db`                | SQLite (dev) default   |
|                | `postgresql://user:pass@localhost:5432/inventory`| PostgreSQL (prod)      |

## Default logins (after `flask seed`)

- **Admin:** `admin` / `admin123`
- **Staff:** `staff` / `staff123`

Change them immediately in a real deployment.

## REST API

All endpoints require a valid session cookie (login first via `/auth/login`).

| Method | Path             | Description                                 |
|--------|------------------|---------------------------------------------|
| GET    | `/api/products`  | List products (supports `?q=`)              |
| POST   | `/api/sales`     | `{ "product_id": 1, "quantity": 3 }`        |
| POST   | `/api/restocks`  | Admin only — `{ "product_id": 1, "quantity_added": 50 }` |

## Deployment (Ubuntu VPS, Nginx + Gunicorn + systemd)

```bash
# 1. System packages
sudo apt update && sudo apt install -y python3 python3-venv python3-pip nginx postgresql

# 2. Clone into /var/www/inventory-system, create venv, install deps
cd /var/www/inventory-system
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Configure .env (use PostgreSQL DATABASE_URL, real SECRET_KEY)
cp .env.example .env && nano .env

# 4. DB migrations
flask --app run.py db upgrade
flask --app run.py create-admin

# 5. Log directory
sudo mkdir -p /var/log/inventory && sudo chown www-data:www-data /var/log/inventory

# 6. systemd
sudo cp deployment/inventory.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now inventory

# 7. Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/inventory
sudo ln -s /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 8. HTTPS (recommended)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## License

MIT — use freely for academic / commercial projects.
