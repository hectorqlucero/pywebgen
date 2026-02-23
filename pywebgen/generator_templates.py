"""
PyWebGen Project Templates

All templates for generating standalone Flask projects.
These projects are completely independent - they don't depend on pywebgen.
"""

from pathlib import Path
from typing import Any


# =============================================================================
# REQUIREMENTS AND CONFIG
# =============================================================================

REQUIREMENTS_TXT = """# Flask Web Application
Flask>=3.0.0
Flask-SQLAlchemy>=3.1.0
Flask-Migrate>=4.0.0
Flask-Login>=0.6.0
Flask-WTF>=1.2.0
SQLAlchemy>=2.0.0
PyYAML>=6.0
python-dotenv>=1.0.0
bcrypt>=4.1.0
click>=8.1.0
rich>=13.0.0

# Optional database drivers (uncomment as needed)
# mysqlclient>=2.2.0
# psycopg2-binary>=2.9.0
# pymysql  # Alternative MySQL driver
"""


def get_config_yaml(project_name: str) -> str:
    return f"""app:
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
  session_secret_key: "{project_name}-change-me-in-production"

connections:
  sqlite:
    db_type: sqlite
    db_name: db/{project_name}.sqlite
  mysql:
    db_type: mysql
    db_name: "//localhost:3306/{project_name}"
    db_user: root
    db_pwd: ""
  postgresql:
    db_type: postgresql
    db_name: "//localhost:5432/{project_name}"
    db_user: postgres
    db_pwd: ""
  default: sqlite

site_name: "{project_name}"
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
"""


# =============================================================================
# I18N FILES
# =============================================================================

EN_I18N = """common:
  save: "Save"
  cancel: "Cancel"
  submit: "Submit"
  edit: "Edit"
  delete: "Delete"
  add: "Add"
  new: "New"
  search: "Search"
  filter: "Filter"
  export: "Export"
  import: "Import"
  close: "Close"
  back: "Back"
  next: "Next"
  previous: "Previous"
  loading: "Loading..."
  actions: "Actions"
  yes: "Yes"
  no: "No"
  ok: "OK"
  confirm: "Confirm"
  select: "Select"
  required: "Required"

menu:
  home: "Home"
  users: "Users"
  contactos: "Contacts"
  admin: "Administration"
  logout: "Logout"
  profile: "Profile"
  settings: "Settings"

form:
  email: "Email"
  password: "Password"
  username: "Username"
  name: "Name"
  phone: "Phone"
  address: "Address"
  date: "Date"
  amount: "Amount"
  description: "Description"
  status: "Status"
  notes: "Notes"
  file: "File"

validation:
  required: "{field} is required"
  invalid_email: "Invalid email address"
  invalid_date: "Invalid date"

error:
  general: "An error occurred. Please try again"
  not_found: "Record not found"
  unauthorized: "You don't have permission"
  forbidden: "Access denied"

success:
  saved: "Saved successfully"
  deleted: "Deleted successfully"
  created: "Created successfully"
  updated: "Updated successfully"

auth:
  login: "Login"
  logout: "Logout"
  invalid_credentials: "Invalid username or password"
  welcome: "Welcome"
  change_password: "Change Password"

grid:
  no_records: "No records found"
"""

ES_I18N = """common:
  save: "Guardar"
  cancel: "Cancelar"
  submit: "Enviar"
  edit: "Editar"
  delete: "Eliminar"
  add: "Agregar"
  new: "Nuevo"
  search: "Buscar"
  filter: "Filtrar"
  export: "Exportar"
  import: "Importar"
  close: "Cerrar"
  back: "Atrás"
  next: "Siguiente"
  previous: "Anterior"
  loading: "Cargando..."
  actions: "Acciones"
  yes: "Sí"
  no: "No"
  ok: "OK"
  confirm: "Confirmar"
  select: "Seleccionar"
  required: "Requerido"

menu:
  home: "Inicio"
  users: "Usuarios"
  contactos: "Contactos"
  admin: "Administración"
  logout: "Cerrar Sesión"
  profile: "Perfil"
  settings: "Configuración"

form:
  email: "Correo Electrónico"
  password: "Contraseña"
  username: "Usuario"
  name: "Nombre"
  phone: "Teléfono"
  address: "Dirección"
  date: "Fecha"
  amount: "Cantidad"
  description: "Descripción"
  status: "Estado"
  notes: "Notas"
  file: "Archivo"

validation:
  required: "{field} es requerido"
  invalid_email: "Correo electrónico inválido"
  invalid_date: "Fecha inválida"

error:
  general: "Ocurrió un error. Por favor intente de nuevo"
  not_found: "Registro no encontrado"
  unauthorized: "No tiene permiso"
  forbidden: "Acceso denegado"

success:
  saved: "Guardado exitosamente"
  deleted: "Eliminado exitosamente"
  created: "Creado exitosamente"
  updated: "Actualizado exitosamente"

auth:
  login: "Iniciar Sesión"
  logout: "Cerrar Sesión"
  invalid_credentials: "Usuario o contraseña inválidos"
  welcome: "Bienvenido"
  change_password: "Cambiar Contraseña"

grid:
  no_records: "No se encontraron registros"
"""


