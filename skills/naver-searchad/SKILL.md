---
name: naver-searchad
displayName: 네이버 검색광고 성과 조회
description: 네이버 검색광고의 노출수·클릭수·광고비·CTR·CPC 등 성과를 조회한다(읽기 전용). 캠페인/광고그룹/키워드 목록, 기간별 성과, 대용량 리포트, 키워드 도구(연관키워드·월 조회수) 조회. 로컬 실행 전용(클로드 코드/코덱스) — 클라우드 샌드박스(코워크)에서는 네이버 차단으로 불가. 트리거 — "네이버 광고 노출수/클릭수/광고비/CTR 보여줘", "이번달 캠페인 성과", "키워드별 클릭률", "연관키워드 월 조회수", "검색광고 리포트 뽑아줘".
license: MIT
metadata:
  category: marketing
  locale: ko-KR
  phase: v1
---

# Naver SearchAd (네이버 검색광고 조회)

네이버 검색광고 API를 감싸 성과를 조회한다. **읽기 전용**, **로컬 실행 전용**. (자동 트리거 스킬)

루트(`scripts/`, `reference/`, `.claude/docs/`)는 이 스킬 디렉토리 기준 `../../` 에 있다.

## When to use

- "지난주/이번달 캠페인별 노출·클릭·광고비 보여줘"
- "이 키워드 CTR / CPC 어때"
- "연관키워드랑 월간 조회수 뽑아줘"
- "검색광고 기간 리포트 파일로 내려줘"
- "내 광고계정 / 캠페인 / 광고그룹 / 키워드 목록"

## When NOT to use

- 클로드 코워크·클라우드 샌드박스 (네이버 egress 차단 — `../../.claude/docs/environment-policy.md`)
- 입찰가 변경·키워드 삭제 등 **쓰기** 작업 (이 스킬은 조회만 — `../../.claude/docs/scope-policy.md`)
- 네이버 검색(블로그/뉴스/쇼핑) 결과 조회 (그건 검색 Open API, 다른 도메인)
- **키 셋업** (Keychain 저장) → 별도 수동 스킬 `naver-searchad-setup` 사용

## Prerequisites

먼저 환경 진단(어느 OS에서든 실행됨):
```bash
python3 scripts/nsa.py doctor   # OS·파이썬·키·네이버 도달 점검 + OS별 다음 단계 안내
```

키 3개가 필요하다. 미설정이면:
- macOS: `/naver-searchad-setup` (수동) → `scripts/nsa init` (Keychain 저장)
- Windows: 환경변수 직접 — `$env:NAVER_AD_API_KEY="..."` 등 후 `python scripts\nsa.py ...`
- 코덱스/Linux/CI: `export NAVER_AD_API_KEY=... NAVER_AD_SECRET_KEY=... NAVER_AD_CUSTOMER_ID=...`

## How to call

**macOS** — `scripts/nsa` 래퍼(Keychain→env→nsa.py 자동):
```bash
scripts/nsa campaigns
scripts/nsa stats --ids <campaignId,adgroupId> --since 2026-06-01 --until 2026-06-17
scripts/nsa keywordtool --keywords 제주여행,게스트하우스
scripts/nsa report --type AD --date 2026-06-17 --out ./report.tsv
```

**Windows** — `scripts\nsa.ps1` 래퍼(자격증명관리자→env→nsa.py 자동):
```powershell
.\scripts\nsa.ps1 campaigns
.\scripts\nsa.ps1 stats --ids <campaignId,adgroupId> --since 2026-06-01 --until 2026-06-17
```
> 첫 실행 시 "running scripts is disabled" 에러가 나면(Windows 기본 차단):
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (1회) 후 재시도.

환경변수를 직접 쓰면 어느 OS든 `python3 scripts/nsa.py <command>` 도 동일하게 동작.

전체 명령·필드 매핑 → `../../reference/endpoints.md`, `../../reference/fields.md`.
인증·서명 동작 → `../../.claude/docs/auth-signature.md`.

## Output

stdout에 JSON(한글 라벨 포함). 에러는 stderr + 원인 힌트(`../../.claude/docs/output-policy.md`).
