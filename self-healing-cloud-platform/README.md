# Self-Healing Cloud Deployment Platform

Production-style DevOps Deployment Control Center built with Flask, Kubernetes, Terraform, GitHub Actions, and monitoring concepts.

This platform simulates realistic workflows found in modern cloud deployment products:

1. Deployment pipeline orchestration
2. Kubernetes rollout and pod telemetry
3. Self-healing incident and recovery lifecycle
4. CI/CD validation and release readiness
5. Infrastructure visibility and operational logs

---

## Key Features

1. Glassmorphism SaaS-style dashboard UI with responsive layout
2. Sidebar navigation and top operational status bar
3. Deployment form with pipeline simulation
4. Live pipeline stages: Build, Validate, Test, Deploy, Health Check, Running
5. Dynamic log stream with realistic DevOps messages
6. Kubernetes pod table with CPU, memory, restarts, and uptime
7. Crash simulation with automatic recovery and recovery metrics
8. Monitoring charts powered by Chart.js
9. Production-style backend APIs for deployment, monitoring, infra, and logs
10. Render-ready startup (`requirements.txt`, `Procfile`, `render.yaml`)

---

## Architecture

High-level flow:

1. User triggers deployment from dashboard
2. Backend simulates CI/CD pipeline and Kubernetes rollout
3. Dashboard continuously polls deployment, pod, infra, and log APIs
4. Crash simulation triggers pod failure state and recovery workflow
5. Metrics endpoint exposes Prometheus-friendly telemetry

Detailed architecture: `docs/architecture.md`

---

## Screenshots

Add screenshots in this section after running the project:

1. `Dashboard Overview` - `assets/screenshots/dashboard-overview.png`
2. `Deployment Pipeline` - `assets/screenshots/pipeline-running.png`
3. `Kubernetes Pod Table` - `assets/screenshots/kubernetes-panel.png`
4. `Monitoring Charts` - `assets/screenshots/monitoring-charts.png`
5. `Self-Healing Recovery` - `assets/screenshots/recovery-logs.png`

---

## Repository Structure

```text
self-healing-cloud-platform/
+-- app/
|   +-- app.py
|   +-- config.py
5. `GET /deployment-history` - historical deployment runs
![Badge](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Badge](https://img.shields.io/badge/Python-3.12+-blue)
![Badge](https://img.shields.io/badge/Framework-Flask-lightblue)

A **production-grade DevOps Control Center** that simulates modern cloud deployment platforms. Demonstrates mastery of Kubernetes, Terraform, GitHub Actions, and monitoring.

## 🎯 Key Features

- ✅ **SaaS-Style Dashboard** - Real-time deployment tracking with glassmorphism UI
- ✅ **CI/CD Pipeline** - Multi-stage deployment simulation (Build → Deploy)
- ✅ **Kubernetes Simulation** - Pod management, health checks, recovery
- ✅ **Self-Healing System** - Crash simulation with automatic recovery
- ✅ **Infrastructure as Code** - Complete Terraform configuration
- ✅ **Helm Charts** - Production-ready Helm deployment
- ✅ **GitHub Actions** - 4 CI/CD workflows (deploy, helm, terraform, security)
- ✅ **Monitoring & Observability** - Prometheus metrics, event streaming
- ✅ **Render-Ready** - Deploy free to Render.com

## 🏗️ Architecture

```
User Dashboard (React/Vanilla JS)
      ↓
Flask Backend + Simulator
   ├─ Deployment Pipeline
   ├─ Kubernetes Mock Layer
   ├─ Self-Healing Engine
   └─ Prometheus Metrics
```

## 🚀 Quick Start

```bash
# Clone & setup
git clone https://github.com/anushka-nath/Self-Healing-Cloud-Deployment-Platform.git
cd self-healing-cloud-platform
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run
python app/app.py

# Open browser
open http://localhost:5000
```
6. `GET /pods` - Kubernetes pod telemetry
7. `GET /logs` - live log stream
8. `GET /infrastructure` - infrastructure and node status
9. `GET /health` - readiness/liveness status payload
10. `GET /metrics` - Prometheus metrics
11. `POST /crash` - simulate pod crash and recovery

---

## Local Run (Flask)

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

1. `http://127.0.0.1:5000/`
2. `http://127.0.0.1:5000/health`
3. `http://127.0.0.1:5000/metrics`

---

## Kubernetes Deployment Workflow

### Linux/macOS/WSL

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
kubectl port-forward -n self-healing-platform service/self-healing-api-service 50080:80
```

Open:

`http://127.0.0.1:50080/`

### Windows PowerShell

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy-windows.ps1
```

---

## CI/CD Workflow (GitHub Actions)

Pipeline file: `.github/workflows/deploy.yml`

Stages:

1. Install runtime and dev dependencies
2. Run `flake8` and Python compile checks
3. Run Flask smoke checks (`/health`, `/deployment-status`, `/pods`)
4. Validate Kubernetes YAML (`yamllint`, `kubeconform`)
5. Validate Terraform (`fmt`, `init -backend=false`, `validate`)
6. Simulate Minikube deployment flow commands

---

## Terraform Setup (AWS)

Target:

1. AWS provider in `ap-south-1`
2. Security group
3. EC2 instance (`t2.micro`)

Commands:

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

---

## Monitoring and Self-Healing

1. Prometheus scrape config: `monitoring/prometheus-config.yaml`
2. Grafana notes and query ideas: `monitoring/grafana-notes.md`
3. Dashboard charts:
   - CPU trend
   - Memory trend
   - Deployment frequency
   - Restart trend
4. Self-healing KPIs:
   - Mean Recovery Time
   - Recovery Success Rate
   - Pod Restart Metrics

---

## Render Deployment

Render-ready files included:

1. `requirements.txt`
2. `Procfile`
3. `render.yaml`

Manual deployment steps:

1. Create new Render Web Service
2. Connect GitHub repository
3. Build command:
   `pip install -r requirements.txt`
4. Start command:
   `gunicorn --chdir app app:app --workers 2 --bind 0.0.0.0:$PORT`
5. Environment variables:
   - `APP_ENV=render`
   - `LOG_LEVEL=INFO`

---

## Resume Bullet Points

1. Built a production-style DevOps Deployment Control Center with Flask, Kubernetes, Terraform, and GitHub Actions.
2. Implemented live CI/CD pipeline simulation and deployment orchestration UI inspired by modern cloud platforms.
3. Designed self-healing failure simulation with automated recovery, restart tracking, and recovery KPIs.
4. Engineered Kubernetes manifests with probe-driven health checks and multi-replica resiliency.
5. Added Prometheus-compatible metrics and real-time monitoring charts for operational visibility.
6. Delivered Render-ready deployment configuration with production Gunicorn startup.

---

## Interview Questions

1. How do readiness and liveness probes influence deployment safety?
2. Why model deployment workflows with explicit pipeline stages?
3. How would you replace simulated pipeline steps with real CI runners?
4. How can this architecture evolve from Minikube to EKS production?
5. What metrics are most important for self-healing SLA tracking?
6. How would you secure repository URL inputs and deployment actions?
7. Which Terraform changes are needed for multi-environment promotion?

---

## GitHub Push Commands

```bash
git init
git add .
git commit -m "Upgrade to production-style DevOps Deployment Control Center"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
