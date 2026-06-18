# nsa.ps1 — 네이버 검색광고 CLI 런처 (Windows / 자격증명 관리자 연동)
#
# 맥 scripts/nsa(bash)의 윈도우 짝꿍. 키를 Windows 자격증명 관리자에
# .NET PasswordVault(OS 내장, 모듈 설치 0)로 저장/조회한다.
# nsa.py는 환경변수만 읽으므로(코드 동일), 이 래퍼가 꺼내 환경변수로 주입한다.
#
# 셋업:  .\scripts\nsa.ps1 init       # 키 3개를 자격증명 관리자에 저장(입력 가림)
# 진단:  .\scripts\nsa.ps1 doctor     # OS·키·egress 진단 (nsa.py 위임)
# 사용:  .\scripts\nsa.ps1 campaigns
#        .\scripts\nsa.ps1 stats --ids cmp-1 --since 2026-06-01 --until 2026-06-17
#
# 저장소 리소스명(Resource) 접두어: 자격증명 관리자에 "naver-searchad:<KEY>"로 저장.

param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Keys = @('NAVER_AD_API_KEY','NAVER_AD_SECRET_KEY','NAVER_AD_CUSTOMER_ID')
$Vault = 'naver-searchad'   # 자격증명 리소스 접두어

# ── PasswordVault 로드 (Windows 내장 WinRT API) ──
function Get-Vault {
  Add-Type -AssemblyName 'Windows.Security.Credentials.PasswordVault, ContentType=WindowsRuntime' -ErrorAction SilentlyContinue | Out-Null
  return New-Object Windows.Security.Credentials.PasswordVault
}

function Save-Key([string]$name, [string]$value) {
  $v = Get-Vault
  # 기존 것 있으면 제거 후 추가(갱신)
  try { $old = $v.Retrieve($Vault, $name); if ($old) { $v.Remove($old) } } catch {}
  $cred = New-Object Windows.Security.Credentials.PasswordCredential($Vault, $name, $value)
  $v.Add($cred)
}

function Get-Key([string]$name) {
  try {
    $v = Get-Vault
    $cred = $v.Retrieve($Vault, $name)
    $cred.RetrievePassword()
    return $cred.Password
  } catch { return $null }
}

# ── 파이썬 가드 (파이썬 밖의 유일한 방어선) ──
function Find-Python {
  foreach ($c in @('python','python3','py')) {
    if (Get-Command $c -ErrorAction SilentlyContinue) { return $c }
  }
  return $null
}

# ── init: 대화형 저장 (입력 가림) ──
function Invoke-Init {
  Write-Host "네이버 검색광고 키 셋업 (Windows 자격증명 관리자)"
  Write-Host "  발급: 네이버 검색광고 > 도구 > API 사용 관리"
  $prompts = @{
    'NAVER_AD_API_KEY'    = 'API_KEY (액세스 라이선스)'
    'NAVER_AD_SECRET_KEY' = 'SECRET_KEY'
    'NAVER_AD_CUSTOMER_ID' = 'CUSTOMER_ID'
  }
  foreach ($k in $Keys) {
    do {
      $sec = Read-Host -Prompt "  $($prompts[$k])" -AsSecureString   # 입력 화면에 안 보임
      $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
    } while ([string]::IsNullOrWhiteSpace($plain))
    Save-Key $k $plain
  }
  Write-Host "`n저장 완료. 확인: .\scripts\nsa.ps1 doctor"
}

# ── 디스패치 ──
$cmd = if ($Args.Count -ge 1) { $Args[0] } else { '' }

if ($cmd -eq 'init') { Invoke-Init; exit 0 }

$py = Find-Python
if (-not $py) {
  Write-Error "Python 3 이 없습니다. nsa는 파이썬으로 동작합니다."
  Write-Host  "  설치: winget install Python.Python.3   (또는 https://www.python.org/downloads/)"
  Write-Host  "  설치 후 다시: .\scripts\nsa.ps1 doctor"
  exit 127
}

# 자격증명 관리자에서 키를 꺼내 환경변수로 주입(이미 있으면 유지)
foreach ($k in $Keys) {
  if (-not [Environment]::GetEnvironmentVariable($k)) {
    $val = Get-Key $k
    if ($val) { Set-Item -Path "Env:$k" -Value $val }
  }
}

# nsa.py로 위임 (doctor/setup/조회 전부)
& $py (Join-Path $ScriptDir 'nsa.py') @Args
exit $LASTEXITCODE
