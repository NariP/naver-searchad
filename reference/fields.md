# 지표 한글 사전

네이버 검색광고 API 응답 필드 ↔ 한글 의미.

## 성과 지표 (`/stats`)

| 필드 | 한글 | 의미 |
|---|---|---|
| `impCnt` | 노출수 | 광고가 노출된 횟수 |
| `clkCnt` | 클릭수 | 광고가 클릭된 횟수 |
| `salesAmt` | 광고비 | 과금된 금액(원) |
| `ctr` | CTR | 클릭률 = 클릭수/노출수 × 100 (%) |
| `cpc` | CPC | 클릭당 비용 = 광고비/클릭수 (원) |
| `avgRnk` | 평균노출순위 | 광고 평균 게재 순위 |
| `ccnt` | 전환수 | 전환 발생 횟수 |

> CTR/CPC가 응답에 없으면 노출·클릭·광고비로 직접 계산(`output-policy.md`).

## 키워드 도구 (`/keywordstool`)

| 필드 | 한글 | 의미 |
|---|---|---|
| `relKeyword` | 연관키워드 | 힌트 키워드와 연관된 키워드 |
| `monthlyPcQcCnt` | 월간PC조회수 | 최근 한 달 PC 검색수 |
| `monthlyMobileQcCnt` | 월간모바일조회수 | 최근 한 달 모바일 검색수 |
| `monthlyAvePcClkCnt` | 월평균PC클릭수 | |
| `monthlyAveMobileClkCnt` | 월평균모바일클릭수 | |
| `compIdx` | 경쟁정도 | 낮음/중간/높음 |

## 구조 식별자

| 필드 | 의미 |
|---|---|
| `nccCampaignId` | 캠페인 ID |
| `nccAdgroupId` | 광고그룹 ID |
| `nccKeywordId` | 키워드 ID |
| `customerId` | 광고계정 ID |
