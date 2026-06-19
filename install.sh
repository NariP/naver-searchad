#!/usr/bin/env bash
# naver-searchad 설치 스크립트 (macOS / Linux) — npm 불필요
#
# 한 줄 설치:
#   curl -fsSL https://raw.githubusercontent.com/NariP/naver-searchad/main/install.sh | bash
#
# 동작: 레포를 ~/.naver-searchad 에 받아두고(소스 1벌), 두 스킬을
#       선택한 위치(전역/프로젝트)의 .claude/skills 에 심볼릭링크한다.
#       scripts/는 레포 안에 그대로 있으므로 경로가 깨지지 않는다.
set -euo pipefail

REPO_URL="https://github.com/NariP/naver-searchad.git"
SRC="${NSA_HOME:-$HOME/.naver-searchad}"   # 소스 통째 보관 위치
SKILLS=(naver-searchad naver-searchad-setup)

say() { printf '%s\n' "$*"; }
err() { printf '%s\n' "$*" >&2; }

# ── 0) git 확인 (없으면 tarball 폴백 안내) ──
if ! command -v git >/dev/null 2>&1; then
  err "[install] git 이 필요합니다. (또는 ZIP 다운로드: ${REPO_URL%.git}/archive/refs/heads/main.zip)"
  exit 1
fi

# ── 1) 소스 받기/갱신 ──
if [ -d "$SRC/.git" ]; then
  say "[install] 기존 소스 갱신: $SRC"
  git -C "$SRC" pull --quiet --ff-only || err "[install] 갱신 실패(로컬 변경?). 계속 진행."
else
  say "[install] 소스 받기: $SRC"
  git clone --quiet --depth 1 "$REPO_URL" "$SRC"
fi

# ── 2) 스코프 선택 (전역 / 프로젝트) ──
SCOPE="${NSA_SCOPE:-}"
if [ -z "$SCOPE" ]; then
  if [ -t 0 ]; then
    say ""
    say "설치 위치를 고르세요:"
    say "  1) 전역    (~/.claude/skills) — 모든 프로젝트에서 사용"
    say "  2) 프로젝트 (./.claude/skills) — 현재 폴더에서만"
    printf "선택 [1/2] (기본 1): "
    read -r ans </dev/tty || ans=1
    case "$ans" in 2) SCOPE=project ;; *) SCOPE=global ;; esac
  else
    SCOPE=global   # 비대화(파이프)면 전역 기본
  fi
fi

if [ "$SCOPE" = "project" ]; then
  DEST="$(pwd)/.claude/skills"
else
  DEST="$HOME/.claude/skills"
fi
mkdir -p "$DEST"

# ── 3) 심볼릭링크 ──
say "[install] 스킬 링크 → $DEST"
for s in "${SKILLS[@]}"; do
  link="$DEST/$s"
  target="$SRC/skills/$s"
  if [ -e "$link" ] || [ -L "$link" ]; then rm -rf "$link"; fi
  ln -s "$target" "$link"
  say "  linked: $s"
done

# ── 4) 파이썬 확인 + 안내 ──
say ""
if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
  say "설치 완료. 다음:"
  say "  python3 $SRC/scripts/nsa.py doctor    # 환경 진단"
  say "  ($SRC/scripts/nsa init 로 키 저장)"
else
  err "⚠️ Python 3 이 없습니다. 설치 후 다시 진단하세요:"
  case "$(uname -s)" in
    Darwin) err "  brew install python3" ;;
    Linux)  err "  sudo apt install python3" ;;
  esac
fi
