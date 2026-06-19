# naver-searchad — 네이버 검색광고 성과 조회 스킬 (v1.0.0)

네이버 검색광고 API를 감싸 **노출수·클릭수·광고비·CTR·CPC** 등 성과를 조회한다. **읽기 전용**, **로컬 실행 전용** (클로드 코드 / 코덱스). 버전 호환성: `README.md` 참조.

## Project

- 형태: **단일 스킬** — scripts·references를 스킬 폴더 안에 자체 보유 (vercel/sentry 표준 구조)
- 의존성: **0개** — 파이썬 표준 라이브러리만 (`hmac`/`hashlib`/`base64`/`urllib`)
- 인증: HMAC-SHA256 서명 (요청마다 계산). 키는 OS 보안저장소/환경변수/`.env`로.
- 범위: 조회(GET/조회용 POST)만. 입찰가 변경·삭제 등 쓰기 없음. 키 셋업·진단 포함.

## 구조

```
skills/naver-searchad/
├── SKILL.md          # 스킬 진입점 (조회 + 셋업 안내)
├── scripts/          # nsa.py(본체) · nsa(mac 래퍼) · nsa.ps1(win 래퍼)
└── references/       # endpoints·fields 사전 + 정책 4종
```

스킬이 자기 안에 모든 걸 가져, `skills add` 또는 폴더 링크 한 번으로 완결 설치된다.

## Architecture

```
사용자 자연어 ("지난주 노출수 보여줘")
   ↓  ← SKILL.md(When to use) + references/endpoints.md 가 매칭 가이드
클로드가 명령 선택
   ↓
python3 <skill>/scripts/nsa.py <command> [opts]
   ↓  ← 서명(ts.method.uri) + urllib HTTP
https://api.searchad.naver.com   (로컬에서만 도달 가능)
   ↓
stdout JSON (한글 라벨) → 클로드가 표로 렌더
```

## 환경 (Prerequisites)

키 3개 (네이버 검색광고 > 도구 > API 사용 관리에서 발급):

| 변수 | 네이버 명칭 |
|---|---|
| `NAVER_AD_API_KEY` | 액세스 라이선스 |
| `NAVER_AD_SECRET_KEY` | 비밀키 |
| `NAVER_AD_CUSTOMER_ID` | 계정(customer) ID |

키 공급 우선순위: 환경변수 → OS 보안저장소(키체인/자격증명관리자) → `.env`.

## 주요 명령어

스킬 폴더 안 `scripts/` 기준. macOS는 `nsa` 래퍼(보안저장소→env 자동), 그 외는 `python3 nsa.py`:

```bash
nsa doctor                                   # 환경 진단
nsa init                                      # 키 저장 (보안저장소)
nsa accounts | campaigns                      # 계정·캠페인 목록
nsa adgroups --campaign <id>                  # 광고그룹
nsa keywords --adgroup <id>                   # 키워드
nsa stats --ids <ids> --since <d> --until <d> # ★ 성과 조회
nsa report --type AD --date <d> --out f.tsv   # 대용량 리포트
nsa keywordtool --keywords 제주여행,게스트하우스  # 키워드 도구
```

## 금지 / 제약

- ❌ 코워크·클라우드 샌드박스에서 실행 (네이버 egress 차단 — `references/environment-policy.md`)
- ❌ 쓰기 작업 (입찰가 변경·키워드 삭제 등) — 이 스킬은 조회만
- ❌ 시크릿을 코드·문서·커밋에 박기 — 보안저장소/환경변수/`.env`(gitignore)만
- ⚠️ 시스템 시계가 틀어지면 인증 실패 (서명에 timestamp 포함)

## 상세 가이드 (네비게이션)

`skills/naver-searchad/references/` 안:
- 인증/서명: `auth-signature.md` — HMAC 서명·헤더·키 보관
- 실행 환경: `environment-policy.md` — OS별·코워크 egress
- 조회 범위: `scope-policy.md` — 읽기 전용 원칙
- 출력/에러: `output-policy.md` — JSON 포맷·에러 힌트
- 엔드포인트 카탈로그(트리거 사전): `endpoints.md`
- 지표 한글 사전: `fields.md`

(내부 전용, 비공개) 작업 목표·결정 로그: `.claude/.private/GOAL.md`, `.claude/.private/DECISIONS.md` — gitignore됨
