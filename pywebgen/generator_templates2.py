"""
PyWebGen Project Templates - Part 2

Routes, Engine, Handlers, and Templates
"""

from pathlib import Path


# Import from part 1
from pywebgen.generator_templates import (
    REQUIREMENTS_TXT, get_config_yaml, CONFIG_PY, MODELS_PY, get_app_py,
    EN_I18N, ES_I18N
)

GITIGNORE = """__pycache__/
*.py[cod]
*$py.class
.env
.venv
venv/
*.sqlite
*.db
db/
uploads/
.idea/
.vscode/
.pytest_cache/
.coverage
htmlcov/
"""


# =============================================================================
# I18N MODULE
# =============================================================================

I18N_INIT = '''"""
Internationalization (i18n) Support
"""
from typing import Any, Optional
from pathlib import Path
import yaml
from flask import Flask
from config import get_locale


SUPPORTED_LOCALES = {
    "en": {"name": "English", "flag": "🇺🇸"},
    "es": {"name": "Español", "flag": "🇲🇽"},
}


class I18N:
    _translations: dict[str, dict[str, Any]] = {}
    
    @classmethod
    def init_app(cls, app: Flask) -> None:
        cls.load_translations()
    
    @classmethod
    def load_translations(cls, path: str = "resources/i18n") -> None:
        i18n_path = Path(path)
        if not i18n_path.exists():
            return
        for file_path in i18n_path.glob("*.yaml"):
            locale = file_path.stem
            with open(file_path, "r") as f:
                cls._translations[locale] = yaml.safe_load(f) or {}
    
    @classmethod
    def translate(cls, key: str, locale: Optional[str] = None, **kwargs) -> str:
        locale = locale or get_locale()
        translations = cls._translations.get(locale, {})
        
        keys = key.split(".")
        value = translations
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return key
            if value is None:
                return key
        
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return value if isinstance(value, str) else key


def tr(key: str, **kwargs) -> str:
    return I18N.translate(key, **kwargs)
'''


# =============================================================================
# MENU MODULE
# =============================================================================

MENU_PY = '''"""
Menu Configuration

Auto-generated from entity configs with manual overrides.
"""
from engine.menu import get_auto_menu_config


# Define menu order here - items not listed appear at the end
def get_menu_order():
    return [
        ("DASHBOARD", "/dashboard", "bi-speedometer2"),  # Custom item
        ("Contactos", None, None),  # From entity (href/icon auto-filled)
        ("Reports", None, None),    # Dropdown
        ("Users", None, None),      # From entity
    ]


# Custom dropdown items
custom_dropdowns = {
    "Reports": [
        {"label": "Contactos", "href": "/reports/contactos", "icon": "bi-file-earmark-text"},
    ],
}


def get_menu_config():
    """Returns the complete menu configuration with ordering."""
    auto = get_auto_menu_config()
    order_list = get_menu_order()
    
    # Build ordered nav links
    ordered_nav = []
    auto_nav = {item["label"]: item for item in auto.get("nav_links", [])}
    
    for label, href, icon in order_list:
        if label in auto_nav:
            ordered_nav.append(auto_nav[label])
        elif href:
            ordered_nav.append({"label": label, "href": href, "icon": icon})
    
    # Add any auto items not in order list
    for item in auto.get("nav_links", []):
        if item["label"] not in [o[0] for o in order_list]:
            ordered_nav.append(item)
    
    # Merge dropdowns
    all_dropdowns = {**auto.get("dropdowns", {}), **custom_dropdowns}
    
    # Reorder dropdowns according to order_list
    ordered_dropdowns = {}
    for label, _, _ in order_list:
        if label in all_dropdowns:
            ordered_dropdowns[label] = all_dropdowns[label]
    for label, items in all_dropdowns.items():
        if label not in ordered_dropdowns:
            ordered_dropdowns[label] = items
    
    return {
        "nav_links": ordered_nav,
        "dropdowns": ordered_dropdowns,
    }
'''


# =============================================================================
# ROUTES
# =============================================================================

ROUTES_AUTH = '''"""
Authentication Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import validate_csrf

from models import db, User
from i18n import tr


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.main"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = db.session.query(User).filter(User.username == username).first()
        
        if user and password and user.check_password(password):
            if user.active == "T":
                login_user(user)
                return redirect(url_for("home.main"))
            else:
                flash(tr("auth.invalid_credentials"), "danger")
        else:
            flash(tr("auth.invalid_credentials"), "danger")
    
    return render_template("auth/login.html", title=tr("auth.login"))


@auth_bp.route("/logoff")
@login_required
def logoff():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            flash(tr("error.general"), "danger")
            return render_template("auth/change_password.html", title=tr("auth.change_password"))
        
        user = db.session.query(User).filter(User.email == email).first()
        
        if user and user.active == "T":
            user.set_password(password)
            db.session.commit()
            flash(tr("success.updated"), "success")
            return redirect(url_for("auth.login"))
        else:
            flash(tr("error.not_found"), "danger")
    
    return render_template("auth/change_password.html", title=tr("auth.change_password"))
'''


ROUTES_HOME = '''"""
Home Routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user


home_bp = Blueprint("home", __name__)


@home_bp.route("/home")
@login_required
def main():
    return render_template("home/main.html", title="Home")
'''


def get_home_main_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="bi bi-house me-2"></i>Welcome, {{ current_user.firstname or current_user.username }}!</h4>
            </div>
            <div class="card-body">
                <p class="lead">This is your dashboard. Use the navigation menu to manage your data.</p>
                <hr>
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <i class="bi bi-people display-4 text-primary"></i>
                                <h5 class="mt-2">Users</h5>
                                <p class="text-muted">Manage system users</p>
                                <a href="/admin/users/" class="btn btn-outline-primary btn-sm">View Users</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <i class="bi bi-person-lines-fill display-4 text-primary"></i>
                                <h5 class="mt-2">Contactos</h5>
                                <p class="text-muted">Manage contacts</p>
                                <a href="/admin/contactos/" class="btn btn-outline-primary btn-sm">View Contactos</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <i class="bi bi-gear display-4 text-primary"></i>
                                <h5 class="mt-2">Settings</h5>
                                <p class="text-muted">System configuration</p>
                                <a href="#" class="btn btn-outline-secondary btn-sm disabled">Coming Soon</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card shadow">
            <div class="card-header bg-secondary text-white">
                <h5 class="mb-0"><i class="bi bi-info-circle me-2"></i>Quick Info</h5>
            </div>
            <div class="card-body">
                <ul class="list-unstyled mb-0">
                    <li><strong>Username:</strong> {{ current_user.username }}</li>
                    <li><strong>Email:</strong> {{ current_user.email or 'N/A' }}</li>
                    <li><strong>Level:</strong> 
                        {% if current_user.level == 'A' %}Admin
                        {% elif current_user.level == 'S' %}System
                        {% else %}User{% endif %}
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''


ROUTES_I18N = '''"""
i18n Routes - Language Switching
"""
from flask import Blueprint, redirect, request
from config import set_locale


i18n_bp = Blueprint("i18n", __name__)


@i18n_bp.route("/set-language/<locale>")
def set_language(locale: str):
    set_locale(locale)
    next_url = request.args.get("next") or request.referrer or "/"
    return redirect(next_url)
'''


ROUTES_CUSTOM = '''"""
Custom Routes

Add your manual routes here for the 20% that doesn\'t fit parameter-driven.
"""
from flask import Blueprint, render_template
from flask_login import login_required


custom_bp = Blueprint("custom", __name__)


@custom_bp.route("/dashboard")
@login_required
def dashboard():
    from handlers.dashboard.controller import main
    return main()


@custom_bp.route("/reports/contactos")
@login_required
def contactos_report():
    from handlers.reports.controller import contactos
    return contactos()
'''


ROUTES_ADMIN = '''"""
Admin Routes - Dynamic Entity CRUD
"""
from typing import Optional
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf

from engine import EntityConfigManager
from engine.crud import save_record, delete_record
from engine.query import list_records, get_record
from engine.render import render_form, render_grid, render_error, render_tabbed_view
from i18n import tr


admin_bp = Blueprint("admin", __name__)


def check_permission(entity: str) -> bool:
    config = EntityConfigManager.get(entity)
    if not config:
        return False
    return current_user.level in config.rights


@admin_bp.route("/<entity>/")
@login_required
def grid(entity: str):
    if not check_permission(entity):
        return render_template("base.html", content=render_error(tr("error.unauthorized")))
    
    config = EntityConfigManager.get(entity)
    selected_id = request.args.get("id", type=int)
    current_tab = request.args.get("tab", "")
    
    content = render_tabbed_view(entity, selected_id, current_tab)
    
    return render_template("admin/entity.html", title=config.title, content=content)


@admin_bp.route("/<entity>/add-form/", methods=["GET"])
@admin_bp.route("/<entity>/add-form/<int:parent_id>", methods=["GET"])
@login_required
def add_form(entity: str, parent_id: Optional[int] = None):
    if not check_permission(entity):
        return render_error(tr("error.unauthorized"))
    
    row = {}
    parent_entity = request.args.get("parent_entity", "")
    
    if parent_id:
        config = EntityConfigManager.get(entity)
        for field in config.fields:
            if field.type == "hidden" and field.id != "id":
                row[field.id] = parent_id
    
    from flask_wtf.csrf import generate_csrf
    return render_form(entity, row, generate_csrf(), parent_entity, parent_id)


@admin_bp.route("/<entity>/edit-form/<int:record_id>", methods=["GET"])
@login_required
def edit_form(entity: str, record_id: int):
    if not check_permission(entity):
        return render_error(tr("error.unauthorized"))
    
    row = get_record(entity, record_id)
    if not row:
        return render_error(tr("error.not_found"))
    
    parent_entity = request.args.get("parent_entity", "")
    parent_id = request.args.get("parent_id", type=int)
    
    from flask_wtf.csrf import generate_csrf
    return render_form(entity, row, generate_csrf(), parent_entity, parent_id)


@admin_bp.route("/<entity>/save", methods=["POST"])
@login_required
def save(entity: str):
    if not check_permission(entity):
        return jsonify({"ok": False, "error": tr("error.unauthorized")}), 403
    
    data = request.form.to_dict()
    files = request.files
    data.pop("csrf_token", None)
    redirect_url = data.pop("_redirect_url", None)
    
    result = save_record(entity, data, files, current_user.id)
    
    if result.get("success"):
        new_id = result.get("id")
        if redirect_url:
            pass
        elif new_id:
            redirect_url = f"/admin/{entity}?id={new_id}"
        else:
            redirect_url = f"/admin/{entity}"
        return jsonify({"ok": True, "redirect": redirect_url, "id": new_id})
    return jsonify({"ok": False, "errors": result.get("errors", result.get("error"))}), 400


@admin_bp.route("/<entity>/delete/<int:record_id>")
@login_required
def delete(entity: str, record_id: int):
    if not check_permission(entity):
        flash(tr("error.unauthorized"), "danger")
        return redirect(url_for("admin.grid", entity=entity))
    
    result = delete_record(entity, record_id, current_user.id)
    
    if result.get("success"):
        flash(tr("success.deleted"), "success")
    else:
        flash(result.get("error", tr("error.general")), "danger")
    
    parent_entity = request.args.get("parent_entity", "")
    parent_id = request.args.get("parent_id", type=int)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(result)
    
    if parent_entity and parent_id:
        return redirect(url_for("admin.grid", entity=parent_entity, id=parent_id))
    return redirect(url_for("admin.grid", entity=entity))


@admin_bp.route("/subgrid")
@login_required
def subgrid():
    entity = request.args.get("entity")
    parent_id = request.args.get("parent_id", type=int)
    foreign_key = request.args.get("foreign_key")
    
    if not entity:
        return jsonify({"success": False, "error": "Entity required"}), 400
    
    if not check_permission(entity):
        return jsonify({"success": False, "error": tr("error.unauthorized")}), 403
    
    config = EntityConfigManager.get(entity)
    if not config:
        return jsonify({"success": False, "error": "Entity not found"}), 404
    
    rows = list_records(entity, parent_id=parent_id, foreign_key=foreign_key)
    
    fields = {}
    field_options = {}
    field_types = {}
    for field in config.get_display_fields():
        fields[field.id] = field.label
        field_types[field.id] = field.type
        if field.options:
            field_options[field.id] = {str(opt.get("value", "")): opt.get("label", "") for opt in field.options}
    
    return jsonify({
        "success": True,
        "rows": rows,
        "fields": fields,
        "field_types": field_types,
        "field_options": field_options,
        "actions": config.actions
    })
'''


