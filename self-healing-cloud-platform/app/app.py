"""
Self-Healing Cloud Deployment Platform - Flask Backend

Production-style backend that powers:
1) SaaS-style DevOps dashboard UI
2) Deployment pipeline simulation
3) Kubernetes pod and infrastructure simulation
4) Self-healing crash and recovery workflow
5) Monitoring endpoints (/health, /metrics, /logs)
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import random
import threading
import time
import uuid
from collections import Counter, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple

from flask import Flask, Response, jsonify, render_template, request

from config import Config


def utc_now_iso() -> str:
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.now(tz=UTC).isoformat()


class JsonLogFormatter(logging.Formatter):
    """Formats log records as JSON for structured logging pipelines."""

    def format(self, record: logging.LogRecord) -> str:
        reserved_fields = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }

        payload = {
            "timestamp": utc_now_iso(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": Config.APP_NAME,
            "environment": Config.APP_ENV,
        }

        for key, value in record.__dict__.items():
            if key not in reserved_fields and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


class MetricsRegistry:
    """In-memory metrics registry for lightweight Prometheus exposition."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._start_time = time.time()
        self._request_counter: Counter[Tuple[str, str, int]] = Counter()
        self._manual_crash_trigger_total = 0

    def record_request(self, method: str, endpoint: str, status_code: int) -> None:
        """Stores request counters by method, endpoint, and status code."""
        with self._lock:
            self._request_counter[(method, endpoint, status_code)] += 1

    def record_crash_trigger(self) -> None:
        """Tracks dashboard-triggered crash simulations."""
        with self._lock:
            self._manual_crash_trigger_total += 1

    def uptime_seconds(self) -> int:
        """Returns process uptime in seconds."""
        return int(time.time() - self._start_time)

    def as_prometheus_text(self, simulator: "DeploymentSimulator") -> str:
        """Exports metrics in Prometheus text exposition format."""
        simulator_summary = simulator.metrics_summary()

        lines = [
            "# HELP app_uptime_seconds Application uptime in seconds.",
            "# TYPE app_uptime_seconds gauge",
            f"app_uptime_seconds {self.uptime_seconds()}",
            "# HELP app_manual_crash_trigger_total Manual crash simulation triggers.",
            "# TYPE app_manual_crash_trigger_total counter",
            f"app_manual_crash_trigger_total {self._manual_crash_trigger_total}",
            "# HELP app_deployments_total Total deployment runs requested from dashboard.",
            "# TYPE app_deployments_total counter",
            f"app_deployments_total {simulator_summary['deployments_total']}",
            "# HELP app_deployments_success_total Successful deployment runs.",
            "# TYPE app_deployments_success_total counter",
            f"app_deployments_success_total {simulator_summary['deployments_success_total']}",
            "# HELP app_pod_restarts_total Total pod restarts observed in simulation.",
            "# TYPE app_pod_restarts_total counter",
            f"app_pod_restarts_total {simulator_summary['pod_restarts_total']}",
            "# HELP app_recovery_events_total Total self-healing recovery events.",
            "# TYPE app_recovery_events_total counter",
            f"app_recovery_events_total {simulator_summary['recovery_events_total']}",
            "# HELP app_mean_recovery_time_seconds Mean recovery time for pod failures.",
            "# TYPE app_mean_recovery_time_seconds gauge",
            f"app_mean_recovery_time_seconds {simulator_summary['mean_recovery_time_seconds']:.2f}",
            "# HELP app_recovery_success_rate Recovery success percentage.",
            "# TYPE app_recovery_success_rate gauge",
            f"app_recovery_success_rate {simulator_summary['recovery_success_rate']:.2f}",
            "# HELP app_requests_total Total HTTP requests grouped by route metadata.",
            "# TYPE app_requests_total counter",
        ]

        with self._lock:
            for (method, endpoint, status_code), value in sorted(self._request_counter.items()):
                lines.append(
                    "app_requests_total"
                    f'{{method="{method}",endpoint="{endpoint}",status="{status_code}"}} {value}'
                )

        return "\n".join(lines) + "\n"


