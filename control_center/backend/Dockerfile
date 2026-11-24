FROM python:3.12-slim

WORKDIR /app
COPY control_center/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY orchestrator /app/orchestrator
COPY scenario_engine /app/scenario_engine
COPY synthetic_data /app/synthetic_data
COPY vulnerability_catalog /app/vulnerability_catalog
COPY validation /app/validation
COPY config /app/config
COPY profiles /app/profiles
COPY control_center/backend/app.py /app/app.py

RUN useradd -m nexora_cc && chown -R nexora_cc:nexora_cc /app
USER nexora_cc

EXPOSE 8443
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8443/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8443"]
