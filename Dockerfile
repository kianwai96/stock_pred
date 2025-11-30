# Use Python 3.10 for CPU-compatible TensorFlow
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies needed for psycopg2, OpenCV, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port 10000 for Render
EXPOSE 10000

# Start Gunicorn pointing to Flask subfolder
CMD ["gunicorn", "Flask.app:app", "--bind", "0.0.0.0:10000"]



