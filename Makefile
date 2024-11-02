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
	poetry run pytest --cov=snookxporter --cov-fail-under=100 --cov-report term-missing tests

.PHONY: lint
lint:
	pylint --max-line-length $(MAX_LINE_LENGTH) snookxporter tests

.PHONY: isort-check
isort-check:
	poetry run isort -l $(MAX_LINE_LENGTH) --check snookxporter tests

.PHONY: tests
tests: isort-check type-check unit-tests

.PHONY: isort
isort:
	poetry run isort -l $(MAX_LINE_LENGTH) snookxporter tests

.PHONY: run
run:
	poetry run snookxporter