# =============================================================================
# ENGINE MODULE
# =============================================================================

ENGINE_INIT = '''"""
Entity Configuration Engine
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from pathlib import Path
import yaml


@dataclass
class FieldConfig:
    id: str
    label: str
    type: str
    required: bool = False
    placeholder: Optional[str] = None
    options: list = field(default_factory=list)
    hidden_in_grid: bool = False
    hidden_in_form: bool = False
    grid_only: bool = False
    fk: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "FieldConfig":
        return cls(
            id=data.get("id", ""),
            label=data.get("label", ""),
            type=data.get("type", "text"),
            required=data.get("required", False),
            placeholder=data.get("placeholder"),
            options=data.get("options", []),
            hidden_in_grid=data.get("hidden_in_grid", False),
            hidden_in_form=data.get("hidden_in_form", False),
            grid_only=data.get("grid_only", False),
            fk=data.get("fk"),
        )


@dataclass
class SubgridConfig:
    entity: str
    title: str
    foreign_key: str
    icon: str = "bi bi-list-ul"
    label: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> "SubgridConfig":
        return cls(
            entity=data.get("entity", ""),
            title=data.get("title", ""),
            foreign_key=data.get("foreign_key", ""),
            icon=data.get("icon", "bi bi-list-ul"),
            label=data.get("label", data.get("title", "")),
        )


@dataclass
class EntityConfig:
    entity: str
    title: str
    table: str
    connection: str = "default"
    rights: list = field(default_factory=lambda: ["U", "A", "S"])
    menu_category: Optional[str] = None
    menu_order: int = 999
    menu_hidden: bool = False
    fields: list = field(default_factory=list)
    queries: dict = field(default_factory=dict)
    actions: dict = field(default_factory=lambda: {"new": True, "edit": True, "delete": True})
    hooks: dict = field(default_factory=dict)
    subgrids: list = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "EntityConfig":
        fields = [FieldConfig.from_dict(f) for f in data.get("fields", [])]
        subgrids = [SubgridConfig.from_dict(s) for s in data.get("subgrids", [])]
        return cls(
            entity=data.get("entity", ""),
            title=data.get("title", ""),
            table=data.get("table", ""),
            connection=data.get("connection", "default"),
            rights=data.get("rights", ["U", "A", "S"]),
            menu_category=data.get("menu_category"),
            menu_order=data.get("menu_order", 999),
            menu_hidden=data.get("menu_hidden", False),
            fields=fields,
            queries=data.get("queries", {}),
            actions=data.get("actions", {"new": True, "edit": True, "delete": True}),
            hooks=data.get("hooks", {}),
            subgrids=subgrids,
        )
    
    def get_display_fields(self) -> list:
        return [f for f in self.fields if f.type not in ("hidden", "password") and not f.hidden_in_grid][:8]
    
    def get_form_fields(self) -> list:
        return [f for f in self.fields if not f.grid_only and not f.hidden_in_form]


class EntityConfigManager:
    _configs: dict = {}
    _hooks: dict = {}
    
    @classmethod
    def load_all(cls, path: str = "resources/entities") -> None:
        entities_path = Path(path)
        if not entities_path.exists():
            return
        for file_path in entities_path.glob("*.yaml"):
            cls.load_file(file_path)
    
    @classmethod
    def load_file(cls, file_path: Path) -> None:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        if data:
            config = EntityConfig.from_dict(data)
            cls._configs[config.entity] = config
            cls._load_hooks(config)
    
    @classmethod
    def _load_hooks(cls, config: EntityConfig) -> None:
        hook_functions = {}
        for hook_name, hook_path in config.hooks.items():
            func = cls._resolve_hook(hook_path)
            if func:
                hook_functions[hook_name] = func
        if hook_functions:
            cls._hooks[config.entity] = hook_functions
    
    @classmethod
    def _resolve_hook(cls, hook_path: str):
        try:
            module_path, func_name = hook_path.rsplit(".", 1)
            import importlib
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        except (ImportError, AttributeError, ValueError):
            return None
    
    @classmethod
    def get(cls, entity: str):
        return cls._configs.get(entity)
    
    @classmethod
    def get_all(cls) -> dict:
        return cls._configs.copy()
    
    @classmethod
    def get_hook(cls, entity: str, hook_name: str):
        return cls._hooks.get(entity, {}).get(hook_name)
    
    @classmethod
    def list_entities(cls) -> list:
        return sorted(cls._configs.keys())
'''


ENGINE_MENU = '''"""
Menu Generation from Entity Configs
"""
from engine import EntityConfigManager


ENTITY_ICONS = {
    "users": "bi bi-people",
    "contactos": "bi bi-person-lines-fill",
    "cars": "bi bi-car-front",
    "siblings": "bi bi-people-fill",
}


def get_auto_menu_config() -> dict:
    """Generate menu configuration from entity configs."""
    entities = EntityConfigManager.get_all()
    
    nav_links = []
    dropdowns = {}
    
    for name, cfg in entities.items():
        if getattr(cfg, 'menu_hidden', False):
            continue
        
        icon = ENTITY_ICONS.get(name, "bi bi-folder")
        menu_order = getattr(cfg, 'menu_order', 999)
        
        item = {
            "label": cfg.title,
            "href": f"/admin/{name}/",
            "icon": icon,
            "order": menu_order,
        }
        
        category = getattr(cfg, 'menu_category', None)
        if category:
            if category not in dropdowns:
                dropdowns[category] = {"items": [], "order": menu_order}
            dropdowns[category]["items"].append(item)
        else:
            nav_links.append(item)
    
    # Sort nav_links by order
    nav_links.sort(key=lambda x: x.get("order", 999))
    
    # Sort dropdown items and dropdowns themselves
    for category in dropdowns:
        dropdowns[category]["items"].sort(key=lambda x: x.get("order", 999))
    
    return {
        "nav_links": nav_links,
        "dropdowns": dropdowns,
    }
'''


def get_engine_crud() -> str:
    return '''"""
Engine CRUD - Create, Read, Update, Delete Operations
"""
from typing import Any, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from models import db
from engine import EntityConfigManager
from config import config


def execute_hook(entity: str, hook_name: str, data: Any) -> Any:
    hook = EntityConfigManager.get_hook(entity, hook_name)
    if hook:
        try:
            return hook(data)
        except Exception as e:
            print(f"[ERROR] Hook {hook_name} failed: {e}")
    return data


def get_model_class(table_name: str):
    from models import User, Contactos, Cars, Siblings
    models = {
        "users": User,
        "contactos": Contactos,
        "cars": Cars,
        "siblings": Siblings,
    }
    return models.get(table_name)


def save_record(entity: str, data: dict, files: Optional[dict] = None, user_id: Optional[int] = None) -> dict:
    cfg = EntityConfigManager.get(entity)
    if not cfg:
        return {"success": False, "error": "Entity not found"}
    
    data = execute_hook(entity, "before_save", data)
    if isinstance(data, dict) and "errors" in data:
        return {"success": False, "errors": data["errors"]}
    
    model_class = get_model_class(cfg.table)
    if not model_class:
        return {"success": False, "error": "Model not found"}
    
    record_id = data.get("id")
    
    try:
        if record_id:
            record = db.session.get(model_class, record_id)
            if not record:
                return {"success": False, "error": "Record not found"}
            
            for key, value in data.items():
                if key != "id" and hasattr(record, key):
                    setattr(record, key, value)
            
            if files:
                for field_name, file in files.items():
                    if file and isinstance(file, FileStorage) and file.filename:
                        filename = handle_file_upload(file, cfg.table, record.id)
                        if filename and hasattr(record, field_name):
                            setattr(record, field_name, filename)
        else:
            record = model_class()
            for key, value in data.items():
                if key != "id" and hasattr(record, key):
                    setattr(record, key, value)
            db.session.add(record)
            db.session.flush()
            
            if files:
                for field_name, file in files.items():
                    if file and isinstance(file, FileStorage) and file.filename:
                        filename = handle_file_upload(file, cfg.table, record.id)
                        if filename and hasattr(record, field_name):
                            setattr(record, field_name, filename)
        
        db.session.commit()
        db.session.refresh(record)
        
        execute_hook(entity, "after_save", {"id": record.id, "data": data})
        
        return {"success": True, "id": record.id}
    
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}


def delete_record(entity: str, record_id: int, user_id: Optional[int] = None) -> dict:
    cfg = EntityConfigManager.get(entity)
    if not cfg:
        return {"success": False, "error": "Entity not found"}
    
    execute_hook(entity, "before_delete", {"id": record_id})
    
    model_class = get_model_class(cfg.table)
    if not model_class:
        return {"success": False, "error": "Model not found"}
    
    try:
        record = db.session.get(model_class, record_id)
        if not record:
            return {"success": False, "error": "Record not found"}
        
        db.session.delete(record)
        db.session.commit()
        
        execute_hook(entity, "after_delete", {"id": record_id})
        
        return {"success": True}
    
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}


def handle_file_upload(file: FileStorage, table: str, record_id: int) -> Optional[str]:
    if not file or not file.filename:
        return None
    
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in config.allowed_image_extensions:
        return None
    
    filename = secure_filename(f"{table}_{record_id}.{ext}")
    upload_path = config.uploads_path
    
    import os
    os.makedirs(upload_path, exist_ok=True)
    
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    
    return filename
'''


