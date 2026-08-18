# apps-dashboard

各アプリの無料ダウンロード数・Gumroad売上を集計し、GitHub Pagesのダッシュボードを自動更新するためのリポジトリ。

- `apps.json`: 集計対象アプリの設定（新しいアプリはここに1件追加するだけでよい）
- `update_dashboard.py`: GitHub Releasesのダウンロード数とGumroadの売上を取得し、`index.html`を生成する
- `update_and_publish.sh`: `update_dashboard.py`を実行し、変更があれば`index.html`をコミット・pushする（launchdから呼ばれる想定）
- `com.kazuya.apps-dashboard.update.plist`: 毎時0分に`update_and_publish.sh`を実行するlaunchdの設定（`~/Library/LaunchAgents/`に配置して`launchctl load`する）
- `.secrets/gumroad_token.env`: `GUMROAD_ACCESS_TOKEN`を保持するローカル専用ファイル（gitignore済み、リポジトリには含まれない）

`GUMROAD_ACCESS_TOKEN`環境変数が必要（GitHub側は`gh`コマンドの認証をそのまま使用）。

ダッシュボード: https://relayworks16.github.io/apps-dashboard/
（1時間おきのスケジュール実行で自動更新）
