"""Koneksi database SQLAlchemy. Default: PostgreSQL."""

import os
import ssl

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Hanya argumen yang diterima pg8000.connect(). Query string lain dari
# provider (mis. channel_binding) harus dibuang Supaya tidak jadi kwarg.
_PG8000_KWARGS = {
    "application_name",
    "database",
    "host",
    "password",
    "port",
    "source_address",
    "unix_sock",
    "ssl_context",
    "timeout",
    "tcp_keepalive",
    "replication",
    "startup_params",
}


def normalize_database_url(raw_url: str):
    """Ubah URL Neon/Render jadi URL pg8000 + connect_args yang valid.

    SQLAlchemy meneruskan semua query string langsung ke ``pg8000.connect()``.
    Karena pg8000 tidak punya argumen ``sslmode``/``channel_binding``, kedua
    parameter itu diterjemahkan/dibuang di sini sebelum engine dibuat.
    """
    url = make_url(raw_url)
    query = {k: v for k, v in url.query.items() if k in _PG8000_KWARGS}

    connect_args = {}
    sslmode = url.query.get("sslmode")
    if sslmode:
        if sslmode.lower() == "disable":
            connect_args["ssl_context"] = False
        else:
            connect_args["ssl_context"] = ssl.create_default_context()

    normalized = url.set(
        drivername="postgresql+pg8000",
        query=query,
    ).render_as_string(hide_password=False)
    return normalized, connect_args


_raw_url = os.getenv(
    "DATABASE_URL",
    "postgresql+pg8000://postgres:postgres@127.0.0.1:5432/spacefighter",
)
DATABASE_URL, CONNECT_ARGS = normalize_database_url(_raw_url)

engine = create_engine(
    DATABASE_URL,
    connect_args=CONNECT_ARGS,
    pool_pre_ping=True,
    future=True,
)
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
        if "is_blocked" not in columns:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE players "
                        "ADD COLUMN is_blocked BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                )
