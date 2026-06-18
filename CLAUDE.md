# naver-searchad — 네이버 검색광고 성과 조회 스킬

네이버 검색광고 API를 감싸 **노출수·클릭수·광고비·CTR·CPC** 등 성과를 조회한다. **읽기 전용**, **로컬 실행 전용** (클로드 코드 / 코덱스).

## Project

- 형태: **스킬 2개**(조회/셋업) + 공유 스크립트(`scripts/nsa`, `scripts/nsa.py`)
- 의존성: **0개** — 파이썬 표준 라이브러리만 (`hmac`/`hashlib`/`base64`/`urllib`)
- 인증: HMAC-SHA256 서명 (요청마다 계산). 키는 Keychain/환경변수로.
- 범위: 조회(GET/조회용 POST)만. 입찰가 변경·삭제 등 쓰기 없음.

### 스킬 2개 (트리거 옵션 분리)

| 스킬 | 역할 | 트리거 |
|---|---|---|
| `skills/naver-searchad` | 성과 조회 | **자동** (클로드가 맥락 보고 띄움) |
| `skills/naver-searchad-setup` | 키 Keychain 저장/점검 | **수동 전용** (`disable-model-invocation: true`) |

셋업을 수동 전용으로 둔 이유: 키 저장은 사용자가 의도적으로 할 일. 자동 트리거 부적합.

## Architecture

```
사용자 자연어 ("지난주 노출수 보여줘")
   ↓  ← SKILL.md(When to use) + reference/endpoints.md 가 매칭 가이드
클로드가 명령 선택
   ↓
python3 scripts/nsa.py <command> [opts]
   ↓  ← 서명(ts.method.uri) + urllib HTTP
https://api.searchad.naver.com   (로컬에서만 도달 가능)
   ↓
stdout JSON (한글 라벨) → 클로드가 표로 렌더
```

자세한 명령·필드는 `reference/` 참조.

## 환경 (Prerequisites)

환경변수 3개 (1회 설정):

| 변수 | 값 | 발급처 |
|---|---|---|
| `NAVER_AD_API_KEY` | 액세스 라이선스 | 네이버 검색광고 > 도구 > API 사용 관리 |
| `NAVER_AD_SECRET_KEY` | 비밀키 | 〃 |
| `NAVER_AD_CUSTOMER_ID` | 계정(customer) ID | 〃 |

## 주요 명령어

macOS는 `./scripts/nsa <command>` 래퍼 권장(Keychain→env 자동). 아래는 환경변수 직접 사용 시.

```bash
python3 scripts/nsa.py accounts                              # 광고계정 목록
python3 scripts/nsa.py campaigns                             # 캠페인 목록
python3 scripts/nsa.py adgroups   --campaign <id>           # 광고그룹 목록
python3 scripts/nsa.py keywords   --adgroup  <id>           # 키워드 목록
python3 scripts/nsa.py stats --ids <ids> --since <d> --until <d>   # ★ 성과 조회
python3 scripts/nsa.py report --type AD --date <d> --out f.tsv     # 대용량 리포트
python3 scripts/nsa.py keywordtool --keywords 제주여행,게스트하우스  # 키워드 도구
```

## 금지 / 제약

- ❌ 코워크·클라우드 샌드박스에서 실행 (네이버 egress 차단됨 — `.claude/docs/environment-policy.md`)
- ❌ 쓰기 작업 (입찰가 변경·키워드 삭제 등) — 이 스킬은 조회만
- ❌ 시크릿을 코드·문서·커밋에 박기 — 반드시 환경변수
- ⚠️ 시스템 시계가 틀어지면 인증 실패 (서명에 timestamp 포함)

## 상세 가이드 (네비게이션)

- 조회 스킬: `skills/naver-searchad/SKILL.md` — 자동 트리거
- 셋업 스킬: `skills/naver-searchad-setup/SKILL.md` — 수동 전용(키 등록/점검)
- 인증/서명 정책: `.claude/docs/auth-signature.md` — HMAC 서명·헤더·함정
- 실행 환경 정책: `.claude/docs/environment-policy.md` — 어디서 되고 안 되나
- 조회 범위 정책: `.claude/docs/scope-policy.md` — 읽기 전용 원칙·금지 작업
- 출력/에러 정책: `.claude/docs/output-policy.md` — JSON 포맷·에러 힌트
- 엔드포인트 카탈로그(트리거 사전): `reference/endpoints.md`
- 지표 한글 사전: `reference/fields.md`
- 작업 목표/완료 조건: `GOAL.md` · 결정 로그: `DECISIONS.md`
