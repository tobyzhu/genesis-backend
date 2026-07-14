#!/usr/bin/env bash
# 定时同步 VIP 生命周期：休眠客写 vip.status，活跃客恢复。
# 用法见 scripts/vip-lifecycle.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$REPO_ROOT/genesis_backend"
PYTHON="${GENESIS_PYTHON:-$BACKEND_DIR/.venv/bin/python}"
LOG_DIR="${GENESIS_LOG_DIR:-$BACKEND_DIR/logs}"
LOCK_DIR="${VIP_LIFECYCLE_LOCK_DIR:-/tmp/genesis-sync-vip-lifecycle.lock}"
DRY_RUN="${VIP_LIFECYCLE_DRY_RUN:-0}"

if [[ ! -x "$PYTHON" ]]; then
  echo "Python 不存在: $PYTHON" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sync-vip-lifecycle-$(date +%Y%m%d).log"
_now() { date '+%Y-%m-%dT%H:%M:%S%z'; }
_trim() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "$(_now) skip: another sync is running" >> "$LOG_FILE"
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

{
  echo "===== $(_now) sync_vip_lifecycle start ====="
  cd "$BACKEND_DIR"

  COMPANIES="${VIP_LIFECYCLE_COMPANIES:-${1:-}}"
  if [[ -z "$COMPANIES" ]]; then
    echo "ERROR: 请设置 VIP_LIFECYCLE_COMPANIES 或传入公司编码参数，如: $0 yiren"
    exit 1
  fi

  DRY_FLAG=()
  if [[ "$DRY_RUN" == "1" || "$DRY_RUN" == "true" ]]; then
    DRY_FLAG=(--dry-run)
  fi

  CRM_FLAG=()
  if [[ "$DRY_RUN" != "1" && "$DRY_RUN" != "true" && "${VIP_LIFECYCLE_CRM_TASKS:-0}" == "1" ]]; then
    CRM_FLAG=(--crm-tasks)
    if [[ -n "${VIP_LIFECYCLE_CRM_SEGMENTS:-}" ]]; then
      CRM_FLAG+=(--crm-segments="${VIP_LIFECYCLE_CRM_SEGMENTS}")
    fi
    if [[ -n "${VIP_LIFECYCLE_CRM_LIMIT:-}" ]]; then
      CRM_FLAG+=(--crm-limit="${VIP_LIFECYCLE_CRM_LIMIT}")
    fi
  fi

  IFS=',' read -ra COMPANY_LIST <<< "$COMPANIES"
  for company in "${COMPANY_LIST[@]}"; do
    company="$(_trim "$company")"
    [[ -z "$company" ]] && continue
    echo "--- company=$company ---"
    SNAPSHOT_FLAG=()
    if [[ "$DRY_RUN" != "1" && "$DRY_RUN" != "true" && "${VIP_LIFECYCLE_SNAPSHOT:-1}" == "1" ]]; then
      SNAPSHOT_FLAG=(--snapshot)
    fi
    "$PYTHON" manage.py sync_vip_lifecycle --company="$company" "${DRY_FLAG[@]}" "${SNAPSHOT_FLAG[@]}" "${CRM_FLAG[@]}"
  done

  echo "===== $(_now) sync_vip_lifecycle done ====="
} >> "$LOG_FILE" 2>&1
