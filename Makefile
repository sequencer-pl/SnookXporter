MAX_LINE_LENGTH = 120

.PHONY: install
install:
	poetry install --only main

.PHONY: install-dev
install-dev:
	poetry install

.PHONY: type-check
type-check:
	poetry run mypy snookxporter tests

.PHONY: unit-tests
unit-tests:
	poetry run pytest --cov --cov-fail-under=100 tests

.PHONY: lint
lint:
	pylint --max-line-length $(MAX_LINE_LENGTH) snookxporter tests

.PHONY: tests
tests: type-check unit-tests

.PHONY: isort-fix
isort-fix:
	isort -l $(MAX_LINE_LENGTH) snookxporter tests
