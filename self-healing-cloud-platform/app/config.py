"""
Application configuration module for the Self-Healing Cloud Deployment Platform.
All runtime configuration is centralized here for predictable deployments.
"""

from __future__ import annotations

import os


class Config:
    """Runtime configuration loaded from environment variables."""

    # Service metadata used in logs and endpoint responses.
    APP_NAME = os.getenv("APP_NAME", "self-healing-cloud-platform")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_ENV = os.getenv("APP_ENV", "development")

    # Flask runtime settings.
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Logging and observability settings.
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "5"))

    # Health status labels.
    HEALTHY_STATUS = "ok"
    UNHEALTHY_STATUS = "degraded"
