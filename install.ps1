# naver-searchad 설치 스크립트 (Windows) — npm 불필요
#
# 한 줄 설치 (PowerShell):
#   irm https://raw.githubusercontent.com/NariP/naver-searchad/main/install.ps1 | iex
#
# 동작: 레포를 %USERPROFILE%\.naver-searchad 에 받아두고, 스킬을
#       스킬을 선택 위치의 .claude\skills 에 링크/복사한다.
$ErrorActionPreference = 'Stop'

$RepoUrl = 'https://github.com/NariP/naver-searchad.git'
$Src     = if ($env:NSA_HOME) { $env:NSA_HOME } else { Join-Path $HOME '.naver-searchad' }
$Skills  = @('naver-searchad')   # 단일 스킬

# ── 0) git 확인 ──
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "git 이 필요합니다. (또는 ZIP: $($RepoUrl -replace '\.git$','')/archive/refs/heads/main.zip)"
  exit 1
}

# ── 1) 소스 받기/갱신 ──
if (Test-Path (Join-Path $Src '.git')) {
  Write-Host "[install] 기존 소스 갱신: $Src"
  git -C $Src pull --quiet --ff-only 2>$null
} else {
  Write-Host "[install] 소스 받기: $Src"
  git clone --quiet --depth 1 $RepoUrl $Src
}

# ── 2) 스코프 선택 ──
$scope = $env:NSA_SCOPE
if (-not $scope) {
  Write-Host ""
  Write-Host "설치 위치를 고르세요:"
  Write-Host "  1) 전역    (~\.claude\skills) — 모든 프로젝트"
  Write-Host "  2) 프로젝트 (.\.claude\skills) — 현재 폴더"
  $ans = Read-Host "선택 [1/2] (기본 1)"
  $scope = if ($ans -eq '2') { 'project' } else { 'global' }
}

if ($scope -eq 'project') {
  # 가드: 소스 레포 자신 안에 설치하면 self-link(깨진 링크)가 생긴다 → 막음
  if ((Resolve-Path (Get-Location)).Path -eq (Resolve-Path $Src).Path) {
    Write-Error "현재 폴더가 소스 레포($Src)입니다. 여기엔 프로젝트 설치하지 않습니다. 다른 폴더 또는 전역 설치를 쓰세요."
    exit 1
  }
  $dest = Join-Path (Get-Location) '.claude\skills'
} else {
  $dest = Join-Path $HOME '.claude\skills'
}
New-Item -ItemType Directory -Force -Path $dest | Out-Null

# ── 3) 링크(심볼릭, 실패 시 복사 폴백) ──
Write-Host "[install] 스킬 설치 → $dest"
foreach ($s in $Skills) {
  $link   = Join-Path $dest $s
  $target = Join-Path $Src "skills\$s"
  if (Test-Path $link) { Remove-Item -Recurse -Force $link }
  try {
    New-Item -ItemType SymbolicLink -Path $link -Target $target -ErrorAction Stop | Out-Null
    Write-Host "  linked: $s"
  } catch {
    # 심볼릭링크는 권한(개발자 모드/관리자) 필요 → 안 되면 복사
    Copy-Item -Recurse -Force $target $link
    Write-Host "  copied: $s (심볼릭링크 권한 없어 복사)"
  }
}

# ── 4) 파이썬 확인 + 안내 ──
Write-Host ""
if ((Get-Command python -ErrorAction SilentlyContinue) -or (Get-Command python3 -ErrorAction SilentlyContinue)) {
  Write-Host "설치 완료. 다음:"
  Write-Host "  python $Src\skills\naver-searchad\scripts\nsa.py doctor      # 환경 진단"
  Write-Host "  $Src\skills\naver-searchad\scripts\nsa.ps1 init             # 키 저장(자격증명 관리자)"
} else {
  Write-Warning "Python 3 이 없습니다. 설치 후 다시 진단:"
  Write-Host "  winget install Python.Python.3"
}
