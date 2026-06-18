#!/usr/bin/env python3
"""naver-searchad (nsa) — 네이버 검색광고 성과 조회 CLI (읽기 전용, 로컬 전용).

표준 라이브러리만 사용. 인증은 HMAC-SHA256 서명(요청마다).
키는 환경변수: NAVER_AD_API_KEY / NAVER_AD_SECRET_KEY / NAVER_AD_CUSTOMER_ID

정책/필드 상세: ../.claude/docs/*, ../reference/*
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.searchad.naver.com"
FIELDS_STATS = ["impCnt", "clkCnt", "salesAmt", "ctr", "cpc", "avgRnk", "ccnt"]

# 원본 필드 → 한글 라벨 (output-policy.md)
LABELS = {
    "impCnt": "노출수",
    "clkCnt": "클릭수",
    "salesAmt": "광고비",
    "ctr": "CTR",
    "cpc": "CPC",
    "avgRnk": "평균노출순위",
    "ccnt": "전환수",
}


# ─────────────────────────── 진단/종료 ───────────────────────────
def eprint(*a):
    print(*a, file=sys.stderr)


def die(msg, code=1):
    eprint(f"[nsa] {msg}")
    sys.exit(code)


def env_or_die(name):
    v = os.environ.get(name)
    if not v:
        die(
            f"환경변수 {name} 없음. 3개 모두 설정 필요: "
            "NAVER_AD_API_KEY / NAVER_AD_SECRET_KEY / NAVER_AD_CUSTOMER_ID "
            "(네이버 검색광고 > 도구 > API 사용 관리에서 발급)",
            code=1,
        )
    return v


# ─────────────────────────── 서명/헤더 ───────────────────────────
def sign(timestamp, method, uri, secret_key):
    """공식 알고리즘: base64( HMAC_SHA256( "{ts}.{method}.{uri}", secret ) ).

    uri는 반드시 path만 (쿼리스트링 제외). auth-signature.md 참조.
    """
    message = f"{timestamp}.{method}.{uri}"
    digest = hmac.new(
        secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def load_creds():
    return (
        env_or_die("NAVER_AD_API_KEY"),
        env_or_die("NAVER_AD_SECRET_KEY"),
        env_or_die("NAVER_AD_CUSTOMER_ID"),
    )


def headers(method, uri):
    api_key, secret, customer = load_creds()
    ts = str(round(time.time() * 1000))  # ms epoch (replay 방지)
    return {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Timestamp": ts,
        "X-API-KEY": api_key,
        "X-Customer": str(customer),
        "X-Signature": sign(ts, method, uri, secret),
    }


# ─────────────────────────── HTTP 코어 ───────────────────────────
def _http(method, uri, params=None, body=None):
    """실제 HTTP. NSA_MOCK=1 이면 가짜 응답 반환(키 불필요, 네트워크 없음)."""
    if os.environ.get("NSA_MOCK"):
        return _mock_response(uri, params)

    url = BASE_URL + uri
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    # 서명은 path(uri)만으로 — 쿼리 제외
    req = urllib.request.Request(url, data=data, headers=headers(method, uri), method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        _die_with_hint(e)
    except urllib.error.URLError as e:
        die(
            f"네트워크 연결 실패: {e.reason}. egress 차단 환경(코워크 등)일 수 있음 — "
            "로컬(클로드 코드/코덱스)에서 실행하세요. (environment-policy.md)",
            code=2,
        )


def api_get(uri, params=None):
    return _http("GET", uri, params=params)


def api_post(uri, body, params=None):
    return _http("POST", uri, params=params, body=body)


def _die_with_hint(http_err):
    code = http_err.code
    hint = {
        401: "서명 실패 — 키가 맞는지 / 시스템 시계가 정확한지 확인",
        403: "권한 없음 — 이 customer_id에 조회 권한이 있는지",
        404: "id를 못 찾음 — campaign/adgroup id 확인",
        429: "호출 한도 초과 — 잠시 후 재시도",
    }.get(code, "")
    try:
        body = http_err.read().decode("utf-8")
    except Exception:
        body = ""
    die(f"HTTP {code} {hint}\n{body}", code=2)


# ─────────────────────────── 출력 헬퍼 ───────────────────────────
def emit(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _pct(num, den):
    return round(num / den * 100, 2) if den else 0.0


def _safe_div(num, den):
    return round(num / den, 1) if den else 0.0


def humanize_stats(rows):
    """원본 필드 유지 + 한글 라벨 덧붙임 + CTR/CPC 폴백 계산."""
    if isinstance(rows, dict):
        rows = rows.get("data", rows.get("statList", [rows]))
    out = []
    for r in rows:
        imp = r.get("impCnt", 0) or 0
        clk = r.get("clkCnt", 0) or 0
        cost = r.get("salesAmt", 0) or 0
        labeled = dict(r)
        labeled["노출수"] = imp
        labeled["클릭수"] = clk
        labeled["광고비"] = cost
        labeled["CTR"] = r.get("ctr") if r.get("ctr") is not None else _pct(clk, imp)
        labeled["CPC"] = r.get("cpc") if r.get("cpc") is not None else _safe_div(cost, clk)
        if r.get("avgRnk") is not None:
            labeled["평균노출순위"] = r["avgRnk"]
        if r.get("ccnt") is not None:
            labeled["전환수"] = r["ccnt"]
        out.append(labeled)
    return out


# ─────────────────────────── 명령들 ───────────────────────────
def cmd_accounts(args):
    emit(api_get("/customer-links", {"type": "MYCLIENTS"}))


def cmd_campaigns(args):
    emit(api_get("/ncc/campaigns"))


def cmd_adgroups(args):
    params = {"nccCampaignId": args.campaign} if args.campaign else None
    emit(api_get("/ncc/adgroups", params))


def cmd_keywords(args):
    if not args.adgroup:
        die("--adgroup <nccAdgroupId> 필요", code=1)
    emit(api_get("/ncc/keywords", {"nccAdgroupId": args.adgroup}))


def cmd_stats(args):
    if not (args.ids and args.since and args.until):
        die("--ids <id,..> --since <YYYY-MM-DD> --until <YYYY-MM-DD> 모두 필요", code=1)
    params = {
        "ids": args.ids.split(","),
        "fields": json.dumps(FIELDS_STATS),
        "timeRange": json.dumps({"since": args.since, "until": args.until}),
    }
    if args.by == "day":
        params["breakdown"] = "day"
    emit(humanize_stats(api_get("/stats", params)))


def cmd_keywordtool(args):
    if not args.keywords:
        die("--keywords 제주여행,게스트하우스 형식 필요", code=1)
    res = api_get("/keywordstool", {"hintKeywords": args.keywords, "showDetail": 1})
    emit(res.get("keywordList", res))


def cmd_report(args):
    if not (args.type and args.date):
        die("--type <AD|...> --date <YYYY-MM-DD> 필요", code=1)
    job = api_post("/stat-reports", {"reportTp": args.type, "statDt": args.date})
    job_id = job.get("reportJobId")
    if not job_id:
        die(f"리포트 생성 응답에 reportJobId 없음: {job}", code=2)
    # 폴링 (BUILDING → BUILT)
    for _ in range(60):
        status = api_get(f"/stat-reports/{job_id}")
        st = status.get("status")
        if st == "BUILT":
            url = status.get("downloadUrl")
            _download(url, args.out)
            print(f"saved -> {args.out}")
            return
        if st in ("FAILED", "ERROR", "NONE"):
            die(f"리포트 생성 실패: {status}", code=2)
        time.sleep(2)
    die("리포트 생성 타임아웃(120s)", code=2)


def _download(url, out):
    if os.environ.get("NSA_MOCK"):
        with open(out, "w", encoding="utf-8") as f:
            f.write("date\timpCnt\tclkCnt\tsalesAmt\n2026-06-17\t100\t5\t1500\n")
        return
    with urllib.request.urlopen(url, timeout=60) as r, open(out, "wb") as f:
        f.write(r.read())


# ─────────────────────────── mock ───────────────────────────
def _mock_response(uri, params):
    """NSA_MOCK=1 용 가짜 응답. 키/네트워크 없이 로직 검증."""
    if uri == "/stats":
        # ctr 의도적으로 빼서 폴백 계산 경로를 검증
        return [{"id": "cmp-1", "impCnt": 1000, "clkCnt": 50, "salesAmt": 35000, "avgRnk": 2.3, "ccnt": 4}]
    if uri == "/ncc/campaigns":
        return [{"nccCampaignId": "cmp-1", "name": "테스트캠페인", "campaignTp": "WEB_SITE"}]
    if uri == "/customer-links":
        return [{"customerId": 1234567, "name": "내계정"}]
    if uri == "/keywordstool":
        return {"keywordList": [
            {"relKeyword": "제주여행", "monthlyPcQcCnt": 12000, "monthlyMobileQcCnt": 88000, "compIdx": "높음"}
        ]}
    return {"_mock": True, "uri": uri, "params": params}


# ─────────────────────────── selftest ───────────────────────────
def cmd_selftest(args):
    """키/네트워크 없이 순수 로직 검증."""
    # 1) 서명: 고정 입력 → 결정론적 base64
    ts, method, uri, secret = "1718700000000", "GET", "/stats", "fake_secret"
    s = sign(ts, method, uri, secret)
    expected = base64.b64encode(
        hmac.new(secret.encode(), f"{ts}.{method}.{uri}".encode(), hashlib.sha256).digest()
    ).decode()
    assert s == expected, "서명 불일치"
    # base64 형식(44자, '=' 패딩)
    assert len(s) == 44 and s.endswith("="), f"base64 형식 이상: {s}"

    # 2) CTR/CPC 폴백
    assert _pct(50, 1000) == 5.0, "CTR 폴백 오류"
    assert _pct(1, 0) == 0.0, "CTR 0분모 처리 오류"
    assert _safe_div(35000, 50) == 700.0, "CPC 폴백 오류"
    assert _safe_div(1, 0) == 0.0, "CPC 0분모 처리 오류"

    # 3) humanize: ctr 없는 행 → 폴백 채워짐, 원본 필드 유지
    h = humanize_stats([{"impCnt": 1000, "clkCnt": 50, "salesAmt": 35000}])[0]
    assert h["노출수"] == 1000 and h["클릭수"] == 50 and h["광고비"] == 35000
    assert h["CTR"] == 5.0 and h["CPC"] == 700.0
    assert h["impCnt"] == 1000, "원본 필드 유실"

    # 4) ms timestamp 자리수
    assert len(str(round(time.time() * 1000))) == 13, "timestamp ms 아님"

    print("selftest OK — 서명/폴백/humanize/timestamp 모두 통과")


# ─────────────────────────── argparse ───────────────────────────
def build_parser():
    p = argparse.ArgumentParser(
        prog="nsa", description="네이버 검색광고 성과 조회 (읽기 전용, 로컬 전용)"
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("accounts", help="광고계정 목록 (/customer-links)")
    sub.add_parser("campaigns", help="캠페인 목록 (/ncc/campaigns)")

    sp = sub.add_parser("adgroups", help="광고그룹 목록 (/ncc/adgroups)")
    sp.add_argument("--campaign", help="nccCampaignId로 필터")

    sp = sub.add_parser("keywords", help="키워드 목록 (/ncc/keywords)")
    sp.add_argument("--adgroup", required=False, help="nccAdgroupId (필수)")

    sp = sub.add_parser("stats", help="성과 조회: 노출/클릭/광고비/CTR/CPC (/stats)")
    sp.add_argument("--ids", help="캠페인/그룹/키워드 id, 콤마구분")
    sp.add_argument("--since", help="YYYY-MM-DD")
    sp.add_argument("--until", help="YYYY-MM-DD")
    sp.add_argument("--by", choices=["day"], help="일별 분해")

    sp = sub.add_parser("report", help="대용량 기간 리포트 (/stat-reports)")
    sp.add_argument("--type", help="reportTp (예: AD)")
    sp.add_argument("--date", help="statDt YYYY-MM-DD")
    sp.add_argument("--out", default="./report.tsv", help="저장 경로")

    sp = sub.add_parser("keywordtool", help="연관키워드·월 조회수 (/keywordstool)")
    sp.add_argument("--keywords", help="힌트 키워드, 콤마구분")

    sub.add_parser("_selftest", help="키 없이 내부 로직 검증")
    return p


DISPATCH = {
    "accounts": cmd_accounts,
    "campaigns": cmd_campaigns,
    "adgroups": cmd_adgroups,
    "keywords": cmd_keywords,
    "stats": cmd_stats,
    "report": cmd_report,
    "keywordtool": cmd_keywordtool,
    "_selftest": cmd_selftest,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    DISPATCH[args.command](args)


if __name__ == "__main__":
    main()
