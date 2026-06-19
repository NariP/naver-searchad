# 출력 / 에러 정책

## 출력 형식

- 기본: **stdout에 JSON** (UTF-8, `ensure_ascii=False`, indent 2). 클로드가 파싱해 표로 렌더.
- `stats`/`keywordtool` 응답은 **한글 라벨을 덧붙인다** (원본 필드는 유지).
- `report`는 다운로드한 **TSV 파일 경로**를 출력.
- 모든 에러·진단 메시지는 **stderr**로. stdout은 항상 깨끗한 데이터만 (파이프·파일 저장 안전).

## 한글 라벨 매핑 (stats)

| 원본 | 한글 |
|---|---|
| `impCnt` | 노출수 |
| `clkCnt` | 클릭수 |
| `salesAmt` | 광고비 |
| `ctr` | CTR |
| `cpc` | CPC |
| `avgRnk` | 평균노출순위 |
| `ccnt` | 전환수 |

### 파생 계산 (API가 값을 안 줄 때 폴백)

- `CTR = clkCnt / impCnt × 100` (impCnt=0 이면 0)
- `CPC = salesAmt / clkCnt` (clkCnt=0 이면 0)

## 에러 힌트 (HTTP 상태 → 원인 안내)

| 상태 | 안내 |
|---|---|
| 401 | 서명 실패 — 키가 맞는지 / 시스템 시계가 정확한지 확인 |
| 403 | 권한 없음 — 이 customer_id에 조회 권한이 있는지 |
| 404 | id를 못 찾음 — campaign/adgroup id 확인 |
| 429 | 호출 한도 초과 — 잠시 후 재시도 |
| 000/timeout | egress 차단 — 로컬 환경에서 실행했는지 (environment-policy.md) |

응답 본문도 함께 출력해 디버깅을 돕는다.

## 종료 코드

- 0: 성공
- 1: 사용자 오류(인자 누락·키 없음 등)
- 2: API 오류(HTTP 4xx/5xx)
