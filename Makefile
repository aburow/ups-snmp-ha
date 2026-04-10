.PHONY: lint lint-fast lint-fix lint-bootstrap lint-security

lint-bootstrap:
	UV_CACHE_DIR=$(PWD)/.tools/uv-cache UV_PROJECT_ENVIRONMENT=$(PWD)/.tools/uv-lint uv sync --group lint

lint-fast: lint-bootstrap
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run --all-files

lint: lint-bootstrap
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run --all-files
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run yamllint --hook-stage manual --all-files
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run shellcheck --hook-stage manual --all-files
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run shfmt --hook-stage manual --all-files
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run sqlfluff-lint --hook-stage manual --all-files
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run semgrep --hook-stage manual --all-files

lint-fix: lint-bootstrap
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run ruff --all-files
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run ruff-format --all-files

lint-security: lint-bootstrap
	PATH="$(PWD)/.tools/uv-lint/bin:$$PATH" pre-commit run codeql --hook-stage manual --all-files
