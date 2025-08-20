# Use official Python image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install system dependencies first
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port Railway will use
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
