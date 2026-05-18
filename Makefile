.PHONY: help setup env-check logcat patch-apply binder-analyze soong-inspect api-diff clean
.DEFAULT_GOAL := help

# Configuration
SCRIPT   := ./hack-framework.sh
AOSP_ROOT ?= $(PWD)
SERVICES ?= ActivityManager WindowManager SystemServer
LOG_BUFFER ?= main
PATCH_FILE ?=
PATCH_DRY_RUN ?= --dry-run
BINDER_LOG ?= binder.log
SOONG_DIR ?= .
OLD_API ?= api/old.txt
NEW_API ?= api/new.txt

help: ## 📖 Show available targets
	@echo "🛠 hack-android-framework Makefile"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## 🔧 Initialize tools & set permissions
	@$(SCRIPT) setup

env-check: ## 🔍 Validate AOSP build environment
	@$(SCRIPT) env-check

logcat: ## 📡 Stream framework logs (override: make logcat SERVICES="ActivityManager")
	@$(SCRIPT) logcat --services $(SERVICES) --buffer $(LOG_BUFFER)

patch-apply: ## 📦 Apply framework patch (set: make patch-apply PATCH_FILE=my.diff)
	@test -n "$(PATCH_FILE)" || (echo "❌ Error: Set PATCH_FILE=your.patch"; exit 1)
	@$(SCRIPT) patch-apply $(PATCH_FILE) --root $(AOSP_ROOT) $(PATCH_DRY_RUN)

binder-analyze: ## 🕸️ Analyze Binder IPC logs (set: make binder-analyze BINDER_LOG=dump.log)
	@test -f "$(BINDER_LOG)" || (echo "❌ Error: BINDER_LOG not found"; exit 1)
	@$(SCRIPT) binder-analyze $(BINDER_LOG)

soong-inspect: ## 🏗️ Inspect Soong build topology (set: make soong-inspect SOONG_DIR=frameworks/base)
	@$(SCRIPT) soong-inspect $(SOONG_DIR)

api-diff: ## 📊 Compare API dumps (set: make api-diff OLD_API=old.txt NEW_API=new.txt)
	@$(SCRIPT) api-diff $(OLD_API) $(NEW_API)

clean: ## 🧹 Remove temporary logs, JSON dumps & test artifacts
	@rm -f *.log *.json test_*.txt 2>/dev/null || true
	@echo "✅ Cleaned temporary files."