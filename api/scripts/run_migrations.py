#!/usr/bin/env python3
"""Run Alembic migrations."""
import os
import sys
from alembic import command
from alembic.config import Config
from api.core.config import settings

def main():
    """Run Alembic migrations."""
    # Get the path to alembic.ini (it's in the root directory)
    script_dir = os.path.dirname(__file__)  # api/scripts/
    api_dir = os.path.dirname(script_dir)  # api/
    root_dir = os.path.dirname(api_dir)  # project root
    alembic_ini_path = os.path.join(root_dir, "alembic.ini")
    
    # If alembic.ini is not in root, try /app/alembic.ini (docker container)
    if not os.path.exists(alembic_ini_path):
        alembic_ini_path = "/app/alembic.ini"
    
    if not os.path.exists(alembic_ini_path):
        print(f"Error: Alembic config not found at {alembic_ini_path}")
        sys.exit(1)
    
    print(f"Using Alembic config: {alembic_ini_path}")
    alembic_cfg = Config(alembic_ini_path)
    
    # Set database URL
    alembic_cfg.set_main_option("sqlalchemy.url", (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    ))
    
    # Set script location to api/alembic (where migrations are stored)
    script_location = os.path.join(api_dir, "alembic")
    if os.path.exists(script_location):
        alembic_cfg.set_main_option("script_location", script_location)
        print(f"Using script_location: {script_location}")
    
    # Apply migrations
    print("Applying migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied successfully!")

if __name__ == "__main__":
    main()

