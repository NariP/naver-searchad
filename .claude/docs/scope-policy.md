# 조회 범위 정책 (읽기 전용)

이 스킬은 **읽기 전용(조회)** 이다. 광고 계정을 변경하는 어떤 작업도 하지 않는다.

## 허용 (조회)

| 명령 | 엔드포인트 | method | 설명 |
|---|---|---|---|
| `accounts` | `/customer-links` | GET | 내 광고계정 목록 |
| `campaigns` | `/ncc/campaigns` | GET | 캠페인 목록 |
| `adgroups` | `/ncc/adgroups` | GET | 광고그룹 목록 |
| `keywords` | `/ncc/keywords` | GET | 키워드 목록 |
| `stats` | `/stats` | GET | 성과(노출·클릭·광고비·CTR·CPC) |
| `report` | `/stat-reports` | GET/POST | 대용량 기간 리포트 생성·다운로드 |
| `keywordtool` | `/keywordstool` | GET | 연관키워드·월간 조회수 |

> `report`의 POST(`/stat-reports`)와 `keywordtool`은 **조회 목적의 POST/GET**이다. 계정 상태를 바꾸지 않으므로 읽기 전용 원칙에 부합한다.

## 금지 (쓰기)

다음은 **구현하지 않는다.** 실수로 광고 운영에 영향을 주지 않기 위함.

- ❌ 입찰가 변경 (`PUT /ncc/keywords` bidAmt 등)
- ❌ 캠페인/그룹/키워드 생성·수정·삭제 (`POST`/`PUT`/`DELETE /ncc/*`)
- ❌ 예산·노출 설정 변경
- ❌ userLock 토글 등 상태 변경

## 변경이 필요해지면

쓰기 기능은 별도 스킬/별도 승인 흐름으로 분리한다. 이 스킬에 끼워넣지 않는다.
(돈이 직접 나가는 작업 ↔ 단순 조회는 안전 경계를 분리해 둔다.)
