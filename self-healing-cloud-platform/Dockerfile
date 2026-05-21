FROM python:3.12-slim

WORKDIR /opt/service

# Install runtime dependencies first for build cache efficiency.
COPY app/requirements.txt /opt/service/requirements.txt
RUN pip install --no-cache-dir -r /opt/service/requirements.txt

# Copy backend source and UI assets.
COPY app /opt/service/app
COPY templates /opt/service/templates
COPY static /opt/service/static

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=kubernetes
ENV PORT=5000

EXPOSE 5000

# Run production server from repository root in the container.
CMD ["gunicorn", "--chdir", "/opt/service/app", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