# =============================================================================
# CORE APPLICATION FILES
# =============================================================================

CONFIG_PY = '''"""
Application Configuration

Loads configuration from YAML files and environment variables.
"""
import os
from pathlib import Path
from typing import Any, Optional
import yaml
from flask import Flask, session


class Config:
    _instance: Optional["Config"] = None
    _config: dict[str, Any] = {}
    _base_path: Optional[Path] = None
    
    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, app: Optional[Flask] = None, config_path: Optional[str] = None) -> None:
        if config_path is None:
            config_path = os.environ.get("APP_CONFIG", "config.yaml")
        
        path = Path(config_path)
        if path.exists():
            self._base_path = path.parent.parent.resolve()
            with open(path, "r") as f:
                self._config = yaml.safe_load(f) or {}
        
        if app:
            self._load_flask_config(app)
    
    def _resolve_path(self, path_str: str) -> str:
        if Path(path_str).is_absolute():
            return path_str
        if self._base_path:
            return str((self._base_path / path_str).resolve())
        return path_str
    
    def _load_flask_config(self, app: Flask) -> None:
        app.config["SECRET_KEY"] = self.get("security.session_secret_key", "change-me")
        app.config["UPLOAD_FOLDER"] = self._resolve_path(self.get("uploads", "./uploads/"))
        app.config["MAX_CONTENT_LENGTH"] = self.get("max_upload_mb", 5) * 1024 * 1024
        app.config["PERMANENT_SESSION_LIFETIME"] = self.get("app.session_timeout", 28800)
        
        default_conn = self.get("connections.default", "sqlite")
        if isinstance(default_conn, str):
            conn_config = self.get(f"connections.{default_conn}", {})
        else:
            conn_config = default_conn
        
        db_type = conn_config.get("db_type", "sqlite") if isinstance(conn_config, dict) else "sqlite"
        
        if db_type == "sqlite":
            db_name = conn_config.get("db_name", "db/app.sqlite") if isinstance(conn_config, dict) else "db/app.sqlite"
            db_path = self._resolve_path(db_name)
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        elif db_type == "mysql":
            db_name = conn_config.get("db_name", "//localhost:3306/app") if isinstance(conn_config, dict) else "//localhost:3306/app"
            db_user = conn_config.get("db_user", "root") if isinstance(conn_config, dict) else "root"
            db_pwd = conn_config.get("db_pwd", "") if isinstance(conn_config, dict) else ""
            app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pwd}@{db_name}"
        elif db_type == "postgresql":
            db_name = conn_config.get("db_name", "//localhost:5432/app") if isinstance(conn_config, dict) else "//localhost:5432/app"
            db_user = conn_config.get("db_user", "postgres") if isinstance(conn_config, dict) else "postgres"
            db_pwd = conn_config.get("db_pwd", "") if isinstance(conn_config, dict) else ""
            app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_pwd}@{db_name}"
        
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    @property
    def site_name(self) -> str:
        return self.get("site_name", "My App")
    
    @property
    def company_name(self) -> str:
        return self.get("company_name", "My Company")
    
    @property
    def theme(self) -> str:
        return self.get("ui.default_theme", "sketchy")
    
    @property
    def uploads_path(self) -> str:
        return self._resolve_path(self.get("uploads", "./uploads/"))
    
    @property
    def allowed_image_extensions(self) -> list[str]:
        return self.get("allowed_image_exts", ["jpg", "jpeg", "png", "gif", "bmp", "webp"])
    
    @property
    def default_locale(self) -> str:
        return self.get("app.default_locale", "es")


config = Config()


def get_locale() -> str:
    return session.get("locale", config.default_locale)


def set_locale(locale: str) -> None:
    if locale in ("en", "es"):
        session["locale"] = locale
        session.permanent = True
'''


