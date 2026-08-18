# apps-dashboard

各アプリの無料ダウンロード数・Gumroad売上を集計し、Artifactダッシュボードを自動更新するためのリポジトリ。

- `apps.json`: 集計対象アプリの設定（新しいアプリはここに1件追加するだけでよい）
- `update_dashboard.py`: GitHub Releasesのダウンロード数とGumroadの売上を取得し、`dashboard.html`（Artifact公開用フラグメント）を生成する

`GUMROAD_ACCESS_TOKEN`環境変数が必要（GitHub側は`gh`コマンドの認証をそのまま使用）。

ダッシュボード: https://claude.ai/code/artifact/8b8632fc-2cdf-46d9-a8ce-992da251a421
（1時間おきのスケジュール実行で自動更新）
