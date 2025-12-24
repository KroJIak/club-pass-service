FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ticket-expiration-service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ticket-expiration-service/ ./ticket-expiration-service/

# Set Python path
ENV PYTHONPATH=/app

# Run the service
CMD ["python", "-m", "ticket-expiration-service.src.main"]

