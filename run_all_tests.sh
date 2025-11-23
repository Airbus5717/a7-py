#!/bin/bash
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          A7 COMPILER - COMPLETE TEST RESULTS              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Parser & Tokenizer Tests:"
PYTHONPATH=. uv run pytest test/test_parser*.py test/test_tokenizer*.py --tb=no -q 2>&1 | tail -1
echo ""
echo "Semantic Analysis Tests (Basic):"
PYTHONPATH=. uv run pytest test/test_semantic_analysis.py --tb=no -q 2>&1 | tail -1
echo ""
echo "Semantic Analysis Tests (Comprehensive):"
PYTHONPATH=. uv run pytest test/test_semantic_comprehensive.py --tb=no -q 2>&1 | tail -1
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "TOTAL (All Tests):"
PYTHONPATH=. uv run pytest --tb=no -q 2>&1 | tail -1
