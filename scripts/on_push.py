"""每次有提交推到 main 时由 GitHub Actions 运行：
1. 把这次新增的 notify/*.json 里的消息推到 Bark 和 ntfy（BB 机）；
2. 更新 data/prices.json（标普 500、纳指 100、QQQM 最新收盘）。
本地试跑：DRY=1 python3 scripts/on_push.py <上一次提交号>
"""
import datetime
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

PAGE = "https://jackdhch.github.io/market-calls-tracker/"


def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def new_notify_files(before):
    if not before or set(before) == {"0"}:  # 新建分支时没有上一次提交
        return []
    out = subprocess.run(["git", "diff", "--diff-filter=A", "--name-only", before, "HEAD", "--", "notify/"],
                         capture_output=True, text=True, check=True).stdout
    return [f for f in out.split() if f.endswith(".json")]


def push(title, body):
    title, body = title[:14], body[:50]  # 手机和 BB 机一屏能显示完
    if os.environ.get("DRY"):
        print("[DRY]", title, "|", body)
        return []
    errs, q = [], lambda s: urllib.parse.quote(s, safe="")
    if key := os.environ.get("BARK_KEY"):
        try:
            r = json.loads(get(f"https://api.day.app/{key}/{q(title)}/{q(body)}?url={q(PAGE)}&group={q('市场观点')}"))
            assert r.get("code") == 200, r
        except Exception as e:
            errs.append(f"Bark：{e}")
    if topic := os.environ.get("NTFY_TOPIC"):
        try:
            get("https://ntfy.sh/", json.dumps({"topic": topic, "title": title, "message": body, "click": PAGE}).encode(),
                {"Content-Type": "application/json"})
        except Exception as e:
            errs.append(f"ntfy：{e}")
    return errs


def prices():
    out = {}
    for sym in ["^GSPC", "^NDX", "QQQM"]:
        r = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=5d&interval=1d"))
        r = r["chart"]["result"][0]
        closes = [(t, c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c]
        t, c = closes[-1]
        out[sym] = {"close": round(c, 2), "date": datetime.datetime.fromtimestamp(t, datetime.timezone(datetime.timedelta(hours=-4))).date().isoformat()}
    out["fetched_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")
    return out


def main():
    errors = []
    for f in new_notify_files(sys.argv[1] if len(sys.argv) > 1 else ""):
        for m in json.load(open(f)):
            errors += [f"{f}「{m['title']}」{e}" for e in push(m["title"], m["body"])]
    try:
        json.dump(prices(), open("data/prices.json", "w"), ensure_ascii=False, indent=1)
    except Exception as e:
        errors.append(f"取价失败：{e}")
    if errors:  # 让 Actions 显示失败，GitHub 会发邮件
        raise SystemExit("\n".join(errors))


if __name__ == "__main__":
    main()