def get_engine_query() -> str:
    return '''"""
Engine Query - Data Query Operations
"""
from typing import Optional, Any
from sqlalchemy import text

from models import db
from engine import EntityConfigManager


def get_model_class(table_name: str):
    from models import User, Contactos, Cars, Siblings
    return {
        "users": User,
        "contactos": Contactos,
        "cars": Cars,
        "siblings": Siblings,
    }.get(table_name)


def execute_hook(entity: str, hook_name: str, data) -> Any:
    hook = EntityConfigManager.get_hook(entity, hook_name)
    if hook:
        try:
            return hook(data)
        except Exception as e:
            print(f"[ERROR] Hook {hook_name} failed: {e}")
    return data


def list_records(entity: str, parent_id: Optional[int] = None, parent_entity: Optional[str] = None, foreign_key: Optional[str] = None) -> list[dict]:
    cfg = EntityConfigManager.get(entity)
    if not cfg:
        return []
    
    execute_hook(entity, "before_load", {"entity": entity})
    
    model_class = get_model_class(cfg.table)
    if not model_class:
        return []
    
    query = cfg.queries.get("list")
    
    if query:
        if parent_id and foreign_key:
            query = query.replace("ORDER BY", f"WHERE {foreign_key} = {parent_id} ORDER BY")
        
        result = db.session.execute(text(query))
        rows = [dict(row._mapping) for row in result]
    else:
        if parent_id and foreign_key:
            records = db.session.query(model_class).filter(
                getattr(model_class, foreign_key) == parent_id
            ).all()
        else:
            records = db.session.query(model_class).all()
        
        rows = [{c.name: getattr(r, c.name) for c in model_class.__table__.columns} for r in records]
    
    rows = execute_hook(entity, "after_load", rows)
    
    return rows if isinstance(rows, list) else []


def get_record(entity: str, record_id: int) -> Optional[dict]:
    cfg = EntityConfigManager.get(entity)
    if not cfg:
        return None
    
    model_class = get_model_class(cfg.table)
    if not model_class:
        return None
    
    query = cfg.queries.get("get")
    
    if query:
        result = db.session.execute(text(query), {"id": record_id})
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return None
    else:
        record = db.session.get(model_class, record_id)
        if record:
            return {c.name: getattr(record, c.name) for c in model_class.__table__.columns}
        return None
'''


def get_engine_render() -> str:
    from pathlib import Path
    template_path = Path(__file__).parent / "engine_render_template.py"
    return template_path.read_text()


def get_engine_scaffold(project_name: str) -> str:
    return f'''"""
Engine Scaffold - Generate entity configurations and hooks from database tables
"""
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml

from sqlalchemy import inspect
from models import db


SQL_TYPE_MAP = {{
    "VARCHAR": "text", "CHAR": "text", "TEXT": "textarea",
    "INT": "number", "INTEGER": "number", "BIGINT": "number",
    "DECIMAL": "number", "FLOAT": "number", "DOUBLE": "number",
    "DATE": "date", "DATETIME": "datetime", "TIMESTAMP": "datetime",
    "BOOLEAN": "checkbox", "BOOL": "checkbox",
    "BLOB": "file", "BYTEA": "file",
}}


def detect_field_type(column_info: dict) -> str:
    sql_type = (column_info.get("type") or "TEXT").upper()
    column_name = column_info.get("name", "").lower()
    
    if re.search(r"email|mail", column_name): return "email"
    if re.search(r"password|passwd|pwd", column_name): return "password"
    if re.search(r"image|photo|picture|img", column_name): return "file"
    if re.search(r"description|comment|note|memo", column_name): return "textarea"
    
    base_type = sql_type.split("(")[0]
    return SQL_TYPE_MAP.get(base_type, "text")


def humanize_label(field_name: str) -> str:
    return " ".join(word.capitalize() for word in field_name.replace("_", " ").split())


def class_name(table_name: str) -> str:
    return "".join(word.capitalize() for word in table_name.split("_"))


def get_table_columns(table_name: str) -> list[dict]:
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    return [{{"name": c["name"], "type": str(c["type"]), "nullable": c.get("nullable", True), "primary": c.get("primary_key", False)}} for c in columns]


def get_foreign_keys(table_name: str) -> list[dict]:
    inspector = inspect(db.engine)
    fks = inspector.get_foreign_keys(table_name)
    return [{{"column": fk["constrained_columns"][0], "referred_table": fk["referred_table"]}} for fk in fks]


def get_all_tables() -> list[str]:
    inspector = inspect(db.engine)
    return inspector.get_table_names()


def get_child_tables(table_name: str) -> list[dict]:
    """Find tables that have foreign keys pointing to this table."""
    inspector = inspect(db.engine)
    all_tables = inspector.get_table_names()
    child_tables = []
    
    for tbl in all_tables:
        if tbl == table_name:
            continue
        fks = inspector.get_foreign_keys(tbl)
        for fk in fks:
            if fk["referred_table"] == table_name:
                child_tables.append({{
                    "table": tbl,
                    "foreign_key": fk["constrained_columns"][0]
                }})
                break
    
    return child_tables


def generate_subgrids(table_name: str) -> list[dict]:
    """Generate subgrid configurations for child tables."""
    child_tables = get_child_tables(table_name)
    subgrids = []
    
    for child in child_tables:
        child_name = child["table"]
        fk_column = child["foreign_key"]
        
        subgrid = {{
            "entity": child_name,
            "title": humanize_label(child_name),
            "icon": "bi-folder" if "car" not in child_name.lower() else "bi-car-front",
            "foreign_key": fk_column
        }}
        
        # Set appropriate icons
        if "sibling" in child_name.lower():
            subgrid["icon"] = "bi-people"
        elif "car" in child_name.lower():
            subgrid["icon"] = "bi-car-front"
        
        subgrids.append(subgrid)
    
    return subgrids


def generate_field(column: dict, fks: list[dict]) -> dict:
    col_name = column["name"]
    col_type = detect_field_type(column)
    
    if col_name == "id":
        return {{"id": "id", "label": "ID", "type": "hidden"}}
    
    fk = next((f for f in fks if f["column"] == col_name), None)
    if fk:
        return {{"id": col_name, "label": humanize_label(fk["referred_table"]) + " ID", "type": "hidden"}}
    
    field = {{"id": col_name, "label": humanize_label(col_name), "type": col_type, "required": not column.get("nullable", True)}}
    if col_type in ("text", "textarea", "email"):
        field["placeholder"] = humanize_label(col_name) + "..."
    return field


def generate_queries(table_name: str) -> dict:
    return {{
        "list": f"SELECT * FROM {{table_name}} ORDER BY id DESC",
        "get": f"SELECT * FROM {{table_name}} WHERE id = :id"
    }}


def generate_hooks(table_name: str, columns: list[dict], fks: list[dict]) -> str:
    file_fields = [c for c in columns if detect_field_type(c) == "file"]
    cls_name = class_name(table_name)
    
    if not file_fields:
        hooks = '"""\\n'
        hooks += 'Business logic hooks for ' + table_name + ' entity\\n'
        hooks += '"""\\n'
        hooks += 'def before_load(params):\\n    return params\\n\\n'
        hooks += 'def after_load(rows):\\n    return rows\\n\\n'
        hooks += 'def before_save(data):\\n    return data\\n\\n'
        hooks += 'def after_save(result):\\n    return result\\n\\n'
        hooks += 'def before_delete(entity_id):\\n    return {{"success": True}}\\n\\n'
        hooks += 'def after_delete(entity_id):\\n    return {{"success": True}}\\n'
        return hooks
    
    file_field_names = [f["name"] for f in file_fields]
    
    hooks = '"""\\n'
    hooks += 'Business logic hooks for ' + table_name + ' entity\\n'
    hooks += '"""\\n'
    hooks += 'import os\\n'
    hooks += 'from werkzeug.utils import secure_filename\\n'
    hooks += 'from config import config\\n'
    hooks += 'from models import db, ' + cls_name + '\\n\\n'
    hooks += 'def before_load(params):\\n    return params\\n\\n'
    hooks += 'def after_load(rows):\\n    return rows\\n\\n'
    hooks += 'def before_save(data):\\n    return data\\n\\n'
    hooks += 'def after_save(result):\\n'
    hooks += '    """Handle file uploads after save"""\\n'
    hooks += '    if not result.get("id"):\\n        return result\\n'
    hooks += '    record = db.session.get(' + cls_name + ', result["id"])\\n'
    hooks += '    if not record:\\n        return result\\n'
    hooks += '    files = result.get("data", {{}}).get("_files", {{}})\\n'
    hooks += '    for field_name, file in files.items():\\n'
    hooks += '        if file and file.filename:\\n'
    hooks += '            ext = file.filename.rsplit(".", 1)[-1].lower()\\n'
    hooks += '            if ext in config.allowed_image_extensions:\\n'
    hooks += '                filename = secure_filename("' + table_name + '_{{}}.{{}}".format(record.id, ext))\\n'
    hooks += '                os.makedirs(config.uploads_path, exist_ok=True)\\n'
    hooks += '                file.save(os.path.join(config.uploads_path, filename))\\n'
    hooks += '                setattr(record, field_name, filename)\\n'
    hooks += '    db.session.commit()\\n'
    hooks += '    return result\\n\\n'
    hooks += 'def before_delete(entity_id):\\n    return {{"success": True}}\\n\\n'
    hooks += 'def after_delete(entity_id):\\n'
    hooks += '    """Clean up uploaded files on delete"""\\n'
    for ff in file_field_names:
        hooks += '    record = db.session.get(' + cls_name + ', entity_id)\\n'
        hooks += '    if record and record.' + ff + ':\\n'
        hooks += '        try:\\n'
        hooks += '            os.remove(os.path.join(config.uploads_path, record.' + ff + '))\\n'
        hooks += '        except:\\n            pass\\n'
    hooks += '    return {{"success": True}}\\n'
    
    return hooks


def scaffold_table(table_name: str, force: bool = False) -> str:
    try:
        columns = get_table_columns(table_name)
        fks = get_foreign_keys(table_name)
        fields = [generate_field(col, fks) for col in columns]
        queries = generate_queries(table_name)
        
        # Determine if this is a child table (has foreign keys)
        is_child_table = len(fks) > 0
        
        # Generate entity config
        config = {{
            "entity": table_name,
            "title": humanize_label(table_name),
            "table": table_name,
            "connection": "default",
            "rights": ["U", "A", "S"],
            "fields": fields,
            "queries": queries,
            "actions": {{"new": True, "edit": True, "delete": True}},
        }}
        
        # Add menu_hidden for child tables
        if is_child_table:
            config["menu_hidden"] = True
        
        # Add subgrids for parent tables (tables with children)
        subgrids = generate_subgrids(table_name)
        if subgrids:
            config["subgrids"] = subgrids
        
        entity_path = Path(f"resources/entities/{{table_name}}.yaml")
        if entity_path.exists() and not force:
            entity_result = f"Skipping {{table_name}} entity (already exists)"
        else:
            entity_path.parent.mkdir(parents=True, exist_ok=True)
            with open(entity_path, "w") as f:
                f.write(f"# Generated {{datetime.now().isoformat()}}\\n")
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            entity_result = f"Created: {{entity_path}}"
        
        # Generate hooks
        hooks_code = generate_hooks(table_name, columns, fks)
        hooks_path = Path(f"hooks/{{table_name}}.py")
        
        if hooks_path.exists() and not force:
            hooks_result = f"Skipping {{table_name}} hooks (already exists)"
        else:
            hooks_path.parent.mkdir(parents=True, exist_ok=True)
            hooks_path.write_text(hooks_code)
            hooks_result = f"Created: {{hooks_path}}"
        
        return f"{{entity_result}}\\n  {{hooks_result}}"
    
    except Exception as e:
        return f"Failed: {{e}}"


def scaffold_all(force: bool = False, exclude: list = None) -> None:
    exclude = exclude or []
    tables = [t for t in get_all_tables() if t not in exclude and not t.startswith(("sqlite_", "pg_", "mysql_"))]
    print(f"Scaffolding {{len(tables)}} tables...")
    for table in tables:
        result = scaffold_table(table, force)
        print(f"  {{result}}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("table", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.all:
        scaffold_all(args.force)
    elif args.table:
        print(scaffold_table(args.table, args.force))
'''


