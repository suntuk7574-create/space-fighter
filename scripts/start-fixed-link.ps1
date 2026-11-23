# Menyalakan demo dengan URL TETAP tanpa akun/kartu kredit (localtunnel).
# URL: https://suntuk-space-fighter.loca.lt
#
# Cara pakai:
#   .\scripts\start-fixed-link.ps1
#
# Tidak perlu daftar, tidak perlu token. Kalau laptop restart, jalankan lagi
# script ini dan URL tetap sama.
#
# Catatan: pengunjung mungkin melihat halaman "Tunnel website ahead" sekali
# per IP (7 hari). Ketik IP yang tertera di halaman itu, lalu klik Continue.
# Itu mekanisme keamanan localtunnel gratis, bukan error game.

param(
  [int]$Port = 8000,
  [string]$Subdomain = 'suntuk-space-fighter'
)

$root = Split-Path -Parent $PSScriptRoot
$tmp = Join-Path $env:LOCALAPPDATA 'Temp\opencode'
$pgBin = Join-Path $tmp 'pgsql19\pgsql\bin'
$pgData = Join-Path $tmp 'pgdata'
$backend = Join-Path $root 'backend'
$nodeDir = Join-Path $tmp 'node22\node-v22.14.0-win-x64'
$ltPrefix = Join-Path $tmp 'localtunnel'
$lt = Join-Path $ltPrefix 'node_modules\localtunnel\bin\lt.js'

if (-not (Test-Path (Join-Path $nodeDir 'node.exe'))) {
  throw "Node portable belum ada di $nodeDir."
}

# 1. Pastikan localtunnel terpasang di folder sementara (bukan di repo).
if (-not (Test-Path $lt)) {
  Write-Host "Mengunduh localtunnel..."
  $env:PATH = $nodeDir + ';' + $env:PATH
  & (Join-Path $nodeDir 'npm.cmd') install localtunnel --prefix $ltPrefix --no-audit --no-fund
}

# 2. Pastikan PostgreSQL portabel berjalan.
if (-not (Test-Path (Join-Path $pgBin 'pg_ctl.exe'))) {
  throw "PostgreSQL portabel belum tersedia di $pgBin."
}
& (Join-Path $pgBin 'pg_isready.exe') -h 127.0.0.1 -p 5432 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Menyalakan PostgreSQL..."
  & (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -o "-p 5432 -h 127.0.0.1" -l "$pgData\server.log" -w start
}

# 3. Pastikan backend berjalan.
$listen = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $listen) {
  Write-Host "Menyalakan backend di http://127.0.0.1:$Port ..."
  $python = (Get-Command python).Source
  Start-Process -FilePath $python `
    -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port $Port" `
    -WorkingDirectory $backend -WindowStyle Hidden
  Start-Sleep -Seconds 4
}

$url = "https://$Subdomain.loca.lt"
Write-Host ""
Write-Host "LINK TETAP KAMU: $url"
Write-Host "Cek kesehatan:   $url/health"
Write-Host "Kalau muncul halaman 'Tunnel website ahead', ketik IP yang tertera lalu Continue."
Write-Host "Jangan tutup jendela ini selama game dipakai."
Write-Host ""

# 4. Buka tunnel dengan subdomain tetap.
$env:PATH = $nodeDir + ';' + $env:PATH
& (Join-Path $nodeDir 'node.exe') $lt --port $Port --subdomain $Subdomain
