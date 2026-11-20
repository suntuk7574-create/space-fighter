"""Logika murni Space Fighter (bisa di-test tanpa database).

Algoritma utama:
1. LCG (Linear Congruential Generator) -> seed harian menghasilkan spawn identik.
2. Difficulty scaling -> jumlah, kecepatan, dan HP musuh naik per wave.
3. Combo scoring -> poin = base + wave bonus + streak bonus.
4. Validasi skor -> batas wajar skor untuk mencegah submit palsu.
"""

import hashlib

MODULUS = 2**31
MULTIPLIER = 1103515245
INCREMENT = 12345

ENEMY_BASE = {"scout": 50, "raider": 80, "boss": 300}


class LCGRandom:
    """PRNG deterministik. Seed sama -> urutan spawn sama."""

    def __init__(self, seed: int):
        self.state = int(seed) % MODULUS

    def random(self) -> float:
        self.state = (MULTIPLIER * self.state + INCREMENT) % MODULUS
        return self.state / MODULUS

    def randint(self, low: int, high: int) -> int:
        return low + int(self.random() * (high - low + 1))

    def choice(self, sequence):
        return sequence[self.randint(0, len(sequence) - 1)]


def daily_seed(date_string: str) -> int:
    """Ubah tanggal (YYYY-MM-DD) jadi seed 31-bit yang stabil."""
    digest = hashlib.sha256(date_string.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % MODULUS


def difficulty_for_wave(wave: int) -> dict:
    """Konfigurasi musuh untuk suatu wave."""
    count = min(3 + wave, 10)
    speed = 60 + wave * 12
    hp = 1 if wave < 3 else 2 if wave < 6 else 3
    enemy_type = "boss" if wave % 5 == 0 else "raider" if wave % 2 == 0 else "scout"
    return {"count": count, "speed": speed, "hp": hp, "type": enemy_type}


def spawn_wave(wave: int, rng: LCGRandom, world_width: int = 800) -> list:
    """Buat daftar musuh untuk wave. Posisi x ditentukan rng."""
    cfg = difficulty_for_wave(wave)
    enemies = []
    for i in range(cfg["count"]):
        enemies.append(
            {
                "x": rng.randint(40, world_width - 40),
                "y": -40 - i * 55,
                "speed": cfg["speed"] + rng.randint(-10, 10),
                "hp": cfg["hp"],
                "type": cfg["type"],
            }
        )
    return enemies


def score_for_kill(enemy_type: str, combo: int, wave: int) -> int:
    """Poin musuh = base + bonus wave + bonus combo."""
    base = ENEMY_BASE.get(enemy_type, 50)
    return base + wave * 5 + combo * 10


def wave_bonus(wave: int) -> int:
    return wave * 100


def validate_run(score: int, wave: int, kills: int, duration: int, max_combo: int):
    """Cek kewajaran hasil run. Mengembalikan (valid, alasan)."""
    if wave < 1 or wave > 100:
        return False, "Wave di luar rentang."
    if duration < 5 or duration > 3600:
        return False, "Durasi tidak wajar."
    if kills < 0 or kills > 2000:
        return False, "Jumlah kill tidak wajar."
    if max_combo < 0 or max_combo > kills + 5:
        return False, "Combo melebihi jumlah kill."

    cap = kills * 400 + wave * 300 + max_combo * 20 + 5000 + duration * 5
    if score > cap:
        return False, "Skor melebihi batas wajar."
    return True, "OK"
