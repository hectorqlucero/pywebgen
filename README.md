# PyWebGen - Parameter-Driven Web Application Framework

**A complete Python port of the Clojure webgen Leiningen template.**

## Features

### 1. Standalone Projects
Generated projects are completely independent - they don't depend on pywebgen package.

### 2. Parameter-Driven CRUD
Define entities in YAML files, get automatic CRUD operations:
```yaml
entity: products
title: Products
table: products
fields:
  - id: name
    label: Name
    type: text
    required: true
  - id: price
    label: Price
    type: decimal
```

### 3. MVC Handlers (for the 20%)
```
handlers/
├── home/
│   ├── controller.py
│   ├── model.py
│   └── view.py
└── dashboard/
    ├── controller.py
    ├── model.py
    └── view.py
```

### 4. TabGrid Interface
All entities use a tabbed interface with:
- Parent record detail view
- Subgrids for child entities
- DataTables with sorting, filtering, pagination
- Modal record selection

### 5. Theme Selector
24 Bootswatch themes available via dropdown:
- Cerulean, Cosmo, Cyborg, Darkly, Flatly, Journal, Litera, Lumen, Lux, Materia, Minty, Morph, Pulse, Quartz, Sandstone, Simplex, Sketchy, Slate, Solar, Spacelab, United, Vapor, Zephyr, and Default
- Theme persisted in localStorage
- No flash of unthemed content (preload class)

### 6. Working i18n
- English and Spanish translations
- DataTables internationalization (pagination, search, etc.)
- Language persisted in session
- Active language highlighted in dropdown

### 7. Scaffold Command
Run inside the generated project:
```bash
python manage.py scaffold products
python manage.py scaffold --all
```

### 8. Multi-Database Migrations
SQLite, MySQL, and PostgreSQL specific migration files:
```
resources/migrations/
├── 001-users.sqlite.up.sql
├── 001-users.sqlite.down.sql
├── 001-users.mysql.up.sql
├── 001-users.mysql.down.sql
├── 001-users.postgresql.up.sql
└── 001-users.postgresql.down.sql
```

### 9. Database Seeding
```bash
python manage.py seed
```

### 10. Hooks for Business Logic
- `before_save` - Validate/transform before saving
- `after_save` - Post-save operations
- `before_load` - Pre-load transformations
- `after_load` - Transform data after loading
- `before_delete` - Pre-delete validation
- `after_delete` - Post-delete cleanup

## Quick Start

### Install PyWebGen
```bash
cd /path/to/pywebgen
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Create a New Project
```bash
pywebgen new myapp --path /path/to/projects
cd /path/to/projects/myapp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py run
```

Then visit: http://localhost:5000

### Default Users
| Email | Password | Level |
|-------|----------|-------|
| user@example.com | user | U (User) |
| admin@example.com | admin | A (Admin) |
| system@example.com | system | S (System) |

## Project Structure

```
myapp/
├── app.py                  # Flask app factory
├── config.py               # Configuration loader
├── config.yaml             # Application configuration
├── models.py               # SQLAlchemy models
├── menu.py                 # Custom menu configuration
├── manage.py               # CLI commands
├── requirements.txt
├── handlers/               # MVC for custom code
│   ├── home/
│   │   ├── controller.py
│   │   ├── model.py
│   │   └── view.py
│   ├── dashboard/
│   └── reports/
├── hooks/                  # Entity lifecycle hooks
│   └── products.py
├── routes/                 # Route blueprints
│   ├── auth.py             # Login/logout
│   ├── home.py             # Home page
│   ├── admin.py            # CRUD admin
│   ├── i18n.py             # Language switching
│   ├── custom.py           # Your manual routes
│   └── __init__.py
├── engine/                 # Framework core
│   ├── __init__.py         # EntityConfigManager
│   ├── crud.py             # CRUD operations
│   ├── query.py            # Query operations
│   ├── render.py           # Form/grid rendering
│   ├── scaffold.py         # Scaffold generator
│   └── menu.py             # Auto-menu generation
├── i18n/                   # Internationalization
│   ├── __init__.py
│   └── translations stored in resources/i18n/
├── resources/
│   ├── config/
│   │   └── app-config.yaml
│   ├── entities/           # Entity YAML configs
│   │   ├── users.yaml
│   │   └── products.yaml
│   ├── i18n/               # Translation files
│   │   ├── en.yaml
│   │   └── es.yaml
│   ├── migrations/         # SQL migrations
│   │   ├── 001-users.sqlite.up.sql
│   │   └── ...
│   └── public/             # Static assets
│       ├── vendor/
│       ├── js/
│       ├── css/
│       └── images/
├── templates/
│   ├── base.html           # Base template with theme/i18n
│   ├── layouts/
│   ├── partials/
│   ├── admin/
│   │   └── entity.html
│   └── handlers/
├── db/
│   └── myapp.sqlite
└── uploads/                # File uploads
```

## CLI Commands (inside generated project)

```bash
python manage.py run              # Start development server
python manage.py migrate          # Run pending migrations
python manage.py rollback         # Rollback last migration
python manage.py seed             # Seed database with demo data
python manage.py scaffold <table> # Scaffold entity from database
python manage.py scaffold --all   # Scaffold all tables
python manage.py routes           # List all routes
```

## Entity Configuration

### Basic Entity
```yaml
# resources/entities/products.yaml
entity: products
title: Products
table: products
connection: default
rights:
  - U
  - A
  - S
