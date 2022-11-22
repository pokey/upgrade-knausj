#!/usr/bin/env bash
set -euo pipefail

pip install typer-cli
typer upgrade_knausj.main utils docs --output README.md --name upgrade-knausj
poetry install
