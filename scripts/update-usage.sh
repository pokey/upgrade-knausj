#!/usr/bin/env bash
set -euo pipefail

pip install typer-cli
typer upgrade_talon_community.main utils docs --output README.md --name upgrade-talon-community
poetry install