MIGRATIONS = {
    "users_sqlite_up": """CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lastname TEXT,
  firstname TEXT,
  username TEXT UNIQUE,
  password TEXT,
  dob TEXT,
  cell TEXT,
  phone TEXT,
  fax TEXT,
  email TEXT,
  level TEXT,
  active TEXT,
  imagen TEXT,
  last_login TEXT DEFAULT (datetime('now'))
);""",
    "users_sqlite_down": "DROP TABLE IF EXISTS users;",
    "users_mysql_up": """CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lastname VARCHAR(255),
  firstname VARCHAR(255),
  username VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  dob DATE,
  cell VARCHAR(50),
  phone VARCHAR(50),
  fax VARCHAR(50),
  email VARCHAR(255),
  level CHAR(1),
  active CHAR(1),
  imagen VARCHAR(255),
  last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    "users_mysql_down": "DROP TABLE IF EXISTS users;",
    "users_postgresql_up": """CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  lastname VARCHAR(255),
  firstname VARCHAR(255),
  username VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  dob DATE,
  cell VARCHAR(50),
  phone VARCHAR(50),
  fax VARCHAR(50),
  email VARCHAR(255),
  level CHAR(1),
  active CHAR(1),
  imagen VARCHAR(255),
  last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    "users_postgresql_down": "DROP TABLE IF EXISTS users;",
    "users_view_sqlite_up": """CREATE VIEW IF NOT EXISTS users_view AS
SELECT id, lastname, firstname, username, dob, cell, phone, fax, email, level, active, imagen, last_login,
    strftime('%d/%m/%Y', dob) as dob_formatted,
    CASE WHEN level = 'U' THEN 'Usuario' WHEN level = 'A' THEN 'Administrador' ELSE 'Sistema' END as level_formatted,
    CASE WHEN active = 'T' THEN 'Activo' ELSE 'Inactivo' END as active_formatted
FROM users ORDER BY lastname, firstname;""",
    "users_view_sqlite_down": "DROP VIEW IF EXISTS users_view;",
    "contactos_sqlite_up": """CREATE TABLE IF NOT EXISTS contactos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT,
  phone TEXT,
  imagen TEXT
);""",
    "contactos_sqlite_down": "DROP TABLE IF EXISTS contactos;",
    "siblings_sqlite_up": """CREATE TABLE IF NOT EXISTS siblings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  age INTEGER,
  imagen TEXT,
  contacto_id INTEGER,
  FOREIGN KEY (contacto_id) REFERENCES contactos(id) ON DELETE CASCADE
);""",
    "siblings_sqlite_down": "DROP TABLE IF EXISTS siblings;",
    "cars_sqlite_up": """CREATE TABLE IF NOT EXISTS cars (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company TEXT,
  model TEXT,
  year INTEGER,
  imagen TEXT,
  contacto_id INTEGER,
  FOREIGN KEY (contacto_id) REFERENCES contactos(id) ON DELETE CASCADE
);""",
    "cars_sqlite_down": "DROP TABLE IF EXISTS cars;",
}


def write_migrations(project_path: Path) -> None:
    """Write migration SQL files for SQLite, MySQL, PostgreSQL."""
    mig_dir = project_path / "resources/migrations"
    mig_dir.mkdir(parents=True, exist_ok=True)
    
    migrations = [
        ("001-users", "sqlite", "up", MIGRATIONS["users_sqlite_up"]),
        ("001-users", "sqlite", "down", MIGRATIONS["users_sqlite_down"]),
        ("001-users", "mysql", "up", MIGRATIONS["users_mysql_up"]),
        ("001-users", "mysql", "down", MIGRATIONS["users_mysql_down"]),
        ("001-users", "postgresql", "up", MIGRATIONS["users_postgresql_up"]),
        ("001-users", "postgresql", "down", MIGRATIONS["users_postgresql_down"]),
        ("002-users_view", "sqlite", "up", MIGRATIONS["users_view_sqlite_up"]),
        ("002-users_view", "sqlite", "down", MIGRATIONS["users_view_sqlite_down"]),
        ("003-contactos", "sqlite", "up", MIGRATIONS["contactos_sqlite_up"]),
        ("003-contactos", "sqlite", "down", MIGRATIONS["contactos_sqlite_down"]),
        ("004-siblings", "sqlite", "up", MIGRATIONS["siblings_sqlite_up"]),
        ("004-siblings", "sqlite", "down", MIGRATIONS["siblings_sqlite_down"]),
        ("005-cars", "sqlite", "up", MIGRATIONS["cars_sqlite_up"]),
        ("005-cars", "sqlite", "down", MIGRATIONS["cars_sqlite_down"]),
    ]
    
    for name, db_type, direction, sql in migrations:
        filename = f"{name}.{db_type}.{direction}.sql"
        (mig_dir / filename).write_text(sql)


def get_users_entity_yaml() -> str:
    return """entity: users
title: Users
table: users
connection: default
rights:
  - U
  - A
  - S
fields:
  - id: id
    label: ID
    type: hidden
  - id: lastname
    label: Lastname
    type: text
    placeholder: Lastname...
  - id: firstname
    label: Firstname
    type: text
    placeholder: Firstname...
  - id: username
    label: Username
    type: text
    placeholder: Username...
  - id: dob
    label: Dob
    type: date
  - id: cell
    label: Cell
    type: text
  - id: phone
    label: Phone
    type: text
  - id: email
    label: Email
    type: email
    placeholder: user@example.com
  - id: level
    label: Level
    type: select
    options:
      - value: ""
        label: Select Level
      - value: U
        label: User
      - value: A
        label: Administrator
      - value: S
        label: System
  - id: active
    label: Active
    type: radio
    options:
      - value: T
        label: Active
      - value: F
        label: Inactive
queries:
  list: SELECT * FROM users ORDER BY id DESC
  get: SELECT * FROM users WHERE id = :id
actions:
  new: true
  edit: true
  delete: true
"""


def get_contactos_entity_yaml() -> str:
    return """entity: contactos
title: Contactos
table: contactos
connection: default
rights:
  - U
  - A
  - S
fields:
  - id: id
    label: ID
    type: hidden
  - id: name
    label: Name
    type: text
    placeholder: Name...
  - id: email
    label: Email
    type: email
  - id: phone
    label: Phone
    type: text
  - id: imagen
    label: Imagen
    type: file
queries:
  list: SELECT * FROM contactos ORDER BY id DESC
  get: SELECT * FROM contactos WHERE id = :id
actions:
  new: true
  edit: true
  delete: true
hooks:
  before_save: hooks.contactos.before_save
  after_load: hooks.contactos.after_load
subgrids:
  - entity: cars
    title: Cars
    foreign_key: contacto_id
    icon: bi bi-list-ul
    label: Cars
  - entity: siblings
    title: Siblings
    foreign_key: contacto_id
    icon: bi bi-list-ul
    label: Siblings
"""


def get_siblings_entity_yaml() -> str:
    return """entity: siblings
title: Siblings
table: siblings
connection: default
rights:
  - U
  - A
  - S
menu_hidden: true
fields:
  - id: id
    label: ID
    type: hidden
  - id: name
    label: Name
    type: text
  - id: age
    label: Age
    type: number
  - id: imagen
    label: Imagen
    type: file
  - id: contacto_id
    label: Contactos ID
    type: hidden
queries:
  list: SELECT * FROM siblings ORDER BY id DESC
  get: SELECT * FROM siblings WHERE id = :id
actions:
  new: true
  edit: true
  delete: true
"""


def get_cars_entity_yaml() -> str:
    return """entity: cars
title: Cars
table: cars
connection: default
rights:
  - U
  - A
  - S
menu_hidden: true
fields:
  - id: id
    label: ID
    type: hidden
  - id: company
    label: Company
    type: text
  - id: model
    label: Model
    type: text
  - id: year
    label: Year
    type: number
  - id: imagen
    label: Imagen
    type: file
  - id: contacto_id
    label: Contactos ID
    type: hidden
queries:
  list: SELECT * FROM cars ORDER BY id DESC
  get: SELECT * FROM cars WHERE id = :id
actions:
  new: true
  edit: true
  delete: true
"""


def write_entity_configs(project_path: Path) -> None:
    """Write entity YAML configuration files."""
    entity_dir = project_path / "resources/entities"
    entity_dir.mkdir(parents=True, exist_ok=True)
    
    (entity_dir / "users.yaml").write_text(get_users_entity_yaml())
    (entity_dir / "contactos.yaml").write_text(get_contactos_entity_yaml())
    (entity_dir / "siblings.yaml").write_text(get_siblings_entity_yaml())
    (entity_dir / "cars.yaml").write_text(get_cars_entity_yaml())


def get_users_hooks_py() -> str:
    return '''"""
Business logic hooks for users entity
"""
def before_load(params):
    print(f"[INFO] Loading users with params: {params}")
    return params

def after_load(rows):
    print(f"[INFO] Loaded {len(rows)} users record(s)")
    return rows

def before_save(data):
    print("[INFO] Saving users...")
    return data

def after_save(entity_id, data):
    print(f"[INFO] Users saved successfully. ID: {entity_id}")
    return {"success": True}

def before_delete(entity_id):
    print(f"[INFO] Checking if users can be deleted. ID: {entity_id}")
    return {"success": True}

def after_delete(entity_id):
    print(f"[INFO] Users deleted successfully. ID: {entity_id}")
    return {"success": True}
'''


def get_contactos_hooks_py() -> str:
    return '''"""
Business logic hooks for contactos entity
"""
def before_load(params):
    print(f"[INFO] Loading contactos with params: {params}")
    return params

def after_load(rows):
    print(f"[INFO] Loaded {len(rows)} contactos record(s)")
    for row in rows:
        if row.get("imagen"):
            row["imagen"] = f"/uploads/{row['imagen']}"
    return rows

def before_save(data):
    print("[INFO] Saving contactos...")
    return data

def after_save(entity_id, data):
    print(f"[INFO] Contactos saved successfully. ID: {entity_id}")
    return {"success": True}

def before_delete(entity_id):
    print(f"[INFO] Checking if contactos can be deleted. ID: {entity_id}")
    return {"success": True}

def after_delete(entity_id):
    print(f"[INFO] Contactos deleted successfully. ID: {entity_id}")
    return {"success": True}
'''


