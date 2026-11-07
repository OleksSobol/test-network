FROM python:3.12-slim

# Install system tools required for Linux network scanning
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    net-tools \
    iproute2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure data directory exists for SQLite persistence
RUN mkdir -p /app/data

ENV PORT=8050
EXPOSE 8050

CMD ["sh", "-c", "python -m uvicorn lanscan.main:app --host 0.0.0.0 --port ${PORT:-8050}"]
