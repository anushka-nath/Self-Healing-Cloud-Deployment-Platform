# Grafana Monitoring Notes

## Recommended Dashboards

1. **Kubernetes / Compute Resources / Pod**
2. **Kubernetes / Networking / Namespace**
3. **Node Exporter Full**
4. **Application Metrics (Custom Flask /metrics)**

## Useful PromQL Queries

```promql
# Total request count grouped by endpoint and status.
sum by (endpoint, status) (app_requests_total)
```

```promql
# Crash trigger count for self-healing demonstrations.
app_manual_crash_trigger_total
```

```promql
# Deployment count triggered from dashboard.
app_deployments_total
```

```promql
# Recovery success rate.
app_recovery_success_rate
```

```promql
# Mean recovery time in seconds.
app_mean_recovery_time_seconds
```

```promql
# Pod restarts in simulator.
app_pod_restarts_total
```

```promql
# CPU usage by pod in Kubernetes runtime (optional).
sum(rate(container_cpu_usage_seconds_total{namespace="self-healing-platform"}[5m])) by (pod)
```

## Alerting Suggestions

1. Alert if `kube_pod_container_status_restarts_total` increases rapidly.
2. Alert if `kube_deployment_status_replicas_available` is below desired replicas.
3. Alert if `up{job="self-healing-flask-api"} == 0` for more than 2 minutes.
4. Alert on high container memory usage nearing limits.

## Kubernetes Monitoring Notes

1. Enable `metrics-server` in Minikube for `kubectl top` commands:
   `minikube addons enable metrics-server`
2. Validate pod health with:
   `kubectl get pods -n self-healing-platform -w`
3. Inspect container lifecycle and probe behavior:
   `kubectl describe pod <pod-name> -n self-healing-platform`
4. Watch app-level telemetry:
   `kubectl logs deployment/self-healing-api -n self-healing-platform --tail=200 -f`
