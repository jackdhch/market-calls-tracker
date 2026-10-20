# 华尔街点位追踪

记录 Tom Lee（Fundstrat）和华尔街各大行给标普 500 / 纳指 100 定的点位目标，按标普目标换算 QQQM 价格。

- 网页：https://jackdhch.github.io/market-calls-tracker/
- 每天由 Claude Code 云端定时任务按 [AGENT.md](AGENT.md) 联网检查一次，更新 `data/calls.json`；有新言论写 `notify/`。
- 每次推送到 main，GitHub Actions 运行 `scripts/on_push.py`：把新增的 `notify/*.json` 推到手机，并更新 `data/prices.json`。

内容只摘录公开报道，附来源链接，不构成投资建议。
