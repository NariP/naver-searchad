# 인증 / 서명 정책

네이버 검색광고 API는 요청마다 **HMAC-SHA256 서명**을 요구한다. 검색 Open API(키를 헤더에 그대로 첨부)와 다르다.

## 헤더 4종

| 헤더 | 값 |
|---|---|
| `X-Timestamp` | 밀리초 epoch (`round(time.time()*1000)`) |
| `X-API-KEY` | 액세스 라이선스 (`NAVER_AD_API_KEY`) |
| `X-Customer` | 계정 ID (`NAVER_AD_CUSTOMER_ID`) |
| `X-Signature` | 아래 서명 |

## 서명 계산

```
message   = "{timestamp}.{method}.{uri}"        # 예: "1718700000000.GET./stats"
signature = base64( HMAC_SHA256(message, SECRET_KEY) )
```

- 해시: HMAC-SHA256 → 출력은 **base64** (hex 아님. 헤더에 짧게 싣기 위함)
- `timestamp`: ms 단위 (replay 방지)
- 공식 파이썬 샘플과 동일 (`naver/searchad-apidoc/python-sample`)

## 함정 (입문자가 자주 틀리는 것)

1. **`uri`는 path만** — 서명에 들어가는 `uri`는 **쿼리스트링 제외**. `/stats` O, `/stats?ids=...` ✗.
   쿼리는 실제 요청 URL에만 붙이고, 서명 message에는 path만.
2. **method 대문자** — `GET`/`POST`. 소문자 쓰면 서명 깨짐.
3. **시계 동기화** — 시스템 시계가 서버와 분 단위로 어긋나면 서명은 맞아도 인증 실패(replay 창 밖).
4. **timestamp 재사용 금지** — 요청마다 새로 찍는다.

## 왜 이 방식인가 (배경)

- 시크릿을 네트워크에 직접 안 보냄 → 도청 안전
- `method`+`uri` 포함 → 요청 위변조 방지
- `timestamp` 포함 → replay(재전송) 차단

AWS SigV4 / PG 결제 서명 / GitHub 웹훅 `X-Hub-Signature`와 같은 계열.

## 키 보관 원칙

- 시크릿은 **환경변수에서만** 읽는다. 코드·문서·커밋·로그에 절대 노출 금지.
- 스크립트는 키가 없으면 명확한 메시지와 함께 즉시 종료(`env_or_die`).

### macOS Keychain (권장)

평문(`.env`·`.zshrc`) 대신 Keychain에 암호화 저장하고, 래퍼(`scripts/nsa`)가 꺼내 환경변수로 주입한다. `nsa.py`는 환경변수만 읽으므로 코드 변경 없음.

**계정 이름(키체인 Account)**: 래퍼는 `NSA_KEYCHAIN_ACCOUNT`가 있으면 그 값, 없으면 `$USER`로 조회한다. 오픈소스 배포 시 하드코딩을 피하기 위함 — 받는 사람은 설정 없이 자기 `$USER`로 동작하고, 회사/공용 계정으로 구분하려면 `export NSA_KEYCHAIN_ACCOUNT=mycompany`.

저장(1회, 사용자가 직접 — 값에 실제 키. `ACC`=위 계정 이름):
```bash
ACC="${NSA_KEYCHAIN_ACCOUNT:-$USER}"
security add-generic-password -U -a "$ACC" -s NAVER_AD_API_KEY     -w '값'
security add-generic-password -U -a "$ACC" -s NAVER_AD_SECRET_KEY  -w '값'
security add-generic-password -U -a "$ACC" -s NAVER_AD_CUSTOMER_ID -w '값'
```
GUI(키체인 접근)로 저장 시: 제목=`NAVER_AD_*`, 사용자 이름=`$ACC`, 암호=키 값.

실행: `./scripts/nsa <command>` (래퍼가 Keychain→env→nsa.py).

이미 환경변수가 설정돼 있으면 래퍼는 Keychain을 건너뛴다(코덱스/CI 호환). 즉 코덱스 등 Keychain 없는 환경에선 환경변수로 직접 주입하면 된다.

### 키 공급 우선순위

`nsa.py`는 환경변수만 읽되, 없으면 `.env`로 폴백한다:

1. **환경변수** (최우선) — CI·명시적 주입. 래퍼(`nsa`/`nsa.ps1`)가 보안저장소에서 꺼내 여기 채움.
2. **OS 보안저장소** — macOS Keychain / Windows 자격증명관리자 (래퍼가 1번으로 변환).
3. **`.env` 파일** (폴백, 평문) — 탐색: `NSA_DOTENV` 경로 > 현재 디렉토리 > 레포 루트. `KEY=VALUE` 형식. `.gitignore`로 커밋 차단됨.

`.env`는 평문이므로 보안저장소가 가능한 환경에선 그쪽을 권장. 리눅스/CI 등 보안저장소가 없을 때의 편의 폴백이다.