mode: parameter-driven

fields:
  - id: id
    label: ID
    type: hidden
  - id: name
    label: Product Name
    type: text
    required: true
    placeholder: Enter product name
  - id: description
    label: Description
    type: textarea
  - id: price
    label: Price
    type: number
  - id: category_id
    label: Category
    type: select
    options:
      - value: "1"
        label: Electronics
      - value: "2"
        label: Clothing
  - id: active
    label: Active
    type: checkbox
  - id: image
    label: Image
    type: file

actions:
  new: true
  edit: true
  delete: true

hooks:
  before_save: hooks.products.before_save
  after_load: hooks.products.after_load
```

### Entity with Subgrids
```yaml
# resources/entities/contactos.yaml
entity: contactos
title: Contactos
table: contactos

fields:
  - id: firstname
    label: First Name
    type: text
    required: true
  - id: lastname
    label: Last Name
    type: text
  - id: email
    label: Email
    type: email

subgrids:
  - entity: cars
    title: Cars
    foreign_key: contacto_id
    icon: bi bi-car-front
  - entity: siblings
    title: Siblings
    foreign_key: contacto_id
    icon: bi bi-people-fill
```

### Child Entity (Hidden from Menu)
```yaml
# resources/entities/cars.yaml
entity: cars
title: Cars
table: cars
menu_hidden: true  # Don't show in main menu

fields:
  - id: contacto_id
    label: Contacto
    type: hidden
  - id: make
    label: Make
    type: text
  - id: model
    label: Model
    type: text
  - id: year
    label: Year
    type: number
```

## Field Types

| Type | Description |
|------|-------------|
| `text` | Text input |
| `email` | Email input |
| `password` | Password input |
| `number` | Number input |
| `date` | Date picker |
| `textarea` | Multi-line text |
| `select` | Dropdown select |
| `radio` | Radio buttons |
| `checkbox` | Checkbox (T/F) |
| `file` | File upload (images) |
| `hidden` | Hidden field |

## Hooks (Business Logic)

```python
# hooks/products.py

def before_save(data: dict) -> dict:
    """Validate and transform before saving.
    Return {"errors": {...}} to cancel save.
    """
    if not data.get("name"):
        return {"errors": {"name": "Name is required"}}
    
    # Handle file upload
    if "image" in data and hasattr(data["image"], "filename"):
        data["file"] = data.pop("image")
    
    # Transform data
    data["name"] = data["name"].strip().title()
    
    return data


def after_load(rows: list) -> list:
    """Transform after loading from database."""
    for row in rows:
        # Add image URL
        if row.get("image"):
            row["image"] = f"/uploads/{row['image']}"
        
        # Add computed fields
        row["full_name"] = f"{row.get('firstname', '')} {row.get('lastname', '')}"
    
    return rows


def before_delete(data: dict) -> dict:
    """Validate before delete. Return errors to cancel."""
    # Check dependencies
    if data.get("has_orders"):
        return {"errors": {"id": "Cannot delete product with orders"}}
    return {"success": True}


def after_delete(data: dict) -> dict:
    """Cleanup after delete."""
    # Delete associated files
    if data.get("image"):
        import os
        os.remove(f"uploads/{data['image']}")
    return {"success": True}
```

## Menu Configuration

```python
# menu.py
from engine.menu import get_auto_menu_config

# Custom nav links (shown before entity links)
custom_nav_links = [
    {"label": "Dashboard", "href": "/dashboard", "icon": "bi-speedometer2"},
]

# Custom dropdowns
custom_dropdowns = {
    "Reports": [
        {"label": "Sales Report", "href": "/reports/sales", "icon": "bi-file-earmark-text"},
        {"label": "Inventory", "href": "/reports/inventory", "icon": "bi-box"},
    ],
}

def get_menu_config():
    auto = get_auto_menu_config()
    return {
        "nav_links": custom_nav_links + auto.get("nav_links", []),
        "dropdowns": {**custom_dropdowns, **auto.get("dropdowns", {})}
    }
```

## MVC Handlers (Custom Code)

For the 20% that doesn't fit parameter-driven:

```python
# handlers/dashboard/controller.py
from flask import render_template, request
from handlers.dashboard.model import get_stats, get_recent_orders
from handlers.dashboard.view import render_dashboard

def dashboard():
    stats = get_stats()
    recent_orders = get_recent_orders(limit=10)
    content = render_dashboard(stats, recent_orders)
    return render_template("handlers/dashboard/view.html", 
                          title="Dashboard", 
                          content=content)
