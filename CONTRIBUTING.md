# Contributing

## Setup

```
poetry install
```

## Upgrading `usage.md`

```
pip install typer-cli
typer upgrade_knausj.main utils docs --output README.md --name upgrade-knausj
```

## Publishing

### Setup

Download pypi token to `~/envs/pypi/POETRY_PYPI_TOKEN_PYPI`

### Publishing

```
POETRY_PYPI_TOKEN_PYPI=$(cat ~/envs/pypi/POETRY_PYPI_TOKEN_PYPI) poetry publish --build
```
