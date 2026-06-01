.PHONY: setup test lint

setup:
	bash scripts/bootstrap.sh

test:
	pytest

lint:
	ruff check .
