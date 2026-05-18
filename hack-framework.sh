#!/usr/bin/env bash
###############################################################################
# hack-framework.sh - Unified CLI for hack-android-framework
# Educational & research tooling for Android Open Source Project (AOSP)
# Usage: ./hack-framework.sh <command> [options]
###############################################################################
set -euo pipefail

# --- Colors & Logging ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'
IS_TTY=0; [[ -t 1 ]] && IS_TTY=1

log_info()  { [[ $IS_TTY -eq 1 ]] && echo -e "${CYAN}ℹ️ ${BOLD}[INFO]${RESET} $*" || echo "[INFO] $*"; }
log_warn()  { [[ $IS_TTY -eq 1 ]] && echo -e "${YELLOW}⚠️ [WARN] $*" || echo "[WARN] $*"; }
log_err()   { [[ $IS_TTY -eq 1 ]] && echo -e "${RED}❌ [ERROR] $*" >&2 || echo "[ERROR] $*" >&2; }
log_success() { [[ $IS_TTY -eq 1 ]] && echo -e "${GREEN}✅ [OK] $*" || echo "[OK] $*"; }

# --- Paths & Dependencies ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="${SCRIPT_DIR}/tools"
PYTHON_CMD="python3"

if ! command -v "$PYTHON_CMD" &>/dev/null; then
  log_err "python3 is required but not found. Install it and retry."
  exit 1
fi

# --- Helper: Run Python Tool Safely ---
run_tool() {
  local script="$1"; shift
  local tool_path="${TOOLS_DIR}/${script}"
  
  if [[ ! -f "$tool_path" ]]; then
    log_err "Tool not found: $tool_path"
    log_info "Run './hack-framework.sh setup' to ensure all tools are executable."
    exit 1
  fi
  
  "$PYTHON_CMD" "$tool_path" "$@"
}

# --- Usage ---
usage() {
  cat <<EOF
${BOLD}hack-android-framework CLI${RESET}
${CYAN}Usage:${RESET} $(basename "$0") <command> [options]

${BOLD}Commands:${RESET}
  setup            Ensure tools are executable & verify environment
  env-check        Validate AOSP build prerequisites  logcat           Stream & filter framework logs (requires adb)
  patch-apply      Safely apply/untest framework patches
  binder-analyze   Parse binder IPC transaction logs
  soong-inspect    Static analysis of Android.bp dependencies
  api-diff         Compare AOSP API dump files
  help             Show this help message

${BOLD}Examples:${RESET}
  $(basename "$0") setup
  $(basename "$0") env-check
  $(basename "$0") logcat --services ActivityManager WindowManager
  $(basename "$0") patch-apply my_fix.diff --dry-run --root /path/to/aosp
  $(basename "$0") binder-analyze binder.log
  $(basename "$0") soong-inspect frameworks/base
  $(basename "$0") api-diff api/old.txt api/new.txt

${CYAN}Note:${RESET} All tools are educational & safe by default. Review outputs before flashing.
EOF
}

# --- Command Implementations ---
cmd_setup() {
  log_info "Setting up framework tools..."
  chmod +x "${TOOLS_DIR}"/*.py 2>/dev/null || true
  log_success "Tools marked as executable. Run './hack-framework.sh env-check' next."
}

cmd_env_check() {
  run_tool "aosp_framework_helper.py" env-check "$@"
}

cmd_logcat() {
  run_tool "aosp_framework_helper.py" logcat-stream "$@"
}

cmd_patch_apply() {
  run_tool "aosp_framework_helper.py" patch-apply "$@"
}

cmd_binder_analyze() {
  [[ $# -eq 0 ]] && { log_err "Usage: $(basename "$0") binder-analyze <log_file> [--json]"; exit 1; }
  run_tool "binder_trace_parser.py" "$@"
}

cmd_soong_inspect() {
  [[ $# -eq 0 ]] && { log_err "Usage: $(basename "$0") soong-inspect <Android.bp or directory>"; exit 1; }
  run_tool "soong_build_inspector.py" "$@"
}

cmd_api_diff() {  [[ $# -lt 2 ]] && { log_err "Usage: $(basename "$0") api-diff <old_api.txt> <new_api.txt>"; exit 1; }
  run_tool "framework_api_diff.py" "$@"
}

# --- Main Dispatcher ---
case "${1:-help}" in
  setup)        cmd_setup "$@" ;;
  env-check)    cmd_env_check "$@" ;;
  logcat)       cmd_logcat "$@" ;;
  patch-apply)  cmd_patch_apply "$@" ;;
  binder-analyze) cmd_binder_analyze "${@:2}" ;;
  soong-inspect) cmd_soong_inspect "${@:2}" ;;
  api-diff)     cmd_api_diff "${@:2}" ;;
  help|-h|--help) usage ;;
  *)
    log_err "Unknown command: $1"
    usage
    exit 1
    ;;
esac