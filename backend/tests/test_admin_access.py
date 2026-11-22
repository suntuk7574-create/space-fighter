"""Tes pengaman akses admin dan blokir pemain."""

from app import main
from app.schemas import AdminStatsOut, PlayerCreate


def test_token_admin_tidak_bisa_dipalsukan():
    token = main.make_admin_token(7)
    assert main.parse_admin_token(token) == 7
    assert main.parse_admin_token("token-Asli-apa-saja") is None
    assert main.parse_admin_token(token[:-2] + "xx") is None


def test_endpoint_blokir_hanya_admin():
    route = next(
        r
        for r in main.app.routes
        if getattr(r, "path", "") == "/api/admin/players/{player_id}/block"
        and "PATCH" in getattr(r, "methods", set())
    )
    dependencies = [d.call for d in route.dependant.dependencies]
    assert main.require_admin in dependencies


def test_pemain_tidak_bisa_mengirim_status_blokir():
    assert "is_blocked" not in PlayerCreate.model_fields
    assert "blocked_players" in AdminStatsOut.model_fields
