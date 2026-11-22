# 🚀 Space Fighter: Orbit Defense

Game **shoot-'em-up 3D** berbasis browser untuk tugas full-stack: **FastAPI + SQLAlchemy + PostgreSQL + Three.js**. Pemain mengendalikan spaceship dan mempertahankan orbit dari gelombang **kumbang alien**.

> **Demo publik (sementara):** https://applicants-rural-genres-subsequently.trycloudflare.com
>
> Link tunnel gratis bisa berubah/expire. Untuk menyalakan ulang: `.\scripts\start-demo.ps1`
>
> **Butuh internet?** Link publik di atas butuh internet. Kalau backend + PostgreSQL jalan di laptop sendiri, game bisa dibuka lewat `http://127.0.0.1:8000` tanpa internet (mode lokal). Akun/skor tetap tersimpan di DB lokal.

## ✨ Fitur

- Arena luar angkasa 3D: cincin orbit, nebula, planet bercincin, sabuk asteroid, bintang, dan debu kosmik (bukan grid datar).
- 6 spaceship futuristik dengan animasi 3D & **glow neon warna khas tiap pesawat**: **Vanguard** (biru), **Raptor** (oranye), **Phantom** (ungu), plus premium **SPECTRE** (mini & paling lincah, mint), **NOVA** (sayap sweep + inti emas), dan **TITAN** (kapaltempur besar, 4 mesin, hijau). Bilah sayap tajam, **meriam + kilat moncong di ujung sayap kiri/kanan**, lampu navigasi berkedip, api mesin, aura energi, dan jejak plasma makin terang saat pesawat bergerak. Senjata satu laras menyala bergantian kiri/kanan; Twin Blaster menyala dari dua sayap sekaligus; Nova Scatter menyebar dari kedua sisi. Premium dibeli di Shop dengan koin.
- 5 senjata dengan perilaku berbeda, semuanya kini berupa **bola api** (inti putih + ekor oranye + halo): **Pulse Cannon**, **Twin Blaster**, **Ion Lance** (tembus 3 musuh), **Nova Scatter** (5 bola api), **Plasma Core** (damage 2). Pesawat premium membuat bola api lebih besar dan lebih sakit: **SPECTRE ×1.4**, **NOVA ×1.7**, **TITAN ×2**.
- Musuh kumbang alien: **Scarab**, **Stag Beetle**, dan **Rhino Beetle** (boss tiap wave ke-5).
- **Power-up jatuh dari alien**: 💚 Repair (+1 nyawa, maks 6), ⚡ Rapid Fire (cooldown ×0.55 selama 6 detik), 🛡️ Shield (menyerap 1–2 serangan), 🔥 Surge (bola api ×1.5 + lebih besar selama 6 detik), dan 🪙 Bonus skor +200. Status aktif tampil di HUD.
- **Suara game sintetis** pakai Web Audio API (tembakan, ledakan, pickup, damage, shield, fanfare sektor, musik ambien). Tanpa file audio eksternal; bisa dibisu lewat tombol 🔊 atau tombol `M`.
- **Menu loadout lebih rapi**: preview pesawat + stat (kecepatan, damage, fire rate, agilitas, DPS), tag stat di tiap kartu pesawat/senjata, dan daftar item yang dipakai.
- **Seed harian** deterministik (SHA-256 + LCG) sehingga pola spawn sama untuk semua pemain.
- Akun, koin, inventory, item, riwayat sesi, dan **leaderboard global** tersimpan di database relasional.
- **Login pakai email + password** (email unik, username dibuat otomatis). Sesi tersimpan di browser → **auto-login**, tidak perlu login lagi saat membuka ulang link di perangkat yang sama.
- Radar/mini-map sektor, efek partikel, glow, dan kontrol: keyboard (A/D, ←/→, SPACE), tombol sentuh ◀ ▶ 🔫 di HP, atau geser jari untuk mengarahkan pesawat. Tampilan game melebar penuh di layar HP + tombol layar penuh.
- **Mode hemat daya otomatis di HP**: pixel ratio diturunkan, antialias dimatikan, jumlah bintang/debu/asteroid/jejak plasma dipangkas, dan api mesin disederhanakan. Kualitas tetap tinggi di desktop.
- Halaman login/daftar bergaya landing page (orbit animasi, tab Login/Daftar) dan HUD game yang dipoles.
- **Admin console khusus satu akun**: tombol/admin login **disembunyikan dari pemain biasa**. Pemilik membuka pintu masuk lewat `?admin=1` sekali, lalu token HMAC 24 jam membuat tombol 🛡️ Admin muncul di perangkatnya saja.
- **Hak blokir admin**: dari tabel Pemain, admin bisa **Blokir / Buka blokir** akun. Pemain diblokir tidak bisa login, mulai sesi, beli item, atau masuk leaderboard; skor terakhirnya tetap ditolak. **Peringkat lawan tetap bisa dilihat semua pemain** lewat Leaderboard.

## 🛡️ Akses admin (khusus pemilik game)

Buka URL game dengan parameter portal pribadi (disimpan pemilik sebagai bookmark, **jangan dibagikan**) → tombol **🛡️ Masuk sebagai Admin** akan muncul → masukkan kredensial admin dari environment variable berikut:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password-baru-anda
ADMIN_DISPLAY_NAME=Administrator
ADMIN_SECRET=string-acak-panjang
```

Hanya satu akun yang bisa menjadi admin; endpoint admin menolak request tanpa `X-Admin-Token` yang valid. Tombol admin otomatis hilang untuk pemain biasa.

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
