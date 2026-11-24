FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn[standard]==0.30.6
COPY app.py .
RUN useradd -m nexora_gql && chown -R nexora_gql:nexora_gql /app
USER nexora_gql
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
