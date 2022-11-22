#!/usr/bin/env bash
set -euo pipefail

POETRY_PYPI_TOKEN_PYPI=$(cat "$HOME/envs/pypi/POETRY_PYPI_TOKEN_PYPI") poetry publish --build
