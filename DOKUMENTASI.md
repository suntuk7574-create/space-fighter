# Space Fighter — Dokumentasi Proyek

## 1. Identitas & Konsep Game

**Nama:** Space Fighter: Orbit Defense
**Genre:** Arcade / Space Shooter (web-based)
**Tema:** Pemain mengendalikan pesawat di orbit dan menahan gelombang musuh agar Bumi tetap aman.

**Mekanisme singkat:**
- Pemawat menggerakkan pesawat (A/D atau ←/→) dan menembak (SPACE).
- Musuh turun dari atas dalam **wave**. Setiap wave jumlah, kecepatan, dan HP musuh meningkat.
- Menembak musuh memberi poin; **combo** bertambah jika menembak terus-menerus dan reset saat terkena musuh / musuh kabur.
- Ada 3 nyawa. Item **Pelindung** menambah 1 nyawa, **Rapid Fire** mempercepat tembakan.
- Musuh berupa **kumbang alien**: `scout` (Scarab), `raider` (Stag Beetle), dan `boss` (Rhinoceros Beetle, muncul tiap wave ke-5).
- Power-up acak: `repair` (+1 nyawa) dan `coin` (+200 skor).
- Skor akhir dikirim ke backend, divalidasi, lalu masuk **leaderboard** dan memberi **koin**.
- Akun memakai **email + password** (email unik, username otomatis jika tidak diisi). Setelah login pertama, ID sesi disimpan di `localStorage` sehingga **auto-login** saat link dibuka ulang di perangkat yang sama.

**Fitur pembeda:** **Seed harian**. Backend membuat seed dari tanggal memakai SHA-256; frontend memakai LCG dengan seed yang sama sehingga pola spawn musuh reproducible untuk semua pemain pada hari itu.

**Tampilan:** game dirender dalam **3D menggunakan Three.js**. Medan perangnya adalah **arena orbit luar angkasa** (cincin pertahanan melingkar, nebula berlapis, planet bercincin + satelit, sabuk asteroid dan kristal bercahaya, bintang berkedip, serta debu kosmik), bukan bidang grid kotak. **Musuh berupa kumbang alien** yang dibuat prosedural: cangkang, sayap keras (elytra), enam kaki, antena, mata majemuk bercahaya, taring dan tanduk. **Pesawat tetap spaceship futuristik** dengan 3 model (Vanguard, Raptor, Phantom) dan 5 pilihan senjata (Pulse Cannon, Twin Blaster, Ion Lance yang menembus musuh, Nova Scatter 5 peluru, dan Plasma Core damage 2). Pilihan loadout disimpan di `localStorage`. Radar/sektor mini-map ada di sudut kanan atas. Versi 2D canvas tetap disimpan sebagai `frontend/index-2d.html` sebagai cadangan.

---

## 2. Algoritma & Logika Pemrograman

| Algoritma | Lokasi | Fungsi |
|---|---|---|
| LCG (Linear Congruential Generator) | `app/game_logic.py`, `frontend/index.html` | Menghasilkan urutan acak deterministik dari seed harian. |
| SHA-256 seed generation | `daily_seed()` | Mengubah tanggal menjadi angka seed 31-bit yang stabil. |
| Difficulty scaling | `difficulty_for_wave()` | Jumlah musuh `3+wave` (max 10), kecepatan `60+12*wave`, HP naik di wave 3 & 6. |
| Combo scoring | `score_for_kill()` | `poin = base + wave*5 + combo*10`. |
| Collision detection (AABB sederhana) | `frontend/index.html` | Cek tabrakan peluru–musuh dan musuh–pesawat; mendukung damage dan peluru penembus (`pierce`). |
| Weapon spread & pierce | `fireWeapon()` | Menyebarkan 5 peluru (Nova Scatter), menembak 2 sejajar (Twin), atau menembus 3 musuh (Ion Lance). |
| Validasi skor | `validate_run()` | Membatasi skor tidak wajar berdasarkan kill, wave, combo, dan durasi. |
| Fisher-Yates (cadangan di proyek Fruit Door) | `fruitdoor/backend/app/game_logic.py` | Referensi pengacakan unbiased. |

