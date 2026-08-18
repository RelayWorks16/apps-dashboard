#!/usr/bin/env python3
"""
apps.json に列挙された各アプリについて、GitHub Releasesのダウンロード数と
Gumroadの売上を取得し、index.html（GitHub Pagesでそのまま公開する完全なHTML文書）を生成する。

使い方: GUMROAD_ACCESS_TOKEN=xxx python3 update_dashboard.py
（GitHub側は `gh` コマンドの認証をそのまま使う）

新しいアプリを追加する場合は apps.json に1件追加するだけでよい。
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_github_downloads(owner: str, repo: str) -> int:
    """全リリースの、.dmgアセットのdownload_countを合計する（Source code zip/tar.gzは除外）。"""
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/releases", "--paginate"],
        capture_output=True, text=True, check=True,
    )
    releases = json.loads(result.stdout)
    total = 0
    for release in releases:
        for asset in release.get("assets", []):
            if asset["name"].endswith(".dmg"):
                total += asset["download_count"]
    return total


def fetch_gumroad_stats(product_id: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.gumroad.com/v2/products",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    for product in data.get("products", []):
        if product["id"] == product_id:
            return {
                "sales_count": product.get("sales_count", 0),
                "revenue_usd": product.get("sales_usd_cents", 0) / 100,
            }
    return {"sales_count": 0, "revenue_usd": 0}


def main():
    token = os.environ.get("GUMROAD_ACCESS_TOKEN")
    if not token:
        print("ERROR: GUMROAD_ACCESS_TOKEN環境変数が設定されていません", file=sys.stderr)
        sys.exit(1)

    with open(os.path.join(SCRIPT_DIR, "apps.json"), encoding="utf-8") as f:
        apps = json.load(f)

    rows = []
    for app in apps:
        try:
            downloads = fetch_github_downloads(app["github_owner"], app["github_repo"])
        except Exception as e:
            print(f"WARN: {app['name']}のGitHubデータ取得に失敗: {e}", file=sys.stderr)
            downloads = None
        try:
            gumroad = fetch_gumroad_stats(app["gumroad_product_id"], token)
        except Exception as e:
            print(f"WARN: {app['name']}のGumroadデータ取得に失敗: {e}", file=sys.stderr)
            gumroad = {"sales_count": 0, "revenue_usd": 0}
        rows.append({
            "name": app["name"],
            "gumroad_product_url": app.get("gumroad_product_url", "#"),
            "downloads": downloads,
            "sales_count": gumroad["sales_count"],
            "revenue_usd": gumroad["revenue_usd"],
        })

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = render_html(rows, updated_at)

    out_path = os.path.join(SCRIPT_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"書き出しました: {out_path}")


def render_html(rows: list, updated_at: str) -> str:
    def fmt(n):
        return f"{n:,}" if n is not None else "—"

    cards = []
    for r in rows:
        conversion = (
            f"{r['sales_count'] / r['downloads'] * 100:.1f}%"
            if r["downloads"] else "—"
        )
        cards.append(f"""
        <div class="app-card">
          <div class="app-name">
            <h2>{r['name']}</h2>
            <a href="{r['gumroad_product_url']}" target="_blank" rel="noopener">Gumroadで見る →</a>
          </div>
          <div class="stat-row">
            <div class="stat">
              <div class="stat-label">無料ダウンロード数</div>
              <div class="stat-value">{fmt(r['downloads'])}</div>
            </div>
            <div class="stat">
              <div class="stat-label">購入数</div>
              <div class="stat-value accent">{fmt(r['sales_count'])}</div>
            </div>
            <div class="stat">
              <div class="stat-label">売上（USD）</div>
              <div class="stat-value">${r['revenue_usd']:,.2f}</div>
            </div>
            <div class="stat">
              <div class="stat-label">無料→有料転換率</div>
              <div class="stat-value">{conversion}</div>
            </div>
          </div>
        </div>""")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>アプリ実績ダッシュボード</title>
<meta name="robots" content="noindex">
<style>
  :root {{
    color-scheme: light dark;
    --bg: #f7f6f2;
    --surface: #ffffff;
    --surface-sunken: #f0efe9;
    --text: #1a1d1a;
    --text-muted: #6b6f68;
    --border: #e4e2db;
    --accent: #0e8f5c;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #14181a;
      --surface: #1c2023;
      --surface-sunken: #23282b;
      --text: #eef1ee;
      --text-muted: #8b9089;
      --border: #2a2f2c;
      --accent: #6fd39d;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #14181a;
    --surface: #1c2023;
    --surface-sunken: #23282b;
    --text: #eef1ee;
    --text-muted: #8b9089;
    --border: #2a2f2c;
    --accent: #6fd39d;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Hiragino Kaku Gothic ProN", sans-serif;
    margin: 0;
  }}
  .wrap {{ max-width: 760px; margin: 0 auto; padding: 40px 24px 60px; }}
  .page-head {{ display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 8px 20px; margin-bottom: 28px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }}
  h1 {{ font-size: 1.3rem; font-weight: 700; margin: 0; letter-spacing: -0.01em; }}
  .updated {{ color: var(--text-muted); font-size: 0.78rem; font-variant-numeric: tabular-nums; }}
  .app-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 22px 24px; margin-bottom: 14px; }}
  .app-name {{ display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }}
  .app-name h2 {{ font-size: 1.05rem; font-weight: 700; margin: 0; }}
  .app-name a {{ font-size: 0.78rem; color: var(--text-muted); text-decoration: none; }}
  .app-name a:hover {{ color: var(--accent); }}
  .stat-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 18px; }}
  .stat {{ background: var(--surface-sunken); border-radius: 10px; padding: 12px 14px; }}
  .stat-label {{ font-size: 0.7rem; color: var(--text-muted); letter-spacing: 0.02em; margin-bottom: 6px; }}
  .stat-value {{
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    font-variant-numeric: tabular-nums;
    font-size: 1.5rem;
    font-weight: 600;
  }}
  .stat-value.accent {{ color: var(--accent); }}
</style>
</head>
<body>
<div class="wrap">
  <div class="page-head">
    <h1>アプリ実績ダッシュボード</h1>
    <div class="updated">最終更新: {updated_at}（1時間おきに自動更新）</div>
  </div>
  {"".join(cards)}
</div>
</body>
</html>
"""


if __name__ == "__main__":
    main()
