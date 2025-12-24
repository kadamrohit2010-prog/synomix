FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/

# Copy frontend build (will be built in CI/CD or before docker build)
COPY backend/static/ /app/static/

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
