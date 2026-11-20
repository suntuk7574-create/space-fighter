"""Unit test logika game tanpa database."""

from app.game_logic import (
    LCGRandom,
    daily_seed,
    difficulty_for_wave,
    score_for_kill,
    spawn_wave,
    validate_run,
    wave_bonus,
)


def test_lcg_deterministik():
    a = LCGRandom(123)
    b = LCGRandom(123)
    assert [a.random() for _ in range(5)] == [b.random() for _ in range(5)]


def test_daily_seed_stabil():
    assert daily_seed("2026-11-20") == daily_seed("2026-11-20")
    assert daily_seed("2026-11-20") != daily_seed("2026-11-21")


def test_difficulty_naik_per_wave():
    assert difficulty_for_wave(1)["count"] < difficulty_for_wave(5)["count"]
    assert difficulty_for_wave(1)["speed"] < difficulty_for_wave(5)["speed"]
    assert difficulty_for_wave(10)["type"] == "boss"


def test_spawn_wave_jumlah_dan_seed():
    rng_a = LCGRandom(99)
    rng_b = LCGRandom(99)
    wave_a = spawn_wave(3, rng_a)
    wave_b = spawn_wave(3, rng_b)
    assert wave_a == wave_b
    assert len(wave_a) == difficulty_for_wave(3)["count"]
    assert all(40 <= e["x"] <= 760 for e in wave_a)


def test_scoring_kombo():
    base = score_for_kill("scout", 0, 1)
    with_combo = score_for_kill("scout", 3, 1)
    assert with_combo > base
    assert score_for_kill("boss", 0, 1) > base
    assert wave_bonus(3) == 300


def test_validasi_skor():
    assert validate_run(5000, 3, 40, 120, 12)[0] is True
    assert validate_run(999999, 3, 40, 120, 12)[0] is False
    assert validate_run(1000, 0, 10, 120, 5)[0] is False
    assert validate_run(1000, 1, 10, 1, 5)[0] is False
