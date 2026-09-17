#!/usr/bin/env bash
# 把十份頁面的瀏覽次數歸零（需先執行 npx wrangler login）
# 用法：bash tools/counter/reset.sh <KV_NAMESPACE_ID> [頁面代號...]
#   不指定頁面代號時，十份全部歸零
set -euo pipefail
NS="${1:?請提供 KV namespace id}"; shift || true
PAGES=("$@")
if [ ${#PAGES[@]} -eq 0 ]; then
  PAGES=(af af-intro af-meds bp brady gout hf oh pacemaker svt)
fi
for p in "${PAGES[@]}"; do
  npx wrangler kv key put --namespace-id="$NS" "views:$p" "0" --remote
  echo "已歸零 views:$p"
done
