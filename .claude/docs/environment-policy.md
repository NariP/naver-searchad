# 실행 환경 정책

이 스킬은 **로컬 실행 전용**이다. 네이버 검색광고 API 호출에는 외부 네트워크(egress)가 필요한데, 클라우드 샌드박스는 그걸 막는다.

## 환경별 동작 (실측 기준)

| 환경 | 서명/연산 | 네이버 egress | 라이브 수집 |
|---|---|---|---|
| 클로드 코드 (로컬 CLI) | ✅ | ✅ | ✅ **지원** |
| 코덱스 (로컬 CLI) | ✅ | ✅ | ✅ **지원** |
| 클로드 데스크탑 (로컬) | ✅ | ✅ | ✅ (참고: MCP/.mcpb로도 가능) |
| **클로드 코워크 (클라우드 샌드박스)** | ✅ | ❌ 차단 | ❌ **미지원** |

## 왜 코워크는 안 되나

- 코워크 샌드박스는 **egress allowlist(기본 차단, 허용된 도메인만 통과)** 방식.
- `api.searchad.naver.com`은 allowlist에 없어 막힌다. (구글조차 막힘 — 네이버만의 문제 아님)
- 프록시를 타도 목적지가 allowlist에 없으면 프록시가 직접 거절(403 tunnel).
- allowlist는 Anthropic 인프라 정책이라 **개인 계정에서 관리 UI 없음** → 우회 불가.

## 대응

- **수집은 로컬에서.** 클로드 코드 / 코덱스 / 데스크탑.
- 코워크에서 분석이 필요하면: 로컬이 결과를 파일(JSON/CSV/TSV)로 떨궈두고, 코워크는 **그 파일만 읽어 분석**. (네이버 호출 없음)

## OS별 키 공급 (조회는 모든 OS 가능)

`nsa.py`는 환경변수만 읽으므로 OS 무관하게 동작한다. 키를 주입하는 방법만 OS별로 다르다.

| OS | 키 공급 | 실행 |
|---|---|---|
| macOS | Keychain (`scripts/nsa init`) 또는 환경변수 | `scripts/nsa <cmd>` (bash 래퍼) |
| Windows | 자격증명관리자 (`scripts\nsa.ps1 init`) 또는 환경변수 | `scripts\nsa.ps1 <cmd>` (PS 래퍼) |
| Linux/코덱스/CI | 환경변수(`export ...`) | `python3 scripts/nsa.py <cmd>` |

> ⚠️ **Windows 래퍼(`nsa.ps1`)는 아직 Windows 실측 검증 전이다.** .NET PasswordVault(OS 내장, 모듈 0)를 쓰는 검증된 패턴으로 작성했으나, 실제 Windows 실행 확인은 미완. 맥/리눅스 경로는 검증됨.

## 자가 점검 (실행 전 확인용)

가장 확실: 크로스플랫폼 진단 명령.
```bash
python3 scripts/nsa.py doctor        # OS·파이썬·키·네이버 도달 + OS별 안내
python3 scripts/nsa.py doctor --no-net   # 네트워크 체크 생략
```

수동 egress 확인(참고):
```bash
# 404/401 = 도달(OK). 000/타임아웃 = egress 차단(코워크 등, 불가)
curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" --max-time 8 https://api.searchad.naver.com/
```
