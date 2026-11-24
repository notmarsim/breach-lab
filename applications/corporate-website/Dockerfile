FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

RUN useradd -m -s /bin/bash nexora_web && chown -R nexora_web:nexora_web /app
USER nexora_web

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
