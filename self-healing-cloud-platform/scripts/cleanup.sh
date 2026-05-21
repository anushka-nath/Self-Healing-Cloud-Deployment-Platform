#!/usr/bin/env bash

# Cleanup helper to remove Kubernetes resources created by this project.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAMESPACE="self-healing-platform"

require_command() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "[ERROR] Required command not found: ${cmd}"
    exit 1
  fi
}

echo "[INFO] Validating prerequisites..."
require_command kubectl

echo "[INFO] Deleting project manifests (if present)..."
kubectl delete -f "${ROOT_DIR}/kubernetes/ingress.yaml" --ignore-not-found=true
kubectl delete -f "${ROOT_DIR}/kubernetes/service.yaml" --ignore-not-found=true
kubectl delete -f "${ROOT_DIR}/kubernetes/deployment.yaml" --ignore-not-found=true
kubectl delete -f "${ROOT_DIR}/kubernetes/namespace.yaml" --ignore-not-found=true

echo "[INFO] Verifying namespace cleanup status..."
if kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1; then
  echo "[WARN] Namespace ${NAMESPACE} still exists. It may be terminating."
  kubectl get namespace "${NAMESPACE}" -o wide
else
  echo "[SUCCESS] Namespace ${NAMESPACE} removed."
fi
