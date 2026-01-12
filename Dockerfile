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
EXPOSE 8080

# Set PORT as environment variable (Cloud Run provides this)
ENV PORT=8080

# Run the application
# Use python -m uvicorn for better error handling
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
