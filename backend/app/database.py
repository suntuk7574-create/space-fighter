"""Koneksi database SQLAlchemy. Default: PostgreSQL."""

import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/spacefighter",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Migrasi ringan: database lama belum punya kolom is_admin / email.
    inspector = inspect(engine)
    if "players" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("players")]
        if "is_admin" not in columns:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE players "
                        "ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                )
        if "email" not in columns:
            with engine.begin() as conn:
                # Email nullable supaya akun lama tetap bisa dipakai via username.
                conn.execute(
                    text(
                        "ALTER TABLE players "
                        "ADD COLUMN email VARCHAR(120) UNIQUE"
                    )
                )
