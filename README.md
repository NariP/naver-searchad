# 네이버 검색광고 성과 조회 (naver-searchad)

네이버 검색광고 API를 감싸 **노출수·클릭수·광고비·CTR·CPC** 등 성과를 조회하는 Claude 스킬. **읽기 전용**, **로컬 실행 전용**.

> 채팅에서 "지난달 네이버 광고 노출수·클릭수·광고비 보여줘" 하면 캠페인별 성과를 표로 돌려준다.

## 무엇을 조회하나

| 명령 | 조회 내용 |
|---|---|
| `stats` ⭐ | **노출수·클릭수·광고비·CTR·CPC·평균순위·전환수** (기간별) |
| `campaigns` / `adgroups` / `keywords` | 캠페인·광고그룹·키워드 목록 |
| `accounts` | 내 광고계정 목록 |
| `report` | 대용량 기간 리포트(TSV 다운로드) |
| `keywordtool` | 연관키워드·월간 조회수·경쟁도 |

**읽기 전용**이라 입찰가 변경·키워드 삭제 같은 쓰기 작업은 하지 않는다(광고 운영 사고 방지).

## 구성

| | 스킬 | 역할 | 트리거 |
|---|---|---|---|
| 1 | `naver-searchad` | 성과 조회 | 자동 |
| 2 | `naver-searchad-setup` | 키 셋업·진단 | 수동 |

실행체는 `scripts/nsa.py`(파이썬 표준 라이브러리만, 의존성 0). OS별 래퍼: macOS `scripts/nsa`(bash), Windows `scripts/nsa.ps1`(PowerShell).

## 사전 준비 — API 키 3개

네이버 검색광고 > 도구 > **API 사용 관리**에서 발급:

| 키 | 네이버 명칭 |
|---|---|
| `NAVER_AD_API_KEY` | 액세스 라이선스 |
| `NAVER_AD_SECRET_KEY` | 비밀키 |
| `NAVER_AD_CUSTOMER_ID` | CUSTOMER ID(계정번호) |

## 설치

**방법 1 — skills CLI (권장)**
```bash
npx skills add NariP/naver-searchad
```
공개 레포에서 두 스킬(`naver-searchad`, `naver-searchad-setup`)을 바로 설치한다.

**방법 2 — 직접 clone**
```bash
git clone https://github.com/NariP/naver-searchad.git
cd naver-searchad
```

설치 후 아래 순서대로 진행한다. 스크립트는 레포 루트 기준 `scripts/` 에 있다.

## 사용

### 1) 환경 진단 (어느 OS든)
```bash
python3 scripts/nsa.py doctor
```
OS·파이썬·키·네이버 도달을 점검하고, 환경에 맞는 다음 단계를 안내한다.

### 2) 키 저장 (OS별)

| OS | 키 보관 | 셋업 |
|---|---|---|
| **macOS** | 키체인 | `scripts/nsa init` |
| **Windows** | 자격증명관리자 | `.\scripts\nsa.ps1 init` |
| **Linux/CI** | 환경변수 또는 `.env` | `export ...` 또는 `.env` 작성 |

> Windows에서 `running scripts is disabled` 에러 시:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (1회)

### 3) 조회
```bash
# macOS
scripts/nsa campaigns
scripts/nsa stats --ids <campaignId> --since 2026-06-01 --until 2026-06-17

# Windows
.\scripts\nsa.ps1 stats --ids <campaignId> --since 2026-06-01 --until 2026-06-17

# 환경변수/.env 직접
python3 scripts/nsa.py campaigns
```

## 키 공급 우선순위

`1. 환경변수` → `2. OS 보안저장소(키체인/자격증명관리자)` → `3. .env 파일(평문 폴백)`

`.env`는 평문이라 보안저장소가 가능한 환경에선 그쪽을 권장. `.env`는 `.gitignore`로 커밋 차단된다.

## 동작 환경

| 환경 | 조회 | 비고 |
|---|---|---|
| 클로드 코드 / 코덱스 / 데스크탑 (로컬) | ✅ | |
| Linux / CI | ✅ | |
| 클로드 코워크 (클라우드 샌드박스) | ❌ | 네이버 egress 차단 |

> 클라우드 샌드박스는 외부 도메인 차단으로 네이버 호출이 불가하다. 로컬에서 실행할 것.

## 인증 방식

요청마다 HMAC-SHA256 서명(`X-Timestamp`/`X-API-KEY`/`X-Customer`/`X-Signature`). 시크릿은 네트워크에 직접 노출되지 않으며, 코드·커밋에 키를 박지 않는다(환경변수/보안저장소만).

## 버전 호환성

네이버 검색광고 API는 URL에 명시적 버전 번호가 없다(`api.searchad.naver.com`). 따라서 "API 버전" 대신 **base URL + 사용 엔드포인트 셋 + 검증 시점**으로 호환성을 표기한다.

| 스킬 버전 | 네이버 API base | 사용 엔드포인트 | 라이브 검증 |
|---|---|---|---|
| **1.0.0** | `api.searchad.naver.com` | `/stats`, `/ncc/campaigns`, `/ncc/adgroups`, `/ncc/keywords`, `/customer-links`, `/keywordstool`, `/stat-reports` | 2026-06 (campaigns·stats 확인) |

엔드포인트별 상세·필드는 `reference/endpoints.md`. 네이버가 엔드포인트·필드를 바꾸면 스킬 마이너 버전을 올리고 이 표에 추가한다.

## 라이선스

MIT
