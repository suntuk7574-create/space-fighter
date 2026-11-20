# Menambahkan remote GitHub dan push commit awal.
# Cara pakai:
#   .\scripts\setup-remote.ps1
# Lalu tempel URL: https://github.com/USERNAME/space-fighter.git
#
# Jika GitHub meminta password, gunakan Personal Access Token (PAT),
# bukan password akun. PAT dibuat di GitHub > Settings > Developer settings.

param([string]$RepoUrl)

if (-not $RepoUrl) {
  $RepoUrl = Read-Host "Masukkan URL repo GitHub (https://github.com/USERNAME/space-fighter.git)"
}

$RepoUrl = $RepoUrl.Trim()
if ($RepoUrl -notlike 'https://github.com/*') {
  throw "URL tidak valid. Harus diawali https://github.com/"
}

git remote remove origin 2>$null
git remote add origin $RepoUrl
git branch -M main
git push -u origin main

Write-Host "Selesai. Cek dengan: git status"
