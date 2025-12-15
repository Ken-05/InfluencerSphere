# Dockerfile for backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app code
COPY app/ ./app

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
