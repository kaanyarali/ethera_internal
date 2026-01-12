FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port (Cloud Run uses PORT env var, defaults to 8080)
ENV PORT=8080

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