def get_cars_hooks_py() -> str:
    return '''"""
Business logic hooks for cars entity
"""
def before_load(params):
    return params

def after_load(rows):
    for row in rows:
        if row.get("imagen"):
            row["imagen"] = f"/uploads/{row['imagen']}"
    return rows

def before_save(data):
    return data

def after_save(entity_id, data):
    return {"success": True}

def before_delete(entity_id):
    return {"success": True}

def after_delete(entity_id):
    return {"success": True}
'''


def get_siblings_hooks_py() -> str:
    return '''"""
Business logic hooks for siblings entity
"""
def before_load(params):
    return params

def after_load(rows):
    for row in rows:
        if row.get("imagen"):
            row["imagen"] = f"/uploads/{row['imagen']}"
    return rows

def before_save(data):
    return data

def after_save(entity_id, data):
    return {"success": True}

def before_delete(entity_id):
    return {"success": True}

def after_delete(entity_id):
    return {"success": True}
'''


def write_hooks(project_path: Path) -> None:
    """Write hook stub files for entities."""
    hooks_dir = project_path / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    (hooks_dir / "__init__.py").write_text("")
    (hooks_dir / "users.py").write_text(get_users_hooks_py())
    (hooks_dir / "contactos.py").write_text(get_contactos_hooks_py())
    (hooks_dir / "cars.py").write_text(get_cars_hooks_py())
    (hooks_dir / "siblings.py").write_text(get_siblings_hooks_py())


def get_home_controller_py(project_name: str) -> str:
    return f'''"""
Home Handler Controller
"""
from flask import render_template
from flask_login import current_user

def main():
    if current_user.is_authenticated:
        return render_template("home/main.html", title="Home")
    return render_template("home/welcome.html", title="Welcome")
'''


def get_home_model_py(project_name: str) -> str:
    return f'''"""
Home Handler Model
"""
from models import db, User

def get_user(username: str):
    return db.session.query(User).filter(User.username == username).first()

def update_password(username: str, hashed_password: str) -> bool:
    user = get_user(username)
    if user:
        user.password = hashed_password
        db.session.commit()
        return True
    return False
'''


def get_home_view_py(project_name: str) -> str:
    return f'''"""
Home Handler View
"""
def home_view():
    return """
    <div class="container mt-5">
        <div class="text-center">
            <h1 class="text-info">Welcome</h1>
            <p class="text-muted">Serving the community since 2024</p>
        </div>
    </div>
    """
'''


def get_dashboard_controller_py(project_name: str) -> str:
    return f'''"""
Dashboard Handler Controller
"""
from flask import render_template
from handlers.dashboard.model import get_stats


def main():
    title = "DASHBOARD"
    stats = get_stats()
    return render_template("dashboard/main.html", title=title, stats=stats)
'''


def get_dashboard_model_py(project_name: str) -> str:
    return f'''"""
Dashboard Handler Model
"""
from sqlalchemy import text
from models import db


def get_total(table: str) -> int:
    result = db.session.execute(text(f"SELECT COUNT(*) as count FROM {{table}}"))
    row = result.fetchone()
    return row.count if row else 0


def get_stats() -> dict:
    return {{
        "total_contactos": get_total("contactos"),
        "total_siblings": get_total("siblings"),
        "total_cars": get_total("cars"),
        "total_users": get_total("users"),
    }}
'''


def get_dashboard_view_py(project_name: str) -> str:
    return f'''"""
Dashboard Handler View
"""
def dashboard_html(title: str, stats: dict) -> str:
    return f"""
    <div class="container text-center w-50">
        <h1 class="text-primary">{{title}}</h1>
        <div class="card-group">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title text-primary">Contactos</h5>
                    <p class="card-text">{{stats['total_contactos']}}</p>
                </div>
            </div>
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title text-primary">Siblings</h5>
                    <p class="card-text">{{stats['total_siblings']}}</p>
                </div>
            </div>
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title text-primary">Cars</h5>
                    <p class="card-text">{{stats['total_cars']}}</p>
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-body">
                <h5 class="card-title text-primary">Users</h5>
                <p class="card-text">{{stats['total_users']}}</p>
            </div>
        </div>
    </div>
    """
'''


def get_reports_controller_py(project_name: str) -> str:
    return f'''"""
Reports Handler Controller
"""
from flask import render_template
from handlers.reports.model import get_contactos
from handlers.reports.view import contactos_view


def contactos():
    title = "Reporte de Contactos"
    rows = get_contactos()
    content, extra_js = contactos_view(title=title, rows=rows)
    return render_template("reports/dashboard.html", title=title, content=content, extra_js=extra_js)
'''


def get_reports_model_py(project_name: str) -> str:
    return f'''"""
Reports Handler Model
"""
from sqlalchemy import text
from models import db


def get_contactos() -> list[dict]:
    result = db.session.execute(text("SELECT * FROM contactos"))
    rows = [dict(row._mapping) for row in result]
    
    for row in rows:
        contacto_id = row["id"]
        
        siblings_result = db.session.execute(
            text("SELECT name FROM siblings WHERE contacto_id = :id"),
            {{"id": contacto_id}}
        )
        row["siblings"] = ", ".join([r.name for r in siblings_result])
        
        cars_result = db.session.execute(
            text("SELECT company || ' ' || model || ' ' || year as car FROM cars WHERE contacto_id = :id"),
            {{"id": contacto_id}}
        )
        row["cars"] = ", ".join([r.car for r in cars_result])
    
    return rows
'''


def get_reports_view_py(project_name: str) -> str:
    return f'''"""
Reports Handler View
"""
from engine.render import build_dashboard


def contactos_view(title: str, rows: list) -> tuple:
    table_id = "contactos-report"
    fields = {{
        "name": "Name",
        "phone": "Phone",
        "email": "Email",
        "siblings": "Siblings",
        "cars": "Cars"
    }}
    return build_dashboard(title, rows, table_id, fields)
'''


def get_readme_md(project_name: str) -> str:
    return f'''# {project_name}

A Flask web application generated by PyWebGen.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py run
```

Visit http://localhost:5000

## Default Users

- user@example.com / user (User level)
- admin@example.com / admin (Admin level)  
- system@example.com / system (System level)

## Commands

```bash
python manage.py run          # Start development server
python manage.py migrate      # Run database migrations
python manage.py seed         # Seed database with demo data
python manage.py scaffold <table>  # Generate entity from table
```

## Structure

- `routes/` - Flask blueprints (auth, admin, home, custom)
- `engine/` - Parameter-driven CRUD engine
- `hooks/` - Business logic hooks for entities
- `handlers/` - MVC handlers for custom code
- `resources/entities/` - YAML entity configurations
- `resources/migrations/` - SQL migration files
- `resources/i18n/` - Translation files (en.yaml, es.yaml)
'''


def download_static_assets(project_path: Path) -> None:
    """Download Bootstrap and jQuery assets."""
    import urllib.request
    
    vendor_dir = project_path / "resources/public/vendor"
    vendor_dir.mkdir(parents=True, exist_ok=True)
    
    assets = [
        ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css", "bootstrap.min.css"),
        ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css", "bootstrap-icons.css"),
        ("https://code.jquery.com/jquery-3.7.1.min.js", "jquery-3.7.1.min.js"),
        ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js", "bootstrap.bundle.min.js"),
    ]
    
    for url, filename in assets:
        try:
            path = vendor_dir / filename
            urllib.request.urlretrieve(url, path)
        except Exception:
            pass  # Skip if download fails


def write_handlers(project_name: str, project_path: Path) -> None:
    """Write MVC handler files for custom routes."""
    handlers_dir = project_path / "handlers"
    
    home_dir = handlers_dir / "home"
    home_dir.mkdir(parents=True, exist_ok=True)
    
    dashboard_dir = handlers_dir / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    reports_dir = handlers_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    (handlers_dir / "__init__.py").write_text("")
    
    (home_dir / "__init__.py").write_text("")
    (home_dir / "controller.py").write_text(get_home_controller_py(project_name))
    (home_dir / "model.py").write_text(get_home_model_py(project_name))
    (home_dir / "view.py").write_text(get_home_view_py(project_name))
    
    (dashboard_dir / "__init__.py").write_text("")
    (dashboard_dir / "controller.py").write_text(get_dashboard_controller_py(project_name))
    (dashboard_dir / "model.py").write_text(get_dashboard_model_py(project_name))
    (dashboard_dir / "view.py").write_text(get_dashboard_view_py(project_name))
    
    (reports_dir / "__init__.py").write_text("")
    (reports_dir / "controller.py").write_text(get_reports_controller_py(project_name))
    (reports_dir / "model.py").write_text(get_reports_model_py(project_name))
    (reports_dir / "view.py").write_text(get_reports_view_py(project_name))


