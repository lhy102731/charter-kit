#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p lib
cp src/index.js lib/index.js
echo "DSH Charter Kit build complete"