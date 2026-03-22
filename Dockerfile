FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Output dir must exist and be writable
RUN mkdir -p output remotion/src/data

EXPOSE 5000

# Single worker required — SSE queues are in-memory and not shared across workers.
# gthread class allows concurrent requests within the same worker.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-class=gthread", "--workers=1", "--threads=8", "--timeout=300", "app:app"]