---

## 3. Arsitektur & Integrasi

```
[ Browser / Canvas JS ]  --REST/JSON-->  [ FastAPI ]  --SQLAlchemy-->  [ PostgreSQL ]
        frontend/index.html              backend/app/                   database
```

- Frontend **tidak** menyimpan skor permanen; semua data akhir dikirim ke API.
- Backend memakai **FastAPI** (wajib) dan **SQLAlchemy ORM** (wajib).
- Django / Phaser / Three.js **tidak dipakai** agar tidak butuh Node.js (tidak tersedia di laptop).
- CORS dibuka untuk development (`file://` dan `localhost`).

---

## 4. Struktur Database & Relasi

```mermaid
erDiagram
    PLAYERS ||--o{ GAME_SESSIONS : has
    PLAYERS ||--o{ SCORES : has
    PLAYERS ||--o{ PLAYER_ITEMS : owns
    ITEMS   ||--o{ PLAYER_ITEMS : stored_as
    GAME_SESSIONS ||--o| SCORES : produces

    PLAYERS {
        int id PK
        string username UK
        string display_name
        string password_hash
        int coins
        int total_score
        int best_score
        datetime created_at
    }
    ITEMS {
        string code PK
        string name
        string description
        int price
    }
    PLAYER_ITEMS {
        int player_id PK_FK
        string item_code PK_FK
        int quantity
    }
    GAME_SESSIONS {
        int id PK
        int player_id FK
        int seed
        string status
        bool shield_active
        bool rapid_active
        int score
        int wave
        int enemies_killed
        int max_combo
        int duration_seconds
        datetime created_at
        datetime finished_at
    }
    SCORES {
        int id PK
        int player_id FK
        int session_id FK_UK
        int score
        int wave
        int enemies_killed
        int max_combo
        int duration_seconds
        bool validated
        datetime created_at
    }
```

---

## 5. REST API

Base URL: `http://localhost:8000`
Dokumentasi otomatis: `http://localhost:8000/docs`

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/health` | Cek status server |
| POST | `/api/players/register` | Daftar pemain (body: `email`, `display_name`, `password`, username opsional) |
| POST | `/api/players/login` | Login pakai email (body: `identifier`/`email`, `password`; username lama tetap didukung) |
| GET | `/api/players/{id}` | Detail profil |
| GET | `/api/items` | Daftar item |
| GET | `/api/players/{id}/inventory` | Inventory pemain |
| POST | `/api/players/{id}/items/{code}/buy` | Beli item |
| POST | `/api/games/start` | Mulai sesi (body: `player_id`, `equip`) |
| GET | `/api/games/{session_id}` | Ambil sesi |
| POST | `/api/games/{session_id}/finish` | Kirim hasil run |
| GET | `/api/leaderboard?limit=10` | Papan peringkat |
| GET | `/api/players/{id}/history` | Riwayat permainan |
| POST | `/api/admin/login` | Login admin tunggal → token HMAC |
| GET | `/api/admin/stats` | Statistik global (butuh `X-Admin-Token`) |
| GET | `/api/admin/players` | Daftar semua pemain |
| GET | `/api/admin/scores` | Riwayat skor terakhir |
| GET | `/api/admin/sessions` | Riwayat sesi terakhir |

**Admin khusus:** hanya ada satu akun admin (`ADMIN_USERNAME`, default `admin`). Endpoint admin menolak permintaan tanpa token yang ditandatangani HMAC dengan `ADMIN_SECRET` (berlaku 24 jam). Token tidak bisa dipalsukan hanya dengan mengubah `player_id`. Di frontend, tombol **🛡️ Admin** membuka konsol berisi statistik, tabel pemain, skor, dan sesi. Kredensial default sebaiknya diganti lewat environment variable sebelum deploy.

Contoh `POST /api/games/1/finish`:

```json
{
  "score": 8420,
  "wave": 4,
  "enemies_killed": 38,
  "max_combo": 12,
  "duration_seconds": 143
}
```

Respons:

```json
{
  "valid": true,
  "reason": "OK",
  "score": 8420,
  "rank": 2,
  "coins_earned": 108
}
```

---

## 6. Cara Menjalankan

> **Catatan laptop:** Node.js/npm tidak tersedia, PostgreSQL belum terpasang, dan akun saat ini bukan administrator. Langkah DB memerlukan hak admin.

1. Pasang PostgreSQL (atau MySQL/MariaDB) dengan hak administrator.
2. Buat database `spacefighter` dan user sesuai `backend/.env.example`.
3. Salin `backend/.env.example` menjadi `backend/.env`, lalu ubah `DATABASE_URL` sesuai user/password database Anda. (Bisa juga memakai environment variable.)
4. Masuk folder backend dan install dependency:
   ```powershell
   pip install -r requirements.txt
   ```
5. Jalankan server:
   ```powershell
   uvicorn app.main:app --reload
   ```
6. Buka `frontend/index.html` di browser, isi alamat API `http://localhost:8000`, lalu daftar/Login.
7. Test logika tanpa database:
   ```powershell
   pytest -q
   ```

