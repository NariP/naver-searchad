# DECISIONS

네이버 검색광고 스킬 설계 결정 로그(ADR). 최신이 위로.

## ADR-012 — Windows는 자격증명 관리자 + `nsa.ps1` 래퍼 (맥 키체인과 대칭)

**Date**: 2026-06-19
**Status**: Accepted (Windows 실측 검증 전)

### Context
Windows 키 보관을 정해야 함. `.env` 평문은 보안 약화, 자격증명관리자 GUI는 비개발자에 투박. 맥 키체인과 대칭 구조를 원함.

### Options
| 옵션 | 설명 |
|---|---|
| A. `.env` 평문 | 간단하나 비암호화 |
| B. 자격증명관리자 + CredentialManager 모듈 | 암호화, but `Install-Module` 의존 |
| C. 자격증명관리자 + .NET PasswordVault | 암호화, OS 내장(모듈 0) |
| D. 브라우저 폼(OAuth식) → .env | OS무관 UX, but 평문·서버기동 |

### Decision
C. `scripts/nsa.ps1`(PowerShell) 래퍼가 .NET `Windows.Security.Credentials.PasswordVault`로 저장/조회. 맥 `nsa`(bash)와 대칭: init=대화형 저장(입력 가림), doctor/setup/조회=nsa.py 위임, python 가드 포함. doctor는 `_secure_store_status`로 OS별(mac=Keychain, win=자격증명관리자) 점검.

### Rationale
의존성 0 원칙 유지(PasswordVault는 Windows 내장). 평문(.env) 회피, 모듈 설치(B) 회피. 맥과 대칭이라 사용법 일관. `nsa.py`는 환경변수만 읽으므로 무수정. **단 맥 개발환경에선 pwsh가 없어 Windows 실측 미완 — 검증된 PasswordVault 패턴으로 작성했으나 Windows 실행 확인 필요(문서에 명시).**

## ADR-011 — 자동 채움은 별도 `setup` 명령, 범위는 키만

**Date**: 2026-06-19
**Status**: Accepted

### Context
doctor가 진단만 하니 사용자가 부족분을 손으로 채워야 한다. 자동 채움을 원하되, 시스템을 건드리는 작업이라 안전장치가 필요. "무엇까지 자동화하나"도 정해야 함(파이썬·gws·키).

### Options
| 옵션 | 설명 |
|---|---|
| A. doctor --fix | 진단·수정 한 명령 |
| B. 별도 setup 명령 | 진단(doctor)과 수정(setup) 분리 |

### Decision
B. `nsa.py setup` 신설. 범위: **키만**. 파이썬=안내만(닭-달걀: 파이썬 없으면 nsa.py 자체가 안 돎 → 래퍼/문서가 안내), gws=대상 아님(우리 스킬 소관 아닌 외부 도구), egress=못 고침(정책). macOS는 없는 키만 입력받아 Keychain 저장, 그 외 OS는 환경변수 안내.

### Rationale
진단/수정 분리로 doctor는 부작용 없는 안전한 점검 유지(CI·자동화 친화). 자동 채움 범위를 키로 좁혀 시스템을 함부로 안 건드림. 파이썬 가드는 파이썬 밖(bash 래퍼)에서만 가능하므로 거기 두고 자동설치 대신 OS별 설치 명령 안내. gws/시트는 이 조회 스킬의 책임 경계 밖.

## ADR-010 — 환경 진단은 `nsa.py doctor`(크로스플랫폼)에 둠

**Date**: 2026-06-18
**Status**: Accepted

### Context
init/doctor가 bash 래퍼(`scripts/nsa`)에만 있어 Windows(=bash 없음)에선 진단조차 못 한다. OS·실행환경 점검을 OS 무관하게 하고 싶다.

### Options
| 옵션 | 설명 |
|---|---|
| A. bash + ps1 양쪽에 진단 로직 | 중복, 동기화 부담 |
| B. nsa.py에 doctor 내장 | 파이썬은 전 OS 동작, 단일 소스 |

### Decision
B. `python3 nsa.py doctor` 추가 — OS 감지, 파이썬 버전, 키 공급 상태(env + macOS는 Keychain 점검), 네이버 egress 도달, OS별 다음 단계 안내. 역할 구분: 파이썬 `doctor`=환경 전반(크로스플랫폼), bash 래퍼 `doctor`=macOS Keychain 등록 점검(맥 전용 편의).

