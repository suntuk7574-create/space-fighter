# Menyalakan demo dengan URL TETAP memakai ngrok free dev domain.
# Tidak butuh kartu kredit. URL tidak berubah walaupun tunnel dijalankan ulang.
#
# Cara pakai pertama kali:
#   1. Daftar/gratis login di https://dashboard.ngrok.com/signup
#   2. Buka https://dashboard.ngrok.com/domains -> salin dev domain
#      (bentuknya seperti abc123xyz.ngrok-free.dev)
#   3. Buka https://dashboard.ngrok.com/get-started/your-authtoken -> salin authtoken
#   4. Jalankan: .\scripts\start-fixed-link.ps1
#   5. Saat diminta, tempel authtoken dan dev domain. Keduanya disimpan lokal
#      di komputer ini, TIDAK masuk ke repo/git.
#
# Cara pakai berikutnya: cukup .\scripts\start-fixed-link.ps1
#
# Catatan: paket free ngrok menampilkan halaman peringatan "Visit Site" sekali
# per browser. Itu wajar, tinggal diklik. Laptop harus tetap menyala karena
# backend + database jalan di sini.

param([int]$Port = 8000)

$root = Split-Path -Parent $PSScriptRoot
$tmp = Join-Path $env:LOCALAPPDATA 'Temp\opencode'
$pgBin = Join-Path $tmp 'pgsql19\pgsql\bin'
$pgData = Join-Path $tmp 'pgdata'
$backend = Join-Path $root 'backend'
$ngrok = Join-Path $tmp 'ngrok\ngrok.exe'
$domainFile = Join-Path $tmp 'ngrok-domain.txt'

if (-not (Test-Path $ngrok)) {
  throw "ngrok belum ada di $ngrok. Jalankan ulang setelah mengunduh ngrok untuk Windows."
}

# 1. Pastikan PostgreSQL portabel berjalan.
if (-not (Test-Path (Join-Path $pgBin 'pg_ctl.exe'))) {
  throw "PostgreSQL portabel belum tersedia di $pgBin."
}
& (Join-Path $pgBin 'pg_isready.exe') -h 127.0.0.1 -p 5432 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Menyalakan PostgreSQL..."
  & (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -o "-p 5432 -h 127.0.0.1" -l "$pgData\server.log" -w start
}

# 2. Pastikan backend berjalan.
$listen = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $listen) {
  Write-Host "Menyalakan backend di http://127.0.0.1:$Port ..."
  $python = (Get-Command python).Source
  Start-Process -FilePath $python `
    -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port $Port" `
    -WorkingDirectory $backend -WindowStyle Hidden
}

# 3. Simpan authtoken + dev domain lokal sekali saja.
if (-not (Test-Path $domainFile)) {
  $secureToken = Read-Host "Tempel ngrok authtoken kamu" -AsSecureString
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
  $token = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  if ([string]::IsNullOrWhiteSpace($token)) { throw "Authtoken tidak boleh kosong." }
  & $ngrok config add-authtoken $token
  $token = $null

  $domain = Read-Host "Tempel dev domain (contoh abc123xyz.ngrok-free.dev)"
  $domain = $domain.Trim().TrimEnd('/')
  if ($domain -match '^https?://') { $domain = ($domain -replace '^https?://', '').TrimEnd('/') }
  if ([string]::IsNullOrWhiteSpace($domain)) { throw "Dev domain tidak boleh kosong." }
  Set-Content -Path $domainFile -Value $domain -Encoding UTF8
} else {
  $domain = (Get-Content $domainFile -Raw).Trim()
}

$url = "https://$domain"
Write-Host ""
Write-Host "LINK TETAP KAMU: $url"
Write-Host "Cek kesehatan:   $url/health"
Write-Host "Kalau muncul halaman 'Visit Site', klik saja (wajar di paket gratis)."
Write-Host "Jangan tutup jendela ini selama game dipakai."
Write-Host ""

# 4. Buka tunnel dengan domain tetap.
& $ngrok http $Port --url $url
