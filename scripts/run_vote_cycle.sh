#!/usr/bin/env bash
# 総選挙2026の収集〜集計〜投稿を、モードごとに決まった順序で実行する。
#
# 判断の要らない機械的な手順なので、対話エージェントを介さず
# GitHub Actions からこのスクリプトを呼ぶだけで完結させる。
#
#   run_vote_cycle.sh top          上位40名を収集する（毎時）
#   run_vote_cycle.sh full         全190名を収集し、速報を集計する（4時間おき）
#   run_vote_cycle.sh daily        全190名を収集し、前日サマリを集計する（0時）
#   run_vote_cycle.sh full --post  集計済みの結果をDiscordへ投稿する
#
# **投稿は収集・集計とは別の呼び出しにしてある。** 呼び出し元は収集結果を
# コミットしてから投稿すること。投稿はやり直せるが、取りこぼした投稿は
# 39件の返却上限のため二度と回収できない。実際、投稿を同じ呼び出しに
# 含めていた際、ウェブフックURLの不正で投稿が落ち、その回に11分かけて
# 集めた190名ぶんの収集がコミットされずに失われた。
#
# DISCORD_WEBHOOK_URL が未設定のときは投稿を飛ばす（収集は続ける）。
#
# 詳細は docs/vote2026-tracking.md を参照。
set -euo pipefail

mode="${1:-}"
action="${2:-collect}"
cd "$(dirname "$0")/.."

# 収集は190名中の一部が失敗しても続行する（終了コード2＝部分失敗）。
# 1件の一時的な失敗で集計まで落とすと、取り返せる情報まで落ちる。
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
  python3 "$1"
}

case "$mode:$action" in
  top:collect)   collect --top 40 ;;
  full:collect)  collect; python3 scripts/rank_vote_share.py ;;
  daily:collect) collect; python3 scripts/daily_report_vote_share.py ;;
  full:--post)   post scripts/post_vote_share_to_discord.py ;;
  daily:--post)  post scripts/post_daily_report_to_discord.py ;;
  top:--post)    echo "上位40名の収集では投稿しません。" >&2 ;;
  *)
    echo "使い方: $0 top|full|daily [--post]" >&2
    exit 64
    ;;
esac
