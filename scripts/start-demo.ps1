# Menyalakan demo lengkap: PostgreSQL portabel + backend FastAPI + tunnel Cloudflare.
# Cara pakai:
#   .\scripts\start-demo.ps1
# Lalu tunggu beberapa detik sampai muncul baris "Your quick Tunnel has been created!"
# URL https://....trycloudflare.com itulah yang dibagikan ke teman/dosen.
#
# Catatan: URL tunnel gratis berubah setiap kali dijalankan ulang dan akan mati
# kalau laptop dimatikan atau terminal ditutup. Untuk URL permanen pakai Render/DEPLOY.md.

param([int]$Port = 8000)

$root = Split-Path -Parent $PSScriptRoot
$tmp = Join-Path $env:LOCALAPPDATA 'Temp\opencode'
$pgBin = Join-Path $tmp 'pgsql19\pgsql\bin'
$pgData = Join-Path $tmp 'pgdata'
$cloudflared = Join-Path $tmp 'cloudflared.exe'
$backend = Join-Path $root 'backend'

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

# 3. Unduh cloudflared bila belum ada, lalu buka tunnel.
if (-not (Test-Path $cloudflared)) {
  Write-Host "Mengunduh cloudflared..."
  Invoke-WebRequest `
    -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' `
    -OutFile $cloudflared
}

Write-Host "Membuka tunnel publik. Tunggu sampai URL trycloudflare.com muncul..."
# http2 lebih stabil daripada quic pada jaringan Wi-Fi/download yang membatasi UDP.
& $cloudflared tunnel --protocol http2 --url "http://127.0.0.1:$Port"
