# 엔드포인트 카탈로그 (트리거 사전)

클로드가 사용자의 자연어 ↔ 명령을 매칭하는 표. Base URL: `https://api.searchad.naver.com`

| 사용자가 이렇게 말하면 | 명령 | API (method path) | 핵심 필드/인자 |
|---|---|---|---|
| "내 광고계정 뭐 있어", "계정 목록" | `accounts` | GET `/customer-links` | type=MYCLIENTS |
| "캠페인 목록", "무슨 캠페인 돌고 있어" | `campaigns` | GET `/ncc/campaigns` | nccCampaignId, name |
| "이 캠페인 광고그룹", "그룹 보여줘" | `adgroups` | GET `/ncc/adgroups` | `--campaign` |
| "이 그룹 키워드", "키워드 목록" | `keywords` | GET `/ncc/keywords` | `--adgroup` |
| **"노출수/클릭수/광고비/CTR/CPC 보여줘"** | `stats` | GET `/stats` | impCnt, clkCnt, salesAmt, ctr, cpc, avgRnk, ccnt |
| "지난주/이번달 성과", "기간별 성과" | `stats` | GET `/stats` | `--since --until` |
| "일별로 쪼개서" | `stats --by day` | GET `/stats` | breakdown=day |
| "기간 리포트 파일로", "대용량 다운로드" | `report` | POST→GET `/stat-reports` | reportTp, statDt |
| "연관키워드", "월 조회수", "키워드 발굴" | `keywordtool` | GET `/keywordstool` | monthlyPcQcCnt, monthlyMobileQcCnt, compIdx |

## 명령별 상세

### stats (성과 조회 — 핵심)
```
GET /stats
  ids       : 캠페인/그룹/키워드 id 배열
  fields    : '["impCnt","clkCnt","salesAmt","ctr","cpc","avgRnk","ccnt"]'  (문자열화 JSON)
  timeRange : '{"since":"2026-06-01","until":"2026-06-17"}'                 (문자열화 JSON)
```

### report (대용량 리포트)
```
POST /stat-reports  {reportTp, statDt}   → reportJobId
GET  /stat-reports/{id}                  → status(BUILDING→BUILT), downloadUrl
download(downloadUrl) → TSV
```
reportTp 예: `AD`(광고), `AD_DETAIL`, `AD_CONVERSION` 등.

### keywordtool (키워드 도구)
```
GET /keywordstool
  hintKeywords : "제주여행,게스트하우스"
  showDetail   : 1
→ keywordList[]: relKeyword, monthlyPcQcCnt, monthlyMobileQcCnt, compIdx,
                 monthlyAvePcClkCnt, monthlyAveMobileClkCnt
```

## 출처
- 공식: https://github.com/naver/searchad-apidoc (python-sample)
- 인증·서명: `.claude/docs/auth-signature.md`