### Rationale
파이썬은 mac/win/linux 모두 실행되므로 진단의 단일 진입점으로 적합. Windows 사용자도 `python nsa.py doctor`로 자기 환경(키 미설정·egress 등)을 바로 확인하고 환경변수 안내를 받는다. 키체인 점검은 macOS에서만 subprocess로 수행하고 타 OS에선 생략.

## ADR-009 — 셋업 마법사: `scripts/nsa init` / `doctor`

**Date**: 2026-06-18
**Status**: Accepted

### Context
키체인 저장을 매번 `security add-generic-password ...` 손으로 치게 하면 항목 이름·계정명 오타가 잦다.

### Decision
래퍼에 `init`(대화형 저장)·`doctor`(등록 점검) 서브명령 추가. `init`은 계정명(기본 `$USER`) + 키 3개를 `read -s`로 입력받아 `add-generic-password -U`로 저장. `doctor`는 존재 여부만 OK/없음 표시(값 비노출).

### Rationale
오타·노출 위험 제거. `read -s`로 키가 화면/히스토리에 안 남음. `-U`로 재실행 시 갱신. 클로드는 값 입력을 대신하지 않고 사용자가 직접 실행. 비-macOS는 환경변수 경로로 우회(`security` 없으면 load 생략).

## ADR-008 — 스킬 2개로 분리, 트리거 옵션 차등

**Date**: 2026-06-18
**Status**: Accepted

### Context
조회와 키 셋업은 트리거 성격이 다르다. 조회는 대화 중 자동으로 띄우면 좋지만, 키 저장은 사용자가 의도적으로 할 일이라 자동 트리거가 부적합.

### Options
| 옵션 | 설명 |
|---|---|
| A. 단일 스킬 | 조회+셋업 한 SKILL.md |
| B. 스킬 2개 | naver-searchad(자동) + naver-searchad-setup(수동) |

### Decision
B. `skills/naver-searchad`(자동 트리거) + `skills/naver-searchad-setup`(`disable-model-invocation: true` = 수동 전용). 스크립트는 공유.

### Rationale
키 셋업이 대화 중 자동 발동하면 의도치 않게 시크릿 입력을 유도할 수 있다. 수동 전용으로 막아 사용자가 `/naver-searchad-setup`을 명시 호출할 때만 동작. `.claude/commands/`(슬래시 커맨드 디렉토리)는 쓰지 않고 스킬 frontmatter 옵션으로 트리거를 제어 — 스킬 표준에 부합.

## ADR-007 — 키 보관: macOS Keychain + 셸 래퍼

**Date**: 2026-06-18
**Status**: Accepted

### Context
API 키 3개를 어디에 둘지. 평문 노출을 피하면서 클로드 코드/코덱스 양쪽에서 써야 함.

### Options
| 옵션 | 설명 |
|---|---|
| A. `.env`/`.zshrc` export | 평문. 백업·공유 시 유출 위험 |
| B. macOS Keychain + 래퍼 | 암호화 저장. `security`로 꺼내 env 주입 |
| C. 1Password CLI(`op`) | 강력하나 외부 도구 의존 |

### Decision
B. Keychain에 저장, `scripts/nsa` 래퍼가 `security find-generic-password`로 꺼내 환경변수로 주입 후 `nsa.py` 실행.

### Rationale
맥 기본 도구만으로 평문 노출 0. `nsa.py`는 환경변수만 읽으므로(변경 없음) 관심사 분리 유지. 래퍼는 이미 설정된 환경변수가 있으면 Keychain을 건너뛰어 코덱스/CI(키 없는 Keychain 환경)와도 호환. 키 저장 명령은 시크릿이 들어가므로 사용자가 직접 실행(대화/로그 노출 방지).

**계정 이름**(키체인 Account)은 하드코딩하지 않는다. 오픈소스 배포 대상이므로 `NSA_KEYCHAIN_ACCOUNT` env가 있으면 그 값, 없으면 `$USER`로 폴백. 받는 사람은 제로 설정으로 자기 `$USER` 동작, 회사/공용 구분 시 env 1개만 지정.

## ADR-006 — 키 없는 검증 수단: `_selftest` + `NSA_MOCK`

**Date**: 2026-06-18
**Status**: Accepted

### Context
Day 1 DoD는 키 없이 검증 가능해야 한다(ADR-005). 라이브 호출 없이 서명·폴백·라벨 로직을 어떻게 검증할지.

