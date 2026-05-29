# Zetix — root orchestration surface.
#
# Make is the COARSE cross-ecosystem graph and the one command surface.
# It tracks module-level and cross-module relationships only ("server up",
# "model converted") — NOT individual source files. Gradle, Xcode/SPM, and the
# Python toolchain are the fine-grained, incremental, cached builders inside their
# own worlds. The root delegates each standard verb to a thin per-module Makefile
# that wraps that module's native tool (recursive Make).
# See docs/adr/0001-mono-repo-orchestration-make.md
#
# Convention:
#   - Delegating targets are .PHONY: we trust native tools to decide what is stale.
#   - Cross-language edges use stamp files in .make/ (Bazel-shaped-gap fillers).
#   - Order-only prereqs (after a `|`) express "must be running/done first".

SHELL := /bin/bash
.DEFAULT_GOAL := help

# --- Artifacts / stamp directory (git-ignored) -------------------------------
MAKE_DIR := .make
STAMP_MODEL     := $(MAKE_DIR)/model-converted.stamp
STAMP_CONTRACTS := $(MAKE_DIR)/contracts.stamp

$(MAKE_DIR):
	@mkdir -p $(MAKE_DIR)

# --- Recursive delegate to a module's own Makefile ---------------------------
# Until a module's Makefile exists (EPIC-0.2) the call is a no-op that says so,
# so the root surface works on a partially-scaffolded tree.
# Usage: $(call mk,<dir>,<targets>)
define mk
	@if [ -f "$(1)/Makefile" ]; then \
		$(MAKE) --no-print-directory -C "$(1)" $(2); \
	else \
		echo "-- skip: $(1) has no Makefile yet (EPIC-0.2)"; \
	fi
endef

# =============================================================================
# Aggregate targets — the everyday surface
# =============================================================================
.PHONY: build test lint fmt clean help bootstrap

build: contracts server-build android-build ios-build sdk-build models  ## Build every surface
test: server-test android-test ios-test sdk-test eval                    ## Run all test suites
lint: server-lint android-lint ios-lint                                  ## Lint every surface
fmt: server-fmt android-fmt ios-fmt                                       ## Auto-format every surface

bootstrap: | $(MAKE_DIR)  ## One-time local dev setup across surfaces
	$(call mk,server,bootstrap)
	$(call mk,apps/android,bootstrap)
	$(call mk,apps/ios,bootstrap)

clean:  ## Reset cross-tool stamps and delegate clean to each surface
	@rm -rf $(MAKE_DIR)
	$(call mk,server,clean)
	$(call mk,apps/android,clean)
	$(call mk,apps/ios,clean)
	$(call mk,packages/contracts,clean)
	$(call mk,models,clean)

# =============================================================================
# Shared spine — contracts & models (the cross-language dependencies)
# =============================================================================
.PHONY: contracts models
contracts: $(STAMP_CONTRACTS)  ## Generate shared API/sync/vector contracts
$(STAMP_CONTRACTS): | $(MAKE_DIR)
	$(call mk,packages/contracts,gen)
	@touch $@

models: $(STAMP_MODEL)  ## Convert + quantise embedding model (TFLite/CoreML/ONNX)
$(STAMP_MODEL): | $(MAKE_DIR)
	$(call mk,models,convert quantise)
	@touch $@

# =============================================================================
# Server (Python / FastAPI) — Phase 1
# =============================================================================
.PHONY: server server-build server-test server-lint server-fmt server-up server-down
server: server-build
server-build: ; $(call mk,server,build)
server-test:  ; $(call mk,server,test)
server-lint:  ; $(call mk,server,lint)
server-fmt:   ; $(call mk,server,fmt)
server-up:    ## Start the server (background) — used as an order-only prereq
	$(call mk,server,up)
server-down:  ; $(call mk,server,down)

# =============================================================================
# Android (Kotlin / Gradle) — Phases 2–3.  Gradle owns file-level incrementality.
# Android inference needs the converted model + shared contracts: declare both.
# =============================================================================
.PHONY: android android-build android-test android-lint android-fmt
android: android-build
android-build: $(STAMP_MODEL) contracts ; $(call mk,apps/android,build)
android-test:                           ; $(call mk,apps/android,test)
android-lint:                           ; $(call mk,apps/android,lint)
android-fmt:                            ; $(call mk,apps/android,fmt)

# =============================================================================
# iOS (Swift / SPM + Xcode) — Phase 4.  Xcode owns file-level incrementality.
# =============================================================================
.PHONY: ios ios-build ios-test ios-lint ios-fmt ios-integration-test
ios: ios-build
ios-build: $(STAMP_MODEL) contracts ; $(call mk,apps/ios,build)
ios-test:                           ; $(call mk,apps/ios,test)
ios-lint:                           ; $(call mk,apps/ios,lint)
ios-fmt:                            ; $(call mk,apps/ios,fmt)

# The canonical cross-ecosystem edge: the iOS integration test needs the model
# converted (file prereq) AND the server running (order-only prereq).
ios-integration-test: $(STAMP_MODEL) | server-up  ## iOS integ test (needs server up + model converted)
	$(call mk,apps/ios,integration-test)

# =============================================================================
# SDKs (packages/) — Phase 5
# =============================================================================
.PHONY: sdk-build sdk-test
sdk-build: contracts          ## Build Android AAR + iOS Swift Package
	$(call mk,packages/sdk-android,build)
	$(call mk,packages/sdk-ios,build)
sdk-test:
	$(call mk,packages/sdk-android,test)
	$(call mk,packages/sdk-ios,test)

# =============================================================================
# Eval harness (Python) — gates Milestone M1 (Top-3 accuracy > 80%)
# =============================================================================
.PHONY: eval
eval: $(STAMP_MODEL)  ## Run search-quality evaluation (Top-3 accuracy)
	$(call mk,models,eval)

# =============================================================================
help:  ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' \
		| sort
