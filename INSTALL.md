# Panduan Install Database & Dependency — Space Fighter

> **Status:** baru panduan. Belum ada instalasi yang saya jalankan.
> Jalankan langkah di bawah **setelah** kamu mendapat hak administrator.

---

## 0. Prasyarat & kondisi laptop saat ini

| Item | Kondisi | Tindakan |
|---|---|---|
| Python 3.15.2 | ✅ sudah ada | tidak perlu install |
| pip 26.2.2 | ✅ sudah ada | pakai `python -m pip` |
| Node.js / npm | ❌ tidak ada | **tidak diperlukan** |
| PostgreSQL / MySQL / MariaDB | ❌ belum ada | install di langkah 3 |
| Hak administrator | ❌ belum aktif | wajib untuk install DB |
| RAM kosong | ±0,66 GB | tutup Chrome/Edge atau restart dulu |

Cek hak admin (jalankan di PowerShell biasa):

```powershell
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

- `True` → lanjut.
- `False` → klik kanan PowerShell → **Run as administrator**, atau login pakai akun admin.

Cek RAM kosong:

```powershell
Get-CimInstance Win32_OperatingSystem | Select @{N='RAM_Kosong_GB';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}
```

Sebaiknya RAM kosong **minimal 1,5 GB** sebelum install.

---

## 1. Ringkasan yang akan dipasang

1. PostgreSQL Server + pgAdmin + Command Line Tools
2. Library Python: `fastapi`, `uvicorn`, `SQLAlchemy`, `pydantic`, `psycopg[binary]`, `python-dotenv`, `pytest`

Perkiraan ruang disk: **~500 MB – 1 GB**. Disk kamu masih ~375 GB, jadi aman.

---

## 2. Instal PostgreSQL

1. Download installer PostgreSQL (Windows x86-64):
   https://www.enterprisedb.com/downloads/postgres-post-sql-download
   Pilih versi terbaru yang tersedia (mis. 17/18).
2. **Klik kanan installer → Run as administrator.**
3. Saat ditanya komponen, centang:
   - `PostgreSQL Server`
   - `pgAdmin 4`
   - `Command Line Tools`
4. Set password untuk user `postgres` → **catat password ini**.
   Contoh: `postgres123` (boleh bebas, tapi pakai yang Kuat).
5. Port biarkan **`5432`**. Jika ada konflik, ganti mis. `5433` dan sesuaikan URL nanti.
6. Locale: default saja.
7. Selesai installer. Jika ditanya Stack Builder, bisa **Skip**.
8. Cek service berjalan:

```powershell
Get-Service -Name 'postgresql*'
```

Status harus `Running`. Jika tidak:

```powershell
Start-Service 'postgresql-x64-18'   # ganti nama sesuai hasil Get-Service
```

---

## 3. Buat database & user khusus game

Buka **SQL Shell (psql)** dari Start Menu, tekan Enter saja sampai diminta password `postgres`, lalu jalankan:

```sql
CREATE USER sf_user WITH PASSWORD 'sf_pass';
CREATE DATABASE spacefighter OWNER sf_user;
\c spacefighter
GRANT ALL ON SCHEMA public TO sf_user;
```

Keluar dengan:

```sql
\q
```

Verifikasi:

```powershell
pg_isready -h localhost -p 5432
psql -U sf_user -d spacefighter -c "SELECT current_database(), current_user;"
```

> Alternatif: kalau mau pakai user `postgres` saja, cukup buat database:
> ```sql
> CREATE DATABASE spacefighter;
> ```
> lalu URL memakai `postgres:password-anda`.

---

## 4. Konfigurasi `.env`

Buka PowerShell di folder backend:

```powershell
cd "C:\Users\desktop\Documents\Default Project\space-fighter\backend"
Copy-Item .env.example .env
notepad .env
```

Ubah baris `DATABASE_URL` menjadi:

```
DATABASE_URL=postgresql+psycopg://sf_user:sf_pass@localhost:5432/spacefighter
```

Simpan. Jangan pernah meng-commit file `.env` ke Git (sudah ada `.gitignore`).

---

## 5. Install dependency Python

Masih di folder `backend`:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Cek berhasil:

```powershell
python -m pip show fastapi SQLAlchemy psycopg python-dotenv
```

---

## 6. Jalankan backend

```powershell
uvicorn app.main:app --reload
```

Jika `uvicorn` tidak dikenali:

```powershell
python -m uvicorn app.main:app --reload
```

Saat startup, aplikasi otomatis:
- membuat tabel `players`, `items`, `player_items`, `game_sessions`, `scores`
- mengisi 2 item awal: `shield` dan `rapid`

Cek di browser:
- http://localhost:8000/health → `{"status":"ok","game":"Space Fighter"}`
- http://localhost:8000/docs → dokumentasi API otomatis

Cek tabel dari psql:

```powershell
psql -U sf_user -d spacefighter -c "\dt"
```

---

## 7. Jalankan test logika

```powershell
python -m pytest -q
```

Harus muncul `6 passed`.

---

## 8. Jalankan frontend

Buka:

```
C:\Users\desktop\Documents\Default Project\space-fighter\frontend\index.html
```

Di kolom **Alamat API Backend** isi:

```
http://localhost:8000
```

Lalu:
1. Daftar pilot (username, nama, password).
2. Buka Shop → beli item jika ingin (koin awal 0, jadi main dulu untuk dapat koin).
3. Klik **Mulai Serangan**.
4. A/D atau ←/→ = gerak, SPACE = tembak, P = pause.
5. Setelah mati, skor otomatis masuk leaderboard.

---

## 9. Alternatif MySQL / MariaDB (jika PostgreSQL sulit)

1. Install MySQL/MariaDB sebagai administrator, buat database `spacefighter` dan user.
2. Tambahkan driver ke `requirements.txt`:
   ```
   pymysql
   ```
3. Ubah `.env`:
   ```
   DATABASE_URL=mysql+pymysql://sf_user:sf_pass@localhost:3306/spacefighter
   ```
   atau
   ```
   DATABASE_URL=mariadb+mariadbconnector://sf_user:sf_pass@localhost:3306/spacefighter
   ```
   (untuk MariaDB connector tambahkan `mariadb` ke requirements).
4. Ulangi langkah 5–8.

---

## 10. Troubleshooting umum

| Masalah | Penyebab | Solusi |
|---|---|---|
| `password authentication failed` | Password di `.env` salah | Samakan dengan password saat install |
| `connection refused` | Service DB mati | `Get-Service postgresql*` lalu `Start-Service ...` |
| `database "spacefighter" does not exist` | DB belum dibuat | Ulangi langkah 3 |
| `psycopg` gagal install | pip lama / Python 32-bit | `python -m pip install -U pip`; pastikan Python 64-bit |
| Port 5432 bentrok | Ada DB lain | Ganti port & URL, mis. `localhost:5433` |
| Frontend “Server offline” | Backend belum jalan / URL salah | Jalankan uvicorn, cek kolom API |
| CORS error | Backend tidak aktif | Pastikan `http://localhost:8000/health` ok |
| `.env` tidak terbaca | File salah folder | Harus di `backend/.env`, bukan root |
| Laptop lelet saat install | RAM mepet | Tutup Chrome/Edge, restart, atau tambah RAM |

---

## 11. Perintah berguna (ringkas)

```powershell
# Cek service DB
Get-Service -Name 'postgresql*'

# Cek koneksi DB
pg_isready -h localhost -p 5432

# Masuk DB
psql -U sf_user -d spacefighter

# Jalankan server
cd "C:\Users\desktop\Documents\Default Project\space-fighter\backend"
python -m uvicorn app.main:app --reload

# Test
python -m pytest -q
```

---

Setelah semua langkah berhasil, demo siap dipresentasikan: daftar akun → main → skor masuk leaderboard → tunjukkan tabel di DB dan dokumentasi API `/docs`.
