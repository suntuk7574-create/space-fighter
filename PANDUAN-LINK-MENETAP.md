# Panduan Link Tetap (Tanpa Kartu Kredit)

Kita pakai **ngrok free dev domain**. Gratis, tidak minta kartu, dan **URL-nya tidak berubah** walaupun tunnel dimatikan/dinyalakan ulang.

Konsekuensinya: karena backend + PostgreSQL jalan di laptop kamu, **laptop harus tetap menyala** saat game dipakai. Kalau laptop mati, link ikut mati (tapi alamatnya tetap sama saat dinyalakan lagi).

---

## Bagian 1 — Buat akun ngrok gratis

1. Buka **https://dashboard.ngrok.com/signup**
2. Daftar pakai email (atau GitHub/Google). **Tidak perlu kartu kredit.**
3. Setelah masuk, buka **https://dashboard.ngrok.com/domains**
4. Di situ ada **dev domain** otomatis, bentuknya seperti:

   ```text
   abc123xyz.ngrok-free.dev
   ```

   Salin domain itu.

5. Buka **https://dashboard.ngrok.com/get-started/your-authtoken**
6. Salin **authtoken**-mu.

> Jangan kirim authtoken ke chat. Nanti kamu tempel langsung di terminal laptop sendiri.

---

## Bagian 2 — Jalankan script link tetap

Di PowerShell, dari folder proyek:

```powershell
cd "C:\Users\desktop\Documents\Default Project\space-fighter"
.\scripts\start-fixed-link.ps1
```

Saat diminta:

1. Tempel **authtoken** → tekan Enter.
2. Tempel **dev domain** (tanpa `https://`) → tekan Enter.

Script akan:
- menyalakan PostgreSQL kalau belum jalan,
- menyalakan backend FastAPI,
- membuka ngrok dengan domain tetap kamu.

Authtoken dan domain **disimpan lokal** di komputer kamu, tidak masuk ke Git.

---

## Bagian 3 — Link yang dibagikan

Setelah script jalan, akan tampil seperti:

```text
LINK TETAP KAMU: https://abc123xyz.ngrok-free.dev
Cek kesehatan:   https://abc123xyz.ngrok-free.dev/health
```

Bagikan URL `https://abc123xyz.ngrok-free.dev` itu ke teman/dosen.

**Catatan paket gratis:** pengunjung pertama kali akan melihat halaman peringatan ngrok bertuliskan **Visit Site / Open Website**. Itu wajar — tinggal diklik sekali per browser. Setelah itu game langsung terbuka.

---

## Bagian 4 — Cek bahwa berhasil

| Alamat | Harapan |
|---|---|
| `https://<domain-mu>.ngrok-free.dev/health` | tampil `{"status":"ok","game":"Space Fighter"}` |
| `https://<domain-mu>.ngrok-free.dev/` | game Space Fighter muncul |
| `https://<domain-mu>.ngrok-free.dev/docs` | halaman dokumentasi API |

Lalu coba daftar akun di dua browser/HP berbeda, main sebentar, dan buka **Leaderboard**. Kedua skor harus muncul di papan peringkat yang sama.

---

## Bagian 5 — Pakai lagi besok

Cukup jalankan ulang:

```powershell
cd "C:\Users\desktop\Documents\Default Project\space-fighter"
.\scripts\start-fixed-link.ps1
```

Authtoken + domain sudah tersimpan, jadi tidak ditanya lagi. **URL-nya tetap sama.**

Kalau laptop restart, jalankan script ini lagi. Jangan pakai `start-demo.ps1` kalau mau URL yang tetap.

---

## Bagian 6 — Masuk sebagai admin (khusus kamu)

1. Buka `https://<domain-mu>.ngrok-free.dev/?admin=1`
2. Muncul tombol **🛡️ Masuk sebagai Admin**.
3. Masukkan username + password admin yang ada di file `backend/.env` kamu.
4. Jangan bagikan `?admin=1` ke orang lain.

---

## Bagian 7 — Kalau ada masalah

| Gejala | Apa yang dilakukan |
|---|---|
| Muncul halaman "Visit Site" | Klik saja. Wajar di paket gratis ngrok. |
| URL mati saat dibuka | Laptop mungkin mati/terminal tertutup. Jalankan `start-fixed-link.ps1` lagi. |
| Error "authentication failed" | Authtoken salah. Hapus file `%LOCALAPPDATA%\Temp\opencode\ngrok-domain.txt`, lalu jalankan script lagi dan tempel ulang token. |
| Error port 8000 dipakai | Script otomatis memakai backend yang sudah jalan. Kalau tetap error, tutup terminal lama lalu jalankan ulang. |
| Ingin laptop boleh mati | Itu butuh cloud berbayar / host cloud gratis dengan kuota kecil. Lihat `DEPLOY.md`. |

---

## Setelah selesai

Kirim URL `ngrok-free.dev`-mu ke saya. Nanti saya ganti link di `README.md`, cek `/health`, lalu commit + push.