def get_base_html(project_name: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{{{{ title }}}}{{% endblock %}} - {project_name}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        html, body {{ height: 100%; }}
        body {{ display: flex; flex-direction: column; }}
        main {{ flex: 1 0 auto; }}
        footer {{ flex-shrink: 0; }}
        .navbar-brand img {{
            height: 40px;
            margin-right: 10px;
        }}
        .preload {{ visibility: hidden; }}
        .dt-buttons .btn {{
            margin-right: 5px;
        }}
        .dt-buttons .btn i {{
            margin-right: 5px;
        }}
    </style>
    {{% block extra_css %}}{{% endblock %}}
</head>
<body class="bg-light preload">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm sticky-top">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold d-flex align-items-center" href="/home">
                <img src="/static/images/logo.png" alt="Logo" onerror="this.style.display='none'">
                {project_name}
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbar">
                <ul class="navbar-nav me-auto">
                    {{% if current_user.is_authenticated %}}
                    <li class="nav-item"><a class="nav-link" href="/home"><i class="bi bi-house"></i> Home</a></li>
                    {{% for item in menu_config.nav_links %}}
                    <li class="nav-item">
                        <a class="nav-link" href="{{{{ item.href }}}}"><i class="{{{{ item.icon or 'bi bi-folder' }}}}"></i> {{{{ item.label }}}}</a>
                    </li>
                    {{% endfor %}}
                    {{% for label, items in menu_config.dropdowns.items() %}}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">{{{{ label }}}}</a>
                        <ul class="dropdown-menu">
                            {{% for item in items %}}
                            <li><a class="dropdown-item" href="{{{{ item.href }}}}"><i class="{{{{ item.icon or 'bi bi-folder' }}}}"></i> {{{{ item.label }}}}</a></li>
                            {{% endfor %}}
                        </ul>
                    </li>
                    {{% endfor %}}
                    {{% endif %}}
                </ul>
                <ul class="navbar-nav">
                    {{% if current_user.is_authenticated %}}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            <i class="bi bi-palette-fill"></i>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item theme-option" href="#" data-theme="cerulean">Cerulean</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="cosmo">Cosmo</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="cyborg">Cyborg</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="darkly">Darkly</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="flatly">Flatly</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="journal">Journal</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="litera">Litera</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="lumen">Lumen</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="lux">Lux</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="materia">Materia</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="minty">Minty</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="morph">Morph</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="pulse">Pulse</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="quartz">Quartz</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="sandstone">Sandstone</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="simplex">Simplex</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="sketchy">Sketchy</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="slate">Slate</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="solar">Solar</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="spacelab">Spacelab</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="united">United</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="vapor">Vapor</a></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="zephyr">Zephyr</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item theme-option" href="#" data-theme="default">Default</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            <i class="bi bi-globe"></i>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item {{% if locale == 'en' %}}active{{% endif %}}" href="/set-language/en">English</a></li>
                            <li><a class="dropdown-item {{% if locale == 'es' %}}active{{% endif %}}" href="/set-language/es">Español</a></li>
                        </ul>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-warning" href="/logoff" title="Logout">
                            <i class="bi bi-box-arrow-right"></i> {{{{ current_user.firstname or current_user.username }}}}
                        </a>
                    </li>
                    {{% else %}}
                    <li class="nav-item"><a class="nav-link" href="/login"><i class="bi bi-box-arrow-in-right"></i> Login</a></li>
                    {{% endif %}}
                </ul>
            </div>
        </div>
    </nav>
    
    <main class="container py-4">
        {{% with messages = get_flashed_messages(with_categories=true) %}}
            {{% if messages %}}
                {{% for category, message in messages %}}
                    <div class="alert alert-{{{{ category }}}} alert-dismissible fade show">
                        {{{{ message }}}}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {{% endfor %}}
            {{% endif %}}
        {{% endwith %}}
        
        {{% block content %}}{{% endblock %}}
    </main>
    
    <footer class="bg-dark text-light py-3">
        <div class="container text-center">
            <small>&copy; {{{{ current_year }}}} {{{{ company_name }}}} - All Rights Reserved</small>
        </div>
    </footer>
    
    <div class="modal fade" id="exampleModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title">Form</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4"></div>
            </div>
        </div>
    </div>
    
    <script>var LOCALE = "{{{{ locale }}}}";</script>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.print.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
    <script>
    // Theme switcher - must run before DOM ready
    (function() {{
        var theme = localStorage.getItem('theme') || 'sketchy';
        var themeMap = {{
            'default': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
            'cerulean': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cerulean/bootstrap.min.css',
            'cosmo': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cosmo/bootstrap.min.css',
            'cyborg': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cyborg/bootstrap.min.css',
            'darkly': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/darkly/bootstrap.min.css',
            'flatly': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/flatly/bootstrap.min.css',
            'journal': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/journal/bootstrap.min.css',
            'litera': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/litera/bootstrap.min.css',
            'lumen': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/lumen/bootstrap.min.css',
            'lux': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/lux/bootstrap.min.css',
            'materia': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/materia/bootstrap.min.css',
            'minty': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/minty/bootstrap.min.css',
            'morph': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/morph/bootstrap.min.css',
            'pulse': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/pulse/bootstrap.min.css',
            'quartz': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/quartz/bootstrap.min.css',
            'sandstone': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/sandstone/bootstrap.min.css',
            'simplex': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/simplex/bootstrap.min.css',
            'sketchy': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/sketchy/bootstrap.min.css',
            'slate': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/slate/bootstrap.min.css',
            'solar': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/solar/bootstrap.min.css',
            'spacelab': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/spacelab/bootstrap.min.css',
            'united': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/united/bootstrap.min.css',
            'vapor': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/vapor/bootstrap.min.css',
            'zephyr': 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/zephyr/bootstrap.min.css'
        }};
        
        var href = themeMap[theme] || themeMap['default'];
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.id = 'bootswatch-theme';
        link.href = href;
        link.onload = function() {{ document.body.classList.remove('preload'); }};
        
        var firstLink = document.querySelector('head link[rel="stylesheet"]');
        if (firstLink) {{
            firstLink.parentNode.insertBefore(link, firstLink);
        }} else {{
            document.head.appendChild(link);
        }}
    }})();
    
    $(function() {{
        // Theme option click handler
        $('.theme-option').on('click', function(e) {{
            e.preventDefault();
            var theme = $(this).data('theme');
            localStorage.setItem('theme', theme);
            location.reload();
        }});
        
        // Highlight current theme in dropdown
        var currentTheme = localStorage.getItem('theme') || 'sketchy';
        $('.theme-option[data-theme="' + currentTheme + '"]').addClass('active');
        
        $(document).on('click', '.new-record-btn, .edit-record-btn', function(e) {{
            e.preventDefault();
            var url = $(this).data('url');
            var modal = $('#exampleModal');
            modal.find('.modal-body').html('<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>');
            modal.find('.modal-title').text($(this).hasClass('edit-record-btn') ? 'Edit Record' : 'New Record');
            modal.modal('show');
            $.get(url, function(html) {{
                modal.find('.modal-body').html(html);
            }}).fail(function() {{
                modal.find('.modal-body').html('<div class="alert alert-danger">Error loading form</div>');
            }});
        }});
        
        $(document).on('submit', '#exampleModal form', function(e) {{
            e.preventDefault();
            var form = $(this);
            var modal = $('#exampleModal');
            var btn = form.find('[type="submit"]');
            btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Saving...');
            
            var formData = new FormData(this);
            $.ajax({{
                url: form.attr('action'),
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(resp) {{
                    if (resp.ok) {{
                        modal.modal('hide');
                        if (resp.redirect) {{
                            window.location.href = resp.redirect;
                        }} else {{
                            location.reload();
                        }}
                    }} else {{
                        alert('Error: ' + (resp.errors || resp.error || 'Unknown error'));
                        btn.prop('disabled', false).html('<i class="bi bi-check-lg me-2"></i>Submit');
                    }}
                }},
                error: function(xhr) {{
                    alert('Error saving record');
                    btn.prop('disabled', false).html('<i class="bi bi-check-lg me-2"></i>Submit');
                }}
            }});
        }});
        
        $(document).on('click', '.delete-record-btn', function(e) {{
            if (!confirm('Are you sure you want to delete this record?')) {{
                e.preventDefault();
            }}
        }});
    }});
    </script>
    {{% block extra_js %}}{{% endblock %}}
</body>
</html>'''


def get_login_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
<div class="container d-flex justify-content-center align-items-center" style="min-height: 80vh;">
    <div class="card shadow-lg w-100" style="max-width: 420px;">
        <div class="card-header bg-primary text-white text-center">
            <h4 class="mb-0 fw-bold">{{ title }}</h4>
        </div>
        <div class="card-body p-4">
            <form method="POST" action="/login" class="needs-validation" novalidate>
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <div class="mb-3">
                    <label class="form-label fw-semibold" for="username">
                        <i class="bi bi-person me-2"></i>{{ tr("form.email") }}
                    </label>
                    <input type="email" name="username" id="username" class="form-control form-control-lg" 
                           placeholder="{{ tr('form.email') }}" required autofocus autocomplete="username">
                </div>
                <div class="mb-4">
                    <label class="form-label fw-semibold" for="password">
                        <i class="bi bi-lock me-2"></i>{{ tr("form.password") }}
                    </label>
                    <input type="password" name="password" id="password" class="form-control form-control-lg" 
                           placeholder="{{ tr('form.password') }}" required autocomplete="current-password">
                </div>
                <div class="d-flex gap-2 justify-content-end">
                    <button type="submit" class="btn btn-success btn-lg fw-semibold">
                        <i class="bi bi-box-arrow-in-right me-2"></i>{{ tr("auth.login") }}
                    </button>
                    <a href="/change-password" class="btn btn-outline-info btn-lg fw-semibold">
                        <i class="bi bi-key me-2"></i>{{ tr("auth.change_password") }}
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}'''


def get_change_password_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
<div class="container d-flex justify-content-center align-items-center" style="min-height: 80vh;">
    <div class="card shadow-lg w-100" style="max-width: 420px;">
        <div class="card-header bg-primary text-white text-center">
            <h4 class="mb-0 fw-bold">{{ title }}</h4>
        </div>
        <div class="card-body p-4">
            <form method="POST" action="/change-password" class="needs-validation" novalidate>
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <div class="mb-3">
                    <label class="form-label fw-semibold" for="email">
                        <i class="bi bi-envelope me-2"></i>{{ tr("form.email") }}
                    </label>
                    <input type="email" name="email" id="email" class="form-control form-control-lg" 
                           placeholder="{{ tr('form.email') }}" required autocomplete="username">
                </div>
                <div class="mb-4">
                    <label class="form-label fw-semibold" for="password">
                        <i class="bi bi-lock me-2"></i>{{ tr("form.password") }}
                    </label>
                    <input type="password" name="password" id="password" class="form-control form-control-lg" 
                           placeholder="{{ tr('form.password') }}" required autocomplete="new-password">
                </div>
                <div class="d-flex gap-2 justify-content-end">
                    <button type="submit" class="btn btn-success btn-lg fw-semibold">
                        <i class="bi bi-key me-2"></i>{{ tr("auth.change_password") }}
                    </button>
                    <a href="/login" class="btn btn-outline-secondary btn-lg fw-semibold">
                        <i class="bi bi-arrow-left me-2"></i>{{ tr("common.back") }}
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}'''


def get_main_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
<div class="text-center py-5">
    <h1 class="display-4 text-primary">Welcome!</h1>
    <p class="lead">You are logged in as {{ current_user.firstname or current_user.username }}</p>
</div>
{% endblock %}'''


def get_welcome_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
<div class="text-center py-5">
    <h1 class="display-4 text-primary">Welcome</h1>
    <p class="lead">Please <a href="/login">login</a> to continue.</p>
</div>
{% endblock %}'''


def get_reports_dashboard_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
{{ content | safe }}
{% endblock %}
{% block extra_js %}
{{ extra_js | safe }}
{% endblock %}
'''


def get_entity_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
{{ content | safe }}
{% endblock %}'''


def get_dashboard_main_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
<div class="container text-center" style="max-width: 600px;">
    <h1 class="text-primary mb-4">{{ title }}</h1>
    <div class="card-group mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title text-primary">Contactos</h5>
                <p class="card-text display-6">{{ stats.total_contactos }}</p>
            </div>
        </div>
        <div class="card">
            <div class="card-body">
                <h5 class="card-title text-primary">Siblings</h5>
                <p class="card-text display-6">{{ stats.total_siblings }}</p>
            </div>
        </div>
        <div class="card">
            <div class="card-body">
                <h5 class="card-title text-primary">Cars</h5>
                <p class="card-text display-6">{{ stats.total_cars }}</p>
            </div>
        </div>
    </div>
    <div class="card">
        <div class="card-body">
            <h5 class="card-title text-primary">Users</h5>
            <p class="card-text display-6">{{ stats.total_users }}</p>
        </div>
    </div>
</div>
{% endblock %}'''


