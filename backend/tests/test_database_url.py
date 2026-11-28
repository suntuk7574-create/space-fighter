"""Test normalisasi DATABASE_URL untuk deploy cloud."""

from app.database import normalize_database_url


def test_url_neon_diterjemahkan_ke_pg8000():
    url, args = normalize_database_url(
        "postgresql://user:pass@ep-abc-pooler.neon.tech/neondb?sslmode=require"
    )
    assert url == "postgresql+pg8000://user:pass@ep-abc-pooler.neon.tech/neondb"
    assert args["ssl_context"] is not None


def test_channel_binding_dibuang():
    url, args = normalize_database_url(
        "postgres://user:pass@ep-abc.neon.tech/db?sslmode=require&channel_binding=require"
    )
    assert "channel_binding" not in url
    assert "sslmode" not in url
    assert args["ssl_context"] is not None


def test_url_lokal_tidak_memaksa_ssl():
    url, args = normalize_database_url(
        "postgresql+pg8000://postgres:postgres@127.0.0.1:5432/spacefighter"
    )
    assert url.startswith("postgresql+pg8000://")
    assert args == {}
