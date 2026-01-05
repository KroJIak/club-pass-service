FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY music-search-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY music-search-service/ ./music_search_service/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8004

# Run the application
CMD ["uvicorn", "music_search_service.main:app", "--host", "0.0.0.0", "--port", "8004"]

