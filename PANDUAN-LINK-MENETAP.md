# Panduan Link Tetap (Tanpa Akun, Tanpa Kartu)

Link yang dipakai sekarang:

```text
https://suntuk-space-fighter-2.loca.lt
```

Alamat ini **tetap**, tidak berubah walaupun tunnel dimatikan atau laptop di-restart. Tidak perlu daftar akun, tidak perlu kartu kredit, tidak perlu token.

Konsekuensinya: backend + PostgreSQL jalan di laptop, jadi **laptop harus menyala** saat game dipakai.

---

## Bagian 1 — Cara menyalakan

Buka PowerShell di folder proyek:

```powershell
cd "C:\Users\desktop\Documents\Default Project\space-fighter"
.\scripts\start-fixed-link.ps1
```

Script otomatis:
1. menyiapkan localtunnel (kalau belum ada),
2. menyalakan PostgreSQL kalau mati,
3. menyalakan backend FastAPI kalau mati,
4. membuka tunnel dengan subdomain tetap `suntuk-space-fighter-2`.

Kalau berhasil akan muncul:

```text
LINK TETAP KAMU: https://suntuk-space-fighter-2.loca.lt
your url is: https://suntuk-space-fighter-2.loca.lt
```

**Jangan tutup jendela PowerShell** selama game dipakai.

---

## Bagian 2 — Halaman "Tunnel website ahead" (wajar)

Karena localtunnel gratis, pengunjung bisa melihat halaman keamanan seperti ini:

> **You are about to visit: https://suntuk-space-fighter-2.loca.lt**
> To continue, enter the IP shown above.

Cara mengatasinya:

1. Lihat angka IP yang tertera di halaman itu (contoh `210.87.90.62`).
2. Ketik di kolom **IP Address**.
3. Klik **Continue**.

Itu hanya **sekali per IP selama 7 hari**. Bukan error game, bukan virus, dan tidak ada biaya.

---

## Bagian 3 — Cek bahwa berhasil

| Alamat | Harapan |
|---|---|
| `https://suntuk-space-fighter-2.loca.lt/health` | tampil `{"status":"ok","game":"Space Fighter"}` |
| `https://suntuk-space-fighter-2.loca.lt/` | game Space Fighter muncul |
| `https://suntuk-space-fighter-2.loca.lt/docs` | halaman dokumentasi API |

Lalu coba daftar akun di dua browser/HP berbeda, main sebentar, dan buka **Leaderboard**. Kedua skor harus muncul di papan peringkat yang sama.

---

## Bagian 4 — Pasang di HP (PWA, tanpa APK)

Game sudah dilengkapi **PWA**, jadi tidak perlu APK dan tidak perlu Android Studio.

**Android / Chrome:**
1. Buka `https://suntuk-space-fighter-2.loca.lt` di Chrome.
2. Kalau muncul halaman "Tunnel website ahead", ketik IP yang tertera → **Continue**.
3. Ketuk menu **⋮** (kanan atas).
4. Pilih **Add to Home Screen** atau **Install app**.
5. Beri nama bebas → **Add / Install**.
6. Ikon **Space Fighter** muncul di layar utama. Buka seperti aplikasi biasa (fullscreen).

**iPhone / Safari:**
1. Buka link di Safari, ketuk tombol **Share** (kotak dengan panah atas).
2. Pilih **Add to Home Screen** → **Add**.

Yang di-cache service worker hanya tampilan game (HTML, Three.js, ikon). **API, skor, dan leaderboard tidak di-cache**, jadi selalu data terbaru.

Catatan: tetap butuh internet dan laptop harus menyala, karena backend + database ada di sini. Kalau game diubah, naikkan nomor versi di `frontend/sw.js` baris `const CACHE = 'space-fighter-shell-v1'` menjadi `v2`, supaya HP mengunduh tampilan terbaru.

---

## Bagian 5 — Pakai lagi setelah laptop restart

Cukup jalankan ulang:

```powershell
cd "C:\Users\desktop\Documents\Default Project\space-fighter"
.\scripts\start-fixed-link.ps1
```

**URL-nya tetap sama.** Tidak ada token yang perlu dimasukkan.

Kalau subdomain suatu hari terpakai orang lain, ganti lewat parameter:

```powershell
.\scripts\start-fixed-link.ps1 -Subdomain suntuk-space-fighter-3
```

---

## Bagian 6 — Masuk sebagai admin (khusus kamu)

1. Buka `https://suntuk-space-fighter-2.loca.lt/?admin=1`
2. Muncul tombol **🛡️ Masuk sebagai Admin**.
3. Masukkan username + password admin yang ada di `backend/.env` kamu.
4. Jangan bagikan `?admin=1` ke orang lain.

---

## Bagian 7 — Kalau ada masalah

| Gejala | Apa yang dilakukan |
|---|---|
| Halaman "Tunnel website ahead" | Ketik IP yang tertera → Continue. Wajar, sekali per 7 hari. |
| URL mati | Laptop mati/terminal tertutup. Jalankan `start-fixed-link.ps1` lagi. |
| Subdomain terpakai | Pakai `-Subdomain suntuk-space-fighter-3`. |
| Port 8000 dipakai | Script otomatis memakai backend yang sudah jalan. |
| PWA tidak muncul tombol Install | Pastikan halaman IP sudah dilewati dan Chrome/Safari versi terbaru. Menu ⋮ → **Add to Home Screen** tetap bisa dipakai. |
| Tampilan game lama setelah update | Naikkan versi `CACHE` di `frontend/sw.js` (`v1` → `v2`), lalu muat ulang. |
| Ingin laptop boleh mati | Itu butuh cloud berbayar / host gratis dengan kuota kecil. Lihat `DEPLOY.md`. |

---

## Alternatif (opsional)

Kalau nanti kamu punya akun ngrok dan ingin halaman peringatan yang lebih sederhana, ada `scripts/start-fixed-link-ngrok.ps1`. Itu butuh authtoken + dev domain, tapi tetap gratis dan tanpa kartu.

Untuk link cloud 24/7 (laptop boleh mati), lihat `DEPLOY.md` + `render.yaml` (Render minta kartu untuk verifikasi, biaya tetap $0 di plan free).
