# Optional Makefile for the Chrono-Geometric Framework.
#
# `make` is NOT installed on the Windows development box, so this file is not
# the verified entry point: `verify.ps1` is (same checks, PowerShell). The
# targets here are kept in sync with it for POSIX CI runners.
#
#   make build   -> lake build
#   make test    -> enclosure consistency suite
#   make verify  -> build + test + placeholder scan

.PHONY: build test verify

build:
	lake build

test:
	python -m pytest python/test_enclosure_consistency.py -q

verify: build test
	@if grep -nE '\b(sorry|admit|unsafe)\b' lean/*.lean; then \
		echo "forbidden placeholder token in lean/*.lean"; exit 1; \
	else \
		echo "verify: PASS"; \
	fi