def get_reports_contactos_html() -> str:
    return '''{% extends "base.html" %}
{% block content %}
<div class="container-fluid">
    <h2 class="text-primary mb-4">{{ title }}</h2>
    <div class="card shadow">
        <div class="card-body">
            <div class="table-responsive">
                <table id="contactos-report" class="table table-striped table-hover">
                    <thead class="table-primary">
                        <tr>
                            <th>Name</th>
                            <th>Phone</th>
                            <th>Email</th>
                            <th>Siblings</th>
                            <th>Cars</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in rows %}
                        <tr>
                            <td>{{ row.name }}</td>
                            <td>{{ row.phone }}</td>
                            <td>{{ row.email }}</td>
                            <td>{{ row.siblings }}</td>
                            <td>{{ row.cars }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
{% block extra_js %}
<script>
$(function() {{
    var dtConfig = {{
        pageLength: 25,
        order: [[0, 'asc']],
        dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>Brtip',
        buttons: [
            {{ extend: 'excel', className: 'btn btn-success btn-sm', text: '<i class="bi bi-file-earmark-excel"></i> Excel' }},
            {{ extend: 'pdf', className: 'btn btn-danger btn-sm', text: '<i class="bi bi-file-earmark-pdf"></i> PDF' }},
            {{ extend: 'print', className: 'btn btn-info btn-sm', text: '<i class="bi bi-printer"></i> Print' }}
        ]
    }};
    if (typeof LOCALE !== 'undefined' && LOCALE !== 'en') {{
        var langMap = {{ 'es': 'es-ES', 'fr': 'fr-FR', 'de': 'de-DE', 'pt': 'pt-PT', 'it': 'it-IT' }};
        var langCode = langMap[LOCALE] || LOCALE;
        dtConfig.language = {{ url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/' + langCode + '.json' }};
    }}
    var dt = $('#contactos-report').DataTable(dtConfig);
    dt.buttons().container().appendTo('#contactos-report_wrapper .col-md-6:eq(0)');
}});
</script>
{% endblock %}'''


