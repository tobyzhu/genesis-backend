#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> genesis_backend pytest (GENESIS_USE_TEST_DB=1)"
cd "$ROOT/genesis_backend"
export GENESIS_USE_TEST_DB=1
if [ -x .venv/bin/pytest ]; then
  if ! .venv/bin/python -c "import pytest_django" 2>/dev/null; then
    .venv/bin/pip install -q pytest-django==4.9.0 || true
  fi
  if ! .venv/bin/pytest assistant/tests -q; then
    echo "Hint: create test DB first: bash scripts/setup-test-db.sh"
    exit 1
  fi
else
  echo "Skip backend: .venv/bin/pytest not found"
fi

echo "==> banxiaozhu jest"
cd "$ROOT/banxiaozhu"
if [ -f package.json ]; then
  if [ ! -d node_modules ]; then
    npm install --silent
  fi
  npm test
else
  echo "Skip banxiaozhu: package.json not found"
fi

echo "==> All tests finished"
echo "CI / Secrets: see scripts/CI.md"