### Options
| 옵션 | 설명 |
|---|---|
| A. 외부 테스트 프레임워크(pytest) | 별도 의존성·파일 |
| B. 스크립트 내장 `_selftest` + `NSA_MOCK` env | 의존성 0, 단일 파일 |

### Decision
B. `_selftest` 서브커맨드(서명/CTR·CPC 폴백/humanize/timestamp assert) + `NSA_MOCK=1`이면 HTTP를 가짜 응답으로 대체.

### Rationale
의존성 0 원칙(ADR-002) 유지. 단일 파일 안에서 키·네트워크 없이 핵심 로직 전부 검증. mock은 `ctr`를 일부러 빼 폴백 경로까지 탐. URLError는 egress 차단 힌트(environment-policy.md)로 연결.

## ADR-005 — 라이브 호출 검증은 Day 2로 분리

**Date**: 2026-06-18
**Status**: Accepted

### Context
실제 네이버 응답을 받는 검증에는 발급된 API 키가 필요한데, 키 발급은 사용자만 가능하다.

### Decision
Day 1 DoD는 키 없이 가능한 범위(코드·서명 단위검증·mock)로 한정. 라이브 검증은 Day 2.

### Rationale
키 없이도 구현·구조·문서·로직을 완성·검증할 수 있다. 키 의존 단계만 분리하면 `/goal`이 사용자 대기로 멈추지 않고 끝까지 진행된다.

## ADR-004 — 코워크(클라우드 샌드박스) 미지원, 로컬 전용

**Date**: 2026-06-18
**Status**: Accepted

### Context
타깃 환경 후보: 클로드 코드, 코덱스, 코워크. 코워크 샌드박스에서 `api.searchad.naver.com` 호출 시 egress 차단(000/403 tunnel) 실측.

### Options
| 옵션 | 설명 |
|---|---|
| A. 로컬 전용 | 클로드 코드/코덱스만 지원 |
| B. 코워크용 프록시 우회 | 본인 도메인 + allowlist 등록 |

### Decision
A. 로컬 전용.

### Rationale
코워크 egress allowlist는 Anthropic 인프라 정책이라 개인 계정에서 관리 불가. 프록시도 allowlist 검사를 받아 우회 불가. 사용자가 클로드 코드/코덱스만 쓰기로 확정. 코워크는 필요 시 "로컬 수집 결과 파일 분석"으로 대응.

## ADR-003 — 읽기 전용(조회만), 쓰기 미구현

**Date**: 2026-06-18
**Status**: Accepted

### Context
검색광고 API는 입찰가 변경·키워드 삭제 등 쓰기도 제공한다.

### Decision
조회(GET/조회용 POST)만 구현. PUT/DELETE/생성 미구현.

### Rationale
쓰기는 광고비가 직접 나가는 작업이라 실수 비용이 크다. 조회와 안전 경계를 분리. 필요 시 별도 스킬/승인 흐름으로.

## ADR-002 — 의존성 0, 표준 라이브러리 urllib 사용

**Date**: 2026-06-18
**Status**: Accepted

### Options
| 옵션 | 설명 |
|---|---|
| A. requests | 공식 샘플과 동일, 가독성↑, but pip 필요 |
| B. urllib | 표준 라이브러리, 설치 0 |

### Decision
B. urllib.

### Rationale
`pip install` 없이 어느 로컬 환경(클로드 코드/코덱스)에서도 즉시 동작. 호출 패턴이 단순(GET/POST + 헤더)이라 urllib로 충분.

## ADR-001 — 형태: 스킬 + 단일 파이썬 스크립트

**Date**: 2026-06-18
**Status**: Accepted

### Options
| 옵션 | 설명 |
|---|---|
| A. 스킬 + 스크립트 | SKILL.md + nsa.py 폴더 1개 |
| B. MCP 서버 | figma-use식 모노레포 |
| C. .mcpb 번들 | 클릭설치용 패키지 |

### Decision
A. 스킬 + 단일 스크립트.

### Rationale
클로드 코드·코덱스 둘 다 "마크다운 스킬 + 로컬 스크립트"를 공통 지원. 빌드·서버·패키징 불필요. 자연어↔명령 매칭은 SKILL.md/endpoints.md 문서가 담당하므로 MCP 도구 스키마 등록이 불필요. 데스크탑 MCP/.mcpb가 필요해지면 코어 로직(nsa.py)을 재사용해 추후 확장.
