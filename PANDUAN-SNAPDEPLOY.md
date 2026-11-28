# Panduan Cloud Tanpa Kartu — SnapDeploy

Tujuan: game jalan di internet **walaupun laptop mati**. URL permanen, tanpa kartu kredit.

Ada dua akun yang perlu dibuat, **dua-duanya gratis dan tanpa kartu**:

1. **Neon** → menyimpan akun + skor (database).
2. **SnapDeploy** → menjalankan game (backend + frontend).

## Yang perlu kamu klik

### 0. Buat database dulu (Neon)

1. Buka **https://neon.tech** → **Login dengan GitHub** (`suntuk7574-create`).
2. **Create project** → nama bebas (misal `spacefighter`), region pilih yang dekat.
3. Buka **Connection Details** → salin connection string yang diawali `postgresql://...`.
4. String itu dipakai di langkah 3 berikutnya. Salin apa adanya — backend otomatis menyesuaikan driver-nya.

Tabel database akan dibuat otomatis saat game pertama kali dijalankan. Tidak perlu import manual. Jangan pernah taruh connection string di repo/chat; isi hanya lewat dashboard.

### 1. Daftar / login SnapDeploy

Buka **https://snapdeploy.dev/register**

- Bisa daftar dengan **GitHub** (`suntuk7574-create`) atau email.
- **Tidak diminta kartu kredit.**

### 2. Buat container

Di dashboard, klik **New Container** → pilih **GitHub repository**.

- Repository: **`space-fighter`**
- Branch: **`main`**
- Nama container: bebas, misalnya `space-fighter`
- Root directory: **kosongkan** (Dockerfile ada di root repo)
- Port: **8000** (atau biarkan auto-detect)
- Health check path: **`/health`**

Dockerfile sudah saya siapkan di repo, jadi SnapDeploy akan memakainya apa adanya.

### 3. Isi Environment Variable

Klik tab **Environment Variables**, tambahkan:

| Nama | Isi |
|---|---|
| `DATABASE_URL` | connection string dari Neon kamu (diawali `postgresql://...`) |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_PASSWORD` | password admin buatanmu sendiri |
| `ADMIN_DISPLAY_NAME` | `Administrator` |
| `ADMIN_SECRET` | string acak panjang buatanmu sendiri |

**Jangan isi `PORT`** — SnapDeploy yang mengatur otomatis.

Versi copy-paste untuk yang bukan rahasia:

```text
ADMIN_USERNAME=admin
ADMIN_DISPLAY_NAME=Administrator
```

Untuk `DATABASE_URL`, `ADMIN_PASSWORD`, dan `ADMIN_SECRET`, isi langsung di dashboard. **Jangan kirim ke chat dan jangan taruh di repo.**

### 4. Deploy

Klik **Deploy**. Tunggu sampai status **Healthy / Live** (biasanya 2–5 menit).

Deploy sudah berhasil. URL tetap game kamu:

```text
https://space-fighter-2a6cb.containers.snapdeploy.app
```

URL itu tidak berubah dan tetap jalan walaupun laptop dimatikan.

### 5. Cek

| Alamat | Harapan |
|---|---|
| `https://space-fighter-2a6cb.containers.snapdeploy.app/health` | `{"status":"ok","game":"Space Fighter"}` |
| `https://space-fighter-2a6cb.containers.snapdeploy.app/` | game tampil |
| `https://space-fighter-2a6cb.containers.snapdeploy.app/docs` | dokumentasi API |

Coba daftar akun dari HP (tanpa laptop menyala). Kalau muncul di leaderboard, berhasil.

---

## Penting soal paket gratis

- Free container **tidur setelah ±15 menit tanpa pengunjung**.
- Pengunjung pertama setelah itu menunggu **±1 menit** saat container bangun. Itu wajar.
- Kuota gratis: **100 jam/bulan** dan **10 deploy/hari**.
- Kalau mau **langsung hidup 24/7 tanpa menunggu**, di dashboard pilih:
  - **Sprint Pack $1 sekali** untuk 24 jam, atau
  - **Always-On Small $12/bulan** untuk permanen.

Setelah terhubung ke GitHub, setiap `git push` ke `main` otomatis redeploy.

---

## Kalau ada masalah

| Gejala | Apa yang dilakukan |
|---|---|
| Deploy failed, log `unexpected keyword argument 'sslmode'` | Sudah diperbaiki di kode: `sslmode` dari Neon diterjemahkan otomatis ke `ssl_context` pg8000. Pastikan repo sudah pull commit terbaru. |
| Health check gagal | Cek port 8000 dan Health Check Path `/health`. |
| Web 503/loading lama | Container sedang bangun dari sleep. Tunggu ±1 menit. |
| Error database | Cek project Neon tidak di-pause dan string DB masih benar. |
| Repo tidak muncul | Hubungkan GitHub di SnapDeploy, lalu pilih repo `space-fighter`. |

---

## Setelah live

Health sudah dicek dan README sudah diperbarui dengan URL di atas. Setiap `git push` ke `main` otomatis redeploy.
