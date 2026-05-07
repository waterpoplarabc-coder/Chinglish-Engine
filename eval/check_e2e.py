import json
import os
import sys
import urllib.error
import urllib.request


def http_get(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return int(resp.status), resp.read().decode("utf-8", errors="replace")


def http_post_json(url: str, payload: dict) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        method="POST",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return int(resp.status), resp.read().decode("utf-8", errors="replace")


def main() -> int:
    base = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    try:
        code, html = http_get(f"{base}/")
    except urllib.error.URLError as e:
        print(f"FAIL /: {e}")
        return 1
    if code != 200:
        print(f"FAIL / status={code}")
        return 1
    if 'id="root"' not in html and "中式多语种引擎" not in html:
        print("FAIL / content not looks like UI or landing page")
        return 1
    print("PASS /")

    code, body = http_get(f"{base}/api/health")
    if code != 200:
        print(f"FAIL /api/health status={code}")
        return 1
    try:
        health = json.loads(body)
    except json.JSONDecodeError:
        print("FAIL /api/health not json")
        return 1
    if health.get("ok") is not True:
        print("FAIL /api/health payload")
        return 1
    print("PASS /api/health")

    code, body = http_post_json(
        f"{base}/api/rewrite",
        {
            "text": "Please turn on the light.",
            "lang": "en",
            "level": 5,
            "domain": "default",
            "seed": 2,
            "explain": True,
        },
    )
    if code != 200:
        print(f"FAIL /api/rewrite status={code}")
        return 1
    try:
        out = json.loads(body)
    except json.JSONDecodeError:
        print("FAIL /api/rewrite not json")
        return 1
    if not isinstance(out.get("output"), str) or not out.get("output"):
        print("FAIL /api/rewrite output missing")
        return 1
    print("PASS /api/rewrite")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

