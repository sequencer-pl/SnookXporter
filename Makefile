MAX_LINE_LENGTH = 119
MIN_TESTS_COVERAGE = 100

.PHONY: install
install:
	uv sync

.PHONY: install-dev
install-dev:
	uv sync --group=dev

.PHONY: type-check
type-check:
	uv run mypy snookxporter tests

.PHONY: unit-tests
unit-tests:
	uv run pytest --cov=snookxporter --cov-fail-under=$(MIN_TESTS_COVERAGE) --cov-report term-missing tests

.PHONY: lint
lint:
	uv --max-line-length $(MAX_LINE_LENGTH) snookxporter tests

.PHONY: isort-check
isort-check:
	uv run isort -l $(MAX_LINE_LENGTH) --check snookxporter tests

.PHONY: tests
tests: isort-check type-check unit-tests

.PHONY: isort
isort:
	uv run isort -l $(MAX_LINE_LENGTH) snookxporter tests

.PHONY: run
run:
	uv run snookxporter