```

```python
# handlers/dashboard/model.py
from models import db

def get_stats():
    return {
        "users": db.session.execute("SELECT COUNT(*) FROM users").scalar(),
        "orders": db.session.execute("SELECT COUNT(*) FROM orders").scalar(),
        "revenue": db.session.execute("SELECT COALESCE(SUM(total), 0) FROM orders").scalar(),
    }

def get_recent_orders(limit=10):
    return db.session.execute(
        f"SELECT * FROM orders ORDER BY created_at DESC LIMIT {limit}"
    ).fetchall()
```

```python
# handlers/dashboard/view.py
def render_dashboard(stats, recent_orders):
    return f"""
    <div class="row">
        <div class="col-md-4">
            <div class="card text-white bg-primary">
                <div class="card-body">
                    <h5>Users</h5>
                    <h2>{stats['users']}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-white bg-success">
                <div class="card-body">
                    <h5>Orders</h5>
                    <h2>{stats['orders']}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-white bg-info">
                <div class="card-body">
                    <h5>Revenue</h5>
                    <h2>${stats['revenue']:,.2f}</h2>
                </div>
            </div>
        </div>
    </div>
    """
```

## Manual Routes

```python
# routes/custom.py
from flask import Blueprint, render_template

custom_bp = Blueprint("custom", __name__)

@custom_bp.route("/dashboard")
def dashboard():
    from handlers.dashboard.controller import dashboard
    return dashboard()

@custom_bp.route("/reports/sales")
def sales_report():
    return render_template("handlers/reports/sales.html")
```

## Migrations

Database-specific SQL files:

```sql
-- resources/migrations/001-users.sqlite.up.sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lastname TEXT,
  firstname TEXT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email TEXT,
  level TEXT DEFAULT 'U',
  active TEXT DEFAULT 'T',
  last_login TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_users_username ON users(username);
```

```sql
-- resources/migrations/001-users.mysql.up.sql
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lastname VARCHAR(255),
  firstname VARCHAR(255),
  username VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  level CHAR(1) DEFAULT 'U',
  active CHAR(1) DEFAULT 'T',
  last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_users_username (username)
);
```

## Configuration

```yaml
# config.yaml
app:
  session_timeout: 28800
  default_locale: es
  cookie_name: LS
  max_file_size_mb: 5

database:
  error_codes:
    postgres:
      unique: "23505"
      fk: "23503"
    mysql:
      unique: 1062
      fk: 1451
    sqlite:
      unique: "UNIQUE constraint failed"
      fk: "foreign key constraint failed"

ui:
  themes:
    - cerulean
    - cosmo
    - cyborg
    - darkly
    - flatly
    - sketchy
    - slate
  default_theme: sketchy

security:
  session_secret_key: "change-me-in-production"

connections:
  sqlite:
    db_type: sqlite
    db_name: db/myapp.sqlite
  mysql:
    db_type: mysql
    db_name: "//localhost:3306/myapp"
    db_user: root
    db_pwd: ""
  postgresql:
    db_type: postgresql
    db_name: "//localhost:5432/myapp"
    db_user: postgres
    db_pwd: ""
  default: sqlite

site_name: "My App"
company_name: "My Company"
port: 5000
uploads: "./uploads/"
path: "/uploads/"
max_upload_mb: 5
allowed_image_exts:
  - jpg
  - jpeg
  - png
  - gif
  - bmp
  - webp
```

## User Levels

| Level | Code | Description |
|-------|------|-------------|
| User | U | Basic user access |
| Administrator | A | Full admin access |
| System | S | System/super admin |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/{entity}/` | List/view entity |
| GET | `/admin/{entity}/add-form/` | Get new record form |
| GET | `/admin/{entity}/edit-form/{id}` | Get edit form |
| POST | `/admin/{entity}/save` | Save record |
| GET | `/admin/{entity}/delete/{id}` | Delete record |
| GET | `/admin/subgrid` | Get subgrid data (JSON) |

## Best Practices

1. Use hooks for business logic, not routes
2. Validate in `before_save` - return `{"errors": {...}}` to cancel
3. Transform data in `after_load` - add computed fields
4. Set `menu_hidden: true` for child entities
5. Use appropriate Bootstrap icons
6. Restrict rights appropriately per entity
7. Use migrations for schema changes
8. Keep handlers thin - logic in model, presentation in view

## Bootstrap Icons Reference

| Entity | Icon |
|--------|------|
| Users | `bi bi-people` |
| Contactos | `bi bi-person-lines-fill` |
| Cars | `bi bi-car-front` |
| Products | `bi bi-box` |
| Orders | `bi bi-cart` |
| Reports | `bi bi-file-earmark-text` |
| Dashboard | `bi bi-speedometer2` |
| Settings | `bi bi-gear` |
| Home | `bi bi-house` |

## License

MIT License
