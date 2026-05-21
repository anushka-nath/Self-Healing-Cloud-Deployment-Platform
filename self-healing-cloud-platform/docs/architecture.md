# Architecture Overview

## Objective

The platform upgrades a basic self-healing Flask app into a full DevOps Deployment Control Center with:

1. Deployment orchestration simulation
2. Kubernetes workload monitoring
3. Self-healing incident recovery workflow
4. CI/CD and infrastructure automation support

## Core Components

1. **Flask Backend (`app/app.py`)**
   - Provides operational APIs (`/deploy`, `/deployment-status`, `/pods`, `/logs`, `/infrastructure`)
   - Hosts dashboard UI (`/`)
   - Exposes health and metrics endpoints (`/health`, `/metrics`)

2. **Frontend Dashboard (`templates/` + `static/`)**
   - Glassmorphism dark theme
   - Sidebar + top status navigation
   - Deployment form and live pipeline
   - Kubernetes table, log stream, and charts

3. **Kubernetes Manifests (`kubernetes/`)**
   - Namespace isolation
   - Deployment with replicas and health probes
   - ClusterIP service and ingress

4. **CI/CD Workflow (`.github/workflows/deploy.yml`)**
   - Validates app runtime, manifests, and Terraform
   - Simulates deployment command path

5. **Terraform (`terraform/`)**
   - AWS provider configuration (`ap-south-1`)
   - Security group and EC2 (`t2.micro`)
   - Variables and outputs for reproducibility

6. **Operational Scripts (`scripts/`)**
   - Linux deployment automation (`deploy.sh`)
   - Windows one-click deployment (`deploy-windows.ps1`)
   - Health checks and cleanup workflow

## Runtime Flow

1. Operator submits deployment form from dashboard
2. Backend starts asynchronous pipeline simulation
3. Pipeline transitions through Build -> Validate -> Test -> Deploy -> Health Check -> Running
4. Pod/resource telemetry updates UI cards and charts
5. Crash trigger simulates failure and automatic recovery lifecycle

## Logical Diagram

```text
User Browser
   |
   v
Flask Dashboard + APIs
   |        |        \
   |        |         -> Prometheus /metrics endpoint
   |        |
   |        -> Deployment Simulator (pipeline + logs + pods + infra + recovery)
   |
   v
Kubernetes Manifests + Minikube Runtime
   |
   v
CI/CD (GitHub Actions) + IaC (Terraform)
```

## Design Decisions

1. UI and APIs are decoupled through JSON endpoints for easy future SPA migration.
2. Pipeline simulation is stateful and thread-based to mimic long-running deployments.
3. Crash recovery avoids hard process kill by default for stable dashboard demos.
4. Render-ready startup is included for cloud hosting without architecture changes.
