# GOAL: 네이버 검색광고 성과 조회 스킬 (naver-searchad)

## 한 줄 목표 + 컨셉

네이버 검색광고 API를 감싸 **노출·클릭·광고비·CTR**를 조회하는 **읽기 전용 로컬 스킬**을, 클로드 코드·코덱스에서 바로 쓸 수 있게 완성한다.

## `/goal` 실행 문구 (복붙용)

> `naver-searchad/GOAL.md`의 Day 1 체크리스트를 위에서부터 실행해 DoD를 모두 충족시켜라.
> 운영 규칙:
> - 사용자에게 질문하지 말 것. 가장 합리적인 추천안을 채택한다.
> - 결정은 `DECISIONS.md`에 새 ADR로 추가한다 (Context / Options / Decision / Rationale).
> - 매 체크리스트 항목 완료 시 `[x]`로 갱신한다.
> - **실제 API 키가 없으면**: 키가 필요한 라이브 호출 단계(아래 "사용자만 가능" 참조)에서 멈추고 사용자에게 알린다. 그 외 단계(코드 작성, mock 검증, 문서)는 끝까지 진행한다.
> - DoD가 모두 충족되면 종료한다. 추가 작업(쓰기 기능 등) 시작 금지.

### 사용자만 가능 (여기서 멈추고 알림)

- 네이버 검색광고 **API 키 발급** (`NAVER_AD_API_KEY` / `SECRET_KEY` / `CUSTOMER_ID`)
- 그 키로 하는 **실제 라이브 호출 검증** (계정 데이터 조회)

→ 키가 없으면 코드·구조·mock 검증까지 완료하고, 라이브 검증만 사용자에게 넘긴다.

## 단계 로드맵

| 단계 | 핵심 변화 |
|---|---|
| **Day 1** | `nsa.py` 구현 (전 명령) + SKILL.md + mock 검증까지. 키 없이 갈 수 있는 데까지. |
| Day 2 | 사용자 키 투입 → 라이브 호출 검증 → 실데이터로 한글 라벨/CTR 폴백 확인 |
| Day 3+ | (선택) CSV 출력 옵션, report 폴링 견고화, 페이지네이션 |

## 오늘 (Day 1) 플랜

### 한 줄 목표

키 없이 검증 가능한 데까지 — `nsa.py` 전 명령 구현 + 서명 단위 검증 + `--help`/인자 검증 + 문서 정합성.

### 아키텍처

```
SKILL.md ──(자연어 매칭)──► nsa.py <command>
                              │  sign(ts.method.uri) + urllib
                              ▼
              https://api.searchad.naver.com  (로컬 egress)
                              │
                              ▼  stdout JSON(한글 라벨) / stderr 진단
```

### 인터페이스 / 의존성

- 명령: `accounts | campaigns | adgroups | keywords | stats | report | keywordtool`
- 의존성: 표준 라이브러리만 (`hmac hashlib base64 json time urllib argparse os sys`)
- 키: 환경변수 `NAVER_AD_API_KEY` / `NAVER_AD_SECRET_KEY` / `NAVER_AD_CUSTOMER_ID`

### 체크리스트

- [x] `scripts/nsa.py` — 서명 코어(`sign`/`headers`/`load_creds`/`env_or_die`)
- [x] `nsa.py` — HTTP 코어(`api_get`/`api_post`/`die_with_hint`), uri는 path만 서명
- [x] `nsa.py` — argparse 진입점 + 7개 명령 디스패치
- [x] `nsa.py` — `stats` (fields/timeRange + 한글 라벨 + CTR/CPC 폴백)
- [x] `nsa.py` — `accounts`/`campaigns`/`adgroups`/`keywords` 조회
- [x] `nsa.py` — `keywordtool` (hintKeywords)
- [x] `nsa.py` — `report` (생성→폴링→다운로드)
- [x] `SKILL.md` 작성 (frontmatter + When to use/not + 호출법)
- [x] 단위 검증: 서명이 공식 샘플 알고리즘과 일치 (고정 입력 → 기대 base64)
- [x] CLI 검증: 키 없이 `--help`, 인자 누락 시 종료코드/메시지 정상
- [x] mock 검증: HTTP를 가짜로 갈아끼워 `stats` 한글 라벨·폴백 동작 확인
- [x] 문서 정합성: CLAUDE.md 명령 ↔ nsa.py 실제 명령 일치, 링크 유효

### Definition of Done (DoD)

1. `python3 scripts/nsa.py --help` 및 각 서브명령 `--help`가 에러 없이 출력된다.
2. 서명 단위 검증 통과 — 고정 입력에 대해 공식 알고리즘과 동일한 base64 서명을 만든다.
3. 키 미설정 시 `load_creds`가 명확한 메시지 + 종료코드 1로 멈춘다 (스택트레이스 노출 X).
4. mock HTTP로 `stats` 호출 시 노출/클릭/광고비/CTR가 한글 라벨로 출력되고, CTR 미제공 시 폴백 계산된다.
5. CLAUDE.md·SKILL.md·reference의 명령/필드가 `nsa.py` 실제 구현과 모순 없다.
6. 시크릿이 코드·문서·커밋에 하드코딩되어 있지 않다 (`grep` 확인).

> **라이브 호출(실제 네이버 응답) 검증은 DoD에 포함하지 않는다** — 사용자 키가 필요하므로 Day 2로 분리.

### 테스트 방법 (키 없이)

```bash
# 1. help/인자 검증
python3 scripts/nsa.py --help
python3 scripts/nsa.py stats            # 인자 누락 → 코드1 + 안내

# 2. 서명 단위 검증 (고정 입력)
python3 scripts/nsa.py _selftest        # 내장 셀프테스트: 서명·폴백 계산 assert

# 3. mock 검증 (env로 가짜 HTTP 주입)
NSA_MOCK=1 python3 scripts/nsa.py stats --ids x --since 2026-06-01 --until 2026-06-02

# 4. 키 미설정 시 멈춤 확인 (env 비우고)
python3 scripts/nsa.py campaigns        # → "환경변수 ... 없음" 코드1
```

## 의사결정 요약

상세는 `DECISIONS.md`.

- ADR-001 — 형태: 스킬+단일 스크립트 (MCP/모노레포 대신)
- ADR-002 — 의존성 0: 표준 라이브러리 urllib (requests 미사용)
- ADR-003 — 읽기 전용: 쓰기(PUT/DELETE) 미구현
- ADR-004 — 코워크 미지원: egress 차단으로 로컬 전용
- ADR-005 — 라이브 검증은 Day 2 분리: 키는 사용자만 발급 가능
- ADR-006 — 키 없는 검증: `_selftest` + `NSA_MOCK` (의존성 0)
- ADR-007 — 키 보관: macOS Keychain + 래퍼 (계정명 env 폴백)
- ADR-008 — 스킬 2개 분리: 조회(자동) + 셋업(수동 `disable-model-invocation`)
- ADR-009 — 셋업 마법사: `scripts/nsa init` / `doctor`
