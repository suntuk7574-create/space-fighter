# Deploy Space Fighter agar Bisa Diakses Banyak Orang

## 0. Apa yang sudah dan belum

**Sudah siap di kode:**
- Frontend ikut disajikan oleh FastAPI → **cukup satu URL** untuk game + API + `/docs`.
- API otomatis memakai `location.origin` saat diakses lewat `http/https`, jadi tidak perlu ubah alamat API manual.
- Leaderboard, akun, inventory, dan riwayat tersimpan di database → pemain berbeda melihat skor yang sama.
- CORS bisa diatur lewat `FRONTEND_ORIGIN`.

**Catatan konsep:** game ini adalah **arcade dengan leaderboard global/asinkron**, bukan *real-time PvP* dua pemain dalam satu arena. Banyak orang bisa main bersamaan dan saling melihat peringkat. Kalau dosen/host ingin *real-time multiplayer*, itu fitur tambahan terpisah.

**Tidak bisa saya lakukan sendiri:** membuat akun cloud, memasukkan kartu/billing, dan memberi hak admin Windows. Semua itu butuh akun & tindakan kamu. Saya hanya menyiapkan kode + langkah pastinya.

---

## 1. Cara aman mendapat hak admin (laptop)

Hak admin **tidak bisa diberikan oleh AI**. Pilih salah satu:

1. Login Windows memakai akun yang sudah termasuk grup **Administrators**, lalu jalankan PowerShell/Installer dengan **Run as administrator**.
2. Minta admin laptop menambahkan akun kamu:
   - Buka **Computer Management → Local Users and Groups → Groups → Administrators → Add**.
   - Atau dari PowerShell admin:
     ```powershell
     net localgroup administrators "Zulkarnain" /add
     ```
     (ganti nama akun; **hanya bisa dijalankan oleh admin yang sudah ada**).

Setelah itu ikuti `INSTALL.md` dari langkah 2.

> Untuk deploy cloud, hak admin laptop **tidak diperlukan** karena database dan server ada di internet.

---

## 2. Siapkan repository GitHub

Repo sudah di-init lokal dengan commit `a696c15`. Tambahkan remote (ganti URL milikmu):

```powershell
cd "C:\Users\desktop\Documents\Default Project\space-fighter"
git remote add origin https://github.com/USERNAME/space-fighter.git
git push -u origin main
```

Kalau belum punya repo: buat di github.com → **New repository** → jangan centang README (biar kosong) → salin URL-nya.

---

## 3. Buat database cloud gratis (Neon)

1. Buka https://neon.tech → daftar / Login dengan GitHub.
2. **Create project** → nama bebas, region pilih yang dekat.
3. Setelah jadi, buka **Connection Details** → salin connection string.
4. Ubah menjadi format SQLAlchemy driver `pg8000` dan tambahkan SSL:

```
DATABASE_URL=postgresql+pg8000://USER:PASSWORD@ep-xxx.region.aws.neon.tech/spacefighter?sslmode=require
```

> Ganti `postgres://` di awal dengan `postgresql+pg8000://`, lalu tambahkan `?sslmode=require` di akhir.

Alternatif: **Supabase** (Database → Connection string → URI) atau **ElephantSQL**.

---

## 4. Deploy backend + frontend di Render

1. Buka https://render.com → daftar / Login dengan GitHub.
2. **New → Web Service** → pilih repo `space-fighter`.
3. Isi:
   - **Name:** `space-fighter`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```
     pip install -r backend/requirements.txt
     ```
   - **Start Command:**
     ```
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
4. Masuk tab **Environment** → **Add Environment Variable**:
   - `DATABASE_URL` = string Neon dari langkah 3
   - `PYTHON_VERSION` = `3.11` (atau versi yang tersedia; kode kompatibel)
   - `FRONTEND_ORIGIN` → **kosongkan** karena frontend satu origin dengan API
5. **Health Check Path:** `/health`
6. Klik **Create Web Service**. Tunggu deploy selesai.
7. Buka URL yang diberikan, misalnya:
   - `https://space-fighter.onrender.com/` → game
   - `https://space-fighter.onrender.com/docs` → dokumentasi API
8. Bagikan URL itu ke teman/tim. Mereka bisa daftar akun dan skor masuk leaderboard yang sama.

---

## 5. Alternatif host lain

**Railway** (`https://railway.app`):
- New Project → Deploy from GitHub repo.
- Variable: `DATABASE_URL`.
- Start command sama seperti Render.

**Fly.io** (`https://fly.io`):
- `fly launch`, lalu `fly secrets set DATABASE_URL="..."`, lalu `fly deploy`.

**Tunnel publik tanpa akun (demo cepat):**
```powershell
.\scripts\start-demo.ps1
```
Skrip menyalakan PostgreSQL portabel + backend + Cloudflare Tunnel. Beberapa detik kemudian muncul URL seperti `https://xxxx.trycloudflare.com` yang bisa langsung dibagikan. Tidak butuh akun GitHub/Render/Neon maupun hak admin. Kekurangannya: URL berubah setiap dijalankan ulang dan mati kalau laptop/terminal ditutup. Untuk URL permanen tetap gunakan Render.

**Lokal tapi bisa diakses LAN** (tanpa cloud):
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Lalu teman di WiFi yang sama buka `http://IP-LAPTOP-KAMU:8000`. Firewall Windows bolehkan port 8000. Ini hanya untuk demo lokal, bukan internet publik.

---

## 6. Verifikasi setelah deploy

| Cek | Harapan |
|---|---|
| `GET /health` | `{"status":"ok","game":"Space Fighter"}` |
| `GET /docs` | Swagger UI tampil |
| `GET /` | Tampilan game Space Fighter |
| Daftar 2 akun di 2 browser | Keduanya bisa login |
| Main lalu buka Leaderboard | Skor kedua akun muncul |
| `GET /api/leaderboard` | JSON berisi peringkat |

---

## 7. Catatan untuk “banyak orang”

- Paket **gratis** Render/Neon biasanya **sleep** saat tidak dipakai dan punya batas koneksi. Untuk puluhan pemain simultan, naikkan ke paket berbayar.
- Jangan simpan password di kode/`.env` yang ter-commit. Memakai Environment Variable di dashboard host sudah aman.
- Kalau ada ribuan pemain, tambahkan indexing/indeks dan connection pooling (mis. PgBouncer). Untuk tugas kuliah, konfigurasi saat ini sudah memadai.
- Pastikan `FRONTEND_ORIGIN` diisi hanya jika frontend dipisah ke domain lain; kalau tidak, biarkan kosong.

---

## 8. Status checklist tugas setelah deploy

- [x] Source frontend + backend
- [x] Database + struktur tabel & relasi
- [x] Dokumentasi API (`/docs`)
- [x] Dokumentasi konsep & mekanisme
- [x] Dokumentasi AI Agent & skills
- [x] Gameplay dapat dimainkan
- [x] Integrasi frontend–backend
- [x] Git repo + commit awal
- [ ] Database cloud aktif
- [ ] Web service aktif & URL dibagikan
- [ ] Demo + presentasi ke dosen
