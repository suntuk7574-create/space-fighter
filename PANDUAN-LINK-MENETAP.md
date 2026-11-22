# Panduan Membuat Link yang Tidak Berubah

Link demo sekarang memakai Cloudflare tunnel gratis: mati kalau laptop restart dan URL bisa ganti.
Ikuti panduan ini supaya dapat **URL permanen** dari Render.

> Aturan penting: **jangan kirim password, connection string database, atau token ke chat.**
> Isi semua langsung di website Render/Neon.

---

## Bagian 1 — Buat Database gratis di Neon

1. Buka **https://neon.tech** di browser.
2. Klik **Login / Sign up with GitHub**.
3. Kalau diminta, setujui/authorize akun GitHub **`suntuk7574-create`**.
4. Klik **Create project**.
   - **Name:** `space-fighter`
   - **Region:** pilih yang paling dekat (mis. Singapore), kalau ada
   - Klik **Create**
5. Di halaman project, cari **Connection Details** atau **Connection String**.
6. Copy string yang diawali dengan:

   ```text
   postgresql://
   ```

   Contoh bentuknya (jangan dipakai ini, punya kamu sendiri):

   ```text
   postgresql://user:pass@ep-xxx.region.aws.neon.tech/spacefighter?sslmode=require
   ```

7. Tempel sementara di Notepad. **Jangan** taruh di chat atau di file repo.

> Backend sudah otomatis mengubah `postgresql://...` menjadi driver `pg8000`,
> jadi tidak perlu diedit apa-apa.

---

## Bagian 2 — Deploy di Render

1. Buka **https://render.com**.
2. Klik **Login / Sign Up with GitHub**.
3. Setujui akun GitHub **`suntuk7574-create`**.
4. Klik **New → Blueprint**.
5. Pilih repo **`space-fighter`**.
   - Kalau repo belum muncul, klik **Configure account / Install GitHub App**, lalu centang `space-fighter`.
6. Pilih branch **`main`**, lalu lanjut.
7. Render akan membaca file `render.yaml` yang sudah ada di repo.
8. Isi Environment Variable yang muncul:

   | Nama | Diisi dengan |
   |---|---|
   | `DATABASE_URL` |string dari Neon langkah 1.6 |
   | `ADMIN_USERNAME` | username admin pilihanmu, misal `admin` |
   | `ADMIN_PASSWORD` | password admin buatanmu sendiri |
   | `ADMIN_DISPLAY_NAME` | `Administrator` (sudah terisi) |
   | `ADMIN_SECRET` | otomatis, **jangan diubah** |
   | `PYTHON_VERSION` | `3.11` (sudah terisi) |

### Versi copy-paste

Salin **nilainya saja** (yang ada di dalam kotak) ke field yang bersangkutan:

**Field `DATABASE_URL`** — tempel dari Neon kamu:

```text
postgresql://USER:PASSWORD@ep-xxx.region.aws.neon.tech/spacefighter?sslmode=require
```

> Di atas hanya contoh. Yang asli ada di halaman Neon kamu. Saya tidak bisa mengisinya karena itu kredensialmu.

**Field `ADMIN_USERNAME`**:

```text
admin
```

**Field `ADMIN_PASSWORD`** (boleh pakai ini, atau ganti sesukamu):

```text
SfAdmin_2026!
```

**Jangan disentuh:**
- `ADMIN_DISPLAY_NAME` → biarkan `Administrator`
- `ADMIN_SECRET` → biarkan kosong, Render yang mengisi
- `PYTHON_VERSION` → biarkan `3.11`

9. Klik **Apply**.
10. Tunggu sampai status service berubah jadi **Live** (hijau). Biasanya 2–5 menit.

---

## Bagian 3 — URL permanen kamu

Setelah `Live`, Render akan menampilkan URL seperti:

```text
https://space-fighter.onrender.com
```

URL itu **tidak berubah** walaupun:
- laptop kamu mati,
- internet laptop putus,
- kamu `git push` ulang.

Kalau nama sudah dipakai orang lain, Render akan menambahkan akhiran, misalnya:

```text
https://space-fighter-abc123.onrender.com
```

Itu tetap permanen.

---

## Bagian 4 — Cek bahwa berhasil

Buka tiga alamat ini:

| Alamat | Harapan |
|---|---|
| `https://...onrender.com/health` | tampil `{"status":"ok","game":"Space Fighter"}` |
| `https://...onrender.com/` | game Space Fighter muncul |
| `https://...onrender.com/docs` | halaman dokumentasi API |

Lalu coba:
1. Daftar akun di browser A.
2. Daftar akun lain di browser B / HP.
3. Main sebentar, buka **Leaderboard**.
4. Kedua skor harus muncul di papan peringkat yang sama.

---

## Bagian 5 — Masuk sebagai admin (khusus kamu)

1. Buka:

   ```text
   https://...onrender.com/?admin=1
   ```

2. Akan muncul tombol **🛡️ Masuk sebagai Admin**.
3. Masukkan `ADMIN_USERNAME` dan `ADMIN_PASSWORD` yang kamu isi di Render.
4. Setelah login, tombol 🛡️ Admin muncul di perangkatmu saja.
5. Jangan bagikan `?admin=1` ke orang lain.

---

## Bagian 6 — Kalau ada masalah

| Gejala | Apa yang dilakukan |
|---|---|
| Status **Deploy failed** | Klik tab **Logs**, salin baris error merah (tanpa password/string DB), lalu kirim ke saya |
| Web lambat / 503 pertama kali | Paket **free** Render sedang sleep. Tunggu ±1 menit. Supaya selalu hidup, ubah `plan: free` jadi `plan: 0.5c-512mb` di `render.yaml` |
| Error database | Cek `DATABASE_URL` di Render masih sama dengan string Neon, dan project Neon tidak di-pause |
| Repo tidak muncul di Render | Klik **Configure account**, centang repo `space-fighter`, lalu Save |

---

## Setelah selesai

Kirim URL `onrender.com`-mu ke saya. Nanti saya:
- ganti link demo di `README.md`,
- cek `/health`,
- commit dan push.

Dengan begitu semua orang cukup membuka **satu link tetap**.
