# Troubleshooting Guide

## Dashboard Unreachable

1. Confirm backend:
   `curl http://127.0.0.1:5000/health`
2. If using Kubernetes, confirm port-forward:
   `kubectl port-forward -n self-healing-platform service/self-healing-api-service 50080:80`
3. Open:
   `http://127.0.0.1:50080/`

## Kubernetes Checks

```bash
kubectl get pods -n self-healing-platform
kubectl describe pod <pod-name> -n self-healing-platform
kubectl logs deployment/self-healing-api -n self-healing-platform --tail=200
kubectl get svc -n self-healing-platform
kubectl get ingress -n self-healing-platform
```

## Rollout Stuck or Failing

```bash
kubectl rollout status deployment/self-healing-api -n self-healing-platform
kubectl get events -n self-healing-platform --sort-by=.metadata.creationTimestamp
```

If image errors appear:

1. Rebuild image:
   `minikube image build -t self-healing-api:2.0.0 .`
2. Restart deployment:
   `kubectl rollout restart deployment/self-healing-api -n self-healing-platform`

## Logs and Metrics Validation

```bash
curl http://127.0.0.1:5000/logs
curl http://127.0.0.1:5000/deployment-status
curl http://127.0.0.1:5000/pods
curl http://127.0.0.1:5000/metrics
```

## Linux Host Diagnostics

```bash
ps aux | grep -i gunicorn
top
netstat -tulnp | grep -E ':(5000|50080)'
curl -v http://127.0.0.1:5000/health
```

## Terraform Diagnostics

```bash
cd terraform
terraform fmt -recursive
terraform validate
aws sts get-caller-identity
```

If `aws sts get-caller-identity` fails, configure credentials:

```bash
aws configure
```
