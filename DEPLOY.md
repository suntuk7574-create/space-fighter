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

Hak admin **tidak bisa diberikan oleh AI**. Cek dulu nama akun Windows kamu dengan:

```powershell
whoami
```

> Di laptop ini hasilnya `desktop-3htok8v\desktop`, dan akun **`desktop` sudah termasuk grup Administrators**. Nama GitHub `suntuk7574-create` **bukan** akun Windows, jadi tidak dipakai di sini.

Pilih salah satu:

1. Login Windows memakai akun yang sudah termasuk grup **Administrators**, lalu jalankan PowerShell/Installer dengan **Run as administrator**.
2. Kalau belum masuk, minta admin laptop menambahkan akun:
   - Buka **Computer Management → Local Users and Groups → Groups → Administrators → Add**.
   - Atau dari PowerShell admin:
     ```powershell
     net localgroup administrators "NAMA_AKUN_WINDOWS_KAMU" /add
     ```
     (ganti dengan hasil `whoami`, bukan username GitHub; **hanya bisa dijalankan oleh admin yang sudah ada**).

Setelah itu ikuti `INSTALL.md` dari langkah 2.

> Untuk deploy cloud, hak admin laptop **tidak diperlukan** karena database dan server ada di internet.

---

## 2. Repository GitHub (sudah terpasang)

Remote repo sudah memakai akun **`suntuk7574-create`**, bukan nama lama:

```powershell
git remote -v
# origin  https://github.com/suntuk7574-create/space-fighter.git
```

Untuk memastikan sudah ter-update:

```powershell
cd "C:\Users\desktop\Documents\Default Project\space-fighter"
git push origin main
```

File `render.yaml` sudah disiapkan di root repo, jadi Render bisa langsung memakai repo ini.

---

## 3. Buat database cloud gratis (Neon)

1. Buka https://neon.tech → daftar / Login dengan GitHub.
2. **Create project** → nama bebas, region pilih yang dekat.
3. Setelah jadi, buka **Connection Details** → salin connection string.
4. Salin connection string apa adanya. Tidak perlu diubah manual: backend otomatis mengubah `postgresql://...` menjadi driver `pg8000`.

```
postgresql://USER:PASSWORD@ep-xxx.region.aws.neon.tech/spacefighter?sslmode=require
```

> String di atas hanya contoh. Jangan pernah menaruhnya di `render.yaml` atau file yang ter-commit; isi lewat Environment Variable di dashboard Render.

Alternatif: **Supabase** (Database → Connection string → URI) atau **ElephantSQL**.

---

## 4. Deploy backend + frontend di Render (URL tetap)

Cara paling cepat memakai file `render.yaml` yang sudah ada:

1. Buka https://render.com → daftar / **Login dengan GitHub** (akun `suntuk7574-create`).
2. **New → Blueprint** → pilih repo `space-fighter` → branch `main`.
3. Render akan mendeteksi `render.yaml` otomatis. Saat diminta, isi Environment Variable:
   - `DATABASE_URL` = connection string Neon dari langkah 3
   - `ADMIN_USERNAME` = username admin pilihanmu
   - `ADMIN_PASSWORD` = password admin pilihanmu
   - `ADMIN_SECRET` sudah di-generate otomatis oleh Render
4. Klik **Apply**. Tunggu deploy selesai (status `Live`).
5. Buka URL permanen, misalnya:
   - `https://space-fighter.onrender.com/` → game
   - `https://space-fighter.onrender.com/docs` → dokumentasi API

URL `onrender.com` **tidak berubah** walaupun laptop dimatikan atau kode di-push ulang. Setiap `git push` ke `main` otomatis redeploy.

> Paket `free` di `render.yaml` membuat web service **sleep** setelah ±15 menit idle; buka pertama bisa ±1 menit. Kalau mau selalu hidup, ubah baris `plan: free` menjadi `plan: 0.5c-512mb` sebelum Apply.

**Cara manual (kalau tidak mau Blueprint):** **New → Web Service** → pilih repo yang sama → isi Build Command `pip install -r backend/requirements.txt`, Start Command `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`, Health Check Path `/health`, lalu isi env variable seperti di atas. Hasilnya sama.

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

**Perkiraan kapasitas (bukan batas hard-code):**

| Setup | Pemain aktif bersamaan | Catatan |
|---|---|---|
| Demo laptop + PostgreSQL portabel + Cloudflare quick tunnel | ±30–50 | Aman untuk demo kelas. Render 3D berjalan di browser tiap pemain; backend hanya request pendek (login, start, finish, leaderboard). Tunnel bisa mati saat laptop restart & URL berubah. |
| Render gratis + Neon gratis | ±20–40 | Web service gratis **sleep** setelah idle; cold start bisa ±1 menit. Cocok untuk demo, bukan SLA. |
| Render/ Railway berbayar + Neon berbayar + 2–4 worker | 100–500+ | Tambah connection pooling (`PgBouncer`) dan indexing kalau skor/riwayat membesar. |

Kenapa demo laptop masih ringan: arena Three.js, partikel, dan audio dihitung di perangkat pemain. Database hanya menyimpan akun, inventory, sesi, dan skor; request bersifat singkat. Beban-naik terjadi terutama saat banyak orang **login bersamaan** karena PBKDF2 120.000 round dipakai untuk hash password.

### Cara naik ke kapasitas lebih besar

1. **Deploy permanen** (langkah 3–4 di atas): Neon untuk DB + Render/Railway untuk backend. Ini menghilangkan masalah laptop mati dan URL berubah.
2. **Tambah worker**: di dashboard Render/Railway pakai minimal paket **Starter**, lalu ubah Start Command:
   ```bash
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
   ```
   Paket gratis biasanya hanya 1 worker, jadi `--workers` tidak akan efektif di sana.
3. **Connection pooling DB**: aktifkan **PgBouncer** di Neon/Supabase dan pakai connection string pooled. Ini mencegah antrean koneksi saat banyak request bersamaan.
4. **Indeks**: tambahkan indeks pada `scores(score DESC)`, `scores(player_id)`, dan `players(is_blocked)` kalau riwayat sudah besar.
5. **Cache leaderboard** 15–30 detik (Redis atau in-memory) + **rate limit** login/register. Ini menghemat DB saat banyak pemain membuka papan peringkat bersamaan.
6. **Di atas ~1000 pemain aktif**: baru perlu load balancer, beberapa instance, Redis, dan DB replica. Untuk tugas kuliah biasanya tidak sampai ke tahap ini.

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
