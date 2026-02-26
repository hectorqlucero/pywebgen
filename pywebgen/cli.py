"""
PyWebGen CLI - Command Line Interface

Usage:
    pywebgen new <project_name> [--path .]   # Create standalone project
    pywebgen --help                          # Show help

Inside generated project:
    python manage.py scaffold <table>        # Scaffold entity
    python manage.py scaffold --all          # Scaffold all tables
    python manage.py migrate                 # Run migrations
    python manage.py rollback                # Rollback migration
    python manage.py seed                    # Seed database
    python manage.py run                     # Run development server
    python manage.py shell                   # Interactive shell with app context
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="pywebgen")
def cli():
    """PyWebGen - Parameter-Driven Web Application Framework
    
    Create standalone Flask projects with:
    - Parameter-driven CRUD from YAML configs
    - MVC handlers for custom code
    - Tabbed grids with subgrids
    - Working i18n (English/Spanish)
    - Multi-database migrations (SQLite, MySQL, PostgreSQL)
    """
    pass


@cli.command()
@click.argument("project_name")
@click.option("--path", default=".", help="Path where to create the project")
def new(project_name: str, path: str):
    """Create a new standalone PyWebGen project"""
    from pywebgen.generator import create_project
    
    project_path = Path(path) / project_name
    if project_path.exists():
        console.print(f"[red]Error: Directory '{project_path}' already exists[/red]")
        sys.exit(1)
    
    console.print(Panel(f"Creating PyWebGen project: {project_name}", style="bold blue"))
    
    create_project(project_name, project_path)
    
    console.print(f"\n[green]✓ Project created successfully![/green]\n")
    console.print("Quick Start:")
    console.print(f"  cd {project_name}")
    console.print("  python -m venv venv")
    console.print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    console.print("  pip install -r requirements.txt")
    console.print("  python manage.py migrate")
    console.print("  python manage.py seed")
    console.print("  python manage.py run")
    console.print("\nThen visit: http://localhost:5000")
    console.print("\nDefault users:")
    console.print("  - user@example.com / user (User level)")
    console.print("  - admin@example.com / admin (Admin level)")
    console.print("  - system@example.com / system (System level)")


def main():
    cli()


if __name__ == "__main__":
    main()
