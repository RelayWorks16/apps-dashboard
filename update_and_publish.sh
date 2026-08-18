#!/bin/bash
# 1時間おきに実行され、apps.json記載の各アプリのダウンロード数/売上を取得して
# index.htmlを再生成し、GitHub Pagesへpushして公開するスクリプト。
# launchd(com.kazuya.apps-dashboard.update)から呼ばれる想定。auto_research.shと同じパターン。

export PATH="/opt/homebrew/bin:/Users/kazuya/.nvm/versions/node/v24.19.0/bin:/usr/bin:/bin:/usr/sbin:/sbin"

PROJECT_DIR="/Users/kazuya/AI/apps-dashboard"
cd "$PROJECT_DIR"

set -a
source "$PROJECT_DIR/.secrets/gumroad_token.env"
set +a

echo "===== $(date) 開始 =====" >> "$PROJECT_DIR/update.log"

python3 "$PROJECT_DIR/update_dashboard.py" >> "$PROJECT_DIR/update.log" 2>&1
if [ $? -ne 0 ]; then
  echo "update_dashboard.py が失敗したため、公開をスキップします" >> "$PROJECT_DIR/update.log"
  echo "===== $(date) 終了（失敗） =====" >> "$PROJECT_DIR/update.log"
  exit 1
fi

git add index.html >> "$PROJECT_DIR/update.log" 2>&1
if git diff --cached --quiet; then
  echo "変更なし（差分ゼロのためコミットをスキップ）" >> "$PROJECT_DIR/update.log"
else
  git commit -m "chore: ダッシュボード自動更新 $(date '+%Y-%m-%d %H:%M')" >> "$PROJECT_DIR/update.log" 2>&1
  git push origin main >> "$PROJECT_DIR/update.log" 2>&1
fi

echo "===== $(date) 終了 =====" >> "$PROJECT_DIR/update.log"
