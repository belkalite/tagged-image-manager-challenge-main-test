SHELL := /bin/bash

ifeq ($(USE_AWS_VAULT), true)
  CHALICE = aws-vault exec $(PROFILE) -- poetry run chalice
  POETRY = aws-vault exec $(PROFILE) -- poetry
  PYTHON = aws-vault exec $(PROFILE) -- python
else
  CHALICE = poetry run chalice
  POETRY = poetry
  PYTHON = python
endif

add-records:
	poetry run python -m scripts.add_records

docs:
	widdershins \
		--environment design-docs/.widdershins.json \
		design-docs/openapi/tagged-image-manager.yml \
		-o design-docs/openapi/generated-tagged-image-manager.md

fix:
	poetry run isort app.py chalicelib/
	poetry run black app.py chalicelib/

lint:
	poetry run black app.py chalicelib/

reset-tables:
	poetry run python -m scripts.reset_tables

run:
	$(POETRY) run chalice local --no-autoreload

tables:
	poetry run python -m scripts.make_tables

tests: lint unittests

unittests:
	poetry run pytest -vv tests/unit

update-snapshots:
	poetry run pytest tests/unit -v --snapshot-update --allow-snapshot-deletion

.PHONY: add-records docs lint reset-tables tests update-snapshots unittests