MODELS_PY = '''"""
Database Models
"""
from datetime import datetime
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import bcrypt

db = SQLAlchemy()
login_manager = LoginManager()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    lastname = db.Column(db.String(255))
    firstname = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.String(20))
    cell = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    fax = db.Column(db.String(50))
    email = db.Column(db.String(255))
    level = db.Column(db.String(1), default="U")
    active = db.Column(db.String(1), default="T")
    imagen = db.Column(db.String(255))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password: str) -> None:
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
    
    @property
    def is_active_user(self) -> bool:
        return self.active == "T"
    
    @property
    def is_admin(self) -> bool:
        return self.level in ("A", "S")


class Contactos(db.Model):
    __tablename__ = "contactos"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    imagen = db.Column(db.String(255))
    
    cars = db.relationship("Cars", backref="contacto", lazy=True, cascade="all, delete-orphan")
    siblings = db.relationship("Siblings", backref="contacto", lazy=True, cascade="all, delete-orphan")


class Cars(db.Model):
    __tablename__ = "cars"
    
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    imagen = db.Column(db.String(255))
    contacto_id = db.Column(db.Integer, db.ForeignKey("contactos.id"), nullable=False)


class Siblings(db.Model):
    __tablename__ = "siblings"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    imagen = db.Column(db.String(255))
    contacto_id = db.Column(db.Integer, db.ForeignKey("contactos.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return db.session.get(User, int(user_id))
'''


def get_app_py(project_name: str) -> str:
    return f'''"""
Flask Application Factory
"""
import os
from pathlib import Path
from typing import Optional
from flask import Flask, redirect, url_for, send_from_directory
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect

from config import config
from models import db, login_manager
from i18n import I18N

csrf = CSRFProtect()


def create_app(config_path: Optional[str] = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="resources/public",
        static_url_path="/static",
    )
    
    config.load(app, config_path)
    
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(os.path.abspath(config.uploads_path), filename)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)
    
    I18N.init_app(app)
    
    from engine import EntityConfigManager
    EntityConfigManager.load_all()
    
    _register_blueprints(app)
    _register_template_filters(app)
    _register_context_processors(app)
    
    return app


def _register_blueprints(app: Flask) -> None:
    from routes.auth import auth_bp
    from routes.home import home_bp
    from routes.admin import admin_bp
    from routes.i18n import i18n_bp
    from routes.custom import custom_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(i18n_bp)
    app.register_blueprint(custom_bp)
    
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("home.main"))
        return redirect(url_for("auth.login"))


def _register_template_filters(app: Flask) -> None:
    @app.template_filter("image_link")
    def image_link(filename: Optional[str]) -> str:
        if not filename:
            return "/static/images/placeholder.png"
        return f"/uploads/{{filename}}"
    
    @app.template_filter("capitalize_words")
    def capitalize_words(text: str) -> str:
        return " ".join(word.capitalize() for word in str(text).split("_"))


def _register_context_processors(app: Flask) -> None:
    @app.context_processor
    def inject_config():
        from datetime import datetime
        return {{
            "config": config,
            "site_name": config.site_name,
            "company_name": config.company_name,
            "theme": config.theme,
            "current_year": datetime.now().year,
        }}
    
    @app.context_processor
    def inject_user():
        return {{
            "current_user": current_user,
            "user_level": current_user.level if current_user.is_authenticated else None,
            "user_name": f"{{current_user.firstname}} {{current_user.lastname}}" if current_user.is_authenticated else None,
        }}
    
    @app.context_processor
    def inject_i18n():
        from i18n import tr
        from config import get_locale
        return {{
            "tr": tr,
            "locale": get_locale(),
        }}
    
    @app.context_processor
    def inject_menu():
        from menu import get_menu_config
        return {{"menu_config": get_menu_config()}}
'''


# Continue in generator_templates_part2.py...
