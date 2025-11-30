# Use Python 3.10 because TensorFlow supports it
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy ALL project files into container
COPY . .

# Expose port for Render
EXPOSE 10000

# Run Gunicorn (pointing to Flask/app.py)
CMD ["gunicorn", "Flask.app:app", "--bind", "0.0.0.0:10000"]
