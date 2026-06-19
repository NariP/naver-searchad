---
name: naver-searchad-setup
displayName: 네이버 검색광고 키 셋업
version: 1.0.0
description: 네이버 검색광고 API 키 3개(API_KEY/SECRET_KEY/CUSTOMER_ID)를 OS 보안저장소(macOS 키체인 / Windows 자격증명관리자)에 안전하게 저장·점검하는 셋업 마법사. 수동 호출 전용 — 키 셋업/재설정/등록 확인이 필요할 때 /naver-searchad-setup 으로 실행한다.
disable-model-invocation: true
license: MIT
argument-hint: "init | doctor (생략 시 init)"
metadata:
  category: marketing
  locale: ko-KR
  phase: v1
---

# Naver SearchAd 셋업 (키 등록/점검)

네이버 검색광고 키를 **macOS Keychain**에 저장하고 점검한다. **수동 호출 전용**(`disable-model-invocation: true`) — 자동 트리거되지 않는다. 키 저장은 사용자가 의도적으로 할 일이기 때문.

루트(`scripts/`)는 이 스킬 디렉토리 기준 `../../` 에 있다.

## When to use

- "네이버 검색광고 키 셋업/등록해줘"
- "키 다시 넣을래 / 계정 바꿀래"
- "키가 제대로 등록됐는지 확인"

## 사용법

### 0. 진단 후 자동 채움 (권장, 크로스플랫폼)

```bash
python3 scripts/nsa.py doctor    # 무엇이 부족한지 진단
python3 scripts/nsa.py setup     # 부족한 키를 동의받고 채움 (macOS Keychain)
```
- `setup`은 **없는 키만** 입력받아 저장. 이미 있으면 건드리지 않음.
- macOS 외(Windows/Linux)에선 환경변수 지정 방법을 안내(자동 저장은 macOS만).
- 대상은 **키뿐**. 파이썬·gws 같은 외부 도구는 채우지 않는다(안내만).

### 1. 키 저장 (init, 대화형 — OS별 보안저장소)

```bash
scripts/nsa init           # macOS: Keychain
.\scripts\nsa.ps1 init     # Windows: 자격증명 관리자 (실측 검증 전)
```
- 대화형: 계정 이름(기본 `$USER`, 회사용이면 `mycompany` 등) → 키 3개 입력
- 키 입력은 화면에 안 찍힌다(`read -s`)
- 기본과 다른 계정명을 썼으면 셸에 `export NSA_KEYCHAIN_ACCOUNT=<이름>` 추가 안내

> ⚠️ 클로드가 키 값을 대신 입력하지 않는다. 사용자가 직접 `scripts/nsa init`을 실행한다(시크릿이 대화·로그에 남지 않게).

기본($USER)과 다른 계정명(예: `mycompany`)을 썼다면, 매번 붙이지 않도록 셸 프로필에 한 줄:
```bash
echo 'export NSA_KEYCHAIN_ACCOUNT=mycompany' >> ~/.zshrc && source ~/.zshrc
```

### 2. 등록 점검 (doctor)

```bash
scripts/nsa doctor
```
- 키 3개가 등록됐는지 OK/없음 표시 (**값은 보여주지 않음**)
- 누락 시 종료코드 1
- 다른 계정명을 썼으면 `NSA_KEYCHAIN_ACCOUNT=<이름> scripts/nsa doctor`

## 비-macOS (코덱스/CI)

Keychain이 없으면 환경변수로 직접 주입한다. 셋업 불필요:
```bash
export NAVER_AD_API_KEY=... NAVER_AD_SECRET_KEY=... NAVER_AD_CUSTOMER_ID=...
```

## 셋업 후

조회는 자동 트리거 스킬 `naver-searchad`로. 검증: `scripts/nsa campaigns`.

상세 키 보관 정책 → `../../.claude/docs/auth-signature.md`.
