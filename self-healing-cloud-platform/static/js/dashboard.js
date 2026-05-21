(function () {
  "use strict";

  const REFRESH_STATUS_MS = 4000;
  const REFRESH_PODS_MS = 5500;
  const REFRESH_LOGS_MS = 3500;
  const REFRESH_HISTORY_MS = 9000;

  const chartState = {
    labels: [],
    cpu: [],
    memory: [],
    deployments: [],
    restarts: [],
  };

  let charts = {
    cpu: null,
    memory: null,
    deployment: null,
    restart: null,
  };

  function nowLabel() {
    const current = new Date();
    return `${current.getHours().toString().padStart(2, "0")}:${current
      .getMinutes()
      .toString()
      .padStart(2, "0")}:${current.getSeconds().toString().padStart(2, "0")}`;
  }

  async function apiGet(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`GET ${path} failed (${response.status})`);
    }
    return response.json();
  }

  async function apiPost(path, payload) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {}),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message || `POST ${path} failed (${response.status})`);
    }
    return data;
  }

  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = value;
    }
  }

  function setClusterIndicator(label) {
    const dot = document.getElementById("cluster-dot");
    const clusterLabel = document.getElementById("cluster-health-label");
    if (!dot || !clusterLabel) return;

    dot.classList.remove("degraded", "down");
    if (label.toLowerCase() === "degraded") {
      dot.classList.add("degraded");
    } else if (label.toLowerCase() === "down") {
      dot.classList.add("down");
    }
    clusterLabel.textContent = `Cluster ${label}`;
  }

  function setDeploymentIndicator(activeDeployments) {
    const dot = document.getElementById("deployment-dot");
    const label = document.getElementById("deployment-status-label");
    if (!dot || !label) return;

    dot.classList.remove("degraded", "down");
    if (activeDeployments > 0) {
      dot.classList.add("degraded");
      label.textContent = "Deployment In Progress";
    } else {
      label.textContent = "No Active Deployment";
    }
  }

  function trimSeries(series, maxPoints) {
    while (series.length > maxPoints) {
      series.shift();
    }
  }

  function updatePipeline(activeDeployment, activeStage, progress) {
    const stages = Array.from(document.querySelectorAll(".pipeline-stage"));
    const pipelineId = activeDeployment ? activeDeployment.deployment_id : "N/A";
    setText("pipeline-deployment-id", pipelineId);
    setText("pipeline-current-stage", activeStage || "Idle");
    setText("pipeline-progress", `${progress || 0}%`);

    stages.forEach((stageElement) => {
      stageElement.classList.remove("active", "done");
      const stageName = stageElement.getAttribute("data-stage");
      if (!activeDeployment || !Array.isArray(activeDeployment.pipeline)) {
        return;
      }
      const pipelineStage = activeDeployment.pipeline.find((item) => item.name === stageName);
      if (!pipelineStage) {
        return;
      }
      if (pipelineStage.status === "active") {
        stageElement.classList.add("active");
      } else if (pipelineStage.status === "completed") {
        stageElement.classList.add("done");
      }
    });
  }

  function createChart(targetId, label, color) {
    const context = document.getElementById(targetId);
    if (!context || typeof Chart === "undefined") return null;

    return new Chart(context, {
      type: "line",
      data: {
        labels: chartState.labels,
        datasets: [
          {
            label,
            data: [],
            borderColor: color,
            pointBackgroundColor: color,
            pointRadius: 2,
            borderWidth: 2,
            fill: false,
            tension: 0.28,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            ticks: { color: "#9db2de", maxTicksLimit: 8 },
            grid: { color: "rgba(144, 168, 224, 0.12)" },
          },
          y: {
            ticks: { color: "#9db2de" },
            grid: { color: "rgba(144, 168, 224, 0.12)" },
          },
        },
        plugins: {
          legend: {
            labels: { color: "#d9e5ff" },
          },
        },
      },
    });
  }

  function initializeCharts() {
    charts.cpu = createChart("cpuChart", "CPU Usage (%)", "#57a1ff");
    charts.memory = createChart("memoryChart", "Memory Usage (%)", "#34d399");
    charts.deployment = createChart("deploymentChart", "Deployments (24h)", "#f9c74f");
    charts.restart = createChart("restartChart", "Pod Restarts", "#ff6f79");
  }

  function refreshCharts(summary) {
    if (!charts.cpu || !charts.memory || !charts.deployment || !charts.restart) {
      return;
    }

    chartState.labels.push(nowLabel());
    chartState.cpu.push(summary.cpu_usage_percent || 0);
    chartState.memory.push(summary.memory_usage_percent || 0);
    chartState.deployments.push(summary.deployment_frequency_24h || 0);
    chartState.restarts.push(summary.pod_restarts_total || 0);

    trimSeries(chartState.labels, 20);
    trimSeries(chartState.cpu, 20);
    trimSeries(chartState.memory, 20);
    trimSeries(chartState.deployments, 20);
    trimSeries(chartState.restarts, 20);

    charts.cpu.data.labels = chartState.labels;
    charts.memory.data.labels = chartState.labels;
    charts.deployment.data.labels = chartState.labels;
    charts.restart.data.labels = chartState.labels;

    charts.cpu.data.datasets[0].data = chartState.cpu;
    charts.memory.data.datasets[0].data = chartState.memory;
    charts.deployment.data.datasets[0].data = chartState.deployments;
    charts.restart.data.datasets[0].data = chartState.restarts;

    charts.cpu.update("none");
    charts.memory.update("none");
    charts.deployment.update("none");
    charts.restart.update("none");
  }

  function renderPods(podPayload) {
    const body = document.getElementById("pod-table-body");
    if (!body) return;
    const rows = (podPayload.pods || [])
      .map((pod) => {
        const statusClass = pod.status === "Running" ? "status-running" : "status-issue";
        return `<tr>
          <td>${pod.name}</td>
          <td class="${statusClass}">${pod.status}</td>
          <td>${pod.restarts}</td>
          <td>${pod.cpu_millicores}m</td>
          <td>${pod.memory_mib}Mi</td>
          <td>${pod.uptime}</td>
        </tr>`;
      })
      .join("");
    body.innerHTML = rows || "<tr><td colspan='6'>No pods found.</td></tr>";
  }

  function renderLogs(payload) {
    const stream = document.getElementById("logs-stream");
    if (!stream) return;
    const lines = (payload.logs || []).map((entry) => {
      const timestamp = new Date(entry.timestamp).toLocaleTimeString();
      return `[${timestamp}] [${entry.level}] [${entry.component}] ${entry.message}`;
    });
    stream.textContent = lines.join("\n");
    stream.scrollTop = stream.scrollHeight;
  }

  async function refreshStatus() {
    try {
      const data = await apiGet("/deployment-status");
      const summary = data.summary || {};

      setText("metric-active-deployments", String(summary.active_deployments || 0));
      setText("metric-running-pods", String(summary.running_pods || 0));
      setText("metric-healthy-services", String(summary.healthy_services || 0));
      setText("metric-infra-health", summary.infrastructure_health || "Healthy");
      setText("metric-cpu", `${summary.cpu_usage_percent || 0}%`);
      setText("metric-memory", `${summary.memory_usage_percent || 0}%`);
      setText("metric-frequency", `${summary.deployment_frequency_24h || 0}/day`);
      setText(
        "metric-recovery",
        `${summary.recovery_events_total || 0} events | ${summary.recovery_success_rate || 100}% success`
      );
      setText("infra-mrt", `${summary.mean_recovery_time_seconds || 0}s`);
      setText("infra-success-rate", `${summary.recovery_success_rate || 100}%`);
      setText("alert-count", String((data.alerts || []).length));

      setClusterIndicator(summary.infrastructure_health || "Healthy");
      setDeploymentIndicator(summary.active_deployments || 0);

      updatePipeline(
        data.active_deployment,
        data.pipeline_stage,
        summary.active_deployments > 0 ? data.active_deployment?.progress_percentage : 0
      );
      refreshCharts(summary);
    } catch (error) {
      console.error("refreshStatus failed:", error);
    }
  }

  async function refreshPods() {
    try {
      const data = await apiGet("/pods");
      renderPods(data);
    } catch (error) {
      console.error("refreshPods failed:", error);
    }
  }

  async function refreshLogs() {
    try {
      const data = await apiGet("/logs?limit=200");
      renderLogs(data);
    } catch (error) {
      console.error("refreshLogs failed:", error);
    }
  }

  async function refreshInfrastructure() {
    try {
      const data = await apiGet("/infrastructure");
      setText("infra-cluster-health", data.cluster_health || "Healthy");
      setText("infra-region", data.region || "ap-south-1");
      setText("infra-namespace", data.namespace || "self-healing-platform");
      const unhealthyNodes = (data.nodes || []).filter((node) => node.status !== "Ready").length;
      setText("infra-node-health", unhealthyNodes > 0 ? "Degraded" : "Ready");
    } catch (error) {
      console.error("refreshInfrastructure failed:", error);
    }
  }

  async function refreshHistory() {
    try {
      await apiGet("/deployment-history?limit=20");
    } catch (error) {
      console.error("refreshHistory failed:", error);
    }
  }

  function bindDeployForm() {
    const form = document.getElementById("deploy-form");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Deploying...";
      }

      try {
        const payload = {
          app_name: document.getElementById("app-name").value,
          repository_url: document.getElementById("repo-url").value,
          environment: document.getElementById("environment").value,
          namespace: document.getElementById("namespace").value,
        };
        await apiPost("/deploy", payload);
        await refreshStatus();
        await refreshLogs();
      } catch (error) {
        alert(error.message);
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = "Deploy";
        }
      }
    });
  }

  function bindCrashButton() {
    const button = document.getElementById("crash-button");
    if (!button) return;

    button.addEventListener("click", async () => {
      button.disabled = true;
      button.textContent = "Simulating...";
      try {
        await apiPost("/crash", {});
        await refreshStatus();
        await refreshLogs();
      } catch (error) {
        alert(error.message);
      } finally {
        setTimeout(() => {
          button.disabled = false;
          button.textContent = "Trigger Crash Simulation";
        }, 900);
      }
    });
  }

  async function bootstrap() {
    initializeCharts();
    bindDeployForm();
    bindCrashButton();

    await Promise.all([refreshStatus(), refreshPods(), refreshInfrastructure(), refreshLogs(), refreshHistory()]);

    setInterval(refreshStatus, REFRESH_STATUS_MS);
    setInterval(refreshPods, REFRESH_PODS_MS);
    setInterval(refreshLogs, REFRESH_LOGS_MS);
    setInterval(refreshInfrastructure, REFRESH_STATUS_MS);
    setInterval(refreshHistory, REFRESH_HISTORY_MS);
  }

  document.addEventListener("DOMContentLoaded", bootstrap);
})();
