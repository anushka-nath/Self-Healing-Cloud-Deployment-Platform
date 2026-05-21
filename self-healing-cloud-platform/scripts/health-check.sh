#!/usr/bin/env bash

# Health check helper for local testing and pipeline usage.
# Usage:
#   ./scripts/health-check.sh [URL] [MAX_RETRIES] [SLEEP_SECONDS]

set -euo pipefail

TARGET_URL="${1:-http://127.0.0.1:50080/health}"
MAX_RETRIES="${2:-10}"
SLEEP_SECONDS="${3:-3}"
REQUEST_TIMEOUT_SECONDS="${4:-5}"

echo "[INFO] Starting health checks against: ${TARGET_URL}"
echo "[INFO] Max retries: ${MAX_RETRIES}, Sleep seconds: ${SLEEP_SECONDS}, Timeout: ${REQUEST_TIMEOUT_SECONDS}s"

for attempt in $(seq 1 "${MAX_RETRIES}"); do
  TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "[INFO] ${TIMESTAMP} | Attempt ${attempt}/${MAX_RETRIES}"

  if RESPONSE="$(curl --silent --show-error --fail --max-time "${REQUEST_TIMEOUT_SECONDS}" "${TARGET_URL}")"; then
    echo "[PASS] Health check succeeded."
    echo "[DATA] ${RESPONSE}"
    exit 0
  fi

  echo "[WARN] Endpoint not healthy yet. Waiting ${SLEEP_SECONDS}s before retry."
  sleep "${SLEEP_SECONDS}"
done

echo "[FAIL] Health checks failed after ${MAX_RETRIES} attempts."
exit 1
