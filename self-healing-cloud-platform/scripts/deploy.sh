#!/usr/bin/env bash

# End-to-end deployment script for Minikube environments.
# Builds the local project image in Minikube runtime and deploys manifests.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAMESPACE="self-healing-platform"
MINIKUBE_DRIVER="${MINIKUBE_DRIVER:-podman}"
MINIKUBE_PROFILE="${MINIKUBE_PROFILE:-minikube}"
IMAGE_TAG="self-healing-api:2.0.0"

require_command() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "[ERROR] Required command not found: ${cmd}"
    exit 1
  fi
}

echo "[INFO] Validating prerequisites..."
require_command minikube
require_command kubectl
require_command curl

echo "[INFO] Ensuring Minikube profile '${MINIKUBE_PROFILE}' is running..."
if ! minikube -p "${MINIKUBE_PROFILE}" status >/dev/null 2>&1; then
  echo "[INFO] Starting Minikube with driver: ${MINIKUBE_DRIVER}"
  minikube start -p "${MINIKUBE_PROFILE}" --driver="${MINIKUBE_DRIVER}" --cpus=2 --memory=4096
else
  echo "[INFO] Minikube profile '${MINIKUBE_PROFILE}' is already running."
fi

echo "[INFO] Setting kubectl context..."
kubectl config use-context "${MINIKUBE_PROFILE}" >/dev/null 2>&1 || true

echo "[INFO] Enabling required Minikube addons..."
minikube -p "${MINIKUBE_PROFILE}" addons enable ingress
minikube -p "${MINIKUBE_PROFILE}" addons enable metrics-server

echo "[INFO] Building image ${IMAGE_TAG} in Minikube runtime..."
minikube -p "${MINIKUBE_PROFILE}" image build -t "${IMAGE_TAG}" "${ROOT_DIR}"

echo "[INFO] Applying Kubernetes manifests..."
kubectl apply -f "${ROOT_DIR}/kubernetes/namespace.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/deployment.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/service.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/ingress.yaml"

echo "[INFO] Restarting deployment to ensure latest image is loaded..."
kubectl rollout restart deployment/self-healing-api -n "${NAMESPACE}"

echo "[INFO] Waiting for deployment rollout..."
kubectl rollout status deployment/self-healing-api -n "${NAMESPACE}" --timeout=300s

echo "[INFO] Current platform status:"
kubectl get all -n "${NAMESPACE}"
kubectl get ingress -n "${NAMESPACE}"

cat <<EONOTE
[SUCCESS] Deployment completed.

To access dashboard:
1) Start local port-forward:
   kubectl port-forward -n ${NAMESPACE} service/self-healing-api-service 50080:80
2) Open:
   http://127.0.0.1:50080/
3) Run health-check:
   ./scripts/health-check.sh http://127.0.0.1:50080/health
EONOTE
