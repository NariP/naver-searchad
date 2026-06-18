# DECISIONS

네이버 검색광고 스킬 설계 결정 로그(ADR). 최신이 위로.

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
