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
