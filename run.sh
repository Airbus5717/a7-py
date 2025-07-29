#!/usr/bin/env bash
set -euo pipefail

# Activate virtual environment
source .venv/bin/activate

# Execute compiler with passed arguments
exec uv run python main.py "$@"

