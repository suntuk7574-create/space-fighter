# 🚀 Space Fighter: Orbit Defense

Game **shoot-'em-up 3D** berbasis browser untuk tugas full-stack: **FastAPI + SQLAlchemy + PostgreSQL + Three.js**. Pemain mengendalikan spaceship dan mempertahankan orbit dari gelombang **kumbang alien**.

> **Demo publik (sementara):** https://internal-patricia-nancy-designs.trycloudflare.com
>
> Link tunnel gratis bisa berubah/expire. Untuk menyalakan ulang: `.\scripts\start-demo.ps1`

## ✨ Fitur

- Arena luar angkasa 3D: cincin orbit, nebula, planet bercincin, sabuk asteroid, bintang, dan debu kosmik (bukan grid datar).
- 3 spaceship futuristik: **Vanguard**, **Raptor**, **Phantom**.
- 5 senjata dengan perilaku berbeda: **Pulse Cannon**, **Twin Blaster**, **Ion Lance** (tembus 3 musuh), **Nova Scatter** (5 peluru), **Plasma Core** (damage 2).
- Musuh kumbang alien: **Scarab**, **Stag Beetle**, dan **Rhino Beetle** (boss tiap wave ke-5).
- **Seed harian** deterministik (SHA-256 + LCG) sehingga pola spawn sama untuk semua pemain.
- Akun, koin, inventory, item, riwayat sesi, dan **leaderboard global** tersimpan di database relasional.
- **Login pakai email + password** (email unik, username dibuat otomatis). Sesi tersimpan di browser → **auto-login**, tidak perlu login lagi saat membuka ulang link di perangkat yang sama.
- Radar/mini-map sektor, efek partikel, glow, dan kontrol sentuh.
- Halaman login/daftar bergaya landing page (orbit animasi, tab Login/Daftar) dan HUD game yang dipoles.
- **Admin console khusus satu akun**: statistik global + tabel pemain, skor, dan sesi. Dilindungi token HMAC 24 jam.

## 🛡️ Akses admin (khusus pemilik game)

Klik tombol **🛡️ Admin** → masukkan kredensial admin. Default: username `admin`, password `admin123`.
Ganti lewat environment variable sebelum deploy:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password-baru-anda
ADMIN_DISPLAY_NAME=Administrator
ADMIN_SECRET=string-acak-panjang
```

Hanya satu akun yang bisa menjadi admin; endpoint admin menolak request tanpa `X-Admin-Token` yang valid.

## 🛠️ Teknologi

| Lapisan | Teknologi |
|---|---|
| Backend | Python 3.15, FastAPI, SQLAlchemy ORM, Pydantic, PBKDF2 |
| Database | PostgreSQL (opsi MySQL/MariaDB didukung via URL SQLAlchemy) |
| Frontend | HTML5, CSS, JavaScript, Three.js (disimpan lokal di `frontend/vendor/`) |
| Testing | pytest |
| Deploy | Render + Neon (lihat `DEPLOY.md`), atau Cloudflare quick tunnel untuk demo |

## 📁 Struktur

```
space-fighter/
├── backend/
│   ├── app/          # main.py, models.py, schemas.py, game_logic.py, security.py
│   ├── tests/        # unit test game_logic
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html    # game 3D + integrasi REST
│   ├── index-2d.html # cadangan versi 2D
│   └── vendor/       # three.min.js (lokal, tanpa CDN)
├── scripts/
│   ├── start-demo.ps1    # PostgreSQL + backend + tunnel publik
│   └── setup-remote.ps1  # bantuan push GitHub
├── DOKUMENTASI.md    # ERD, algoritma, API, pembagian peran, AI agent
├── INSTALL.md        # instalasi lokal
└── DEPLOY.md         # deploy permanen Render + Neon
```

## ▶️ Menjalankan lokal

```powershell
# 1. siapkan database (lihat INSTALL.md), lalu:
cd backend
python -m pip install -r requirements.txt
copy .env.example .env   # isi DATABASE_URL
python -m uvicorn app.main:app --reload

# 2. buka http://127.0.0.1:8000
```

API docs otomatis: `http://127.0.0.1:8000/docs`

Jalankan tes:

```powershell
cd backend
python -m pytest -q
```

## 🌐 Deploy permanen

Ikuti **`DEPLOY.md`** untuk membuat database Neon dan web service Render. Repository ini sudah bisa langsung di-deploy dari GitHub.

## 📚 Dokumentasi

- [`DOKUMENTASI.md`](DOKUMENTASI.md) — dokumentasi tugas lengkap
- [`INSTALL.md`](INSTALL.md) — panduan instalasi
- [`DEPLOY.md`](DEPLOY.md) — panduan deploy

Dibuat dengan bantuan AI Coding Agent **OpenCode**. Seluruh aset visual dibuat prosedural dari geometri Three.js; tidak ada aset berhak cipta yang disalin.
