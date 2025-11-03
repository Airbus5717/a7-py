#!/usr/bin/env bash
# Simple test runner script for A7 compiler

PYTHONPATH=. uv run pytest "$@"