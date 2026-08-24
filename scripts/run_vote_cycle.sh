#!/usr/bin/env bash
# 総選挙2026 の収集〜集計〜投稿を、モードごとに決まった順序で実行する。
#
# 判断の要らない機械的な手順なので、対話エージェントを介さず
# GitHub Actions からこのスクリプトを1本呼ぶだけで完結させる。
#
#   top    上位40名だけを収集する（毎時）
#   full   全190名を収集し、速報を集計してDiscordに投稿する（4時間おき）
#   daily  全190名を収集し、前日サマリを集計してDiscordに投稿する（0時）
#
# DISCORD_WEBHOOK_URL が未設定のときは投稿だけを飛ばす。
# 投稿はやり直せるが、収集の取りこぼしは39件上限のため二度と回収できないため。
#
# 詳細は docs/vote2026-tracking.md を参照。
set -euo pipefail

mode="${1:-}"
cd "$(dirname "$0")/.."

# 収集は190名中の一部が失敗しても続行する（終了コード2＝部分失敗）。
# 1件の一時的な失敗で集計と投稿まで落とすと、取り返せる情報まで落ちる。
collect() {
  local status=0
  python3 scripts/collect_vote_share.py "$@" || status=$?
  case "$status" in
    0) ;;
    2) echo "注意: 一部のアイドルの取得に失敗しましたが、収集を続行します。" >&2 ;;
    *) echo "収集が異常終了しました (exit $status)。" >&2; return "$status" ;;
  esac
}

post() {
  if [ -z "${DISCORD_WEBHOOK_URL:-}" ]; then
    echo "DISCORD_WEBHOOK_URL が未設定のため、Discordへの投稿は行いません。" >&2
    return 0
  fi
  python3 "$@"
}

case "$mode" in
  top)
    collect --top 40
    ;;
  full)
    collect
    python3 scripts/rank_vote_share.py
    post scripts/post_vote_share_to_discord.py
    ;;
  daily)
    collect
    python3 scripts/daily_report_vote_share.py
    post scripts/post_daily_report_to_discord.py
    ;;
  *)
    echo "使い方: $0 top|full|daily" >&2
    exit 64
    ;;
esac