class DeploymentSimulator:
    """Stateful simulator for deployment workflows and self-healing behavior."""

    PIPELINE_STAGES = ("Build", "Validate", "Test", "Deploy", "Health Check", "Running")

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._logs: Deque[Dict[str, Any]] = deque(maxlen=1200)
        self._current_deployment: Optional[Dict[str, Any]] = None
        self._deployment_history: List[Dict[str, Any]] = []
        self._deployments_total = 0
        self._deployments_success_total = 0
        self._recovery_events_total = 0
        self._recovery_success_total = 0
        self._pod_restarts_total = 0
        self._total_recovery_time_seconds = 0.0
        self._active_alerts: List[Dict[str, Any]] = []
        self._nodes = [
            {"name": "node-a", "status": "Ready", "cpu_pressure": False, "memory_pressure": False},
            {"name": "node-b", "status": "Ready", "cpu_pressure": False, "memory_pressure": False},
        ]
        self._services = [
            {"name": "self-healing-api-service", "status": "Healthy", "namespace": "self-healing-platform"}
        ]
        self._pods = self._build_initial_pods()
        self._recent_deploy_timestamps: Deque[float] = deque(maxlen=500)
        self._deployment_sequence = 0

        self._append_log("INFO", "Platform bootstrap completed.", component="platform")
        self._append_log("INFO", "Cluster monitoring initialized.", component="kubernetes")

    def _build_initial_pods(self) -> List[Dict[str, Any]]:
        now_epoch = time.time()
        return [
            {
                "name": "self-healing-api-7f9a1-0",
                "namespace": "self-healing-platform",
                "status": "Running",
                "restarts": 0,
                "cpu_millicores": 82,
                "memory_mib": 186,
                "uptime_started_epoch": now_epoch - 1200,
                "health": "healthy",
            },
            {
                "name": "self-healing-api-7f9a1-1",
                "namespace": "self-healing-platform",
                "status": "Running",
                "restarts": 0,
                "cpu_millicores": 75,
                "memory_mib": 172,
                "uptime_started_epoch": now_epoch - 1080,
                "health": "healthy",
            },
        ]

    def _append_log(
        self,
        level: str,
        message: str,
        *,
        component: str = "platform",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        record: Dict[str, Any] = {
            "timestamp": utc_now_iso(),
            "level": level,
            "component": component,
            "message": message,
        }
        if context:
            record["context"] = context
        self._logs.append(record)

    def _format_uptime(self, started_epoch: float) -> str:
        elapsed = int(max(0, time.time() - started_epoch))
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _pipeline_template(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": stage,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
            }
            for stage in self.PIPELINE_STAGES
        ]

    def _active_pipeline_stage(self) -> str:
        if not self._current_deployment:
            return "idle"

        for stage in self._current_deployment["pipeline"]:
            if stage["status"] == "active":
                return stage["name"]

        if self._current_deployment["status"] in {"running", "completed"}:
            return "Running"
        return "idle"

    def _jitter_pod_usage(self) -> None:
        for pod in self._pods:
            pod["cpu_millicores"] = max(35, min(400, pod["cpu_millicores"] + random.randint(-9, 11)))
            pod["memory_mib"] = max(96, min(460, pod["memory_mib"] + random.randint(-7, 10)))

    def _deployment_frequency_24h(self) -> int:
        window_start = time.time() - 86400
        return len([timestamp for timestamp in self._recent_deploy_timestamps if timestamp >= window_start])

    def _mean_recovery_time_seconds(self) -> float:
        if self._recovery_events_total == 0:
            return 0.0
        return self._total_recovery_time_seconds / self._recovery_events_total

    def _recovery_success_rate(self) -> float:
        if self._recovery_events_total == 0:
            return 100.0
        return (self._recovery_success_total / self._recovery_events_total) * 100

    def _infrastructure_health_label(self) -> str:
        if self._active_alerts:
            return "Degraded"
        return "Healthy"

    def start_deployment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Starts an asynchronous deployment simulation."""
        app_name = str(payload.get("app_name", "self-healing-api")).strip() or "self-healing-api"
        repository_url = str(payload.get("repository_url", "")).strip()
        environment = str(payload.get("environment", "staging")).strip() or "staging"
        namespace = str(payload.get("namespace", "self-healing-platform")).strip() or "self-healing-platform"

        with self._lock:
            if self._current_deployment and self._current_deployment["status"] == "in_progress":
                return {
                    "status": "rejected",
                    "message": "A deployment pipeline is already running.",
                }

            self._deployment_sequence += 1
            deployment_id = f"dep-{int(time.time())}-{self._deployment_sequence}"
            self._deployments_total += 1
            self._recent_deploy_timestamps.append(time.time())

            self._current_deployment = {
                "deployment_id": deployment_id,
                "app_name": app_name,
                "repository_url": repository_url,
                "environment": environment,
                "namespace": namespace,
                "status": "in_progress",
                "pipeline": self._pipeline_template(),
                "created_at": utc_now_iso(),
                "started_epoch": time.time(),
                "completed_at": None,
                "active_stage": "Build",
                "progress_percentage": 0,
            }

            self._append_log(
                "INFO",
                f"Deployment {deployment_id} requested for {app_name} ({environment}).",
                component="deployments",
                context={"repository_url": repository_url, "namespace": namespace},
            )

        worker = threading.Thread(
            target=self._run_pipeline_worker,
            args=(deployment_id,),
            daemon=True,
        )
        worker.start()

        return {
            "status": "accepted",
            "deployment_id": deployment_id,
            "message": "Deployment pipeline started successfully.",
        }

    def _run_pipeline_worker(self, deployment_id: str) -> None:
        stage_durations = {
            "Build": 1.8,
            "Validate": 1.2,
            "Test": 1.5,
            "Deploy": 2.3,
            "Health Check": 1.7,
            "Running": 0.8,
        }

        stage_logs = {
            "Build": "Fetching repository and building artifact image layer cache...",
            "Validate": "Running YAML and Terraform validation gates...",
            "Test": "Executing smoke tests and runtime policy checks...",
            "Deploy": "Applying Kubernetes deployment and service manifests...",
            "Health Check": "Running readiness and liveness probe checks...",
            "Running": "Deployment completed. Service is now active.",
        }

        for index, stage_name in enumerate(self.PIPELINE_STAGES, start=1):
            with self._lock:
                if not self._current_deployment or self._current_deployment["deployment_id"] != deployment_id:
                    return

                stage_ref = self._current_deployment["pipeline"][index - 1]
                stage_ref["status"] = "active"
                stage_ref["started_at"] = utc_now_iso()
                self._current_deployment["active_stage"] = stage_name
                self._current_deployment["progress_percentage"] = int(((index - 1) / len(self.PIPELINE_STAGES)) * 100)
                self._append_log("INFO", stage_logs[stage_name], component="pipeline")

                if stage_name == "Deploy":
                    for pod in self._pods:
                        pod["status"] = "ContainerCreating"
                        pod["health"] = "initializing"
                    self._append_log(
                        "INFO",
                        "Kubernetes deployment created. Pods are initializing...",
                        component="kubernetes",
                    )

            time.sleep(stage_durations[stage_name])

            with self._lock:
                if not self._current_deployment or self._current_deployment["deployment_id"] != deployment_id:
                    return

                stage_ref = self._current_deployment["pipeline"][index - 1]
                stage_ref["status"] = "completed"
                stage_ref["completed_at"] = utc_now_iso()

                if stage_name == "Deploy":
                    now_epoch = time.time()
                    for pod in self._pods:
                        pod["status"] = "Running"
                        pod["health"] = "healthy"
                        pod["uptime_started_epoch"] = now_epoch
                        pod["cpu_millicores"] = random.randint(62, 140)
                        pod["memory_mib"] = random.randint(140, 250)
                    self._append_log("INFO", "Pod initialized and service endpoint published.", component="kubernetes")

                if stage_name == "Health Check":
                    self._append_log("INFO", "Liveness probe passed for all replicas.", component="kubernetes")
                    self._append_log("INFO", "Deployment healthy and traffic enabled.", component="kubernetes")

                if stage_name == "Running":
                    now_iso = utc_now_iso()
                    self._current_deployment["status"] = "running"
                    self._current_deployment["completed_at"] = now_iso
                    self._current_deployment["progress_percentage"] = 100
                    self._deployments_success_total += 1
                    duration_seconds = round(
                        time.time() - float(self._current_deployment["started_epoch"]),
                        2,
                    )
                    self._deployment_history.insert(
                        0,
                        {
                            "deployment_id": deployment_id,
                            "app_name": self._current_deployment["app_name"],
                            "environment": self._current_deployment["environment"],
                            "namespace": self._current_deployment["namespace"],
                            "status": "success",
                            "duration_seconds": duration_seconds,
                            "created_at": self._current_deployment["created_at"],
                            "completed_at": now_iso,
                        },
                    )
                    self._append_log(
                        "INFO",
                        f"Deployment {deployment_id} completed in {duration_seconds}s.",
                        component="deployments",
                    )

        with self._lock:
            self._jitter_pod_usage()

    def get_status_snapshot(self) -> Dict[str, Any]:
        """Returns current deployment status and high-level metrics."""
        with self._lock:
            self._jitter_pod_usage()

            running_pods = len([pod for pod in self._pods if pod["status"] == "Running"])
            healthy_services = len([svc for svc in self._services if svc["status"] == "Healthy"])
            infrastructure_health = self._infrastructure_health_label()
            mean_recovery = self._mean_recovery_time_seconds()

            active_deployments = 0
            if self._current_deployment and self._current_deployment["status"] == "in_progress":
                active_deployments = 1

            payload = {
                "status": "ok",
                "active_deployment": self._current_deployment,
                "pipeline_stage": self._active_pipeline_stage(),
                "summary": {
                    "active_deployments": active_deployments,
                    "running_pods": running_pods,
                    "healthy_services": healthy_services,
                    "infrastructure_health": infrastructure_health,
                    "cpu_usage_percent": self._cpu_usage_percent(),
                    "memory_usage_percent": self._memory_usage_percent(),
                    "deployment_frequency_24h": self._deployment_frequency_24h(),
                    "recovery_events_total": self._recovery_events_total,
                    "pod_restarts_total": self._pod_restarts_total,
                    "mean_recovery_time_seconds": round(mean_recovery, 2),
                    "recovery_success_rate": round(self._recovery_success_rate(), 2),
                },
                "alerts": list(self._active_alerts),
                "timestamp": utc_now_iso(),
            }
            return payload

    def get_history(self, limit: int) -> Dict[str, Any]:
        """Returns deployment history and trend values."""
        with self._lock:
            return {
                "status": "ok",
                "deployments": self._deployment_history[:limit],
                "total": len(self._deployment_history),
                "timestamp": utc_now_iso(),
            }

    def get_pods(self) -> Dict[str, Any]:
        """Returns simulated Kubernetes pod table payload."""
        with self._lock:
            self._jitter_pod_usage()
            pods = [
                {
                    "name": pod["name"],
                    "namespace": pod["namespace"],
                    "status": pod["status"],
                    "restarts": pod["restarts"],
                    "cpu_millicores": pod["cpu_millicores"],
                    "memory_mib": pod["memory_mib"],
                    "uptime": self._format_uptime(pod["uptime_started_epoch"]),
                    "health": pod["health"],
                }
                for pod in self._pods
            ]
            return {
                "status": "ok",
                "pods": pods,
                "replicas_desired": 2,
                "replicas_available": len([pod for pod in self._pods if pod["status"] == "Running"]),
                "timestamp": utc_now_iso(),
            }

    def get_logs(self, limit: int) -> Dict[str, Any]:
        """Returns recent platform logs."""
        with self._lock:
            return {
                "status": "ok",
                "logs": list(self._logs)[-limit:],
                "timestamp": utc_now_iso(),
            }

    def get_infrastructure(self) -> Dict[str, Any]:
        """Returns simulated cluster and infrastructure health payload."""
        with self._lock:
            return {
                "status": "ok",
                "cluster_name": "self-healing-cluster",
                "cluster_health": self._infrastructure_health_label(),
                "region": "ap-south-1",
                "nodes": list(self._nodes),
                "services": list(self._services),
                "namespace": "self-healing-platform",
                "cpu_usage_percent": self._cpu_usage_percent(),
                "memory_usage_percent": self._memory_usage_percent(),
                "timestamp": utc_now_iso(),
            }

    def simulate_crash(self) -> Dict[str, Any]:
        """Triggers simulated pod failure and asynchronous recovery."""
        with self._lock:
            target_pod = random.choice(self._pods)
            target_pod["status"] = "CrashLoopBackOff"
            target_pod["health"] = "unhealthy"
            target_pod["restarts"] += 1
            self._pod_restarts_total += 1

            incident_id = f"inc-{uuid.uuid4().hex[:8]}"
            started_epoch = time.time()
            expected_recovery_seconds = random.randint(5, 9)
            alert = {
                "incident_id": incident_id,
                "severity": "critical",
                "message": f"Pod {target_pod['name']} failed liveness checks.",
                "created_at": utc_now_iso(),
            }
            self._active_alerts = [alert]
            self._append_log("ERROR", "Crash simulation triggered for pod failure.", component="self-healing")
            self._append_log(
                "WARN",
                f"Pod {target_pod['name']} entered CrashLoopBackOff.",
                component="kubernetes",
            )

        recovery_thread = threading.Thread(
            target=self._recover_pod_worker,
            args=(target_pod["name"], started_epoch, expected_recovery_seconds),
            daemon=True,
        )
        recovery_thread.start()

        return {
            "status": "crash_simulated",
            "pod_name": target_pod["name"],
            "incident_id": incident_id,
            "expected_recovery_seconds": expected_recovery_seconds,
            "message": "Pod failure simulated. Self-healing workflow started.",
            "timestamp": utc_now_iso(),
        }

    def _recover_pod_worker(self, pod_name: str, started_epoch: float, recovery_seconds: int) -> None:
        time.sleep(recovery_seconds)

        with self._lock:
            for pod in self._pods:
                if pod["name"] == pod_name:
                    pod["status"] = "Running"
                    pod["health"] = "healthy"
                    pod["uptime_started_epoch"] = time.time()
                    pod["cpu_millicores"] = random.randint(70, 150)
                    pod["memory_mib"] = random.randint(140, 240)
                    break

            duration = time.time() - started_epoch
            self._recovery_events_total += 1
            self._recovery_success_total += 1
            self._total_recovery_time_seconds += duration
            self._active_alerts = []

            self._append_log("INFO", "Recovery workflow executed successfully.", component="self-healing")
            self._append_log("INFO", f"Pod {pod_name} recovered and healthy.", component="kubernetes")
            self._append_log(
                "INFO",
                f"Recovery successful in {duration:.2f}s.",
                component="self-healing",
            )

    def has_active_incident(self) -> bool:
        """Returns whether any incident alert is active."""
        with self._lock:
            return len(self._active_alerts) > 0

    def _cpu_usage_percent(self) -> float:
        total_cpu = sum(pod["cpu_millicores"] for pod in self._pods)
        return round(min(95.0, max(12.0, total_cpu / 10.5)), 2)

    def _memory_usage_percent(self) -> float:
        total_memory = sum(pod["memory_mib"] for pod in self._pods)
        return round(min(96.0, max(18.0, total_memory / 8.7)), 2)

    def metrics_summary(self) -> Dict[str, Any]:
        """Returns aggregated simulator metrics used by /metrics and dashboard."""
        with self._lock:
            return {
                "deployments_total": self._deployments_total,
                "deployments_success_total": self._deployments_success_total,
                "pod_restarts_total": self._pod_restarts_total,
                "recovery_events_total": self._recovery_events_total,
                "mean_recovery_time_seconds": self._mean_recovery_time_seconds(),
                "recovery_success_rate": self._recovery_success_rate(),
            }


def configure_logging() -> None:
    """Builds a production-style JSON logging setup."""
    root_logger = logging.getLogger()
    root_logger.setLevel(Config.LOG_LEVEL)
    root_logger.handlers.clear()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(JsonLogFormatter())
    root_logger.addHandler(stream_handler)


def create_app() -> Flask:
    """Application factory used by local runs and WSGI servers."""
    configure_logging()

    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )

    metrics = MetricsRegistry()
    simulator = DeploymentSimulator()

    app.config["APP_START_TIME"] = time.time()
    app.config["METRICS_REGISTRY"] = metrics
    app.config["SIMULATOR"] = simulator

    @app.before_request
    def track_request_start() -> None:
        request._start_time = time.time()

    @app.after_request
    def log_request(response: Response) -> Response:
        request_duration_ms = round((time.time() - request._start_time) * 1000, 2)
        metrics.record_request(request.method, request.path, response.status_code)

        app.logger.info(
            "request_completed",
            extra={
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "latency_ms": request_duration_ms,
                "remote_addr": request.remote_addr,
            },
        )
        return response

    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        app.logger.exception("unhandled_exception")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An internal server error occurred.",
                    "service": Config.APP_NAME,
                }
            ),
            500,
        )

    @app.route("/", methods=["GET"])
    def dashboard():
        return render_template(
            "dashboard.html",
            app_name=Config.APP_NAME,
            app_version=Config.APP_VERSION,
            app_env=Config.APP_ENV,
        )

    @app.route("/api", methods=["GET"])
    def api_metadata():
        return jsonify(
            {
                "service": Config.APP_NAME,
                "version": Config.APP_VERSION,
                "environment": Config.APP_ENV,
                "status": "running",
                "available_endpoints": [
                    "/",
                    "/api",
                    "/deploy",
                    "/deployment-status",
                    "/deployment-history",
                    "/pods",
                    "/logs",
                    "/infrastructure",
                    "/aws/infrastructure",
                    "/helm/releases",
                    "/helm/deploy",
                    "/events",
                    "/terraform/state",
                    "/observability/metrics",
                    "/health",
                    "/metrics",
                    "/crash",
                ],
            }
        )

    @app.route("/deploy", methods=["POST"])
    def deploy():
        payload = request.get_json(silent=True) or {}
        app_name = str(payload.get("app_name", "")).strip()
        repository_url = str(payload.get("repository_url", "")).strip()

        if not app_name:
            return jsonify({"status": "error", "message": "Application name is required."}), 400

        if not repository_url:
            return jsonify({"status": "error", "message": "GitHub repository URL is required."}), 400

        if repository_url and not repository_url.startswith(("http://", "https://", "git@")):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Repository URL must start with http://, https://, or git@",
                    }
                ),
                400,
            )

        result = simulator.start_deployment(payload)
        if result["status"] == "rejected":
            return jsonify(result), 409
        return jsonify(result), 202

    @app.route("/deployment-status", methods=["GET"])
    def deployment_status():
        return jsonify(simulator.get_status_snapshot())

    @app.route("/deployment-history", methods=["GET"])
    def deployment_history():
        try:
            limit = int(request.args.get("limit", "20"))
        except ValueError:
            limit = 20
        limit = max(1, min(100, limit))
        return jsonify(simulator.get_history(limit))

    @app.route("/pods", methods=["GET"])
    def pods():
        return jsonify(simulator.get_pods())

    @app.route("/logs", methods=["GET"])
    def logs():
        try:
            limit = int(request.args.get("limit", "120"))
        except ValueError:
            limit = 120
        limit = max(10, min(400, limit))
        return jsonify(simulator.get_logs(limit))

    @app.route("/infrastructure", methods=["GET"])
    def infrastructure():
        return jsonify(simulator.get_infrastructure())

    @app.route("/health", methods=["GET"])
    def health():
        status_label = Config.HEALTHY_STATUS
        http_status = 200
        if simulator.has_active_incident():
            status_label = Config.UNHEALTHY_STATUS
            http_status = 200

        return (
            jsonify(
                {
                    "status": status_label,
                    "service": Config.APP_NAME,
                    "version": Config.APP_VERSION,
                    "uptime_seconds": metrics.uptime_seconds(),
                    "timestamp": utc_now_iso(),
                    "checks": {
                        "application": "up",
                        "deployment_engine": "up",
                        "self_healing_controller": "active",
                    },
                }
            ),
            http_status,
        )

    @app.route("/metrics", methods=["GET"])
    def prometheus_metrics():
        body = metrics.as_prometheus_text(simulator)
        return Response(body, mimetype="text/plain; version=0.0.4; charset=utf-8")

    @app.route("/crash", methods=["POST", "GET"])
    def crash():
        mode = request.args.get("mode", "simulate").lower().strip()
        metrics.record_crash_trigger()

        if mode == "process":
            app.logger.warning("manual_process_crash_triggered")

            def terminate_process() -> None:
                time.sleep(1)
                os._exit(1)

            crash_thread = threading.Thread(target=terminate_process, daemon=True)
            crash_thread.start()
            return (
                jsonify(
                    {
                        "status": "crash_scheduled",
                        "mode": "process",
                        "message": "Application process will terminate intentionally in 1 second.",
                    }
                ),
                202,
            )

        result = simulator.simulate_crash()
        app.logger.warning("simulated_pod_crash_triggered", extra={"pod_name": result["pod_name"]})
        return jsonify(result), 202

    # AWS Infrastructure Simulation
    @app.route("/aws/infrastructure", methods=["GET"])
    def aws_infrastructure():
        """Simulates AWS infrastructure resources."""
        return jsonify({
            "status": "ok",
            "region": "ap-south-1",
            "infrastructure": {
                "ec2_instances": {
                    "running": 4,
                    "stopped": 1,
                    "instances": [
                        {"id": "i-0a1b2c3d4e5f6g7h8", "type": "t2.micro", "state": "running", "cpu_percent": 22},
                        {"id": "i-0b2c3d4e5f6g7h8i9", "type": "t2.small", "state": "running", "cpu_percent": 35},
                        {"id": "i-0c3d4e5f6g7h8i9j0", "type": "t2.micro", "state": "running", "cpu_percent": 18},
                        {"id": "i-0d4e5f6g7h8i9j0k1", "type": "t2.micro", "state": "running", "cpu_percent": 28},
                        {"id": "i-0e5f6g7h8i9j0k1l2", "type": "t2.micro", "state": "stopped", "cpu_percent": 0},
                    ]
                },
                "eks_cluster": {
                    "name": "self-healing-cluster",
                    "status": "ACTIVE",
                    "node_count": 3,
                    "version": "1.27",
                    "endpoint": "https://ABC123DEF456.eks.ap-south-1.amazonaws.com"
                },
                "iam_roles": {
                    "eks_service_role": {"arn": "arn:aws:iam::123456789012:role/eks-service-role", "status": "active"},
                    "node_role": {"arn": "arn:aws:iam::123456789012:role/NodeInstanceRole", "status": "active"},
                    "lambda_role": {"arn": "arn:aws:iam::123456789012:role/lambda-execution-role", "status": "active"},
                },
                "s3_buckets": {
                    "count": 2,
                    "buckets": [
                        {"name": "self-healing-deployments", "size_gb": 45.2, "objects": 3421},
                        {"name": "self-healing-logs", "size_gb": 128.5, "objects": 156892},
                    ]
                },
                "sns_topics": {
                    "count": 3,
                    "topics": [
                        {"name": "deployment-alerts", "subscriptions": 5},
                        {"name": "pod-failures", "subscriptions": 3},
                        {"name": "health-checks", "subscriptions": 2},
                    ]
                },
                "sqs_queues": {
                    "count": 2,
                    "queues": [
                        {"name": "deployment-tasks", "messages": 12, "dlq_messages": 0},
                        {"name": "event-stream", "messages": 345, "dlq_messages": 2},
                    ]
                }
            },
            "timestamp": utc_now_iso(),
        })

    # Helm Deployment Management
    @app.route("/helm/releases", methods=["GET"])
    def helm_releases():
        """Lists Helm releases deployed in the cluster."""
        return jsonify({
            "status": "ok",
            "releases": [
                {
                    "name": "self-healing-api",
                    "namespace": "self-healing-platform",
                    "chart": "self-healing-api",
                    "version": "1.2.3",
                    "app_version": "v1.2.3",
                    "status": "deployed",
                    "created_at": "2024-05-15T10:30:00Z",
                    "updated_at": "2024-05-21T14:22:00Z",
                },
                {
                    "name": "prometheus",
                    "namespace": "monitoring",
                    "chart": "kube-prometheus-stack",
                    "version": "54.0.0",
                    "app_version": "v0.68.0",
                    "status": "deployed",
                    "created_at": "2024-05-01T08:15:00Z",
                    "updated_at": "2024-05-20T10:00:00Z",
                },
                {
                    "name": "ingress-nginx",
                    "namespace": "ingress-nginx",
                    "chart": "ingress-nginx",
                    "version": "4.9.1",
                    "app_version": "1.9.3",
                    "status": "deployed",
                    "created_at": "2024-04-20T09:00:00Z",
                    "updated_at": "2024-05-21T11:45:00Z",
                }
            ],
            "timestamp": utc_now_iso(),
        })

    @app.route("/helm/deploy", methods=["POST"])
    def helm_deploy():
        """Simulates Helm chart deployment."""
        payload = request.get_json(silent=True) or {}
        chart_name = str(payload.get("chart_name", "")).strip()
        release_name = str(payload.get("release_name", "")).strip()
        namespace = str(payload.get("namespace", "default")).strip()

        if not chart_name or not release_name:
            return jsonify({"status": "error", "message": "chart_name and release_name required"}), 400

        simulator._append_log("INFO", f"Helm deploy: {chart_name} -> {release_name}", component="helm")
        
        return jsonify({
            "status": "deploying",
            "chart": chart_name,
            "release": release_name,
            "namespace": namespace,
            "message": f"Deploying Helm chart {chart_name} as {release_name}",
            "timestamp": utc_now_iso(),
        }), 202

    # Event-Driven Architecture
    @app.route("/events", methods=["GET"])
    def get_events():
        """Returns recent infrastructure and deployment events."""
        events = [
            {"timestamp": utc_now_iso(), "type": "deployment", "severity": "info", "message": "Deployment pipeline started"},
            {"timestamp": utc_now_iso(), "type": "pod", "severity": "info", "message": "Pod self-healing-api-7f9a1-0 initialized"},
            {"timestamp": utc_now_iso(), "type": "health", "severity": "info", "message": "Health check passed for all replicas"},
            {"timestamp": utc_now_iso(), "type": "scaling", "severity": "info", "message": "HPA: Scaled to 3 replicas (CPU: 75%)"},
            {"timestamp": utc_now_iso(), "type": "monitoring", "severity": "warning", "message": "Memory usage above 80% threshold"},
        ]
        return jsonify({
            "status": "ok",
            "events": events,
            "total": len(events),
            "timestamp": utc_now_iso(),
        })

    # Terraform State & IaC
    @app.route("/terraform/state", methods=["GET"])
    def terraform_state():
        """Returns Terraform infrastructure state."""
        return jsonify({
            "status": "ok",
            "terraform": {
                "version": "1.5.7",
                "backend": "s3://self-healing-terraform-state",
                "resources": {
                    "vpc": {"name": "self-healing-vpc", "cidr": "10.0.0.0/16", "status": "created"},
                    "subnets": [
                        {"name": "public-subnet-1", "cidr": "10.0.1.0/24", "az": "ap-south-1a"},
                        {"name": "private-subnet-1", "cidr": "10.0.10.0/24", "az": "ap-south-1a"},
                    ],
                    "security_groups": [
                        {"name": "eks-cluster-sg", "rules": 8},
                        {"name": "node-sg", "rules": 12},
                    ],
                    "eks_cluster": {"name": "self-healing-cluster", "version": "1.27"},
                    "iam_roles": 3,
                },
                "outputs": {
                    "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
                    "eks_cluster_endpoint": "https://ABC123DEF456.eks.ap-south-1.amazonaws.com",
                    "eks_cluster_security_group": "sg-0x1y2z3a4b5c6d7e8",
                }
            },
            "timestamp": utc_now_iso(),
        })

    # Monitoring & Observability
    @app.route("/observability/metrics", methods=["GET"])
    def observability_metrics():
        """Returns detailed observability metrics."""
        with simulator._lock:
            cpu = simulator._cpu_usage_percent()
            memory = simulator._memory_usage_percent()
        
        return jsonify({
            "status": "ok",
            "metrics": {
                "system": {
                    "cpu_usage_percent": cpu,
                    "memory_usage_percent": memory,
                    "disk_usage_percent": 42.5,
                    "network_in_mbps": 125.3,
                    "network_out_mbps": 98.7,
                },
                "application": {
                    "request_rate_per_sec": 145,
                    "error_rate_percent": 0.2,
                    "p95_latency_ms": 285,
                    "p99_latency_ms": 450,
                },
                "kubernetes": {
                    "pod_count": len(simulator._pods),
                    "running_pods": len([p for p in simulator._pods if p["status"] == "Running"]),
                    "restart_count": simulator._pod_restarts_total,
                    "node_count": len(simulator._nodes),
                },
            },
            "timestamp": utc_now_iso(),
        })

    @atexit.register
    def on_shutdown() -> None:
        app.logger.info("service_shutdown")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
