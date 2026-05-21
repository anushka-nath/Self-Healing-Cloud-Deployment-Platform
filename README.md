# Self-Healing-Cloud-Deployment-Platform
Self-Healing Cloud Deployment Platform is a cloud-native DevOps project built using Flask, Kubernetes, GitHub Actions, and Terraform. The platform demonstrates automated deployment workflows, self-healing Kubernetes architecture, CI/CD pipelines, infrastructure automation, and monitoring concepts in a production-style environment.
# Self-Healing Cloud Deployment Platform

## Overview

Self-Healing Cloud Deployment Platform is a production-style cloud-native DevOps project designed to simulate modern deployment and infrastructure workflows used in real-world engineering teams.

The project focuses on:

* Kubernetes orchestration
* CI/CD automation
* Infrastructure as Code (IaC)
* Monitoring and troubleshooting
* Self-healing application architecture

The platform uses a Flask backend application deployed through Kubernetes manifests with automated deployment workflows powered by GitHub Actions and infrastructure provisioning managed through Terraform.

---

# Features

## Cloud-Native Deployment

* Kubernetes-based deployment architecture
* Scalable pod replicas
* Namespace isolation
* Service-based networking

## Self-Healing Infrastructure

* Kubernetes liveness probes
* Readiness probes
* Automatic pod recovery
* Failure simulation endpoint

## CI/CD Automation

* GitHub Actions workflow
* Automated validation pipeline
* Kubernetes manifest verification
* Terraform configuration checks

## Infrastructure as Code

* Terraform-based AWS infrastructure setup
* EC2 provisioning
* Security group configuration
* Modular infrastructure files

## Monitoring & Troubleshooting

* Health monitoring endpoints
* Structured logging
* Prometheus configuration
* Linux troubleshooting scripts

---

# Tech Stack

| Category       | Technologies         |
| -------------- | -------------------- |
| Backend        | Python, Flask        |
| Orchestration  | Kubernetes, Minikube |
| CI/CD          | GitHub Actions       |
| Infrastructure | Terraform            |
| Cloud          | AWS EC2              |
| Monitoring     | Prometheus           |
| Scripting      | Bash                 |
| OS/Environment | Linux, WSL           |

---

# Project Architecture

Client Request
↓
Flask Application
↓
Kubernetes Deployment
↓
Liveness/Readiness Probes
↓
Self-Healing Recovery
↓
CI/CD Workflow
↓
Terraform Infrastructure Provisioning

---

# Project Structure

```bash
self-healing-cloud-platform/
│
├── app/
├── kubernetes/
├── terraform/
├── monitoring/
├── scripts/
├── docs/
└── .github/workflows/
```

---

# Flask Endpoints

| Endpoint   | Purpose                     |
| ---------- | --------------------------- |
| `/`        | Main application endpoint   |
| `/health`  | Health monitoring endpoint  |
| `/metrics` | Monitoring metrics          |
| `/crash`   | Simulates application crash |

---

# Kubernetes Features

* Deployment manifests
* Replica management
* Health probes
* Service networking
* Ingress configuration
* Automatic pod restart
* Namespace isolation

---

# CI/CD Workflow

The GitHub Actions pipeline performs:

1. Dependency installation
2. Flask validation
3. Kubernetes YAML validation
4. Terraform configuration validation
5. Deployment workflow simulation

---

# Terraform Infrastructure

Terraform configuration includes:

* AWS provider setup
* EC2 instance provisioning
* Security group creation
* Infrastructure outputs
* Variable-based configuration

---

# Monitoring & Troubleshooting

Monitoring setup includes:

* Prometheus configuration
* Kubernetes pod monitoring
* Health check scripts
* Linux troubleshooting utilities

Useful commands:

```bash
kubectl get pods
kubectl logs <pod-name>
kubectl describe pod <pod-name>
kubectl get services
```

---

# Self-Healing Demonstration

The `/crash` endpoint intentionally terminates the application process.

Kubernetes detects the failure using liveness probes and automatically recreates the failed pod, demonstrating self-healing cloud-native architecture.

---

# Resume Highlights

* Built a cloud-native deployment platform using Kubernetes and Flask
* Automated CI/CD workflows using GitHub Actions
* Implemented self-healing architecture using Kubernetes health probes
* Provisioned infrastructure using Terraform
* Configured monitoring and Linux troubleshooting workflows

---

# Future Improvements

* AWS EKS deployment
* Helm chart integration
* Advanced Grafana dashboards
* Centralized logging
* Horizontal pod autoscaling
* Multi-service microservice architecture

---

# Learning Outcomes

This project demonstrates practical understanding of:

* Kubernetes orchestration
* CI/CD automation
* Infrastructure as Code
* Cloud-native deployments
* Monitoring and troubleshooting
* Linux system workflows
* Deployment reliability engineering