def write_templates(project_name: str, project_path: Path) -> None:
    """Write Jinja2 HTML templates."""
    templates_dir = project_path / "templates"
    auth_dir = templates_dir / "auth"
    home_dir = templates_dir / "home"
    admin_dir = templates_dir / "admin"
    dashboard_dir = templates_dir / "dashboard"
    reports_dir = templates_dir / "reports"
    
    for d in [auth_dir, home_dir, admin_dir, dashboard_dir, reports_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    (templates_dir / "base.html").write_text(get_base_html(project_name))
    (auth_dir / "login.html").write_text(get_login_html())
    (auth_dir / "change_password.html").write_text(get_change_password_html())
    (home_dir / "main.html").write_text(get_main_html())
    (home_dir / "welcome.html").write_text(get_welcome_html())
    (admin_dir / "entity.html").write_text(get_entity_html())
    (dashboard_dir / "main.html").write_text(get_dashboard_main_html())
    (reports_dir / "dashboard.html").write_text(get_reports_dashboard_html())


def get_manage_py(project_name: str) -> str:
    return f'''#!/usr/bin/env python
"""
{project_name} Management CLI

Commands:
    python manage.py run          # Start development server
    python manage.py migrate      # Run database migrations  
    python manage.py seed         # Seed database with demo data
    python manage.py scaffold <table>  # Generate entity from table
"""
import os
import sys
import re
import argparse
import hashlib
from pathlib import Path
from datetime import datetime


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = True):
    """Start the Flask development server."""
    from app import create_app
    app = create_app()
    app.run(host=host, port=port, debug=debug)


def run_migrations():
    """Run database migrations and generate models."""
    import sqlite3
    from config import config
    
    config.load()
    db_name = config.get("connections.sqlite.db_name", "db/app.sqlite")
    db_path = db_name if db_name.startswith("/") else str(Path.cwd() / db_name)
    print(f"Running migrations on: {{db_path}}")
    
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    mig_dir = Path("resources/migrations")
    if not mig_dir.exists():
        print("No migrations directory found")
        return
    
    migrations = sorted([f for f in mig_dir.glob("*.sqlite.up.sql")])
    
    for mig_file in migrations:
        print(f"  Applying: {{mig_file.name}}")
        sql = mig_file.read_text()
        try:
            cursor.executescript(sql)
        except Exception as e:
            print(f"    Warning: {{e}}")
    
    conn.commit()
    conn.close()
    print("Migrations complete")
    
    # Generate models from migrations
    generate_models_from_migrations(migrations)


def generate_models_from_migrations(migrations: list):
    """Generate SQLAlchemy models from migration SQL files."""
    models_path = Path("models.py")
    if not models_path.exists():
        print("  models.py not found, skipping model generation")
        return
    
    content = models_path.read_text()
    
    # Check for existing table names in models
    existing_tables = set()
    for match in re.finditer(r'__tablename__\s*=\s*[\\'"](\w+)[\\'"]', content):
        existing_tables.add(match.group(1))
    
    SQL_TYPE_TO_SA = {{
        "INTEGER": "db.Integer",
        "INT": "db.Integer", 
        "BIGINT": "db.BigInteger",
        "VARCHAR": "db.String(255)",
        "CHAR": "db.String(1)",
        "TEXT": "db.Text",
        "DATE": "db.Date",
        "DATETIME": "db.DateTime",
        "TIMESTAMP": "db.DateTime",
        "BOOLEAN": "db.Boolean",
        "BOOL": "db.Boolean",
        "DECIMAL": "db.Numeric",
        "FLOAT": "db.Float",
        "DOUBLE": "db.Float",
        "NUMERIC": "db.Numeric",
    }}
    
    for mig_file in migrations:
        sql = mig_file.read_text()
        
        # Extract CREATE TABLE statements
        table_pattern = r'CREATE\\s+TABLE\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?(\\w+)\\s*\\(([^;]+)\\)'
        for match in re.finditer(table_pattern, sql, re.IGNORECASE | re.DOTALL):
            table_name = match.group(1)
            columns_str = match.group(2)
            
            # Skip if model already exists for this table
            if table_name in existing_tables:
                print(f"  Model for table '{{table_name}}' already exists, skipping")
                continue
            
            cls_name = "".join(word.capitalize() for word in table_name.split("_"))
            
            # Parse columns
            columns = []
            for line in columns_str.split(","):
                line = line.strip()
                if not line or line.upper().startswith(("PRIMARY", "FOREIGN", "UNIQUE", "INDEX", "CONSTRAINT", "CHECK")):
                    continue
                
                parts = line.split()
                if len(parts) >= 2:
                    col_name = parts[0]
                    col_type = parts[1].upper()
                    
                    # Extract length from type like VARCHAR(255)
                    sa_type = "db.String(255)"
                    type_match = re.match(r'(\\w+)(?:\\((\\d+)\\))?', col_type)
                    if type_match:
                        base_type = type_match.group(1)
                        length = type_match.group(2)
                        if length:
                            sa_type = f"db.String({{length}})"
                        elif base_type in SQL_TYPE_TO_SA:
                            sa_type = SQL_TYPE_TO_SA[base_type]
                    
                    is_primary = "PRIMARY" in line.upper()
                    is_nullable = "NOT NULL" not in line.upper() and not is_primary
                    
                    columns.append({{
                        "name": col_name,
                        "type": sa_type,
                        "primary": is_primary,
                        "nullable": is_nullable
                    }})
            
            if not columns:
                continue
            
            # Generate model class
            lines = ["class " + cls_name + "(db.Model):"]
            lines.append('    __tablename__ = "' + table_name + '"')
            lines.append("")
            
            for col in columns:
                if col["primary"]:
                    lines.append('    ' + col["name"] + ' = db.Column(db.Integer, primary_key=True)')
                elif not col["nullable"]:
                    lines.append('    ' + col["name"] + ' = db.Column(' + col["type"] + ', nullable=False)')
                else:
                    lines.append('    ' + col["name"] + ' = db.Column(' + col["type"] + ')')
            
            lines.append("")
            model_code = "\\n".join(lines)
            
            # Insert before @login_manager.user_loader
            insert_marker = "@login_manager.user_loader"
            if insert_marker in content:
                content = content.replace(insert_marker, model_code + "\\n\\n" + insert_marker)
                print(f"  Generated model: {{cls_name}} (table: {{table_name}})")
                existing_tables.add(table_name)
    
    models_path.write_text(content)


def seed_database():
    """Seed database with demo users."""
    import sqlite3
    import bcrypt
    from config import config
    
    config.load()
    db_name = config.get("connections.sqlite.db_name", "db/app.sqlite")
    db_path = db_name if db_name.startswith("/") else str(Path.cwd() / db_name)
    print(f"Seeding database: {{db_path}}")
    
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    users = [
        ("User", "Regular", "user@example.com", hash_password("user"), "U"),
        ("User", "Admin", "admin@example.com", hash_password("admin"), "A"),
        ("User", "System", "system@example.com", hash_password("system"), "S"),
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE username LIKE '%@example.com'")
    
    for lastname, firstname, username, password, level in users:
        cursor.execute(
            "INSERT INTO users (lastname, firstname, username, password, email, level, active, dob) "
            "VALUES (?, ?, ?, ?, ?, ?, 'T', '1957-02-07')",
            (lastname, firstname, username, password, username, level)
        )
    
    conn.commit()
    conn.close()
    print(f"Seeded {{len(users)}} demo users")
    print("  user@example.com / user (User)")
    print("  admin@example.com / admin (Admin)")
    print("  system@example.com / system (System)")


def scaffold_table(table_name: str, force: bool = False):
    """Run scaffold command for a single table."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from engine.scaffold import scaffold_table as do_scaffold
        print(do_scaffold(table_name, force))


def scaffold_all(force: bool = False):
    """Run scaffold command for all tables."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from engine.scaffold import scaffold_all as do_scaffold_all
        do_scaffold_all(force)


def main():
    parser = argparse.ArgumentParser(description="{project_name} Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    run_parser = subparsers.add_parser("run", help="Start development server")
    run_parser.add_argument("--host", default="0.0.0.0")
    run_parser.add_argument("--port", type=int, default=5000)
    run_parser.add_argument("--no-debug", action="store_true")
    
    subparsers.add_parser("migrate", help="Run database migrations and generate models")
    subparsers.add_parser("seed", help="Seed database with demo data")
    
    scaffold_parser = subparsers.add_parser("scaffold", help="Generate entity from table")
    scaffold_parser.add_argument("table", nargs="?", help="Table name to scaffold (optional with --all)")
    scaffold_parser.add_argument("--all", action="store_true", help="Scaffold all tables")
    scaffold_parser.add_argument("--force", action="store_true", help="Overwrite existing entities and hooks")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_server(args.host, args.port, not args.no_debug)
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "seed":
        seed_database()
    elif args.command == "scaffold":
        if args.all:
            scaffold_all(args.force)
        elif args.table:
            scaffold_table(args.table, args.force)
        else:
            print("Error: Specify a table name or use --all")
            parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
'''


def get_pywebgen_cheatsheet() -> str:
    return '''# PyWebGen Framework Cheat Sheet

## Entity Configuration (YAML)

### Complete Entity Structure

```yaml
entity: users                    # Unique entity identifier (required)
title: Users                     # Display title (required)
table: users                     # Database table name (required)
connection: default              # Database connection (default: "default")
rights:                          # User levels that can access (default: ["U", "A", "S"])
  - U                            # User
  - A                            # Administrator
  - S                            # System
menu_category: System            # Group in dropdown menu (optional)
menu_hidden: false               # Hide from menu (default: false)

fields:                          # Field definitions (see below)
  - ...

queries:                         # Custom SQL queries (optional)
  list: "SELECT * FROM users ORDER BY id DESC"
  get: "SELECT * FROM users WHERE id = :id"

actions:                         # Enable/disable actions (default: all true)
  new: true
  edit: true
  delete: true

hooks:                           # Business logic hooks (optional)
  before_save: hooks.users.before_save
  after_save: hooks.users.after_save
  before_load: hooks.users.before_load
  after_load: hooks.users.after_load
  before_delete: hooks.users.before_delete
  after_delete: hooks.users.after_delete

subgrids:                        # Child entities displayed as tabs
  - entity: cars
    title: Cars
    foreign_key: user_id
    icon: bi bi-car-front
```

---

## Field Types

### Basic Fields

```yaml
# Text Input
- id: name
  label: Name
  type: text
  placeholder: Enter name...
  required: true

# Email Input (with validation)
- id: email
  label: Email
  type: email
  placeholder: user@example.com
  required: true

# Password Input (masked)
- id: password
  label: Password
  type: password
  placeholder: Enter password...
  required: true

# Number Input
- id: age
  label: Age
  type: number
  placeholder: "0"

# Date Input
- id: birth_date
  label: Birth Date
  type: date

# Textarea (multi-line)
- id: description
  label: Description
  type: textarea
  placeholder: Enter description...
```

### Selection Fields

```yaml
# Dropdown Select
- id: level
  label: Level
  type: select
  options:
    - value: ""
      label: Select Level
    - value: U
      label: User
    - value: A
      label: Administrator
    - value: S
      label: System

# Radio Buttons
- id: status
  label: Status
  type: radio
  options:
    - value: T
      label: Active
    - value: F
      label: Inactive

# Checkbox
- id: terms_accepted
  label: I accept the terms
  type: checkbox
```

### File Upload

```yaml
- id: imagen
  label: Image
  type: file
```

### Hidden Fields

```yaml
# Hidden field (for foreign keys, computed values)
- id: contacto_id
  type: hidden

# Primary key (auto-generated)
- id: id
  type: hidden
```

---

## Field Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `id` | string | required | Field name (matches database column) |
| `label` | string | required | Display label |
| `type` | string | "text" | Field type (see above) |
| `required` | boolean | false | Mark as required |
| `placeholder` | string | null | Placeholder text |
| `options` | array | [] | Options for select/radio |
| `hidden_in_grid` | boolean | false | Hide in grid view |
| `hidden_in_form` | boolean | false | Hide in form view |
| `grid_only` | boolean | false | Show only in grid (not in form) |
| `fk` | string | null | Foreign key reference |

---

## Subgrids (Child Entities)

```yaml
# In parent entity (contactos.yaml)
subgrids:
  - entity: cars                # Child entity name
    title: Cars                 # Tab title
    foreign_key: contacto_id    # FK column in child table
    icon: bi bi-car-front       # Bootstrap icon
  
  - entity: siblings
    title: Siblings
    foreign_key: contacto_id
    icon: bi bi-people-fill
```

---

## Custom Queries

```yaml
queries:
  # List query (with optional WHERE injection for subgrids)
  list: "SELECT * FROM users WHERE active = \'T\' ORDER BY created_at DESC"
  
  # Get single record (must use :id parameter)
  get: "SELECT * FROM users WHERE id = :id"
```

---

## Hooks

### Hook Configuration

```yaml
# In entity YAML
hooks:
  before_save: hooks.contactos.before_save
  after_save: hooks.contactos.after_save
  before_load: hooks.contactos.before_load
  after_load: hooks.contactos.after_load
  before_delete: hooks.contactos.before_delete
  after_delete: hooks.contactos.after_delete
```

### Hook Implementation

```python
# hooks/contactos.py

def after_load(rows):
    """Called after loading records."""
    for row in rows:
        if row.get("imagen"):
            row["imagen"] = f"/uploads/{row[\'imagen\']}"
        row["full_name"] = f"{row.get(\'firstname\', \'\')} {row.get(\'lastname\', \'\')}"
    return rows


def before_save(data):
    """Called before saving. Return {"errors": {...}} to cancel."""
    if not data.get("email"):
        return {"errors": {"email": "Email is required"}}
    data["email"] = data["email"].lower().strip()
    return data


def after_save(result):
    """Called after saving."""
    print(f"Record {result.get(\'id\')} saved")
    return result


def before_delete(data):
    """Called before delete. Return {"errors": {...}} to cancel."""
    return {"success": True}


def after_delete(data):
    """Called after delete."""
    print(f"Record {data.get(\'id\')} deleted")
    return {"success": True}
```

---

## Menu Configuration

```python
# menu.py
from engine.menu import get_auto_menu_config

custom_nav_links = [
    {"label": "DASHBOARD", "href": "/dashboard", "icon": "bi-speedometer2"},
]

custom_dropdowns = {
    "Reports": [
        {"label": "Contactos", "href": "/reports/contactos", "icon": "bi-file-earmark-text"},
    ],
}

def get_menu_config():
    auto = get_auto_menu_config()
    return {
        "nav_links": auto.get("nav_links", []) + custom_nav_links,
        "dropdowns": {**auto.get("dropdowns", {}), **custom_dropdowns}
    }
```

---

## User Levels

| Level | Code | Description |
|-------|------|-------------|
| User | U | Basic user access |
| Administrator | A | Full admin access |
| System | S | System/super admin |

---

## Bootstrap Icons

| Entity | Icon |
|--------|------|
| Users | `bi bi-people` |
| Contactos | `bi bi-person-lines-fill` |
| Cars | `bi bi-car-front` |
| Products | `bi bi-box` |
| Orders | `bi bi-cart` |
| Reports | `bi bi-file-earmark-text` |
| Dashboard | `bi bi-speedometer2` |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/{entity}/` | List/view entity |
| GET | `/admin/{entity}/add-form/` | Get new record form |
| GET | `/admin/{entity}/edit-form/{id}` | Get edit form |
| POST | `/admin/{entity}/save` | Save record |
| GET | `/admin/{entity}/delete/{id}` | Delete record |
| GET | `/admin/subgrid` | Get subgrid data (JSON) |

---

## Best Practices

1. Use hooks for business logic
2. Validate in before_save - Return `{"errors": {...}}` to cancel
3. Transform data in after_load - Add computed fields
4. Set menu_hidden for child entities
5. Use appropriate icons
6. Restrict rights appropriately
'''


def write_all_templates(project_name: str, project_path: Path) -> None:
    """Write all template files for a new project."""
    
    def ensure_dir(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
    
    # Requirements and config
    ensure_dir(project_path / "requirements.txt")
    (project_path / "requirements.txt").write_text(REQUIREMENTS_TXT)
    ensure_dir(project_path / "config.yaml")
    (project_path / "config.yaml").write_text(get_config_yaml(project_name))
    ensure_dir(project_path / "config.py")
    (project_path / "config.py").write_text(CONFIG_PY)
    ensure_dir(project_path / "models.py")
    (project_path / "models.py").write_text(MODELS_PY)
    ensure_dir(project_path / "app.py")
    (project_path / "app.py").write_text(get_app_py(project_name))
    ensure_dir(project_path / "menu.py")
    (project_path / "menu.py").write_text(MENU_PY)
    
    # i18n
    ensure_dir(project_path / "i18n/__init__.py")
    (project_path / "i18n/__init__.py").write_text(I18N_INIT)
    ensure_dir(project_path / "resources/i18n/en.yaml")
    (project_path / "resources/i18n/en.yaml").write_text(EN_I18N)
    ensure_dir(project_path / "resources/i18n/es.yaml")
    (project_path / "resources/i18n/es.yaml").write_text(ES_I18N)
    
    # Routes
    ensure_dir(project_path / "routes/__init__.py")
    (project_path / "routes/__init__.py").write_text("")
    ensure_dir(project_path / "routes/auth.py")
    (project_path / "routes/auth.py").write_text(ROUTES_AUTH)
    ensure_dir(project_path / "routes/home.py")
    (project_path / "routes/home.py").write_text(ROUTES_HOME)
    ensure_dir(project_path / "routes/i18n.py")
    (project_path / "routes/i18n.py").write_text(ROUTES_I18N)
    ensure_dir(project_path / "routes/custom.py")
    (project_path / "routes/custom.py").write_text(ROUTES_CUSTOM)
    ensure_dir(project_path / "routes/admin.py")
    (project_path / "routes/admin.py").write_text(ROUTES_ADMIN)
    
    # Engine
    ensure_dir(project_path / "engine/__init__.py")
    (project_path / "engine/__init__.py").write_text(ENGINE_INIT)
    ensure_dir(project_path / "engine/menu.py")
    (project_path / "engine/menu.py").write_text(ENGINE_MENU)
    
    # Engine CRUD
    ensure_dir(project_path / "engine/crud.py")
    (project_path / "engine/crud.py").write_text(get_engine_crud())
    
    # Engine Query
    ensure_dir(project_path / "engine/query.py")
    (project_path / "engine/query.py").write_text(get_engine_query())
    
    # Engine Render
    ensure_dir(project_path / "engine/render.py")
    (project_path / "engine/render.py").write_text(get_engine_render())
    
    # Engine Scaffold
    ensure_dir(project_path / "engine/scaffold.py")
    (project_path / "engine/scaffold.py").write_text(get_engine_scaffold(project_name))
    
    # Migrations
    write_migrations(project_path)
    
    # Entity configs
    write_entity_configs(project_path)
    
    # Hooks
    write_hooks(project_path)
    
    # Handlers
    write_handlers(project_name, project_path)
    
    # Templates
    write_templates(project_name, project_path)
    
    # manage.py
    ensure_dir(project_path / "manage.py")
    (project_path / "manage.py").write_text(get_manage_py(project_name))
    
    # .gitignore
    ensure_dir(project_path / ".gitignore")
    (project_path / ".gitignore").write_text(GITIGNORE)
    
    # README.md
    ensure_dir(project_path / "README.md")
    (project_path / "README.md").write_text(get_readme_md(project_name))
    
    # PYWEBGEN_CHEATSHEET.md
    ensure_dir(project_path / "PYWEBGEN_CHEATSHEET.md")
    (project_path / "PYWEBGEN_CHEATSHEET.md").write_text(get_pywebgen_cheatsheet())
    
    # Download static assets
    download_static_assets(project_path)
    
    print(f"Project created: {project_path}")
