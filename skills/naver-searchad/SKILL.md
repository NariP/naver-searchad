---
name: naver-searchad
displayName: 네이버 검색광고 성과 조회
version: 1.0.0
description: 네이버 검색광고의 노출수·클릭수·광고비·CTR·CPC 등 성과를 조회한다(읽기 전용). 캠페인/광고그룹/키워드 목록, 기간별 성과, 대용량 리포트, 키워드 도구(연관키워드·월 조회수) 조회. 키 셋업·환경 진단 포함. 로컬 실행 전용(클로드 코드/코덱스) — 클라우드 샌드박스(코워크)에서는 네이버 차단으로 불가. 트리거 — "네이버 광고 노출수/클릭수/광고비/CTR 보여줘", "이번달 캠페인 성과", "키워드별 클릭률", "연관키워드 월 조회수", "검색광고 리포트 뽑아줘", "네이버 검색광고 키 셋업".
license: MIT
metadata:
  category: marketing
  locale: ko-KR
  phase: v1
---

# Naver SearchAd (네이버 검색광고 조회)

네이버 검색광고 API를 감싸 성과를 조회한다. **읽기 전용**, **로컬 실행 전용**.

> **스크립트 경로**: 실행체(`scripts/nsa.py` 등)는 이 `SKILL.md`와 같은 폴더의 `scripts/` 에 있다.
> - 클로드 코드: `${CLAUDE_SKILL_DIR}/scripts/nsa.py`
> - 코덱스: `$CODEX_HOME/skills/naver-searchad/scripts/nsa.py`
> - 직접 clone: 레포 안 `skills/naver-searchad/scripts/nsa.py`
> 아래 예시는 `SKILL_DIR` 가 이 스킬 폴더라고 가정한다.

## When to use

- "지난주/이번달 캠페인별 노출·클릭·광고비 보여줘"
- "이 키워드 CTR / CPC 어때"
- "연관키워드랑 월간 조회수 뽑아줘"
- "검색광고 기간 리포트 파일로 내려줘"
- "내 광고계정 / 캠페인 / 광고그룹 / 키워드 목록"
- "네이버 검색광고 키 셋업 / 키 다시 등록" (셋업도 이 스킬)

## When NOT to use

- 클라우드 샌드박스(코워크): 네이버 egress 차단 → `references/environment-policy.md`
- 입찰가 변경·키워드 삭제 등 **쓰기**: 이 스킬은 조회만 → `references/scope-policy.md`
- 네이버 검색(블로그/뉴스/쇼핑) 결과 조회: 그건 검색 Open API, 다른 도메인

## Prerequisites — 진단 & 키 셋업

먼저 진단(어느 OS든 실행됨):
```bash
python3 "$SKILL_DIR/scripts/nsa.py" doctor   # OS·파이썬·키·네이버 도달 점검 + 다음 단계 안내
```

키 3개가 필요하다(네이버 검색광고 > 도구 > API 사용 관리에서 발급):

| OS | 키 보관 | 셋업 |
|---|---|---|
| macOS | 키체인 | `"$SKILL_DIR/scripts/nsa" init` |
| Windows | 자격증명관리자 | `& "$SKILL_DIR/scripts/nsa.ps1" init` |
| Linux/코덱스/CI | 환경변수 또는 `.env` | `export NAVER_AD_API_KEY=... NAVER_AD_SECRET_KEY=... NAVER_AD_CUSTOMER_ID=...` |

> ⚠️ **키는 사용자가 직접 입력한다.** 클로드는 키 값을 대신 받아 입력하지 않는다(시크릿이 대화·로그에 남지 않게). 키 셋업이 필요하면 사용자에게 위 `init` 또는 `nsa.py setup` 실행을 안내만 한다.

키 공급 우선순위: 환경변수 → OS 보안저장소 → `.env`. 상세 → `references/auth-signature.md`.

## How to call

macOS는 `scripts/nsa` 래퍼(보안저장소→env→nsa.py 자동), 그 외는 `python3 scripts/nsa.py`:
```bash
"$SKILL_DIR/scripts/nsa" campaigns
"$SKILL_DIR/scripts/nsa" stats --ids <campaignId,adgroupId> --since 2026-06-01 --until 2026-06-17
"$SKILL_DIR/scripts/nsa" keywordtool --keywords 제주여행,게스트하우스
"$SKILL_DIR/scripts/nsa" report --type AD --date 2026-06-17 --out ./report.tsv
```
Windows: `& "$SKILL_DIR/scripts/nsa.ps1" stats ...` / 환경변수 직접 시: `python3 "$SKILL_DIR/scripts/nsa.py" <command>`.

명령·필드 매핑 → `references/endpoints.md`, `references/fields.md`.

## 명령 요약

| 명령 | 조회 |
|---|---|
| `stats` ⭐ | 노출수·클릭수·광고비·CTR·CPC·평균순위·전환수 |
| `campaigns`/`adgroups`/`keywords`/`accounts` | 구조 목록 |
| `report` | 대용량 기간 리포트(TSV) |
| `keywordtool` | 연관키워드·월 조회수 |
| `doctor`/`setup` | 환경 진단 / 키 채움 |

## Output

stdout에 JSON(한글 라벨 포함). 에러는 stderr + 원인 힌트 → `references/output-policy.md`.
