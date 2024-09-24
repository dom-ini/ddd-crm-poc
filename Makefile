.DEFAULT_GOAL := all

bandit:
	poetry run bandit -r ./src
toml_sort:
	poetry run toml-sort pyproject.toml --all --in-place
flake8:
	poetry run flake8 ./src
isort:
	poetry run isort ./src
ruff:
	poetry run ruff check ./src
pylint:
	poetry run pylint src --extension-pkg-whitelist='pydantic'
black:
	poetry run black ./src
lint: black flake8 isort ruff pylint toml_sort
lint_tests:
	poetry run black ./tests
	poetry run isort ./tests
	poetry run flake8 ./tests
	poetry run ruff check ./tests
test_domain:
	poetry run pytest tests/domain
test_application:
	poetry run pytest tests/application
test_all:
	poetry run pytest tests