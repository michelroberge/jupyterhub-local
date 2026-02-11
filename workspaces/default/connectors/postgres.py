"""
PostgreSQL connector module.
Provides get_engine() to create SQLAlchemy engines from credentials/postgres.yaml
"""

from pathlib import Path
import yaml
from sqlalchemy import create_engine


def get_engine(connection_name: str):
    """
    Create a SQLAlchemy engine for the specified connection.

    Args:
        connection_name: Key from credentials/postgres.yaml (e.g., "staging")

    Returns:
        SQLAlchemy Engine connected to the specified PostgreSQL database
    """
    # Find credentials file relative to this module's location
    module_dir = Path(__file__).parent.parent
    credentials_path = module_dir / "credentials" / "postgres.yaml"

    if not credentials_path.exists():
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    with open(credentials_path, "r") as f:
        credentials = yaml.safe_load(f)

    if connection_name not in credentials:
        available = list(credentials.keys())
        raise KeyError(f"Connection '{connection_name}' not found. Available: {available}")

    creds = credentials[connection_name]

    connection_string = (
        f"postgresql+psycopg://{creds['username']}:{creds['password']}"
        f"@{creds['host']}:{creds['port']}/{creds['database']}"
    )

    return create_engine(connection_string)
