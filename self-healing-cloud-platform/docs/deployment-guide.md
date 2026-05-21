# Deployment Guide

## 1. Prerequisites

Install:

1. Python 3.12+
2. Minikube
3. kubectl
4. Terraform 1.6+
5. Docker or Podman (for Minikube image runtime)

## 2. Local Backend Run

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

`http://127.0.0.1:5000/`

## 3. Kubernetes Deployment (Linux/macOS/WSL)

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
kubectl port-forward -n self-healing-platform service/self-healing-api-service 50080:80
```

Open:

`http://127.0.0.1:50080/`

## 4. Kubernetes Deployment (Windows)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy-windows.ps1
```

## 5. Self-Healing Demo

```bash
curl -X POST http://127.0.0.1:50080/crash
kubectl get pods -n self-healing-platform -w
```

## 6. Terraform Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Destroy:

```bash
terraform destroy
```

## 7. Render Deployment

The project includes:

1. `requirements.txt`
2. `Procfile`
3. `render.yaml`

Manual Render setup values:

1. Build command:
   `pip install -r requirements.txt`
2. Start command:
   `gunicorn --chdir app app:app --workers 2 --bind 0.0.0.0:$PORT`
3. Environment variables:
   - `APP_ENV=render`
   - `LOG_LEVEL=INFO`