---

## 7. Penggunaan AI Coding Agent & Skills

- **AI Agent:** OpenCode — dipakai untuk merancang arsitektur, membuat model SQLAlchemy, endpoint FastAPI, logika game, dan frontend 3D (Three.js).
- **Tools/Skill:** Browser skill — dipakai untuk memprevieu dan menguji game HTML sebelumnya (Fruit Door) serta memeriksa error konsol.
- **Pendekatan instruksi:** Instruksi ringkas dan inkremental (gaya *Caveman*) dipakai saat iterasi fitur.
- **REA:** Tidak dipakai. Seluruh aset dan mekanisme dibuat sendiri (emoji + geometri Three.js), sehingga tidak ada konten berhak cipta yang disalin. Pustaka Three.js (MIT) disimpan lokal di `frontend/vendor/three.min.js`.
- **UI/UX:** Desain panel gelap, HUD jelas, kontrol keyboard ditampilkan di layar.

Dokumentasi ini dapat dilengkapi tim dengan prompt/conversation log sesuai format dosen.

---

## 8. Pembagian Tugas Tim (template)

| Peran | Bagian |
|---|---|
| Backend 1 | Model & migrasi SQLAlchemy, koneksi DB |
| Backend 2 | Endpoint FastAPI, validasi skor, leaderboard |
| Frontend 1 | Scene 3D Three.js, model spaceship & kumbang alien musuh, arena orbit luar angkasa, radar mini-map, game loop, kontrol, collision |
| Frontend 2 | Integrasi REST, auth panel, shop, leaderboard UI |
| Dokumentasi | Diagram ER, dokumentasi API, catatan AI agent |
| Testing | Unit test `game_logic.py`, uji manual end-to-end |

---

## 9. Checklist Ketentuan Tugas

- [x] FastAPI sebagai backend
- [x] SQLAlchemy ORM
- [x] Target DB relasional PostgreSQL (opsi MySQL/MariaDB tersedia)
- [x] REST API frontend ↔ backend
- [x] Penyimpanan data: akun, progres, skor, inventory, riwayat
- [x] Frontend web 3D terintegrasi (tanpa Node.js untuk menjalankan proyek)
- [x] AI Coding Agent (OpenCode) + tools
- [x] Algoritma & logika jelas dan dapat di-test
- [x] Identitas visual & gameplay dapat dimainkan
- [x] Dokumentasi API, database, konsep, AI agent
- [ ] Demo live setelah DB terpasang
- [ ] Presentasi & pemahaman kode oleh seluruh anggota
