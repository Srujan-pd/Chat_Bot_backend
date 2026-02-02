<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port for Cloud Run
ENV PORT=8080

# Start FastAPI via Uvicorn
=======
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

>>>>>>> b72a9f6 (backend)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

